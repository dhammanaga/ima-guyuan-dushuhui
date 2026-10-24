#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git Data API 推送：112 份 4周版 docx + 3 个脚本（必须带 base_tree，PATCH ref 重试 5 次）"""
import os, sys, json, glob, base64, subprocess, time, urllib.parse

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "dhammanaga/ima-guyuan-dushuhui"
API = f"https://api.github.com/repos/{REPO}"


def req(method, url, payload=None, raw=None):
    cmd = ["curl", "-s", "-X", method, "--max-time", "120", "--retry", "3",
           "-H", "Authorization: Bearer " + TOKEN,
           "-H", "Accept: application/vnd.github+json",
           "-H", "Content-Type: application/json"]
    if payload is not None:
        tmp = "/tmp/_payload.json"
        open(tmp, "w").write(json.dumps(payload))
        cmd += ["--data-binary", "@" + tmp]
    cmd.append(url)
    for attempt in range(5):
        r = subprocess.run(cmd, capture_output=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            if attempt == 4:
                raise RuntimeError(f"{method} {url} -> {r.stdout[:200]!r}")
            time.sleep(2 + attempt * 2)


def make_blob(path):
    data = open(path, "rb").read()
    return req("POST", API + "/git/blobs",
               {"content": base64.b64encode(data).decode(), "encoding": "base64"})["sha"]


def main(msg, manifest):
    ref = req("GET", API + "/git/ref/heads/main")
    head = ref["object"]["sha"]
    tree_sha = req("GET", API + "/git/commits/" + head)["tree"]["sha"]
    print("head", head[:8], "tree", tree_sha[:8])

    entries = []
    for local, remote in manifest:
        sha = make_blob(local)
        entries.append(dict(path=remote, mode="100644", type="blob", sha=sha))
        print("  blob", remote.split("/")[-1], sha[:8])
    new_tree = req("POST", API + "/git/trees", {"base_tree": tree_sha, "tree": entries})
    commit = req("POST", API + "/git/commits",
                 {"message": msg, "tree": new_tree["sha"], "parents": [head]})
    print("commit", commit["sha"])
    for attempt in range(5):
        r = req("PATCH", API + "/git/refs/heads/main", {"sha": commit["sha"], "force": False})
        if isinstance(r, dict) and r.get("object", {}).get("sha") == commit["sha"]:
            print("ref updated ->", commit["sha"][:8], "attempt", attempt + 1)
            break
        print("patch retry", attempt + 1, str(r)[:160])
        time.sleep(3 + attempt * 3)
    else:
        raise SystemExit("PATCH ref 失败 5 次")
    json.dump({"commit": commit["sha"], "files": len(entries)},
              open("/sandbox/workspace/work/last_commit.json", "w"))


if __name__ == "__main__":
    msg = sys.argv[1]
    man = []
    for line in open(sys.argv[2], encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        local, remote = line.split("|", 1)
        man.append((local, remote))
    print("待推", len(man), "个文件")
    main(msg, man)
