# SignalFox

[English](../../README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md) | [粵語](./README.yue.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md)

SignalFox 係一個個人資訊搜查同證據整理系統。

佢想做到嘅事好直接：幫單一使用者收集訊號、保存原始證據、之後可以返轉頭睇返實際搵到啲咩，令成個流程都保持可追溯。

## 專案簡介

好多 AI 工具好叻俾答案，但唔係咁擅長保存證據。

SignalFox 由另一個假設出發：

- 證據應該先保存，再整理
- 來源脈絡唔應該喺處理途中消失
- 不確定性應該保留低
- 本地、睇得到、查得到嘅 workflow，比一次性對話輸出更有價值

呢個專案目前係本地優先、輕量、可檢查，目標係做一個個人研究 workflow 嘅穩定地基。

## 目前功能

- 用本地 SQLite 資料庫儲存證據
- 手動加入附帶來源資訊同可信度備註嘅 note
- 擷取網頁並寫入證據庫
- 自動去重
- 根據關鍵字或者來源條件篩選證據
- 對長內容顯示摘要預覽，避免終端機被洗版
- 用單條紀錄方式睇完整內容

## 快速開始

SignalFox 目前建議喺獨立嘅 Conda 環境入面運行。

```bash
conda activate signalfox
pip install -e .[dev]
```

初始化執行目錄同本地資料庫：

```bash
signalfox --init
```

加入一條手動 note：

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

擷取網頁並寫入證據庫：

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

如果你本地 Python 環境冇裝好 CA 憑證，可以暫時關閉 TLS 驗證：

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

列出證據並顯示摘要預覽：

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

用關鍵字或者來源條件做篩選：

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

睇全文，或者直接開單條紀錄：

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

執行測試：

```bash
pytest -q
```

## 點解做 SignalFox

SignalFox 想支援一條可以重複使用嘅證據 workflow：

1. 收集
2. 保存
3. 檢視
4. 篩選
5. 綜合整理

佢唔係想取代人嘅判斷，而係想保留原始材料，等之後分析仲可以回溯同審視。

## 專案原則

- 先保存原始證據，再做整理
- 每條紀錄都保留來源 metadata
- 優先選擇簡單、透明、可檢查嘅流程
- 先做好一個人用都實用，再考慮擴展
- 將可追溯當成核心功能，而唔係事後補上

## 倉庫結構

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

## 目前狀態

呢個倉庫仲係早期版本，但已經可以當成本地證據筆記本同採集工具使用。

而家已經做到：

- 本地資料庫初始化
- 手動 note 錄入
- 網頁擷取
- 去重
- 條件篩選同列表檢視
- 單條證據檢視

短期重點：

- 匯出 Markdown 或 JSON
- 增加更多採集入口
- 提升證據清洗同綜合整理能力

工作路線圖見 [docs/ROADMAP.md](../ROADMAP.md)。
