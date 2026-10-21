#!/usr/bin/env python3
"""桌面版监督器：监控真实桌面上的 MAME 实例"""
import subprocess, time, json, os, sys
from datetime import datetime

SSH = "ssh -F /home/hatch/.ssh/config zhang-new"
CP_FILE = "/home/hatch/workspace/sdmg2-test/learning/checkpoints-desktop.json"

def ssh(cmd, timeout=30):
    r = subprocess.run(f"{SSH} '{cmd}'", shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def get_mame_pid():
    for _ in range(3):
        try:
            out = ssh("pgrep -f 'sdmg2754ca.*desktop' | head -1")
            pid = out.strip().split()[0] if out.strip() else ""
            if pid.isdigit():
                return pid
        except: pass
        time.sleep(5)
    return None

def save_checkpoint(data):
    with open(CP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

print(f"[{datetime.now()}] 桌面监督器启动", flush=True)
restarts = 0
while True:
    try:
        pid = get_mame_pid()
        if not pid:
            print(f"[{datetime.now()}] MAME 未运行，重启", flush=True)
            ssh("setsid /tmp/start-mame-desktop.sh < /dev/null > /dev/null 2>&1 &", timeout=15)
            restarts += 1
            time.sleep(20)
        else:
            # 检查进程是否真的在运行
            alive = ssh(f"ps -p {pid} -o pid 2>&1 | tail -1", timeout=15)
            if pid not in alive:
                print(f"[{datetime.now()}] PID {pid} 已退出", flush=True)
                restarts += 1
            else:
                print(f"[{datetime.now()}] MAME 运行中 PID={pid}", flush=True)
        
        save_checkpoint({
            "mame_pid": pid,
            "restarts": restarts,
            "last_check": datetime.now().isoformat(),
            "mode": "desktop",
        })
    except Exception as e:
        print(f"[{datetime.now()}] 异常: {e}", flush=True)
    time.sleep(60)
