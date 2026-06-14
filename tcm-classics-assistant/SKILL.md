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

Work with 700+ volumes of traditional Chinese medicine classical texts.

## Text Corpus

- **Location**: `../中医古籍700本TXT/`
- **Encoding**: GBK (majority), UTF-16LE, UTF-8-BOM (auto-detected)
- **Total**: 700+ classical medical texts spanning Han dynasty through Qing dynasty

### Primary Categories

| Category | Count | Key Contents |
|---|---|---|
| 本草 (Materia Medica) | 55 | 神农本草经, 本草纲目, 本草经集注, 新修本草, etc. |
| 方剂 (Formulas) | 111 | 伤寒杂病论, 千金方, 外台秘要, 太平惠民和剂局方, 汤头歌诀, etc. |
| 伤寒 (Shang Han) | 44 | 注解伤寒论, 伤寒论条辨, 伤寒来苏集, 伤寒贯珠集, etc. |
| 金匮 (Jin Gui) | 8 | 金匮要略注, 金匮方歌括, 金匮钩玄, etc. |
| 内经 (Nei Jing) | 30 | 黄帝内经素问, 灵枢, 难经, 类经, etc. |
| 温病 (Warm Disease) | 17 | 温病条辨, 温热论, 温疫论, 湿热病篇, etc. |
| 诊法 (Diagnostics) | 34 | 脉经, 濒湖脉学, 四诊抉微, 望诊遵经, etc. |
| 女科 (Gynecology) | 23 | 妇人大全良方, 傅青主女科, 女科要旨, etc. |
| 儿科 (Pediatrics) | 22 | 小儿药证直诀, 幼科发挥, 幼幼集成, etc. |
| 外科 (Surgery) | 23 | 外科正宗, 疡医大全, 正骨心法, etc. |
| 针灸 (Acupuncture) | 26 | 针灸甲乙经, 针灸大成, 十四经发挥, etc. |
| 医案 (Case Records) | 48 | 临证指南医案, 名医类案, 章次公医案, etc. |
| 综合医论 (General) | 60 | 景岳全书, 医宗金鉴, 证治准绳, 医学心悟, etc. |

## Search Tool

Use `scripts/search_texts.py` to locate relevant classical passages. Always run the search BEFORE attempting to answer TCM questions.

```
python scripts/search_texts.py "<query>" [--max-results 15] [--category CAT] [--json]
python scripts/search_texts.py --keywords "term1" "term2" --mode all [--category CAT]
python scripts/search_texts.py --list-categories
python scripts/search_texts.py --list-texts [CATEGORY]
```

### Search Strategy

1. **Single keyword**: for herbs, formulas, diseases, or specific concepts
   ```
   python scripts/search_texts.py "桂枝汤" --max-results 10
   ```

2. **Multi-keyword (all mode)**: narrow results when combining symptoms/herbs/diagnosis
   ```
   python scripts/search_texts.py --keywords "阴虚" "潮热" "盗汗" --mode all --max-results 5
   ```

3. **Category-filtered**: target specific domain texts
   ```
   python scripts/search_texts.py "头痛" --category 伤寒 --max-results 8
   ```

4. **Broad exploration**: when unsure where to look, omit category filter

### After searching, ALWAYS:
- Read the most relevant full text passage using `Get-Content` with proper encoding
- Cross-reference multiple texts from different eras/categories
- Cite the source text name and dynasty/author when presenting findings

## Domain Knowledge

### TCM Theoretical Framework

- **八纲辨证** (Eight-Principle Differentiation): 阴阳, 表里, 寒热, 虚实
- **脏腑辨证** (Zang-Fu Differentiation): 五脏 (心肝脾肺肾) + 六腑 (胆胃大肠小肠膀胱三焦)
- **六经辨证** (Six-Channel Differentiation): 太阳, 阳明, 少阳, 太阴, 少阴, 厥阴 — from 伤寒论
- **卫气营血辨证** (Four-Level Differentiation): 卫, 气, 营, 血 — from 温病学
- **气血津液辨证**: Qi, Blood, Body Fluids
- **病因** (Etiology): 六淫 (风,寒,暑,湿,燥,火) + 七情 (喜怒忧思悲恐惊)

### Key Classical Texts to Prioritize

| Era | Text | Author | Domain |
|---|---|---|---|
| 汉 | 神农本草经 | — | 本草 |
| 汉 | 伤寒杂病论 | 张仲景 | 方剂/伤寒 |
| 汉 | 黄帝内经 | — | 理论 |
| 战国 | 难经 | 扁鹊 | 理论 |
| 晋 | 脉经 | 王叔和 | 诊法 |
| 隋 | 诸病源候论 | 巢元方 | 病因 |
| 唐 | 千金要方/千金翼方 | 孙思邈 | 方剂 |
| 宋 | 太平惠民和剂局方 | 陈承 | 方剂 |
| 金元 | 脾胃论 | 李东垣 | 医论 |
| 明 | 本草纲目 | 李时珍 | 本草 |
| 清 | 温病条辨 | 吴鞠通 | 温病 |
| 清 | 医宗金鉴 | 吴谦 | 综合 |

### Answering Protocol

1. **Search**: Run `search_texts.py` on the user's question keywords
2. **Read**: Open 2-3 most relevant texts for full context
3. **Analyze**: Synthesize across multiple sources; note era differences
4. **Present**: Cite specific text + author, explain TCM rationale
5. **Cross-check**: When appropriate, search another category for corroborating views

### Important Notes

- Classical Chinese medical texts use specialized terminology that may differ from modern usage
- Ming-Qing era texts often comment on and refine earlier Han-Tang theories
- 本草 texts describe herbs (性味归经, 功效主治); 方剂 texts describe formula compositions
- Different medical schools (伤寒派, 温病派, 补土派, etc.) may have conflicting views — present both
- Always distinguish between classical theory and personal opinion
