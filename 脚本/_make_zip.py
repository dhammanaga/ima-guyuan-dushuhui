#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_make_zip.py — 打包资料包为 zip（UTF-8 文件名防乱码）
用法: python3 _make_zip.py <源目录> <输出zip路径>
"""
import os
import sys
import zipfile

def main():
    if len(sys.argv) < 3:
        print("用法: python3 _make_zip.py <源目录> <输出zip路径>"); return 1
    src, out = sys.argv[1], sys.argv[2]
    if not os.path.isdir(src):
        print(f"❌ 源目录不存在: {src}"); return 1
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(src):
            for f in sorted(files):
                p = os.path.join(root, f)
                arc = os.path.relpath(p, os.path.dirname(os.path.abspath(src)))
                z.write(p, arc)   # Python3 自动以 UTF-8 编码文件名并置 0x800 标志位
                n += 1
    print(f"✅ 已打包 {n} 个文件 -> {out}（{os.path.getsize(out)/1024:.0f} KB）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
