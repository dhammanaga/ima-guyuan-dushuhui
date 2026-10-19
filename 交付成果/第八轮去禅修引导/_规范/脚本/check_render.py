# -*- coding: utf-8 -*-
"""读书会主持人版 · 渲染层自检（模拟 Markdown 段落切分）

为什么需要它：`final_check` / `check_format` 只查**结构标记**，查不出**渲染**问题。
最典型：`**一、…**` 段标题行若**紧贴上一行正文**（中间无空行），
Markdown 会把整块当一个段落渲染 —— 网页上段标题就「混进正文里」了。
2026-10-15 第2周实际发生（7 个段标题全部中招），而两个脚本都报「合规」。

用法：
    python check_render.py <文件.md> [<文件.md> …]
退出码：0 = 渲染无问题；1 = 有段标题被吸进段落
"""
import re, sys

# 块级元素：标题／段标题小标签／表格／引用／列表／图片／分隔线
BLOCK = re.compile(r"^\s*(#{1,6}\s|\*\*[^*]+\*\*\s*$|[|>-]|!\[|---+$)")

def is_title(s):
    s = s.strip()
    return bool(re.match(r"^\*\*[^*]+\*\*$", s)) and len(s) < 80

def seg_title(s):
    s = s.strip()
    return bool(re.match(r"^\*\*[一二三四五六七八九十]、", s))

def check(path):
    t = open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    L = t.split("\n")
    name = path.replace("\\", "/").split("/")[-1]
    tight, mixed, blocks = [], [], []
    para, inside = [], False
    for i, l in enumerate(L):
        s = l.strip()
        if s.startswith("```"):
            inside = not inside
            if para: blocks.append(para); para = []
            continue
        if inside: continue
        if not s:                       # 空行 = 段落边界
            if para: blocks.append(para); para = []
            continue
        para.append((i + 1, s))
    if para: blocks.append(para)

    # 1) 段标题行是否紧贴上下行
    for i, l in enumerate(L):
        if is_title(l):
            if i > 0 and L[i - 1].strip():
                tight.append((i + 1, l.strip()[:40], "上行紧贴"))
            if i + 1 < len(L) and L[i + 1].strip():
                tight.append((i + 1, l.strip()[:40], "下行紧贴"))
    # 2) 是否存在「段标题 + 正文」同块
    for blk in blocks:
        has_t = any(seg_title(x[1]) for x in blk)
        has_o = any(not seg_title(x[1]) for x in blk)
        if has_t and has_o:
            mixed.append(blk[0])

    print(name)
    print("  渲染块 %d 个" % len(blocks))
    if tight:
        print("  ✗ 段标题紧贴上下行 %d 处（缺空行 → 会被渲染成同一段）：" % len(tight))
        for ln, tt, why in tight[:8]:
            print("      L%-4d [%s] %s" % (ln, why, tt))
    if mixed:
        print("  ✗ 段标题与正文同块 %d 处：" % len(mixed))
        for ln, _ in mixed[:5]:
            print("      L%d" % ln)
    if not tight and not mixed:
        print("  ✓ 渲染无问题：所有段标题均独立成段")
    return not (tight or mixed)

if __name__ == "__main__":
    ok = True
    for f in sys.argv[1:]:
        ok = check(f) and ok
    sys.exit(0 if ok else 1)
