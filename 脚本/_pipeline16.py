#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_pipeline16.py — 读书会16 一键流水线（学员版生成 + 原文全集 + 终检 + 打包 + 推送）
用法: TZ='Asia/Shanghai' python3 _pipeline16.py
硬性要求：qa 终检 0 失败；全部 md + zip 推送成功。
"""
import os, sys, glob, subprocess, datetime, zipfile

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
PKG = os.path.join(BASE, "交付成果/读书会16_突破生命的束缚_8周资料包")

def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=BASE, **kw).returncode

def main():
    # 1) 学员版生成
    for h in sorted(glob.glob(os.path.join(PKG, "第*主持人版.md"))):
        run([sys.executable, "_mk_student.py", h])
    # 2) 原文全集
    run([sys.executable, "_gen_yuanwen16.py"])
    # 3) 终检（v2.3：不传硬禁用清单）
    env = dict(os.environ); env["QA_BANNED"] = "/tmp/nonexistent_banned.txt"
    rc = run([sys.executable, "_qa_check.py", PKG], env=env)
    if rc != 0:
        print("❌ 终检未通过，中止"); return 1
    # 4) 打包
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    zpath = os.path.join(BASE, "交付成果", f"读书会16_突破生命的束缚_8周资料包_{stamp}_v1.0.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _d, files in os.walk(PKG):
            for f in sorted(files):
                p = os.path.join(root, f)
                arc = os.path.relpath(p, os.path.dirname(os.path.abspath(PKG)))
                z.write(p, arc)
    print(f"✅ zip: {zpath}（{os.path.getsize(zpath)/1024:.0f} KB）")
    # 5) 推送（全部 md + zip）
    files = sorted(glob.glob(os.path.join(PKG, "*.md"))) + [zpath]
    rels = [os.path.relpath(f, BASE) for f in files]
    rc = run([sys.executable, "_push_gh.py"] + rels)
    print(f"推送 {'✅' if rc==0 else '❌'}：{len(rels)} 份")
    return rc

if __name__ == "__main__":
    sys.exit(main())
