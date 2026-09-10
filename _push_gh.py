#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_push_gh.py — 通用 GitHub 推送脚本（Contents API）
用法: python3 _push_gh.py <本地文件1> <本地文件2> ...
  - 自动读取 GITHUB_TOKEN 环境变量
  - 中文路径自动 quote；分支 main；每文件间隔 0.4s
  - 文件已存在则先取 sha 再 PUT（更新）
  - 提交信息: "docs: <文件名>"
"""
import os
import sys
import time
import json
import base64
import urllib.request
import urllib.parse

OWNER_REPO = "dhammanaga/ima-guyuan-dushuhui"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = f"https://api.github.com/repos/{OWNER_REPO}/contents"

def log(msg):
    print(msg, flush=True)

def api_request(method, url, payload=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=data, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_sha(gh_path):
    """返回远端文件 sha；不存在返回 None"""
    try:
        r = api_request("GET", API + "/" + gh_path)
        return r.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def push(local_path):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    rel = os.path.relpath(local_path).replace(os.sep, "/")  # 保留相对路径（支持子目录）
    gh_path = urllib.parse.quote(rel)
    sha = get_sha(gh_path)
    payload = {"message": f"docs: {rel}", "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    try:
        r = api_request("PUT", API + "/" + gh_path, payload)
        log(f"✅ {rel} -> {r['content']['path']} ({'更新' if sha else '新建'})")
        return True
    except urllib.error.HTTPError as e:
        log(f"❌ {rel} 推送失败 HTTP {e.code}: {e.read().decode()[:200]}")
        return False

def main():
    files = sys.argv[1:]
    if not files:
        log("用法: python3 _push_gh.py <文件> [文件...]")
        return 1
    if not TOKEN:
        log("❌ 环境变量 GITHUB_TOKEN 未设置")
        return 1
    ok = 0
    for f in files:
        if not os.path.isfile(f):
            log(f"⚠️ 本地文件不存在，跳过: {f}")
            continue
        if push(f):
            ok += 1
        time.sleep(0.4)
    log(f"汇总: {ok}/{len(files)} 成功")
    return 0 if ok == len(files) else 1

if __name__ == "__main__":
    sys.exit(main())
