# 超级大满贯II 本地AI 新架构设计

**日期**：2026-10-17
**目标**：理解整个系统后重新梳理，替代补丁式修复

## 一、游戏完整流程（实测）

```
ODDS屏
  │ 按1（开始）/ 按3（押分）
  ▼
换牌阶段（选0-13张 + Enter确认）
  │
  ▼
打牌循环
  │ 摸牌（自动）→ 选手牌（a-n）→ Enter确认
  │ 重复直到胡牌/流局
  ▼
结算屏（显示番数/得分）
  │
  ▼
比倍？（Right Shift进入）
  │ 大=Enter / 小=Backspace
  │ 可继续或停止
  ▼
回到ODDS屏
```

## 二、核心设置（已验证）

| 设置 | 值 | 影响 |
|------|-----|------|
| Credit Limit | 2000 | 上分上限 |
| Double Up Jackpot | 500 | 比倍奖池上限 |
| Minimum Bet | 1 | 最小押分 |
| Key-In Rate | 10 | 上分比率 |

## 三、完整键位（MAME截图）

**牌操作**：A-N选槽位，Enter确认
**吃碰杠**：Space=吃，LAlt=碰，LCtrl=杠，LShift=立直，Z=荣
**比倍**：RShift=比倍，Enter=大，Backspace=小
**分数**：RCtrl=取分（疑似退分），4=赔付，3=押分
**系统**：1=开始，5=投币，9=显示信用

## 四、新架构：四层分离

```
┌─────────────────────────────────────┐
│ 感知层 Perception                      │
│ - screenshot()                       │
│ - detect_phase() → ODDS/EXCHANGE/    │
│   PLAY/SETTLEMENT/DOUBLEUP           │
│ - recognize_hand() → 牌编码+置信度    │
│ - read_credit() → 信用分              │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 决策层 Decision                       │
│ - 规则查询：当前阶段允许什么动作       │
│ - 策略选择：打哪张/押多少/比不比      │
│ - 输入：GameState，输出：Action       │
│ - 不直接操作硬件                     │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 执行层 Execution                      │
│ - press(key)：uinput单键             │
│ - discard(slot)：选中+确认           │
│ - 动作后验证：截图对比               │
│ - 超时/失败处理                      │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 记录层 Recording                      │
│ - SQLite：对局/动作/状态/结算        │
│ - 日志文件：/tmp/sdmg2_ai.log        │
│ - 截图存档：异常时保存               │
└─────────────────────────────────────┘
```

## 五、模块重组

**保留**（已验证）：
- `tile_codec.py`：编码转换
- `winning_db.py`：胡牌判定
- `fan_db.py`：番数计算
- `target_config.py`：目标配置
- `settings_db.py`：DIP设置

**合并**（功能重叠）：
- `local_ai_controller.py` + `game_controller.py` + `player_v2.py` + `ai_loop.py`
  → 新 `game_agent.py`：唯一的游戏主循环
- `mahjong_vision.py` → 感知层
- `high_fan_strategy.py` + `exchange_strategy.py` + `mahjong_strategy.py`
  → 新 `strategy.py`：统一策略接口

**删除**（过时）：
- `player.py`（旧版）
- `input_adapter.py`（discard缺enter）

## 六、状态机（核心）

```python
STATES = {
    'ODDS':       {'allow': ['credit', 'start', 'bet'], 'next': 'EXCHANGE'},
    'EXCHANGE':   {'allow': ['select', 'confirm'],      'next': 'PLAY'},
    'PLAY':       {'allow': ['discard'],                'next': 'SETTLEMENT'},
    'SETTLEMENT': {'allow': ['confirm'],                'next': 'DOUBLEUP|ODDS'},
    'DOUBLEUP':   {'allow': ['big', 'small', 'stop'],   'next': 'ODDS'},
}
```

每个状态：
- 进入条件（画面特征）
- 允许动作（白名单）
- 禁止动作（ODDS屏禁打牌键）
- 超时处理

## 七、关键修复清单

1. **状态识别**：ODDS vs PLAY用多特征，不只看亮度
2. **单实例**：文件锁+PID校验，原子操作
3. **按键**：补全a-m映射（已修）
4. **识别**：补模板到35/35，混淆矩阵验证
5. **下一局**：SETTLEMENT后自动回ODDS，按1开始
6. **比倍**：RShift进入，Enter大/Backspace小，按策略决定
7. **退分**：RCtrl待验证，先标记unknown

## 八、实施顺序

1. 先写 `game_agent.py` 新主循环（四层结构）
2. 迁移已验证逻辑（按键/配置/记录）
3. 补状态识别（ODDS/PLAY/SETTLEMENT）
4. 实测一局完整流程
5. 再补比倍/退分
6. 老模块标记deprecated，测试稳定后删除
