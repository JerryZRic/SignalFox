# SignalFox

[English](../../README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md) | [粵語](./README.yue.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md)

SignalFox는 개인용 정보 탐색 및 증거 정리 시스템입니다.

목표는 단순합니다. 한 명의 사용자가 신호를 수집하고, 원본 증거를 보존하고, 실제로 무엇을 수집했는지 나중에 다시 확인할 수 있게 하며, 전체 흐름을 추적 가능하게 유지하는 것입니다.

## 개요

많은 AI 도구는 답을 만드는 데는 강하지만, 증거를 남기는 데는 약합니다.

SignalFox는 다른 전제에서 시작합니다.

- 요약보다 먼저 증거를 저장한다
- 출처 맥락을 기록에 함께 남긴다
- 불확실성을 보이지 않게 숨기지 않는다
- 일회성 채팅 출력보다 로컬에서 검토 가능한 워크플로를 더 중시한다

이 프로젝트는 현재 로컬 우선, 경량, 검토 가능성을 핵심으로 두고 있으며, 개인 리서치 워크플로의 기반이 되는 것을 목표로 합니다.

## 현재 기능

- 로컬 SQLite 데이터베이스에 증거 저장
- 출처 정보와 신뢰 메모가 포함된 수동 노트 추가
- 웹페이지를 가져와 증거 저장소에 기록
- 중복 레코드 자동 제거
- 키워드와 출처 조건으로 증거 필터링
- 긴 레코드에 대한 미리보기 표시
- 단일 레코드 전체 내용 조회

## 빠른 시작

SignalFox는 현재 전용 Conda 환경에서 실행하는 것을 권장합니다.

```bash
conda activate signalfox
pip install -e .[dev]
```

실행 디렉터리와 로컬 데이터베이스를 초기화합니다.

```bash
signalfox --init
```

수동 노트를 추가합니다.

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

웹페이지를 가져와 증거 저장소에 저장합니다.

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

로컬 Python 환경에 CA 인증서가 없으면 TLS 검증을 임시로 끌 수 있습니다.

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

증거 목록과 요약 미리보기를 확인합니다.

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

키워드나 출처 조건으로 필터링합니다.

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

전체 내용을 보거나 단일 레코드를 바로 열 수 있습니다.

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

테스트 실행:

```bash
pytest -q
```

## SignalFox를 만드는 이유

SignalFox가 지원하려는 것은 반복 가능한 증거 워크플로입니다.

1. 수집
2. 보존
3. 검토
4. 필터링
5. 종합

판단 자체를 대신하려는 것이 아닙니다. 나중에 다시 검토할 수 있도록 원본 재료를 남겨 두는 것이 목적입니다.

## 프로젝트 원칙

- 요약보다 먼저 원본 증거를 보존한다
- 모든 기록에 출처 메타데이터를 남긴다
- 단순하고 검토 가능한 파이프라인을 선호한다
- 먼저 개인 사용자에게 유용한 도구가 되는 데 집중한다
- 추적 가능성을 부가 기능이 아니라 핵심 기능으로 다룬다

## 저장소 구조

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

## 현재 상태

이 저장소는 아직 초기 단계이지만, 로컬 증거 노트와 수집 도구로는 이미 사용할 수 있습니다.

현재 가능한 것:

- 로컬 데이터베이스 초기화
- 수동 노트 추가
- 웹페이지 수집
- 중복 제거
- 조건 기반 목록 조회
- 단일 레코드 상세 조회

가까운 다음 목표:

- Markdown / JSON 내보내기
- 더 많은 수집 경로 추가
- 증거 정리 및 종합 흐름 개선

작업 로드맵은 [docs/ROADMAP.md](../ROADMAP.md) 를 참고하세요.
