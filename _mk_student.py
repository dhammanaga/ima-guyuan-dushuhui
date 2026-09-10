#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_mk_student.py — 由主持人版脚本化生成学员版（通用版，Token优化方案·措施A）
读书会系列通用；体例对齐读书会03/05/06/07。
用法: python3 _mk_student.py <主持人版.md> [输出路径]
  省略输出路径时输出到同目录，文件名"主持人版"→"学员版"。

主持人版需埋的定界标记（HTML注释，不显示）：
  <!--W_LEAD-->主持人导语<!--/W_LEAD-->        学员版中转为纯文本保留
  <!--EXT_READ-->## 📖 延伸阅读…<!--/EXT_READ-->  学员版中挪到文末
脚本自动处理（无需标记）：
  删块: ⭐主持人速览 / ⏱时间弹性指南 / 📌本讲主持人特别提醒（至其后第一个 \n---\n）
  删行: "> ⚠️ 主持人操作：" / "> 主持人：" 开头行
  标题: （主持人版）→（学员版）
  插行: "> 本周主题："行后插学员版说明行
  引导: "**主持人引导语**（照读即可）：" → "**请跟随引导静心**："（静心段）/ "**请跟随引导练习**："（其余）
  收尾: >3 连续空行压缩；文末追加 EXT_READ 内容
生成后建议跑 _qa_check.py 复核双版本一致性（QA_BANNED 指向本系列禁用清单）。
"""
import sys
import re


def cut_block(text, start_marker):
    """删除从 start_marker 所在行开始到其后第一个 '\\n---\\n'（含）的块"""
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


def main(src, dst=None):
    t = open(src, encoding="utf-8").read()
    # 1) 提取 EXT_READ 块
    m = re.search(r"<!--EXT_READ-->(.*?)<!--/EXT_READ-->\s*", t, re.S)
    ext = m.group(1).strip() if m else ""
    t = t.replace(m.group(0), "") if m else t
    # 2) 删主持人专属块
    t = cut_block(t, "> ⭐ **本讲主持人速览**")
    t = cut_block(t, "## ⏱ 时间弹性指南")
    for marker in ("## 📌 本讲主持人特别提醒", "## ⚠️ 特别提醒"):
        if marker in t:
            t = cut_block(t, marker)
    # 3) 删单行
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> ⚠️ 主持人操作："))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> 主持人："))
    # 4) W_LEAD → 纯文本
    t = re.sub(r"<!--W_LEAD-->(.*?)<!--/W_LEAD-->", r"\1", t, flags=re.S)
    # 5) 标题
    t = t.replace("（主持人版）", "（学员版）")
    # 6) "本周主题"行后插说明行（仅学员版）
    lines = t.split("\n")
    out = []
    inserted = False
    for l in lines:
        out.append(l)
        if not inserted and l.startswith("> 本周主题："):
            out.append("> 说明：本学员版按次序列出本讲全部共读内容（★核心必读 / ◈扩展可选）与讨论、练习，内容与主持人版完全一致。")
            inserted = True
    t = "\n".join(out)
    # 7) 引导语标签
    t = t.replace("**主持人引导语**（照读即可）：\n\n> 我们先静坐一分钟",
                  "**请跟随引导静心**：\n\n> 我们先静坐一分钟")
    t = t.replace("**主持人引导语**（照读即可）：", "**请跟随引导练习**：")
    # 8) 清理多余空行
    t = re.sub(r"\n{4,}", "\n\n", t)
    # 9) 末尾追加延伸阅读
    if ext:
        t = t.rstrip() + "\n\n---\n\n" + ext + "\n"
    if not dst:
        dst = src.replace("主持人版", "学员版")
    open(dst, "w", encoding="utf-8").write(t)
    print(f"✅ 学员版已生成: {dst}（{len(t)} 字符）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
