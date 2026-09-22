#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_mk4w.py —— 第三轮 · 4周版改制（连续两周合并）
8周版资料包（主持人版源 + 学员版源）→ 4周版资料包。
合并：第1周=原1+2，第2周=原3+4，第3周=原5+6，第4周=原7+8。
9 环节：静心10 / 共读1 20 / 分享1 10 / 讨论1 10 / 禅修15 / 共读2 20 / 分享2 10 / 讨论2 10 / 收尾15。
用法: python3 _mk4w.py <NN> [--dry]
"""
import os, re, sys, json, glob, datetime
from datetime import timezone, timedelta

CST = timezone(timedelta(hours=8))
BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
SRC_ROOT = os.path.join(BASE, "交付成果/第二轮修订版")
OUT_ROOT = os.path.join(BASE, "交付成果/第三轮修订版/第三轮4周版")
CFG = json.load(open(os.path.join(BASE, "_thirdround_titles.json"), encoding="utf-8"))

CORE = [
    ("信息卡", lambda t: t == "📋 本周信息卡"),
    ("弹性",   lambda t: "时间弹性指南" in t),
    ("静心",   lambda t: t.startswith("🧘 静心开场")),
    ("共读",   lambda t: t.startswith("📖 共读原文")),
    ("分享",   lambda t: t.startswith("💬") and "分享" in t),
    ("讨论",   lambda t: t.startswith("🎯") and "主题讨论" in t and "追问" not in t),
    ("禅修",   lambda t: t.startswith("🧘 禅修练习")),
    ("扩展",   lambda t: t.startswith("📚 扩展内容包")),
    ("收尾",   lambda t: t.startswith("🔚 收尾与回向")),
    ("特别",   lambda t: t.startswith("📌 本讲主持人特别提醒")),
    ("延伸",   lambda t: t.startswith("📖 延伸阅读")),
]
CONTENT_KEYS = {"静心", "共读", "分享", "讨论", "禅修", "扩展", "收尾", "特别", "延伸"}

def classify(title):
    for k, f in CORE:
        if f(title):
            return k
    return None

def parse(text):
    """返回 (header, [ {i,title,key,body} ])，核心内容节 span 直到下一个核心内容节。"""
    lines = text.split("\n")
    n = len(lines)
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    header = "\n".join(lines[:idx[0]]) if idx else text
    meta = []
    for i in idx:
        title = lines[i][3:].strip()
        meta.append({"i": i, "title": title, "key": classify(title)})
    for a, m in enumerate(meta):
        if m["key"] in CONTENT_KEYS:
            end = n
            for b in range(a + 1, len(meta)):
                if meta[b]["key"] in CONTENT_KEYS:
                    end = meta[b]["i"]; break
        else:
            end = meta[a + 1]["i"] if a + 1 < len(meta) else n
        m["body"] = "\n".join(lines[m["i"]:end])
    return header, meta

def title_of(body):
    return body.split("\n", 1)[0][3:].strip()

def body_of(body):
    parts = body.split("\n", 1)
    return parts[1].strip("\n") if len(parts) > 1 else ""

def collect(meta):
    d, misc = {}, []
    core_starts = [m["i"] for m in meta if m["key"] in CONTENT_KEYS]
    first_core = min(core_starts) if core_starts else (len(meta) and meta[-1]["i"] + 1 or 0)
    for m in meta:
        if m["key"] in CONTENT_KEYS:
            d.setdefault(m["key"], []).append(m["body"])
        elif m["key"] is None and m["i"] < first_core:
            misc.append(m["body"])
    return d, misc

def extract_lead(header):
    lines = header.split("\n")
    start = None
    for i, l in enumerate(lines):
        if re.match(r"^> \*\*读书会\d", l):
            start = i; break
    if start is None:
        return {"prose": [], "theme": "", "guard": []}
    block = []
    for l in lines[start + 1:]:
        if not l.startswith(">"):
            break
        block.append(l)
    prose, theme, guard = [], "", []
    for l in block:
        s = l.lstrip(">").strip()
        if not s or s.startswith("说明："):
            continue
        s = s.replace("八周", "四周").replace("8周", "4周")
        if s.startswith("本周主题："):
            theme = s[len("本周主题："):].strip()
        elif "一句话护心" in s:
            guard.append(s)
        else:
            prose.append(s)
    return {"prose": prose, "theme": theme, "guard": guard}

def parse_info(body):
    d = {}
    for l in body.split("\n"):
        m = re.match(r"^- \*\*(.+?)\*\*：(.+)$", l.strip())
        if m:
            d[m.group(1)] = m.group(2).strip()
    return d

def pick_info(d, keys):
    for kk in d:
        for k in keys:
            if k in kk:
                return d[kk]
    return "—"

SPEED_TABLE = """> ⭐ **本讲主持人速览**（新主持人必读，2分钟看完）
>
> 你不是老师，是"共学同行者"。你不需要懂内容，只需要按流程走。本周由**连续两周内容合并**而成，含两段共读、两轮分享与两轮讨论。
>
> | 环节 | 标准时长 | ⏱ 时间不够→ | ⏱ 时间富余→ |
> |:-----|:----:|:-----|:-----|
> | 🧘 静心开场 | 10 min | 缩至5 min | 加2分钟静坐 |
> | 📖 共读原文1 | 20 min | 只读★核心段 | 加读◈扩展段 |
> | 💬 第一轮分享 | 10 min | 每人1句话 | 每人3分钟 |
> | 🎯 第一轮主题讨论 | 10 min | 只讨论问题① | 讨论全部问题+扩展 |
> | 🧘 禅修练习 | 15 min | 缩至8–10 min | 延长至20 min |
> | 📖 共读原文2 | 20 min | 只读★核心段 | 加读◈扩展段 |
> | 💬 第二轮分享 | 10 min | 每人1句话 | 每人3分钟 |
> | 🎯 第二轮主题讨论 | 10 min | 只讨论问题① | 讨论全部问题+扩展 |
> | 🔚 收尾与回向 | 15 min | 缩至10 min | 保持 |
>
> **主持人10条守则（精简版）**：
> > ① 不讲解、不提供答案——让原文自己说话；② 有人问"正确答案"→说"先听听大家的看法"；③ 冷场→主持人先分享自己的真实感受；④ 跑题→温和拉回："这个有意思，我们回到今天的原文"；⑤ 争论→"两种看法都很好，大家保留自己的理解"；⑥ 确保人人发言；⑦ 不评判任何人的分享；⑧ 时间到了就推进；⑨ 禅修练习照读引导词即可；⑩ 结束一起回向。"""

GUIDE_TABLE = """## ⏱ 时间弹性指南（本讲通用）

> 本讲 120 分钟是硬约束，任何情况下不得改动总时长；下表只帮助你在"某个环节超时／结余"时做即时调整。

| 分段 | 标准 | 若前段超时（收紧） | 若时间富余（放宽） |
|---|---|---|---|
| 静心开场 | 10 | 5 min：只做呼吸＋发愿 | 13 min：加慈心/延伸 |
| 共读原文1 | 20 | 15 min：只读★核心段 | 加读◈扩展段 |
| 第一轮分享 | 10 | 8 min：每人一句话 | 每人2–3分钟 |
| 第一轮主题讨论 | 10 | 只谈问题① | 全谈＋追问 |
| 禅修练习 | 15 | 8–10 min：缩短引导词 | 18 min：加静默 |
| 共读原文2 | 20 | 15 min：只读★核心段 | 加读◈扩展段 |
| 第二轮分享 | 10 | 8 min：每人一句话 | 每人2–3分钟 |
| 第二轮主题讨论 | 10 | 只谈问题① | 全谈＋追问 |
| 收尾与回向 | 15 | 10 min：压缩预告 | 自由补充 |"""

def merge(nn, name, k, srcA, srcB, version):
    hA, mA = parse(srcA)
    hB, mB = parse(srcB)
    dA, miscA = collect(mA)
    dB, miscB = collect(mB)
    leadA, leadB = extract_lead(hA), extract_lead(hB)
    infoA = parse_info(body_of(mA[0]["body"]) if mA else "")
    # 找到信息卡节
    def info_of(meta):
        for m in meta:
            if m["key"] == "信息卡":
                return parse_info(body_of(m["body"]))
        return {}
    infoA, infoB = info_of(mA), info_of(mB)

    out = []
    ts = datetime.datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    out.append(f'<div align="right">📅 最近更新：{ts}　|　第三轮4周版（连续两周合并）：由原第{2*k-1}周＋原第{2*k}周合并；共读原文逐字未改</div>')
    out.append("")
    if "🔴🔴🔴" in (srcA + srcB):
        out.append("> 🔴🔴🔴 **【存疑·未改】** 标记之间的文字＝红方审计判定「存疑、未改」之处，照录原文一字未动，待人工核实修改。")
        out.append("")
    out.append(f"# 第{k}周：{CFG[str(nn)]['t4'][k-1]}（{'主持人版' if version=='host' else '学员版'}）")
    if version == "host":
        out.append(SPEED_TABLE)
    out.append("")
    out.append(f"> **读书会{nn}：{name} · 第{k}周（4周版 · 连续两周合并）**")
    out.append(">")
    for p in leadA["prose"]:
        out.append("> " + p)
    if leadA["prose"] and leadB["prose"]:
        out.append(">")
    for p in leadB["prose"]:
        out.append("> " + p)
    thA, thB = leadA.get("theme", ""), leadB.get("theme", "")
    if thA or thB:
        out.append(">")
        out.append(f"> 本周主题：{thA}（原第{2*k-1}周）；{thB}（原第{2*k}周）")
    if version == "student":
        out.append("> 说明：本学员版按次序列出本讲全部共读内容（★核心必读 / ◈扩展可选）与讨论、练习，内容与主持人版完全一致。")
    out.append("")
    # 信息卡
    out.append("## 📋 本周信息卡")
    out.append("")
    out.append("| 项目 | 内容 |")
    out.append("|:----|:-----|")
    out.append("| 时长 | 约120分钟（设计=2小时，按新流程弹性调控） |")
    out.append(f"| 核心问题 | {pick_info(infoA,['核心问题'])}；{pick_info(infoB,['核心问题'])} |")
    out.append(f"| 共读原文 | 共读原文1（原第{2*k-1}周）：{pick_info(infoA,['共读原文提要','共读提要','共读原文'])}　｜　共读原文2（原第{2*k}周）：{pick_info(infoB,['共读原文提要','共读提要','共读原文'])} |")
    out.append(f"| 本周作业 | {pick_info(infoA,['本周作业','作业'])}；{pick_info(infoB,['本周作业','作业'])} |")
    out.append("")
    if version == "host":
        out.append(GUIDE_TABLE)
        out.append("")
    # 前置加强节
    titlesA = [title_of(b) for b in miscA]
    titlesB = [title_of(b) for b in miscB]
    collide = set(titlesA) & set(titlesB)
    for tag, misc in ((f"原第{2*k-1}周", miscA), (f"原第{2*k}周", miscB)):
        for b in misc:
            t = title_of(b)
            suffix = f"（{tag}）" if (version == "host" or t in collide) else ""
            out.append(f"## {t}{suffix}")
            out.append("")
            out.append(body_of(b))
            out.append("")
    # 9 环节
    def emit(outtitle, bodies, minstr, subj):
        if not bodies:
            return
        out.append(f"## {outtitle}{('（'+minstr+'）') if (version=='host' and minstr) else ''}")
        out.append("")
        if len(bodies) > 1:
            for tag, b in bodies:
                if version == "host":
                    out.append(f"### {subj}（{tag}）")
                    out.append("")
                out.append(body_of(b))
                out.append("")
        else:
            out.append(body_of(bodies[0][1]))
            out.append("")
    tA, tB = f"原第{2*k-1}周", f"原第{2*k}周"
    def pk(d, key, tag):
        return [(tag, d[key][0])] if d.get(key) else []
    emit("🧘 静心开场", pk(dA, "静心", tA), "10 min", "静心开场")
    emit("📖 共读原文1", pk(dA, "共读", tA), "20 min", "共读原文1")
    emit("💬 第一轮分享", pk(dA, "分享", tA), "10 min", "第一轮分享")
    emit("🎯 第一轮主题讨论", pk(dA, "讨论", tA), "10 min", "第一轮主题讨论")
    emit("🧘 禅修练习", pk(dA, "禅修", tA) + pk(dB, "禅修", tB), "15 min", "禅修练习")
    emit("📖 共读原文2", pk(dB, "共读", tB), "20 min", "共读原文2")
    emit("💬 第二轮分享", pk(dB, "分享", tB), "10 min", "第二轮分享")
    emit("🎯 第二轮主题讨论", pk(dB, "讨论", tB), "10 min", "第二轮主题讨论")
    emit("📚 扩展内容包（时间富余时使用）", pk(dA, "扩展", tA) + pk(dB, "扩展", tB), "", "扩展内容包")
    emit("🔚 收尾与回向", pk(dA, "收尾", tA) + pk(dB, "收尾", tB), "15 min", "收尾回向")
    if version == "host":
        emit("📌 本讲主持人特别提醒", pk(dA, "特别", tA) + pk(dB, "特别", tB), "", "本讲主持人特别提醒")
    emit("📖 延伸阅读", pk(dA, "延伸", tA) + pk(dB, "延伸", tB), "", "延伸阅读")
    if version == "host":
        out.append("## 🗂 更新记录")
        out.append("")
        out.append("| 时间 | 说明 |")
        out.append("|:--|:--|")
        out.append(f"| {datetime.datetime.now(CST):%Y-%m-%d} | 第三轮4周版：由原第{2*k-1}周＋原第{2*k}周合并（9环节120min）；共读原文逐字未改。 |")
    txt = "\n".join(out)
    return txt

def main():
    nn = int(sys.argv[1])
    dry = "--dry" in sys.argv
    cfg = CFG[str(nn)]
    srcdir = glob.glob(os.path.join(SRC_ROOT, f"读书会{nn:02d}_*_8周资料包（第二版修订）"))
    if not srcdir:
        print("❌ 未找到源目录", nn); return 1
    srcdir = srcdir[0]
    outdir = os.path.join(OUT_ROOT, f"读书会{nn:02d}_{cfg['name']}_4周资料包（第三版修订）")
    if not dry:
        os.makedirs(outdir, exist_ok=True)
    def rd(pat):
        return sorted(glob.glob(os.path.join(srcdir, pat)), key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
    hosts, stus = rd("第*周_*主持人版.md"), rd("第*周_*学员版.md")
    assert len(hosts) == 8 and len(stus) == 8, (len(hosts), len(stus))
    for k in range(1, 5):
        A, B = 2*k-1, 2*k
        th = merge(nn, cfg["name"], k, open(hosts[A-1], encoding="utf-8").read(), open(hosts[B-1], encoding="utf-8").read(), "host")
        ts = merge(nn, cfg["name"], k, open(stus[A-1], encoding="utf-8").read(), open(stus[B-1], encoding="utf-8").read(), "student")
        fh = os.path.join(outdir, f"第{k}周_{cfg['t4'][k-1]}_主持人版.md")
        fs = os.path.join(outdir, f"第{k}周_{cfg['t4'][k-1]}_学员版.md")
        if not dry:
            with open(fh, "w", encoding="utf-8") as f: f.write(th)
            with open(fs, "w", encoding="utf-8") as f: f.write(ts)
        print(f"  W{k}: 主持{len(th):,} / 学员{len(ts):,}")
    print("✅ 4周版文本生成完成" + ("（dry-run）" if dry else " → " + outdir))
    return 0

if __name__ == "__main__":
    sys.exit(main())
