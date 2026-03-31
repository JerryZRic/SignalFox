from pathlib import Path

from signalfox.pipeline import ensure_runtime_dirs, initialize_runtime


def test_ensure_runtime_dirs_creates_standard_directories(tmp_path: Path) -> None:
    created = ensure_runtime_dirs(tmp_path)

    assert created == [
        tmp_path / "data",
        tmp_path / "reports",
        tmp_path / "artifacts",
    ]
    assert all(path.exists() and path.is_dir() for path in created)


def test_initialize_runtime_creates_database(tmp_path: Path) -> None:
    state = initialize_runtime(tmp_path)

    assert state.database_path == tmp_path / "data" / "signalfox.db"
    assert state.database_path.exists()
