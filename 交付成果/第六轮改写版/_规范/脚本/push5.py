# -*- coding: utf-8 -*-
"""push5.py — 把 /sandbox/workspace/交付成果/第5版精修版/** 推到 GitHub
远端前缀：交付成果/第五轮精简版/**
用法: python3 push5.py [--all | <系列目录名关键字…>] [--message "…"]
  不给参数 = 推送全部已存在的（主持人版+图片，排除 _draft_/_meta_/_meta 目录）
"""
import os, sys, json, time, base64, urllib.request, urllib.parse, urllib.error

TOK = os.environ['GITHUB_TOKEN']
REPO = 'dhammanaga/ima-guyuan-dushuhui'
BRANCH = 'main'
LOCAL_ROOT = '/sandbox/workspace/交付成果/第5版精修版'
GH_PREFIX = '交付成果/第五轮精简版'
API = 'https://api.github.com/repos/' + REPO

def req(method, url, payload=None, raw=False, tries=5):
    data = json.dumps(payload).encode() if payload is not None else None
    for a in range(tries):
        try:
            r = urllib.request.Request(url, method=method, data=data)
            r.add_header('Authorization', 'Bearer ' + TOK)
            r.add_header('Accept', 'application/vnd.github+json')
            if data: r.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(r, timeout=120) as resp:
                b = resp.read()
                return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code in (404, 422): raise
            if a == tries-1: raise
            time.sleep(2)
        except Exception:
            if a == tries-1: raise
            time.sleep(2)

def list_files(keys):
    out = []
    for root, dirs, files in os.walk(LOCAL_ROOT):
        dirs[:] = [d for d in dirs if d not in ('_meta', '__pycache__')]
        for f in files:
            if f.startswith('_draft_') or f.startswith('_meta_') or f.endswith('.pdf'):
                continue
            if f.endswith('.py') and '_规范' not in root:
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, LOCAL_ROOT)
            if keys and not any(k in rel for k in keys):
                continue
            out.append((rel, p))
    return out

def main():
    args = sys.argv[1:]
    msg = 'docs: 第五轮精简版 上传'
    keys = []
    i = 0
    while i < len(args):
        if args[i] == '--message':
            msg = args[i+1]; i += 2
        elif args[i] == '--all':
            i += 1
        else:
            keys.append(args[i]); i += 1
    files = list_files(keys)
    print('待推送文件:', len(files), 'keys=', keys)
    # 1) base
    ref = req('GET', f'{API}/git/ref/heads/{BRANCH}')
    head = ref['object']['sha']
    commit = req('GET', f'{API}/git/commits/{head}')
    base_tree = commit['tree']['sha']
    tree = []
    for n, (rel, p) in enumerate(files, 1):
        with open(p, 'rb') as fh:
            content = base64.b64encode(fh.read()).decode()
        blob = req('POST', f'{API}/git/blobs', {'content': content, 'encoding': 'base64'})
        tree.append({'path': f'{GH_PREFIX}/{rel}', 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        if n % 40 == 0: print('  blobs', n)
    print('创建 tree…')
    new_tree = req('POST', f'{API}/git/trees', {'base_tree': base_tree, 'tree': tree})
    new_commit = req('POST', f'{API}/git/commits', {'message': msg, 'tree': new_tree['sha'], 'parents': [head]})
    req('PATCH', f'{API}/git/refs/heads/{BRANCH}', {'sha': new_commit['sha']})
    print('✅ 已推送', len(files), '个文件, commit', new_commit['sha'][:8])

if __name__ == '__main__':
    main()
