#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHANGELOG 追加 A 批 Word 条目（4周版 01–14，112 份）"""
import re, subprocess, datetime

P = "/sandbox/workspace/repo/CHANGELOG.md"
s = open(P, encoding="utf-8").read()

now = subprocess.run(["date", "+%Y-%m-%d %H:%M"], env={"TZ": "Asia/Shanghai", "PATH": "/usr/bin:/bin"},
                     capture_output=True, text=True).stdout.strip()

lines = s.split("\n")
assert lines[0].startswith('<div align="right">')
lines[0] = ('<div align="right">📅 最近更新：%s　｜第八轮 · Word 版重出 A 批'
            '（4周版 读书会01–14，112 份）</div>' % now)
s = "\n".join(lines)

ENTRY = """## 第八轮 · Word 版重出 · A 批（4周版 读书会01–14，112 份，2026-10-25）

**触发**：尊者指令「A 批 · 4周版 01–14：先修两处脚本缺陷，再生成 112 份 Word 并逐份过门禁」。

**开工前修脚本（渲染／验证双侧同步，缺一即差异互相看不见）**：
- **P1 层级上限**：`_mk_word_latest.py` 知识地图代码块 `min(pre//4, 4)` → `min(pre//4, 8)`；`verify_md_docx.py` 解析侧同改 8，docx 侧 `p_kind` 层级判定放宽到 `0<=lvl<=8`。修复前两侧同截断至 4，5 级以上层级被压平且**验证不可见**；修复后读书会10 第1周 level 5（2 条）双侧逐条可比。
- **P2 奇数 `**` 预处理**：两侧统一 `prep_bold()`——本行 `**` 为奇数且下一行含 `**` → 合并两行为一段再解析；否则删除本行「两两配对后落单」的 `**`（保留文字与已成对加粗）。全库命中 14 处（06 第1周 2+2、06 第3周 3+3、11 第4周 2+2），处理后 **读书会06 第1周 Word 正文零字面 `**`**（验收项）。
- **附带修正**：`verify_word.py` 页眉周次原硬编码「第1周」，改为按文件名解析（否则第 2–4 周必然 FAIL）；补第 **10 项「无自动编号」**（`numPr=0`），12 项齐全。

**范围与结果**：读书会01–14（4周版）× 4 周 × 主持人版/学员版 = **112 份**；落位 `交付成果/第八轮去禅修引导/Word版/4周版/`（平铺）；页眉「读书会NN · 第N周 · 第八轮（第8版）（4周版） · 主持人版|学员版」。**页数 12–23 页/份，合计 1858 页**。

**门禁（112 份逐份，全 PASS）**：
- `verify_word.py` **12 项全 PASS**（页面/边距、Normal 字体、首行标题 20pt 居中、字号集、配色唯一、页眉文案、页脚 PAGE 域、引用块三属性、表格样式、无自动编号、无 md 残留、不嵌图）；
- `verify_md_docx.py` **一致性差异 0**（顺序／类型／层级／编号／文本／加粗／表格逐格）；
- **numPr = 0**；**字体仅 宋体／Times New Roman／微软雅黑**；
- **md 残留 0**（`**`、`<!--`、```` ``` ````、行首 `#`、表格行 `|` 全部为 0）。

**留档豁免（源文合法字符，非残留，未改 md）**：①每份 1 个 `|`＝时间戳行「📅 最近更新…　|　第N轮…」的分隔符；②读书会10 第3周主持人版正文讲排版规则的字面「### ／##」5 个 `#`（行内引用，非行首标记）。

**异常**：无。生成过程中发现并修正 3 类渲染缺陷（见上 P1/P2 与 verify_word 硬编码），修正后 112 份一次性全绿；无单份豁免、无重跑。

**commit**：`1415efaf`（112 份 docx ＋ 3 个脚本）。

---

"""

anchor = "## 第八轮 · 学员版内容净化 · 第二批"
assert s.count(anchor) == 1
s = s.replace(anchor, ENTRY + anchor)
open(P, "w", encoding="utf-8").write(s)
print("CHANGELOG updated, 首行:", s.split("\n")[0])
