#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量终检：ext 时长/环节/安全 + 双版本 + 禁用 + 新增 id 核验 + 版本说明。"""
import os, re, glob, subprocess, sys
BASE = "/sandbox/workspace/交付成果"
REV = os.path.join(BASE, "第二轮修订版")
SERS = {"19": "01-17", "20": "01-19", "21": "01-20", "22": "01-20", "23": "01-22", "24": "01-23", "25": "01-24"}
ID_RE = re.compile(r"(?:soundrecording|pdf|word)_[a-f0-9]+_[a-f0-9]+")

flag = 0
for ser in SERS:
    d1 = glob.glob(os.path.join(REV, "读书会%s_*（第二版修订）" % ser))[0]
    d0 = glob.glob(os.path.join(BASE, "第一轮初稿", "读书会%s_*" % ser))[0]
    print("=" * 72)
    print("读书会%s  %s" % (ser, os.path.basename(d1)))
    # ext 检查
    r = subprocess.run([sys.executable, "/sandbox/workspace/_qa_check_ext.py", d1],
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.splitlines() if "失败" in l]
    print("  [ext]  " + " | ".join(tail[-1:]) + "  (exit=%d)" % r.returncode)
    if r.returncode: flag += 1
    # 禁用 / 双版本
    banned_f = glob.glob("/sandbox/workspace/读书会%s素材/_禁用清单_*.txt" % ser)[0]
    env = dict(os.environ, QA_BANNED=banned_f)
    r2 = subprocess.run([sys.executable, "/sandbox/workspace/_qa_check.py", d1],
                        capture_output=True, text=True, env=env)
    hits = re.findall(r"禁用❌\{([^}]*)\}", r2.stdout)
    hitids = set()
    for h in hits:
        for x in re.findall(r"'([^']+)'", h):
            hitids.add(x)
    # 新增 id（v2.0 相对 v1.0）
    ids0, ids1 = set(), set()
    for f in glob.glob(os.path.join(d0, "*.md")):
        ids0 |= set(ID_RE.findall(open(f, encoding="utf-8").read()))
    for f in glob.glob(os.path.join(d1, "*.md")):
        ids1 |= set(ID_RE.findall(open(f, encoding="utf-8").read()))
    print("  [禁用] 命中 %d 个（均为 v1.0 既有：%s）" % (len(hitids), sorted(hitids) == sorted(hitids & ids0)))
    print("  [新增id] v2.0 相对 v1.0 新增 = %d 个 %s" % (len(ids1 - ids0), sorted(ids1 - ids0)[:5]))
    print("  [ext尾] " + " | ".join([l for l in r2.stdout.splitlines() if "硬性失败" in l]))
    # 版本说明
    rd = open(os.path.join(d1, "README_资料包说明.md"), encoding="utf-8").read()
    ch = open(os.path.join(d1, "更新日志_CHANGELOG.md"), encoding="utf-8").read()
    print("  [README版本说明] %s  [CHANGELOG v2.0] %s" % ("版本说明" in rd, "v2.0" in ch))
print("=" * 72)
print("ext 失败系列数 =", flag)
