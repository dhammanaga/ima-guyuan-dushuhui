#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验：修订前后主持人版「共读原文区块」逐字零改动（仅允许新增朗读段标记行）。"""
import os, re, glob, sys
sys.path.insert(0, "/sandbox/workspace")
from _revise1925 import read_block_range

BASE = "/sandbox/workspace/交付成果"


def block_txt(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    r = read_block_range(lines)
    if not r:
        return None
    s, e = r
    out = []
    for l in lines[s + 1:e]:          # 排除共读节标题行（其时长按手册改动）
        if l.startswith("> **【本周朗读段"):     # 仅忽略新增标记行
            continue
        if l.strip() == "":            # 忽略插入标记带来的空行
            continue
        out.append(l)
    return out


def main():
    sers = sys.argv[1:] or ["19", "20", "21", "22", "23", "24", "25"]
    bad = 0
    for ser in sers:
        d0 = glob.glob(os.path.join(BASE, "第一轮初稿", "读书会%s_*" % ser))[0]
        d1 = glob.glob(os.path.join(BASE, "第二轮修订版", "读书会%s_*（第二版修订）" % ser))[0]
        for h0 in sorted(glob.glob(os.path.join(d0, "*主持人版.md"))):
            w = re.search(r"第(\d+)周", os.path.basename(h0)).group(1)
            h1 = os.path.join(d1, os.path.basename(h0))
            a, b = block_txt(h0), block_txt(h1)
            if a == b:
                print("  ✓ %s W%s  共读原文区块零改动（%d 行）" % (ser, w, len(a)))
            else:
                bad += 1
                print("  ✗ %s W%s  差异！" % (ser, w))
                import difflib
                for x in list(difflib.unified_diff(a, b, lineterm=""))[:12]:
                    print("       " + x[:100])
    print("== 共读原文校验：%d 处失败 ==" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
