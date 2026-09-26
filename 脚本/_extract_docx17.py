#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 交付成果/*.docx 提取段落，定位「读书会17」「菩萨道」「十波罗蜜」方案。"""
import sys, glob, os
try:
    from docx import Document
except ImportError:
    os.system("pip install python-docx -q")
    from docx import Document

ROOT = "/sandbox/workspace/新型读书会.大佛寺/第二轮/交付成果"
KEY = sys.argv[1] if len(sys.argv) > 1 else "17"
for p in sorted(glob.glob(os.path.join(ROOT, "*.docx"))):
    try:
        d = Document(p)
    except Exception as e:
        print(f"[skip] {p}: {e}"); continue
    paras = [x.text for x in d.paragraphs]
    hits = []
    for i, t in enumerate(paras):
        if ("读书会17" in t) or ("读书会17" in t) or ("菩萨道" in t) or ("十波罗蜜" in t) or ("巴拉密" in t and "读书会" in t):
            hits.append(i)
    if hits:
        print(f"\n########## {os.path.basename(p)} (total {len(paras)} paras) 命中 {len(hits)} ##########")
        lo = max(0, hits[0]-3); hi = min(len(paras), hits[-1]+3)
        for i in range(lo, hi):
            t = paras[i].strip()
            if t:
                print(f"[{i}] {t}")
