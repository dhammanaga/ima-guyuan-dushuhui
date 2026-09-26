#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地 ↔ GitHub 逐文件对账：05–10、19–25 修订目录 + 相关 zip + 根脚本。"""
import os, glob, json, urllib.request, urllib.parse, sys
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "dhammanaga/ima-guyuan-dushuhui"
API = f"https://api.github.com/repos/{REPO}/contents"
REV = "/sandbox/workspace/交付成果/第二轮修订版"
LOCAL_ROOT = "/sandbox/workspace"


def api(path):
    url = API + "/" + urllib.parse.quote(path) + "?ref=main"
    req = urllib.request.Request(url, headers={"Authorization": "token " + TOKEN})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def remote_map(path):
    d = api(path)
    return {x["name"]: x.get("size") for x in d}


series = ["05", "06", "07", "08", "09", "10", "19", "20", "21", "22", "23", "24", "25"]
problems = []

# 1) 各系列目录 20 份对账
for s in series:
    ld = glob.glob(os.path.join(REV, "读书会%s_*（第二版修订）" % s))[0]
    lfiles = {os.path.basename(p): os.path.getsize(p) for p in glob.glob(ld + "/*")}
    rfiles = remote_map("交付成果/第二轮修订版/" + os.path.basename(ld))
    miss = set(lfiles) - set(rfiles)
    diff = {k for k in lfiles if k in rfiles and lfiles[k] != rfiles[k]}
    extra = set(rfiles) - set(lfiles)
    tag = "✓" if not (miss or diff or extra) else "✗"
    print("%s 读书会%s 本地%d/远端%d  缺%s 异%s 多%s" % (
        tag, s, len(lfiles), len(rfiles), sorted(miss)[:2], sorted(diff)[:2], sorted(extra)[:2]))
    if miss or diff or extra:
        problems.append((s, miss, diff, extra))

# 2) zip 对账
rzips = {x["name"]: x["size"] for x in api("交付成果/第二轮修订版") if x["name"].endswith(".zip")}
lzips = {}
for p in glob.glob(REV + "/*.zip"):
    lzips[os.path.basename(p)] = os.path.getsize(p)
print("-" * 70)
for s in ["05", "06", "07", "08", "09", "10", "19", "20", "21", "22", "23", "24", "25"]:
    lz = [n for n in lzips if ("读书会%s_" % s) in n]
    rz = [n for n in rzips if ("读书会%s_" % s) in n]
    ok = len(lz) == 1 and len(rz) == 1 and lzips[lz[0]] == rzips[rz[0]]
    print("%s zip %s 本地%s 远端%s" % ("✓" if ok else "✗", s, lz, rz))
    if not ok:
        problems.append((s, "zip", lz, rz))

# 3) 根脚本
print("-" * 70)
for f in ["_revise1925.py", "_data_1925.py", "_qa_all.py", "_verify_read.py", "_final_check.py", "_mk_student.py", "_fix0510_titles.py"]:
    lp = os.path.join(LOCAL_ROOT, f)
    rl = remote_map("")
    ok = f in rl and os.path.getsize(lp) == rl[f]
    print("%s %s 本地%s 远端%s" % ("✓" if ok else "✗", f, os.path.getsize(lp), rl.get(f)))
    if not ok:
        problems.append((f, "script"))

print("=" * 70)
print("对账结束：%d 组异常" % len(problems))
for p in problems:
    print("  ✗", p)
sys.exit(1 if problems else 0)
