---
name: tcm-classics-assistant
description: >
  Search and reference 700+ volumes of Chinese medicine (TCM) classical texts spanning
  materia medica (本草), herbal formulas (方剂), Shang Han Lun (伤寒论), Jin Gui Yao Lue
  (金匮要略), Huang Di Nei Jing (黄帝内经), warm disease (温病), pulse diagnosis (诊法),
  gynecology (女科), pediatrics (儿科), surgery (外科), acupuncture/meridians (针灸经络),
  medical case records (医案), and comprehensive medical treatises (综合医论).
  Use when the user asks about traditional Chinese medicine, Chinese herbal medicine,
  acupuncture, TCM theory, classical formulas (经方/时方), syndrome differentiation
  (辨证论治), Chinese medical history, or any TCM-related diagnosis and treatment.
  Keywords: 中医, 中药, 本草, 方剂, 伤寒, 金匮, 内经, 针灸, 经络, 脉诊, 温病, 辨证,
  herbs, acupuncture, TCM, Chinese medicine, 草药, 经方, 醫案.
---

# TCM Classics Assistant

Search 700+ volumes of TCM classical texts (汉 through 清 dynasty).

## Setup

古籍 TXT 文件需放在此 skill 同级的 `中医古籍700本TXT/`，或设 `$env:TCM_TXT_DIR`。

## Search

**Always search before answering.** The search tool auto-detects encoding (GBK/UTF-16LE/UTF-8).

```bash
# Single keyword
python scripts/search_texts.py "桂枝汤" --max-results 10

# Multi-keyword (all required)
python scripts/search_texts.py --keywords "阴虚" "潮热" "盗汗" --mode all

# Category filter (本草/方剂/伤寒/金匮/内经/温病/诊法/女科/儿科/外科/针灸/医案/综合医论/眼科/喉科/养生)
python scripts/search_texts.py "头痛" --category 伤寒

# Browse
python scripts/search_texts.py --list-categories
python scripts/search_texts.py --list-texts 本草
```

## Workflow

1. **Search**: run `search_texts.py` with the user's key terms
2. **Read**: pick 2-3 top-ranking results, `Get-Content` the full passage
3. **Cross-reference**: search a second category for corroborating views (e.g. 本草 + 方剂, or 伤寒 + 医案)
4. **Present**: cite source (书名-朝代-作者), explain TCM rationale, note era differences

## Corpus

| Category | ~Volumes | Top texts |
|---|---|---|
| 本草 | 55 | 神农本草经, 本草纲目, 本草经集注 |
| 方剂 | 111 | 伤寒杂病论, 千金要方, 外台秘要, 太平惠民和剂局方 |
| 伤寒 | 44 | 注解伤寒论, 伤寒来苏集, 伤寒贯珠集 |
| 金匮 | 8 | 金匮要略注, 金匮钩玄 |
| 内经 | 30 | 黄帝内经素问, 灵枢, 难经, 类经 |
| 温病 | 17 | 温病条辨, 温热论, 温疫论 |
| 诊法 | 34 | 脉经, 濒湖脉学, 四诊抉微 |
| 针灸 | 26 | 针灸甲乙经, 针灸大成 |
| 医案 | 48 | 临证指南医案, 名医类案 |
| 综合医论 | 60 | 景岳全书, 医宗金鉴, 证治准绳, 医学心悟 |
| 其他 | 130+ | 女科, 儿科, 外科, 眼科, 喉科, 养生 |

## Notes

- Prefer authoritative texts: 伤寒→张仲景原本, 本草→神农本草经/本草纲目, 诊断→脉经/濒湖脉学
- Ming-Qing texts often critique Han-Tang theories — present both perspectives
- Different medical schools may conflict — note the school (伤寒派/温病派/补土派 etc.)
- Use `--json` for machine-readable output when chaining searches
