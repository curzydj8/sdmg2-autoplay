#!/bin/bash
echo "========================================="
echo "  彻底清理环境与释放底层设备..."
echo "========================================="
pkill -9 -f '/usr/games/mame' 2>/dev/null
pkill -9 -f 'tools/main.py' 2>/dev/null
pkill -9 -f 'game_agent' 2>/dev/null
pkill -9 -f 'local_ai_controller' 2>/dev/null
sleep 1
# 释放uinput（需sudo，可能失败则跳过）
sudo modprobe -r uinput 2>/dev/null
sudo modprobe uinput 2>/dev/null
sudo chmod 666 /dev/uinput 2>/dev/null
# 清MAME锁
rm -f ~/.mame/*.lock 2>/dev/null
rm -f ~/mame/*.lock 2>/dev/null
rm -f /tmp/sdmg2_ai.lock /tmp/sdmg2_launcher.lock
find ~/sdmg2-test -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
sleep 1
echo "[✔] 环境已重置"
echo "========================================="
export DISPLAY=:0
echo "启动 MAME..."
cd ~/mame && nohup /usr/games/mame sdmg2 -rompath ~/mame/roms -window > /tmp/mame.log 2>&1 &
sleep 6
pgrep -f '/usr/games/mame' > /dev/null && echo "[✔] MAME已启动" || { echo "[✘] MAME失败"; cat /tmp/mame.log | head -5; exit 1; }
echo "启动 AI..."
cd ~/sdmg2-test && nohup python3 -u tools/main.py > /tmp/autobot.log 2>&1 &
sleep 3
pgrep -f 'tools/main.py' > /dev/null && echo "[✔] AI已启动" || { echo "[✘] AI失败"; exit 1; }
echo "========================================="
