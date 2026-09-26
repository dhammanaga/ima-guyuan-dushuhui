#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_gen_yuanwen06.py — 读书会06（四念处·一·身念处）原文全集生成脚本
从各周主持人版 md 中提取「## 📖 共读原文」节内容（到下一个 ## 节为止），
按周次顺序拼装，每周前加 "# 第X周 <周标题>" 分隔头。
纯汇编，不改写原文。生成后核对：每周非空、总字符数 > 9 万。
"""
import os
import re
import sys

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
PKG = os.path.join(BASE, "交付成果/读书会06_四念处（一）身念处与受念处_8周资料包")
OUT = os.path.join(PKG, "原文全集.md")

WEEK_FILES = [
    "第1周_四念处总说与二十一种修法框架_主持人版.md",
    "第2周_身念处（一）——入出息念_主持人版.md",
    "第3周_身念处（二）——四威仪_主持人版.md",
    "第4周_身念处（三）——四种正知_主持人版.md",
    "第5周_身念处（四）——三十二身分_主持人版.md",
    "第6周_身念处（五）——界作意与墓园九相_主持人版.md",
    "第7周_受念处（一）——九种受的如实观_主持人版.md",
    "第8周_受念处（二）——受与解脱及身受整合_主持人版.md",
]

HEADER = """<div align="right">📅 最近更新：2026-09-10 15:00　|　v1.0</div>

# 四念处（一）身念处与受念处读书会 · 原文全集

> **本全集收录「读书会06·四念处（一）身念处与受念处」全部共读原文的完整文字，按周次编排（第1周→第8周），全部真实取自知识库「古源尊者开示及上座部佛教资料」。**
>
> - **本集用法**：每周共读文档（主持人版/学员版）中已嵌入当周所需全部段落；本全集按“第1周→第8周”汇总各周共读块，供课后完整查阅、对照与复习——**使用资料包过程中无需再去查知识库**。想重读某一周的原文，直接翻到对应“第X周”部分即可。
> - **标注约定**：每份材料含“段落优先级”行与**出处信息行**（标题／文件类型／说明／知识库出处／media_id／打开方式）；**★核心段落**为时间不够时的必读段，**◈扩展段落**为时间富余时的可选段；录音转写段首的时间码（如[00:01:45]）是出处标记，朗读时跳过不念；（ ）内为整理注记，同样跳过不念。
> - **“（依据录音转写整理）”的含义**：该材料来自录音转写稿，已按上下文校对明显同音错字（各材料“说明”行内注明主要校对项），非逐字原稿；请以原录音为准。
> - **“[generated, not original text]”标注的含义**：知识库提取工具返回该标注时，表示返回文本为整理版而非逐字原稿；本全集在对应材料的“说明”行如实保留该标注，照常使用。
> - **PDF 提取缺口的处理**：个别 PDF 课件在知识库片段中存在图形页/图表/页眉排版等提取缺口，全部**如实标注**在对应材料“说明”行内（如第6周“（课件图：……）”为图示说明，朗读时跳过不念），不虚构、不臆补原文。
> - **跨周共用资源**：《〈大念处经〉析解·帕奥西亚多202406V2.0》（第3周材料②取威仪路章／第4周材料③取正知章）与《四念处3-〈大念处经〉讲记2》（第3周材料③取四威仪段／第6周材料③取世界差别段）为跨周共用资源，另第6周材料①与材料①（续）取自《第183讲》同一课件的两个不同段落——同一资源均**按章节切分、照录段落互不重复**，拆分情况见各材料“说明”行。
> - 全集**一律不放置链接**（知识库临时导出链接会过期）；需要查看原件时，按各材料“打开方式”所列关键词在 ima 知识库搜索即可打开。

---
"""

def main():
    parts = [HEADER]
    total = 0
    report = []
    for i, fn in enumerate(WEEK_FILES, 1):
        path = os.path.join(PKG, fn)
        text = open(path, encoding="utf-8").read()

        # 周标题：第一个 "# 第X周：...（主持人版）" 行
        m = re.search(r"^# 第(\d+)周[：:](.+?)(（主持人版）)\s*$", text, flags=re.M)
        if not m:
            print(f"[FAIL] {fn}: 未找到周标题行"); sys.exit(1)
        week_no = int(m.group(1))
        week_title = m.group(2).strip()
        if week_no != i:
            print(f"[FAIL] {fn}: 周号 {week_no} 与顺序 {i} 不符"); sys.exit(1)

        # 共读原文节：从 "## 📖 共读原文" 行到下一个 "## " 行（不含）
        m2 = re.search(r"^## 📖 共读原文.*$", text, flags=re.M)
        if not m2:
            print(f"[FAIL] {fn}: 未找到共读原文节"); sys.exit(1)
        start = m2.start()
        nxt = re.search(r"^## (?!📖 共读原文)", text[m2.end():], flags=re.M)
        end = m2.end() + nxt.start() if nxt else len(text)
        sec = text[start:end].rstrip() + "\n"

        sec_chars = len(sec)
        if sec_chars == 0:
            print(f"[FAIL] 第{week_no}周提取为空"); sys.exit(1)

        parts.append(f"\n# 第{week_no}周 {week_title}\n\n{sec}")
        total += sec_chars
        report.append(f"第{week_no}周 《{week_title}》 共读块 {sec_chars:,} 字符")

    out_text = "".join(parts)
    total_chars = len(out_text)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out_text)

    print("=" * 60)
    for r in report:
        print("✅ " + r)
    print("-" * 60)
    print(f"每周提取非空核对: 8/8 通过")
    print(f"原文全集总字符数: {total_chars:,}（要求 > 90,000 → {'达标' if total_chars > 90000 else '不达标'}）")
    print(f"落盘: {OUT}")

if __name__ == "__main__":
    main()
