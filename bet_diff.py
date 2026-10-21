#!/usr/bin/env python3
"""BET地址差分分析：对比两个快照，找随BET变化的地址"""
import sys

def load(path):
    with open(path, 'rb') as f:
        return f.read()

if len(sys.argv) != 3:
    print(f"用法: {sys.argv[0]} <snap_bet0.bin> <snap_bet5.bin>")
    sys.exit(1)

a = load(sys.argv[1])
b = load(sys.argv[2])
base = 0x1F0000

print(f"快照大小: {len(a)} vs {len(b)}")
print("\n变化的地址 (值从x变为y):")
count = 0
for i in range(min(len(a), len(b))):
    if a[i] != b[i]:
        addr = base + i
        # 重点关注：值变化符合BET特征的（0->5，或小数值）
        marker = ""
        if a[i] == 0 and b[i] == 5:
            marker = " <== BET 0->5 候选!"
        elif a[i] < 10 and b[i] < 15:
            marker = " (小数值)"
        print(f"  0x{addr:06X}: 0x{a[i]:02X}({a[i]:3d}) -> 0x{b[i]:02X}({b[i]:3d}){marker}")
        count += 1
        if count > 50:
            print("  ... (超过50个，只显示前50)")
            break
print(f"\n共 {count} 个地址发生变化")
