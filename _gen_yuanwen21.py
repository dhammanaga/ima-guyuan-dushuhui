#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen21.py — 读书会21 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen21.py
"""
import os, re, glob, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会21素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会21_破妄显真破除三十八种修道上的自欺_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "自欺总论：善恶辨析与修道自欺的本质",
    2: "以「贪」为借口的伪装",
    3: "以「嗔/抗拒」为伪装的自我欺骗",
    4: "以「痴/禅定/中舍」为伪装的暗坑",
    5: "以「邪见/思察」为伪装的摄取",
    6: "以「自尊/我慢」为伪装的修行姿态",
    7: "以「悭吝/慈悲」为伪装的占有",
    8: "总摄对治：正见·正念·正精进铁三角",
}

def main():
    parts = [
        "# 📖 读书会21《破妄显真——破除三十八种修道上的自欺》原文全集\n",
        f"\n> 📅 最近更新：{datetime.date.today():%Y-%m-%d}　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，`[generated, not original text]` 标注与缺口说明照实保留。\n",
        "> 核心素材：古源尊者 2026 年《破妄显真》系列 21 讲（录音转写＋课件），依《导论义注》三十八种修道自欺。\n",
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
