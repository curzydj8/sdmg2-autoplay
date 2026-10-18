#!/usr/bin/env python3
"""
Lua主流程 - 纯Lua输入，计数法
不依赖内存读数，不依赖视觉识别
"""
import sys
import time
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from lua_bridge import send_action, press_coin, press_bet, press_start

def main():
    print("=== Lua主流程启动 ===")
    
    # 1. 上分：按15次COIN（确保CREDIT充足）
    print("步骤1: 上分 (15次 COIN)...")
    for i in range(15):
        press_coin()
        time.sleep(0.3)
    print("上分完成")
    time.sleep(1)
    
    # 2. 押注：按10次BET（Lua 100%可靠，无需验证）
    print("步骤2: 押注 (10次 BET)...")
    for i in range(10):
        press_bet()
        time.sleep(0.3)
    print("押注完成 (BET应为10)")
    time.sleep(1)
    
    # 3. 开始：按5次START
    print("步骤3: 开始游戏 (5次 START)...")
    for i in range(5):
        press_start()
        time.sleep(0.5)
    print("开始指令已发送")
    
    print("=== 主流程完成 ===")
    print("注意：游戏应已开始，请检查画面")

if __name__ == "__main__":
    main()
