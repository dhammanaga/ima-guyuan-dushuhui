#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Word 交付前 12 项校验（规则 §11 精简实现）"""
import sys, re, glob, zipfile
from docx import Document
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

OK, FAIL = "PASS", "FAIL"


def hexc(r):
    try:
        return str(r.font.color.rgb) if r.font.color and r.font.color.rgb else None
    except Exception:
        return None


def check(path, series="01", weeks=4, edition="第八轮（第8版）"):
    res = []
    d = Document(path)
    sec = d.sections[0]
    res.append(("1 页面/边距", OK if (round(sec.page_width.cm, 1), round(sec.page_height.cm, 1)) == (21.0, 29.7)
                and round(sec.top_margin.cm, 2) == 2.0 and round(sec.bottom_margin.cm, 2) == 2.0
                and round(sec.left_margin.cm, 2) == 2.2 else FAIL,
                f"{sec.top_margin.cm:.1f}/{sec.bottom_margin.cm:.1f}/{sec.left_margin.cm:.1f}"))
    st = d.styles["Normal"]
    ea = st.element.rPr.rFonts.get(qn("w:eastAsia"))
    res.append(("2 Normal 字体", OK if (st.font.name == "Times New Roman" and ea == "宋体"
                                     and st.font.size.pt == 10.5) else FAIL,
                f"{st.font.name}/{ea}/{st.font.size.pt}"))
    first = [p for p in d.paragraphs if p.text.strip()][1] if len(d.paragraphs) > 1 else None
    h = [p for p in d.paragraphs if p.runs and p.runs[0].bold and p.runs[0].font.size
         and p.runs[0].font.size.pt == 20]
    res.append(("3 首行标题 20pt 居中", OK if h and h[0].alignment == WD_ALIGN_PARAGRAPH.CENTER
                and "（主持人版）" not in h[0].text and "（学员版）" not in h[0].text else FAIL,
                h[0].text[:30] if h else "缺"))
    sizes = {p.runs[0].font.size.pt for p in d.paragraphs if p.runs and p.runs[0].font.size}
    sizes |= {r.font.size.pt for t in d.tables for row in t.rows for c in row.cells
              for p in c.paragraphs for r in p.runs if r.font.size}
    res.append(("4 字号集", OK if sizes <= {20, 16, 13.5, 11.5, 10.5, 10, 9.5, 8} else FAIL, str(sorted(sizes))))
    stu = "学员版" in path
    want = "1E4620" if stu else "1F3864"
    colors = {hexc(r) for p in d.paragraphs for r in p.runs if hexc(r)} | \
             {hexc(r) for t in d.tables for row in t.rows for c in row.cells
              for p in c.paragraphs for r in p.runs if hexc(r)}
    other = colors - {want, "FFFFFF", "888888", "808080", "222222", "1A1A1A", "333333"}
    res.append(("5 配色唯一", OK if not other else FAIL, f"{want} 额外={sorted(other)}"))
    hdr = sec.header.paragraphs[0].text
    exp_prefix = f"读书会{series} · 第1周 · {edition}（{weeks}周版） · "
    res.append(("6 页眉文案", OK if hdr.startswith(exp_prefix) and hdr.endswith("主持人版" if not stu else "学员版")
                else FAIL, hdr))
    flds = re.findall(r"<w:instrText[^>]*>([^<]*)</w:instrText>", sec.footer.paragraphs[0]._p.xml)
    ftxt = re.sub(r"[—\-\s]", "", sec.footer.paragraphs[0].text)
    res.append(("7 页脚 PAGE 域", OK if flds == ["PAGE"] and not ftxt else FAIL,
                f"{flds} 文本={sec.footer.paragraphs[0].text!r}"))
    qs = [p for p in d.paragraphs if re.search(r"<w:left [^>]*w:color=", p._p.xml)]
    bad = 0
    for p in qs:
        x = p._p.xml
        if f'w:color="{want}"' not in x or 'w:fill="EEF3F9"' not in x:
            bad += 1
        if not p.paragraph_format.left_indent or round(p.paragraph_format.left_indent.cm, 2) != 0.45:
            bad += 1
    res.append(("8 引用块三属性", OK if qs and bad == 0 else FAIL, f"{len(qs)} 段，异常 {bad}"))
    tb_bad = []
    for t in d.tables:
        if t.style.name != "Table Grid":
            tb_bad.append(t.style.name)
            continue
        s0 = t.rows[0].cells[0]._tc.tcPr.find(qn("w:shd"))
        if s0 is None or s0.get(qn("w:fill")) != want:
            tb_bad.append("表头底色")
        for ri, row in enumerate(t.rows):
            f = row.cells[0]._tc.tcPr.find(qn("w:shd"))
            fill = f.get(qn("w:fill")) if f is not None else None
            if ri >= 1 and ri % 2 == 0 and fill != "EEF2F8":
                tb_bad.append(f"第{ri}行隔行")
    res.append(("9 表格样式", OK if not tb_bad else FAIL, f"{len(d.tables)} 张，异常 {tb_bad}"))
    resid = [p.text[:40] for p in d.paragraphs if re.search(r"\*\*|^#{1,6} |<!--|^\|.*\|$", p.text)]
    resid += [c.text[:30] for t in d.tables for row in t.rows for c in row.cells
              if "**" in c.text or "|" in c.text]
    res.append(("11 md 残留", OK if not resid else FAIL, f"{len(resid)} 处 {resid[:2]}"))
    media = [n for n in zipfile.ZipFile(path).namelist() if n.startswith("word/media/")]
    res.append(("12 不嵌图", OK if not media else FAIL, f"media={len(media)}"))
    print("=" * 70)
    print(path.split("/")[-1])
    allp = True
    for name, st_, note in res:
        allp &= (st_ == OK)
        print(f"  [{st_}] {name}  {note}")
    print("  →", "全部通过" if allp else "有未通过项")
    return allp


if __name__ == "__main__":
    args = sys.argv[1:]
    weeks = int(args[0]); edition = args[1]
    ok = True
    for p in args[2:]:
        ok &= check(p, "01", weeks, edition)
    print("\n整体:", "PASS" if ok else "FAIL")
