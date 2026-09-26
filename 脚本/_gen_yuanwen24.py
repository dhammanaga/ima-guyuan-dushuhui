#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen24.py — 读书会24 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen24.py
"""
import os, re, glob, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会24素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会24_三十二身分（身至念）专修_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "总论：定义、出处与六组划分",
    2: "第一组·第二组身分观照",
    3: "第三组身分观照（心肝脾肺膜）",
    4: "第四至六组身分观照",
    5: "七种学习善巧与十种作意善巧",
    6: "可厌作意与顺逆序修法",
    7: "修习利益与定力成就",
    8: "三十二身分与四界差别、观智次第",
}

def main():
    parts = [
        "# 📖 读书会24《三十二身分（身至念）专修》原文全集\n",
        f"\n> 📅 最近更新：{datetime.date.today():%Y-%m-%d}　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，照实保留。\n",
        "> 核心素材：百花古寺 2025 百日禅专讲 4 讲（2025-01-22 至 01-25，课件＋录音）＋2025-05-03「03_三十二身分1」专题＋13_禅修引导＋四界差别专讲。\n",
        "> 打开方式：ima 知识库「古源尊者开示及上座部佛教资料」搜索材料标题；media_id 均为完整串。\n",
    ]
    total = 0
    for path in SRC:
        w = int(re.search(r"第(\d+)周", path).group(1))
        t = open(path, encoding="utf-8").read()
        blocks = re.split(r"^(?=## 材料)", t, flags=re.M)
        parts.append(f"\n\n---\n\n# 第{w}周　{WEEK_TITLE.get(w,'')}\n")
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
