#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B 批 4周版 读书会15-27：md → docx（复用 _mk_word_latest.convert）
用法：
  python3 build_sel.py 18:1 22:1 25:1 27:1      # 指定系列:周
  python3 build_sel.py 18 22 25 27              # 指定系列全 4 周
  python3 build_sel.py all                      # 15-27 全部
"""
import os, sys, glob, json, importlib.util

spec = importlib.util.spec_from_file_location("MK", "/sandbox/workspace/scripts/_mk_word_latest.py")
MK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MK)

SRC = "/sandbox/workspace/src"
OUT = "/sandbox/workspace/out"
EDITION = "第八轮（第8版）"
WEEKS = 4
SERIES = [f"{i:02d}" for i in range(15, 28)]
STATS = "/sandbox/workspace/work/build_stats.json"


def main(args):
    if not args or args == ["all"]:
        args = SERIES
    plan = []          # (nn, week or None)
    for a in args:
        if ":" in a:
            nn, w = a.split(":")
            plan.append((nn, int(w.lstrip("w"))))
        else:
            plan.append((a, None))
    stats = json.load(open(STATS)) if os.path.exists(STATS) else []
    done = {s["docx"] for s in stats}
    for nn, w in plan:
        mds = sorted(x for x in glob.glob(os.path.join(SRC, "读书会" + nn, "*.md"))
                     if not os.path.basename(x).startswith(MK.SKIP_NAMES))
        os.makedirs(os.path.join(OUT, "读书会" + nn), exist_ok=True)
        for md in mds:
            bn = os.path.basename(md)
            m = MK.WEEK_RE.match(bn)
            assert m, bn
            wk, role = m.group(1), m.group(3)
            if w is not None and int(wk) != w:
                continue
            stu = role == "学员版"
            color, hexc = (MK.STU_C, "1E4620") if stu else (MK.HOST_C, "1F3864")
            header = MK.build_header(nn, bn, EDITION, WEEKS)
            out_name = "读书会%s_第%s周_%s_%s.docx" % (nn, wk, m.group(2), role)
            outpath = os.path.join(OUT, "读书会" + nn, out_name)
            doc = MK.convert(md, outpath, header, color, hexc)
            rec = dict(nn=nn, week=int(wk), role=role, md=md, docx=outpath,
                       name=out_name, tables=len(doc.tables))
            stats = [s for s in stats if s["docx"] != outpath] + [rec]
            print("✅", out_name, "表", len(doc.tables))
            sys.stdout.flush()
            json.dump(stats, open(STATS, "w"), ensure_ascii=False, indent=1)
    json.dump(stats, open(STATS, "w"), ensure_ascii=False, indent=1)
    print("累计 docx:", len(stats))


if __name__ == "__main__":
    main(sys.argv[1:])
