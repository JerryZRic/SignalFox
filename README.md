# SignalFox

[English](./README.md) | [简体中文](./docs/i18n/README.zh-CN.md) | [繁體中文](./docs/i18n/README.zh-TW.md) | [粵語](./docs/i18n/README.yue.md) | [日本語](./docs/i18n/README.ja.md) | [한국어](./docs/i18n/README.ko.md)

SignalFox is a personal information scouting and evidence synthesis system.

It is built for a simple but important job: help one person collect signals, preserve raw evidence, inspect what was actually captured, and keep the whole workflow traceable.

## Overview

Many AI tools are good at producing answers, but weak at preserving evidence.

SignalFox starts from a different assumption:

- evidence should be stored before it is summarized
- source context should stay attached to the record
- uncertainty should remain visible
- local, inspectable workflows are more useful than disposable chat output

The project is local-first, lightweight, and designed as a practical foundation for a personal research workflow.

## Current Features

- Store evidence in a local SQLite database
- Add manual notes with source metadata and trust notes
- Fetch a webpage into the evidence store
- Deduplicate repeated records
- List evidence with keyword and source filters
- Preview long records without flooding the terminal
- Open a single evidence record in full detail

## Quick Start

SignalFox is currently designed to run inside a dedicated Conda environment.

```bash
conda activate signalfox
pip install -e .[dev]
```

Initialize runtime directories and the local database:

```bash
signalfox --init
```

Add a manual note:

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

Fetch a webpage into the evidence store:

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

If your local Python environment is missing CA certificates, you can temporarily disable TLS verification:

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

List evidence with compact previews:

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

Filter by keyword or source metadata:

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

Show full content or open a single record directly:

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

Run tests:

```bash
pytest -q
```

## Why SignalFox

SignalFox is meant to support a repeatable evidence workflow:

1. collect
2. preserve
3. inspect
4. filter
5. synthesize

The goal is not to replace judgment. The goal is to keep the raw material available so later analysis stays auditable.

## Project Principles

- Preserve raw evidence before summarizing it
- Keep source metadata attached to every record
- Prefer simple and inspectable pipelines
- Stay useful for one person before growing into a larger system
- Treat traceability as a product feature, not an afterthought

## Repository Layout

```text
SignalFox/
├── docs/
│   ├── i18n/
│   └── ROADMAP.md
├── src/
│   └── signalfox/
├── tests/
├── LICENSE
├── environment.yml
├── pyproject.toml
└── README.md
```

## Status

This repository is still early, but it is already usable as a local evidence notebook and capture tool.

Working now:

- local database initialization
- note capture
- webpage capture
- deduplication
- filtered evidence listing
- single-record inspection

Near-term focus:

- export selected evidence as Markdown or JSON
- add more ingestion paths
- improve evidence cleaning and synthesis workflows

See [docs/ROADMAP.md](./docs/ROADMAP.md) for the working roadmap.
