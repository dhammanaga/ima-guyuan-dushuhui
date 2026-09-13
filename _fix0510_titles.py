#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05–10 第二版修订：学员版环节标题去除时长括号（对齐《读书会修订执行手册 v1.4》§10.1）。"""
import os, re, glob
REV = "/sandbox/workspace/交付成果/第二轮修订版"
TITLE_RE = re.compile(r"（\s*约?\s*\d+\s*(?:min|分钟)\s*([^）]*)）")


def repl(m):
    tail = m.group(1).strip().lstrip("·").strip()
    return ("（%s）" % tail) if tail else ""


def main():
    for s in ["05", "06", "07", "08", "09", "10"]:
        d = glob.glob(os.path.join(REV, "读书会%s_*（第二版修订）" % s))[0]
        n = 0
        for f in sorted(glob.glob(os.path.join(d, "*学员版.md"))):
            lines = open(f, encoding="utf-8").read().split("\n")
            out = []
            changed = 0
            for l in lines:
                if l.startswith("## "):
                    nl = TITLE_RE.sub(repl, l)
                    if nl != l:
                        changed += 1
                    l = nl
                out.append(l)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("\n".join(out))
            n += 1
            print("  %s %-52s 标题改动 %d" % (s, os.path.basename(f)[:40], changed))
        # CHANGELOG 追加一句（v2.0 条目内）
        cp = os.path.join(d, "更新日志_CHANGELOG.md")
        t = open(cp, encoding="utf-8").read()
        note = "- 学员版环节标题去除时长括号（`（N min）`），对齐《读书会修订执行手册 v1.4》§10.1\n"
        if "学员版环节标题去除时长括号" not in t:
            m = re.search(r"(?m)^(# 📝 更新日志.*\n)", t)
            if m:
                # 在 v2.0 条目的最后一条 bullet 之后插入
                m2 = re.search(r"(?m)^(- 学员版由修订后主持人版脚本重新派生[^\n]*\n)", t)
                if m2:
                    t = t[:m2.end()] + note + t[m2.end():]
                else:
                    t = t[:m.start()] + note + t[m.start():]
            with open(cp, "w", encoding="utf-8") as fh:
                fh.write(t)
            print("  %s CHANGELOG 已补注" % s)


if __name__ == "__main__":
    main()
