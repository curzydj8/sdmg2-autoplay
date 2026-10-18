# Copilot总任务：sdmg2全量输入与数据测绘

## 背景
- `ai_bridge.lua` 的 Lua ioport 直控已证实：`field:set_value()` 能改变端口值，但**不等于真实按键事件**
- A/B测试证实：uinput的KEY_3能让BET 0→1，Lua的set_value按住2秒端口255→223但画面不动
- COIN via Lua有效，BET via Lua无效——同一机制，效果不同

## 总目标
测出**所有按键**的Lua有效性、**所有牌**（A-N选牌键）的输入效果、以及**所有能拿到的数据**。

## 任务1：全按键Lua有效性矩阵

对 `ai_bridge.lua` 中 `ACTION_MAP` 的**每一个**动作，在隔离实例中测试Lua `set_value` 是否能让游戏响应：

| 动作 | 端口/字段 | 测试方法 | 判定标准 |
|------|-----------|----------|----------|
| COIN | :COINS/Coin 1 | 按1次，看CREDIT+1 | ✅已知有效 |
| START | :KEY0/1 Player Start | ODDS按1次，看是否进游戏 | 画面变化 |
| BET | :KEY1/P1 Mahjong Bet | ODDS按1次，看BET+1 | ❌已知无效 |
| KAN | :KEY0/P1 Mahjong Kan | 需在游戏中测试 | 待测 |
| PON | :KEY3/P1 Mahjong Pon | 需在游戏中测试 | 待测 |
| CHI | :KEY2/P1 Mahjong Chi | 需在游戏中测试 | 待测 |
| REACH | :KEY1/P1 Mahjong Reach | 需在游戏中测试 | 待测 |
| RON | :KEY2/P1 Mahjong Ron | 需在游戏中测试 | 待测 |
| DOUBLEUP | :KEY4/P1 Mahjong Double Up | 比倍时测试 | 待测 |
| BIG | :KEY4/P1 Mahjong Big | 比倍时测试 | 待测 |
| SMALL | :KEY4/P1 Mahjong Small | 比倍时测试 | 待测 |
| A-N | :KEY0-3/P1 Mahjong X | 选牌/打牌时测试 | 待测 |

**测试规范**（每个动作）：
1. 用隔离实例（独立cfg/nvram/state目录，不碰生产MAME）
2. 记录：`set_value(1)` 前/后端口 `read()` 值
3. 截图对比动作前后画面
4. 结论：**有效**（画面变化）/ **无效**（端口变画面不变）/ **待游戏状态**（需特定局面）

## 任务2：A-N选牌键全测

A-N对应14张手牌的选择/打出。在游戏进行中（需先用uinput把游戏打到出牌阶段）：
1. 对A-N每个键，用Lua `set_value` 按1次
2. 记录哪个键让哪张牌有反应（高亮/打出）
3. 特别注意：打牌是"单键a-n直接打出，不用Enter"（用户实测）

如果A-N的Lua也无效，标记为"需uinput"，不要强行用Lua。

## 任务3：Lua可获取的数据全清单

尝试用Lua获取以下数据，记录**能拿到**和**拿不到**的：

### 3.1 内存数据（已尝试未成功，继续想办法）
- CREDIT地址：尝试BCD、u16/u8、不同CPU、0x0000-0xFFFF全扫
- BET地址：同上
- 手牌数据地址：未知，需探索

### 3.2 ioport状态数据（已部分成功）
- 每个端口的 `read()` 值
- 每个字段的 `enabled`/`live` 状态

### 3.3 游戏状态推断
- 能否通过ioport或内存判断当前画面（ODDS/换牌/打牌/结算/比倍）？
- 如不能，明确记录"Lua无法判断游戏状态"

## 任务4：输出总报告

### 4.1 输入有效性总表
```
动作 | Lua有效? | uinput有效? | 推荐方案 | 备注
COIN | ✅ | ✅ | Lua | 
BET  | ❌ | ✅ | uinput | set_value端口变但游戏不响应
START| ?  | ?  | ? |
...
```

### 4.2 数据可获取性总表
```
数据项 | Lua可获取? | 方法 | 备注
CREDIT | ❌ | - | 内存地址未找到
BET值  | ❌ | - | 同上
游戏状态| ❌ | - | 无法判断
...
```

### 4.3 最终推荐架构
基于实测，给出推荐：
- 哪些输入走Lua，哪些走uinput
- 状态判断用什么方案（如果Lua不行，是否恢复最小化视觉？）
- 列出所有"待解决"项

## 约束
1. **生产MAME（PID 1750610）绝不碰**：所有测试用隔离实例（参考之前 `/tmp/sdmg2-bet-diag` 的做法：独立cfg/nvram/state目录）
2. **不改项目代码**：只做测试和诊断，不改 `ai_bridge.lua`、`modules/` 下的任何文件
3. **每个结论都要有证据**：截图、日志行、端口读值，不要推测
4. **uinput测试时**：用Python `evdev` 发单键，间隔0.3秒以上，防丢键
5. **游戏状态推进**：如需打到特定局面（换牌/打牌/比倍），可用uinput按已知有效的键推进，记录步骤

## 交付物
1. `KEYMAP-TEST-REPORT.md`：全按键测试报告（含有效性矩阵）
2. `TILE-INPUT-TEST-REPORT.md`：A-N选牌键测试报告
3. `LUA-DATA-AVAILABILITY.md`：Lua数据可获取性清单
4. `RECOMMENDED-ARCHITECTURE.md`：推荐架构（基于实测）

所有报告放在 `~/sdmg2-test/` 下，直接写文件。
