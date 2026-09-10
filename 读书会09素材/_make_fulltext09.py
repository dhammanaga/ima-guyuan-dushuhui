#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_make_fulltext09.py — 读书会09《原文全集》脚本化组装（零LLM）
从8周主持人版提取「## 📖 共读原文」节（至下一「## 💬」止），删除主持人专属操作行，
按周组装为 原文全集.md（材料节完整保留，参照08线"## 材料"节切分零遗漏口径）。
"""
import re
import glob
import os

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
PKG = BASE + "/交付成果/读书会09_四圣谛二灭与道_8周资料包"
OUT = PKG + "/原文全集.md"

TITLES = {
    1: "苦集回顾与苦灭圣谛总说",
    2: "苦灭圣谛深讲——有余/无余涅槃与十组渴爱之灭",
    3: "道圣谛总说——八正道是唯一之道",
    4: "道谛义理（一）——三种断与八圣道分",
    5: "道谛义理（二）——十二道分（八正道＋四邪道支）",
    6: "八正道的整体运作与三十七道品",
    7: "涅槃与道果的证悟原理",
    8: "四圣谛完整回顾",
}

def extract(text):
    m = re.search(r"## 📖 共读原文（30 min）\n(.*?)\n## 💬", text, re.S)
    if not m:
        return None
    sec = m.group(1)
    # 删主持人专属行
    lines = [l for l in sec.split("\n") if not l.startswith("> ⚠️ 主持人操作：")]
    return "\n".join(lines).strip()

def main():
    parts = [
        "# 📚 原文全集 · 读书会09 四圣谛（二）——灭与道",
        "",
        "> 📅 最近更新：2026-09-10 22:25　|　脚本化组装自8周主持人版「共读原文」节（_make_fulltext09.py，零LLM、逐字一致）",
        "> 用途：全部共读原文的单一汇编，供打印与离线共读；每周原文与对应周文档**逐字一致**（qa锚点+实质原文行双校验）。",
        "> 使用提示：★核心/◈扩展标记、编者注（＞【编者注】）、音声时间码均照周文档保留；出处信息行（media_id 等）见各周文档或素材照录。",
        "",
        "---",
        "",
    ]
    total = 0
    for wk in range(1, 9):
        pat = os.path.join(PKG, f"第{wk}周_*主持人版.md")
        files = glob.glob(pat)
        if not files:
            raise SystemExit(f"❌ 缺第{wk}周主持人版")
        text = open(files[0], encoding="utf-8").read()
        sec = extract(text)
        if not sec:
            raise SystemExit(f"❌ 第{wk}周未提取到共读原文节")
        mats = len(re.findall(r"### 原文材料", sec))
        parts.append(f"## 第{wk}周：{TITLES[wk]}（共读原文·材料{mats}份）")
        parts.append("")
        parts.append(sec)
        parts.append("")
        parts.append("---")
        parts.append("")
        total += len(sec)
        print(f"✅ 第{wk}周：{len(sec):,} 字符，{mats} 份材料")
    out = "\n".join(parts)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"✅ 原文全集已生成：{OUT}（{len(out):,} 字符，8周共 {total:,} 字符原文）")

if __name__ == "__main__":
    main()
