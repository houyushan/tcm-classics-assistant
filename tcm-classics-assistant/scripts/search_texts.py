#!/usr/bin/env python3
"""
TCM Classics Search Engine — World-class TCM text retrieval.

Modes:
  --mode herb      草药查询：搜本草文献，提取性味归经功效主治
  --mode formula   方剂查询：搜方书，提取组成、功效、主治
  --mode disease   病症查询：搜病机证候，给出历代辨治论述
  --mode differential  辨证查询：多源交叉对照，梳理各家异同
  --mode full      全文搜索（默认）

Usage:
  python search_texts.py "<query>" --mode herb [--dynasty 唐] [--json]
  python search_texts.py --keywords "头痛" "发热" --mode disease
  python search_texts.py --list-categories / --list-texts
"""
import os, re, sys, json, time, argparse
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TXT_DIR = Path(os.environ.get("TCM_TXT_DIR", str(SKILL_DIR.parent / "中医古籍700本TXT")))
INDEX_PATH = SCRIPT_DIR / "tcm_index.json"

# -- load index --

_index = None

def load_index():
    global _index
    if _index is not None: return _index
    if INDEX_PATH.exists():
        try:
            _index = json.loads(INDEX_PATH.read_text(encoding='utf-8'))
            return _index
        except: pass
    return None

# -- encoding --

def detect_encoding(fp):
    with open(fp, 'rb') as f: h = f.read(4)
    if h[:3] == b'\xef\xbb\xbf': return 'utf-8-sig'
    if h[:2] == b'\xff\xfe':     return 'utf-16-le'
    if h[:2] == b'\xfe\xff':     return 'utf-16-be'
    return 'gbk'

def read_file(fp):
    return open(fp, 'r', encoding=detect_encoding(fp), errors='replace').read().replace('\ufeff','').replace('\x00','')

def ensure_dir():
    if not TXT_DIR.exists() or not list(TXT_DIR.glob("*.txt")):
        print(f"\n古籍未找到: {TXT_DIR}\n设 $env:TCM_TXT_DIR 指向你的古籍目录", file=sys.stderr)
        sys.exit(1)

# -- categories and filtering --

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

# Dynasty priority for authoritative texts
DYNASTY_RANK = {"汉":10,"晋":9,"唐":9,"宋":8,"金":8,"元":8,"明":7,"清":7}

def categorize(fname): 
    for c,k in CATEGORIES.items():
        for kw in k:
            if kw in fname: return c
    return "其他"

def get_files(category=None, dynasties=None):
    """Get file list, optionally using index for filtering."""
    idx = load_index()
    files = []
    if idx:
        for entry in idx["files"]:
            if category and entry["category"] != category: continue
            if dynasties and entry["dynasty"] not in dynasties: continue
            fp = TXT_DIR / entry["filename"]
            if fp.exists():
                files.append((fp, entry["stem"], entry["category"], entry.get("dynasty",""), entry.get("author","")))
    else:
        for fp in TXT_DIR.glob("*.txt"):
            c = categorize(fp.name)
            if category and c != category: continue
            files.append((fp, fp.stem, c, "", ""))
    return sorted(files, key=lambda x: x[1])

def sort_by_authority(files):
    """Rank files: primary sources (汉唐) > commentaries (宋元) > later (明清)."""
    def rank(f):
        dyn = f[3]
        return DYNASTY_RANK.get(dyn, 5)
    return sorted(files, key=lambda f: -rank(f))

# -- snippet extraction --

def best_snippet(content, pos, qlen, target_term=None):
    """Extract paragraph around match, extending to section boundaries."""
    start = max(0, pos - 150)
    end = min(len(content), pos + qlen + 300)
    before = content.rfind('\n\n', 0, start)
    start = max(0, before+2) if before >= 0 else start
    after = content.find('\n\n', end)
    end = after if after >= 0 else end
    snip = content[start:end].strip()
    # Highlight the search term if provided
    return snip[:1000] + ("\n  ..." if len(snip)>1000 else "")

# -- HERB mode --

def search_herb(query, max_results=10):
    """Search for herb information in 本草 texts."""
    files = get_files(category="本草")
    files = sort_by_authority(files)
    results = []
    
    for fp, name, cat, dyn, auth in files:
        try: content = read_file(fp)
        except: continue
        if query not in content: continue
        
        # Find all matches and their contexts
        for m in re.finditer(re.escape(query), content):
            pos = m.start()
            ctx = best_snippet(content, pos, len(query))
            # Score: higher for earlier matches (usually definition section)
            score = 1.0 - (pos / max(len(content), 1))
            # Boost if near 性味/归经/主治 keywords
            nearby = content[max(0,pos-100):pos+len(query)+100]
            for kw in ['味','性','归经','主治','功效','治','主','无毒','有毒','大毒','小毒']:
                if kw in nearby: score += 0.2
            
            results.append({
                'file': name, 'category': cat, 'dynasty': dyn, 'author': auth,
                'score': score, 'snippet': ctx
            })
    
    # Deduplicate and sort
    results.sort(key=lambda r: -r['score'])
    seen = set(); uniq = []
    for r in results:
        key = r['snippet'][:100]
        if key in seen: continue
        seen.add(key); uniq.append(r)
        if len(uniq) >= max_results: break
    
    return [{'file':r['file'],'dynasty':r['dynasty'],'author':r['author'],
             'category':r['category'],'snippet':r['snippet']} for r in uniq]

# -- FORMULA mode --

FORMULA_HEADERS = re.compile(
    r'([\u4e00-\u9fff]{2,10}(?:汤|散|丸|丹|饮|膏|煎))'
    r'[\s\S]{0,100}?(?:方|组成|\n[\u4e00-\u9fff()（）\d两钱分斤枚个片克升合])'
)

def search_formula(query, max_results=10):
    """Search for formula composition and usage."""
    files = get_files(category=None)  # search all categories for formulas
    files = sort_by_authority(files)
    results = []
    
    for fp, name, cat, dyn, auth in files:
        try: content = read_file(fp)
        except: continue
        if query not in content: continue
        
        # Find formula entries (structured look)
        for m in re.finditer(re.escape(query), content):
            pos = m.start()
            # Look backward for the formula header
            header_start = max(0, pos - 30)
            header = content[header_start:pos].strip()
            # Extract full context
            ctx = best_snippet(content, pos, len(query))
            # Heuristic: formulas usually have ingredient lists with 两/钱/分
            nearby = content[pos:pos+500]
            has_dosage = bool(re.search(r'[一两钱分斤枚个片升合]', nearby))
            
            results.append({
                'file': name, 'category': cat, 'dynasty': dyn, 'author': auth,
                'score': (2 if has_dosage else 1) + (10 if dyn in ['汉','唐'] else 5),
                'has_dosage': has_dosage,
                'snippet': ctx
            })
    
    results.sort(key=lambda r: (-r['has_dosage'], -r['score']))
    seen = set(); uniq = []
    for r in results:
        key = r['snippet'][:100]
        if key in seen: continue
        seen.add(key); uniq.append(r)
        if len(uniq) >= max_results: break
    
    return [{'file':r['file'],'dynasty':r['dynasty'],'author':r['author'],
             'category':r['category'],'snippet':r['snippet'],
             'has_dosage':r['has_dosage']} for r in uniq]

# -- DISEASE mode --

def search_disease(query, max_results=12):
    """Search for disease patterns across 伤寒/金匮/温病/综合."""
    # Priority categories for disease queries
    priority_cats = ["伤寒","金匮","温病","综合医论","医案","方剂","诊法"]
    results = []
    
    for cat in priority_cats:
        files = get_files(category=cat)
        files = sort_by_authority(files)
        
        for fp, name, _, dyn, auth in files:
            try: content = read_file(fp)
            except: continue
            if query not in content: continue
            
            for m in re.finditer(re.escape(query), content):
                pos = m.start()
                ctx = best_snippet(content, pos, len(query))
                
                # Relevance scoring for disease context
                score = 0
                nearby = content[max(0,pos-100):pos+len(query)+200]
                # Clinical relevance markers
                for kw in ['脉','证','治','主之','宜','与','方']:
                    if kw in nearby: score += 1
                if any(kw in nearby for kw in ['发热','恶寒','汗','痛','渴','烦','呕']):
                    score += 3
                
                results.append({
                    'file': name, 'category': cat, 'dynasty': dyn, 'author': auth,
                    'score': score, 'snippet': ctx
                })
    
    results.sort(key=lambda r: -r['score'])
    # Per-category: keep best 2
    seen_cat = {}; uniq = []
    for r in results:
        c = r['category']
        seen_cat[c] = seen_cat.get(c, 0) + 1
        if seen_cat[c] > 2: continue
        key = r['snippet'][:100]
        if key in [u['snippet'][:100] for u in uniq]: continue
        uniq.append(r)
        if len(uniq) >= max_results: break
    
    return [{'file':r['file'],'dynasty':r['dynasty'],'author':r['author'],
             'category':r['category'],'snippet':r['snippet']} for r in uniq]

# -- DIFFERENTIAL mode --

def search_differential(keywords, max_results=15):
    """Cross-reference multiple sources for differential diagnosis."""
    results = []
    cats_to_search = ["伤寒","金匮","温病","综合医论","医案","诊法"]
    
    for cat in cats_to_search:
        files = get_files(category=cat)
        files = sort_by_authority(files)
        
        for fp, name, _, dyn, auth in files:
            try: content = read_file(fp)
            except: continue
            
            matches = sum(1 for kw in keywords if kw in content)
            if matches < len(keywords): continue
            
            # Find best context
            best_pos = 0; best_score = 0
            for kw in keywords:
                for m in re.finditer(re.escape(kw), content):
                    pos = m.start()
                    # Score: proximity of all keywords
                    nearby = content[max(0,pos-300):pos+len(kw)+300]
                    kw_score = sum(nearby.count(k) for k in keywords) * 3
                    if kw_score > best_score:
                        best_score = kw_score
                        best_pos = pos
            
            ctx = best_snippet(content, best_pos, len(keywords[0]))
            
            results.append({
                'file': name, 'category': cat, 'dynasty': dyn, 'author': auth,
                'score': best_score, 'snippet': ctx
            })
    
    results.sort(key=lambda r: -r['score'])
    seen = set(); uniq = []
    for r in results:
        key = r['snippet'][:100]
        if key in seen: continue
        seen.add(key); uniq.append(r)
        if len(uniq) >= max_results: break
    
    return [{'file':r['file'],'dynasty':r['dynasty'],'author':r['author'],
             'category':r['category'],'snippet':r['snippet']} for r in uniq]

# -- FULL TEXT mode (default) --

def search_full(query, max_results=15, category=None, dynasties=None):
    """Full-text search across all texts with relevance ranking."""
    files = get_files(category, dynasties)
    results = []
    
    for fp, name, cat, dyn, auth in files:
        try: content = read_file(fp)
        except: continue
        if query not in content: continue
        
        for m in re.finditer(re.escape(query), content):
            pos = m.start()
            count = content.count(query)
            # Score
            score = 0
            score += min(count, 20)
            score += int(max(0, 1.0 - pos/max(len(content),1)) * 10)
            score += DYNASTY_RANK.get(dyn, 5)
            
            ctx = best_snippet(content, pos, len(query))
            results.append({
                'file': name, 'category': cat, 'dynasty': dyn, 'author': auth,
                'score': score, 'snippet': ctx
            })
    
    results.sort(key=lambda r: -r['score'])
    seen_files = {}; uniq = []
    for r in results:
        fn = r['file']
        seen_files[fn] = seen_files.get(fn, 0) + 1
        if seen_files[fn] > 2: continue
        key = r['snippet'][:100]
        if key in [u['snippet'][:100] for u in uniq]: continue
        uniq.append(r)
        if len(uniq) >= max_results: break
    
    return [{'file':r['file'],'dynasty':r['dynasty'],'author':r['author'],
             'category':r['category'],'snippet':r['snippet']} for r in uniq]

# -- output --

def print_results(results, mode=""):
    if not results:
        print("\n无匹配结果。")
        return
    header = {"herb":"草药查询","formula":"方剂查询","disease":"病症查询",
              "differential":"辨证对照","full":"全文搜索"}.get(mode, mode)
    print(f"\n{'='*60}")
    print(f"  {header}  ·  {len(results)} 条结果")
    print(f"{'='*60}")
    
    for i, r in enumerate(results, 1):
        dyn = f" · {r.get('dynasty','')}" if r.get('dynasty') else ""
        auth = f" · {r.get('author','')}" if r.get('author') else ""
        dosage = " [剂量]含剂量" if r.get('has_dosage') else ""
        print(f"\n── [{i}] [{r['category']}]{dyn}{auth} ── {r['file']}{dosage}")
        print(r['snippet'])

# -- CLI --


def print_status():
    """Print skill readiness status."""
    idx = load_index()
    txt_ok = TXT_DIR.exists() and bool(list(TXT_DIR.glob("*.txt")))
    
    print()
    print("  ========================================")
    print("   中医古籍助手 - 状态检查")
    print("  ========================================")
    
    if txt_ok:
        count = len(list(TXT_DIR.glob("*.txt")))
        size_mb = round(sum(f.stat().st_size for f in TXT_DIR.glob("*.txt")) / (1024*1024), 1)
        print(f"  古籍文本  [OK] {count} 文件, {size_mb} MB")
        print(f"  文本目录    {TXT_DIR}")
    else:
        print("  古籍文本  [MISSING]")
        print(f"  预期目录    {TXT_DIR}")
        print("  请将 700 本 TXT 放入该目录，或设置 TCM_TXT_DIR 环境变量")
    
    if idx:
        print(f"  搜索索引  [OK] {idx['total_files']} 文件已索引, {idx['total_size_mb']} MB")
        print(f"  构建时间    {idx.get('build_time','unknown')}")
    else:
        print("  搜索索引  [NOT BUILT] 运行 build_index.py 以加速搜索")
    
    if idx:
        cats = idx.get("categories", {})
        major = sorted(cats.items(), key=lambda x: -x[1])
        top5 = " | ".join(f"{c}:{n}" for c, n in major[:5])
        print(f"  分类({len(major)}):  {top5} ...")
    
    print()
    print("  使用方式: 在 Codex 中用中文提问中医相关问题即可自动触发")
    print("  手动搜索: python scripts/search_texts.py '<关键词>' --mode herb|formula|disease|differential")
    print("  ========================================")
    print()


def main():
    # Force UTF-8 output on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    p = argparse.ArgumentParser(description="TCM古籍搜索引擎")
    p.add_argument("query", nargs="?")
    p.add_argument("--mode","-M", choices=["herb","formula","disease","differential","full"], default="full",
                   help="搜索模式: herb/formula/disease/differential/full")
    p.add_argument("--max-results","-n", type=int, default=12)
    p.add_argument("--category","-C")
    p.add_argument("--dynasty","-d", help="朝代过滤 (汉/唐/宋/金/元/明/清), 逗号分隔")
    p.add_argument("--keywords","-k", nargs="+")
    p.add_argument("--json", action="store_true")
    p.add_argument("--list-categories", action="store_true")
    p.add_argument("--list-texts", nargs="?", const="__ALL__")
    p.add_argument("--status", action="store_true", help="Check if skill is ready to use")
    p.add_argument("--build-index", action="store_true", help="(Re)build search index")
    args = p.parse_args()
    
    # Status check
    if args.status:
        print_status()
        return

    # Build index
    if args.build_index:
        from build_index import build_index
        build_index()
        return
    
    # List modes (no TXT dir needed for index-based listing)
    if args.list_categories:
        idx = load_index()
        if idx:
            for c,n in sorted(idx["categories"].items(), key=lambda x:-x[1]):
                print(f"  {c}: {n}卷")
        else:
            ensure_dir()
            cats = {}
            for _,_,c in get_files(): cats[c]=cats.get(c,0)+1
            for c,n in sorted(cats.items(), key=lambda x:-x[1]): print(f"  {c}: {n}卷")
        return
    
    if args.list_texts is not None:
        idx = load_index()
        if idx:
            cat = None if args.list_texts=="__ALL__" else args.list_texts
            for e in idx["files"]:
                if cat and e["category"]!=cat: continue
                print(f"  [{e['category']}] {e['filename']}")
        else:
            ensure_dir(); cat = None if args.list_texts=="__ALL__" else args.list_texts
            for n,c in [(fp.stem,c) for fp,_,c in get_files(cat)]: print(f"  [{c}] {n}")
        return
    
    if not args.query and not args.keywords:
        p.print_help()
        return
    
    ensure_dir()
    
    dynasties = None
    if args.dynasty:
        dynasties = set(args.dynasty.split(","))
    
    # Route to mode
    mode = args.mode
    if args.keywords and mode == "full":
        mode = "differential"  # multi-keyword default → differential
    
    if mode == "herb":
        results = search_herb(args.query, args.max_results)
    elif mode == "formula":
        results = search_formula(args.query, args.max_results)
    elif mode == "disease":
        results = search_disease(args.query, args.max_results)
    elif mode == "differential":
        kws = args.keywords or [args.query]
        results = search_differential(kws, args.max_results)
    else:
        results = search_full(args.query, args.max_results, args.category, dynasties)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_results(results, mode)

if __name__ == "__main__":
    main()
