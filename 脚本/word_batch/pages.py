#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx → pdf → 页数统计（4 并行，独立 UserInstallation）"""
import os, glob, json, subprocess, concurrent.futures, shutil, tempfile

OUT = "/sandbox/workspace/out"
PDF = "/sandbox/workspace/pdf"


def conv(args):
    idx, files = args
    prof = tempfile.mkdtemp(prefix="lo%d_" % idx)
    cmd = ["soffice", "--headless", "-env:UserInstallation=file://" + prof,
           "--convert-to", "pdf", "--outdir", PDF] + files
    subprocess.run(cmd, capture_output=True, timeout=1800)
    shutil.rmtree(prof, ignore_errors=True)
    return len(files)


def main():
    os.makedirs(PDF, exist_ok=True)
    files = sorted(glob.glob(os.path.join(OUT, "读书会*", "*.docx")))
    todo = [f for f in files
            if not os.path.exists(os.path.join(PDF, os.path.basename(f)[:-5] + ".pdf"))]
    print("待转", len(todo), "/", len(files))
    k = 4
    groups = [(i, todo[i::k]) for i in range(k) if todo[i::k]]
    with concurrent.futures.ThreadPoolExecutor(k) as ex:
        for n in ex.map(conv, groups):
            print("组完成", n)
    pages = {}
    for f in files:
        pdf = os.path.join(PDF, os.path.basename(f)[:-5] + ".pdf")
        try:
            out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
            pages[os.path.basename(f)] = int([l for l in out.split("\n") if l.startswith("Pages:")][0].split()[1])
        except Exception:
            pages[os.path.basename(f)] = None
    json.dump(pages, open("/sandbox/workspace/work/pages.json", "w"), ensure_ascii=False, indent=1)
    bad = [k for k, v in pages.items() if not v]
    print("页数统计", len(pages), "缺", bad[:5])


if __name__ == "__main__":
    main()
