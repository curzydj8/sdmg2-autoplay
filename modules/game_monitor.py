#!/usr/bin/env python3
"""
游戏运行检测与状态机 v1.0

本地AI使用：检测MAME进程、游戏窗口、识别阶段
"""
import os
import subprocess


# 游戏阶段定义
PHASES = {
    "MAME_NOT_RUNNING": {"id": 0, "desc": "MAME未启动"},
    "MAME_STARTING": {"id": 1, "desc": "MAME启动中"},
    "GAME_BOOT": {"id": 2, "desc": "游戏启动画面"},
    "TITLE_MENU": {"id": 3, "desc": "标题菜单"},
    "ODDS": {"id": 4, "desc": "赔率界面"},
    "CREDIT": {"id": 5, "desc": "上分/信用分界面"},
    "BET": {"id": 6, "desc": "押分选择"},
    "EXCHANGE": {"id": 7, "desc": "换牌阶段"},
    "PLAY": {"id": 8, "desc": "打牌阶段"},
    "SETTLEMENT": {"id": 9, "desc": "结算阶段"},
    "DOUBLEUP": {"id": 10, "desc": "比倍阶段"},
    "GAME_OVER": {"id": 11, "desc": "游戏结束"},
    "UNKNOWN": {"id": 99, "desc": "未知"},
}


def check_mame_running():
    """检查MAME进程（兼容手动启动）"""
    try:
        r = subprocess.run(
            ["pgrep", "-f", "mame"],
            capture_output=True, text=True, timeout=5)
        return bool(r.stdout.strip())
    except:
        return False


def start_mame():
    """启动MAME（已验证命令）"""
    cmd = "cd ~/mame && /usr/games/mame sdmg2 -rompath ~/mame/roms -window > /tmp/mame.log 2>&1 &"
    os.system(cmd)
    print("[GameMonitor] MAME启动命令已发送")


def get_phase():
    """
    识别当前阶段（简化版，需接入screen_db完善）
    返回：(phase_name, confidence)
    """
    if not check_mame_running():
        return "MAME_NOT_RUNNING", 1.0
    # TODO: 截图识别具体阶段
    return "UNKNOWN", 0.3


if __name__ == "__main__":
    print(f"MAME运行中: {check_mame_running()}")
    print(f"当前阶段: {get_phase()}")
