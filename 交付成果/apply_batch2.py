# -*- coding: utf-8 -*-
import docx
from docx import Document

SRC = "读书会_修订版_引用替换_第一批.docx"
DST = "读书会_修订版_引用替换_第二批.docx"

# Real media_ids from KB (前缀_d0dd1c0cd17209afe241ece24bf6b7b4_真实40hex)
M = {
 'out18': 'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_e3ca6a9f0b4e0ef0e1f2f147618899007439961422831605',
 'bj10':  'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_48be730fc7b37233e47786d4d2deaad27439996142231605',
 'zgs8':  'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_2fd660aaae951407543b768554ad31ea37439996142231605',
 'zgs12': 'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_2ba605763034eb2b0864b0128a02f8f27439996142231605',
 'da20':  'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_b5f6de581ed6430c71120b7caa00019e7439961422831605',
 'da21':  'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_db84877571aa0cef443e8a4092ac28ca7439961422831605',
 'jw191': 'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_fceb94bd963f6fc53f4bace57593f57f7439961422831605',
 'jw192': 'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_2385595da537142bbeb7fa68fba159f77439996142231605',
 's194':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_1ae80881c1fde1e512c5658ff38cd3197439961422831605',
 'sy1':   'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_a0dd78e67fe37024e83b92503ce1a8b97439996142231605',
 'sy4':   'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_8adbb537b06a267c7c882702050eb66d7439961422831605',
 'sy10':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_cd931faef6603f58fd64f8f7a5b70eed7439961422831605',
 'sy20':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_f44e9641ff0c00ed3a854f958dd9ead77439996142231605',
 'sy21':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_fd09c488b3c749a9581e0140e062c16c7439961422831605',
 'sy22':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_1689674a8c8f8377cada6208e4b0c13d7439961422831605',
 'sy25':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_245d4e7ddb3099a4c26e05fdbc39433e7439961422831605',
 'sy34':  'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_6576e951937f29485ad107f6cb2924c37439996142231605',
 'sy36':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_d8c00607e96356765584d6ff83b7d0f47439996142231605',
 'sy37':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_f47e9924ffc594032799670c9c3a6c9a7439961422831605',
 'sy46':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b4_408bda6e0457370e7c498b4ea115feba7439961422831605',
 'sy45':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_f88278556e333cc4b7067d652e2186697439961422831605',
 'sy60':  'pdf_d0dd1c0cd17209afe241ece24bf6b7b4_680fc50f9dbcb54df9f50b0a78021d71743996142231605',
 'sy20s': 'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_f490a09764d9ff10f4260c8a2ca059f47439996142231605',
 'p13':   'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_01b146670d6ba490e3c3b188ae6941877439961422831605',
 'p23':   'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_f5beb568f10918e38b0ff5e0fa5b19aa7439961422831605',
 'p81':   'word_d0dd1c0cd17209afe241ece24bf6b7b7b4_76a81259305d0220abe6938e678d4a0f7439961422831605',
 'p57':   'pdf_d0dd1c0cd17209afe241ece24bf6b7b7b4_98c15852ac89dc63f7972ceb5332eab67439996142231605',
 's24t1': 'soundrecording_d0dd1c0cd17209afe241ece24bf6b7b7b4_52ff5a81be26a6baa65493ff6942bad77439961422831605',
}

doc = Document(SRC)

def setrun(p, idx, text):
    p.runs[idx].text = text

# ---------------- 读书会01 ----------------
# W5 共读原文 (135)
p = doc.paragraphs[135]
t = p.runs[1].text
t = t.replace('「如来禅修学体系介绍29」（media_id: 如来禅修学体系介绍29-20240711）、',
              '「2024百花古寺禅修营13-大念处经讲记10-古源尊者-20240217」（media_id: %s）；' % M["bj10"])
t = t.replace('「18_入出息念」（media_id: 18_入出息念-20240701）',
              '「18_入出息念-古源尊者-20240701」（media_id: %s）' % M["out18"])
p.runs[1].text = t
assert '如来禅修学体系介绍29' not in p.text, "01W5 still has wrong ref"

# W6 共读原文 (151)
p = doc.paragraphs[151]
t = p.runs[1].text
t = t.replace('「188讲-法念处-五盖2」（media_id: 188讲-法念处-五盖2-20220106）、',
              '「止观前行实修营8-舍离五盖1-20220501」（media_id: %s）；「止观前行实修营12-舍离五盖5-20220511」（media_id: %s）；'
              % (M["zgs8"], M["zgs12"]))
p.runs[1].text = t
assert '188讲-法念处-五盖2' not in p.text, "01W6 共读原文 still has 188讲"

# W6 延伸阅读 (163)
p = doc.paragraphs[163]
p.runs[0].text = ('media_id: %s（止观前行实修营8-舍离五盖1-古源尊者-20220501）；'
                  'media_id: %s（止观前行实修营12-舍离五盖5-古源尊者-20220511）'
                  % (M["zgs8"], M["zgs12"]))
assert '188讲-法念处-五盖2' not in p.text, "01W6 延伸阅读 still has 188讲"

# ---------------- 读书会06 ----------------
# W7 共读原文 (864): run2/run3 = 四念处3-大念处经讲记2 (correct, keep); run4/run5 = 大念处经讲记28 (wrong, fix)
p = doc.paragraphs[864]
p.runs[4].text = 'media_id: %s' % M["da20"]
p.runs[5].text = ('（2024百花古寺禅修营23-大念处经讲记20-古源尊者-20240227）；'
                  'media_id: %s（2024百花古寺禅修营24-大念处经讲记21-古源尊者-20240228）' % M["da21"])
assert '大念处经讲记28' not in p.text, "06W7 共读原文 still has 讲记28"
# W7 延伸阅读 (880)
p = doc.paragraphs[880]
p.runs[0].text = ('media_id: %s（2024百花古寺禅修营23-大念处经讲记20-古源尊者-20240227）；'
                  'media_id: %s（2024百花古寺禅修营24-大念处经讲记21-古源尊者-20240228）'
                  % (M["da20"], M["da21"]))
p.runs[1]._element.getparent().remove(p.runs[1]._element)
assert '大念处经讲记28' not in p.text, "06W7 延伸阅读 still has 讲记28"
# W8 共读原文 (883)
p = doc.paragraphs[883]
p.runs[2].text = 'media_id: %s' % M["da20"]
p.runs[3].text = ('（2024百花古寺禅修营23-大念处经讲记20-古源尊者-20240227）；'
                  'media_id: %s（2024百花古寺禅修营24-大念处经讲记21-古源尊者-20240228）' % M["da21"])
assert '大念处经讲记28' not in p.text, "06W8 共读原文 still has 讲记28"

# ---------------- 读书会07 ----------------
# W5 共读原文 (987)
p = doc.paragraphs[987]
p.runs[2].text = 'media_id: %s' % M["jw191"]
p.runs[3].text = ('（191讲-十二处2&七觉支1-古源尊者）中关于念觉支、择法觉支的部分；'
                  'media_id: %s（192讲-七觉支2-古源尊者）中关于择法、精进、喜觉支的部分' % M["jw192"])
assert '193讲' not in p.text, "07W5 共读原文 still has 193讲"
# W5 延伸阅读 (1003)
p = doc.paragraphs[1003]
p.runs[0].text = ('media_id: %s（191讲-十二处2&七觉支1-古源尊者）；'
                  'media_id: %s（192讲-七觉支2-古源尊者）' % (M["jw191"], M["jw192"]))
p.runs[1]._element.getparent().remove(p.runs[1]._element)
assert '193讲' not in p.text, "07W5 延伸阅读 still has 193讲"

# ---------------- 读书会12 ----------------
# W1 共读原文 (1724)
p = doc.paragraphs[1724]
p.runs[2].text = 'media_id: %s' % M["sy1"]
p.runs[3].text = ('（古源尊者24缘释义第1讲）中关于二十四缘概述的部分；'
                  'media_id: %s（第4讲-摄缘-缘概说4-古源尊者-20220731共修版）中帕奥九组56缘分类的部分；以及' % M["sy4"])
assert '24缘教学01' not in (p.runs[2].text + p.runs[3].text), "12W1 still has 24缘教学01 in new runs"
# W2 共读原文 (1745)
p = doc.paragraphs[1745]
p.runs[2].text = 'media_id: %s' % M["sy10"]
p.runs[3].text = ('（第10讲-摄缘-因缘1-古源尊者-20220918共修版）中关于因缘的部分；以及'
                  'media_id: %s（第13讲-摄缘-所缘缘2-古源尊者-20221023共修版）中关于所缘缘的部分；以及' % M["p13"])
assert '24缘教学01' not in p.text
# W3 共读原文 (1765)
p = doc.paragraphs[1765]
p.runs[4].text = 'media_id: %s' % M["sy20"]
p.runs[5].text = ('（第20讲-摄缘-俱生缘1-古源尊者-20221225共修版）中关于俱生缘的部分；以及'
                  'media_id: %s（第21讲-摄缘-俱生缘2-古源尊者-20230101共修版）中关于俱生缘的段落' % M["sy21"])
assert '第17讲' not in p.text, "12W3 still has 第17讲"
# W4 共读原文 (1785)
p = doc.paragraphs[1785]
p.runs[2].text = 'media_id: %s' % M["sy22"]
p.runs[3].text = '（第22讲-摄缘-相互缘-古源尊者-20230108共修版）中关于相互缘的部分；以及'
p.runs[4].text = 'media_id: %s' % M["p23"]
p.runs[5].text = ('（第23讲-摄缘-依止缘1-古源尊者-20230115共修版）中关于依止缘的部分；以及'
                  'media_id: %s（第25讲-摄缘-亲依止缘1-古源尊者-20230205共修版）中关于亲依止缘的部分；以及'
                  'media_id: %s（第34讲-摄缘-亲依止缘10-古源尊者-20230409）中关于亲依止缘（善法可能成为不善法缘）的部分'
                  % (M["sy25"], M["sy34"]))
assert '关于相互缘的部分' in p.text and '第13讲-摄缘-所缘缘2' not in p.text, "12W4 相互缘 not fixed"
# W5 共读原文 (1806)
p = doc.paragraphs[1806]
p.runs[2].text = 'media_id: %s' % M["sy36"]
p.runs[3].text = ('（第36讲-摄缘-前生缘-古源尊者-20230423共修版）中关于前生缘的部分；以及'
                  'media_id: %s（第37讲-摄缘-后生缘-古源尊者-20230430共修版）中关于后生缘的部分' % M["sy37"])
for ridx in (5, 4):
    r = p.runs[ridx]
    r._element.getparent().remove(r._element)
assert '第57讲' not in p.text and '24缘教学01' not in p.text, "12W5 still has 第57讲/24缘教学01"
# W6 共读原文 (1826)
p = doc.paragraphs[1826]
p.runs[4].text = 'media_id: %s' % M["sy46"]
p.runs[5].text = '（第46讲-摄缘-异熟缘-古源尊者-20230709共修版）中关于果报缘（异熟缘）的段落'
assert '第39讲' not in p.text, "12W6 still has 第39讲"
# W8 共读原文 (1868)
p = doc.paragraphs[1868]
p.runs[3].text = ('（24缘教学01-20190802-Bhante Ven.Uttama）中关于二十四缘整体回顾的部分；以及'
                  'media_id: %s（第60讲-摄缘-诸缘的分组方法-古源尊者-20231022共修版）中诸缘分组方法与56缘的部分；以及'
                  'media_id: %s（古源尊者24缘释义第20讲-24缘总说）中关于二十四缘总结的部分；以及'
                  % (M["sy60"], M["sy20s"]))

# ---------------- 读书会08 W5 编辑事故修复 ----------------
from docx.oxml import OxmlElement
from copy import deepcopy
def set_para_full(p, text):
    # rebuild paragraph with a single run, preserving run0 formatting if present
    src_rpr = None
    if p.runs:
        try:
            src_rpr = deepcopy(p.runs[0]._element.get_or_add_rPr())
        except Exception:
            src_rpr = None
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    new_r = OxmlElement('w:r')
    if src_rpr is not None:
        new_r.append(src_rpr)
    t = OxmlElement('w:t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    new_r.append(t)
    p._p.append(new_r)

set_para_full(doc.paragraphs[1154], '你最近一次强烈的“想要”是什么？它属于欲爱、有爱还是无有爱？')
set_para_full(doc.paragraphs[1155], '如果渴爱暂时止息，你的心是什么状态？')
set_para_full(doc.paragraphs[1156], '在日常生活中，哪一种渴爱最常操控你的选择？')
for idx in (1161, 1160, 1159, 1158, 1157):
    el = doc.paragraphs[idx]._element
    el.getparent().remove(el)
ref = doc.paragraphs[1156]
h_template = doc.paragraphs[1153]  # Heading 4 (讨论引导)
c_template = doc.paragraphs[1154]  # Compact
def insert_after(ref_p, text, template_p):
    ref_el = ref_p._element if hasattr(ref_p, '_element') else ref_p
    new_p = OxmlElement('w:p')
    tpr = template_p._p.get_or_add_pPr()
    new_p.append(deepcopy(tpr))
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    new_p.append(r)
    ref_el.addnext(new_p)
    return new_p
ref = insert_after(ref, "主持人提示", h_template)
ref = insert_after(ref, "主持人只念出问题，不做解读，也不急着给答案——把思考与体悟的空间留给每位参与者。", c_template)
ref = insert_after(ref, "每题请控制在8–10分钟，可用计时器计时；若冷场，主持人先分享一个自己的真实例子带起气氛，但不要把话题引向抽象义理争辩。", c_template)
ref = insert_after(ref, "如有人把话题引向比较或评判，温和地拉回原文与自身经验：“我们这次只观察自己的渴爱。”", c_template)
ref = insert_after(ref, "延伸阅读（课后自由选读）", h_template)
ref = insert_after(ref, 'media_id: %s（194讲-摄集-摄菩提分-法念处-四圣谛2-古源尊者）' % M["s194"], c_template)

doc.save(DST)
print("SAVED", DST)
