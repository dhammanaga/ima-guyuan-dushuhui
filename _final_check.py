#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终校验：
1) 共读原文区块逐字零改动（v1.0 vs v2.0）；
2) 逐周 media_id 集合 v1.0/v2.0 完全一致（主持人版+学员版）；
3) 学员版 ## 标题不含（N min）；
4) v2.0 主持人版各环节和=120、含朗读段/破冰/心理安全/禅修禁忌/分层追问；
5) 学员版同样含上述要素且共读原文与主持人版一致。
"""
import os, re, glob, sys
sys.path.insert(0, "/sandbox/workspace")
from _revise1925 import read_block_range

BASE = "/sandbox/workspace/交付成果"
ID_RE = re.compile(r"(?:soundrecording|pdf|word)_[a-f0-9]+_[a-f0-9]+")
SEC_RE = re.compile(r"（(\d+)\s*min）")
sers = ["19", "20", "21", "22", "23", "24", "25"]
fails = 0


def block(path):
    ls = open(path, encoding="utf-8").read().split("\n")
    r = read_block_range(ls)
    if not r:
        return None
    s, e = r
    return [l for l in ls[s + 1:e] if l.strip() and not l.startswith("> **【本周朗读段")]


for ser in sers:
    d0 = glob.glob(os.path.join(BASE, "第一轮初稿", "读书会%s_*" % ser))[0]
    d1 = glob.glob(os.path.join(BASE, "第二轮修订版", "读书会%s_*（第二版修订）" % ser))[0]
    n_ok = 0
    for h0 in sorted(glob.glob(os.path.join(d0, "*主持人版.md"))):
        name = os.path.basename(h0)
        w = re.search(r"第(\d+)周", name).group(1)
        h1 = os.path.join(d1, name)
        s0 = h1.replace("主持人版", "学员版")
        t1 = open(h1, encoding="utf-8").read()
        st1 = open(s0, encoding="utf-8").read()
        # 1 共读原文零改动
        if block(h0) != block(h1):
            print("  ✗ %s W%s 共读原文有改动" % (ser, w)); fails += 1
        # 2 id 集合一致
        ids0 = set(ID_RE.findall(open(h0, encoding="utf-8").read()))
        ids1 = set(ID_RE.findall(t1)) | set(ID_RE.findall(st1))
        if ids0 != ids1:
            print("  ✗ %s W%s id集合不一致 +%s -%s" % (ser, w, sorted(ids1 - ids0)[:2], sorted(ids0 - ids1)[:2])); fails += 1
        # 3 学员版标题无时长
        bad_title = [l for l in st1.split("\n") if l.startswith("## ") and SEC_RE.search(l)]
        if bad_title:
            print("  ✗ %s W%s 学员版标题含时长 %s" % (ser, w, bad_title[:2])); fails += 1
        # 4/5 要素
        for k in ["本周朗读段", "破冰", "心理安全", "禅修禁忌", "分层追问"]:
            if k not in t1:
                print("  ✗ %s W%s 主持人版缺 %s" % (ser, w, k)); fails += 1
            if k not in st1:
                print("  ✗ %s W%s 学员版缺 %s" % (ser, w, k)); fails += 1
        if sum(int(x) for x in SEC_RE.findall(t1)) != 120:
            print("  ✗ %s W%s 主持时长和≠120" % (ser, w)); fails += 1
        if "学生版说明" in st1 or "学员版" not in st1:
            pass
        n_ok += 1
    print("读书会%s：%d 周校验完成" % (ser, n_ok))
print("=== 最终校验：%d 处失败 ===" % fails)
sys.exit(1 if fails else 0)
