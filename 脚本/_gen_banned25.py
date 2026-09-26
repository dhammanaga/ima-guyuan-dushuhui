#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总既有系列（读书会01-24）【真实已用】media_id，生成读书会25禁用清单（参考基线）。

口径（v2.3 段落级查重 + 21线修正口径）：
- 仅取「真实已用」：各读书会XX素材/第X周_素材照录.md ＋ 交付成果/读书会XX_*资料包/**/*.md
- 【排除】《补充系列设计稿》《第一步_20系列周标题确定稿》《读书会_补充系列_第四批.docx》等预留来源，
  避免候选 id（系列21-25设计稿预留）「自命中」假阳性。
- 本清单为【参考工具】：可引用同一 media_id，但不可引用相同段落。
"""
import os, re, glob, subprocess

ROOT = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
OUT  = os.path.join(ROOT, "读书会25素材", "_禁用清单_读书会01-24已用media_id.txt")
PAT  = re.compile(r"(?:soundrecording|pdf|word)_[a-f0-9]+_[a-f0-9]+")

ids = set()

# 1) 各系列素材照录（真实照录原文）
for p in glob.glob(os.path.join(ROOT, "读书会*素材", "*照录*.md")):
    try:
        ids |= set(PAT.findall(open(p, encoding="utf-8", errors="ignore").read()))
    except Exception:
        pass

# 2) 各系列交付成品资料包（含共读原文）
for p in glob.glob(os.path.join(ROOT, "交付成果", "读书会*资料包", "**", "*.md"), recursive=True):
    try:
        ids |= set(PAT.findall(open(p, encoding="utf-8", errors="ignore").read()))
    except Exception:
        pass

ids = sorted(ids)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
ts = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True,
                    env={**os.environ, "TZ": "Asia/Shanghai"}).stdout.strip()
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"# 禁用清单（参考基线）· 读书会01-24【真实已用】media_id并集（供读书会25查重参考，共 {len(ids)} 个）\n")
    f.write(f"# 生成时间：{ts}（北京时间）\n")
    f.write("# 口径：仅取真实已用（素材照录 md ＋ 交付成品资料包 md）；【已排除】《补充系列设计稿》《第四批.docx》等预留来源，防候选id自命中。\n")
    f.write("# 规则（v2.3）：不同系列或同系列不同周【可引用同一 media_id】，但【不可引用相同段落/相同内容】。\n")
    f.write("#   候选命中须对照其素材照录确认所取章节不重复，并注明\"与读书会XX第X周同文件不同段落（本讲取〈章节名〉，彼讲取〈章节名〉）\"。\n")
    f.write("#\n")
    for i in ids:
        f.write(i + "\n")

print("OUT=" + OUT)
print("total_ids=" + str(len(ids)))
