"""Core data models for evidence and investigation cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Evidence:
    """A single evidence record kept with its source metadata."""

    title: str
    content: str
    source_type: str
    source_ref: str
    captured_at: datetime = field(default_factory=utc_now)
    published_at: datetime | None = None
    trust_note: str = ""


@dataclass(slots=True)
class CaseFile:
    """A lightweight container for an investigation topic."""

    topic: str
    created_at: datetime = field(default_factory=utc_now)
