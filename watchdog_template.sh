#!/usr/bin/env bash
# 看门狗模板：沙箱存活期内守护可脚本化长任务（进程级崩溃自愈）
# 注意：容器回收时本脚本一并消亡——这只防进程级崩溃，容器级回收由《守护协议》第三/四节兜底
# 用法: bash watchdog_template.sh <进程匹配关键字> <启动命令> [日志文件]

set -u
PROC_KEY="${1:?需要进程匹配关键字，如 make_dushuhui}"
START_CMD="${2:?需要启动命令}"
LOG_FILE="${3:-/sandbox/workspace/watchdog_run.log}"
WATCH_LOG="/sandbox/workspace/watchdog_自身日志_$(date +%Y%m%d_%H%M%S).log"
INTERVAL=300   # 每5分钟检查一次

start_task() {
  echo "$(date '+%F %T') [看门狗] 启动任务: $START_CMD" >> "$WATCH_LOG"
  nohup bash -c "$START_CMD" >> "$LOG_FILE" 2>&1 &
}

is_running() {
  pgrep -f "$PROC_KEY" > /dev/null 2>&1
}

# 首次启动
if ! is_running; then
  start_task
fi

while true; do
  sleep $INTERVAL
  if is_running; then
    echo "$(date '+%F %T') [看门狗] 进程存活(关键字=$PROC_KEY)" >> "$WATCH_LOG"
  else
    echo "$(date '+%F %T') [看门狗] 进程失活！检查原因并重启..." >> "$WATCH_LOG"
    echo "----- 日志尾部(原因线索) -----" >> "$WATCH_LOG"
    tail -30 "$LOG_FILE" >> "$WATCH_LOG" 2>/dev/null || echo "(无日志文件 $LOG_FILE)" >> "$WATCH_LOG"
    echo "----- 重启 -----" >> "$WATCH_LOG"
    start_task
  fi
done
