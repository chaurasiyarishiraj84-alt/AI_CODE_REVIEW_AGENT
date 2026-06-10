"""Pydantic schemas for agent configuration."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    model: str = "gpt-4o-mini"
    max_tokens: int = 2048
    temperature: float = 0.1
    max_retries: int = 3


class ChunkConfig(BaseModel):
    max_tokens: int = 4000
    overlap: int = 200


class AgentConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    chunk: ChunkConfig = Field(default_factory=ChunkConfig)
    supported_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".jsx", ".tsx"]
    )
    confidence_threshold: int = 70
    github_token: str = ""