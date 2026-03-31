"""Project configuration helpers for SignalFox."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Runtime settings for the local project."""

    project_root: Path
    data_dir: Path
    database_path: Path
    reports_dir: Path
    artifacts_dir: Path


def load_settings(project_root: Path | None = None) -> Settings:
    """Create filesystem settings relative to the active project root."""

    root = (project_root or Path.cwd()).resolve()
    data_dir = root / "data"
    return Settings(
        project_root=root,
        data_dir=data_dir,
        database_path=data_dir / "signalfox.db",
        reports_dir=root / "reports",
        artifacts_dir=root / "artifacts",
    )
