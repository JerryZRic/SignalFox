from __future__ import annotations

import sys
from pathlib import Path

from signalfox import cli
from signalfox.config import load_settings
from signalfox.fetch import FetchedPage
from signalfox.storage import EvidenceStore


def test_add_note_command_persists_evidence(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Test note",
            "--content",
            "A preserved manual note.",
            "--trust-note",
            "Recorded during bootstrap.",
        ],
    )

    cli.main()

    output = capsys.readouterr().out
    settings = load_settings(tmp_path)
    records = EvidenceStore(settings.database_path).list_evidence()

    assert "Saved note as evidence #1" in output
    assert len(records) == 1
    assert records[0].title == "Test note"
    assert records[0].content == "A preserved manual note."
    assert records[0].source_type == "note"
    assert records[0].source_ref == "manual:cli"
    assert records[0].trust_note == "Recorded during bootstrap."


def test_fetch_url_command_persists_web_evidence(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        cli,
        "fetch_url_text",
        lambda url, verify_tls=True: FetchedPage(
            url=url,
            title="Fetched page",
            content="A fetched article body.",
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "fetch-url",
            "--url",
            "https://example.com/story",
            "--trust-note",
            "Archived for review.",
        ],
    )

    cli.main()

    output = capsys.readouterr().out
    settings = load_settings(tmp_path)
    records = EvidenceStore(settings.database_path).list_evidence()

    assert "Saved fetched page as evidence #1" in output
    assert "Title: Fetched page" in output
    assert len(records) == 1
    assert records[0].title == "Fetched page"
    assert records[0].content == "A fetched article body."
    assert records[0].source_type == "web"
    assert records[0].source_ref == "https://example.com/story"
    assert records[0].trust_note == "Archived for review."


def test_fetch_url_command_trims_content_when_requested(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        cli,
        "fetch_url_text",
        lambda url, verify_tls=True: FetchedPage(
            url=url,
            title="Fetched page",
            content="alpha beta gamma delta epsilon",
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "fetch-url",
            "--url",
            "https://example.com/story",
            "--max-chars",
            "12",
        ],
    )

    cli.main()

    output = capsys.readouterr().out
    settings = load_settings(tmp_path)
    records = EvidenceStore(settings.database_path).list_evidence()

    assert "Content trimmed to 26 characters" in output
    assert records[0].content == "alpha beta\n... [truncated]"


def test_fetch_url_command_passes_insecure_flag(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    received: dict[str, object] = {}

    def fake_fetch(url: str, verify_tls: bool = True) -> FetchedPage:
        received["url"] = url
        received["verify_tls"] = verify_tls
        return FetchedPage(url=url, title="Fetched page", content="Body")

    monkeypatch.setattr(cli, "fetch_url_text", fake_fetch)
    monkeypatch.setattr(
        sys,
        "argv",
        ["signalfox", "fetch-url", "--url", "https://example.com/story", "--insecure"],
    )

    cli.main()
    capsys.readouterr()

    assert received == {"url": "https://example.com/story", "verify_tls": False}


def test_add_note_command_skips_duplicate_records(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    argv = [
        "signalfox",
        "add-note",
        "--title",
        "Duplicate note",
        "--content",
        "The same note should not be stored twice.",
    ]

    monkeypatch.setattr(sys, "argv", argv)
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", argv)
    cli.main()

    output = capsys.readouterr().out
    settings = load_settings(tmp_path)
    records = EvidenceStore(settings.database_path).list_evidence()

    assert "Matched existing evidence #1; skipped duplicate insert" in output
    assert len(records) == 1


def test_list_evidence_command_shows_preview_by_default(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Saved clue",
            "--content",
            "A saved clue for listing with extra details that should be shortened in preview mode.",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence", "--preview-chars", "24"])
    cli.main()

    output = capsys.readouterr().out
    assert "Showing 1 evidence record(s):" in output
    assert "[1] Saved clue" in output
    assert "content: A saved clue for\n  ... [truncated]" in output


def test_list_evidence_command_shows_full_content_when_requested(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Saved clue",
            "--content",
            "A saved clue for listing with extra details.",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence", "--show-full"])
    cli.main()

    output = capsys.readouterr().out
    assert "content: A saved clue for listing with extra details." in output
    assert "... [truncated]" not in output


def test_show_evidence_command_by_id(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Saved clue",
            "--content",
            "Full record content for detailed viewing.",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "show-evidence", "--id", "1"])
    cli.main()

    output = capsys.readouterr().out
    assert "title: Saved clue" in output
    assert "content: Full record content for detailed viewing." in output


def test_show_evidence_command_by_title(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Saved clue",
            "--content",
            "Full record content for detailed viewing.",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "show-evidence", "--title", "Saved clue"])
    cli.main()

    output = capsys.readouterr().out
    assert "title: Saved clue" in output
    assert "content: Full record content for detailed viewing." in output


def test_show_evidence_command_handles_missing_record(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["signalfox", "show-evidence", "--id", "99"])

    cli.main()

    output = capsys.readouterr().out
    assert "Evidence record not found." in output


def test_list_evidence_command_filters_by_contains(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Policy shift",
            "--content",
            "The policy changed on March 20.",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Market rumor",
            "--content",
            "This note talks about pricing pressure.",
            "--source-ref",
            "manual:rumor",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence", "--contains", "policy"])
    cli.main()

    output = capsys.readouterr().out
    assert "Showing 1 evidence record(s):" in output
    assert "[1] Policy shift" in output
    assert "Market rumor" not in output


def test_list_evidence_command_filters_by_source_ref(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Policy shift",
            "--content",
            "The policy changed on March 20.",
            "--source-ref",
            "manual:policy",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "signalfox",
            "add-note",
            "--title",
            "Market rumor",
            "--content",
            "This note talks about pricing pressure.",
            "--source-ref",
            "manual:rumor",
        ],
    )
    cli.main()
    capsys.readouterr()

    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence", "--source-ref", "rumor"])
    cli.main()

    output = capsys.readouterr().out
    assert "Showing 1 evidence record(s):" in output
    assert "[1] Market rumor" in output
    assert "Policy shift" not in output


def test_list_evidence_command_filters_by_source_type(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    settings = load_settings(tmp_path)
    store = EvidenceStore(settings.database_path)
    store.initialize()
    store.add_evidence(
        cli.Evidence(
            title="Manual note",
            content="A user note.",
            source_type="note",
            source_ref="manual:cli",
        )
    )
    store.add_evidence(
        cli.Evidence(
            title="Imported article",
            content="A saved article snippet.",
            source_type="web",
            source_ref="import:web",
        )
    )

    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence", "--source-type", "web"])
    cli.main()

    output = capsys.readouterr().out
    assert "Showing 1 evidence record(s):" in output
    assert "[1] Imported article" in output
    assert "Manual note" not in output


def test_list_evidence_command_handles_empty_database(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["signalfox", "list-evidence"])

    cli.main()

    output = capsys.readouterr().out
    assert "No evidence records found." in output
