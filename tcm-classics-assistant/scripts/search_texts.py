#!/usr/bin/env python3
"""Search 700+ TCM classical texts with relevance ranking.

Usage:
    python search_texts.py "<query>" [--max-results N] [--category CAT] [--json]
    python search_texts.py --keywords "A" "B" --mode all [--category CAT]
    python search_texts.py --list-categories / --list-texts [CAT]
"""
import os, re, sys, argparse, json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TXT_DIR = Path(os.environ.get("TCM_TXT_DIR", str(SKILL_DIR.parent / "中医古籍700本TXT")))

CATEGORIES = {
    "本草": ["本草","药性","药鉴","药征","药症","炮炙","炮制","食疗","食鉴","饮膳","滇南","海药","本经"],
    "方剂": ["方","汤头","剂录","良方","验方","秘方","集验","本事方","济生方","百一选","回生集"],
    "伤寒": ["伤寒","仲景"],
    "金匮": ["金匮"],
    "内经": ["内经","素问","灵枢","难经","黄帝","灵素","太素"],
    "温病": ["温病","温疫","温热","温症","时病","伏气","湿温","暑","霍乱","痧","疟"],
    "诊法": ["脉","诊","望","闻","问","舌","四诊"],
    "女科": ["女科","妇人","产科","产宝","济生集","傅青主"],
    "儿科": ["儿科","幼科","婴童","小儿","痘","种痘","麻科","片玉"],
    "外科": ["外科","疡医","疮疡","痈","正骨","伤科","跌打","金疮","仙授"],
    "针灸": ["针灸","经穴","经脉","经络","刺血","十四经","针经","灸法"],
    "医案": ["医案","医话","医验","经验集","临证经验","临证验案","经方实验"],
    "综合医论": ["医论","医说","医贯","医通","医宗","医旨","医法","医镜","医述","医门",
                 "医学","医林","辨证","证治","石室秘录","医碥","儒门事亲","兰室秘藏",
                 "脾胃论","格致","丹溪","万病回春","古今医","医经","此事难知","玉机微义","明医"],
    "眼科": ["眼科","目经"],
    "喉科": ["喉"],
    "养生": ["养生","摄生","延年","导引","气功","丹","仙","道藏"],
    "医史": ["医籍考","名老中医"],
    "现代": ["思考中医","中医之钥","民间","澄空"],
}

HELP_MSG = """========================================
  TCM古籍未找到！
  请放置到: {txt_dir}
  或: $env:TCM_TXT_DIR = "你的路径"
========================================
"""

def die(msg): print(msg.format(txt_dir=TXT_DIR), file=sys.stderr); sys.exit(1)

def detect_encoding(fp):
    with open(fp, 'rb') as f: h = f.read(4)
    if h[:3] == b'\xef\xbb\xbf': return 'utf-8-sig'
    if h[:2] == b'\xff\xfe':     return 'utf-16-le'
    if h[:2] == b'\xfe\xff':     return 'utf-16-be'
    return 'gbk'

def read_file(fp):
    text = open(fp, 'r', encoding=detect_encoding(fp), errors='replace').read()
    # Strip BOM and null chars
    return text.replace('\ufeff', '').replace('\x00', '')

def get_category(fname):
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            if kw in fname: return cat
    return "其他"

def build_files(category=None):
    fs = [(f, f.stem, get_category(f.name)) for f in TXT_DIR.glob("*.txt")
          if not category or get_category(f.name) == category]
    return sorted(fs, key=lambda x: x[1])

def ensure_dir():
    if not TXT_DIR.exists() or not list(TXT_DIR.glob("*.txt")): die(HELP_MSG)

# ---- relevance ----

def score_match(query, content, pos, fname):
    s = 0
    s += 10 if query in content else 0
    window = content[max(0,pos-200):min(len(content),pos+200)]
    s += min(window.count(query), 8) * 2
    s += int(max(0, 1.0 - pos/max(len(content),1)) * 15)
    if query in fname: s += 12
    return s

def best_snippet(content, pos, qlen):
    start = max(0, pos - 200)
    end = min(len(content), pos + qlen + 300)
    # Extend to paragraph boundaries
    before = content.rfind('\n\n', 0, start)
    start = max(0, before+2) if before >= 0 else start
    after = content.find('\n\n', end)
    end = after if after >= 0 else end
    snip = content[start:end].strip()
    return snip[:800] + ("\n  ..." if len(snip)>800 else "")

# ---- search ----

def search(query, max_results=15, category=None):
    ensure_dir()
    raw = []
    for fp, name, cat in build_files(category):
        try: content = read_file(fp)
        except: continue
        if query not in content: continue
        for m in re.finditer(re.escape(query), content):
            pos = m.start()
            raw.append({
                'file':name, 'category':cat,
                'score':score_match(query, content, pos, name),
                'snippet':best_snippet(content, pos, len(query))
            })
    if not raw: return []
    raw.sort(key=lambda x:-x['score'])
    # Per-file: keep top 2, dedup by snippet prefix
    seen = {}; uniq = []
    for r in raw:
        fn = r['file']
        seen.setdefault(fn, 0)
        if seen[fn] >= 2: continue
        if any(p['file']==fn and p['snippet'][:80]==r['snippet'][:80] for p in uniq): continue
        seen[fn] += 1; uniq.append(r)
        if len(uniq) >= max_results: break
    return [{'file':r['file'],'category':r['category'],'snippet':r['snippet']} for r in uniq]

def search_multi(keywords, max_results=20, category=None, mode="any"):
    ensure_dir()
    results = []
    for fp, name, cat in build_files(category):
        try: content = read_file(fp)
        except: continue
        if mode=="all":
            if not all(kw in content for kw in keywords): continue
        else:
            if not any(kw in content for kw in keywords): continue
        # Score by combined density, penalize extremely common hits
        score = sum(content.count(kw) for kw in keywords)
        # Skip files with excessive matches (>500 matches = too generic)
        if score > 500: continue
        best = min((content.find(kw), kw) for kw in keywords if kw in content)
        pos, kw = best
        results.append({'file':name,'category':cat,'score':score,
                        'snippet':best_snippet(content, pos, len(kw))})
    results.sort(key=lambda x:-x['score'])
    per_file = {}
    out = []
    for r in results:
        fn = r['file']
        if per_file.get(fn, 0) >= 1: continue
        if any(p['file']==fn and p['snippet'][:80]==r['snippet'][:80] for p in out): continue
        per_file[fn] = per_file.get(fn,0) + 1; out.append(r)
        if len(out) >= max_results: break
    return [{'file':r['file'],'category':r['category'],'snippet':r['snippet']} for r in out]

def list_cats():
    ensure_dir()
    cats = {}
    for _,_,c in build_files(): cats[c]=cats.get(c,0)+1
    return cats

def main():
    p = argparse.ArgumentParser(description="搜索中医古籍")
    p.add_argument("query", nargs="?")
    p.add_argument("--max-results","-n", type=int, default=15)
    p.add_argument("--category","-C")
    p.add_argument("--keywords","-k", nargs="+")
    p.add_argument("--mode","-m", choices=["any","all"], default="any")
    p.add_argument("--list-categories", action="store_true")
    p.add_argument("--list-texts", nargs="?", const="__ALL__")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    
    if args.list_categories:
        for cat,n in sorted(list_cats().items(), key=lambda x:-x[1]): print(f"  {cat}: {n}卷")
        return
    if args.list_texts is not None:
        for name,c in build_files(None if args.list_texts=="__ALL__" else args.list_texts):
            print(f"  [{c}] {name}")
        return
    if not args.query and not args.keywords: p.print_help(); return
    
    results = (search_multi(args.keywords, args.max_results, args.category, args.mode)
               if args.keywords
               else search(args.query, args.max_results, args.category))
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i,r in enumerate(results,1):
            print(f"\n{'='*55}\n  [{i}] [{r['category']}] {r['file']}\n{'='*55}")
            print(r['snippet'])
    if not results:
        q = args.query or ' '.join(args.keywords or [])
        print(f"\n未找到与'{q}'相关的结果。")

if __name__ == "__main__":
    main()
