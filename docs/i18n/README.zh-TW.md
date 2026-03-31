# SignalFox

[English](../../README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md) | [粵語](./README.yue.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md)

SignalFox 是一個個人資訊搜查與證據整理系統。

它想完成的事情很直接：幫助單一使用者收集訊號、保存原始證據、回看實際抓到的內容，並讓整個流程保持可追溯。

## 專案概覽

很多 AI 工具擅長產生答案，但不擅長保存證據。

SignalFox 從另一個假設出發：

- 證據應該先保存，再整理
- 來源脈絡不應在處理過程中遺失
- 不確定性應該被保留下來
- 本地、可檢查的工作流程，比一次性的聊天輸出更有價值

這個專案目前堅持本地優先、輕量、可檢查，目標是成為個人研究工作流的可靠基礎。

## 目前功能

- 用本地 SQLite 資料庫保存證據
- 手動加入附帶來源資訊與可信度備註的筆記
- 抓取網頁並寫入證據庫
- 自動去重
- 依關鍵字或來源條件篩選證據
- 對長內容顯示摘要預覽，避免終端被刷滿
- 依單筆紀錄查看完整內容

## 快速開始

SignalFox 目前建議在獨立的 Conda 環境中執行。

```bash
conda activate signalfox
pip install -e .[dev]
```

初始化執行目錄與本地資料庫：

```bash
signalfox --init
```

加入一條手動筆記：

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

抓取網頁並寫入證據庫：

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

如果你的本地 Python 環境缺少 CA 憑證，也可以暫時關閉 TLS 驗證：

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

列出證據並顯示摘要預覽：

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

依關鍵字或來源條件過濾：

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

查看全文或直接開啟單筆紀錄：

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

執行測試：

```bash
pytest -q
```

## 為什麼做 SignalFox

SignalFox 想支援的是一條可重複使用的證據工作流程：

1. 收集
2. 保存
3. 檢視
4. 篩選
5. 綜合整理

它不是要取代人的判斷，而是要把原始材料保留下來，讓後續分析可以被回溯、被審視。

## 專案原則

- 先保存原始證據，再做整理
- 每筆紀錄都保留來源中繼資料
- 優先選擇簡單、透明、可檢查的流程
- 先把單人使用情境做好，再考慮擴展
- 把「可追溯」當成功能，而不是附加項

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

這個倉庫仍在早期階段，但已經可以作為本地證據筆記本與採集工具使用。

目前已可使用：

- 本地資料庫初始化
- 手動筆記錄入
- 網頁抓取
- 去重
- 條件篩選與列表檢視
- 單筆證據檢視

近期重點：

- 匯出 Markdown 或 JSON
- 增加更多採集入口
- 提升證據清洗與綜合整理能力

工作路線圖見 [docs/ROADMAP.md](../ROADMAP.md)。
