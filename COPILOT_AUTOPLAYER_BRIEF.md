# Copilot 任务书：超级大满贯Ⅱ 全自动AI (auto_player.py)

## 项目概述

为街机麻将游戏《超级大满贯Ⅱ》(sdmg2, IGS 1997) 编写全自动AI，通过内存直读感知游戏状态，用xdotool模拟按键实现无人值守自动打牌。

**架构**：MAME Lua桥接(感知) → Python状态机(决策) → xdotool(执行)

## 当前文件

- `~/auto_player.py` - 主程序 (Python)
- `/tmp/ai_reader2.lua` - MAME Lua桥接，每0.5秒写 `/tmp/sdmg2_state.json`
- `/tmp/sdmg2_state.json` - 状态文件：`{"hand":[14个字节], "bet":int, "credit":int, "phase":{...}}`

## 内存地址 (已验证)

| 地址 | 用途 | 编码 |
|------|------|------|
| 0x1F043F | 手牌起始 (14字节) | 万0x01-09, 筒0x11-19, 条0x21-29, 字0x31-37 |
| 0x1F0BB5 | BET (有残留问题，见下) | 整数 |
| 0x1F09FD | CREDIT | 整数 |

工作RAM: 0x1F0000-0x1FFFFF (64KB)，CPU=m68000大端

## 按键映射 (xdotool)

- `5` = 投币 (Coin)
- `3` = 押注 (Bet)
- `1` = 开始 (Start)
- `Return` = 确认/收分
- `a`-`n` = 打第1-14张牌

必须用 `xdotool key --window <WIN_ID> --clearmodifiers <key>` 发送，WIN_ID通过 `xdotool search --onlyvisible --class "mame"` 获取。uinput已被MAME过滤，不可用。

## 状态机逻辑 (decide_action)

```
ODDS画面 (手牌全零):
  credit==0 → coin (投币)
  bet<10 → bet (押注)
  bet>=10 → start (开始)

结算画面 (有牌, credit==0, bet==0):
  → collect (按Enter收分)

打牌中 (有牌):
  优先打字牌 (>=0x30)
  否则打第14张 (索引13)
  连续3次手牌无变化 → collect (防卡死，可能是胡/杠)
```

## 已知问题 (需要你修复)

### P0: BET地址残留
- 现象：游戏画面BET=0，但内存0x1F0BB5读到10 (上局残留)
- 影响：AI误判为"注满"，按1开始无反应，卡死
- 任务：重新扫描定位真正的BET地址
  - 方法：`/tmp/bet_scanner.lua` 每10秒dump内存到 `/tmp/bet_snap_N.bin`
  - 在BET=0和BET=5时各取一个快照
  - 用 `/tmp/bet_diff.py` 对比，找 0x00→0x05 变化的地址
  - 验证新地址随押注实时同步

### P1: 投注速度
- 当前一次按3次3键，约3-4秒到10注
- 可优化但别太快，MAME会丢键

### P2: 出牌策略
- 当前：字牌优先 → 兜底第14张
- 可升级：孤张识别、搭子保留、危险牌规避 (参考日本麻将AI启发式)

## 代码规范

- Python 3，无第三方依赖 (只用标准库+subprocess调xdotool)
- 所有按键走 `xdotool_key()` 函数
- 状态机保持纯函数 `decide_action(state)` 返回 `(action, param)`
- 关键决策加 `print` 日志
- 缩进4空格，无tab

## 测试方法

```bash
# 终端1：启动MAME+Lua桥接
/usr/games/mame sdmg2 -rompath ~/roms -window -autoboot_script /tmp/ai_reader2.lua &

# 终端2：运行AI
python3 -u ~/auto_player.py
```

观察日志：`感知 CREDIT:x BET:y` 应与游戏画面同步，动作应依次为 coin→bet→start→discard循环。

## 交付标准

1. 修复P0后，BET感知与画面100%同步，连续跑10局无卡死
2. 代码有注释，关键分支说明原因
3. 不引入新依赖，不改MAME配置，不写游戏内存 (只读)
