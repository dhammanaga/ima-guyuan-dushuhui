#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载第八轮 精修4周版 读书会01-14 全部 md 到本地 src/读书会NN/"""
import json, os, urllib.parse, subprocess, sys

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "dhammanaga/ima-guyuan-dushuhui"
BASE = "交付成果/第八轮去禅修引导/精修4周版"


def api(path):
    u = f"https://api.github.com/repos/{REPO}/contents/" + urllib.parse.quote(path) + "?ref=main"
    for _ in range(5):
        r = subprocess.run(["curl", "-s", "--max-time", "90", "-H",
                            "Authorization: Bearer " + TOKEN, u], capture_output=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            continue
    raise RuntimeError("api fail " + path)


def raw(path, out):
    u = f"https://api.github.com/repos/{REPO}/contents/" + urllib.parse.quote(path) + "?ref=main"
    for _ in range(5):
        r = subprocess.run(["curl", "-s", "--max-time", "120", "-H",
                            "Authorization: Bearer " + TOKEN,
                            "-H", "Accept: application/vnd.github.raw", u], capture_output=True)
        if r.stdout and (b"404" not in r.stdout[:40]) and len(r.stdout) > 2000:
            open(out, "wb").write(r.stdout)
            return len(r.stdout)
    return 0


def main():
    dirs = {x["name"].split("_")[0][-2:]: x["name"] for x in api(BASE) if x["type"] == "dir"}
    want = sys.argv[1:] or [f"{i:02d}" for i in range(1, 15)]
    root = "/sandbox/workspace/src"
    for nn in want:
        d = dirs[nn]
        files = [x for x in api(BASE + "/" + d) if x["type"] == "file" and x["name"].endswith(".md")]
        os.makedirs(os.path.join(root, "读书会" + nn), exist_ok=True)
        for f in sorted(files, key=lambda x: x["name"]):
            out = os.path.join(root, "读书会" + nn, f["name"])
            if os.path.exists(out) and os.path.getsize(out) == f["size"]:
                print("skip", nn, f["name"]); continue
            n = raw(BASE + "/" + d + "/" + f["name"], out)
            print(nn, f["name"], n, "OK" if n == f["size"] else "MISMATCH")
        print("--- 读书会%s: %d 文件 (dir=%s)" % (nn, len(files), d))


if __name__ == "__main__":
    main()
