#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_student07.py — 由主持人版生成学员版（读书会07双版本一致性保障）
用法: python3 _mk_student07.py <主持人版.md>
规则（对齐读书会03/05格式）:
  删除: ⭐主持人速览块 / ⏱时间弹性指南节 / ⚠️主持人操作行 / 📌特别提醒节 / EXT_READ块
  替换: 标题(主持人版)→(学员版); 删"> 主持人："行; 引言插入"说明"行; W_LEAD→纯文本行;
        静心开场引导语标签→"请跟随引导静心"; 禅修练习引导语标签→"请跟随引导练习"
  末尾: 追加 EXT_READ 内容（延伸阅读表）
"""
import sys, re

def cut_block(text, start_marker):
    """删除从 start_marker 所在行开始到其后第一个 '\n---\n'（含）的块"""
    i = text.find(start_marker)
    if i < 0:
        print(f"⚠️ 未找到标记: {start_marker[:20]}")
        return text
    j = text.find("\n---\n", i)
    if j < 0:
        j = len(text)
    else:
        j += len("\n---\n")
    return text[:i] + text[j:]

def main(src):
    t = open(src, encoding="utf-8").read()
    # 1) 提取 EXT_READ 块
    m = re.search(r"<!--EXT_READ-->(.*?)<!--/EXT_READ-->\s*", t, re.S)
    ext = m.group(1).strip() if m else ""
    t = t.replace(m.group(0), "") if m else t
    # 2) 删主持人专属块
    t = cut_block(t, "> ⭐ **本讲主持人速览**")
    t = cut_block(t, "## ⏱ 时间弹性指南")
    t = cut_block(t, "## 📌 本讲主持人特别提醒")
    # 3) 删单行
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> ⚠️ 主持人操作："))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> 主持人："))
    # 4) W_LEAD → 纯文本
    t = re.sub(r"<!--W_LEAD-->(.*?)<!--/W_LEAD-->", r"\1", t)
    # 5) 标题与引言
    t = t.replace("（主持人版）", "（学员版）")
    # 在"本周主题"行后插入说明行（仅学员版）
    lines = t.split("\n")
    out = []
    inserted = False
    for l in lines:
        out.append(l)
        if not inserted and l.startswith("> 本周主题："):
            out.append("> 说明：本学员版按次序列出本讲全部共读内容（★核心必读 / ◈扩展可选）与讨论、练习，内容与主持人版完全一致。")
            inserted = True
    t = "\n".join(out)
    # 6) 引导语标签
    t = t.replace("**主持人引导语**（照读即可）：\n\n> 我们先静坐一分钟", "**请跟随引导静心**：\n\n> 我们先静坐一分钟")
    t = t.replace("**主持人引导语**（照读即可）：", "**请跟随引导练习**：")
    # 7) 清理多余空行（>3连续空行→1空行）
    t = re.sub(r"\n{4,}", "\n\n", t)
    # 8) 末尾追加延伸阅读
    if ext:
        t = t.rstrip() + "\n\n---\n\n" + ext + "\n"
    dst = src.replace("主持人版", "学员版")
    open(dst, "w", encoding="utf-8").write(t)
    print(f"✅ 学员版已生成: {dst}")

if __name__ == "__main__":
    main(sys.argv[1])
