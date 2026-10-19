# -*- coding: utf-8 -*-
"""读书会主持人版 · 格式核对（2026-10-15 尊者令「每次修订都要注意格式」）

用法：
    python check_format.py <文件.md> [<标杆文件.md> …]
    python check_format.py --std  <标杆.md>      # 只打印标杆的格式构成（开工前提取标尺用）

检查项（对照读书会17 第3周定稿）：
  1. H1  全文仅 1 个：# 第N周：…（主持人版）
  2. H2  九个环节，固定带 emoji：📋🗺🧘📖💬🎯🔚📌
  3. H3  材料标题 ### 原文材料X／### 练习X
  4. 段标题 **一、…**（加粗、不加【】），且各级编号连续
  5. 小标签 **…**（不含序号）
  6. 不得有裸编号行（^[一二三四五六]、）——三重失效
  7. 代码块 ``` 成对
  8. EXT_READ 标记 1/1
  9. 行尾无残留 \\r
"""
import re, sys, io

EMOJI_H2 = ['📋','🗺','🧘','📖','💬','🎯','🔚','📌']
CN = '一二三四五六七八九十'

def rd(p):
    return open(p, encoding='utf-8', newline='').read()

def analyze(path):
    raw = rd(path)
    t = raw.replace('\r\n', '\n')
    L = t.split('\n')
    inside = False
    h1 = h2 = h3 = seg = tag = 0
    bare = []
    segs = []
    for i, l in enumerate(L, 1):
        s = l.strip()
        if s.startswith('```'):
            inside = not inside
            continue
        if inside:
            continue
        m = re.match(r'^(#{1,6})\s+(.+)$', s)
        if m:
            lv, txt = len(m.group(1)), m.group(2)
            if lv == 1: h1 += 1
            elif lv == 2: h2 += 1
            elif lv == 3: h3 += 1
            continue
        if re.match(r'^\*\*[^*]+\*\*$', s):
            if re.match(r'^\*\*[%s]、' % CN, s): seg += 1; segs.append(s)
            else: tag += 1
            continue
        if re.match(r'^[%s]、\S' % CN, s):
            bare.append((i, s[:40]))
    fences = sum(1 for l in L if l.strip().startswith('```'))
    return dict(
        name=path.split('/')[-1].split('\\')[-1],
        h1=h1, h2=h2, h3=h3, seg=seg, tag=tag,
        bare=bare, segs=segs,
        fences=fences,
        crlf=raw.count('\r\n'),
        stray_cr=sum(1 for l in L if l.endswith('\r')),
        ext=(t.count('<!--EXT_READ-->'), t.count('<!--/EXT_READ-->')),
    )

def std(path):
    d = analyze(path)
    print('═══ 格式标尺：%s ═══' % d['name'])
    print('  H1 文件标题   × %d' % d['h1'])
    print('  H2 九个环节   × %d' % d['h2'])
    print('  H3 材料/练习  × %d' % d['h3'])
    print('  段标题 **X、…** × %d' % d['seg'])
    print('  小标签 **…**   × %d' % d['tag'])
    print('  ``` 围栏      %d 个（%s）' % (d['fences'], '成对 ✅' if d['fences'] % 2 == 0 else '奇数 ✗'))
    if d['segs']:
        print('  段标题样例：')
        for s in d['segs'][:4]:
            print('    %s' % s[:62])
        print('    …（共 %d 个）' % len(d['segs']))

def check(path, std_path=None):
    d = analyze(path)
    p = []
    if d['h1'] != 1:
        p.append('H1 应为 1 个，实为 %d' % d['h1'])
    if d['h2'] != 13:
        p.append('H2 应为 13 个（九个环节＋特别提醒＋延伸阅读等），实为 %d' % d['h2'])
    if d['bare']:
        p.append('⚠ 裸编号行 %d 处（第 %s 行）——不进大纲·无字号·脚本不认，'
                 '应改为 **X、…**' % (len(d['bare']), '/'.join(str(x[0]) for x in d['bare'][:5])))
    if d['fences'] % 2 != 0:
        p.append('⑥ 代码块 ``` 奇数个（%d）——未闭合会吞掉其后全部 ## 标题' % d['fences'])
    if d['ext'] != (1, 1):
        p.append('③ EXT_READ 标记 %d/%d —— 应为 1/1' % d['ext'])
    if d['stray_cr']:
        p.append('⚠ 行尾残留 \\r %d 处 —— 正则 $ 匹配不到，先清理' % d['stray_cr'])
    if std_path:
        s = analyze(std_path)
        if s['seg'] and d['seg']:
            a = d['segs'][0].startswith('**【')
            b = s['segs'][0].startswith('**【')
            if a != b:
                p.append('段标题形态与标杆不一致：标杆是 %s，本文件是 %s'
                         % ('**【X、…】**' if b else '**X、…**',
                            '**【X、…】**' if a else '**X、…**'))
    print('%s' % d['name'])
    print('  H1=%d H2=%d H3=%d 段标题=%d 小标签=%d ```=%d CRLF=%d'
          % (d['h1'], d['h2'], d['h3'], d['seg'], d['tag'], d['fences'], d['crlf']))
    if p:
        for x in p:
            print('  ✗ ' + x)
    else:
        print('  ✓ 格式合规')
    return not p

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--std':
        std(args[1])
    else:
        ok = True
        for f in args:
            ok = check(f) and ok
        sys.exit(0 if ok else 1)
