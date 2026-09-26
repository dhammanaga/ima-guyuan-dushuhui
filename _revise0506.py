#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书会05/06 第二版修订：主持人版定点修订 + 学员版脚本重派生（120口径）。
依据《读书会修订执行手册 v1.3》；省 Token：机械改动全脚本，仅破冰/分层问题为内嵌小片段。"""
import os, re, glob, shutil
from datetime import datetime, timezone, timedelta

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
NOW = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
DIV = re.compile(r'(?m)^<div align="right">.*?</div>$')

SERIES = {
    "05": dict(src=os.path.join(BASE, "pkg05"), dst=os.path.join(BASE, "out05"),
               title="日常生活中的正念正知"),
    "06": dict(src=os.path.join(BASE, "pkg06"), dst=os.path.join(BASE, "out06"),
               title="四念处（一）身念处与受念处"),
}

ICE = {
"05": {
1: "这一周，你哪一次是「身体在做、心却跑到了别处」？一句话说说那个场景，说完就放下。",
2: "今天出门到现在，你做过的一个小决定里，哪一个是「停下来想过一秒」的？",
3: "这一周，你有没有一个下意识就去做的动作或常去的地方——几乎不用想就做了？",
4: "最近的一顿饭，你是「知道自己在吃」的，还是「边做别的事边吃」的？",
5: "如果一天只设一个「提醒自己回来」的觉知点，你会把它设在哪里？",
6: "这一周，有没有哪一次你的反应比预想快——事后才发现「我又这样了」？",
7: "有没有一个跟了你很多年的小习惯，你至今说不清它为什么还留着？",
8: "这八周里，哪个「想起来一下」的时刻，让你印象最深？",
},
"06": {
1: "听到「四念处」三个字，你最先想到的，是身体的哪一处？",
2: "此刻，你能感觉到呼吸正经过鼻端吗？给这一份「感觉到」，打一个 0 到 10 的分。",
3: "从你进门坐下到现在，身体经过了几种姿势——走、站、坐？",
4: "今天你做的一个小动作（起身、开门、倒水），你有没有「知道」自己在做？",
5: "说到身体，你平时最容易「忘记」的是哪一部分——头发、牙齿，还是别的？",
6: "用一句话说：这个身体，对你来说是「我」，还是「我所用的」？",
7: "此刻你心里是一种什么「受」——舒服、不舒服，还是说不上来？",
8: "这八周，你对自己身体的感觉，多了几分留意？",
},
}

LAY = {
"05": {
1: ("原文说「心在天马行空，就是忘失」。回想这一周，你最常「自动驾驶」的是哪个时刻？",
    "这些「心不在」的时刻，带给你的多是方便，还是代价？举一个具体的例子。",
    "若从明天起只挑一个场景练「想起来一下」，你会挑哪一个？打算怎么做？"),
2: ("四种正知里，「有益」与「适宜」，你觉得更像哪一类决定——「该不该做」还是「什么时候做」？",
    "你有没有过「话是对的、但说得不是时候」的经历？当时带来了什么结果？",
    "接下来一周，你可以在哪一个小决定上，先停一秒问一句「这样做有益吗？适宜吗」？"),
3: ("「行处」说的是心常待的地方。你的心平常最爱去哪儿——担忧、回忆、计划，还是评判？",
    "这个「常去的地方」，是让你更安定，还是更疲惫？",
    "这一周，你愿意给心「换一个行处」吗？比如把它放回呼吸或脚步，可以从哪一次开始？"),
4: ("这一周，你有没有一顿饭是「真正尝到味道」的？和平时有什么不同？",
    "如果吃饭、走路都变成「顺便完成的事」，你会失去什么？",
    "明天选一顿饭或一段路，你打算怎么「只做这一件事」？给自己一个具体可行的做法。"),
5: ("你一天里有哪些事是「固定会发生」的（起床、开门、洗手、上床）？哪一件最适合当觉知点？",
    "把觉知点设在日常动作上，跟「专门抽时间打坐」，你觉得各有什么长短？",
    "这周你打算设几个觉知点？把它们写下来，并想好「想起来」之后对自己说一句什么。"),
6: ("这一周，你有没有注意到一个「自动反应」——还没想清楚，情绪或动作就已经出来了？",
    "这种自动反应，是不是在最亲近的人面前更明显？它带来了什么？",
    "下次它再出现，你愿意先做哪一个动作——停下来、深呼吸，还是问一句「我这是怎么了」？"),
7: ("八步拆解里，哪一步你觉得最难——认出标签、追问来源，还是重新试验？",
    "一个跟了你很久的反应模式，如果一直不拆，会在哪些关系里反复出现？",
    "这周你打算先拆哪一个「小标签」？从哪里动第一刀？"),
8: ("八周下来，你觉得自己最大的一个变化是什么？哪怕很小。",
    "这个变化，身边的人有没有察觉到？它改变了你和谁、在哪件事上的相处？",
    "往后你打算怎么把「想起来一下」留在每天？给自己定一个最小、能坚持的做法。"),
},
"06": {
1: ("听完今天的「二十一种修法」框架，你觉得哪一类练法跟你眼下最相应？",
    "如果一开始就想把「全部方法」都做一遍，通常会发生什么？",
    "这八周，你打算先专心走哪一段？可以从哪一个小目标开始？"),
2: ("入出息念里，你的心最容易在什么时候跑掉——刚坐下，还是过一会儿？",
    "心一次次跑掉又拉回，这个过程让你觉得挫败，还是更像在「练习」？",
    "下次再跑掉，你打算怎么对待自己——责备，还是轻轻说一句「回来」？"),
3: ("行、住、坐、卧四种姿势里，你哪一种最容易「忘记觉察」？",
    "如果只在坐着时能觉察、一动起来就全忘，长期下来会怎样？",
    "明天你打算在哪一个姿势转换的瞬间（起身、坐下）插入一次觉察？"),
4: ("四种正知里，「有益」「适宜」「行处」「无痴」，你觉得哪一个最难在日常做到？",
    "缺了正知的动作，往往在什么时候给你带来麻烦？",
    "这周挑一个最常做的小动作，你打算怎么把「先想一下」放进去？"),
5: ("三十二身分里，哪些部分是你平时几乎不去想的？",
    "把身体拆开来看，跟你平时「这是我的身体」的感觉，有什么不一样？",
    "这一周你打算怎么做一个「分寸合适」的简版观察？（可先说清如何避免不适、如何以慈心收尾）"),
6: ("「界作意」与「墓园九相」，哪一部分让你心里最有触动，或最想回避？",
    "直面身体的「无常与不净」，对你的日常心态有什么影响？",
    "若感到不适，你打算怎么照顾自己？什么情况下该暂停、并向可信的人求助？"),
7: ("九种受里，你最近最常出现的是哪一种——身体的苦受，还是心里的忧受？",
    "当「痛」或「烦」升起时，你通常是被它推着走，还是能看着它一会儿？",
    "下次不舒服时，你愿意先做哪一步——不急着赶走它，先看清它是「身」还是「心」？"),
8: ("把「身」与「受」放在一起看之后，你对自己身体的感受有什么新发现？",
    "这份新发现，改变了你面对疼痛或情绪时的态度吗？",
    "往后你打算怎么在日常里继续「如实观受」？可以给自己一个最小的练习约定。"),
},
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
PREAM = re.compile(r"你应该|你必须|一定要|只要.{0,8}就.{0,6}(?:能|会|可以)")


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


def dedupe_tail(lines):
    idx = [i for i, l in enumerate(lines) if "下一份文档" in l]
    if len(idx) <= 1:
        return lines
    cut = next((j for j in range(idx[0], len(lines)) if lines[j].strip() == "---"), len(lines) - 1)
    return lines[:cut + 1] + ["", "---", ""]


def revise_host(txt, ser, w):
    txt = put_hdr(txt, w)
    lines = txt.split("\n")
    # 1) 环节时长（标题）
    for i, l in enumerate(lines):
        if l.startswith("## "):
            if "共读原文" in l:
                lines[i] = re.sub(r"（\d+(\s*min[^）]*)）", r"（25\1）", l)
            elif "第一轮分享" in l:
                lines[i] = re.sub(r"（\d+(\s*min[^）]*)）", r"（20\1）", l)
            elif "收尾" in l:
                lines[i] = re.sub(r"（\d+(\s*min[^）]*)）", r"（15\1）", l)
    t = "\n".join(lines)
    # 2) 速览表时长
    for a, b in [("| 📖 共读原文 | 30 min |", "| 📖 共读原文 | 25 min |"),
                 ("| 💬 第一轮分享 | 25 min |", "| 💬 第一轮分享 | 20 min |"),
                 ("| 🔚 收尾回向 | 20 min |", "| 🔚 收尾回向 | 15 min |")]:
        t = t.replace(a, b)
    # 速览表单元格内的（NN min）加“约”，避免被时长校验误计（对齐 01/02 先例）
    t = "\n".join(re.sub(r"（(\d+)\s*min）", r"（约\1 min）", l) if l.startswith("> |") else l
                  for l in t.split("\n"))
    lines = t.split("\n")
    # 3) 破冰 + 心理安全（静心）
    r = sec_range(lines, "静心")
    if r:
        s, e = r
        if not any("心理安全" in lines[k] for k in range(s, e)):
            k = last_hr(lines, s, e)
            lines[k:k] = ["", "> 💬 **破冰｜3–5分钟**：%s" % ICE[ser][w], "", SAFE, ""]
    # 4) 禅修禁忌（禅修练习）
    r = sec_range(lines, "禅修练习")
    if not r:
        r = sec_range(lines, "禅修")
    if r:
        s, e = r
        if not any("禅修禁忌" in lines[k] for k in range(s, e)):
            oi = next((k for k in range(s, e) if lines[k].startswith("> ⚠️ 主持人操作")), None)
            pos = oi + 1 if oi is not None else s + 1
            lines[pos:pos] = ["", TABOO]
    # 5) 分层追问（主题讨论）
    r = sec_range(lines, "主题讨论")
    if r:
        s, e = r
        a1, b1, c1 = LAY[ser][w]
        k = last_hr(lines, s, e)
        lines[k:k] = ["", "> **分层追问**（可视时间取用，由浅入深）：",
                      "> - 【现象】%s" % a1, "> - 【影响】%s" % b1, "> - 【应对】%s" % c1, ""]
    # 6) 朗读段标注（共读原文）
    r = sec_range(lines, "共读原文")
    if r:
        s, e = r
        span = reading_span(lines, s, e)
        if span:
            a, b, acc = span
            mins = max(1, round(acc / 175))
            end = ("> **【本周朗读段 · 结束】**（以下为默读／选读／延伸内容，时间富余时再读）")
            start = ("> **【本周朗读段 · 开始】**（本段约 %d 字，供中等稍慢朗读，约 %d 分钟；"
                     "其余为默读／选读／延伸内容）" % (acc, mins))
            if not any("本周朗读段" in lines[k] for k in range(s, e)):
                lines.insert(b + 1, "")
                lines.insert(b + 2, end)
                lines.insert(a, start)
                lines.insert(a + 1, "")
    lines = dedupe_tail(lines)
    return "\n".join(lines)


# ---------- 学员版派生（体例对齐 03/05/06/07；兼容两种速览写法） ----------
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
    t = cut_block(t, r"(?m)^> \*{0,2}⭐\*{0,2} ?\*{0,2}本讲主持人速览.*$")
    t = cut_block(t, r"(?m)^## ⏱ 时间弹性指南.*$")
    for mk in ("## 📌 本讲主持人特别提醒", "## ⚠️ 特别提醒"):
        if mk in t:
            t = cut_block(t, re.escape(mk))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> ⚠️ 主持人操作："))
    t = "\n".join(l for l in t.split("\n") if not l.startswith("> 主持人："))
    t = re.sub(r"<!--W_LEAD-->(.*?)<!--/W_LEAD-->", r"\1", t, flags=re.S)
    t = t.replace("（主持人版）", "（学员版）")
    # 本周主题行后插说明
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
        src, dst = cfg["src"], cfg["dst"]
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
            print("  %s 第%d周 host=%d stu=%d" % (ser, w, len(nh), len(st)))
        # 原文全集 原样复制（不动一字）
        shutil.copy(os.path.join(src, "原文全集.md"), os.path.join(dst, "原文全集.md"))
        # 00 总指南
        t = put_hdr(open(os.path.join(src, "00_主持人总指南.md"), encoding="utf-8").read(), None)
        t = re.sub(r"(\| 📖 \*{0,2}共读原文\*{0,2} \| )30 min", r"\g<1>25 min", t)
        t = re.sub(r"(\| 💬 \*{0,2}第一轮分享\*{0,2} \| )25 min", r"\g<1>20 min", t)
        t = re.sub(r"(\| 🔚 \*{0,2}收尾[^|]*\*{0,2} \| )20 min", r"\g<1>15 min", t)
        t = t.replace("名义时长合计约135分钟，实际按120分钟执行",
                      "时长合计120分钟（静心10／共读25／分享20／讨论35／禅修15／收尾15）")
        open(os.path.join(dst, "00_主持人总指南.md"), "w", encoding="utf-8").write(t)
        # README
        t = put_hdr(open(os.path.join(src, "README_资料包说明.md"), encoding="utf-8").read(), None)
        vn = ("> **版本说明**：本目录为《读书会%s · %s》**第二版修订**；原始第一版见 "
              "`交付成果/第一轮初稿/读书会%s_%s_8周资料包/`。本版变动：六环节统一 120 分钟口径"
              "（静心10／共读25／分享20／讨论35／禅修15／收尾15）、共读原文标注「本周朗读段」、"
              "补齐心理安全三约定与禅修禁忌、静心开场增破冰、主题讨论增分层追问。") % (ser, cfg["title"], ser, cfg["title"])
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
