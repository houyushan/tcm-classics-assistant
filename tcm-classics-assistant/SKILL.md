---
name: tcm-classics-assistant
description: >
  World-class TCM classical texts search engine with 700+ volumes. Four search modes:
  herb (草药性味归经), formula (方剂组成剂量), disease (病症历代辨治),
  differential (多源辨证对照). Covers materia medica, formulas, Shang Han Lun,
  Jin Gui Yao Lue, Nei Jing, warm disease, pulse diagnosis, acupuncture,
  case records, and comprehensive medical treatises from Han to Qing.
  Use for any TCM question: herbal properties, formula composition, disease
  patterns, differential diagnosis, acupuncture points, medical history.
  Keywords: 中医, 中药, 本草, 方剂, 伤寒, 金匮, 内经, 针灸, 经络, 脉诊, 温病,
  辨证, herbs, acupuncture, TCM, Chinese medicine, 草药, 经方, 醫案, 诊断, 治疗.
---

# TCM Classics Assistant — World-Class

Search 700+ volumes of TCM classical texts with four specialized search modes and
a 理→法→方→药 thinking chain.

## Quick Setup

```powershell
# Place TXT files next to this skill, or set env var:
$env:TCM_TXT_DIR = "path/to/中医古籍700本TXT"

# (Optional) Build index for instant metadata lookup:
python scripts/build_index.py
```

## Search Modes

Route the user's question to the right mode:

| User Question Type | Mode | Command |
|---|---|---|
| "人参的功效？" "当归性味归经？" | `herb` | `--mode herb "人参"` |
| "桂枝汤组成？" "四物汤剂量？" | `formula` | `--mode formula "桂枝汤"` |
| "头痛怎么治？" "咳嗽的辨证？" | `disease` | `--mode disease "咳嗽"` |
| "头痛发热恶寒无汗" (多症状) | `differential` | `--keywords A B C --mode differential` |
| General TCM theory | `full` (default) | `"query"` |

```bash
python scripts/search_texts.py "人参" --mode herb -n 8      # herb properties
python scripts/search_texts.py "四物汤" --mode formula -n 6  # formula composition
python scripts/search_texts.py "眩晕" --mode disease -n 10   # disease patterns
python scripts/search_texts.py -k "头痛" "发热" "恶寒" --mode differential  # cross-reference
python scripts/search_texts.py --list-categories              # browse corpus
```

### Mode Details

**herb** — Searches 本草 texts only (55 volumes). Prioritizes primary sources
(神农本草经, 本草纲目). Extracts 性味, 归经, 功效, 主治, 禁忌, 炮制.

**formula** — Searches all categories, prioritizes texts with dosage info (两/钱/分).
Boosts Han-Tang originals. Flags results with exact ingredient amounts.

**disease** — Priority order: 伤寒→金匮→温病→综合→医案→方剂→诊法.
Scores by clinical relevance markers (脉/证/治/主之). Per-category diversity.

**differential** — Requires all keywords present. Scores by keyword proximity.
Cross-references across 伤寒, 金匮, 温病, 综合医论, 医案 in parallel.
This is the go-to mode for syndrome differentiation (辨证论治).

## TCM Thinking Chain: 理 → 法 → 方 → 药

For any clinical TCM question, follow this 4-step chain:

### 1. 理 (Principle) — Identify the pattern
- Search symptoms with `--mode disease` or `--mode differential`
- Determine: 八纲 (阴阳表里寒热虚实) + 病位 (脏腑/六经/卫气营血) + 病性
- Cross-reference at least 2 different categories (e.g., 伤寒 + 综合医论)

### 2. 法 (Method) — Derive the treatment principle
- From the pattern, derive: 汗/吐/下/和/温/清/消/补
- Cite texts that establish the treatment method for this pattern
- Note differing opinions across medical schools (伤寒派 vs 温病派 vs 补土派)

### 3. 方 (Formula) — Select the formula
- Search with `--mode formula` for the candidate formula
- Verify composition, dosage, and preparation method
- Prefer primary sources (仲景原文) over later commentaries
- Check if the formula has variants (加减方) for specific presentations

### 4. 药 (Herb) — Analyze key herbs
- Search with `--mode herb` for the sovereign herb (君药)
- Extract 性味归经, verify it matches the pattern
- Note herb interactions (配伍), contraindications (禁忌), processing (炮制)

## Citation Quality

Rank sources by authority when presenting findings:

| Tier | Criteria | Examples |
|---|---|---|
| ⭐⭐⭐ 一级 | Original classics, Han-Tang | 神农本草经, 伤寒杂病论, 黄帝内经 |
| ⭐⭐ 二级 | Major commentaries, Song-Yuan | 注解伤寒论, 本草纲目, 脾胃论 |
| ⭐ 三级 | Later compilations, Qing | 医宗金鉴, 温病条辨, 临证指南医案 |

Always cite: **书名 · 朝代 · 作者** for every claim.

## Important Rules

- Never claim the text corpus replaces clinical diagnosis (望闻问切)
- When medical schools disagree, present both views, note which school each represents
- Classical texts use era-specific terminology — clarify when a term's meaning changed
- Herbs may have different names across dynasties — verify via 本草纲目·释名
- For safety-critical questions, explicitly state: "此为古籍文献参考，具体诊疗请咨询执业中医师"
