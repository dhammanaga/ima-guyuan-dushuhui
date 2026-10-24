#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_md_docx.py —— Word 与 md 的**严格一致性验证**

逐结构单元比对（顺序、类型、层级、编号、文本），不通过即视为交付失败：
  标题层级 / 引用块（含块内列表与编号）/ 表格（行列与单元格）/ 列表（序号数字必须与 md 相同）
  代码块（知识地图层级）/ 时间戳 / 普通段落；另抽查加粗是否落在对应段落

用法：
  python3 verify_md_docx.py <md> <docx>
  python3 verify_md_docx.py --pair <资料包目录>        # 比对 目录/*.md 与 目录/Word版/*.docx
  python3 verify_md_docx.py <md> <docx> --verbose
"""
import os, re, sys, glob, argparse
from docx import Document
from docx.oxml.ns import qn

SEP_RE = re.compile(r"^\|[\s:|\-]+\|$")
OL_RE = re.compile(r"^(\d+)\.\s+(.*)$")
UL_RE = re.compile(r"^[-*]\s+(.*)$")


def norm(t):
    t = re.sub(r"<br\s*/?>", " ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("**", "").replace("`", "")
    t = t.replace("\u2002", " ").replace("\u00a0", " ").replace("\u3000", " ")
    t = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def dequote(line):
    s = line.rstrip("\r\n")
    while s.lstrip().startswith(">"):
        s = s.lstrip()[1:]
    return s.strip()


# ---------- 加粗预处理（与 _mk_word_latest.py 必须逐字同逻辑） ----------
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
    pos = [m.start() for m in re.finditer(r"\*\*", text)]
    if len(pos) % 2 == 0:
        return text
    cut = pos[-1]
    return text[:cut] + text[cut + 2:]


def prep_bold(lines):
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


def parse_md(path):
    lines = prep_bold(open(path, encoding="utf-8").read().split("\n"))
    n = len(lines)
    units = []
    i, seen = 0, False
    seen_heading = False
    while i < n:
        raw = lines[i].rstrip()
        s = raw.strip()
        dq = dequote(raw)

        if s.startswith("```"):
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                r = lines[i].rstrip()
                pre = 0
                for ch in r:
                    if ch in "│├└─┄┈┠┣┗┏ ":
                        pre += 1
                    else:
                        break
                body = r[pre:].strip().lstrip("·•").strip()
                if body:
                    units.append(dict(kind="code", level=min(pre // 4, 8), text=norm(body)))
                    seen = True
                i += 1
            i += 1
            continue

        nxt = dequote(lines[i + 1]) if i + 1 < n else ""
        if dq.startswith("|") and SEP_RE.match(nxt):
            rows, j = [], i
            while j < n:
                row = dequote(lines[j])
                if not row.startswith("|"):
                    break
                rows.append([norm(c) for c in row.strip("|").split("|")])
                j += 1
            if len(rows) >= 2:
                rows = [rows[0]] + rows[2:]
            units.append(dict(kind="table", rows=rows))
            seen = True
            i = j
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            kind = "h0" if not seen_heading else ("h1" if lvl == 1 else ("h2" if lvl == 2 else "h3"))
            seen_heading = True
            _t = norm(m.group(2))
            if kind == "h0":
                _t = _t.replace("（主持人版）", "").replace("（学员版）", "").strip()
            units.append(dict(kind=kind, text=_t,
                              bold=bool(re.search(r"\*\*.+?\*\*", m.group(2)))))
            seen = True
            i += 1
            continue

        if s.startswith(">"):
            while i < n and (lines[i].lstrip().startswith(">") or lines[i].strip() == ">"):
                cc = dequote(lines[i])
                nn = dequote(lines[i + 1]) if i + 1 < n else ""
                if cc.startswith("|") and SEP_RE.match(nn):
                    break
                b = lines[i].lstrip()[1:].strip()
                i += 1
                if not b or b.startswith("<!--"):
                    continue
                mu, mo = UL_RE.match(b), OL_RE.match(b)
                if mu:
                    units.append(dict(kind="quote_ul", text=norm(mu.group(1))))
                elif mo:
                    units.append(dict(kind="quote_ol", num=int(mo.group(1)), text=norm(mo.group(2))))
                else:
                    units.append(dict(kind="quote", text=norm(b),
                                      bold=bool(re.search(r"\*\*.+?\*\*", b))))
                seen = True
            continue

        if s.startswith("<div"):
            mm = re.search(r">(.*?)</div>", s)
            if mm and mm.group(1).strip():
                units.append(dict(kind="stamp", text=norm(mm.group(1))))
            i += 1
            continue

        if s.startswith("<!--") or s in ("---", "***", "___"):
            i += 1
            continue
        if not s:
            i += 1
            continue

        mu, mo = UL_RE.match(s), OL_RE.match(s)
        if mu:
            units.append(dict(kind="ul", text=norm(mu.group(1))))
        elif mo:
            units.append(dict(kind="ol", num=int(mo.group(1)), text=norm(mo.group(2))))
        else:
            units.append(dict(kind="p", text=norm(s), bold=bool(re.search(r"\*\*.+?\*\*", s))))
        seen = True
        i += 1
    return units


def p_kind(p):
    xml = p._p.xml
    txt = p.text.replace("\u2002", " ").strip()
    runs = [r for r in p.runs if r.text.strip()]
    size = runs[0].font.size.pt if runs and runs[0].font.size else None
    has_left = bool(re.search(r"<w:left [^>]*w:color=", xml))
    ind = p.paragraph_format.left_indent.cm if p.paragraph_format.left_indent else 0.0

    if size == 8 and p.alignment is not None and int(p.alignment) == 2:
        return dict(kind="stamp", text=norm(txt))
    if has_left:
        mo = re.match(r"^(\d+)\.\s*(.*)$", txt)
        if txt.startswith("•"):
            return dict(kind="quote_ul", text=norm(txt.lstrip("•").strip()))
        if mo:
            return dict(kind="quote_ol", num=int(mo.group(1)), text=norm(mo.group(2)))
        return dict(kind="quote", text=norm(txt), bold=any(r.bold for r in runs))
    if size == 20:
        return dict(kind="h0", text=norm(txt), bold=True)
    if size == 16:
        return dict(kind="h1", text=norm(txt), bold=True)
    if size == 13.5:
        return dict(kind="h2", text=norm(txt), bold=True)
    if size == 11.5:
        return dict(kind="h3", text=norm(txt), bold=True)
    if txt.startswith("•"):
        return dict(kind="ul", text=norm(txt.lstrip("•").strip()))
    mo = re.match(r"^(\d+)\.\s*(.*)$", txt)
    if mo and ind > 0.5:
        return dict(kind="ol", num=int(mo.group(1)), text=norm(mo.group(2)))
    if 0.3 <= ind and size in (10, 10.5):
        lvl = int(round((ind - 0.35) / 0.55))
        if 0 <= lvl <= 8 and abs(ind - (0.35 + 0.55 * lvl)) < 0.06:
            return dict(kind="code", level=lvl, text=norm(txt))
    return dict(kind="p", text=norm(txt), bold=any(r.bold for r in runs))


def parse_docx(path):
    doc = Document(path)
    units = []
    pmap = {p._p: p for p in doc.paragraphs}
    tmap = {t._tbl: t for t in doc.tables}
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:tbl"):
            t = tmap[child]
            units.append(dict(kind="table", rows=[[norm(c.text) for c in row.cells] for row in t.rows]))
        elif child.tag == qn("w:p"):
            p = pmap.get(child)
            if p is None:
                continue
            if not p.text.strip() and "w:pBdr" not in p._p.xml:
                continue
            units.append(p_kind(p))
    return units


def compare(md_units, dx_units):
    diffs = []
    for idx in range(max(len(md_units), len(dx_units))):
        a = md_units[idx] if idx < len(md_units) else None
        b = dx_units[idx] if idx < len(dx_units) else None
        if a is None:
            diffs.append((idx, "docx 多出单元", "", str(b.get("text", b.get("kind")))[:40]))
            continue
        if b is None:
            diffs.append((idx, "docx 缺失单元", str(a.get("text", a.get("kind")))[:40], ""))
            continue
        if a["kind"] != b["kind"]:
            diffs.append((idx, "类型不符", f'{a["kind"]}:{a.get("text","")[:28]}', f'{b["kind"]}:{b.get("text","")[:28]}'))
            continue
        if a["kind"] in ("ol", "quote_ol") and a.get("num") != b.get("num"):
            diffs.append((idx, "编号不符", f'{a.get("num")}.{a["text"][:26]}', f'{b.get("num")}.{b["text"][:26]}'))
            continue
        if a["kind"] == "code" and a.get("level") != b.get("level"):
            diffs.append((idx, "层级不符", f'L{a.get("level")}:{a["text"][:26]}', f'L{b.get("level")}:{b["text"][:26]}'))
            continue
        if a["kind"] == "table":
            if len(a["rows"]) != len(b["rows"]) or any(len(x) != len(y) for x, y in zip(a["rows"], b["rows"])):
                diffs.append((idx, "表格规模不符",
                              f'{len(a["rows"])}行',
                              f'{len(b["rows"])}行'))
                continue
            for ri, (ra, rb) in enumerate(zip(a["rows"], b["rows"])):
                for ci, (ca, cb) in enumerate(zip(ra, rb)):
                    if ca != cb:
                        diffs.append((idx, f"单元格不符 r{ri}c{ci}", ca[:28], cb[:28]))
            continue
        if a["text"] != b["text"]:
            diffs.append((idx, "文本不符", a["text"][:55], b["text"][:55]))
        elif a.get("bold") and not b.get("bold"):
            diffs.append((idx, "加粗丢失", a["text"][:40], "docx 未加粗"))
    return diffs


def doc_extra_checks(path):
    """结构级硬检查：禁止 Word 自动编号（防跨列表续编）、字体白名单"""
    doc = Document(path)
    xml = doc.element.xml
    numpr = len(re.findall(r"<w:numPr>", xml))
    import zipfile, collections
    z = zipfile.ZipFile(path)
    fonts = collections.Counter()
    for n in z.namelist():
        if n.endswith(".xml"):
            x = z.read(n).decode("utf-8", "ignore")
            for m in re.findall(r'w:(?:ascii|hAnsi|eastAsia|cs)="([^"]+)"', x):
                fonts[m] += 1
    bad_fonts = {k: v for k, v in fonts.items() if k in
                 ("Courier", "Courier New", "Symbol", "Wingdings", "等线", "DengXian", "Calibri", "Cambria", "Arial")}
    return dict(numpr=numpr, fonts=dict(fonts), bad_fonts=bad_fonts)


def run_one(md, docx, verbose=False):
    mdu, dxu = parse_md(md), parse_docx(docx)
    diffs = compare(mdu, dxu)
    ex = doc_extra_checks(docx)
    print("=" * 74)
    print(f"{os.path.basename(docx)}\n  md 结构单元 {len(mdu)} ／ docx 结构单元 {len(dxu)}")
    print(f"  自动编号 numPr={ex['numpr']}（须为 0）  ｜ 字体={ex['fonts']}")
    if ex["numpr"]:
        diffs.append((-1, "存在 Word 自动编号（会跨列表续编）", f"numPr={ex['numpr']}", ""))
    if ex["bad_fonts"]:
        diffs.append((-1, "含非白名单字体", str(ex["bad_fonts"]), ""))
    if not diffs:
        print("  ✅ 完全一致（顺序／类型／层级／编号／文本／加粗）")
        return 0
    print(f"  ❌ 差异 {len(diffs)} 处：")
    for d in diffs[: (300 if verbose else 25)]:
        print(f"    #{d[0]:4d} [{d[1]}] md={d[2]!r} | docx={d[3]!r}")
    return len(diffs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md", nargs="?")
    ap.add_argument("docx", nargs="?")
    ap.add_argument("--pair")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    total = 0
    if a.pair:
        pairs = []
        for md in sorted(glob.glob(os.path.join(a.pair, "*.md"))):
            base = os.path.splitext(os.path.basename(md))[0]
            if base.startswith("README") or "CHANGELOG" in base:
                continue
            for c in (os.path.join(a.pair, "Word版", base + ".docx"), os.path.join(a.pair, base + ".docx")):
                if os.path.exists(c):
                    pairs.append((md, c))
                    break
        if not pairs:
            raise SystemExit("未找到可比的 md/docx 对")
        for md, dx in pairs:
            total += run_one(md, dx, a.verbose)
    else:
        total = run_one(a.md, a.docx, a.verbose)
    print(f"\n总计差异：{total} 处 —— " + ("PASS ✅" if total == 0 else "FAIL ❌"))
    sys.exit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
