# -*- coding: utf-8 -*-
"""mk_student5.py — 第5版：由主持人版派生学员版（块按 `## ` 边界切分）
用法: python3 mk_student5.py <主持人版.md> [输出.md]
"""
import sys, re

HOST_BLOCKS = [  # (起始正则, 结束边界类型)  end='hr' 到下一个 ---；end='sec' 到下一个 ##
    (r'^>\s*⭐\s*\*\*本讲主持人速览', 'hr'),
    (r'^##\s*⏱\s*时间弹性指南', 'sec'),
    (r'^##\s*📌\s*本讲主持人特别提醒', 'sec'),
    (r'^##\s*🎓\s*本讲教学要点', 'sec'),
    (r'^##\s*📚\s*扩展内容包', 'sec'),
]

def cut(text, start_re, end):
    lines = text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        if re.match(start_re, lines[i]):
            i += 1
            if end == 'hr':
                while i < len(lines) and not re.match(r'^-{3,}\s*$', lines[i]):
                    i += 1
                if i < len(lines): i += 1  # 吃掉 ---
            else:
                while i < len(lines) and not re.match(r'^##\s', lines[i]):
                    i += 1
            continue
        out.append(lines[i]); i += 1
    return '\n'.join(out)

def main(src, dst=None):
    t = open(src, encoding='utf-8').read()
    # EXT_READ
    m = re.search(r'<!--EXT_READ-->(.*?)<!--/EXT_READ-->\s*', t, re.S)
    ext = m.group(1).strip() if m else ''
    if m: t = t.replace(m.group(0), '')
    # 主持人专属块
    for pat, end in HOST_BLOCKS:
        t = cut(t, pat, end)
    # 单行
    t = '\n'.join(l for l in t.split('\n')
                  if '主持人操作' not in l
                  and not re.match(r'^>\s*主持人：', l)
                  and not re.match(r'^>\s*📚\s*\*\*下一份文档', l))
    # W_LEAD
    t = re.sub(r'<!--W_LEAD-->(.*?)<!--/W_LEAD-->', r'\1', t, flags=re.S)
    t = t.replace('（主持人版）', '（学员版）')
    # 本周主题行后插说明
    lines = t.split('\n'); out = []; ins = False
    for l in lines:
        out.append(l)
        if not ins and l.startswith('> 本周主题：'):
            out.append('> 说明：本学员版按次序列出本讲全部共读内容与讨论、练习，与主持人版完全一致。')
            ins = True
    t = '\n'.join(out)
    t = t.replace('**主持人引导语**（照读即可）：\n\n> 我们先静坐一分钟', '**请跟随引导静心**：\n\n> 我们先静坐一分钟')
    t = t.replace('**主持人引导语**（照读即可）：', '**请跟随引导练习**：')
    t = re.sub(r'\n{4,}', '\n\n', t)
    t = re.sub(r'(\n-{3,}\n)\s*(\n-{3,}\n)', r'\1', t)
    if ext:
        t = t.rstrip() + '\n\n---\n\n' + ext + '\n'
    if not dst:
        dst = src.replace('主持人版', '学员版')
    open(dst, 'w', encoding='utf-8').write(t)
    print('学员版:', dst, len(t), '字符')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
