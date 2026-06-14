#!/usr/bin/env python3
"""Search TCM classical texts for relevant passages.

Supports GBK, UTF-8, UTF-16LE encoded Chinese text files.

古籍目录默认: 此脚本所在目录的上级目录下的 "中医古籍700本TXT/"
也可通过 TCM_TXT_DIR 环境变量指定路径。

Usage:
    python search_texts.py "<query>" [--max-results N] [--context-lines N] [--category CAT]
    python search_texts.py --list-categories
    python search_texts.py --list-texts [CATEGORY]
"""
import os
import re
import sys
import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

# 环境变量优先，否则用默认相对路径
DEFAULT_TXT_DIR = SKILL_DIR.parent / "中医古籍700本TXT"
TXT_DIR = Path(os.environ.get("TCM_TXT_DIR", str(DEFAULT_TXT_DIR)))

CATEGORIES = {
    "本草": ["本草", "药性", "药鉴", "药征", "药症", "炮炙", "炮制", "食疗", "食鉴", "饮膳", "滇南", "海药", "本经"],
    "方剂": ["方", "汤头", "剂录", "良方", "验方", "秘方", "集验", "本事方", "济生方", "百一选", "回生集"],
    "伤寒": ["伤寒", "仲景"],
    "金匮": ["金匮"],
    "内经": ["内经", "素问", "灵枢", "难经", "黄帝", "灵素", "太素"],
    "温病": ["温病", "温疫", "温热", "温症", "时病", "伏气", "湿温", "暑", "霍乱", "痧", "疟"],
    "诊法": ["脉", "诊", "望", "闻", "问", "舌", "四诊"],
    "女科": ["女科", "妇人", "产科", "产宝", "济生集", "傅青主"],
    "儿科": ["儿科", "幼科", "婴童", "小儿", "痘", "种痘", "麻科", "片玉"],
    "外科": ["外科", "疡医", "疮疡", "痈", "正骨", "伤科", "跌打", "金疮", "仙授"],
    "针灸": ["针灸", "经穴", "经脉", "经络", "刺血", "十四经", "针经", "灸法"],
    "医案": ["医案", "医话", "医验", "经验集", "临证经验", "临证验案", "经方实验"],
    "综合医论": ["医论", "医说", "医贯", "医通", "医宗", "医旨", "医法", "医镜", 
                 "医述", "医门", "医学", "医林", "辨证", "证治", "石室秘录", 
                 "医碥", "儒门事亲", "兰室秘藏", "脾胃论", "格致", "丹溪", 
                 "万病回春", "古今医", "医经", "此事难知", "玉机微义", "明医"],
    "眼科": ["眼科", "目经"],
    "喉科": ["喉"],
    "养生": ["养生", "摄生", "延年", "导引", "气功", "丹", "仙", "道藏"],
    "医史": ["医籍考", "名老中医"],
    "现代": ["思考中医", "中医之钥", "民间", "澄空"],
}

TXT_HELP = """
========================================
  未找到中医古籍文本文件！
========================================

请将 700 本中医古籍 TXT 文件放到以下目录：

    {txt_dir}

或设置环境变量 TCM_TXT_DIR 指向你的古籍目录：

    PowerShell:
      $env:TCM_TXT_DIR = "你的古籍目录路径"

    CMD:
      set TCM_TXT_DIR=你的古籍目录路径

    Linux/Mac:
      export TCM_TXT_DIR="你的古籍目录路径"

文件命名格式: 编号-书名-朝代-作者.txt
例如: 013-本草纲目-明-李时珍.txt
========================================
"""

def check_txt_dir():
    """Check if TXT directory exists and has files."""
    if not TXT_DIR.exists():
        print(TXT_HELP.format(txt_dir=TXT_DIR), file=sys.stderr)
        sys.exit(1)
    txts = list(TXT_DIR.glob("*.txt"))
    if not txts:
        print(TXT_HELP.format(txt_dir=TXT_DIR), file=sys.stderr)
        sys.exit(1)
    return True

def detect_encoding(filepath):
    """Detect file encoding via BOM."""
    with open(filepath, 'rb') as f:
        head = f.read(4)
    if head[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    if head[:2] == b'\xff\xfe':
        return 'utf-16-le'
    if head[:2] == b'\xfe\xff':
        return 'utf-16-be'
    return 'gbk'

def read_file(filepath):
    """Read a text file with auto-detected encoding."""
    enc = detect_encoding(filepath)
    with open(filepath, 'r', encoding=enc, errors='replace') as f:
        return f.read()

def get_category(filename):
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in filename:
                return cat
    return "其他"

def build_file_list(category=None):
    files = []
    for f in TXT_DIR.glob("*.txt"):
        cat = get_category(f.name)
        if category and cat != category:
            continue
        files.append((f, f.stem, cat))
    return sorted(files, key=lambda x: x[1])

def search_texts(query, max_results=15, context_lines=3, category=None):
    files = build_file_list(category)
    results = []

    for filepath, name, cat in files:
        try:
            content = read_file(filepath)
        except Exception:
            continue
        
        if query not in content:
            continue
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if query in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                ctx = '\n'.join(lines[start:end]).strip()
                if ctx:
                    results.append({
                        'file': name, 'category': cat,
                        'line_num': i + 1, 'matched_line': line.strip(),
                        'context': ctx, 'filepath': str(filepath)
                    })
                if len(results) >= max_results * 3:
                    break
        if len(results) >= max_results * 3:
            break
    
    seen = set()
    unique = []
    for r in results:
        key = (r['file'], r['matched_line'][:80])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:max_results]

def search_multi_keywords(keywords, max_results=20, context_lines=3, category=None, mode="any"):
    files = build_file_list(category)
    results = []

    for filepath, name, cat in files:
        try:
            content = read_file(filepath)
        except Exception:
            continue

        if mode == "all":
            if not all(kw in content for kw in keywords):
                continue
        else:
            if not any(kw in content for kw in keywords):
                continue

        best_positions = []
        for kw in keywords:
            if kw not in content:
                continue
            for m in re.finditer(re.escape(kw), content):
                best_positions.append(m.start())
        best_positions.sort()

        ctx_parts = []
        for pos in best_positions[:5]:
            start = max(0, pos - 250)
            end = min(len(content), pos + 250)
            snippet = content[start:end].strip()
            if snippet and snippet not in ctx_parts:
                ctx_parts.append(snippet)

        for ctx in ctx_parts[:3]:
            results.append({'file': name, 'category': cat, 'context': ctx})
            if len(results) >= max_results * 2:
                break
        if len(results) >= max_results * 2:
            break

    seen = set()
    unique = []
    for r in results:
        key = r['context'][:120]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:max_results]

def list_categories():
    files = build_file_list()
    cats = {}
    for _, _, cat in files:
        cats[cat] = cats.get(cat, 0) + 1
    return cats

def list_texts(category=None):
    return [(name, cat) for _, name, cat in build_file_list(category)]

def main():
    # Allow --list-* to work even without TXT files (they read from metadata)
    parser = argparse.ArgumentParser(description="Search TCM classical texts")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--max-results", "-n", type=int, default=15)
    parser.add_argument("--context-lines", "-c", type=int, default=3)
    parser.add_argument("--category", "-C")
    parser.add_argument("--keywords", "-k", nargs="+")
    parser.add_argument("--mode", "-m", choices=["any", "all"], default="any")
    parser.add_argument("--list-categories", action="store_true")
    parser.add_argument("--list-texts", nargs="?", const="__ALL__")
    parser.add_argument("--json", action="store_true")
    
    args = parser.parse_args()
    
    # Always check TXT dir first, except for help-like flags
    check_txt_dir()
    
    if args.list_categories:
        cats = list_categories()
        if args.json:
            print(json.dumps(cats, ensure_ascii=False, indent=2))
        else:
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                print(f"  {cat}: {count}卷")
        return
    
    if args.list_texts is not None:
        cat = None if args.list_texts == "__ALL__" else args.list_texts
        texts = list_texts(cat)
        for name, cat_name in texts:
            print(f"  [{cat_name}] {name}")
        return
    
    if not args.query and not args.keywords:
        parser.print_help()
        return
    
    if args.keywords:
        results = search_multi_keywords(args.keywords, args.max_results, args.context_lines, args.category, args.mode)
    else:
        results = search_texts(args.query, args.max_results, args.context_lines, args.category)
    
    if args.json:
        safe = []
        for r in results:
            safe.append({k: v for k, v in r.items() if k != 'filepath'})
        print(json.dumps(safe, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"  [{i}] [{r['category']}] {r['file']}")
            print(f"{'='*60}")
            ctx = r['context'][:1000]
            print(ctx)
            if len(r['context']) > 1000:
                print("  ... (截断)")
    
    if not results:
        q = args.query or ' '.join(args.keywords or [])
        print(f"\n未找到与 '{q}' 相关的结果。")

if __name__ == "__main__":
    main()
