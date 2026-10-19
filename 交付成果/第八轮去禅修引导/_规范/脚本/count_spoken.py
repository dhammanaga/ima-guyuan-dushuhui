# -*- coding: utf-8 -*-
"""第5版主持人版「朗读字数」核验工具

口径依据（2026-10-17 尊者令，最新；取代 2026-10-13 的「8周版 ≤4500」）：
  ★8 周版：每周「原文阅读／共读原文」＝ **3600–5400 纯汉字**（下限 3600／上限 5400，
     单段判定）；不满 3600 判「偏少」，超 5400 判「超标」。
  · 4 周版：共读原文1 = 20 分钟 → ≤3600 字；共读原文2 = 20 分钟 → ≤3600 字
            （两段各自独立判定，不是相加再比）
  · ◈ 扩展段＝时间富余才加读，**字数不受限制**（2026-10-13 尊者令）。
  · 字数一律按**纯汉字**计（re.findall(r'[\\u4e00-\\u9fff]')），不含标点／数字／字母，
    与 RULES5 二·8「唯一裁决口径＝纯汉字」一致。

「朗读正文」范围 = 仅 `## 📖 共读原文N`（或 8 周版裸 `## 📖 共读（25 min）`）整节内的可朗读文字；
不含材料标题行、`- **文件**：`、`> ⚠️ 主持人操作：`、`> 主持人：`、
`**主持人课前准备**` 及其下编号清单、`---`，也不含速览表/信息卡/讨论题/
特别提醒/延伸阅读等节外文字。

用法：
    python3 count_spoken.py <文件.md> [<文件.md>…]   # 逐文件逐段报字数并判合规
    python3 count_spoken.py -v <文件.md>              # 另附逐段明细
    python3 count_spoken.py <目录>/                   # 批量扫，末尾汇总超标段
"""
import re
import sys
import glob
import os

# 中等偏慢朗读速度（字/分钟）
CPS = 180

HZ = re.compile(r"[\u4e00-\u9fff]")


def hz(s):
    """纯汉字数（唯一裁决口径）。"""
    return len(HZ.findall(s))


# 节名 → (下限, 上限)。下限 None 表示只判上限。
# 8 周版：2026-10-17 尊者令「原文阅读汉字 3600–5400」（原 ≤4500 作废）
LIM = {
    "共读原文1": (None, 20 * CPS),      # ≤3600（4 周版第一段）
    "共读原文2": (None, 20 * CPS),      # ≤3600（4 周版第二段）
    "共读": (3600, 5400),               # 3600–5400（8 周版单段）
}

# ◈ 扩展段：2026-10-13 尊者令「放宽字数限制，拓展内容字数不受限制」
EXT_LIM = None

SKIP_PREFIX = (
    "### 原文材料", "- **文件**", "> ⚠️", "> 主持人", "## ",
)


def sections(t):
    """返回 [(节名, 节正文)]，只取共读原文节。
    兼容 4 周版 `## 📖 共读原文1/2` 与 8 周版 `## 📖 共读（25 min）`。"""
    out = []
    for m in re.finditer(r"(?m)^## \U0001F4D6 (共读原文\d|共读)", t):
        st = m.start()
        nx = re.search(r"(?m)^## ", t[st + 5:])
        en = st + 5 + nx.start() if nx else len(t)
        out.append((m.group(1), t[st:en]))
    return out


def limit_of(name):
    """按节名取 (下限, 上限)。「共读原文1/2」查 20 分钟档；裸「共读」查 8 周版档。"""
    for k in ("共读原文1", "共读原文2"):
        if name.startswith(k):
            return LIM[k]
    return LIM["共读"]


def spoken(text):
    """单个共读节的纯汉字朗读字数 + 逐段明细（段标题行本身不计字数）。
    返回 (节朗读纯汉字数, [(段标题, 纯汉字数, 是否◈扩展)], ◈扩展合计纯汉字数)"""
    detail, cur, curname, cur_ext = [], [], "(前言)", False
    keep, ext = [], []
    in_prep = False
    for ln in text.split("\n"):
        x = ln.strip()
        if not x or x == "---":
            continue
        if x.startswith("**主持人课前准备"):
            in_prep = True
            continue
        if in_prep:
            # 课前准备下的编号清单，直到第一个材料块为止
            if x.startswith("### 原文材料"):
                in_prep = False
            else:
                continue
        if x.startswith(SKIP_PREFIX):
            continue
        # 段标题行只作分段，不计字数。两种写法：
        #   **一、xxx**（★核心） / **【◈扩展段落…】** / **xxx**（★核心）
        m = re.match(r"^\*\*[一二三四五六七八九十]、", x) or \
            re.match(r"^\*\*【", x) or \
            re.match(r"^\*\*[^*]+\*\*（[★◈]", x)
        if m:
            if cur:
                detail.append((curname, hz("".join(cur)), cur_ext))
            cur_ext = ("◈" in x) or ("扩展" in x)
            cur, curname = [], x[:44]
            continue
        cur.append(x)
        keep.append(x)
        if cur_ext:
            ext.append(x)
    if cur:
        detail.append((curname, hz("".join(cur)), cur_ext))
    return hz("".join(keep)), detail, hz("".join(ext))


def check_html(text):
    """HTML 标签配对自检——第1行 </div> 缺失会让 GitHub 整篇右对齐（2026-10-12 踩坑）。"""
    o = text.count('<div align="right">')
    c = text.count("</div>")
    if o == c:
        return True, ""
    if o > c:
        return False, "\u2717 </div> 缺失 %d 个 → GitHub 会整篇右对齐" % (o - c)
    return False, "\u2717 <div align=\"right\"> 多 %d 个（无害，但建议清理）" % (c - o)


XIFANG = ["愿我此功德，导向诸漏尽！",
          "愿我此功德，为证涅槃缘！",
          "我此功德分，回向诸有情！",
          "愿彼等一切，同得功德分！"]
XIFANG_CUSTOM = "愿以此共修|愿此善缘成熟|愿正见灯灯相续"


def check_xifang(text):
    """回向词与收尾自检（2026-10-12 尊者令：回向词绝对不可改，收尾只设一个）。"""
    msgs = []
    n = sum(text.count(x) for x in XIFANG)
    if n == 0 and "回向" in text:
        msgs.append("✗ 无标准回向词四句")
    elif n > 4:
        msgs.append("✗ 回向词出现%d 次（应全篇仅 4 句）" % n)
    if re.search(XIFANG_CUSTOM, text):
        msgs.append("✗ 含自造回向文，须换回标准四句")
    if re.search(r"(?m)^### 收尾(?:一|二)?", text):
        msgs.append("✗ 收尾被拆成「收尾一/二」，应合并为单一环节")
    return (len(msgs) == 0), " ".join(msgs)


def band_of(lo, hi):
    return ("≤%d" % hi) if lo is None else ("%d–%d" % (lo, hi))


def judge(n, lo, hi):
    """返回 (是否合规, 备注)。8 周版同时判下限/上限。"""
    if n > hi:
        return False, " 超%d" % (n - hi)
    if lo is not None and n < lo:
        return False, " 偏少%d" % (lo - n)
    return True, ""


def check(path, verbose=False):
    t = open(path, encoding="utf-8").read()
    secs = sections(t)
    if not secs:
        print("无共读节  %s" % path)
        return [], False, False
    if verbose:
        print("=" * 78)
        print(os.path.basename(path))
    rows, bad = [], False
    for name, body in secs:
        n, detail, extn = spoken(body)
        lo, hi = limit_of(name)
        ok, flag = judge(n, lo, hi)
        bad = bad or not ok
        rows.append((name, n, lo, hi, extn, ok, flag))
        if verbose:
            print("  %-11s 纯汉字 %5d/%s  扩展 %4d(不限)  %s"
                  % (name, n, band_of(lo, hi), extn, "OK" if ok else flag.strip()))
            for dname, c, is_ext in detail:
                print("        %5d  %s%s" % (c, "[扩展] " if is_ext else "", dname))

    # 自检：开头必须有「本周知识地图」节（树形框架 + 要点）
    has_map = bool(re.search(r"(?m)^##\s*\U0001F5FA\s*本周知识地图", t)) or \
        bool(re.search(r"(?m)^##\s*[^\n]*本周知识地图", t))
    if not has_map:
        bad = True
    # 自检：HTML 标签配对（缺 </div> → GitHub 整篇右对齐）
    html_ok, html_msg = check_html(t)
    if not html_ok:
        bad = True
    # 自检：回向词与收尾结构（尊者令：回向词绝对不可改，收尾只设一个）
    xf_ok, xf_msg = check_xifang(t)
    if not xf_ok:
        bad = True
    print("%s  %s%s%s%s" % (
        "   ".join("%s=%d/%s(扩%d)%s" % (r[0], r[1], band_of(r[2], r[3]), r[4],
                                         "" if r[5] else " X")
                   for r in rows),
        "合规" if not bad else "有段不合规",
        "" if has_map else "  \u2717缺「本周知识地图」节",
        "" if html_ok else "  " + html_msg,
        "" if xf_ok else "  " + xf_msg))
    print("      %s" % path)
    return rows, bad, has_map


if __name__ == "__main__":
    args = sys.argv[1:]
    verbose = "-v" in args
    args = [a for a in args if a != "-v"]
    if args and (os.path.isdir(args[0]) or args[0].endswith(("/", "\\"))):
        files = []
        for d in args:
            files += sorted(glob.glob(os.path.join(d, "*.md")))
    else:
        files = args
    over = []
    for f in files:
        rows, bad, has_map = check(f, verbose)
        for name, n, lo, hi, extn, ok, flag in rows:
            if not ok:
                over.append((lo if (lo is not None and n < lo) else hi, n, lo, hi,
                             extn, name, f, flag))
    if not files:
        print("未找到 .md 文件")
    print()
    print("共 %d 个文件，字数不合规 %d 段" % (len(files), len(over)))
    for d, n, lo, hi, extn, name, f, flag in sorted(over, reverse=True):
        print("  %-11s 纯汉字%6d/%s 扩展%5d(不限)%s  %s"
              % (name, n, band_of(lo, hi), extn, flag, os.path.basename(f)[:40]))
