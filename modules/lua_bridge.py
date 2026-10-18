"""MAME Lua直控桥接 - Python端
通过 /tmp/mame_action.json 向MAME发送动作，无需uinput，无视窗口焦点。
"""
import json
import os
import time

ACTION_PATH = "/tmp/mame_action.json"

def send_action(action):
    """发送动作到MAME，action如 'COIN', 'BET', 'START', 'A'-'N'"""
    # 等待上一个动作被消费（文件被清空）
    for _ in range(20):
        try:
            with open(ACTION_PATH, "r") as f:
                content = f.read().strip()
            if content in ("{}", ""):
                break
        except:
            pass
        time.sleep(0.05)
    
    # 写入新动作
    with open(ACTION_PATH, "w") as f:
        json.dump({"action": action}, f)
    
    # 等待被消费
    time.sleep(0.2)
    return True

# 快捷函数
def press_coin(): return send_action("COIN")
def press_bet(): return send_action("BET")
def press_start(): return send_action("START")
def press_tile(t): return send_action(t.upper())  # 'a'-'n'

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        send_action(sys.argv[1].upper())
        print(f"已发送: {sys.argv[1].upper()}")
