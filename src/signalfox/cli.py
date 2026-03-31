"""Minimal CLI entrypoint for SignalFox."""

from __future__ import annotations

import argparse

from .fetch import fetch_url_text, truncate_text
from .models import Evidence
from .pipeline import initialize_runtime
from .storage import EvidenceStore


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""

    parser = argparse.ArgumentParser(
        prog="signalfox",
        description="Personal information scouting and evidence synthesis.",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create the standard runtime directories and local evidence database.",
    )

    subparsers = parser.add_subparsers(dest="command")

    add_note_parser = subparsers.add_parser(
        "add-note",
        help="Add a manual note to the local evidence store.",
    )
    add_note_parser.add_argument("--title", required=True, help="Short title for the note.")
    add_note_parser.add_argument(
        "--content",
        required=True,
        help="Raw note content to preserve as evidence.",
    )
    add_note_parser.add_argument(
        "--source-ref",
        default="manual:cli",
        help="Source reference string for this note.",
    )
    add_note_parser.add_argument(
        "--trust-note",
        default="",
        help="Optional note about why this source should be trusted or handled carefully.",
    )

    fetch_url_parser = subparsers.add_parser(
        "fetch-url",
        help="Fetch a URL, extract readable text, and save it as evidence.",
    )
    fetch_url_parser.add_argument("--url", required=True, help="URL to fetch.")
    fetch_url_parser.add_argument(
        "--trust-note",
        default="",
        help="Optional note about the quality or caveats of this source.",
    )
    fetch_url_parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for this request.",
    )
    fetch_url_parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Maximum number of content characters to store for the fetched page.",
    )

    list_parser = subparsers.add_parser(
        "list-evidence",
        help="List evidence currently stored in the local database.",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of evidence records to display.",
    )
    list_parser.add_argument(
        "--contains",
        default="",
        help="Only show evidence whose title or content contains this text.",
    )
    list_parser.add_argument(
        "--source-type",
        default="",
        help="Only show evidence from this source type.",
    )
    list_parser.add_argument(
        "--source-ref",
        default="",
        help="Only show evidence whose source reference contains this text.",
    )
    list_parser.add_argument(
        "--show-full",
        action="store_true",
        help="Show full evidence content instead of a shortened preview.",
    )
    list_parser.add_argument(
        "--preview-chars",
        type=int,
        default=280,
        help="Maximum number of content characters to show in list previews.",
    )

    show_parser = subparsers.add_parser(
        "show-evidence",
        help="Show a single evidence record in full detail.",
    )
    selector_group = show_parser.add_mutually_exclusive_group(required=True)
    selector_group.add_argument("--id", type=int, help="Show a record by numeric evidence id.")
    selector_group.add_argument("--title", help="Show the latest record whose title matches exactly.")
    return parser


def _render_evidence(record: Evidence, *, show_full: bool, preview_chars: int) -> str:
    lines = [
        f"title: {record.title}",
        f"source_type: {record.source_type}",
        f"source_ref: {record.source_ref}",
    ]
    if record.trust_note:
        lines.append(f"trust_note: {record.trust_note}")
    content = record.content if show_full else truncate_text(record.content, preview_chars)
    lines.append(f"content: {content}")
    return "\n".join(lines)


def handle_add_note(args: argparse.Namespace) -> int:
    """Persist a manual note into the local evidence store."""

    state = initialize_runtime()
    store = EvidenceStore(state.database_path)
    row_id, created = store.add_evidence(
        Evidence(
            title=args.title,
            content=args.content,
            source_type="note",
            source_ref=args.source_ref,
            trust_note=args.trust_note,
        )
    )
    if created:
        print(f"Saved note as evidence #{row_id}")
    else:
        print(f"Matched existing evidence #{row_id}; skipped duplicate insert")
    print(f"Database: {state.database_path}")
    return row_id


def handle_fetch_url(args: argparse.Namespace) -> int:
    """Fetch a URL and persist the extracted content as evidence."""

    state = initialize_runtime()
    page = fetch_url_text(args.url, verify_tls=not args.insecure)
    store = EvidenceStore(state.database_path)
    content = truncate_text(page.content, args.max_chars)
    row_id, created = store.add_evidence(
        Evidence(
            title=page.title,
            content=content,
            source_type="web",
            source_ref=page.url,
            trust_note=args.trust_note,
        )
    )
    if created:
        print(f"Saved fetched page as evidence #{row_id}")
    else:
        print(f"Matched existing evidence #{row_id}; skipped duplicate insert")
    print(f"Title: {page.title}")
    if args.max_chars and len(page.content) > len(content):
        print(f"Content trimmed to {len(content)} characters")
    print(f"Database: {state.database_path}")
    return row_id


def handle_list_evidence(args: argparse.Namespace) -> list[Evidence]:
    """Print evidence currently stored in the local database."""

    state = initialize_runtime()
    store = EvidenceStore(state.database_path)
    visible_records = store.search_evidence(
        args.contains,
        source_type=args.source_type,
        source_ref=args.source_ref,
        limit=args.limit,
    )

    if not visible_records:
        print("No evidence records found.")
        print(f"Database: {state.database_path}")
        return []

    print(f"Showing {len(visible_records)} evidence record(s):")
    for index, record in enumerate(visible_records, start=1):
        print(f"[{index}] {record.title}")
        rendered = _render_evidence(record, show_full=args.show_full, preview_chars=args.preview_chars)
        for line in rendered.splitlines()[1:]:
            print(f"  {line}")
    print(f"Database: {state.database_path}")
    return visible_records


def handle_show_evidence(args: argparse.Namespace) -> Evidence | None:
    """Print one evidence record in full detail."""

    state = initialize_runtime()
    store = EvidenceStore(state.database_path)
    if args.id is not None:
        record = store.get_evidence_by_id(args.id)
    else:
        record = store.get_latest_evidence_by_title(args.title)

    if record is None:
        print("Evidence record not found.")
        print(f"Database: {state.database_path}")
        return None

    print(_render_evidence(record, show_full=True, preview_chars=0))
    print(f"Database: {state.database_path}")
    return record


def main() -> None:
    """Run the SignalFox CLI."""

    parser = build_parser()
    args = parser.parse_args()

    if args.init:
        state = initialize_runtime()
        print("Initialized SignalFox runtime assets:")
        for path in state.directories:
            print(f"- {path}")
        print(f"- {state.database_path}")
        return

    if args.command == "add-note":
        handle_add_note(args)
        return

    if args.command == "fetch-url":
        handle_fetch_url(args)
        return

    if args.command == "list-evidence":
        handle_list_evidence(args)
        return

    if args.command == "show-evidence":
        handle_show_evidence(args)
        return

    parser.print_help()
