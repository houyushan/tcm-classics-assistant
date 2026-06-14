#!/usr/bin/env python3
"""Build search index for TCM classical texts.

Creates a JSON index file with per-file metadata and key term extraction.
Run once; the search engine uses this index for instant queries.

Usage:
    python build_index.py [--output index.json] [--txt-dir PATH]
"""
import os, re, sys, json, time, argparse
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TXT_DIR = Path(os.environ.get("TCM_TXT_DIR", str(SKILL_DIR.parent / "中医古籍700本TXT")))
INDEX_PATH = SCRIPT_DIR / "tcm_index.json"

# -- encoding --

def detect_encoding(fp):
    with open(fp, 'rb') as f: h = f.read(4)
    if h[:3] == b'\xef\xbb\xbf': return 'utf-8-sig'
    if h[:2] == b'\xff\xfe':     return 'utf-16-le'
    if h[:2] == b'\xfe\xff':     return 'utf-16-be'
    return 'gbk'

def read_file(fp):
    text = open(fp, 'r', encoding=detect_encoding(fp), errors='replace').read()
    return text.replace('\ufeff','').replace('\x00','')

# -- text analysis --

# TCM-relevant patterns
HERB_PATTERN = re.compile(
    r'(?:[故治主疗][以用]?|宜|与|方用?|加|减|去|倍)\s*'
    r'([\u4e00-\u9fff]{1,4}(?:子|草|花|叶|根|皮|仁|参|术|苓|芪|归|芎|芍|地|连|芩|柏|栀|附|桂|麻|葛|柴|薄|姜|枣|甘|辛|夏|陈|枳|朴|杏|桔|前|菀|款|紫|款|贝|蒌|桑|菊|银|翘|荆|防|羌|独|芷|藁|蔓|秦|艽|威|己|乌|藤|龙|牡|赭|琥|琥|珍|母|决|明|蒙|蒺|藜|青|葙|密|蝉|蜕|僵|蚕|蝎|蜈|地|蛇|腥|败|酱|蒲|公|英|鱼|腥|金|荞|麦|穿|心|莲|半|枝|莲|白|花|蛇|舌|草|半|边|莲|重|楼|拳|参|土|茯|苓|菝|葜|猫|爪|草|猫|人|参|猪|苓|泽|泻|茯|苓|薏|苡|车|前|滑|石|木|通|通|草|金|钱|海|金|沙|石|韦|萹|蓄|瞿|麦|萆|薢|茵|陈|虎|杖|地|耳|草|垂|盆|鸡|骨|大|黄|芒|硝|番|泻|芦|荟|火|麻|郁|李|甘|遂|大|戟|芫|花|商|陆|牵|牛|巴|豆|独|活|威|灵|川|乌|草|乌|蕲|蛇|乌|梢|蛇|木|瓜|蚕|沙|伸|筋|海|风|藤|青|风|藤|路|路|通|秦|艽|防|己|桑|枝|豨|莶|臭|梧|桐|海|桐|皮|络|石|藤|雷|公|藤|老|鹳|草|丝|瓜|络|桑|寄|生|五|加|皮|狗|脊|千|年|健|雪|莲|花|鹿|衔|草|石|楠|叶|藿|香|佩|兰|苍|术|厚|朴|砂|仁|白|豆|蔻|草|豆|蔻|草|果|茯|苓|猪|苓|泽|泻|薏|苡|仁|车|前|子|滑|石|川|木|通|通|草|金|钱|草|海|金|沙|石|韦|萹|蓄|瞿|麦|萆|薢|茵|陈|虎|杖|地|耳|草|垂|盆))'
)

FORMULA_PATTERN = re.compile(
    r'([\u4e00-\u9fff]{2,8}(?:汤|散|丸|丹|饮|膏|煎|方|剂|法))'
)

SECTION_PATTERN = re.compile(r'^[卷篇章节门][\s　]*[一二三四五六七八九十百千万\d]+', re.MULTILINE)

DISEASE_PATTERN = re.compile(
    r'(?:治|主|疗|攻|逐|下|汗|吐|和|温|清|消|补)\s*'
    r'([\u4e00-\u9fff]{2,6}(?:病|证|症|痛|咳|嗽|喘|满|胀|肿|痹|痿|厥|痉|疸|淋|浊|遗|泄|崩|漏|带|胎|产|疳|积|痫|癫|狂|疮|疡|痈|疽|疹|斑|痘|瘰|疬|瘿|瘤|痰|饮|水|气|血|虚|劳|损|伤|感|冒|温|热|暑|湿|燥|火|风|寒|头|目|耳|鼻|喉|口|齿|心|肺|肝|脾|肾|胃|肠|胆|膀|胱|腰|背|胁|腹|肢|节|皮|毛|筋|骨|脉))'
)

def extract_terms(text, pattern, top_n=30):
    """Extract and count matching terms from text."""
    terms = pattern.findall(text)
    counter = Counter(terms)
    return [{"term": t, "count": c} for t, c in counter.most_common(top_n)]

def extract_sections(text):
    """Extract section/chapter headers."""
    sections = SECTION_PATTERN.findall(text)
    return list(dict.fromkeys(sections))[:50]  # unique, preserve order, limit

def parse_filename(fname):
    """Parse '编号-书名-朝代-作者.txt' format."""
    stem = fname.stem
    parts = stem.split('-', 2)
    dynasty = ""; author = ""
    if len(parts) >= 2:
        # Try to extract dynasty from parts
        for p in parts[1:]:
            for d in ['汉','晋','隋','唐','宋','金','元','明','清','南北朝','五代','战国','春秋',
                      '梁','陈','魏','南齐','北齐','辽','西夏','大理','民国','日','韩']:
                if d in p:
                    dynasty = d
                    # Author is after dynasty
                    idx = p.find(d)
                    author = p[idx+len(d):].lstrip('- ')
                    break
            if dynasty: break
        if not dynasty and len(parts) >= 3:
            dynasty = parts[1]
            author = parts[2]
    return {"dynasty": dynasty, "author": author}

# -- main index builder --

def build_index(txt_dir=None, output_path=None):
    if txt_dir is None: txt_dir = TXT_DIR
    if output_path is None: output_path = INDEX_PATH
    
    if not txt_dir.exists():
        print(f"ERROR: Directory not found: {txt_dir}", file=sys.stderr)
        return None
    
    txt_files = sorted(txt_dir.glob("*.txt"))
    if not txt_files:
        print(f"ERROR: No .txt files in {txt_dir}", file=sys.stderr)
        return None
    
    print(f"Building index for {len(txt_files)} files...")
    
    # Category rules (mirrors search_texts.py)
    CAT_RULES = {
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
    
    def categorize(fname):
        for cat, kws in CAT_RULES.items():
            for kw in kws:
                if kw in fname: return cat
        return "其他"
    
    index = {
        "build_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": 0,
        "total_size_mb": 0,
        "categories": {},
        "files": []
    }
    
    for i, fp in enumerate(txt_files):
        try:
            content = read_file(fp)
        except Exception as e:
            print(f"  SKIP [{fp.name}]: {e}")
            continue
        
        cat = categorize(fp.name)
        meta = parse_filename(fp)
        file_size = fp.stat().st_size / (1024 * 1024)
        word_count = len(content)
        
        # Extract key structural info
        sections = extract_sections(content)
        
        # Extract TCM-specific terms
        formulas = extract_terms(content, FORMULA_PATTERN, 25)
        # For herbs and diseases, only do lightweight extraction
        herbs_sample = extract_terms(content, HERB_PATTERN, 15)
        
        entry = {
            "id": i,
            "filename": fp.name,
            "stem": fp.stem,
            "category": cat,
            "dynasty": meta["dynasty"],
            "author": meta["author"],
            "size_mb": round(file_size, 2),
            "word_count": word_count,
            "encoding": detect_encoding(fp),
            "sections": sections[:20],
            "top_formulas": formulas[:10],
            "top_herbs": herbs_sample[:10],
        }
        
        index["files"].append(entry)
        index["total_files"] += 1
        index["total_size_mb"] += file_size
        
        # Category counts
        index["categories"][cat] = index["categories"].get(cat, 0) + 1
        
        if (i+1) % 100 == 0:
            print(f"  Processed {i+1}/{len(txt_files)}...")
    
    index["total_size_mb"] = round(index["total_size_mb"], 2)
    
    # Write index
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\nIndex built: {output_path}")
    print(f"  Files: {index['total_files']}")
    print(f"  Size: {index['total_size_mb']} MB")
    print(f"  Categories: {len(index['categories'])}")
    
    return index

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Build TCM text index")
    p.add_argument("--output","-o", help="Output path", default=str(INDEX_PATH))
    p.add_argument("--txt-dir","-t", help="TXT directory", default=str(TXT_DIR))
    args = p.parse_args()
    
    idx = build_index(Path(args.txt_dir), Path(args.output))
    if idx:
        # Quick stats
        for cat, n in sorted(idx["categories"].items(), key=lambda x:-x[1]):
            print(f"    {cat}: {n}卷")
