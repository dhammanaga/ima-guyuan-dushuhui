# -*- coding: utf-8 -*-
r"""
push_via_api.py —— 坏索引仓库的推送通道（2026-10-12 实战沉淀）

【为什么需要这个】
本仓库有文件名含 ASCII 直引号（Windows 非法字符），导致：
  1. `git clone` / `git checkout` 报 `unable to checkout working tree`
  2. `git reset` / `git read-tree` 报 `invalid path ... "思即是业"...`
  3. 索引里堆约 5200 条假删除 → **`git commit -a` 会真删掉整个仓库**
所以推送一律走 GitHub REST API，完全不碰本地索引。

【用法】
1. 文件清单（一行一个仓库内相对路径）写入 files.txt
   行首加 `-` 表示**删除远端该路径**（用于重命名场景，例：`-旧路径.md`）
2. commit message 写入 msg.txt
3. 运行：python push_via_api.py files.txt msg.txt

【原理】
  POST /git/blobs  （每个文件一个 blob，sha 自校验，代理转码会当场发现）
  → POST /git/trees   （base_tree = 远端当前 tree，只提交列出的路径）
  → POST /git/commits （parents = 远端当前 commit）
  → PATCH /git/refs/heads/main（force=false，fast-forward 保护）

【安全要点】
- ✅ 绝不 git commit / commit -a / add -A（会连带提交 5200 条假删除）
- ✅ payload 一律 ensure_ascii=True，中文走 \uXXXX 防 GBK 乱码
- ✅ 用 curl 子进程，不用 urllib（代理会转码 urllib 响应）
- ✅ 每个 blob 的 sha 与本地 hash-object 逐个比对，转码即报错
- ⚠️ Trees API 的 content 字段不接受 base64 文本，必须先走 Blob API 拿 sha
"""
import base64, hashlib, json, os, subprocess, sys, time

REPO = "dhammanaga/ima-guyuan-dushuhui"
GCM = r"D:\Program Files\WorkBuddy\resources\vendor\PortableGit\mingw64\bin\git-credential-manager.exe"
PROXY = "http://127.0.0.1:7892"
API = "https://api.github.com"
# ⚠️ 载荷文件统一加 _pushapi_ 前缀，避免与手工 curl 查询（如 _ref.json）撞名覆盖
TMP = "D:/tmp/_pushapi_"


def token():
    r"""取 token：优先读明文 ~/.git-credentials（快且不会挂），
    GCM 仅作兜底 —— ⚠️ 2026-10-13 实测 GCM 在后台非交互下会永久挂起
    （输入 'protocol=https\nhost=github.com\n\n' 时 timeout 124），
    故绝不可把它当首选通道。"""
    cred = os.path.join(os.path.expanduser("~"), ".git-credentials")
    if os.path.exists(cred):
        import re as _re
        for ln in open(cred, encoding="utf-8").read().splitlines():
            m = _re.match(r"https://[^:]+:([^@]+)@github\.com", ln.strip())
            if m:
                return m.group(1)
    # 兜底：GCM（加超时，防止永久挂起）
    try:
        out = subprocess.run([GCM, "get"], input="protocol=https\nhost=github.com\n\n",
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=20)
    except subprocess.TimeoutExpired:
        raise SystemExit("GCM 超时挂起，且 ~/.git-credentials 中无可用 token")
    for ln in out.stdout.splitlines():
        if ln.startswith("password="):
            return ln[9:].strip()
    raise SystemExit("取不到 token")


TOK = token()


def curl(args, data=None):
    cmd = ["curl", "-s", "--proxy", PROXY, "-H", "Authorization: Bearer " + TOK,
           "-H", "Accept: application/vnd.github+json", "--max-time", "120"]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@" + data]
    cmd += args
    r = subprocess.run(cmd, capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    # 代理可能转码，改用 bytes 严格解码
    try:
        txt = r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        txt = r.stdout.decode("utf-8", "replace")
    try:
        return json.loads(txt)
    except Exception:
        return {"_raw": txt[:400], "_bytes": len(r.stdout)}


def git(*a):
    return subprocess.run(["git", "-C", r"D:\tmp\repo"] + list(a),
                          capture_output=True).stdout.decode("utf-8", "replace")


def main():
    files = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    dels = [f[1:].strip() for f in files if f.startswith("-")]
    ups = [f for f in files if not f.startswith("-")]
    print("待推送 %d 个文件（新增/更新 %d，删除 %d）\n" % (len(ups) + len(dels), len(ups), len(dels)))

    # 1. 拿远端最新 commit + tree
    branch = curl([f"{API}/repos/{REPO}/git/ref/heads/main"])
    if "object" not in branch:
        print("!! 取 branch 失败：", str(branch)[:300]); return 1
    head_sha = branch["object"]["sha"]
    c = curl([f"{API}/repos/{REPO}/git/commits/{head_sha}"])
    base_tree = c["tree"]["sha"]
    print("远端 HEAD = %s  tree = %s\n" % (head_sha[:10], base_tree[:10]))

    # 2. 逐文件建 blob
    entries = []
    for f in ups:
        full = os.path.join(r"D:\tmp\repo", f.replace("/", os.sep))
        if not os.path.exists(full):
            print("  ?? 本地不存在，跳过：%s" % os.path.basename(f)); continue
        raw = open(full, "rb").read()
        blob_sha = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
        payload = json.dumps({"content": base64.b64encode(raw).decode(), "encoding": "base64"},
                             ensure_ascii=True)
        pf = TMP + "_blob.json"
        open(pf, "w", encoding="ascii").write(payload)
        res = curl([f"{API}/repos/{REPO}/git/blobs"], data=pf)
        if "sha" not in res:
            print("  !! blob 失败 %s：%s" % (os.path.basename(f), str(res)[:160])); continue
        if res["sha"] != blob_sha:
            print("  !! sha 不符（代理转码？）%s: %s != %s" % (os.path.basename(f), res["sha"][:8], blob_sha[:8]))
        entries.append({"path": f, "mode": "100644", "type": "blob", "sha": res["sha"]})
        print("  ✓ %-46s %8d字节 %s" % (os.path.basename(f)[:44], len(raw), res["sha"][:8]))

    if not entries and not dels:
        print("\n没有可提交的 blob，中止。"); return 1

    # 2.5 删除条目：sha=null 即从 tree 中移除该路径（Git Trees API 官方删除语法）
    for f in dels:
        entries.append({"path": f, "mode": "100644", "type": "blob", "sha": None})
        print("  ✗ 删除远端 %s" % f)

    # 3. 建 tree
    payload = json.dumps({"base_tree": base_tree, "tree": entries}, ensure_ascii=True)
    open(TMP + "_tree.json", "w", encoding="ascii").write(payload)
    tree = curl([f"{API}/repos/{REPO}/git/trees"], data=TMP + "_tree.json")
    if "sha" not in tree:
        print("\n!! tree 失败：", str(tree)[:300]); return 1
    print("\n新 tree = %s （改动 %d 项）" % (tree["sha"][:10], len(entries)))

    # 4. 建 commit
    msg = open(sys.argv[2], encoding="utf-8").read() if len(sys.argv) > 2 else "update"
    payload = json.dumps({
        "message": msg,
        "tree": tree["sha"],
        "parents": [head_sha],
        "author": {"name": "dhammanaga", "email": "dhammanaga@users.noreply.github.com",
                   "date": "2026-10-12T18:10:00+08:00"},
        "committer": {"name": "dhammanaga", "email": "dhammanaga@users.noreply.github.com",
                      "date": "2026-10-12T18:10:00+08:00"},
    }, ensure_ascii=True)
    open(TMP + "_commit.json", "w", encoding="ascii").write(payload)
    commit = curl([f"{API}/repos/{REPO}/git/commits"], data=TMP + "_commit.json")
    if "sha" not in commit:
        print("!! commit 失败：", str(commit)[:300]); return 1
    print("新 commit = %s" % commit["sha"][:10])

    # 5. 更新 ref
    payload = json.dumps({"sha": commit["sha"], "force": False}, ensure_ascii=True)
    open(TMP + "_ref.json", "w", encoding="ascii").write(payload)
    ref = curl([f"{API}/repos/{REPO}/git/refs/heads/main"], data=TMP + "_ref.json")
    if ref.get("object", {}).get("sha", "")[:10] != commit["sha"][:10]:
        print("!! 更新 ref 失败：", str(ref)[:300]); return 1
    print("\n✅ 推送完成 → %s@main = %s" % (REPO, commit["sha"][:10]))
    print("https://github.com/%s/commit/%s" % (REPO, commit["sha"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())