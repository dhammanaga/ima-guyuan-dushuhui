#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_mk_word_latest.py —— 读书会资料包 md → docx 生成器（Word 规则 v1.1 · 2026-10-24）

v1.1 变更（相对 v1.0）：
  ① 字体改为全平台标配，杜绝 WPS「字体缺失」提示：
     正文＝中文 宋体 + 西文 Times New Roman；标题＝微软雅黑（西文亦用雅黑）
  ② 版式增强，层次更清楚：
     首行标题 20pt 居中 + 标题下横线；# 16pt 带下细线；## 13.5pt；### 11.5pt
     正文行距 1.5、段后 4pt、两端对齐；引用块 10pt/行距1.4/左竖线 3pt/右缩进0.2cm
     表格 9.5pt、表头行跨页重复（tblHeader）、单元格留白、首列加粗
     列表左缩进 0.75cm；页眉 8.5pt + 底部细线；页脚「— 页码 —」

用法：
  python3 _mk_word_latest.py <资料包目录|单个md> [--series 05] [--edition "第八轮（第8版）"]
                            [--weeks 4|8] [--out 输出目录] [--zip]
"""
import os, re, sys, glob, zipfile, argparse, datetime, collections

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HOST_C = RGBColor(0x1F, 0x38, 0x64)   # 主持人版 藏青
STU_C = RGBColor(0x1E, 0x46, 0x20)    # 学员版 墨绿
QUOTE_BG = "EEF3F9"
STAMP_GREY = RGBColor(0x88, 0x88, 0x88)
BODY_GREY = RGBColor(0x22, 0x22, 0x22)
LINE_GREY = "D0D7E2"

F_BODY_CN = "宋体"
F_BODY_EN = "Times New Roman"
F_HEAD_CN = "微软雅黑"
F_HEAD_EN = "微软雅黑"

SKIP_NAMES = ("README", "更新日志_CHANGELOG", "CHANGELOG")
WEEK_RE = re.compile(r"^第(\d+)周_(.+)_(主持人版|学员版)\.md$")


# ---------- 底层工具 ----------
_PBDR_SUCC = ('w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap',
              'w:overflowPunct', 'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN',
              'w:bidi', 'w:adjustRightInd', 'w:snapToGrid', 'w:spacing', 'w:ind',
              'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc',
              'w:textDirection', 'w:textAlignment', 'w:textboxTightWrap', 'w:outlineLvl',
              'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr', 'w:pPrChange')
_SHD_SUCC = _PBDR_SUCC[1:]


def _shade(el, fill):
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), fill)
    try:
        el.insert_element_before(sh, *_SHD_SUCC)   # 保证 w:pPr 子元素顺序合规
    except Exception:
        el.append(sh)


def _border(p, edge="left", color="1F3864", sz=24, space=6):
    pPr = p._p.get_or_add_pPr()
    pbdr = pPr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        try:
            pPr.insert_element_before(pbdr, *_PBDR_SUCC)
        except Exception:
            pPr.append(pbdr)
    e = OxmlElement(f"w:{edge}")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(sz))
    e.set(qn("w:space"), str(space))
    e.set(qn("w:color"), color)
    pbdr.append(e)


def _font(run, cn=F_BODY_CN, en=F_BODY_EN, size=None, color=None, bold=None):
    run.font.name = en                       # 正确写入 w:ascii / w:hAnsi
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:eastAsia"), cn)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    if bold is not None:
        run.bold = bold


def _field(p, code, prefix="", suffix=""):
    if prefix:
        _font(p.add_run(prefix), size=9, color=RGBColor(0x80, 0x80, 0x80))
    r = p.add_run()
    _font(r, size=9, color=RGBColor(0x80, 0x80, 0x80))
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = code
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(it); r._r.append(f2)
    if suffix:
        _font(p.add_run(suffix), size=9, color=RGBColor(0x80, 0x80, 0x80))


PALI_RE = re.compile("[\u0100-\u024F\u1E00-\u1EFF]")


def _set_latin(run, latin):
    """只改拉丁/复杂文种字体，不动 eastAsia（中文照旧）"""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), latin)
    rFonts.set(qn("w:hAnsi"), latin)
    rFonts.set(qn("w:cs"), latin)


def add_runs(p, text, size=10.5, color=None, base_bold=False, latin=None, cn=None, en=None):
    """段内 **加粗** / `代码` 处理；含巴利语变音符号的片段自动改用 Times New Roman，
    保证 ā ī ū ṅ ñ ṭ ḍ ṇ ḷ ṃ ḥ 等在各类环境下都能正常显示。"""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace("<br>", " ").replace("<br/>", " ")
    for seg in re.split(r"(\*\*.+?\*\*)", text):
        if not seg:
            continue
        bold = None
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            seg = seg[2:-2]
            bold = True
        for piece in re.split(r"(\S+)", seg):
            if not piece:
                continue
            r = p.add_run(piece)
            _font(r, cn=(cn or F_BODY_CN), en=(en or F_BODY_EN), size=size, color=color,
                  bold=(bold if bold else base_bold))
            if latin:
                _set_latin(r, latin)
            if PALI_RE.search(piece):
                _set_latin(r, F_BODY_EN)
    return p


def _body_fmt(p, before=0, after=5, line=1.4, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
              left=None, right=None):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if align is not None:
        p.alignment = align
    if left is not None:
        pf.left_indent = Cm(left)
    if right is not None:
        pf.right_indent = Cm(right)



FONT_ALIAS = {
    "Courier": "Times New Roman", "Courier New": "Times New Roman",
    "Symbol": "Times New Roman", "Wingdings": "Times New Roman",
    "Wingdings 2": "Times New Roman", "Wingdings 3": "Times New Roman",
    "DengXian": "\u5b8b\u4f53", "\u7b49\u7ebf": "\u5b8b\u4f53", "\u7b49\u7ebf Light": "\u5b8b\u4f53",
    "Calibri": "Times New Roman", "Cambria": "Times New Roman",
}


def clean_theme(docx_path):
    """把主题字体统一为宋体/Times New Roman/微软雅黑，并清掉其他语言脚本字体，
    避免 WPS/Office 打开时提示「字体缺失」。"""
    tmp = docx_path + ".tmp"
    zin = zipfile.ZipFile(docx_path)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/theme/theme1.xml":
            x = data.decode("utf-8")
            x = re.sub(r'(<a:majorFont>\s*)<a:latin typeface="[^"]*"[^>]*/>',
                       r'\1<a:latin typeface="微软雅黑"/>', x)
            x = re.sub(r'(<a:majorFont>\s*<a:latin typeface="[^"]*"/>\s*)<a:ea typeface="[^"]*"[^>]*/>',
                       r'\1<a:ea typeface="微软雅黑"/>', x)
            x = re.sub(r'(<a:minorFont>\s*)<a:latin typeface="[^"]*"[^>]*/>',
                       r'\1<a:latin typeface="Times New Roman"/>', x)
            x = re.sub(r'(<a:minorFont>\s*<a:latin typeface="[^"]*"/>\s*)<a:ea typeface="[^"]*"[^>]*/>',
                       r'\1<a:ea typeface="宋体"/>', x)
            x = re.sub(r'<a:font script="[^"]*" typeface="[^"]*"/>', "", x)
            for bad, good in FONT_ALIAS.items():
                x = x.replace('typeface="%s"' % bad, 'typeface="%s"' % good)
            data = x.encode("utf-8")
        elif item.filename.endswith(".xml"):
            x = data.decode("utf-8", "ignore")
            orig = x
            for bad, good in FONT_ALIAS.items():
                x = re.sub(r'(w:(?:ascii|hAnsi|cs)=")' + re.escape(bad) + r'(")',
                           r'\g<1>' + good + r'\g<2>', x)
            if x != orig:
                data = x.encode("utf-8")
        zout.writestr(item, data)
    zout.close(); zin.close()
    os.replace(tmp, docx_path)


# ---------- 单文件转换 ----------
# ---------- 加粗预处理（与 verify_md_docx.py 必须逐字同逻辑） ----------
CJK_RE = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")


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
    if re.match(r"^\d+\. ", s):
        return False
    return True


def drop_lone_bold(text):
    """删掉行内两两配对后落单的 **（保留文字与已完整成对的加粗）"""
    pos = [m.start() for m in re.finditer(r"\*\*", text)]
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


def convert(md_path, docx_path, header_text, color, color_hex):
    lines = prep_bold(open(md_path, encoding="utf-8").read().split("\n"))
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.header_distance = Cm(1.2)
    sec.footer_distance = Cm(1.2)

    # 页眉：8.5pt 主题色居中 + 底部细线
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.text = ""
    _font(hp.add_run(header_text), cn=F_HEAD_CN, en=F_HEAD_EN, size=8.5, color=color)
    _border(hp, "bottom", LINE_GREY, 6, 4)

    # 页脚：— 页码 —
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.text = ""
    _field(fp, "PAGE", "— ", " —")

    # Normal 样式
    st = doc.styles["Normal"]
    st.font.name = F_BODY_EN
    st.font.size = Pt(10.5)
    rPr = st.element.get_or_add_rPr()
    rPr.get_or_add_rFonts().set(qn("w:eastAsia"), F_BODY_CN)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.line_spacing = 1.4

    def heading(text, lvl, first=False):
        p = doc.add_paragraph()
        if first:
            t = text.replace("（主持人版）", "").replace("（学员版）", "").strip()
            add_runs(p, t, size=20, color=color, base_bold=True, cn=F_HEAD_CN, en=F_HEAD_EN)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.space_before = Pt(2); pf.space_after = Pt(10); pf.line_spacing = 1.3
            _border(p, "bottom", "%02X%02X%02X" % (color[0], color[1], color[2]), 12, 8)
            return
        size = 16 if lvl == 1 else (13.5 if lvl == 2 else 11.5)
        before = 18 if lvl == 1 else (14 if lvl == 2 else 9)
        after = 6 if lvl == 1 else (4 if lvl == 2 else 2)
        add_runs(p, text, size=size, color=color, base_bold=True, cn=F_HEAD_CN, en=F_HEAD_EN)
        pf = p.paragraph_format
        pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = 1.25
        pf.keep_with_next = True
        if lvl == 1:
            _border(p, "bottom", LINE_GREY, 6, 4)

    def make_table(rows):
        cols = max(len(r) for r in rows)
        t = doc.add_table(rows=0, cols=cols)
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        tblPr = t._tbl.tblPr
        # 固定列宽布局
        layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed")
        try:
            tblPr.insert_element_before(layout, "w:tblCellMar", "w:tblLook")
        except Exception:
            tblPr.append(layout)
        # 单元格留白
        mar = OxmlElement("w:tblCellMar")
        for side, w in (("top", 80), ("bottom", 80), ("left", 110), ("right", 110)):
            e = OxmlElement(f"w:{side}")
            e.set(qn("w:w"), str(w)); e.set(qn("w:type"), "dxa")
            mar.append(e)
        try:
            tblPr.insert_element_before(mar, "w:tblLook", "w:tblCaption", "w:tblDescription")
        except Exception:
            tblPr.append(mar)

        # 按内容估算列宽（可用宽度 16.6cm）
        def tw(x):
            return sum(2 if ord(ch) > 127 else 1 for ch in x)
        wsum = []
        for ci in range(cols):
            cand = [tw(r[ci]) for r in rows if ci < len(r)]
            wsum.append(max(max(cand) if cand else 6, 6))
        total_cm = 16.6
        raw = [total_cm * w / sum(wsum) for w in wsum]
        raw = [max(1.7, x) for x in raw]
        k = total_cm / sum(raw)
        widths = [x * k for x in raw]

        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            if ri == 0:   # 表头跨页重复
                trPr = t.rows[0]._tr.get_or_add_trPr()
                th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true")
                trPr.append(th)
                trPr_h = OxmlElement("w:trHeight")
                trPr_h.set(qn("w:val"), str(int(0.70 * 567))); trPr_h.set(qn("w:hRule"), "atLeast")
                trPr.append(trPr_h)
            for ci in range(cols):
                cell = cells[ci]
                cell.width = Cm(widths[ci])
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.2
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ri == 0 else WD_ALIGN_PARAGRAPH.LEFT
                txt = row[ci] if ci < len(row) else ""
                if ri == 0 or ci == 0:
                    add_runs(p, txt, size=10 if ri == 0 else 9.5,
                             color=RGBColor(0xFF, 0xFF, 0xFF) if ri == 0 else None,
                             base_bold=True)
                else:
                    add_runs(p, txt, size=9.5)
                tcPr = cell._tc.get_or_add_tcPr()
                if ri == 0:
                    _shade(tcPr, color_hex)
                elif ri % 2 == 0:
                    _shade(tcPr, "EEF2F8")

    def dequote(line):
        s = line.rstrip()
        while s.lstrip().startswith(">"):
            s = s.lstrip()[1:]
        return s.strip()

    i, n, seen_content = 0, len(lines), False
    seen_heading = False
    while i < n:
        s = lines[i].rstrip()
        stripped = s.strip()

        # 代码块（知识地图的树状结构）→ 转层级缩进文本
        if stripped.startswith("```"):
            i += 1
            block = []
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i].rstrip())
                i += 1
            i += 1  # 跳过结束围栏
            for raw in block:
                # 计算层级：连续「│ ├ └ ─ ┄ ┈ 空格」的字符数 // 4
                pre = 0
                for ch in raw:
                    if ch in "│├└─┄┈┠┣┗┏ ":
                        pre += 1
                    else:
                        break
                body = raw[pre:].strip().lstrip("·•").strip()
                if not body:
                    continue
                lvl = min(pre // 4, 8)
                p = doc.add_paragraph()
                if lvl == 0:
                    add_runs(p, body, size=10.5, color=RGBColor(0x1A, 0x1A, 0x1A), base_bold=True)
                else:
                    add_runs(p, body, size=10, color=RGBColor(0x33, 0x33, 0x33))
                _body_fmt(p, before=0, after=2, line=1.3,
                          align=WD_ALIGN_PARAGRAPH.LEFT, left=0.35 + 0.55 * lvl, right=0.2)
            seen_content = True; continue

        # 表格（含引用块内嵌表格 > | a | b |）
        cur = dequote(lines[i])
        nxt = dequote(lines[i + 1]) if i + 1 < n else ""
        if cur.startswith("|") and re.match(r"^\|[\s:|\-]+\|$", nxt):
            rows, j = [], i
            while j < n:
                row = dequote(lines[j])
                if not row.startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip("|").split("|")])
                j += 1
            if len(rows) >= 2:
                rows = [rows[0]] + rows[2:]
            make_table(rows)
            # 表格后留一点呼吸（半行高空段）
            gap = doc.add_paragraph()
            gap.paragraph_format.space_before = Pt(0)
            gap.paragraph_format.space_after = Pt(0)
            gap.paragraph_format.line_spacing = 0.5
            i = j; seen_content = True; continue

        # 标题
        m = re.match(r"^(#{1,6}) (.*)$", s)
        if m:
            lvl, text = len(m.group(1)), m.group(2).strip()
            heading(text, lvl, first=(not seen_heading))
            seen_heading = True
            i += 1; seen_content = True; continue

        # 引用块
        if stripped.startswith(">"):
            buf = []
            while i < n and (lines[i].lstrip().startswith(">") or lines[i].strip() == ">"):
                cc = dequote(lines[i])
                nn2 = dequote(lines[i + 1]) if i + 1 < n else ""
                if cc.startswith("|") and re.match(r"^\|[\s:|\-]+\|$", nn2):
                    break
                buf.append(lines[i].lstrip()[1:].strip()); i += 1
            if not buf and i < n:
                i += 1
            for b in buf:
                if not b or b.startswith("<!--"):
                    continue
                p = doc.add_paragraph()
                if re.match(r"^[-*] ", b):                    # 引用块内的无序列表
                    add_runs(p, "\u2022\u2002" + b[2:], size=10, color=BODY_GREY)
                    _body_fmt(p, before=0, after=2, line=1.45,
                              align=WD_ALIGN_PARAGRAPH.JUSTIFY, left=0.95, right=0.25)
                    p.paragraph_format.first_line_indent = Cm(-0.45)
                elif re.match(r"^\d+\. ", b):                 # 引用块内的有序列表：保留 md 原编号
                    add_runs(p, b, size=10, color=BODY_GREY)
                    _body_fmt(p, before=0, after=2, line=1.45,
                              align=WD_ALIGN_PARAGRAPH.JUSTIFY, left=0.95, right=0.25)
                    p.paragraph_format.first_line_indent = Cm(-0.5)
                else:
                    add_runs(p, b, size=10, color=BODY_GREY)
                    _body_fmt(p, before=0, after=2, line=1.45,
                              align=WD_ALIGN_PARAGRAPH.JUSTIFY, left=0.45, right=0.25)
                _border(p, "left", color_hex, 30, 8)
                pPr = p._p.get_or_add_pPr()
                _shade(pPr, QUOTE_BG)
            seen_content = True; continue

        # 时间戳
        if stripped.startswith("<div") or stripped.startswith("</div>"):
            mm = re.search(r">(.*?)</div>", s)
            if mm and mm.group(1).strip():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                _font(p.add_run(mm.group(1).strip()), size=8, color=STAMP_GREY)
                p.paragraph_format.space_after = Pt(6)
            i += 1; continue

        if stripped.startswith("<!--") or stripped in ("---", "***", "___"):
            i += 1; continue
        if not stripped:
            i += 1; continue

        # 列表
        if re.match(r"^[-*] ", stripped):
            p = doc.add_paragraph()
            add_runs(p, "\u2022\u2002" + stripped[2:])
            _body_fmt(p, before=0, after=3, line=1.4, left=0.95)
            p.paragraph_format.first_line_indent = Cm(-0.45)
            i += 1; seen_content = True; continue
        mnum = re.match(r"^(\d+)\. (.*)$", stripped)
        if mnum:
            p = doc.add_paragraph()
            add_runs(p, mnum.group(1) + ".\u2002" + mnum.group(2))
            _body_fmt(p, before=0, after=3, line=1.4, left=0.95)
            p.paragraph_format.first_line_indent = Cm(-0.5)
            i += 1; seen_content = True; continue

        # 正文
        p = doc.add_paragraph()
        add_runs(p, stripped)
        _body_fmt(p, before=0, after=5, line=1.4)
        i += 1; seen_content = True

    os.makedirs(os.path.dirname(docx_path) or ".", exist_ok=True)
    doc.save(docx_path)
    clean_theme(docx_path)
    return doc


# ---------- 批量 ----------
def infer_series(path):
    m = re.search(r"读书会(\d{1,2})", path)
    return m.group(1).zfill(2) if m else "00"


def infer_weeks(path):
    return 8 if "8周" in path else 4


def build_header(nn, md_name, edition, weeks):
    tag = f"（{weeks}周版）"
    m = WEEK_RE.match(md_name)
    if m:
        wk, _, role = m.group(1), m.group(2), m.group(3)
        return f"读书会{nn} · 第{wk}周 · {edition}{tag} · {role}"
    stem = os.path.splitext(md_name)[0]
    if stem.startswith("00_"):
        return f"读书会{nn} · 主持人总指南 · {edition}{tag}"
    return f"读书会{nn} · {stem} · {edition}{tag}"


def convert_package(src, out=None, series=None, edition="第八轮（第8版）", weeks=None, do_zip=False):
    src = os.path.abspath(src)
    pkg = src if os.path.isdir(src) else os.path.dirname(src)
    outdir = out or os.path.join(pkg, "Word版")
    os.makedirs(outdir, exist_ok=True)

    mds = ([src] if os.path.isfile(src) else sorted(glob.glob(os.path.join(pkg, "*.md"))))
    targets = [f for f in mds if not os.path.basename(f).startswith(SKIP_NAMES)]

    stats = collections.Counter()
    for md in targets:
        bn = os.path.basename(md)
        m = WEEK_RE.match(bn)
        stu = bool(m and m.group(3) == "学员版")
        color, hexc = (STU_C, "1E4620") if stu else (HOST_C, "1F3864")
        nn = series or infer_series(pkg)
        wks = weeks or infer_weeks(pkg)
        header = build_header(nn, bn, edition, wks)
        docx_path = os.path.join(outdir, bn.replace(".md", ".docx"))
        doc = convert(md, docx_path, header, color, hexc)
        q = sum(1 for p in doc.paragraphs if "w:pBdr" in p._p.xml)
        stats["docx"] += 1; stats["tables"] += len(doc.tables); stats["quotes"] += q
        sizes = collections.Counter(p.runs[0].font.size.pt for p in doc.paragraphs
                                    if p.runs and p.runs[0].font.size)
        print(f"  ✅ {bn[:-3]} → {os.path.basename(docx_path)} | 表 {len(doc.tables)} | "
              f"引用段 {q} | 字号 {dict(sorted(sizes.items()))}")

    if do_zip:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        zpath = os.path.join(pkg, f"{os.path.basename(pkg)}_Word版_{ts}_v1.1.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(glob.glob(os.path.join(outdir, "*.docx"))):
                z.write(f, os.path.join("Word版", os.path.basename(f)))
        print(f"  📦 {os.path.basename(zpath)}（{os.path.getsize(zpath)/1024:.0f} KB）")

    print(f"合计：docx {stats['docx']} 份 | 表格 {stats['tables']} | 引用段 {stats['quotes']} | 输出 {outdir}")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--series")
    ap.add_argument("--edition", default="第八轮（第8版）")
    ap.add_argument("--weeks", type=int, choices=(4, 8))
    ap.add_argument("--out")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    convert_package(a.src, a.out, a.series, a.edition, a.weeks, a.zip)


if __name__ == "__main__":
    main()
