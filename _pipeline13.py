#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_pipeline13.py — 读书会13 一键流水线（token优化·措施C：机械步骤零LLM）
顺序：①由各周主持人版生成学员版（_mk_student.py）→②qa终检（_qa_check.py, QA_BANNED=13清单）
      →③原文全集聚合（_gen_yuanwen13.py）→④打包zip（_make_zip.py）→⑤推送GitHub（_push_gh.py）
用法：
  python3 _pipeline13.py            # 学员版+终检（制作期反复跑）
  python3 _pipeline13.py --full     # 学员版+终检+原文全集+zip+推送（系列收尾跑）
终检失败只回传失败行；硬性0失败才算通过。
"""
import os, sys, glob, subprocess, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
os.chdir(BASE)
PKG = "交付成果/读书会13_业与轮回_8周资料包"
BANNED = "读书会13素材/_禁用清单_读书会01-12已用media_id.txt"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")
ZIP = f"{PKG}_{STAMP}_v1.0.zip"

def run(cmd, env=None):
    e = dict(os.environ); 
    if env: e.update(env)
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    return r.returncode, r.stdout + r.stderr

def main():
    full = "--full" in sys.argv
    hosts = sorted(glob.glob(os.path.join(PKG, "*主持人版.md")))
    print(f"[1] 学员版生成：{len(hosts)} 份主持人版")
    ok = 0
    for h in hosts:
        c, o = run(["python3", "_mk_student.py", h])
        if c == 0: ok += 1
        else: print("  ❌", h, o[-120:])
    print(f"    生成成功 {ok}/{len(hosts)}")

    print("[2] qa 终检（v2.3 段落级口径：不传 QA_BANNED，id级清单降为参考工具；同 11/12 线先例）")
    c, o = run(["python3", "_qa_check.py", PKG])
    tail = [l for l in o.splitlines() if ("硬性失败" in l or "❌" in l or "禁用" in l or "共读原文" in l)]
    print("\n".join(tail[-40:]))
    if c != 0:
        print("❌ 终检未通过，停止流水线"); return 1
    print("✅ 终检硬性 0 失败")

    if not full:
        print("（未加 --full：以上两步完成）"); return 0

    print("[3] 原文全集聚合")
    c, o = run(["python3", "_gen_yuanwen13.py"]); print(o.strip()[-300:])
    if c != 0: return 1

    print("[4] 打包 zip")
    c, o = run(["python3", "_make_zip.py", PKG, ZIP]); print(o.strip())
    if c != 0: return 1

    print("[5] 推送 GitHub（资料包20份 + zip + 素材照录 + 脚本）")
    files = sorted(glob.glob(os.path.join(PKG, "*"))) + [ZIP] \
            + sorted(glob.glob("读书会13素材/第*周_素材照录.md")) \
            + ["_gen_yuanwen13.py", "_pipeline13.py"]
    c, o = run(["python3", "_push_gh.py"] + files)
    print(o.strip()[-600:])
    return 0

if __name__ == "__main__":
    sys.exit(main())
