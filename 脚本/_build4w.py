#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_build4w.py <NN> [NN2 ...] [--zip] —— 第三轮4周版一键编排：改制→适配→终检→(打包)
输出每系列摘要（几行）。"""
import os, sys, subprocess, glob, datetime, zipfile, json
from datetime import timezone, timedelta
CST = timezone(timedelta(hours=8))
BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
CFG = json.load(open(os.path.join(BASE, "_thirdround_titles.json"), encoding="utf-8"))
OUT_ROOT = os.path.join(BASE, "交付成果/第三轮修订版/第三轮4周版")

def run(args):
    r = subprocess.run(args, cwd=BASE, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def build(nn, dozip=False):
    print(f"===== 读书会{nn:02d} =====")
    for step in ([sys.executable, "_mk4w.py", str(nn)], [sys.executable, "_adapt_pkg4w.py", str(nn)]):
        c, o = run(step)
        if c != 0:
            print("  ❌", step, o[-300:]); return False
    cfg = CFG[str(nn)]
    pkg = os.path.join(OUT_ROOT, f"读书会{nn:02d}_{cfg['name']}_4周资料包（第三版修订）")
    c1, o1 = run([sys.executable, "_qa_check.py", pkg])
    c2, o2 = run([sys.executable, "_qa_check_ext.py", pkg])
    f1 = [l for l in o1.splitlines() if "硬性失败" in l]
    f2 = [l for l in o2.splitlines() if "汇总" in l]
    print("  QA:", f1[-1].strip() if f1 else "?", "|", f2[-1].strip() if f2 else "?")
    bad1 = [l for l in o1.splitlines() if "❌" in l]
    if bad1:
        print("   ⚠️", bad1[:3])
    ok = (c1 == 0 and c2 == 0)
    if dozip:
        ts = datetime.datetime.now(CST).strftime("%Y%m%d_%H%M")
        z = os.path.join(pkg, f"读书会{nn:02d}_{cfg['name']}_4周资料包（第三版修订）_{ts}_v3.0.zip")
        n = 0
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _d, files in os.walk(pkg):
                for f in sorted(files):
                    if f.endswith(".zip"):
                        continue
                    p = os.path.join(root, f)
                    zf.write(p, os.path.relpath(p, os.path.dirname(os.path.abspath(pkg))))
                    n += 1
        print(f"  zip: {n} files, {os.path.getsize(z)/1024:.0f} KB")
    return ok

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dozip = "--zip" in sys.argv
    res = {}
    for a in args:
        res[int(a)] = build(int(a), dozip)
    print("\n===== 汇总 =====")
    for k, v in res.items():
        print(f"  {k:02d}: {'✅' if v else '❌'}")
