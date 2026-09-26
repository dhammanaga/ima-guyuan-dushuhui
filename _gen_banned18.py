#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总既有系列（读书会01-17）已用 media_id，生成读书会18禁用清单（参考基线）。
口径（v2.3 段落级查重）：本清单为【参考工具】——可引用同一 media_id，但不可引用相同段落。
扫描范围：第二轮/ 全目录文本文件（交付成果01-17资料包 + 读书会04-17素材目录 + 历代禁用清单 + docx）。
"""
import os, re, subprocess, glob, zipfile

ROOT = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
OUT  = os.path.join(ROOT, "读书会18素材", "_禁用清单_读书会01-17已用media_id.txt")

PAT = re.compile(r"(?:soundrecording|pdf|word)_[a-f0-9]+_[a-f0-9]+")

ids = set()
exts = (".md", ".txt", ".py", ".json", ".csv")
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith(exts):
            continue
        p = os.path.join(dirpath, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                t = f.read()
        except Exception:
            continue
        for m in PAT.findall(t):
            ids.add(m)

try:
    for p in glob.glob(os.path.join(ROOT, "**", "*.docx"), recursive=True):
        try:
            with zipfile.ZipFile(p) as z:
                for name in z.namelist():
                    if name.startswith("word/") and name.endswith(".xml"):
                        t = z.read(name).decode("utf-8", "ignore")
                        for m in PAT.findall(t):
                            ids.add(m)
        except Exception:
            pass
except Exception:
    pass

ids = sorted(ids)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
ts = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True,
                    env={**os.environ, "TZ": "Asia/Shanghai"}).stdout.strip()
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"# 禁用清单（参考基线）· 读书会01-17已用media_id并集（供读书会18查重参考，共 {len(ids)} 个）\n")
    f.write(f"# 生成时间：{ts}（北京时间）\n")
    f.write("# 来源：第二轮/ 全目录文本 —— 交付成果/读书会01-17资料包全部文档 + 读书会04-17素材目录全部id + 历代禁用清单（含系列21-25设计稿预留id）\n")
    f.write("# 口径（v2.3 段落级查重）：本清单为【参考工具】——不同系列或同系列不同周【可引用同一 media_id】，但【不可引用相同段落/相同内容】。\n")
    f.write("#   候选验证：完整id ∈ 本清单 → 该文件已被既有系列使用 → 须对照其素材照录确认所取章节不重复，并在照录与周文档注明\"与读书会XX第X周同文件不同段落（本讲取〈章节名〉，彼讲取〈章节名〉）\"。\n")
    f.write("#\n")
    for i in ids:
        f.write(i + "\n")

print(f"OUT={OUT}")
print(f"total_ids={len(ids)}")
