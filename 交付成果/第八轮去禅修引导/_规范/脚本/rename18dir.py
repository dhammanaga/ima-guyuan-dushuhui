# -*- coding: utf-8 -*-
"""读书会18 目录改名：…_4周资料包（第5版）→ …_4周资料包（第6版）
GitHub 无 move 端点 → Trees API：base_tree=当前 main tree，
新路径复用原 blob sha，旧路径显式 sha:null 删除。文件内容零改动。"""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error

REPO = "dhammanaga/ima-guyuan-dushuhui"
REPO_DIR = r"C:\Users\27659\AppData\Local\Temp\dsh\dsrepo"
API = "https://api.github.com"
PROXY = "http://127.0.0.1:7892"
TMP = "D:/tmp/_pushapi_"

OLD = "交付成果/第六轮改写版/精修4周版/读书会18_大念处经精读_4周资料包（第5版）"
NEW = "交付成果/第六轮改写版/精修4周版/读书会18_大念处经精读_4周资料包（第6版）"
MSG = ("读书会18 目录改名：精修4周版 4周资料包（第5版）→（第6版）\n\n"
       "整目录 18 个条目（4 份主持人版 md ＋ 14 张课件原图 jpg）路径由「第5版」改为「第6版」，\n"
       "文件内容与 blob sha 全部保持不变（零字节改动），仅路径变更。\n"
       "第1周已于上一提交 3737119 换入尊者朗读底本，本提交仅改名。")

_opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))


def token():
    # 凭据格式：https://<user>:<token>@github.com
    for ln in open(os.path.expanduser("~/.git-credentials"), encoding="utf-8"):
        ln = ln.strip()
        if "github.com" not in ln or "@" not in ln:
            continue
        userinfo = ln.split("://", 1)[1].split("@", 1)[0]
        if ":" in userinfo:
            t = userinfo.split(":", 1)[1].strip()
            if t:
                return t
    raise SystemExit("no token")


TOK = token()


def curl(path, data=None, method=None):
    url = API + path
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "push")
    if data is not None:
        b = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
        req.data = b
    for a in range(4):
        try:
            with _opener.open(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:400]
            if e.code in (502, 503, 504) and a < 3:
                time.sleep(3); continue
            raise SystemExit("HTTP %s %s\n%s" % (e.code, path, body))
    raise SystemExit("curl failed " + path)


# ── 1. 取当前 main 与 tree ──
head = curl("/repos/%s/git/ref/heads/main" % REPO)["object"]["sha"]
print("远端 HEAD =", head[:10])
c = curl("/repos/%s/git/commits/%s" % (REPO, head))
base_tree = c["tree"]["sha"]
print("base tree =", base_tree[:10])

# ── 2. 列出旧目录全部 blob（含 sha）──
entries = []
out = subprocess.run(["git", "-C", REPO_DIR, "ls-tree", "-r", head, OLD],
                     capture_output=True).stdout.decode()
for ln in out.splitlines():
    meta, path = ln.split("\t", 1)
    mode, typ, sha = meta.split()
    entries.append((path, sha))
assert entries, "旧目录为空"
print("旧目录条目 %d 个" % len(entries))
for p, s in entries:
    assert p.startswith(OLD + "/"), p
    assert NEW not in p

# ── 3. 构造 tree：旧路径置 null + 新路径复用 sha ──
tree = []
for p, s in entries:
    tree.append({"path": p, "mode": "100644", "type": "blob", "sha": None})
    tree.append({"path": p.replace(OLD, NEW, 1), "mode": "100644",
                 "type": "blob", "sha": s})
payload = {"base_tree": base_tree, "tree": tree}
open(TMP + "_tree_rename.json", "w", encoding="utf-8").write(json.dumps(payload))
res = curl("/repos/%s/git/trees" % REPO, data=payload)
new_tree = res["sha"]
print("新 tree =", new_tree[:10], "（改名必然改变 tree sha，属预期）")

# 校验：新 tree 递归展开后，新路径齐全、旧路径清零、条目总数不变
nt = curl("/repos/%s/git/trees/%s?recursive=1" % (REPO, new_tree))
paths = {e["path"] for e in nt["tree"] if e["type"] == "blob"}
new_ones = {p.replace(OLD, NEW, 1) for p, _ in entries}
old_ones = {p for p, _ in entries}
assert new_ones <= paths, "新路径缺失: %s" % (new_ones - paths)
assert not (old_ones & paths), "旧路径残留: %s" % (old_ones & paths)
print("✅ 校验通过：新路径 %d 条齐全，旧路径 0 条残留，远端 blob 总数 %d（改名前 %d）"
      % (len(new_ones), len(paths), len(paths) - len(new_ones) + len(old_ones)))
for p, s in entries:
    got = next(e["sha"] for e in nt["tree"] if e["path"] == p.replace(OLD, NEW, 1))
    assert got == s, "sha 变了：%s %s→%s" % (p, s, got)
print("✅ 全部 18 个 blob sha 与改名前逐一相同（文件内容零改动）")

# ── 4. commit + 更新 ref ──
cm = {"message": MSG, "tree": new_tree, "parents": [head]}
open(TMP + "_commit_rename.json", "w", encoding="utf-8").write(json.dumps(cm))
commit = curl("/repos/%s/git/commits" % REPO, data=cm)
print("新 commit =", commit["sha"][:10])

rf = {"sha": commit["sha"], "force": False}
curl("/repos/%s/git/refs/heads/main" % REPO, data=rf, method="PATCH")
print("\n✅ 改名完成 → %s@main = %s" % (REPO, commit["sha"][:10]))
print("https://github.com/%s/commit/%s" % (REPO, commit["sha"]))
