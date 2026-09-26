#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_mk8w.py <NN> —— 第三轮8周版目录（D7 同步）：复制第二轮8周版包，更新头部时间戳为第三轮。
用法: python3 _mk8w.py <NN>"""
import os, sys, re, glob, shutil, json, datetime
from datetime import timezone, timedelta
CST = timezone(timedelta(hours=8))
BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC_ROOT = os.path.join(BASE, "交付成果/第二轮修订版")
OUT_ROOT = os.path.join(BASE, "交付成果/第三轮修订版/第三轮8周版")
CFG = json.load(open(os.path.join(BASE, "_thirdround_titles.json"), encoding="utf-8"))

def run(NN):
    cfg = CFG[str(NN)]
    srcdir = glob.glob(os.path.join(SRC_ROOT, f"读书会{NN:02d}_*_8周资料包（第二版修订）"))[0]
    outdir = os.path.join(OUT_ROOT, f"读书会{NN:02d}_{cfg['name']}_8周资料包（第三版修订）")
    os.makedirs(outdir, exist_ok=True)
    ts = datetime.datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    for f in glob.glob(os.path.join(srcdir, "*")):
        bn = os.path.basename(f)
        if bn.endswith(".zip"):
            continue
        dst = os.path.join(outdir, bn)
        shutil.copy2(f, dst)
        if bn.endswith(".md"):
            t = open(dst, encoding="utf-8").read()
            newline = f'<div align="right">📅 最近更新：{ts}　|　第三轮8周版同步：学员版主持人专属内容清理；元数据与 CHANGELOG 同步；结构仍6环节120min；共读原文一字未改</div>'
            if t.startswith("<div"):
                t = newline + "\n" + t.split("\n", 1)[1]
            else:
                t = newline + "\n\n" + t
            open(dst, "w", encoding="utf-8").write(t)
    print(f"✅ 8周版 → {outdir}（{len(glob.glob(outdir+'/*'))} 文件）")

if __name__ == "__main__":
    run(int(sys.argv[1]))
