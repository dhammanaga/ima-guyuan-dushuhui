#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_del_gh.py — 删除 GitHub 仓库中的文件（Contents API DELETE）
用法: python3 _del_gh.py <仓库相对路径>
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error

OWNER_REPO = "dhammanaga/ima-guyuan-dushuhui"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = f"https://api.github.com/repos/{OWNER_REPO}/contents"

def req(method, url, payload=None):
    r = urllib.request.Request(url, method=method)
    r.add_header("Authorization", f"token {TOKEN}")
    r.add_header("Accept", "application/vnd.github+json")
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, data=data, timeout=60) as resp:
        return json.loads(resp.read().decode())

def main():
    if len(sys.argv) < 2:
        print("用法: python3 _del_gh.py <仓库相对路径>"); return 1
    rel = sys.argv[1]
    gp = urllib.parse.quote(rel)
    try:
        info = req("GET", f"{API}/{gp}?ref={BRANCH}")
    except urllib.error.HTTPError as e:
        print(f"❌ 读取失败 HTTP {e.code}: {e.read().decode()[:200]}"); return 1
    sha = info.get("sha")
    try:
        req("DELETE", f"{API}/{gp}", {"message": f"chore: remove {rel}", "sha": sha, "branch": BRANCH})
        print(f"✅ 已删除: {rel}")
        return 0
    except urllib.error.HTTPError as e:
        print(f"❌ 删除失败 HTTP {e.code}: {e.read().decode()[:200]}"); return 1

if __name__ == "__main__":
    sys.exit(main())
