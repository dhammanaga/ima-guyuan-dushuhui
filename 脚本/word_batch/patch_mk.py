#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对 _mk_word_latest.py 做定点修补（P1 层级上限 8 + P2 奇数 ** 预处理）"""
import re

P = "/sandbox/workspace/scripts/_mk_word_latest.py"
s = open(P, encoding="utf-8").read()

BLOCK = '''# ---------- 加粗预处理（与 verify_md_docx.py 必须逐字同逻辑） ----------
CJK_RE = re.compile(r"[\\u3000-\\u303f\\u4e00-\\u9fff\\uff00-\\uffef]")


def _merge_text(a, b):
    a, b = a.rstrip(), b.strip()
    if not a:
        return b
    if not b:
        return a
    if CJK_RE.match(a[-1]) and CJK_RE.match(b[0]):
        return a + b
    return a + " " + b


def _mergeable(t):
    """下一行是否是可与本行合并的普通正文行（结构行不合并，避免破坏引用块/标题/表格）"""
    s = t.strip()
    if not s:
        return False
    if s[0] in "#>|`<":
        return False
    if re.match(r"^[-*+] ", s):
        return False
    if re.match(r"^\\d+\\. ", s):
        return False
    return True


def drop_lone_bold(text):
    """删掉行内两两配对后落单的 **（保留文字与已完整成对的加粗）"""
    pos = [m.start() for m in re.finditer(r"\\*\\*", text)]
    if len(pos) % 2 == 0:
        return text
    cut = pos[-1]
    return text[:cut] + text[cut + 2:]


def prep_bold(lines):
    """奇数 ** 行预处理：本行 ** 为奇数且下一行含 ** → 合并两行为一段；
       否则删掉本行落单的 **。"""
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.count("**") % 2 == 1:
            while (line.count("**") % 2 == 1 and i + 1 < n
                   and "**" in lines[i + 1] and _mergeable(lines[i + 1])):
                line = _merge_text(line, lines[i + 1])
                i += 1
            if line.count("**") % 2 == 1:
                line = drop_lone_bold(line)
            out.append(line)
        else:
            out.append(line)
        i += 1
    return out


def convert(md_path, docx_path, header_text, color, color_hex):'''

anchor = "def convert(md_path, docx_path, header_text, color, color_hex):"
assert s.count(anchor) == 1, s.count(anchor)
s = s.replace(anchor, BLOCK)

old_line = 'lines = open(md_path, encoding="utf-8").read().split("\\n")'
assert s.count(old_line) == 1, s.count(old_line)
s = s.replace(old_line, 'lines = prep_bold(open(md_path, encoding="utf-8").read().split("\\n"))')

assert s.count("lvl = min(pre // 4, 4)") == 1
s = s.replace("lvl = min(pre // 4, 4)", "lvl = min(pre // 4, 8)")

open(P, "w", encoding="utf-8").write(s)
print("patched")
