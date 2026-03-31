# SignalFox

[English](../../README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md) | [粵語](./README.yue.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md)

SignalFox 是一个个人信息搜查与证据整理系统。

它想解决的事情很直接：帮助单个用户收集信号、保存原始证据、回看实际抓到的内容，并让整个过程保持可追溯。

## 项目概览

很多 AI 工具擅长给答案，但不擅长保存证据。

SignalFox 从另一个假设出发：

- 证据应该先保存，再总结
- 来源上下文不应该在处理中丢失
- 不确定性应该保留下来
- 本地、可检查的工作流比一次性的聊天输出更有价值

这个项目目前坚持本地优先、轻量、可检查，目标是成为个人研究工作流的可靠地基。

## 当前功能

- 用本地 SQLite 数据库存储证据
- 手动添加带来源信息和可信度备注的笔记
- 抓取网页并写入证据库
- 自动去重
- 按关键词或来源条件筛选证据
- 对长文本显示摘要预览，避免刷屏
- 按单条记录查看完整内容

## 快速开始

SignalFox 当前建议运行在独立的 Conda 环境中。

```bash
conda activate signalfox
pip install -e .[dev]
```

初始化运行目录和本地数据库：

```bash
signalfox --init
```

添加一条手动笔记：

```bash
signalfox add-note \
  --title "Initial clue" \
  --content "A source claims the policy changed on March 20." \
  --trust-note "Unverified note captured for follow-up."
```

抓取网页并写入证据库：

```bash
signalfox fetch-url \
  --url https://example.com/story \
  --trust-note "Archived for later review." \
  --max-chars 2000
```

如果你的本地 Python 环境缺少 CA 证书，也可以临时关闭 TLS 验证：

```bash
signalfox fetch-url --url https://example.com/story --insecure
```

列出证据并显示摘要预览：

```bash
signalfox list-evidence
signalfox list-evidence --preview-chars 180
```

按关键词或来源条件过滤：

```bash
signalfox list-evidence --contains policy
signalfox list-evidence --source-type note
signalfox list-evidence --source-ref manual
```

查看全文或直接打开单条记录：

```bash
signalfox list-evidence --show-full
signalfox show-evidence --id 3
signalfox show-evidence --title "Example Domain"
```

运行测试：

```bash
pytest -q
```

## 为什么做 SignalFox

SignalFox 想支持的是一条可以反复使用的证据工作流：

1. 收集
2. 保存
3. 检查
4. 过滤
5. 综合整理

它不是为了代替人的判断，而是为了把原始材料保留下来，让后续分析可以被回溯、被审视。

## 项目原则

- 先保存原始证据，再做总结
- 每条记录都保留来源元数据
- 优先选择简单、透明、可检查的流程
- 先把单人使用场景做好，再考虑扩展
- 把“可追溯”当成功能，而不是附加项

## 仓库结构

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

## 当前状态

这个仓库还在早期阶段，但已经可以作为本地证据笔记本和采集工具使用。

目前已经可用：

- 本地数据库初始化
- 手动笔记录入
- 网页抓取
- 去重
- 条件筛选与列表查看
- 单条证据查看

近期重点：

- 导出 Markdown 或 JSON
- 增加更多采集入口
- 提升证据清洗和综合整理能力

工作路线图见 [docs/ROADMAP.md](../ROADMAP.md)。
