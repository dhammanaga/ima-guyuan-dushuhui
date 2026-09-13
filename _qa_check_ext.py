#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_qa_check_ext.py —— 读书会资料「时间 / 内容 / 安全」扩展校验

在原 _qa_check.py（双版本逐字一致 / 禁用清单 / 临时链接）之外，补充：
  1) 时间封顶：各环节时长之和 ≤ 120，且与"信息卡总时长"声明一致
  2) 环节齐备：静心 / 共读 / 分享 / 讨论 / 练习 / 收尾
  3) 安全声明：心理安全 / 保密 / 可随时暂停 / 禁忌
  4) 说教腔初筛：高说教风险句式
  5) 定界标记：不得出现全角 <！--

用法：
    python3 _qa_check_ext.py <文件.md 或 目录>
退出码：0 = 全过；1 = 有失败项
"""
import sys, os, re, glob

MAX_TOTAL = 120
REQUIRED_SECTIONS = ["静心", "共读", "分享", "讨论", "禅修", "收尾"]
SAFETY_KEYWORDS = ["心理安全", "保密", "可随时暂停", "禁忌"]

SEC_RE = re.compile(r"[（(]\s*(\d+)\s*(?:min|分钟)\s*[）)]")        # （10 min）/（10分钟）
TOTAL_RE = re.compile(r"时长\s*[:：]?\s*(\d+)\s*(?:min|分钟)")      # 时长120min
PREACH_RE = re.compile(r"你应该|你必须|一定要|只要.{0,8}就.{0,6}(?:能|会|可以)")

def check_file(path):
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    fails, warns = [], []

    # 1) 时间封顶
    secs = [int(x) for x in SEC_RE.findall(txt)]
    total_decl = [int(x) for x in TOTAL_RE.findall(txt)]
    if secs:
        s = sum(secs)
        if s > MAX_TOTAL:
            fails.append("环节时长之和 = %d 分钟 > %d（超 %d 分钟）" % (s, MAX_TOTAL, s - MAX_TOTAL))
        if total_decl and s != total_decl[0]:
            fails.append("环节之和 = %d，与声明总时长 = %d 不一致" % (s, total_decl[0]))
    else:
        warns.append("未解析到环节时长（格式应为 如『（10 min）』）")

    # 2) 环节齐备
    missing = [k for k in REQUIRED_SECTIONS if k not in txt]
    if missing:
        fails.append("缺少环节：" + " / ".join(missing))

    # 3) 安全声明
    ms = [k for k in SAFETY_KEYWORDS if k not in txt]
    if ms:
        warns.append("缺少安全关键词：" + " / ".join(ms))

    # 4) 说教腔初筛
    hits = PREACH_RE.findall(txt)
    if hits:
        warns.append("可疑说教句式 %d 处（请人工复核）：%s" % (len(hits), "；".join(hits[:5])))

    # 5) 全角定界标记
    if "<！--" in txt:
        fails.append("存在全角定界标记 <！--（应为半角 <!--）")

    return fails, warns, secs

def collect(target):
    if os.path.isdir(target):
        return sorted(glob.glob(os.path.join(target, "**", "*.md"), recursive=True))
    return [target]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    files = collect(sys.argv[1])
    if not files:
        print("未找到任何 .md 文件：", sys.argv[1]); sys.exit(2)

    total_fail = 0
    for fp in files:
        fails, warns, secs = check_file(fp)
        name = os.path.basename(fp)
        if fails:
            total_fail += 1
            print("✗ %s" % name)
            for x in fails: print("    [失败] " + x)
            for x in warns: print("    [提醒] " + x)
        else:
            print("✓ %s   (环节时长 %s，合计 %d)" % (name, secs, sum(secs) if secs else 0))
            for x in warns: print("    [提醒] " + x)

    print("\n==== 汇总：%d 个文件，%d 个失败 ====" % (len(files), total_fail))
    sys.exit(1 if total_fail else 0)

if __name__ == "__main__":
    main()
