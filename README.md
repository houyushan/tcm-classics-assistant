# 中医古籍助手 (TCM Classics Assistant)

基于 700+ 卷中医古籍经典文献的 Codex 技能助手。

## 功能

- 搜索 700+ 卷中医古籍，涵盖从《神农本草经》到清代医案
- 支持 19 个分类：本草、方剂、伤寒、金匮、内经、温病、诊法、女科、儿科、外科、针灸、医案等
- 智能编码检测（GBK / UTF-16LE / UTF-8）
- 多模式搜索：单关键词、多关键词（all/any）、分类筛选

## 安装

将 `tcm-classics-assistant` 目录复制到 `$CODEX_HOME/skills/`（默认 `~/.codex/skills/`）。

```powershell
Copy-Item tcm-classics-assistant -Destination "$env:USERPROFILE\.codex\skills\tcm-classics-assistant" -Recurse
```

重启 Codex 后生效。

## 使用

在 Codex 中直接用中文提问中医相关问题即可自动触发：

- "桂枝汤的组成和功效是什么？"
- "阴虚潮热盗汗怎么辨证？"
- "伤寒论中麻黄汤的适应证有哪些？"

## 古籍来源

文本文件需自行放置在 `中医古籍700本TXT/` 目录下（已通过 .gitignore 排除）。

## 结构

```
tcm-classics-assistant/
├── SKILL.md              # 核心技能定义
├── agents/
│   └── openai.yaml       # 元数据
├── references/
│   └── catalog.txt       # 分类目录
└── scripts/
    └── search_texts.py   # 搜索脚本
```
