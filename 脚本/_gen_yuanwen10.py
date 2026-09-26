#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen10.py — 读书会10 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen10.py
"""
import os, re, glob, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会10素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会10_八正道实践_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "中道——八正道的总纲", 2: "正见——修行的眼睛", 3: "正思维——心的转向",
    4: "戒学三支的实践", 5: "正精进——四正勤的实践",
    6: "正念——四念处的生活应用与四种正知", 7: "正定——从近行定到安止定",
    8: "十二道分与八正道在生活中的实践路径",
}

def main():
    parts = [
        "# 📖 读书会10《八正道实践》原文全集\n",
        f"\n> 📅 最近更新：{datetime.date.today():%Y-%m-%d}　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，`[generated, not original text]` 标注与缺口说明照实保留。\n",
        "> 打开方式：ima 知识库「古源尊者开示及上座部佛教资料」搜索材料标题；media_id 均为完整串。\n",
    ]
    total = 0
    for path in SRC:
        w = int(re.search(r"第(\d+)周", path).group(1))
        t = open(path, encoding="utf-8").read()
        # 以 "## 材料" 为界切分，首块为文件头（保留出处说明）
        blocks = re.split(r"^(?=## 材料)", t, flags=re.M)
        header = blocks[0].strip()
        parts.append(f"\n\n---\n\n# 第{w}周　{WEEK_TITLE[w]}\n")
        m = re.search(r"^# .*$", header, flags=re.M)
        parts.append(f"\n> 照录底本：{os.path.basename(path)}（fetch 逐字照录，含缺口注记）\n")
        n = 0
        for b in blocks[1:]:
            b = b.strip()
            if not b:
                continue
            n += 1
            parts.append(f"\n{b}\n")
            total += 1
        # 统计并回写每周块数
        print(f"第{w}周: {n} 块材料")
    out = "".join(parts)
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"\n合计 {total} 块材料 → {OUT}（{len(out):,} 字符）")

if __name__ == "__main__":
    main()
