#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_adapt_pkg4w.py —— 为 4周版资料包适配资料包级文件（00_主持人总指南 / README / 原文全集 / CHANGELOG）
规则：①周数措辞替换；②六环节串→九环节串；③8行「周表」重建为4行（原A+B合并）；④流程表换九环节；⑤加4周版说明。
用法: python3 _adapt_pkg4w.py <NN>
"""
import os, re, sys, glob, json, datetime, shutil
from datetime import timezone, timedelta
CST = timezone(timedelta(hours=8))
BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC_ROOT = os.path.join(BASE, "交付成果/第二轮修订版")
OUT_ROOT = os.path.join(BASE, "交付成果/第三轮修订版/第三轮4周版")
CFG = json.load(open(os.path.join(BASE, "_thirdround_titles.json"), encoding="utf-8"))

SIX = "静心10／共读25／分享20／讨论35／禅修15／收尾15"
NINE = "静心10／共读1 20／分享1 10／讨论1 10／禅修15／共读2 20／分享2 10／讨论2 10／收尾15"
NINE_FULL = "静心开场10／共读原文1 20／第一轮分享10／第一轮主题讨论10／禅修练习15／共读原文2 20／第二轮分享10／第二轮主题讨论10／收尾与回向15"

FLOW9 = """| 环节 | 时长 | 内容 |
|:-----|:----:|:-----|
| 🧘 静心开场 | 10 min | 静坐1分钟＋破冰暖场＋心理安全三约定（保密／不评判／可随时暂停） |
| 📖 共读原文1 | 20 min | 原A周共读材料，轮流朗读；★核心必读／◈扩展可选 |
| 💬 第一轮分享 | 10 min | 每人说一句"最触动我的话"，只说不评论 |
| 🎯 第一轮主题讨论 | 10 min | 分层次引导问题（现象—影响—应对）开放式讨论 |
| 🧘 禅修练习 | 15 min | 照读本讲引导词（两段原周次引导词，时间紧取其一） |
| 📖 共读原文2 | 20 min | 原B周共读材料，轮流朗读 |
| 💬 第二轮分享 | 10 min | 每人说一句"最触动我的话" |
| 🎯 第二轮主题讨论 | 10 min | 分层次引导问题开放式讨论 |
| 🔚 收尾与回向 | 15 min | 一句话收获→下周预告→作业→回向文（四句） |"""

def wk_hdr_row(first, titles):
    """把 first = '第1周'／'1' 之类重写为 第k周（原A+B）"""
    pass

def merge_table_rows(rows, titles):
    """rows: 8 行（list of list[str]，不含表头）；合并 (0,1)(2,3)(4,5)(6,7)"""
    out = []
    for k in range(4):
        a, b = rows[2*k], rows[2*k+1]
        new = []
        for i in range(max(len(a), len(b))):
            ca = a[i] if i < len(a) else ""
            cb = b[i] if i < len(b) else ""
            if i == 0:
                new.append(f"第{k+1}周（{titles[k]}）")
            else:
                if ca.strip() and cb.strip() and ca.strip() != cb.strip():
                    new.append(ca.strip() + "　｜　" + cb.strip())
                else:
                    new.append(ca.strip() or cb.strip())
        out.append(new)
    return out

def find_week_tables(text):
    """定位以 | 1 | … | 8 | 的周表；返回 (start_line_idx, end_line_idx_exclusive, rows)"""
    lines = text.split("\n")
    res = []
    i = 0
    while i < len(lines):
        m = re.match(r"^\|\s*(\d+)\s*\|", lines[i])
        if m and m.group(1) == "1":
            # 收集连续行 | 1 |..| 8 |
            j = i
            rows = []
            while j < len(lines) and re.match(r"^\|\s*\d+\s*\|", lines[j]):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            if len(rows) == 8:
                res.append((i, j, rows))
            i = j
        else:
            i += 1
    return res

def rebuild_tables(text, titles):
    lines = text.split("\n")
    tabs = find_week_tables(text)
    for start, end, rows in reversed(tabs):
        newrows = merge_table_rows(rows, titles)
        block = ["| " + " | ".join(r) + " |" for r in newrows]
        lines[start:end] = block
    return "\n".join(lines)

def replace_flow_table(text, titles):
    # 六环节流程表：| 环节 | 时长 | 内容 | 之后 6 行
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if re.match(r"^\|\s*环节\s*\|\s*时长\s*\|", l.strip()) and "内容" in l:
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            # 仅当紧随 6 数据行（静心/共读/分享/讨论/禅修/收尾）才替换
            body = "\n".join(lines[i:j])
            if "静心开场" in body and "收尾" in body and "共读原文2" not in body:
                lines[i:j] = FLOW9.split("\n")
                break
    return "\n".join(lines)

def replace_structure_table(text, titles):
    """README 的资料包结构表（| 文件名 | 用途 |）→ 4周版"""
    lines = text.split("\n")
    new_rows = ["| 文件名 | 用途 |", "|:-----|:-----|",
                "| 📌 **00_主持人总指南.md** | 先读这份！主持人角色定位、120分钟九环节流程、10条守则、四周主线一览、共读材料读法、心理安全要点索引、跨系列边界、FAQ |",
                "| 📖 **原文全集.md** | ⭐ **全部共读原文的完整文字**（按周编排，每块标注出处 media_id 与打开方式） |",
                "| 📝 **更新日志_CHANGELOG.md** | 全部更新历史记录 |",
                "| 📄 **README_资料包说明.md** | 本文件：结构清单、使用方法、系列定位、查重与出处声明 |"]
    for k in range(1, 5):
        t = titles[k-1]
        new_rows.append(f"| 📅 第{k}周_{t}_主持人版.md | 第{k}周主持人用（含速览／时间弹性指南／特别提醒；原第{2*k-1}＋{2*k}周合并） |")
        new_rows.append(f"| 📅 第{k}周_{t}_学员版.md | 第{k}周学员用（共读内容与主持人版完全一致，末尾附延伸阅读） |")
    for i, l in enumerate(lines):
        if l.strip().startswith("| 文件名") and "用途" in l:
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            lines[i:j] = new_rows
            break
    return "\n".join(lines)

def adapt(NN):
    cfg = CFG[str(NN)]
    titles = cfg["t4"]
    srcdir = glob.glob(os.path.join(SRC_ROOT, f"读书会{NN:02d}_*_8周资料包（第二版修订）"))[0]
    outdir = os.path.join(OUT_ROOT, f"读书会{NN:02d}_{cfg['name']}_4周资料包（第三版修订）")
    ts = datetime.datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    # 复制非周文档（原文全集 / 编者语 / 图片等）
    for f in glob.glob(os.path.join(srcdir, "*")):
        bn = os.path.basename(f)
        if re.search(r"第\d+周", bn):
            continue
        if bn in ("00_主持人总指南.md", "README_资料包说明.md", "更新日志_CHANGELOG.md"):
            continue
        shutil.copy2(f, os.path.join(outdir, bn))
    # ---- 00_主持人总指南 ----
    src = open(os.path.join(srcdir, "00_主持人总指南.md"), encoding="utf-8").read()
    t = src
    t = t.replace(f"六环节120分钟口径（{SIX}）", f"九环节120分钟口径（{NINE}）")
    t = re.sub(r"共8周", "共4周", t)
    t = re.sub(r"八周", "四周", t)
    t = t.replace("（共20份文档）", "（共12份文档）")
    t = t.replace("六环节", "九环节")
    t = t.replace("8周资料包", "4周资料包")
    t = t.replace("（静心10／共读25／分享20／讨论35／禅修15／收尾15）", f"（{NINE}）")
    t = t.replace(SIX, NINE)
    t = t.replace("120分钟标准流程（每周相同）", "120分钟标准流程（新9环节·每周相同）")
    t = replace_flow_table(t, titles)
    t = rebuild_tables(t, titles)
    head = f'<div align="right">📅 最近更新：{ts}　|　第三轮4周版（连续两周合并）：由8周版按原1+2／3+4／5+6／7+8周合并为4周；共读原文逐字未改</div>\n\n'
    t = t.split("\n", 1)[1] if t.startswith("<div") else t
    t = head + t
    open(os.path.join(outdir, "00_主持人总指南.md"), "w", encoding="utf-8").write(t)
    # ---- README ----
    src = open(os.path.join(srcdir, "README_资料包说明.md"), encoding="utf-8").read()
    t = src
    t = t.replace(f"六环节120分钟口径（{SIX}）", f"九环节120分钟口径（{NINE}）")
    t = re.sub(r"共8周", "共4周", t)
    t = re.sub(r"八周", "四周", t)
    t = t.replace("（共20份文档）", "（共12份文档）")
    t = t.replace("六环节", "九环节")
    t = t.replace("8周资料包", "4周资料包")
    t = t.replace("（静心10／共读25／分享20／讨论35／禅修15／收尾15）", f"（{NINE}）")
    t = t.replace(SIX, NINE)
    t = t.replace("读书会8周资料包", "读书会4周资料包")
    t = t.replace("120分钟六环节", "120分钟九环节")
    t = t.replace("按120分钟六环节推进（静心开场10′→共读原文30′→第一轮分享25′→主题讨论35′→禅修练习15′→收尾回向20′）",
                  f"按120分钟九环节推进（{NINE_FULL}）；每周由连续两周合并，含两段共读、两轮分享与两轮讨论")
    t = replace_structure_table(t, titles)
    t = rebuild_tables(t, titles)
    head = f'<div align="right">📅 最近更新：{ts}　|　第三轮4周版（连续两周合并；9环节120min；共读原文逐字未改）</div>\n\n'
    t = t.split("\n", 1)[1] if t.startswith("<div") else t
    t = head + t
    open(os.path.join(outdir, "README_资料包说明.md"), "w", encoding="utf-8").write(t)
    # ---- CHANGELOG ----
    cl = f"""<div align="right">📅 最近更新：{ts}　|　第三轮4周版改制</div>

# 📝 更新日志 · CHANGELOG（读书会{NN:02d} · {cfg['name']} · 4周版）

| 时间 | 版本 / 更新内容 |
|:-----|:--------------|
| {ts} | **第三轮4周版初建（v3.0）**：基于 `交付成果/第二轮修订版/读书会{NN:02d}_{cfg['name']}_8周资料包（第二版修订）`，按"连续两周合并"（第1+2、3+4、5+6、7+8周）重组为4周版；单周6环节改为9环节（{NINE}）；**共读原文逐字保留、未改动**；学员版由8周学员版源合并保留既有清理规则。 |

> 说明：本 CHANGELOG 仅记录第三轮4周版；第二版修订（v2.x）历史见 `交付成果/第二轮修订版/` 对应说明文件，原始第一版（v1.0）见 `交付成果/第一轮初稿/`。
"""
    open(os.path.join(outdir, "更新日志_CHANGELOG.md"), "w", encoding="utf-8").write(cl)
    print(f"✅ 适配完成 → {outdir}")
    return 0

if __name__ == "__main__":
    sys.exit(adapt(int(sys.argv[1])))
