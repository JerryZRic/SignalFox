"""Bootstrap pipeline helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import load_settings
from .storage import EvidenceStore


@dataclass(slots=True)
class RuntimeState:
    """Created runtime assets for the local project."""

    directories: list[Path]
    database_path: Path


def ensure_runtime_dirs(project_root: Path | None = None) -> list[Path]:
    """Create the standard runtime directories if they do not already exist."""

    settings = load_settings(project_root)
    created = []
    for path in (settings.data_dir, settings.reports_dir, settings.artifacts_dir):
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)
    return created


def initialize_runtime(project_root: Path | None = None) -> RuntimeState:
    """Create runtime directories and initialize the local evidence database."""

    settings = load_settings(project_root)
    created = ensure_runtime_dirs(settings.project_root)
    database_path = EvidenceStore(settings.database_path).initialize()
    return RuntimeState(directories=created, database_path=database_path)
