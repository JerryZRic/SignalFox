# SignalFox

[English](../../README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md) | [粵語](./README.yue.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md)

SignalFox は、個人向けの情報探索と証拠整理のためのシステムです。

目的はシンプルです。1人のユーザーがシグナルを集め、生の証拠を保存し、実際に取得した内容をあとから確認できるようにし、全体の流れを追跡可能に保つことです。

## 概要

多くの AI ツールは答えを出すのは得意ですが、証拠を残すことはあまり得意ではありません。

SignalFox は別の前提から設計されています。

- 要約する前に証拠を保存する
- 出典の文脈を記録に残す
- 不確実性を見えたままにする
- 使い捨てのチャット出力より、ローカルで検証可能なワークフローを重視する

このプロジェクトは現在、ローカルファースト、軽量、検証しやすい構成を重視しており、個人研究ワークフローの土台になることを目指しています。

## 現在の機能

- ローカル SQLite データベースへの証拠保存
- 出典情報と信頼メモ付きの手動ノート追加
- Web ページの取得と証拠ストアへの保存
- 重複レコードの自動排除
- キーワードや出典条件による絞り込み
- 長文のプレビュー表示
- 単一レコードの詳細表示

## クイックスタート

SignalFox は現在、専用の Conda 環境で動かすことを想定しています。

```bash
conda activate signalfox
pip install -e .[dev]
```

実行用ディレクトリとローカルデータベースを初期化します。

```bash
signalfox --init
```

手動ノートを追加します。

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

Web ページを取得して証拠ストアに保存します。

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

ローカルの Python 環境に CA 証明書が不足している場合は、一時的に TLS 検証を無効にできます。

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

証拠を一覧表示し、短いプレビューを確認します。

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

キーワードや出典情報で絞り込みます。

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

全文表示、または単一レコードの直接表示も可能です。

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

テストを実行します。

```bash
pytest -q
```

## SignalFox の目的

SignalFox が支えたいのは、再利用可能な証拠ワークフローです。

1. 収集
2. 保存
3. 確認
4. 絞り込み
5. 統合

判断そのものを置き換えるのが目的ではありません。あとから検証できるように、生の材料を残しておくことが目的です。

## プロジェクト原則

- 要約より先に生の証拠を保存する
- すべての記録に出典メタデータを残す
- シンプルで検証可能なパイプラインを優先する
- まずは個人利用で役立つことを重視する
- 追跡可能性を後付けではなく機能として扱う

## リポジトリ構成

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

## 現在の状態

このリポジトリはまだ初期段階ですが、ローカルの証拠ノート兼収集ツールとしてすでに利用できます。

現在できること：

- ローカルデータベース初期化
- 手動ノート追加
- Web ページ取得
- 重複排除
- 条件付き一覧表示
- 単一レコード詳細表示

直近の重点項目：

- Markdown / JSON へのエクスポート
- 取り込み経路の追加
- 証拠のクリーニングと統合フローの改善

作業ロードマップは [docs/ROADMAP.md](../ROADMAP.md) を参照してください。
