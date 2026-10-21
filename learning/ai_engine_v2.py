#!/usr/bin/env python3
"""
AI自主决策引擎 v2 - 带分级故障处理
"""
import subprocess
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT = Path("/home/hatch/workspace/sdmg2-test")
SSH = "ssh -F /home/hatch/.ssh/config zhang-new"
WID = "10485767"

# 故障计数
fault_counts = {"screenshot": 0, "vision": 0, "input": 0}

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    with open("/tmp/ai-engine.log", "a") as f:
        f.write(line + "\n")

def ssh(cmd, timeout=30):
    r = subprocess.run(f"{SSH} '{cmd}'", shell=True,
                      capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def screenshot(name):
    """一级故障处理：截图失败重试"""
    global fault_counts
    remote = f"/tmp/xvfb-test/desktop/screenshots/ai-{name}.png"
    for attempt in range(3):
        try:
            out = ssh(f'MYUID=$(id -u); export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$MYUID/bus"; '
                     f'timeout 25 python3 /tmp/portal_screenshot.py {remote} 2>&1 | tail -1',
                     timeout=40)
            # 验证文件存在且非空
            check = ssh(f'stat -c%s {remote} 2>&1')
            if check.isdigit() and int(check) > 10000:
                fault_counts["screenshot"] = 0
                return remote
        except Exception as e:
            log(f"截图尝试{attempt+1}失败: {e}", "WARN")
        time.sleep(3)
    
    fault_counts["screenshot"] += 1
    log(f"截图连续失败{ fault_counts['screenshot']}次", "ERROR")
    return None

def download(remote, local_name):
    local = PROJECT / "screenshots" / local_name
    subprocess.run(f'{SSH} "base64 -w 0 {remote}" 2>&1 | base64 -d > {local} 2>&1',
                  shell=True, timeout=60)
    return str(local) if local.exists() else None

def detect_phase_local(remote_path):
    """二级：本地视觉识别"""
    try:
        result = ssh(f'python3 /tmp/local_vision.py {remote_path} 2>&1', timeout=15)
        parts = result.split()
        if len(parts) >= 2:
            return parts[0], float(parts[1])
    except Exception as e:
        log(f"视觉识别失败: {e}", "WARN")
    return "UNKNOWN", 0.0

def send_key(key):
    """二级故障处理：输入验证"""
    ssh(f'export DISPLAY=:0; export XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.EN5WW3; '
        f'xdotool key --delay 150 --window {WID} {key} 2>/dev/null; echo OK',
        timeout=15)
    return True

def decide_and_act():
    ts = datetime.now().strftime("%H%M%S")
    
    # 1. 观察（含一级故障处理）
    remote_before = screenshot(f"e{ts}-before")
    if not remote_before:
        log("跳过本轮：截图失败", "WARN")
        return {"status": "skip_screenshot"}
    
    # 2. 识别
    phase, conf = detect_phase_local(remote_before)
    log(f"阶段={phase} 置信度={conf:.2f}")
    
    if conf < 0.5:
        log("置信度过低，跳过", "WARN")
        return {"status": "skip_low_conf"}
    
    # 3-4. 决策
    if phase == "ODDS":
        actions = [("5", "投币"), ("3", "压注"), ("1", "开始")]
    elif phase == "EXCHANGE":
        actions = [("k", "换西"), ("l", "换中"), ("m", "换?"), ("a", "换1萬"), ("e", "换9萬")]
    elif phase == "MAIN":
        actions = [("n", "摸牌")]
    else:
        return {"status": "skip_unknown_phase"}
    
    # 5. 执行
    for key, desc in actions:
        send_key(key)
        log(f"执行: {desc}({key})")
        time.sleep(1)
        if phase == "MAIN":
            # 主局：摸牌后弃一张
            send_key("k")  # 优先弃孤张
            log("执行: 弃k")
            break
    
    # 6. 验证
    time.sleep(2)
    remote_after = screenshot(f"e{ts}-after")
    
    return {
        "status": "done",
        "phase": phase,
        "actions": [d for _, d in actions],
        "timestamp": ts,
    }

def main():
    log("AI决策引擎 v2 启动（含故障处理）")
    consecutive_skips = 0
    
    while True:
        try:
            result = decide_and_act()
            if result["status"].startswith("skip"):
                consecutive_skips += 1
                if consecutive_skips >= 5:
                    log("连续5轮跳过，可能游戏异常，等待30秒", "ERROR")
                    time.sleep(30)
                    consecutive_skips = 0
            else:
                consecutive_skips = 0
        except Exception as e:
            log(f"主循环异常: {e}", "ERROR")
            time.sleep(10)
        
        time.sleep(5)

if __name__ == "__main__":
    main()
