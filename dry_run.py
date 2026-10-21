#!/usr/bin/env python3
"""Dry Run: 只读不写，验证Lua→JSON→Python链路"""
import time, json

STATE_FILE = "/tmp/sdmg2_state.json"

print("=== Dry Run: 监控内存数据 ===")
print("按Ctrl+C退出\n")

last = None
while True:
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        time.sleep(0.5)
        continue
    
    hand = state.get('hand', [])
    # 只在变化时打印
    key = tuple(hand)
    if key != last:
        last = key
        hex_hand = ' '.join(f'{b:02X}' for b in hand)
        print(f"手牌: {hex_hand}  BET={state.get('bet')} CREDIT={state.get('credit')}")
    
    time.sleep(0.3)
