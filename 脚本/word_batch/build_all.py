#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 批 4周版 读书会01-14：md → docx（复用 _mk_word_latest.convert，不复制渲染代码）"""
import os, sys, glob, json, importlib.util

spec = importlib.util.spec_from_file_location("MK", "/sandbox/workspace/scripts/_mk_word_latest.py")
MK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MK)

SRC = "/sandbox/workspace/src"
OUT = "/sandbox/workspace/out"
EDITION = "第八轮（第8版）"
WEEKS = 4
SERIES = [f"{i:02d}" for i in range(1, 15)]


def main(only=None):
    want = only or SERIES
    stats = []
    for nn in want:
        mds = sorted(x for x in glob.glob(os.path.join(SRC, "读书会" + nn, "*.md"))
                     if not os.path.basename(x).startswith(MK.SKIP_NAMES))
        os.makedirs(os.path.join(OUT, "读书会" + nn), exist_ok=True)
        for md in mds:
            bn = os.path.basename(md)
            m = MK.WEEK_RE.match(bn)
            assert m, bn
            wk, role = m.group(1), m.group(3)
            stu = role == "学员版"
            color, hexc = (MK.STU_C, "1E4620") if stu else (MK.HOST_C, "1F3864")
            header = MK.build_header(nn, bn, EDITION, WEEKS)
            out_name = "读书会%s_第%s周_%s_%s.docx" % (nn, wk, m.group(2), role)
            outpath = os.path.join(OUT, "读书会" + nn, out_name)
            doc = MK.convert(md, outpath, header, color, hexc)
            stats.append(dict(nn=nn, week=int(wk), role=role, md=md,
                              docx=outpath, name=out_name,
                              tables=len(doc.tables)))
            print("✅", out_name, "表", len(doc.tables))
    json.dump(stats, open("/sandbox/workspace/work/build_stats.json", "w"), ensure_ascii=False, indent=1)
    print("合计 docx:", len(stats))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
