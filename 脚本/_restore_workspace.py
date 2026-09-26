#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_restore_workspace.py — 工作区一键恢复脚本（守护协议·第五节）
用途：沙箱容器被回收后，从 GitHub 恢复全部任务文件。
数据源：dhammanaga/ima-guyuan-dushuhui (main) zipball
用法：
  python3 _restore_workspace.py          # 正常恢复（目标已完好则提示跳过）
  python3 _restore_workspace.py --force  # 强制重建（旧目录改名保留，不删除）
依赖：GITHUB_TOKEN 环境变量（经 env_manage 持久化）；git 协议不可达，走 zipball。
"""
import os
import sys
import io
import json
import shutil
import urllib.request
import zipfile
import datetime

OWNER_REPO = "dhammanaga/ima-guyuan-dushuhui"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TARGET = "/sandbox/workspace/新型读书会.大佛寺/第二轮"
KEY_FILE = "任务需求文档"          # 判断目标是否完好的关键文件前缀
ZIPBALL_URL = f"https://api.github.com/repos/{OWNER_REPO}/zipball/{BRANCH}"

def log(msg):
    print(f"[{datetime.datetime.now():%F %T}] {msg}", flush=True)

def http_get(url):
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()

def target_ok():
    """目标目录是否存在且含关键文件"""
    if not os.path.isdir(TARGET):
        return False
    for name in os.listdir(TARGET):
        if name.startswith(KEY_FILE):
            return True
    return False

def main():
    force = "--force" in sys.argv

    if target_ok() and not force:
        log(f"目标目录已完好（{TARGET}），跳过恢复。如需强制重建请加 --force")
        return 0

    if force and os.path.isdir(TARGET):
        bak = TARGET + f"_旧_{datetime.datetime.now():%Y%m%d_%H%M%S}"
        shutil.move(TARGET, bak)
        log(f"旧目录已改名保留: {bak}")

    log(f"下载 {ZIPBALL_URL} ...")
    data = http_get(ZIPBALL_URL)
    log(f"下载完成: {len(data)/1024:.0f} KB")

    os.makedirs(TARGET, exist_ok=True)
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = zf.namelist()
    root = names[0].split("/")[0]
    log(f"归档根目录: {root}，文件 {len(names)} 个")
    zf.extractall(TARGET)   # 解出 TARGET/<root>/...

    # 将 <root>/ 下内容上移一层
    inner = os.path.join(TARGET, root)
    for item in os.listdir(inner):
        shutil.move(os.path.join(inner, item), os.path.join(TARGET, item))
    os.rmdir(inner)

    if target_ok():
        log("恢复成功 ✅ 目标目录: " + TARGET)
        # 列出关键目录
        for sub in sorted(os.listdir(TARGET)):
            p = os.path.join(TARGET, sub)
            if os.path.isdir(p):
                n = len(os.listdir(p))
                log(f"  📁 {sub}/ ({n} 项)")
            else:
                log(f"  📄 {sub}")
        log("提示：恢复后请按《守护协议》第三节唤醒自检 SOP 继续（读任务需求文档→定位断点→核素材蓝图→续跑）")
        return 0
    else:
        log("恢复失败 ❌ 目标目录缺少关键文件，请人工检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())
