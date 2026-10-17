#!/bin/bash
# AI稳定版 - 超级大满贯II自主循环
# 注意：去掉c键（sdmg2按C会崩溃，ID 03543）
export DISPLAY=:0
export XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.U3HSW3
WID=8388613
SHOT=/tmp/ai-stable.png
TILES=(k l m a e f b d g h i j)
log() { echo "$(date +%H:%M:%S) $1" >> /tmp/ai-stable.log; }
i=0
log "AI稳定版启动（Xorg回滚后重建，已移除C键防崩溃）"
while true; do
  MYUID=$(id -u)
  export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$MYUID/bus"
  timeout 25 python3 /tmp/portal_screenshot.py $SHOT >/dev/null 2>&1
  if [ ! -f $SHOT ]; then log "截图失败"; sleep 5; continue; fi
  RESULT=$(python3 /tmp/local_vision.py $SHOT 2>/dev/null)
  PHASE=$(echo $RESULT | cut -d" " -f1)
  if [ "$PHASE" = "ODDS" ]; then
    xdotool key --delay 100 --window $WID 5 2>/dev/null; sleep 0.5
    xdotool key --delay 100 --window $WID 3 2>/dev/null; sleep 0.5
    xdotool key --delay 100 --window $WID 1 2>/dev/null
    log "ODDS开局"
  elif [ "$PHASE" = "EXCHANGE" ]; then
    for k in k l m a e; do xdotool key --delay 100 --window $WID $k 2>/dev/null; sleep 0.4; done
    log "换牌"
  elif [ "$PHASE" = "MAIN" ]; then
    xdotool key --delay 100 --window $WID n 2>/dev/null; sleep 1
    tile=${TILES[$((i % 12))]}
    xdotool key --delay 100 --window $WID $tile 2>/dev/null
    log "MAIN N+$tile"
    i=$((i+1))
  else
    log "UNKNOWN"
  fi
  sleep 3
done
