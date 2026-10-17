# 24小时持续运行测试

**开始时间**：2026-10-14 23:52 CST
**目标**：连续运行 ≥24 小时，之后继续直到用户叫停

## 运行组件

| 组件 | PID | 功能 | 状态 |
|------|-----|------|------|
| MAME | 46647 | 游戏本体 | ✅ 运行中 |
| autostart.sh | 54285 | 25秒/轮：5投币+3压注+1开始 | ✅ 运行中 |
| gameplay-24h.sh | 58855 | 5秒/轮：N摸牌+智能弃牌 | ✅ 运行中 |
| supervisor-desktop.py | 58801 | 60秒检查MAME进程 | ✅ 运行中 |

## 监控指标

- 游戏阶段识别：每30分钟截图一次
- 进程存活：supervisor每60秒检查
- 自动恢复：MAME退出后supervisor自动重启
- 学习记录：不清空，持续追加

## 中断记录

（待记录）

## 23:58 三级故障：游戏红屏卡死
- 现象：MAME窗口全红屏，持续10秒无变化
- 进程：PID 46647 仍存活（01:17:22）
- 截图：screenshots/upgrade-check.png, screenshots/red-check2.png
- 处理：重启MAME

## 00:00 故障恢复完成
- 新MAME PID：60595
- 状态：DONDEN 4，CREDIT=3，BET=1，正常对局
- 恢复方式：kill后重启，autostart自动开局
- 用时：约2分钟
- 学习记录保留完整
[05:53:40] Xorg切换：gdm3已配WaylandEnable=false，准备重启
[06:04:14] 用户批准第二次重启，切Xorg
