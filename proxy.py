"""
Fast reverse proxy: binds port 5000 immediately (so the workflow port-detection
check passes), then forwards all HTTP and WebSocket traffic to Streamlit on
port 5001.

Streamlit takes 60-90 seconds to start in this environment. While it loads,
the proxy serves a friendly "Starting…" page with auto-refresh.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

import aiohttp
from aiohttp import web

PORT = int(os.getenv("PORT", "5000"))
STREAMLIT_PORT = PORT + 1
STREAMLIT_URL = f"http://127.0.0.1:{STREAMLIT_PORT}"
ROOT = Path(__file__).parent

log = logging.getLogger("proxy")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [proxy] %(message)s",
    datefmt="%H:%M:%S",
)

_LOADING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="5">
  <title>🤖 AI Code Review — Starting…</title>
  <style>
    body {{ font-family: sans-serif; display: flex; align-items: center;
           justify-content: center; height: 100vh; margin: 0;
           background: #0e1117; color: #fafafa; }}
    .box   {{ text-align: center; }}
    h1     {{ font-size: 2rem; margin-bottom: .5rem; }}
    p      {{ color: #aaa; }}
    .spinner {{ width: 48px; height: 48px; border: 5px solid #444;
               border-top-color: #4CAF50; border-radius: 50%;
               animation: spin 1s linear infinite; margin: 1.5rem auto; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="box">
    <h1>🤖 AI Code Review Agent</h1>
    <div class="spinner"></div>
    <p>Starting Streamlit … this page refreshes automatically.</p>
    <p style="font-size:.8rem; color:#666">
      Importing ML libraries (pandas, plotly, tiktoken …)
    </p>
  </div>
</body>
</html>"""


async def _streamlit_ready(session: aiohttp.ClientSession) -> bool:
    try:
        async with session.get(
            f"{STREAMLIT_URL}/_stcore/health",
            timeout=aiohttp.ClientTimeout(total=2),
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


async def proxy_http(request: web.Request) -> web.StreamResponse:
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector) as session:
        if not await _streamlit_ready(session):
            return web.Response(
                content_type="text/html",
                body=_LOADING_HTML.encode(),
            )

        url = f"{STREAMLIT_URL}{request.path_qs}"
        try:
            async with session.request(
                method=request.method,
                url=url,
                headers={
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() not in ("host", "content-length")
                },
                data=await request.read(),
                allow_redirects=False,
            ) as backend:
                body = await backend.read()
                return web.Response(
                    status=backend.status,
                    headers={
                        k: v
                        for k, v in backend.headers.items()
                        if k.lower()
                        not in (
                            "content-encoding",
                            "transfer-encoding",
                            "connection",
                        )
                    },
                    body=body,
                )
        except aiohttp.ClientError:
            return web.Response(
                content_type="text/html",
                body=_LOADING_HTML.encode(),
            )


async def proxy_ws(request: web.Request) -> web.WebSocketResponse:
    ws_client = web.WebSocketResponse()
    await ws_client.prepare(request)

    backend_url = f"ws://127.0.0.1:{STREAMLIT_PORT}{request.path_qs}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(backend_url) as ws_backend:

                async def forward_to_backend() -> None:
                    async for msg in ws_client:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await ws_backend.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await ws_backend.send_bytes(msg.data)
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break

                async def forward_to_client() -> None:
                    async for msg in ws_backend:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await ws_client.send_str(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            await ws_client.send_bytes(msg.data)
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break

                await asyncio.gather(
                    forward_to_backend(),
                    forward_to_client(),
                    return_exceptions=True,
                )
    except Exception:
        pass

    return ws_client


async def route(request: web.Request) -> web.StreamResponse:
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await proxy_ws(request)
    return await proxy_http(request)


def _launch_streamlit() -> subprocess.Popen:
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app" / "main.py"),
        "--server.port",
        str(STREAMLIT_PORT),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
    ]
    log.info("Launching Streamlit on port %d …", STREAMLIT_PORT)
    return subprocess.Popen(cmd, cwd=str(ROOT))


async def main() -> None:
    app = web.Application()
    app.router.add_route("*", "/{path_info:.*}", route)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info("Proxy listening on port %d → Streamlit on port %d", PORT, STREAMLIT_PORT)

    proc = _launch_streamlit()

    loop = asyncio.get_running_loop()

    def _stop(*_args: object) -> None:
        proc.terminate()
        loop.stop()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    try:
        await asyncio.Event().wait()
    finally:
        proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())