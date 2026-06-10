"""Production launcher with Rich status output."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

ROOT = Path(__file__).parent
MAIN = ROOT / "app" / "main.py"
console = Console()


def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]🤖 AI Code Review Agent[/bold cyan]\n"
            "[dim]Starting Streamlit dashboard…[/dim]",
            border_style="cyan",
        )
    )

    port = "5000"
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(MAIN),
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
    ]

    console.print(f"[green]→[/green] Running on [bold]http://localhost:{port}[/bold]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    subprocess.run(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    main()