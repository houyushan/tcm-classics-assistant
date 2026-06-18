# 中医古籍助手 (TCM Classics Assistant)

基于 700+ 卷中医古籍经典文献的 Codex 技能助手，全文搜索 + 理法方药思维链。

## 一键安装

```powershell
# 1. 克隆仓库（含700本古籍原文，约146MB）
git clone https://github.com/houyushan/tcm-classics-assistant.git "$env:USERPROFILE\.codex\skills\tcm-classics-assistant"

# 2. 构建搜索索引（加速搜索，仅需一次）
python "$env:USERPROFILE\.codex\skills\tcm-classics-assistant\scripts\build_index.py"

# 3. 验证安装
python "$env:USERPROFILE\.codex\skills\tcm-classics-assistant\scripts\search_texts.py" --status
```

重启 Codex 即可。

## 手动搜索

```bash
# 草药查询：性味 / 归经 / 功效 / 主治 / 禁忌
python scripts/search_texts.py "人参" --mode herb -n 8

# 方剂查询：组成 / 剂量 / 煎服法
python scripts/search_texts.py "桂枝汤" --mode formula -n 6

# 病症查询：历代辨治论述（伤寒→金匮→温病→综合→医案）
python scripts/search_texts.py "咳嗽" --mode disease -n 10

# 辨证对照：多症状交叉引用（必须全部关键词出现）
python scripts/search_texts.py -k "头痛" "发热" "恶寒" "无汗" --mode differential

# 全文搜索（默认）
python scripts/search_texts.py "阴阳"

# 状态检查
python scripts/search_texts.py --status
```

## 覆盖范围

| 分类 | 卷数 | 代表著作 |
|---|---|---|
| 本草 | 55 | 神农本草经、本草纲目、本草经集注 |
| 方剂 | 110 | 伤寒杂病论、千金要方、外台秘要 |
| 伤寒 | 44 | 注解伤寒论、伤寒来苏集、伤寒贯珠集 |
| 金匮 | 8 | 金匮要略注、金匮钩玄 |
| 内经 | 31 | 黄帝内经素问、灵枢、难经、类经 |
| 温病 | 17 | 温病条辨、温热论、温疫论 |
| 诊法 | 33 | 脉经、濒湖脉学、四诊抉微 |
| 针灸 | 24 | 针灸甲乙经、针灸大成、十四经发挥 |
| 医案 | 48 | 临证指南医案、名医类案 |
| 综合医论 | 65 | 景岳全书、医宗金鉴、证治准绳 |
| 女科/儿科/外科等 | 120+ | 妇人大全良方、小儿药证直诀、外科正宗 |

## 文件结构

```
tcm-classics-assistant/
├── SKILL.md                    # 技能定义 & TCM 专家思维链
├── agents/openai.yaml          # 元数据
├── references/catalog.txt      # 692 卷分类目录
├── scripts/
│   ├── build_index.py          # 构建搜索索引
│   ├── search_texts.py         # 四模式搜索引擎
│   └── tcm_index.json          # 本地索引（gitignore）
└── 中医古籍700本TXT/           # 700+ 卷古籍原文
    ├── 000-神农本草经-清-孙星衍.txt
    ├── 013-本草纲目-明-李时珍.txt
    └── ...
```
