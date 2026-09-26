#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_mk4w.py —— 第三轮 · 4周版改制（连续两周合并）
对齐读书会02–12他机范式：lean 头部、练习一/二、收尾一/二、无「（原第X周）」、学员版保留（N min）、特别提醒置文末。
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
    ("特别",   lambda t: t.startswith("📌 本讲主持人特别提醒") or t == "### 本讲主持人特别提醒" or t.startswith("本讲主持人特别提醒")),
    ("延伸",   lambda t: t.startswith("📖 延伸阅读") or t.startswith("📚 延伸阅读")),
]
CONTENT_KEYS = {"静心", "共读", "分享", "讨论", "禅修", "扩展", "收尾", "特别", "延伸"}

def classify(title):
    for k, f in CORE:
        if f(title):
            return k
    return None

def parse(text):
    lines = text.split("\n")
    n = len(lines)
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    header = "\n".join(lines[:idx[0]]) if idx else text
    meta = [{"i": i, "title": lines[i][3:].strip(), "key": classify(lines[i][3:].strip())} for i in idx]
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

def title_of(body): return body.split("\n", 1)[0][3:].strip()
def body_of(body):
    parts = body.split("\n", 1)
    return parts[1].strip("\n") if len(parts) > 1 else ""

def collect(meta):
    d, misc, order = {}, {}, []
    core_starts = [m["i"] for m in meta if m["key"] in CONTENT_KEYS]
    first_core = min(core_starts) if core_starts else 10 ** 9
    for m in meta:
        if m["key"] in CONTENT_KEYS:
            d.setdefault(m["key"], []).append(m["body"])
        elif m["key"] is None and m["i"] < first_core:
            t = title_of(m["body"])
            if t not in misc:
                misc[t] = []
                order.append(t)
            misc[t].append(body_of(m["body"]))
    return d, misc, order

def extract_theme(header):
    for l in header.split("\n"):
        s = l.lstrip("> ").strip()
        if s.startswith("本周主题："):
            return s[len("本周主题："):].strip().replace("**", "")
    return ""

def parse_info(meta):
    for m in meta:
        if m["key"] == "信息卡":
            d = {}
            for l in body_of(m["body"]).split("\n"):
                mm = re.match(r"^- \*\*(.+?)\*\*：(.+)$", l.strip())
                if mm:
                    d[mm.group(1)] = mm.group(2).strip()
            return d
    return {}

def pick_info(d, keys):
    for kk in d:
        for k in keys:
            if k in kk:
                return d[kk]
    return ""

SPEED = """> ⭐ **本讲主持人速览**（新主持人必读，2分钟看完）
>
> 你不是老师，是"共学同行者"。你不需要提前懂内容，只需要按流程走。
> **本周由连续两周内容合并**而成，含两段共读、两轮分享与两轮讨论，单讲 120 分钟。
>
> | 环节 | 标准时长 | ⏱ 时间不够→ | ⏱ 时间富余→ |
> |:-----|:----:|:-----|:-----|
> | 🧘 静心开场 | 10 min | 缩至5 min | 加2分钟静坐 |
> | 📖 共读原文1 | 20 min | 只读★核心段（约15 min） | 加读◈扩展段 |
> | 💬 第一轮分享 | 10 min | 每人1句话 | 每人3分钟 |
> | 🎯 第一轮主题讨论 | 10 min | 只讨论问题① | 讨论全部问题+扩展 |
> | 🧘 禅修练习 | 15 min | 缩至8 min（只念引导词前半） | 延长至20 min |
> | 📖 共读原文2 | 20 min | 只读★核心段 | 加读◈扩展段 |
> | 💬 第二轮分享 | 10 min | 每人1句话 | 每人3分钟 |
> | 🎯 第二轮主题讨论 | 10 min | 只讨论问题① | 讨论全部问题+扩展 |
> | 🔚 收尾与回向 | 15 min | 缩至10 min | 保持 |
>
> **主持人10条守则（精简版）**：
> ① 不讲解、不提供答案——让原文自己说话；② 有人问"正确答案"→说"先听听大家的看法"；③ 冷场→主持人先分享自己的真实感受；④ 跑题→温和拉回："这个有意思，我们回到今天的原文"；⑤ 争论→"两种看法都很好，大家保留自己的理解"；⑥ 确保人人发言；⑦ 不评判任何人的分享；⑧ 时间到了就推进；⑨ 禅修练习照读引导词即可；⑩ 结束一起回向。"""

GUIDE = """## ⏱ 时间弹性指南（本讲通用）

| 情况 | 应对方法 |
|:-----|:---------|
| **时间不够**（共读太长／讨论超时） | ① 静心开场缩至5分钟；② 两段共读原文均只读标注 **★核心** 的段落；③ 两轮分享每人只说一句话；④ 两轮主题讨论只讨论各自的问题①；⑤ 禅修练习缩至8分钟（只念引导词前半段）；⑥ 收尾回向缩至10分钟 |
| **时间富余**（共读快／讨论提前结束） | ① 用"📚 扩展内容包"中的补充原文段落继续共读；② 增加扩展讨论问题；③ 延长禅修练习时间；④ 增加"每人分享一个生活实例"环节 |

> 💡 原则：**讨论比读完重要，体验比讲完重要。** 宁可跳过扩展原文，也要让每个人都有机会说话。"""

LABELS = {"禅修": ["练习一", "练习二"], "扩展": ["扩展一", "扩展二"], "收尾": ["收尾一", "收尾二"]}

def merge(nn, name, k, srcA, srcB, version):
    hA, mA = parse(srcA); hB, mB = parse(srcB)
    dA, miscA, ordA = collect(mA); dB, miscB, ordB = collect(mB)
    infoA, infoB = parse_info(mA), parse_info(mB)
    ts = datetime.datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    out = []
    if version == "host":
        out.append(f'<div align="right">📅 最近更新：{ts}　|　第三版修订（4周版）：连续两周合并为9环节、单讲120分钟；共读原文一字未改；学员版去除主持人专属内容</div>')
    else:
        out.append(f'<div align="right">📅 最近更新：{ts}　|　学员版（第三版修订 · 4周版）</div>')
    out.append("")
    out.append(f"# 第{k}周：{CFG[str(nn)]['t4'][k-1]}（{'主持人版' if version=='host' else '学员版'}）")
    out.append("")
    if version == "host":
        out.append(SPEED)
        out.append("")
        out.append(f"> **读书会{nn}：{name} · 第{k}周（4周版 · 连续两周合并）**")
        out.append("> 主持人：你不需要提前懂内容，按本手册推进即可。")
        thA, thB = extract_theme(hA), extract_theme(hB)
        out.append(f"> 本周主题：**{thA}**；**{thB}**。")
        out.append("")
    # 信息卡
    out.append("## 📋 本周信息卡")
    out.append("")
    out.append("| 项目 | 内容 |")
    out.append("|:----|:-----|")
    out.append("| 时长 | 120分钟（4周版 · 9环节） |")
    out.append(f"| 核心问题 | {pick_info(infoA,['核心问题'])}；{pick_info(infoB,['核心问题'])} |")
    out.append(f"| 共读原文 | 共读原文1：{pick_info(infoA,['共读原文提要','共读提要','共读原文'])}　｜　共读原文2：{pick_info(infoB,['共读原文提要','共读提要','共读原文'])} |")
    out.append(f"| 本周作业 | {pick_info(infoA,['本周作业','作业'])}；{pick_info(infoB,['本周作业','作业'])} |")
    out.append("")
    if version == "host":
        out.append(GUIDE)
        out.append("")
    # 前置加强节（按标题合并，A先B后）
    allt = ordA + [t for t in ordB if t not in ordA]
    for t in allt:
        bodies = miscA.get(t, []) + miscB.get(t, [])
        out.append(f"## {t}")
        out.append("")
        out.append("\n\n".join(bodies))
        out.append("")
    def emit(outtitle, bodies, minstr, key):
        if not bodies:
            return
        head = f"## {outtitle}" + (f"（{minstr}）" if minstr else "")
        out.append(head); out.append("")
        labels = LABELS.get(key, [])
        if len(bodies) == 1:
            out.append(body_of(bodies[0][1])); out.append("")
        else:
            for i, (tag, b) in enumerate(bodies):
                if i < len(labels):
                    out.append(f"### {labels[i]}"); out.append("")
                out.append(body_of(b)); out.append("")
    tA, tB = f"原第{2*k-1}周", f"原第{2*k}周"
    def pk(d, key, tag): return [(tag, d[key][0])] if d.get(key) else []
    emit("🧘 静心开场", pk(dA, "静心", tA), "10 min", "静心")
    emit("📖 共读原文1", pk(dA, "共读", tA), "20 min", "共读")
    emit("💬 第一轮分享", pk(dA, "分享", tA), "10 min", "分享")
    emit("🎯 第一轮主题讨论", pk(dA, "讨论", tA), "10 min", "讨论")
    emit("🧘 禅修练习", pk(dA, "禅修", tA) + pk(dB, "禅修", tB), "15 min", "禅修")
    emit("📖 共读原文2", pk(dB, "共读", tB), "20 min", "共读")
    emit("💬 第二轮分享", pk(dB, "分享", tB), "10 min", "分享")
    emit("🎯 第二轮主题讨论", pk(dB, "讨论", tB), "10 min", "讨论")
    emit("📚 扩展内容包（时间富余时使用）", pk(dA, "扩展", tA) + pk(dB, "扩展", tB), "", "扩展")
    emit("🔚 收尾与回向", pk(dA, "收尾", tA) + pk(dB, "收尾", tB), "15 min", "收尾")
    emit("📚 延伸阅读（课后自由选读，均为文字版）", pk(dA, "延伸", tA) + pk(dB, "延伸", tB), "", "延伸")
    if version == "host":
        sp = pk(dA, "特别", tA) + pk(dB, "特别", tB)
        if sp:
            out.append("### 本讲主持人特别提醒"); out.append("")
            out.append("\n\n".join(body_of(b) for _, b in sp)); out.append("")
    return "\n".join(out)

def main():
    nn = int(sys.argv[1]); dry = "--dry" in sys.argv
    cfg = CFG[str(nn)]
    srcdir = glob.glob(os.path.join(SRC_ROOT, f"读书会{nn:02d}_*_8周资料包（第二版修订）"))[0]
    outdir = os.path.join(OUT_ROOT, f"读书会{nn:02d}_{cfg['name']}_4周资料包（第三版修订）")
    if not dry: os.makedirs(outdir, exist_ok=True)
    def rd(pat): return sorted(glob.glob(os.path.join(srcdir, pat)), key=lambda p: int(re.search(r"第(\d+)周", p).group(1)))
    hosts, stus = rd("第*周_*主持人版.md"), rd("第*周_*学员版.md")
    assert len(hosts) == 8 and len(stus) == 8
    for k in range(1, 5):
        A, B = 2*k-1, 2*k
        th = merge(nn, cfg["name"], k, open(hosts[A-1], encoding="utf-8").read(), open(hosts[B-1], encoding="utf-8").read(), "host")
        ts = merge(nn, cfg["name"], k, open(stus[A-1], encoding="utf-8").read(), open(stus[B-1], encoding="utf-8").read(), "student")
        fh = os.path.join(outdir, f"第{k}周_{cfg['t4'][k-1]}_主持人版.md")
        fs = os.path.join(outdir, f"第{k}周_{cfg['t4'][k-1]}_学员版.md")
        if not dry:
            open(fh, "w", encoding="utf-8").write(th); open(fs, "w", encoding="utf-8").write(ts)
        print(f"  W{k}: 主持{len(th):,} / 学员{len(ts):,}")
    print("✅ 4周版文本生成完成" + ("（dry-run）" if dry else " → " + outdir))

if __name__ == "__main__":
    sys.exit(main())
