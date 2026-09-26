#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书会02 第二版修订：主持人版定点修订 + 学员版脚本重派生。"""
import os, re, glob, shutil
from datetime import datetime, timezone, timedelta

SRC, DST = "pkg02", "out02"
NOW = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
DIV = re.compile(r"(?m)^<div align=\"right\">.*?</div>$")

ICE = {
 1: "这周里，有没有哪件小事让你心里有点紧、想放下的？（一句话，说完就放下）",
 2: "这周，你对自己说过一句温柔的话吗？如果没有，此刻你最想对自己说的一句是什么？",
 3: "这周，你想起谁的时候心里是暖的？或者：最近为谁真心高兴过？",
 4: "这周，有没有一个人让你心里「过不去」？（不用说名字，说一个词就行）",
 5: "这周，你有没有对完全陌生的人，生出过一点点善意？（比如让路、道谢）",
 6: "这周，你心里最明显的一种情绪是什么——是喜，是悲，还是平静？",
 7: "这周，有没有哪个时刻，你很希望自己「别被情绪带走」？",
 8: "这8周里，哪一周你的心变化最大？用一个词说说。",
}
LAY = {
 1: ("这周，「慈心」这个词让你最先想到的是谁，或者什么画面？",
     "如果一个人对自己和身边人都多一分慈心，他的日常会有什么不同？",
     "今天讲的十一种利益，你最想先「试」哪一条？明天可以怎么开始？"),
 2: ("你上一次真心对自己好，是什么时候、做了什么？",
     "一个习惯苛责自己的人，他的生活通常是什么样子？",
     "接下来一周，你可以用哪一种「对自己好」的小动作来练习？"),
 3: ("你身边「不亲不疏」的中性人，大概有谁？",
     "如果对所有人都一样地祝福，你的心会更松，还是更累？",
     "这周你可以先挑哪一位「中性人」，在心里默默祝福一次？"),
 4: ("你心里的「怨敌」，更多是「伤害过你的人」，还是「让你不舒服的那种感受」？",
     "一直抱着这份嗔心，最先被消耗掉的人是谁？",
     "如果暂时做不到祝福他，可以先做哪一步——「看见他的苦」，还是「先照顾好自己」？"),
 5: ("把慈心送给「完全不认识的人」，你的第一反应是自然，还是别扭？",
     "如果一个人的善意只给「自己人」，长期下去会怎样？",
     "这周出门时，你可以选哪一个具体时刻（等电梯、排队），来练一练「经过即祝福」？"),
 6: ("慈悲喜舍四样里，哪一样你天生就比较少？",
     "缺了这一样，会在你和谁的相处里带来摩擦？",
     "这周你想先练哪一样？从哪一个具体的人开始？"),
 7: ("这周有哪个时刻，你希望自己不被情绪带走？",
     "情绪上头时，你通常怎么处理？结果如何？",
     "下次情绪来时，你愿意先试哪个动作——停下来呼吸，还是先祝自己平安？"),
 8: ("8周前后，你对自己「脾气」的观察有什么变化？",
     "这份变化，影响到了你和谁的相处？",
     "往后你打算怎么把慈心留在每一天？给自己定一个最小的习惯。"),
}
SAFE = ("> 🛡️ **心理安全三约定**（每次开场在心里过一遍）：① **保密**——这里说的话不出这间屋子；"
        "② **不评判**——不评价任何人的分享，也不急着评价自己；"
        "③ **可随时暂停**——任何时候觉得不舒服，都可以停下来休息、喝水或离开，不需要解释。")
TABOO = ("> ⚠️ **禅修禁忌提示**：若你正处在严重抑郁、焦虑、创伤后应激，或精神类疾病的发作／用药期，"
         "或正经历强烈的情绪危机，请先咨询医生或心理师，再决定是否练习；"
         "练习中若出现明显不适（如心悸、胸闷、情绪失控），请立即停止，睁开眼睛，把注意力放回呼吸与身体，必要时离场休息。")
VERNOTE = ("> **版本说明**：本目录为《读书会02 · 慈心禅修习》**第二版修订**；原始第一版见 "
           "`交付成果/读书会02_慈心禅修习_8周资料包/`。本版变动：六环节统一 120 分钟口径"
           "（静心10／共读25／分享20／讨论35／禅修15／收尾15）、共读原文标注「本周朗读段」、"
           "补齐心理安全三约定与禅修禁忌、静心开场增破冰、主题讨论增分层追问。")
HDR = ('<div align="right">📅 最近更新：%s　|　第二版修订：六环节120分钟口径（静心10／共读25／分享20／'
       '讨论35／禅修15／收尾15）；共读原文标注「本周朗读段」；补心理安全三约定与禅修禁忌；'
       '静心增破冰、讨论增分层追问</div>' % NOW)

def put_hdr(t):
    if DIV.search(t):
        return DIV.sub(lambda m: HDR + "\n\n" + m.group(0), t, count=1)
    return HDR + "\n\n" + t

def section(lines, pred):
    s = next((i for i, l in enumerate(lines) if l.startswith("## ") and pred(l)), None)
    if s is None:
        return None
    e = next((j for j in range(s + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return s, e

def last_hr(lines, s, e):
    for k in range(e - 1, s, -1):
        if lines[k].strip() == "---":
            return k
    return e

def dedupe_tail(lines):
    idx = [i for i, l in enumerate(lines) if "下一份文档" in l]
    if len(idx) <= 1:
        return lines
    cut = next((j for j in range(idx[0], len(lines)) if lines[j].strip() == "---"), len(lines) - 1)
    return lines[:cut + 1] + ["", "---", ""]

def revise_host(txt, w):
    txt = put_hdr(txt)
    lines = txt.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("## "):
            if "📖" in l:
                lines[i] = re.sub(r"（[^）]*min）", "（25 min）", l)
            elif "💬" in l:
                lines[i] = re.sub(r"（[^）]*min）", "（20 min）", l)
            elif "🔚" in l:
                lines[i] = re.sub(r"（[^）]*min）", "（15 min）", l)
            elif "🧘" in l and "练习" in l:
                lines[i] = re.sub(r"（[^）]*min）", "（15 min）", l)
        else:
            l = re.sub(r"（(\d+)\s*min）", r"（约\1 min）", l)
            l = re.sub(r"（(\d+)分钟）", r"（约\1分钟）", l)
            lines[i] = l
    t = "\n".join(lines)
    for a, b in [("| 📖 共读原文 | 30 min |", "| 📖 共读原文 | 25 min |"),
                 ("| 📖 回顾式共读 | 30 min |", "| 📖 回顾式共读 | 25 min |"),
                 ("| 💬 第一轮分享 | 25 min |", "| 💬 第一轮分享 | 20 min |"),
                 ("| 💬 第一轮分享（深度分享） | 25 min |", "| 💬 第一轮分享（深度分享） | 20 min |"),
                 ("| 🔚 收尾回向 | 20 min |", "| 🔚 收尾回向 | 15 min |")]:
        t = t.replace(a, b)
    t = re.sub(r"(\| 🔚 收尾[^|]*\| )20 min", r"\g<1>15 min", t)
    lines = dedupe_tail(t.split("\n"))
    r = section(lines, lambda l: "静心" in l)
    if r:
        s, e = r
        lines[last_hr(lines, s, e):last_hr(lines, s, e)] = ["", "> 💬 **破冰｜3–5分钟**：%s" % ICE[w], "", SAFE, ""]
    r = section(lines, lambda l: "主题讨论" in l)
    if r:
        s, e = r; a, b, c = LAY[w]
        lines[last_hr(lines, s, e):last_hr(lines, s, e)] = ["", "> **分层追问**（可视时间取用，由浅入深）：",
            "> - 【现象】%s" % a, "> - 【影响】%s" % b, "> - 【应对】%s" % c, ""]
    r = section(lines, lambda l: "🧘" in l and "练习" in l)
    if r:
        s, e = r
        oi = next((i for i in range(s, e) if lines[i].startswith("> ⚠️ 主持人操作")), None)
        if oi is not None:
            lines[oi + 1:oi + 1] = ["", TABOO]
    else:
        r2 = section(lines, lambda l: "扩展内容包" in l)
        idx = r2[0] if r2 else len(lines)
        lines[idx:idx] = ["## 🧘 慈心练习（15 min）", "",
            "> ⚠️ 主持人操作：这是第一次练习，重点是「体验」，不是「做到」。让大家坐好、闭眼，你照读下面的引导词；读完后问一句「刚才心里有什么感觉」，不评价对错。", "",
            TABOO, "", "**引导词**：", "",
            "> 请大家调整好坐姿，轻轻闭上眼睛，先做三次深呼吸，让身体慢慢放松下来。（停顿）", ">",
            "> 现在，把注意力放在自己身上。在心里，缓缓地对自己说这四句话——",
            "> 愿我没有危难；", "> 愿我没有内心的痛苦；", "> 愿我没有身体的痛苦；", "> 愿我保有快乐。（停顿）", ">",
            "> 不用追求「有感觉」，也不用评判自己说得好不好。只是这样说一遍，看看心里有什么变化。", ">",
            "> 如果一时说不出口，也没关系——先静静地听一听这四句话，让它们在心里待一会儿。（停顿）", ">",
            "> 好，慢慢把注意力带回呼吸，再轻轻睁开眼睛。", "", "---", ""]
    r = section(lines, lambda l: "共读原文" in l)
    if r:
        s, e = r; core = 0; total = 0; inc = False
        for i in range(s, e):
            l = lines[i].strip()
            if l.startswith("**") and "★核心段落" in l:
                inc = True; continue
            if l.startswith("**") and "◈扩展段落" in l:
                inc = False; continue
            if l and not l.startswith("#") and not l.startswith(">") and not l.startswith("- **"):
                total += len(l)
                if inc:
                    core += len(l)
        mk = ("> 🎤 **本周朗读段**（★核心段落｜约 %d 字｜中等稍慢约 %d 分钟；本讲共读原文正文合计约 %d 字）："
              "先朗读全部★核心段落；◈扩展段落及补充原文作默读／选读／延伸。"
              % (core, max(1, round(core / 175)), total))
        oi = next((i for i in range(s, e) if lines[i].startswith("> ⚠️ 主持人操作")), None)
        pos = (oi + 1) if oi is not None else (s + 1)
        lines[pos:pos] = ["", mk]
        for i, l in enumerate(lines):
            s2 = l.strip()
            if s2.startswith("**") and "★核心段落" in s2 and "本周朗读段" not in s2:
                lines[i] = l.rstrip() + "【本周朗读段】"
            elif s2.startswith("**") and "◈扩展段落" in s2 and "默读／选读／延伸" not in s2:
                lines[i] = l.rstrip() + "【默读／选读／延伸】"
    return "\n".join(lines)

def del_quote_block(lines, anchor):
    s = next((i for i, l in enumerate(lines) if l.startswith(anchor)), None)
    if s is None:
        return
    j = s
    while j < len(lines) and lines[j].startswith(">"):
        j += 1
    del lines[s:j]

def drop_to_hr(lines, contains):
    s = next((i for i, l in enumerate(lines) if contains in l), None)
    if s is None:
        return
    e = len(lines)
    for j in range(s, len(lines)):
        if lines[j].strip() == "---":
            e = j + 1; break
    del lines[s:e]

def make_student(host):
    lines = host.split("\n")
    del_quote_block(lines, "> ⭐ **本讲主持人速览**")
    drop_to_hr(lines, "## ⏱ 时间弹性指南")
    drop_to_hr(lines, "本讲主持人特别提醒")
    bad = ("> ⚠️ 主持人操作：", "> 主持人：", "**主持人引导**：", "> 💡 ", "> 📚 **下一份文档**")
    lines = [l for l in lines if not l.startswith(bad)]
    lines = ["**请跟随引导静心**：" if l == "**主持人引导语**（照读即可）：" else l for l in lines]
    lines = [re.sub(r"^> \*\*段落优先级\*\*：.*$", "> **段落优先级**：★核心必读｜◈扩展可选", l) for l in lines]
    lines = [l.replace("（主持人版）", "（学员版）") if l.startswith("# ") else l for l in lines]
    lines = [re.sub(r"（[^）]*min）", "", l) if l.startswith("## ") else l for l in lines]
    out = []; done = False
    for l in lines:
        out.append(l)
        if not done and l.startswith("> 本周主题："):
            out.append("> 说明：本学员版按次序列出本讲全部共读内容（★核心必读 / ◈扩展可选）与讨论、练习，内容与主持人版完全一致。")
            done = True
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip() + "\n"

def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)
    os.makedirs(DST)
    for h in sorted(glob.glob(os.path.join(SRC, "*主持人版.md"))):
        w = int(re.search(r"第(\d+)周", os.path.basename(h)).group(1))
        nh = revise_host(open(h, encoding="utf-8").read(), w)
        open(os.path.join(DST, os.path.basename(h)), "w", encoding="utf-8").write(nh)
        st = make_student(nh)
        open(os.path.join(DST, os.path.basename(h).replace("主持人版", "学员版")), "w", encoding="utf-8").write(st)
        print("revised 第%d周 host=%d stu=%d" % (w, len(nh), len(st)))
    shutil.copy(os.path.join(SRC, "原文全集.md"), os.path.join(DST, "原文全集.md"))
    t = put_hdr(open(os.path.join(SRC, "00_主持人总指南.md"), encoding="utf-8").read())
    t = t.replace("| 📖 **共读原文** | 30 min |", "| 📖 **共读原文** | 25 min |")
    t = t.replace("| 💬 **第一轮分享** | 25 min |", "| 💬 **第一轮分享** | 20 min |")
    t = t.replace("| 🔚 **收尾与回向** | 20 min |", "| 🔚 **收尾与回向** | 15 min |")
    t = re.sub(r"(\| 🎯 \*\*主题讨论\*\* \| 35 min \|[^\n]*\n)",
               r"\1| 🧘 **慈心练习** | 15 min | 由主持人带领做简短慈心练习 | 照读引导词，不评价对错 |\n", t)
    t = t.replace("5-10分钟的简短慈心练习", "约15分钟的简短慈心练习").replace("（第2周起）", "（第1周起）")
    open(os.path.join(DST, "00_主持人总指南.md"), "w", encoding="utf-8").write(t)
    t = put_hdr(open(os.path.join(SRC, "README_资料包说明.md"), encoding="utf-8").read())
    t = t.replace("# 📖 慈心禅修习 · 读书会8周资料包\n",
                  "# 📖 慈心禅修习 · 读书会8周资料包\n\n" + VERNOTE + "\n")
    open(os.path.join(DST, "README_资料包说明.md"), "w", encoding="utf-8").write(t)
    t = put_hdr(open(os.path.join(SRC, "更新日志_CHANGELOG.md"), encoding="utf-8").read())
    t = t.replace("# 📝 更新日志（CHANGELOG）\n", "# 📝 更新日志（CHANGELOG）\n\n" + VERNOTE + "\n")
    entry = ("## [v2.0-修订] %s（第二版修订 · 120分钟口径）\n\n"
             "- 六环节统一为 120 分钟：静心10／共读25／分享20／讨论35／禅修15／收尾15；同步速览表、时间弹性指南、本周信息卡与 00 主持人总指南\n"
             "- 共读原文标注「本周朗读段」（以★核心段落为朗读主体，其余标默读／选读／延伸）\n"
             "- 静心开场补「破冰」与「心理安全三约定」（保密／不评判／可随时暂停）；禅修练习补「禅修禁忌提示」\n"
             "- 主题讨论补「分层追问」（现象—影响—应对）\n"
             "- 学员版由修订后主持人版脚本重新派生，共读原文与主持人版逐字一致\n"
             "- 第1周补独立「慈心练习」环节；清理第2周尾部重复段落\n\n") % NOW
    t = t.replace("## [v2.0] 2026-09-09 19:00（第二轮审核修订）",
                  entry + "## [v2.0] 2026-09-09 19:00（第二轮审核修订）", 1)
    open(os.path.join(DST, "更新日志_CHANGELOG.md"), "w", encoding="utf-8").write(t)
    print("done ->", DST, len(os.listdir(DST)), "files")

if __name__ == "__main__":
    main()
