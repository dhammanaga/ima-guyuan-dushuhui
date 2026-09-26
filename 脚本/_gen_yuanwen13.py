#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen13.py — 读书会13 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen13.py
"""
import os, re, glob, datetime
from datetime import timezone, timedelta
CST = timezone(timedelta(hours=8))  # 北京时间

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会13素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会13_业与轮回_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "业的总说——\"思即是业\"与原理",
    2: "业的分类（一）——依作用与依成熟次序",
    3: "业的分类（二）——依成熟时间与依成熟地",
    4: "善业、不善业与三福行事",
    5: "临终心路与结生",
    6: "业的同一性、多样性与运作定则",
    7: "轮回的机制与三十一界",
    8: "业论的生活启示与总结",
}

def main():
    parts = [
        "# 📖 读书会13《业与轮回》原文全集\n",
        f"\n> 📅 最近更新：{datetime.datetime.now(CST):%Y-%m-%d %H:%M}（北京时间）　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，`[generated, not original text]` 标注与缺口说明照实保留。\n",
        "> 打开方式：ima 知识库「古源尊者开示及上座部佛教资料」搜索材料标题；media_id 均为完整串。\n",
    ]
    total = 0
    for path in SRC:
        w = int(re.search(r"第(\d+)周", path).group(1))
        t = open(path, encoding="utf-8").read()
        blocks = re.split(r"^(?=## 材料)", t, flags=re.M)
        header = blocks[0].strip()
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
        print(f"第{w}周: {n} 块材料")
    out = "".join(parts)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"\n合计 {total} 块材料 → {OUT}（{len(out):,} 字符）")

if __name__ == "__main__":
    main()
