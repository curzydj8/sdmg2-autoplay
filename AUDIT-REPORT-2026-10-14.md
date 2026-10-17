# 超级大满贯Ⅱ 自主游戏 AI — 项目审计与第一轮测试报告

**报告时间**：2026-10-14 23:50 CST  
**报告人**：Muse (till)

---

## 1. 当前真实游戏进程和窗口状态

- **MAME 进程**：PID 46647，`/usr/games/mame sdmg2754ca -rompath /home/zhangdawei/roms -window`
- **窗口 ID**：10485767，标题 `Chaoji Da Manguan II (China, V754C, set 1) [sdmg2754ca] - MAME 0.285`
- **桌面环境**：GNOME Wayland + XWayland，DISPLAY=:0
- **DIP 设置**：Controls=Mahjong（用户 22:38 手动确认，配置文件写入无效）
- **运行中脚本**：
  - `/tmp/autostart.sh` (PID 54285)：每25秒发送 5+3+1，自动开新局
  - `/tmp/proactive.sh` 已停止（与下注冲突）
- **截图能力**：✅ XDG Portal Screenshot API 可用，已验证

## 2. 实际识别出的游戏阶段

基于真机截图确认存在的阶段：

| 阶段 | 识别特征 | 状态 |
|------|----------|------|
| ODDS/投注 | 紫色ODDS大字，CREDIT/BET数字，"PUSH START OR BET BUTTON" | ✅ 已确认 |
| 选牌交换 | "請選擇您要交換的牌！！"，手牌A-N可见 | ✅ 已确认 |
| 主局打牌 | DONDEN计数器，手牌+牌河，倒计时 | ✅ 已确认 |
| 结算 | 待观察 | ❓ 未知 |

## 3. 已经证实的规则与仍未知的规则

**已验证**（8条，见 `learning/rules-database.json`）：
- R001：按5投币 ✅
- R002：按3下注 ✅
- R003：按1开始 ✅
- R005：按A-N选牌/出牌 ✅
- R006：Mahjong模式正确 ✅
- R007：游戏流程 ✅
- R008：CPU超时自动出牌 ✅

**待验证**：
- R004：按N摸牌（用户指示，待截图验证）

**未知**：
- 胡牌判定条件
- 番数/得分计算
- DONDEN具体含义
- 比倍触发条件
- 听牌提示机制

**已否定**：
- 配置文件写DIP有效（实际无效，必须手动改）
- Joystick模式下注有效（实际无效）
- IPT_BUTTON2是下注键（实际是Mahjong Bet=3键）

## 4. 实际执行的输入及其效果

本轮（23:43-23:50）：
1. `3`（下注）：BET 0→1 ✅ 截图证实
2. `a,d,n`（换牌）：选中1萬、1筒、中 ✅
3. 之前系统测试：5/3/1/A/N/Z/Space 全部引起画面变化 ✅

## 5. 操作前后截图路径

- `screenshots/audit-current.png`：23:43 ODDS，CREDIT=43
- `screenshots/phase9-test.png`：23:45 ODDS，CREDIT=44
- `screenshots/bet-test.png`：23:46 换牌阶段，CREDIT=46，BET=1
- `screenshots/proactive.png`：23:35 主局，DONDEN 0
- `screenshots/strategy.png`：23:30 换牌阶段

## 6. 本轮新增或修正的学习记录

- 新建 `learning/rules_database.py` + `rules-database.json`：8条结构化规则
- 新建 `GAME-RULES-OBSERVED.md`：规则观察记录
- 更新 `INPUT-MAPPING-CONFIRMED.md`：系统测试结果
- 修正：DIP配置文件无效、Joystick模式无效、Button2非下注键

## 7. AI 当前采用的决策方式

当前为**规则基线 + 人工干预**：
- 自动循环负责开局（5+3+1）
- 换牌/打牌阶段由我根据截图人工分析后发送指令
- 策略：优先打孤张字牌和边张（K/L/M/A/E/F）
- 尚未实现：自动牌面识别、自动策略搜索

## 8. 下一轮自动测试任务

1. 验证 R004（N摸牌）：在主局阶段按N，截图确认是否摸牌
2. 观察完整一局：从开局到结算，记录DONDEN变化和得分
3. 测试吃/碰/槓：Z/Space/Alt在特定牌型下的效果
4. 建立牌面识别：从截图中识别手牌，为自动策略打基础

## 9. 是否具备进入策略学习阶段

**尚未完全具备**。原因：
- ✅ 状态识别：可通过截图人工识别，但无自动OCR/牌面识别
- ✅ 基础动作：已验证
- ✅ 规则基线：8条已验证
- ❌ 自动状态机：无程序化阶段识别
- ❌ 奖励信号：未建立得分与动作的关联
- ❌ 评估基线：无可比的策略对比数据

**建议**：先实现自动截图→阶段识别→规则动作的闭环，再谈策略优化。
