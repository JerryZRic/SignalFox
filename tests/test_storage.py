from datetime import datetime, timezone
from pathlib import Path

from signalfox.models import Evidence
from signalfox.storage import EvidenceStore


def test_evidence_store_round_trip(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "signalfox.db")
    store.initialize()

    evidence = Evidence(
        title="Local note",
        content="An early test record.",
        source_type="note",
        source_ref="manual:test",
        captured_at=datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc),
        trust_note="Captured manually for bootstrap testing.",
    )

    row_id, created = store.add_evidence(evidence)
    records = store.list_evidence()

    assert row_id == 1
    assert created is True
    assert len(records) == 1
    assert records[0] == evidence


def test_evidence_store_deduplicates_identical_records(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "signalfox.db")
    store.initialize()

    evidence = Evidence(
        title="Repeated note",
        content="Same content should not be inserted twice.",
        source_type="note",
        source_ref="manual:test",
        trust_note="First capture.",
    )

    first_row_id, first_created = store.add_evidence(evidence)
    second_row_id, second_created = store.add_evidence(evidence)
    records = store.list_evidence()

    assert first_row_id == 1
    assert first_created is True
    assert second_row_id == 1
    assert second_created is False
    assert len(records) == 1
