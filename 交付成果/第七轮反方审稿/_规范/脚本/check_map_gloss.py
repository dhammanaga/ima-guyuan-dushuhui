# -*- coding: utf-8 -*-
"""校验 v2：排除「分组标题行」（A. / B1 / 一、），只查真正的知识点条目是否带释义。"""
import re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'D:\tmp\repo\知识框架与要点'
HEAD = '### 2. 知识地图（层级框架）'
NEXT = '### 3. 总核心要点'

MARK = re.compile(r'[：＝]|——|（[^）]{4,}）|即|所谓|指|意为|如|非|·\s*\S{6,}')

def key_of(b):
    m = re.match(r'读书会(\d+)_', b)
    if m: return m.group(1)
    if '人生七阶段' in b: return 'X1'
    if '想蕴梳理' in b: return 'X2'
    return None

# 分组标题：A. / B1 / B1 xxx（W2） / 一、  等骨架行（不含释义，属分类骨架）
GROUP = re.compile(r'^[A-Z]\d*[\.、]?\s|^[一二三四五六七八九十]+、')

fs = sorted(f for f in glob.glob(os.path.join(BASE, '*.md'))
            if '核对报告' not in f and '_backup' not in f and not os.path.basename(f).startswith('_tmp'))

tn = tb = 0
for f in fs:
    b = os.path.basename(f); k = key_of(b)
    t = open(f, encoding='utf-8').read()
    i = t.find(HEAD); j = t.find(NEXT, i)
    m = re.search(r'```[a-z]*\n(.*?)```', t[i:j], re.S)
    code = m.group(1) if m else ''
    nodes = [l for l in code.split('\n') if re.search(r'[├└]─', l)]
    bare = []
    for l in nodes:
        txt = re.sub(r'^[│\s]*[├└]─\s*', '', l).strip()
        if GROUP.match(txt):      # 骨架行，跳过
            continue
        tn += 1
        if not MARK.search(txt) or len(txt) < 8:
            bare.append(txt[:80])
    tb += len(bare)
    if bare:
        print('%-4s %s' % (k, b[:52]))
        for x in bare:
            print('       └─ %s' % x)
print('-' * 100)
print('知识点条目 %d 个，疑似裸 %d 个' % (tn, tb))
