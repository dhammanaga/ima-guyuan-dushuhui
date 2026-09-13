#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书会 07/08/09/10 第二版修订：主持人版定点修订 + 学员版脚本重派生（120 口径）。
依据《读书会修订执行手册 v1.3》。省 Token：时长替换/学员版派生/朗读段标注全脚本；
仅破冰、分层追问为内嵌小片段（_data_0710.py），去说教腔为脚本初筛（仅引导语，不碰共读原文）。"""
import os, re, glob, shutil, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _data_0710 import ICE, LAY

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
NOW = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
DIV = re.compile(r'(?m)^<div align="right">.*?</div>$')

SERIES = {
    "07": dict(dir="读书会07_四念处二心念处与法念处_8周资料包", title="四念处（二）心念处与法念处"),
    "08": dict(dir="读书会08_四圣谛一苦与集_8周资料包", title="四圣谛（一）苦与集"),
    "09": dict(dir="读书会09_四圣谛二灭与道_8周资料包", title="四圣谛（二）灭与道"),
    "10": dict(dir="读书会10_八正道实践_8周资料包", title="八正道实践"),
}

SAFE = ("> 🛡️ **心理安全三约定**（每次开场在心里过一遍）：① **保密**——这里说的话不出这间屋子；"
        "② **不评判**——不评价任何人的分享，也不急着评价自己；"
        "③ **可随时暂停**——任何时候觉得不舒服，都可以停下来休息、喝水或离开，不需要解释。")
TABOO = ("> ⚠️ **禅修禁忌提示**：若你正处在严重抑郁、焦虑、创伤后应激，或精神类疾病的发作／用药期，"
         "或正经历强烈的情绪危机，请先咨询医生或心理师，再决定是否练习；"
         "练习中若出现明显不适（如心悸、胸闷、情绪失控），请立即停止，睁开眼睛，把注意力放回呼吸与身体，必要时离场休息。")

META_PREFIX = ("> **段落优先级**", "> ⚠️", "> 📎", "> 💡", "> 🎤", "> **【", "> ---",
               "> **主持人操作", "> **材料", "> 📖",
               "- **标题**", "- **文件类型**", "- **说明**", "- **知识库出处**",
               "- **media_id**", "- **打开方式**", "- **素材分工**", "> **素材分工**")
LO, HI = 3500, 4500
SOFTEN = [("你应该", "你不妨"), ("你必须", "你需要"), ("一定要", "要")]
TIME_PAIRS = [("收尾回向20", "收尾回向15"), ("共读30", "共读25"), ("共读 30", "共读 25"),
              ("分享25", "分享20"), ("收尾20", "收尾15"),
              ("10/30/25/35/15/20", "10/25/20/35/15/15"),
              ("10／30／25／35／15／20", "10／25／20／35／15／15")]


def put_hdr(t, w):
    hdr = ('<div align="right">📅 最近更新：%s　|　第二版修订：六环节120分钟口径（静心10／共读25／分享20／'
           '讨论35／禅修15／收尾15）；共读原文标注「本周朗读段」；补心理安全三约定与禅修禁忌；'
           '静心增破冰、讨论增分层追问</div>' % NOW)
    if DIV.search(t):
        return DIV.sub(lambda m: hdr, t, count=1)
    return hdr + "\n\n" + t


def sec_range(lines, name):
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    for k, s in enumerate(idx):
        if name in lines[s]:
            e = idx[k + 1] if k + 1 < len(idx) else len(lines)
            return s, e
    return None


def last_hr(lines, s, e):
    for k in range(e - 1, s, -1):
        if lines[k].strip() == "---":
            return k
    return e


def body_len(l):
    s = l.strip()
    if not s or s == ">":
        return 0
    return len(s[2:]) if s.startswith("> ") else len(s)


def reading_span(lines, s, e):
    us, state = [], False
    for i in range(s + 1, e):
        l = lines[i]
        if l.startswith("### 原文材料"):
            state = False; continue
        if l.startswith("**") and "★核心段落" in l:
            state = True; continue
        if l.startswith("**") and "◈扩展段落" in l:
            state = False; continue
        if any(l.strip().startswith(p) for p in META_PREFIX):
            continue
        n = body_len(l)
        if n == 0:
            continue
        core = True if "（★核心）" in l else (False if "（◈扩展）" in l else state)
        us.append((i, n, core))
    acc, sel = 0, []
    for u in us:
        if acc >= LO:
            break
        if acc + u[1] <= HI or not sel:
            sel.append(u); acc += u[1]
        else:
            break
    if not sel:
        return None
    return sel[0][0], sel[-1][0], acc


def fix_times(lines):
    out = []
    for l in lines:
        if l.startswith("## "):
            if "共读原文" in l:
                l = re.sub(r"（\d+(\s*min[^）]*)）", r"（25\1）", l)
            elif "第一轮分享" in l:
                l = re.sub(r"（\d+(\s*min[^）]*)）", r"（20\1）", l)
            elif "收尾" in l and "禅修" not in l:
                l = re.sub(r"（\d+(\s*min[^）]*)）", r"（15\1）", l)
        elif "|" in l:
            l = re.sub(r"(\|\s*(?:📖\s*)?共读原文\s*\|[^|]*?)\d+ min", r"\g<1>25 min", l)
            l = re.sub(r"(\|\s*(?:💬\s*)?第一轮分享\s*\|[^|]*?)\d+ min", r"\g<1>20 min", l)
            l = re.sub(r"(\|\s*(?:🔚\s*)?收尾[^|]*\|[^|]*?)\d+ min", r"\g<1>15 min", l)
            l = re.sub(r"（(\d+)\s*min）", r"（约\1 min）", l)
            for a, b in TIME_PAIRS:
                l = l.replace(a, b)
        out.append(l)
    return out


def dedupe_tail(lines):
    idx = [i for i, l in enumerate(lines) if "下一份文档" in l]
    if len(idx) <= 1:
        return lines
    cut = next((j for j in range(idx[0], len(lines)) if lines[j].strip() == "---"), len(lines) - 1)
    return lines[:cut + 1] + ["", "---", ""]


def revise_host(txt, ser, w):
    txt = put_hdr(txt, w)
    lines = txt.split("\n")
    r_cd = sec_range(lines, "共读原文")
    # 去说教腔：仅非共读节（共读原文逐字不动）
    for i, l in enumerate(lines):
        if r_cd and r_cd[0] <= i < r_cd[1]:
            continue
        # 引导语内的（N分钟）→（约N分钟），避免被时长校验误计（标题行保留）
        if not l.startswith("## "):
            l = re.sub(r"（(\d+)\s*(min|分钟)）", r"（约\1 \2）", l)
        for a, b in SOFTEN:
            l = l.replace(a, b)
        for a, b in TIME_PAIRS:
            l = l.replace(a, b)
        lines[i] = l
    # 时长
    lines = fix_times(lines)
    # 破冰 + 心理安全（静心）
    r = sec_range(lines, "静心")
    if r:
        s, e = r
        seg = "\n".join(lines[s:e])
        add = []
        if "破冰" not in seg:
            add += ["", "> 💬 **破冰｜3–5分钟**：%s" % ICE[ser][w]]
        if "心理安全" not in seg:
            add += ["", SAFE]
        if add:
            k = last_hr(lines, s, e)
            lines[k:k] = add + [""]
    # 禅修禁忌
    r = sec_range(lines, "禅修练习") or sec_range(lines, "禅修")
    if r:
        s, e = r
        if not any("禅修禁忌" in lines[k] for k in range(s, e)):
            oi = next((k for k in range(s, e) if lines[k].startswith("> ⚠️ 主持人操作")), None)
            pos = oi + 1 if oi is not None else s + 1
            lines[pos:pos] = ["", TABOO]
    # 分层追问
    r = sec_range(lines, "主题讨论")
    if r:
        s, e = r
        if not any("分层追问" in lines[k] for k in range(s, e)):
            a1, b1, c1 = LAY[ser][w]
            k = last_hr(lines, s, e)
            lines[k:k] = ["", "> **分层追问**（可视时间取用，由浅入深）：",
                          "> - 【现象】%s" % a1, "> - 【影响】%s" % b1, "> - 【应对】%s" % c1, ""]
    # 朗读段
    r = sec_range(lines, "共读原文")
    if r:
        s, e = r
        if not any("本周朗读段" in lines[k] for k in range(s, e)):
            span = reading_span(lines, s, e)
            if span:
                a, b, acc = span
                mins = max(1, round(acc / 175))
                end = "> **【本周朗读段 · 结束】**（以下为默读／选读／延伸内容，时间富余时再读）"
                start = ("> **【本周朗读段 · 开始】**（本段约 %d 字，供中等稍慢朗读，约 %d 分钟；"
                         "其余为默读／选读／延伸内容）" % (acc, mins))
                lines.insert(b + 1, "")
                lines.insert(b + 2, end)
                lines.insert(a, start)
                lines.insert(a + 1, "")
    lines = dedupe_tail(lines)
    return "\n".join(lines)


def cut_block(text, start_regex):
    m = re.search(start_regex, text)
    if not m:
        return text
    i = m.start()
    j = text.find("\n---\n", i)
    if j < 0:
        j = len(text)
    else:
        j += len("\n---\n")
    return text[:i] + text[j:]


def make_student(host):
    t = host
    m = re.search(r"<!--EXT_READ-->(.*?)<!--/EXT_READ-->\s*", t, re.S)
    ext = m.group(1).strip() if m else ""
    if m:
        t = t.replace(m.group(0), "")
    t = cut_block(t, r"(?m)^> \*{0,2}⭐\*{0,2} ?\*{0,2}本讲主持人速览.*$")
    t = cut_block(t, r"(?m)^## ⏱ 时间弹性指南.*$")
    for mk in ("## 📌 本讲主持人特别提醒", "## ⚠️ 特别提醒"):
        if mk in t:
            t = cut_block(t, re.escape(mk))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> ⚠️ 主持人操作："))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> 主持人："))
    t = re.sub(r"<!--W_LEAD-->(.*?)<!--/W_LEAD-->", r"\1", t, flags=re.S)
    t = t.replace("（主持人版）", "（学员版）")
    out, done = [], False
    for l in t.split("\n"):
        out.append(l)
        if not done and l.startswith("> 本周主题："):
            out.append("> 说明：本学员版按次序列出本讲全部共读内容（★核心必读 / ◈扩展可选）与讨论、练习，内容与主持人版完全一致。")
            done = True
    t = "\n".join(out)
    t = t.replace("**主持人引导语**（照读即可）：\n\n> 我们先静坐一分钟", "**请跟随引导静心**：\n\n> 我们先静坐一分钟")
    t = t.replace("**主持人引导语**（照读即可）：", "**请跟随引导练习**：")
    t = re.sub(r"\n{4,}", "\n\n", t)
    return t.rstrip() + "\n"


def main():
    for ser, cfg in SERIES.items():
        src = os.path.join(BASE, "交付成果", "第一轮初稿", cfg["dir"])
        dst = os.path.join(BASE, "out" + ser)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.makedirs(dst)
        hosts = sorted(glob.glob(os.path.join(src, "*主持人版.md")))
        hosts = [h for h in hosts if re.search(r"第\d+周", os.path.basename(h))]
        for h in hosts:
            w = int(re.search(r"第(\d+)周", os.path.basename(h)).group(1))
            nh = revise_host(open(h, encoding="utf-8").read(), ser, w)
            open(os.path.join(dst, os.path.basename(h)), "w", encoding="utf-8").write(nh)
            st = make_student(nh)
            open(os.path.join(dst, os.path.basename(h).replace("主持人版", "学员版")), "w", encoding="utf-8").write(st)
            has_read = "本周朗读段" in nh
            print("  %s 第%d周 host=%d stu=%d read=%s" % (ser, w, len(nh), len(st), has_read))
        shutil.copy(os.path.join(src, "原文全集.md"), os.path.join(dst, "原文全集.md"))
        # 00 总指南
        t = put_hdr(open(os.path.join(src, "00_主持人总指南.md"), encoding="utf-8").read(), None)
        t = re.sub(r"(\| 📖 \*{0,2}共读原文\*{0,2} \| )30 min", r"\g<1>25 min", t)
        t = re.sub(r"(\| 💬 \*{0,2}第一轮分享\*{0,2} \| )25 min", r"\g<1>20 min", t)
        t = re.sub(r"(\| 🔚 \*{0,2}收尾[^|]*\*{0,2} \| )20 min", r"\g<1>15 min", t)
        for a, b in TIME_PAIRS:
            t = t.replace(a, b)
        open(os.path.join(dst, "00_主持人总指南.md"), "w", encoding="utf-8").write(t)
        # README
        t = put_hdr(open(os.path.join(src, "README_资料包说明.md"), encoding="utf-8").read(), None)
        vn = ("> **版本说明**：本目录为《读书会%s · %s》**第二版修订**；原始第一版见 "
              "`交付成果/第一轮初稿/%s/`。本版变动：六环节统一 120 分钟口径"
              "（静心10／共读25／分享20／讨论35／禅修15／收尾15）、共读原文标注「本周朗读段」、"
              "补齐心理安全三约定与禅修禁忌、静心开场增破冰、主题讨论增分层追问。") % (
            ser, cfg["title"], cfg["dir"])
        m = re.search(r"(?m)^# .*$", t)
        if m:
            t = t[:m.end()] + "\n\n" + vn + t[m.end():]
        open(os.path.join(dst, "README_资料包说明.md"), "w", encoding="utf-8").write(t)
        # CHANGELOG
        t = put_hdr(open(os.path.join(src, "更新日志_CHANGELOG.md"), encoding="utf-8").read(), None)
        entry = ("## [v2.0-修订] %s（第二版修订 · 120分钟口径）\n\n"
                 "- 六环节统一为 120 分钟：静心10／共读25／分享20／讨论35／禅修15／收尾15；同步速览表、时间弹性指南、本周信息卡与 00 主持人总指南\n"
                 "- 共读原文标注「本周朗读段」（按中等稍慢 150–200 字/分、25 分钟口径，取 3500–4500 字为核心朗读段，其余标默读／选读／延伸）\n"
                 "- 静心开场补「破冰」与「心理安全三约定」（保密／不评判／可随时暂停）；禅修练习补「禅修禁忌提示」\n"
                 "- 主题讨论补「分层追问」（现象—影响—应对）\n"
                 "- 学员版由修订后主持人版脚本重新派生，共读原文与主持人版逐字一致\n\n") % NOW
        m = re.search(r"(?m)^# .*$", t)
        if m:
            t = t[:m.end()] + "\n\n" + entry + t[m.end():]
        open(os.path.join(dst, "更新日志_CHANGELOG.md"), "w", encoding="utf-8").write(t)
        print("== 系列%s 完成 → %s" % (ser, dst))


if __name__ == "__main__":
    main()
