# SignalFox Roadmap

## North Star

Build a personal investigation system that helps one user collect evidence,
track sources, compare narratives, and produce reports with explicit
uncertainty.

## Phase 1: Foundation

- Establish package layout
- Add CLI entrypoint
- Define core data models
- Decide on local storage format

Deliverable:

- repository is installable
- `signalfox --help` works
- evidence objects have a stable schema

## Phase 2: Evidence Layer

- Add evidence record schema
- Add source metadata fields
- Add local JSONL or SQLite storage
- Add import/export helpers

Deliverable:

- can save and load evidence records
- every record includes source, time, and content

## Phase 3: Collection

- Add first source adapter
- Support manual evidence ingestion
- Add URL-based ingestion workflow

Deliverable:

- can create a case and attach evidence from at least one source

## Phase 4: Synthesis

- Build timeline generation
- Build contradiction flags
- Build uncertainty annotations
- Add markdown report rendering

Deliverable:

- can convert a case into a readable report

## Phase 5: Quality Controls

- Add claim-to-evidence linking
- Add source confidence heuristics
- Add duplicate and near-duplicate detection
- Add review checklist for final reports

Deliverable:

- reports distinguish evidence from inference
- conflicting signals are visible instead of hidden
