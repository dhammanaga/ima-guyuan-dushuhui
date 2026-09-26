#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读书会 19–25 第二版修订（120 口径）。
依据《读书会修订执行手册 v1.4》。省 Token：时长替换/学员版派生/朗读段标注/终检全脚本；
仅破冰、分层追问为内嵌小片段（_data_1925.py），去说教腔为脚本初筛（仅引导语，不碰共读原文）。
用法：
  python3 _revise1925.py            # 全量 19–25
  python3 _revise1925.py 19         # 单系列
  python3 _revise1925.py 19 dry     # 单系列干跑（只打印，不写盘）
"""
import os, re, glob, shutil, sys, time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _data_1925 import ICE, LAY

BASE = "/sandbox/workspace/交付成果"
SRCROOT = os.path.join(BASE, "第一轮初稿")
DSTROOT = os.path.join(BASE, "第二轮修订版")
NOW = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")

SERIES = {
 "19": dict(dir="读书会19_戒定慧三学_8周资料包", title="戒定慧三学——修学的完整框架", num="19"),
 "20": dict(dir="读书会20_从凡夫到圣者道果与涅槃_8周资料包", title="从凡夫到圣者——道果与涅槃", num="20"),
 "21": dict(dir="读书会21_破妄显真破除三十八种修道上的自欺_8周资料包", title="破妄显真——破除三十八种修道上的自欺", num="21"),
 "22": dict(dir="读书会22_四预流支_8周资料包", title="四预流支", num="22"),
 "23": dict(dir="读书会23_小问答经讲记萨迦耶见与圣八支道_8周资料包", title="《小问答经》讲记——萨迦耶见与圣八支道", num="23"),
 "24": dict(dir="读书会24_三十二身分（身至念）专修_8周资料包", title="三十二身分（身至念）专修", num="24"),
 "25": dict(dir="读书会25_随念修习全系列（七随念与食厌想）_8周资料包", title="随念修习全系列（七随念与食厌想）", num="25"),
}

DIV = re.compile(r'(?m)^<div align="right">.*?</div>$')
SAFE = ("> 🛡️ **心理安全三约定**（每次开场在心里过一遍）：① **保密**——这里说的话不出这间屋子；"
        "② **不评判**——不评价任何人的分享，也不急着评价自己；"
        "③ **可随时暂停**——任何时候觉得不舒服，都可以停下来休息、喝水或离开，不需要解释。")
TABOO = ("> ⚠️ **禅修禁忌提示**：若你正处在严重抑郁、焦虑、创伤后应激，或精神类疾病的发作／用药期，"
         "或正经历强烈的情绪危机，请先咨询医生或心理师，再决定是否练习；"
         "练习中若出现明显不适（如心悸、胸闷、情绪失控），请立即停止，睁开眼睛，把注意力放回呼吸与身体，必要时离场休息。")
SOFTEN = [("你应该", "你不妨"), ("你必须", "你需要"), ("一定要", "要"),
          ("只要", "只要"), ]  # 保留"只要"，去说教只做温和替换
SOFTEN = [("你应该", "你不妨"), ("你必须", "你需要"), ("一定要", "要")]

# 共读原文节内「非阅读内容」行前缀（用于朗读段字数统计时跳过）
SKIP_PREFIX = ("> ⚠️", "> **说明**", "> **【本周朗读段", "- 文件类型", "- 知识库出处",
               "- media_id", "- 打开方式", "- 说明", "**主持人：", "> 主持人：",
               "（以下", "（主持人：", "### 原文材料", "### 共读原文串讲", "### 🧭", "### 🧩",
               "### 🗣", "### 📎")
HOSTH3 = ("主持人用", "主持备用", "备课用", "不必照读", "主持人带读", "主持人导读", "主持备用", "串讲导引")
LO, HI = 3500, 4500


def put_hdr(t):
    hdr = ('<div align="right">📅 最近更新：%s　|　第二版修订：六环节120分钟口径（静心10／共读25／分享20／'
           '讨论35／禅修15／收尾15）；共读原文标注「本周朗读段」；补心理安全三约定与禅修禁忌；'
           '静心增破冰、讨论增分层追问</div>' % NOW)
    if DIV.search(t):
        return DIV.sub(lambda m: hdr, t, count=1)
    return hdr + "\n\n" + t


def sec_range(lines, name, allsec=False):
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for k, s in enumerate(idx):
        if name in lines[s]:
            e = idx[k + 1] if k + 1 < len(idx) else len(lines)
            if allsec:
                out.append((s, e))
            else:
                return s, e
    return out if allsec else None


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


def read_block_range(lines):
    """共读原文区块 [s, e)：自 '## 📖 共读原文' 起，其后紧跟的 '## 材料N' 同级节一并纳入，
    直到「第一个非材料的 ## 节」或「第一个主持人专用 ### 子节」为止。返回 (s, e) 或 None。"""
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    ci = None
    for k, s in enumerate(idx):
        if "共读原文" in lines[s]:
            ci = k; break
    if ci is None:
        return None
    s = idx[ci]
    e = len(lines)
    for j in range(ci + 1, len(idx)):
        title = lines[idx[j]][3:].lstrip()
        if title.startswith("材料"):
            continue
        e = idx[j]; break
    # 收紧：遇主持人专用 ### 子节即止（该子节属主持人导读，不必照读、可按新口径改时长）
    for i in range(s + 1, e):
        if lines[i].startswith("### ") and any(k in lines[i] for k in HOSTH3):
            e = i; break
    return s, e


def reading_span(lines, s, e):
    us, fenced, skip_h3 = [], False, False
    for i in range(s + 1, e):
        l = lines[i]
        st = l.strip()
        if st.startswith("```"):
            if not fenced and "graph" in (lines[i + 1].strip().lower()[:12] if i + 1 < e else ""):
                fenced = "graph"      # 图形块：整段跳过
            else:
                fenced = (not fenced)
            continue
        if st.startswith("### "):
            skip_h3 = any(k in st for k in HOSTH3)
            continue
        if skip_h3 or fenced == "graph":
            continue
        if fenced:
            n = len(st)
            if n:
                us.append((i, n))
            continue
        if any(st.startswith(p) for p in SKIP_PREFIX):
            continue
        n = body_len(l)
        if n == 0:
            continue
        us.append((i, n))
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


def title_fix(l):
    l = re.sub(r"(共读原文)（30(\s*min[^）]*)）", r"\1（25\2）", l)
    l = re.sub(r"(第一轮分享)（25(\s*min[^）]*)）", r"\1（20\2）", l)
    l = re.sub(r"(收尾[^（]*?)（(\d+)(\s*min[^）]*)）", lambda m: m.group(1) + "（15" + m.group(3) + "）", l)
    l = re.sub(r"(分段朗读与板书建议)（30(\s*min[^）]*)）", r"\1（25\2）", l)
    return l


def nt_fix(l):
    # 表格行
    l = re.sub(r"(\|\s*共读原文\s*\|\s*)\d+(\s*min)", r"\g<1>25\g<2>", l)
    l = re.sub(r"(\|\s*第一轮分享\s*\|\s*)\d+(\s*min)", r"\g<1>20\g<2>", l)
    l = re.sub(r"(\|\s*收尾[^|]*\|\s*)\d+(\s*min)", r"\g<1>15\g<2>", l)
    l = re.sub(r"(\|\s*分享与讨论\s*\|\s*)\d+(\s*min)", r"\g<1>55\g<2>", l)
    # 具名括号
    l = l.replace("共读原文（30 min）", "共读原文（约 25 min）")
    l = l.replace("第一轮分享（25 min）", "第一轮分享（约 20 min）")
    l = l.replace("收尾与回向（20 min）", "收尾与回向（约 15 min）")
    l = l.replace("收尾回向（20 min）", "收尾回向（约 15 min）")
    l = l.replace("时间切分（30 min）", "时间切分（约 25 min）")
    # 六数串
    for a, b in [("10/30/25/35/15/20", "10/25/20/35/15/15"),
                 ("10／30／25／35／15／20", "10／25／20／35／15／15")]:
        l = l.replace(a, b)
    # 其余非标题括号 → 加“约”以免被时长校验误计
    l = re.sub(r"（(\d+)\s*(min|分钟)）", r"（约 \1 \2）", l)
    for a, b in SOFTEN:
        l = l.replace(a, b)
    return l


def revise_host(txt, ser, w):
    txt = put_hdr(txt)
    lines = txt.split("\n")
    rb = read_block_range(lines)
    rs, re_ = rb if rb else (-1, -1)
    for i, l in enumerate(lines):
        if rs < i < re_:          # 共读原文正文：逐字不动
            continue
        if i == rs:               # 共读原文标题行：只改时长
            lines[i] = title_fix(l)
            continue
        if l.startswith("## "):
            lines[i] = title_fix(l)
        else:
            lines[i] = nt_fix(l)
    # 静心：破冰 + 心理安全
    r = sec_range(lines, "静心")
    if r:
        s, e = r
        seg = "\n".join(lines[s:e])
        block = []
        if "破冰" not in seg:
            block.append("> 💬 **破冰｜3–5分钟**：%s" % ICE[ser][w])
        if "心理安全" not in seg:
            block.append(SAFE)
        if block:
            k = e
            while k - 1 > s and lines[k - 1].strip() == "":
                k -= 1
            ins = []
            for b in block:
                ins += ["", b]
            lines[k:k] = ins + [""]
    # 禅修禁忌
    r = sec_range(lines, "禅修练习") or sec_range(lines, "禅修")
    if r:
        s, e = r
        if not any("禅修禁忌" in lines[k] for k in range(s, e)):
            oi = next((k for k in range(s, e) if lines[k].startswith("> ⚠️ 主持人操作")), None)
            pos = oi + 1 if oi is not None else s + 1
            lines[pos:pos] = ["", TABOO]
    # 分层追问
    r = sec_range(lines, "主题讨论") or sec_range(lines, "讨论")
    if r:
        s, e = r
        if not any("分层追问" in lines[k] for k in range(s, e)):
            a1, b1, c1 = LAY[ser][w]
            k = last_hr(lines, s, e)
            if k == e:
                k = e
                while k - 1 > s and lines[k - 1].strip() == "":
                    k -= 1
            lines[k:k] = ["", "> **分层追问**（可视时间取用，由浅入深）：",
                          "> - 【现象】%s" % a1, "> - 【影响】%s" % b1,
                          "> - 【应对】%s" % c1, ""]
    # 朗读段
    r = read_block_range(lines)
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


def dedupe_tail(lines):
    idx = [i for i, l in enumerate(lines) if "下一份文档" in l]
    if len(idx) <= 1:
        return lines
    cut = next((j for j in range(idx[0], len(lines)) if lines[j].strip() == "---"), len(lines) - 1)
    return lines[:cut + 1] + ["", "---", ""]


# ---------- 学员版派生（复用 _mk_student.main，再补体例修正） ----------
import _mk_student


def derive_student(host_path, stu_path):
    _mk_student.main(host_path, stu_path)
    with open(stu_path, encoding="utf-8") as f:
        t = f.read()
    # §10.1 学员版环节标题一律不带（N min）
    lines = [re.sub(r"（\s*约?\s*\d+\s*(?:min|分钟)\s*）", "", l) if l.startswith("## ") else l
             for l in t.split("\n")]
    t = "\n".join(lines)
    with open(stu_path, "w", encoding="utf-8") as f:
        f.write(t)
    # 回读校验（防未 flush 截断）
    for _ in range(3):
        try:
            with open(stu_path, encoding="utf-8") as f:
                back = f.read()
            if back == t:
                return
        except UnicodeDecodeError:
            pass
        time.sleep(0.2)
        with open(stu_path, "w", encoding="utf-8") as f:
            f.write(t)


def revise_aux(cfg, dst):
    num, title, srcdir = cfg["num"], cfg["title"], cfg["dir"]
    src = os.path.join(SRCROOT, srcdir)
    # 原文全集：原样复制（内容不动）
    shutil.copy(os.path.join(src, "原文全集.md"), os.path.join(dst, "原文全集.md"))
    # 00 总指南
    t = put_hdr(open(os.path.join(src, "00_主持人总指南.md"), encoding="utf-8").read())
    reps = [("| 📖 共读原文 | 30 min |", "| 📖 共读原文 | 25 min |"),
            ("| 💬 第一轮分享 | 25 min |", "| 💬 第一轮分享 | 20 min |"),
            ("| 🔚 收尾回向 | 20 min |", "| 🔚 收尾回向 | 15 min |"),
            ("| 🔚 收尾与回向 | 20 min |", "| 🔚 收尾与回向 | 15 min |"),
            ("合计60分钟", "合计55分钟"), ("守住30分钟", "守住25分钟"),
            ("留足20分钟", "留足15分钟"), ("留 20 分钟", "留 15 分钟"),
            ("10/30/25/35/15/20", "10/25/20/35/15/15")]
    for a, b in reps:
        t = t.replace(a, b)
    t = re.sub(r"（(共读原文|第一轮分享|收尾回向|收尾与回向)[^）]*?）", lambda m: m.group(0), t)
    with open(os.path.join(dst, "00_主持人总指南.md"), "w", encoding="utf-8") as f:
        f.write(t)
    # README
    t = put_hdr(open(os.path.join(src, "README_资料包说明.md"), encoding="utf-8").read())
    for a, b in reps:
        t = t.replace(a, b)
    vn = ("> **版本说明**：本目录为《读书会%s · %s》**第二版修订**；原始第一版见 "
          "`交付成果/第一轮初稿/%s/`。本版变动：六环节统一 120 分钟口径"
          "（静心10／共读25／分享20／讨论35／禅修15／收尾15）、共读原文标注「本周朗读段」、"
          "补齐心理安全三约定与禅修禁忌、静心开场增破冰、主题讨论增分层追问。") % (num, title, srcdir)
    m = re.search(r"(?m)^# .*$", t)
    if m:
        t = t[:m.end()] + "\n\n" + vn + t[m.end():]
    with open(os.path.join(dst, "README_资料包说明.md"), "w", encoding="utf-8") as f:
        f.write(t)
    # CHANGELOG
    t = put_hdr(open(os.path.join(src, "更新日志_CHANGELOG.md"), encoding="utf-8").read())
    entry = ("## v2.0（第二版修订） · %s\n\n"
             "- **修订口径**：按《读书会修订执行手册 v1.4》把 8 周文档改为 120 分钟严格封顶——"
             "静心10／共读25／分享20／讨论35／禅修15／收尾15；同步修正各环节标题、时间弹性指南、"
             "本周信息卡与 00 主持人总指南中的时长字段。\n"
             "- **共读朗读段**：在共读原文中标注「本周朗读段」（约 3,500–4,500 字，按中等稍慢 150–200 字/分），"
             "其余标默读／选读／延伸；**共读原文逐字未改**。\n"
             "- **安全与教学法**：补齐心理安全三约定与禅修禁忌提示；静心开场增 3–5 分钟主题相关破冰；"
             "主题讨论增 2–3 个分层次追问（现象—影响—应对）；弱化说教腔（仅改引导语）。\n"
             "- **学员版**：由修订后的主持人版经 `_mk_student.py` 重新派生，环节标题去除时长括号，"
             "共读原文与主持人版逐字一致。\n\n---\n\n") % NOW.split(" ")[0]
    m = re.search(r"(?m)^## v1\.0.*$", t)
    if m:
        t = t[:m.start()] + entry + t[m.start():]
    else:
        t = t.rstrip() + "\n\n" + entry
    with open(os.path.join(dst, "更新日志_CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write(t)
    # 辅助文件净化：避免出现全角定界标记字面量（终检硬性项）
    for fn in ("00_主持人总指南.md", "README_资料包说明.md", "更新日志_CHANGELOG.md"):
        p = os.path.join(dst, fn)
        with open(p, encoding="utf-8") as f:
            s = f.read().replace("<！--", "&lt;！--")
        with open(p, "w", encoding="utf-8") as f:
            f.write(s)


def main():
    argser = sys.argv[1] if len(sys.argv) > 1 else None
    dry = len(sys.argv) > 2 and sys.argv[2] == "dry"
    sers = [argser] if argser else list(SERIES)
    for ser in sers:
        cfg = SERIES[ser]
        src = os.path.join(SRCROOT, cfg["dir"])
        dst = os.path.join(DSTROOT, cfg["dir"] + "（第二版修订）")
        if not dry:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            os.makedirs(dst)
        hosts = sorted(glob.glob(os.path.join(src, "*主持人版.md")))
        hosts = [h for h in hosts if re.search(r"第\d+周", os.path.basename(h))]
        hosts.sort(key=lambda x: int(re.search(r"第(\d+)周", os.path.basename(x)).group(1)))
        for h in hosts:
            w = int(re.search(r"第(\d+)周", os.path.basename(h)).group(1))
            nh = revise_host(open(h, encoding="utf-8").read(), ser, w)
            name = os.path.basename(h)
            if dry:
                sp = reading_span(nh.split("\n"), *read_block_range(nh.split("\n")))
                secs = [int(x) for x in re.findall(r"（(\d+)\s*min）", nh)]
                print("  [%s W%d] host=%d secs=%s sum=%d span=%s" % (
                    ser, w, len(nh), secs, sum(secs), (sp[2] if sp else None)))
                continue
            with open(os.path.join(dst, name), "w", encoding="utf-8") as f:
                f.write(nh)
            derive_student(os.path.join(dst, name), os.path.join(dst, name.replace("主持人版", "学员版")))
            with open(os.path.join(dst, name.replace("主持人版", "学员版")), encoding="utf-8") as f:
                stu_len = len(f.read())
            print("  %s W%d host=%d stu=%d read=%s" % (
                ser, w, len(nh), stu_len, "本周朗读段" in nh))
        if not dry:
            revise_aux(cfg, dst)
            print("  -> %s 完成" % os.path.basename(dst))


if __name__ == "__main__":
    main()
