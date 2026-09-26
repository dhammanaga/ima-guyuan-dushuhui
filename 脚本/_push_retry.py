#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带重试的 GitHub Contents API 推送（中文路径），相对路径=仓库路径。"""
import os, sys, time, json, base64, urllib.request, urllib.parse, urllib.error

OWNER_REPO = "dhammanaga/ima-guyuan-dushuhui"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = f"https://api.github.com/repos/{OWNER_REPO}/contents"


def api(method, url, payload=None, tries=6):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, method=method)
            req.add_header("Authorization", f"token {TOKEN}")
            req.add_header("Accept", "application/vnd.github+json")
            data = None
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")
                req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, data=data, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = e
        except Exception as e:
            last = e
        time.sleep(2 + k * 3)
    raise last


def get_sha(gh_path):
    r = api("GET", API + "/" + gh_path)
    return r.get("sha") if r else None


def push(local):
    with open(local, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    rel = os.path.relpath(local).replace(os.sep, "/")
    gh_path = urllib.parse.quote(rel)
    sha = get_sha(gh_path)
    payload = {"message": f"docs: {rel}", "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    r = api("PUT", API + "/" + gh_path, payload)
    return r["content"]["path"], ("更新" if sha else "新建")


def main():
    files = sys.argv[1:]
    ok = 0
    for f in files:
        if not os.path.isfile(f):
            print("⚠️ 缺失", f); continue
        try:
            p, act = push(f)
            print(f"✅ {act} {p}", flush=True)
            ok += 1
        except Exception as e:
            print(f"❌ {os.path.basename(f)}: {e}", flush=True)
        time.sleep(0.3)
    print(f"汇总 {ok}/{len(files)}")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
