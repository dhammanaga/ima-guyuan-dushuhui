# -*- coding: utf-8 -*-
"""第5版 预清理（机械、零LLM）
用法: python3 preclean.py <输入主持人版.md> <输出.md> [<扩展内容包sidecar.md>]
规则见 work/RULES5.md
"""
import re, sys, os

def parse_material_line(block, key):
    m = re.search(r'^- \*\*%s\*\*：?(.*)$' % key, block, re.M)
    return m.group(1).strip() if m else ''

def clean(text):
    lines = text.split('\n')
    out = []
    ext = []            # 扩展内容包内容（移到原文全集）
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        s = ln.rstrip()
        # 1) 顶部审计行（存疑说明）
        if re.match(r'^>\s*🔴+.*【存疑', s):
            i += 1
            continue
        # 2) 扩展内容包整块删除（## 📚 扩展内容包 … 到下一个 ## ）
        if re.match(r'^##\s*📚?\s*扩展内容包', s):
            j = i + 1
            while j < n and not re.match(r'^## ', lines[j]):
                ext.append(lines[j]); j += 1
            i = j
            continue
        # 3) 材料信息行块 -> 只留文件名
        if re.match(r'^>\s*\*\*段落优先级\*\*', s):
            blk = []
            j = i
            while j < n:
                t = lines[j]
                if t.startswith('-') or t.startswith('>') or t.strip() == '':
                    blk.append(t); j += 1
                    if j < n and not (lines[j].startswith('-') or lines[j].startswith('>') or lines[j].strip()==''):
                        break
                else:
                    break
            blocktext = '\n'.join(blk)
            title = parse_material_line(blocktext, '标题')
            fname = ''
            mm = re.search(r'《[^》]+》', title)
            if mm: fname = mm.group(0)
            else:
                mm2 = re.search(r'^- \*\*标题\*\*：?(.*)$', blocktext, re.M)
                fname = (mm2.group(1).strip() if mm2 else title)
            # 输出规范化：文件行
            out.append('- **文件**：%s' % fname)
            out.append('')
            i = j
            continue
        # 4) 材料信息行（无段落优先级时，直接 - **标题** 起头）
        if re.match(r'^- \*\*标题\*\*', s):
            blk = []; j = i
            while j < n and re.match(r'^- \*\*(标题|文件类型|说明|知识库出处|media_id|打开方式)\*\*', lines[j]):
                blk.append(lines[j]); j += 1
            blocktext = '\n'.join(blk)
            title = parse_material_line(blocktext, '标题')
            mm = re.search(r'《[^》]+》', title)
            fname = mm.group(0) if mm else title
            out.append('- **文件**：%s' % fname)
            out.append('')
            i = j
            continue
        # 5) 完整原文见《原文全集》提示行
        if '完整原文见《原文全集》' in s:
            i += 1
            continue
        # 6) 朗读段 · 开始 行 -> 删除（保留后续内容）
        if '【本周朗读段 · 开始】' in s:
            i += 1
            continue
        # 7) 朗读段 · 结束 行 -> 删除，并丢弃至下一个 '## '
        if '【本周朗读段 · 结束】' in s:
            j = i + 1
            while j < n and not re.match(r'^## ', lines[j]):
                j += 1
            i = j
            continue
        out.append(ln)
        i += 1
    res = '\n'.join(out)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res, '\n'.join(ext)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    side = sys.argv[3] if len(sys.argv) > 3 else None
    t = open(src, encoding='utf-8').read()
    c, ext = clean(t)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8').write(c)
    if side and ext.strip():
        os.makedirs(os.path.dirname(side), exist_ok=True)
        open(side, 'w', encoding='utf-8').write(ext)
    print('in', len(t), '-> out', len(c), 'ext', len(ext))
