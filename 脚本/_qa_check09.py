#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_qa_check09.py — 读书会09资料包程序化质检（终检用）
基于 _qa_check08.py，适配 09：禁用清单指向 读书会09素材/218个id 清单（01-08已用并集），默认包目录 09。
硬校验：①文件存在 ②禁用清单命中 ③临时链接 ④双版本「共读原文」引用行逐字一致 ⑤内容锚点
提示项：主题讨论/禅修练习/扩展包/回向 的独有行（多为主持人专属标签，供人工过目）
用法: python3 _qa_check09.py [资料包目录]
"""
import os
import re
import sys
import glob

BASE = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
PKG = sys.argv[1] if len(sys.argv) > 1 else BASE + "/交付成果/读书会09_四圣谛二灭与道_8周资料包"
BANNED_F = BASE + "/读书会09素材/_禁用清单_读书会0102030405060708已用media_id.txt"
ID_RE = re.compile(r"(?:soundrecording|pdf|word)_[a-f0-9]+_[a-f0-9]+")
SHARE_KEYS = ["共读原文", "主题讨论", "禅修练习", "扩展内容包", "收尾与回向"]
SKIP = ["主持人", "照录即可", "照读即可", "主持人先看", "共读提要", "请跟随引导",
        "提示：以下为完整原文", "讨论问题（按优先级）", "学习提示", "延伸阅读"]

# 周次内容锚点（防材料错置）
ANCHORS = {
    1: ["灭圣谛", "苦之集"],
    2: ["涅槃", "渴爱"],
    3: ["八正道", "道圣谛"],
    4: ["彼分断", "镇伏断"],
    5: ["邪见", "十二道分"],
    6: ["三十七", "觉支"],
    7: ["出世间心", "道心"],
    8: ["转法轮", "八正道"],
}

def log(m, **kw):
    print(m, **kw, flush=True)

def sections(t):
    d = {}
    for p in re.split(r"^## ", t, flags=re.M)[1:]:
        d[p.split("\n", 1)[0].strip()] = p
    return d

def norm(sec):
    out = []
    for ln in sec.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("> ⚠️"):
            continue
        if s == ">":
            continue
        if any(k in s for k in SKIP):
            continue
        s = re.sub(r"[（(]\s*\d+\s*min\s*[)）]", "", s)
        s = re.sub(r"^\d+\.\s*", "", s)
        out.append(s)
    return out

def smap(secs):
    m = {}
    for title, body in secs.items():
        for k in SHARE_KEYS:
            if k in title:
                m[k] = norm(body)
    return m

def main():
    banned = set(open(BANNED_F, encoding="utf-8").read().split()) if os.path.exists(BANNED_F) else set()
    hosts = sorted(glob.glob(os.path.join(PKG, "*主持人版.md")))
    if not hosts:
        log("❌ 目录为空: " + PKG); return 1
    hard = 0
    log(f"质检: {PKG}\n周数 {len(hosts)} / 禁用清单 {len(banned)} 个\n" + "-" * 62)
    for h in hosts:
        s = h.replace("主持人版", "学员版")
        wk = os.path.basename(h).split("_")[0]
        ht = open(h, encoding="utf-8").read()
        if not os.path.exists(s):
            log(f"▸ {wk}: ❌ 缺学员版"); hard += 1; continue
        st = open(s, encoding="utf-8").read()
        hit = set(ID_RE.findall(ht + st)) & banned
        links = re.findall(r"https?://\S+", ht + st)
        hm, sm = smap(sections(ht)), smap(sections(st))
        # 共读原文硬校验：比较"实质原文行"集合（原文引用行/材料标题/信息行），忽略主持人专属引导行
        PREF = ("> [", "### 原文材料", "- **标题**", "- **文件类型**",
                "- **知识库出处**", "- **media_id**", "- **打开方式**")
        def subst(ls):
            return {x for x in ls if x.startswith(PREF)}
        ha, sa = subst(hm.get("共读原文", [])), subst(sm.get("共读原文", []))
        ok = ha == sa
        # 内容锚点校验
        wknum = int(re.sub(r"\D", "", wk) or 0)
        anchors = ANCHORS.get(wknum, [])
        body = ht + st
        miss_anchor = [a for a in anchors if a not in body]
        log(f"▸ {wk} 主持{len(ht):,}/学员{len(st):,}字 | 禁用{'❌'+str(hit) if hit else '✅0'} | "
            f"链接{'❌' if links else '✅无'} | 共读原文{'✅' if ok else '❌'}({len(ha)}条实质原文行) | "
            f"锚点{'✅' if not miss_anchor else '❌缺'+str(miss_anchor)}")
        if not ok:
            for x in list(sa - ha)[:3]:
                log(f"      学员独有: {x[:60]}")
            for x in list(ha - sa)[:3]:
                log(f"      主持独有: {x[:60]}")
            hard += 1
        if hit: hard += 1
        if links: hard += 1
        if miss_anchor: hard += 1
        for k in ["主题讨论", "禅修练习", "扩展内容包", "收尾与回向"]:
            onlyA, onlyB = set(hm.get(k, [])) - set(sm.get(k, [])), set(sm.get(k, [])) - set(hm.get(k, []))
            if onlyA or onlyB:
                log(f"    ~[{k}] 独有行 主持{len(onlyA)}/学员{len(onlyB)}")
                for x in list(onlyA)[:2]:
                    log(f"        主持独有: {x[:52]}")
                for y in list(onlyB)[:2]:
                    log(f"        学员独有: {y[:52]}")
    log("=" * 62)
    log(f"硬性失败: {hard} 处 {'✅ 全部通过' if hard == 0 else '❌ 需处理'}")
    return 0 if hard == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
