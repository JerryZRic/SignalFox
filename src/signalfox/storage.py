"""SQLite-backed evidence storage."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Evidence

SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    published_at TEXT,
    trust_note TEXT NOT NULL,
    fingerprint TEXT
);
"""

FINGERPRINT_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_evidence_fingerprint
ON evidence (fingerprint);
"""


class EvidenceStore:
    """Store and retrieve evidence records from a local SQLite database."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> Path:
        """Create the database and schema if they do not exist."""

        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(SCHEMA)
            self._ensure_fingerprint_column(connection)
            self._backfill_fingerprints(connection)
            self._deduplicate_existing_rows(connection)
            connection.execute(FINGERPRINT_INDEX)
            connection.commit()
        return self.database_path

    def add_evidence(self, evidence: Evidence) -> tuple[int, bool]:
        """Insert a single evidence record and return its row id and creation status."""

        fingerprint = self._fingerprint(evidence)
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO evidence (
                    title,
                    content,
                    source_type,
                    source_ref,
                    captured_at,
                    published_at,
                    trust_note,
                    fingerprint
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence.title,
                    evidence.content,
                    evidence.source_type,
                    evidence.source_ref,
                    evidence.captured_at.isoformat(),
                    evidence.published_at.isoformat() if evidence.published_at else None,
                    evidence.trust_note,
                    fingerprint,
                ),
            )
            connection.commit()

            if cursor.lastrowid:
                return int(cursor.lastrowid), True

            existing_id = connection.execute(
                "SELECT id FROM evidence WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
        return int(existing_id[0]), False

    def get_evidence_by_id(self, evidence_id: int) -> Evidence | None:
        """Return a single evidence record by row id."""

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT title, content, source_type, source_ref, captured_at, published_at, trust_note
                FROM evidence
                WHERE id = ?
                """,
                (evidence_id,),
            ).fetchone()

        if row is None:
            return None
        return self._rows_to_evidence([row])[0]

    def get_latest_evidence_by_title(self, title: str) -> Evidence | None:
        """Return the most recent evidence record whose title matches exactly."""

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT title, content, source_type, source_ref, captured_at, published_at, trust_note
                FROM evidence
                WHERE title = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (title.strip(),),
            ).fetchone()

        if row is None:
            return None
        return self._rows_to_evidence([row])[0]

    def list_evidence(self) -> list[Evidence]:
        """Return evidence records in insertion order."""

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT title, content, source_type, source_ref, captured_at, published_at, trust_note
                FROM evidence
                ORDER BY id ASC
                """
            ).fetchall()

        return self._rows_to_evidence(rows)

    def search_evidence(
        self,
        query: str = "",
        *,
        source_type: str = "",
        source_ref: str = "",
        limit: int = 20,
    ) -> list[Evidence]:
        """Return evidence records filtered by text and optional source metadata."""

        conditions = []
        parameters: list[str | int] = []

        normalized_query = query.strip()
        if normalized_query:
            conditions.append("(title LIKE ? COLLATE NOCASE OR content LIKE ? COLLATE NOCASE)")
            parameters.extend([f"%{normalized_query}%", f"%{normalized_query}%"])

        normalized_source_type = source_type.strip()
        if normalized_source_type:
            conditions.append("source_type = ?")
            parameters.append(normalized_source_type)

        normalized_source_ref = source_ref.strip()
        if normalized_source_ref:
            conditions.append("source_ref LIKE ? COLLATE NOCASE")
            parameters.append(f"%{normalized_source_ref}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT title, content, source_type, source_ref, captured_at, published_at, trust_note
                FROM evidence
                {where_clause}
                ORDER BY id ASC
                LIMIT ?
                """,
                [*parameters, max(limit, 0)],
            ).fetchall()

        return self._rows_to_evidence(rows)

    def _rows_to_evidence(
        self,
        rows: list[tuple[str, str, str, str, str, str | None, str]],
    ) -> list[Evidence]:
        return [
            Evidence(
                title=title,
                content=content,
                source_type=source_type,
                source_ref=source_ref,
                captured_at=datetime.fromisoformat(captured_at),
                published_at=datetime.fromisoformat(published_at) if published_at else None,
                trust_note=trust_note,
            )
            for title, content, source_type, source_ref, captured_at, published_at, trust_note in rows
        ]

    def _ensure_fingerprint_column(self, connection: sqlite3.Connection) -> None:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(evidence)").fetchall()}
        if "fingerprint" not in columns:
            connection.execute("ALTER TABLE evidence ADD COLUMN fingerprint TEXT")

    def _backfill_fingerprints(self, connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            """
            SELECT id, title, content, source_type, source_ref
            FROM evidence
            WHERE fingerprint IS NULL OR fingerprint = ''
            """
        ).fetchall()
        for row_id, title, content, source_type, source_ref in rows:
            fingerprint = self._fingerprint_from_parts(
                title=title,
                content=content,
                source_type=source_type,
                source_ref=source_ref,
            )
            connection.execute(
                "UPDATE evidence SET fingerprint = ? WHERE id = ?",
                (fingerprint, row_id),
            )

    def _deduplicate_existing_rows(self, connection: sqlite3.Connection) -> None:
        duplicate_groups = connection.execute(
            """
            SELECT fingerprint, MIN(id) AS keep_id
            FROM evidence
            WHERE fingerprint IS NOT NULL AND fingerprint != ''
            GROUP BY fingerprint
            HAVING COUNT(*) > 1
            """
        ).fetchall()
        for fingerprint, keep_id in duplicate_groups:
            connection.execute(
                "DELETE FROM evidence WHERE fingerprint = ? AND id != ?",
                (fingerprint, keep_id),
            )

    def _fingerprint(self, evidence: Evidence) -> str:
        return self._fingerprint_from_parts(
            title=evidence.title,
            content=evidence.content,
            source_type=evidence.source_type,
            source_ref=evidence.source_ref,
        )

    def _fingerprint_from_parts(
        self,
        *,
        title: str,
        content: str,
        source_type: str,
        source_ref: str,
    ) -> str:
        payload = "\n".join([title.strip(), content.strip(), source_type.strip(), source_ref.strip()])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
