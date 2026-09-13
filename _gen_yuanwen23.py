#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen23.py — 读书会23 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen23.py
"""
import os, re, glob, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会23素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会23_小问答经讲记萨迦耶见与圣八支道_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "经之缘起与萨迦耶=五取蕴",
    2: "萨迦耶的执取机制与观照",
    3: "萨迦耶灭、十二缘起与四圣谛",
    4: "二十种萨迦耶见（身见/我见）",
    5: "导向萨迦耶灭的圣八支道构成",
    6: "圣八支道与戒·三摩地·慧三蕴",
    7: "三摩地：定义、依止与修习",
    8: "三受、受随观与随眠",
}

def main():
    parts = [
        "# 📖 读书会23《〈小问答经〉讲记（萨迦耶见与圣八支道）》原文全集\n",
        f"\n> 📅 最近更新：{datetime.date.today():%Y-%m-%d}　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，照实保留。\n",
        "> 核心素材：2025-11《小问答经》讲记13讲课件（pdf）＋《根本五十篇·小问答经》经文原文＋《蕴品》五取蕴经文及相关开示。\n",
        "> 打开方式：ima 知识库「古源尊者开示及上座部佛教资料」搜索材料标题；media_id 均为完整串。\n",
    ]
    total = 0
    for path in SRC:
        w = int(re.search(r"第(\d+)周", path).group(1))
        t = open(path, encoding="utf-8").read()
        blocks = re.split(r"^(?=## 材料)", t, flags=re.M)
        parts.append(f"\n\n---\n\n# 第{w}周　{WEEK_TITLE[w]}\n")
        parts.append(f"\n> 照录底本：{os.path.basename(path)}（fetch 逐字照录，含缺口注记）\n")
        n = 0
        for b in blocks[1:]:
            b = b.strip()
            if not b:
                continue
            n += 1
            parts.append(f"\n{b}\n")
            total += 1
    out = "".join(parts)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"合计 {total} 块材料 → {OUT}（{len(out):,} 字符）")

if __name__ == "__main__":
    main()
