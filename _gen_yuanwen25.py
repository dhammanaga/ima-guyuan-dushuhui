#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_gen_yuanwen25.py — 读书会25 原文全集生成（零LLM，脚本化）
从8份素材照录提取全部「## 材料」块，聚合为《原文全集.md》。
用法: python3 _gen_yuanwen25.py
"""
import os, re, glob, datetime

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC = sorted(glob.glob(os.path.join(BASE, "读书会25素材/第*周_素材照录.md")),
             key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
OUT = os.path.join(BASE, "交付成果/读书会25_随念修习全系列（七随念与食厌想）_8周资料包/原文全集.md")

WEEK_TITLE = {
    1: "总论：四十种业处、十随念与四护卫禅",
    2: "佛随念：十号功德与建塔法",
    3: "法随念：六特质与法随法行",
    4: "僧随念：四双八士与三种行道",
    5: "天随念：依圣者五德与四功德",
    6: "死随念：四种死亡与九种利益",
    7: "不净随念与食厌想",
    8: "随念与皈依、四不坏信、从止转观",
}

def main():
    parts = [
        "# 📖 读书会25《随念修习全系列（七随念 + 食厌想）》原文全集\n",
        f"\n> 📅 最近更新：{datetime.date.today():%Y-%m-%d}　|　由8份《第X周_素材照录.md》脚本化聚合生成（零LLM，逐字保真）\n",
        "> 用途：共读原文的单一检索底本；正文逐字取自知识库 fetch 返回，照实保留。\n",
        "> 核心素材：四十种业处与十随念总论（231111大佛禅修营）＋佛随念/法随念/僧随念/天随念/死随念/不净随念/食厌想专讲（古源尊者，2023–2025）＋三皈依与止观前行。\n",
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
