"""Pydantic schemas for code review results."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ReviewIssue(BaseModel):
    file: str = Field(..., description="Relative file path")
    line: str = Field(..., description="Line number or range, e.g. '42' or '42-55'")
    issue_type: str = Field(..., description="bug | security | performance | bad_practice | style")
    severity: str = Field(..., description="critical | high | medium | low | info")
    comment: str = Field(..., description="Human-readable description of the issue")
    suggestion: str = Field(..., description="How to fix it")
    confidence: int = Field(..., ge=0, le=100, description="0-100 confidence score")
    confidence_reason: str = Field(..., description="Why this confidence was assigned")
    needs_verification: bool = Field(default=False, description="True when confidence < 70")

    @field_validator("needs_verification", mode="before")
    @classmethod
    def set_needs_verification(cls, v: object, info: object) -> bool:
        confidence = info.data.get("confidence", 100) if hasattr(info, "data") else 100 #type: ignore
        return confidence < 70

    model_config = {"populate_by_name": True}


class FileReview(BaseModel):
    file: str
    issues: List[ReviewIssue] = []
    error: Optional[str] = None


class ReviewReport(BaseModel):
    repo_url: str
    total_files: int = 0
    total_issues: int = 0
    files: List[FileReview] = []
    summary: Optional[str] = None