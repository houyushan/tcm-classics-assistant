# 中医古籍助手 (TCM Classics Assistant)

基于 700+ 卷中医古籍经典文献的 Codex 技能助手，支持全文搜索、分类浏览、多关键词检索。

## 快速开始

### 1. 准备古籍文本

将 700 本中医古籍 TXT 文件放到 skill 同级的 `中医古籍700本TXT/` 目录：

```
skills/
├── tcm-classics-assistant/   ← git clone 这个仓库
└── 中医古籍700本TXT/          ← 手动放置古籍文件
    ├── 000-神农本草经-清-孙星衍.txt
    ├── 001-吴普本草-晋-吴普.txt
    ├── 013-本草纲目-明-李时珍.txt
    └── ...（共 700+ 个文件）
```

如果你的古籍在其他位置，设置环境变量：

```powershell
# PowerShell
$env:TCM_TXT_DIR = "D:\你的古籍目录"

# CMD
set TCM_TXT_DIR=D:\你的古籍目录
```

### 2. 安装技能

```powershell
Copy-Item tcm-classics-assistant -Destination "$env:USERPROFILE\.codex\skills\tcm-classics-assistant" -Recurse
```

### 3. 重启 Codex

重启后在对话中用中文提问中医相关问题即可自动触发。

## 功能演示

在 Codex 中直接问：

- "桂枝汤的组成和功效？"
- "阴虚潮热盗汗怎么辨证？"
- "伤寒论中麻黄汤的适应证？"
- "李时珍本草纲目对人参的论述"

## 搜索工具

```bash
# 单关键词搜索
python scripts/search_texts.py "小柴胡汤" --max-results 10

# 多关键词搜索
python scripts/search_texts.py --keywords "阴虚" "潮热" "盗汗" --mode all

# 按分类搜索
python scripts/search_texts.py "头痛" --category 伤寒

# 查看所有分类
python scripts/search_texts.py --list-categories

# 列出某分类下所有古籍
python scripts/search_texts.py --list-texts 本草
```

## 覆盖范围

| 分类 | 数量 | 代表著作 |
|---|---|---|
| 本草 | 55卷 | 神农本草经、本草纲目、本草经集注 |
| 方剂 | 111卷 | 伤寒杂病论、千金方、外台秘要、太平惠民和剂局方 |
| 伤寒 | 44卷 | 注解伤寒论、伤寒来苏集、伤寒贯珠集 |
| 内经 | 30卷 | 黄帝内经素问、灵枢、难经、类经 |
| 温病 | 17卷 | 温病条辨、温热论、温疫论 |
| 诊法 | 34卷 | 脉经、濒湖脉学、四诊抉微 |
| 针灸 | 26卷 | 针灸甲乙经、针灸大成、十四经发挥 |
| 医案 | 48卷 | 临证指南医案、名医类案 |
| 综合 | 60卷 | 景岳全书、医宗金鉴、证治准绳 |
| 其他 | 117卷 | 女科、儿科、外科、眼科、喉科、养生等 |

## 注意事项

- 古籍文本为 GBK/UTF-16LE 编码，脚本自动检测
- 本仓库不包含古籍原文，需自行准备（`.gitignore` 已排除）
- 搜索结果会注明出处（书名、朝代、作者）
