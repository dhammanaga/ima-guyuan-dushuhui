# -*- coding: utf-8 -*-
"""
final_check.py —— 尊者手动编辑后的四项必查（count_spoken.py 一个都不查）

用法：python final_check.py <文件.md> [<文件.md> …]
"""
import re
import sys
import os

PAT_ENT = re.compile(r'&#x[0-9A-Fa-f]+;|&amp;|&lt;|&gt;|&quot;')
XF = ['愿我此功德，导向诸漏尽！', '愿我此功德，为证涅槃缘！',
      '我此功德分，回向诸有情！', '愿彼等一切，同得功德分！']
BAD_XF = re.compile('愿以此功德|愿此善缘成熟|愿正见灯灯相续')


def check(path):
    b = open(path, 'rb').read()
    s = b.decode('utf-8')
    name = os.path.basename(path)
    problems = []

    # ① 换行符：必须是 CRLF 且无裸 LF
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n')
    bare = sum(1 for i, c in enumerate(b) if c == 0x0A and (i == 0 or b[i - 1] != 0x0D))
    nl_ok = (crlf == lf and bare == 0)
    if not nl_ok:
        problems.append('① 换行符：CRLF=%d LF=%d 裸LF=%d → 全文件统一为 CRLF'
                        % (crlf, lf, bare))

    # ② HTML 实体：混入朗读字数却不显示
    ents = PAT_ENT.findall(s)
    if ents:
        import html
        problems.append('② HTML 实体 %d 处：%s → html.unescape() 还原'
                        % (len(ents), sorted(set(html.unescape(x) for x in ents))))

    # ③ EXT_READ 定界标记：学员版派生脚本依赖它（已被删除过两次）
    op = s.count('<!--EXT_READ-->')
    cl = s.count('<!--/EXT_READ-->')
    if op != 1 or cl != 1:
        problems.append('③ EXT_READ 标记 %d/%d → 须为 1/1（学员版派生依赖）' % (op, cl))

    # ④ U+FFFD 编码损坏：count_spoken.py 不检测
    n_ff = s.count('\ufffd')
    if n_ff:
        problems.append('④ U+FFFD 编码损坏 %d 处 → 需还原为正确汉字' % n_ff)

    # ⑤ 时间戳：第 1 行「📅 最近更新：YYYY-MM-DD HH:MM」必须与文件 mtime 同期
    #    尊者反复强调：任何改稿后必须更新时间戳。此项由 --fix-stamp 自动改。
    m = re.search(r'📅\s*最近更新：\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', s)
    if not m:
        problems.append('⑤ 缺时间戳：第 1 行须为 '
                        '<div align="right">📅 最近更新：YYYY-MM-DD HH:MM　|　第5版精修（朗读优化版）</div>')
    else:
        import datetime
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        want_d, want_t = mt.strftime('%Y-%m-%d'), mt.strftime('%H:%M')
        got_d, got_t = m.group(1), m.group(2)
        # 允许 0 分钟差（同分钟内编辑）；超过 2 分钟即视为未更新
        delta = abs((mt - datetime.datetime.strptime(
            '%s %s' % (got_d, got_t), '%Y-%m-%d %H:%M')).total_seconds()) / 60
        if delta > 2:
            problems.append('⑤ 时间戳未更新：文件内 %s %s，文件最后修改 %s %s'
                            '（差 %.0f 分钟）→ 须改为「📅 最近更新：%s %s」'
                            % (got_d, got_t, want_d, want_t, delta, want_d, want_t))

    # ⑥ 代码块围栏（```）必须成对：未闭合会把后面所有 ## 标题吞进代码块，
    #    导致 GitHub 目录只剩前几个环节（2026-10-15 实际发生）
    fences = [i + 1 for i, ln in enumerate(s.split('\n')) if ln.strip().startswith('```')]
    if len(fences) % 2 != 0:
        problems.append('⑥ 代码块围栏 ``` 共 %d 个（行 %s）→ 奇数个未闭合；'
                        '未闭合的代码块会吞掉其后的全部 ## 标题，GitHub 目录会缺失环节'
                        % (len(fences), fences))

    # 附：节内混用 ## 会让 count_spoken 字数静默归零（skill §15.7）
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'cs', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'count_spoken.py'))
    try:
        cs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cs)
        for sec, body in cs.sections(s):
            n, _, _ = cs.spoken(body)
            if n < 500:
                h2 = re.findall(r'(?m)^## (?!📖).*', body)
                problems.append('附·%s 字数仅 %d（<500）——疑似节内混用 ## 导致统计失效；'
                                '节内段标题须用 **【…】**，见 skill §15.7%s'
                                % (sec, n, ('；节内 ## 行：' + ' / '.join(x[:24] for x in h2[:3])) if h2 else ''))
    except Exception as e:
        problems.append('附·字数交叉校验未执行（%s）' % type(e).__name__)

    # 附：RULES5 三·七 回向词与收尾（脚本已查，但一并复核）
    n_xf = sum(s.count(x) for x in XF)
    if n_xf != 4:
        problems.append('附·回向词标准四句 = %d（应为 4）' % n_xf)
    if BAD_XF.search(s):
        problems.append('附·含自造回向文')
    if re.search(r'(?m)^### 收尾(?:一|二)', s):
        problems.append('附·收尾被拆成收尾一/二')
    if not re.search(r'(?m)^##\s*\U0001F5FA\s*本周知识地图', s):
        problems.append('附·缺「本周知识地图」节')
    if s.count('<div align="right">') != s.count('</div>'):
        problems.append('附·HTML div 标签不配对（会导致整篇右对齐）')

    print('=' * 70)
    print(name)
    if problems:
        for x in problems:
            print('  ✗ ' + x)
    else:
        print('  ✓ 五项必查 + 回向/收尾/地图/div 全部通过')
    return len(problems)


def fix_stamp(path, stamp=None):
    """把第 1 行时间戳改为指定时间（默认取当前时间）。

    ★尊者铁律：任何改稿后必须更新时间戳。用法：
        python final_check.py --fix-stamp <文件.md> [<文件.md> …]
    只替换「📅 最近更新：YYYY-MM-DD HH:MM」这一段，其余字节不动
    （避免 [^<]* 之类的正则吃掉 '　|　第5版精修' 分隔符，见 skill §11）。
    """
    import datetime
    if stamp is None:
        stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    raw = open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.replace('\r\n', '\n').split('\n')
    m = re.search(r'(📅\s*最近更新：\s*)\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', lines[0])
    if not m:
        print('  ✗ %s 第 1 行无时间戳，无法自动修（须手工补）' % os.path.basename(path))
        return 1
    old = lines[0]
    lines[0] = old[:m.start()] + m.group(1) + stamp + old[m.end():]
    open(path, 'w', encoding='utf-8', newline='').write(nl.join(lines))
    print('  ✓ %s  时间戳 → %s' % (os.path.basename(path), stamp))
    return 0


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--fix-stamp':
        rest = args[1:]
        stamp = None
        if rest and rest[0].startswith('--at='):
            stamp = rest[0][5:]
            rest = rest[1:]
        files = []
        for a in rest:
            if os.path.isdir(a):
                files += [os.path.join(a, f) for f in sorted(os.listdir(a)) if f.endswith('.md')]
            else:
                files.append(a)
        if not files:
            print('用法：python final_check.py --fix-stamp [--at=YYYY-MM-DD HH:MM] <文件.md|目录> …')
            sys.exit(2)
        rc = 0
        for f in files:
            rc += fix_stamp(f, stamp)
        sys.exit(1 if rc else 0)
    if not args:
        print('用法：python final_check.py <文件.md|目录> [<文件.md|目录> …]')
        print('      也接受目录参数（自动扫描该目录下所有 *.md）')
        print('      自动修时间戳：python final_check.py --fix-stamp <文件.md|目录> …')
        sys.exit(2)
    # 目录参数 → 展开为该目录下的 *.md
    files = []
    for a in args:
        if os.path.isdir(a):
            files.extend(sorted(
                os.path.join(a, f) for f in os.listdir(a) if f.endswith('.md')))
        else:
            files.append(a)
    total = 0
    for f in files:
        total += check(f)
    print()
    print('共 %d 个文件，待修 %d 项' % (len(files), total))
    sys.exit(1 if total else 0)