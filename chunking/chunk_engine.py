"""Token-aware chunking engine that respects function/class boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.constants import MAX_CHUNK_TOKENS, CHUNK_OVERLAP
from app.logger import get_logger
from chunking.smart_splitter import split_source
from chunking.token_counter import count_tokens

logger = get_logger(__name__)


@dataclass
class Chunk:
    file: str
    index: int
    total: int
    content: str
    token_count: int


def chunk_file(
    source: str,
    filepath: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap: int = CHUNK_OVERLAP,
) -> List[Chunk]:
    """Split *source* into token-bounded chunks and return a list of Chunk objects."""
    rough_chunks = split_source(source, max_lines=300)

    final_texts: List[str] = []
    for rough in rough_chunks:
        tokens = count_tokens(rough)
        if tokens <= max_tokens:
            final_texts.append(rough)
        else:
            lines = rough.splitlines(keepends=True)
            buf: List[str] = []
            buf_tokens = 0
            for line in lines:
                lt = count_tokens(line)
                if buf_tokens + lt > max_tokens and buf:
                    final_texts.append("".join(buf))
                    overlap_lines = buf[-5:]
                    buf = overlap_lines
                    buf_tokens = count_tokens("".join(buf))
                buf.append(line)
                buf_tokens += lt
            if buf:
                final_texts.append("".join(buf))

    total = len(final_texts)
    chunks: List[Chunk] = []
    for idx, text in enumerate(final_texts):
        c = Chunk(
            file=filepath,
            index=idx + 1,
            total=total,
            content=text,
            token_count=count_tokens(text),
        )
        chunks.append(c)
        logger.debug("Chunk %d/%d for %s: %d tokens", idx + 1, total, filepath, c.token_count)

    return chunks