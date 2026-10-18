# Copilot任务：BET字段运行时状态诊断

## 背景
- `ai_bridge.lua` 的 BET 映射（`:KEY1`/`P1 Mahjong Bet`）经转储核实无误
- 单次BET实测：Lua日志显示"按下/释放"，但画面BET保持0
- COIN（`:COINS`/`Coin 1`）有效，BET无效——同一机制，一半工作

## 目标
区分三种可能：
1. **端口值变了但游戏不响应** → 输入已到ioport，查游戏状态/输入条件
2. **端口值没变** → Lua写入方式没真正驱动字段，需换MAME输入注入路径
3. **字段未启用** → 查Controls DIP或其他条件

## 步骤：取BET按下前/中/后的运行时状态

写一个Lua脚本 `diag_bet_state.lua`，在一次BET动作的前、中、后记录：
- `field.live` 的值（字段是否活跃）
- `field.mask` 的值
- 所属端口 `:KEY1` 的 `port:read()` 值
- 字段是否启用（`field.enabled` 如果存在）

脚本逻辑：
1. 找到 `:KEY1`/`P1 Mahjong Bet` 字段
2. 记录初始状态 → 写 `/tmp/mame_bet_diag.log`
3. `set_value(1)` → 等待100ms → 记录"按下期间"状态
4. `set_value(0)` → 等待100ms → 记录"释放后"状态
5. 结束

运行命令：
```bash
pkill -9 mame; sleep 2; rm -f /tmp/mame_bet_diag.log
cd ~/mame && DISPLAY=:0 timeout 20 /usr/games/mame sdmg2 -rompath ~/mame/roms -window -autoboot_script ~/sdmg2-test/diag_bet_state.lua > /dev/null 2>&1 &
sleep 15; cat /tmp/mame_bet_diag.log
```
注意：MAME启动有两页提示（ROM信息→警告），timeout 20秒内脚本的periodic（设3秒间隔）应能执行。如未执行，加长timeout或先手动按Enter过提示。

## 对比基线：COIN字段的同样数据
对 `:COINS`/`Coin 1` 做同样的三段记录（因为COIN是已知有效的）。对比两者的差异：
- COIN的 `field.live`/`mask`/`port:read()` 在按下前后如何变化？
- BET的对应值是否以同样方式变化？

如果COIN的端口值变化而BET的不变 → Lua写入对BET无效
如果两者都变但只有COIN让游戏响应 → 游戏端对BET有额外条件

## 交付
1. `/tmp/mame_bet_diag.log` 的完整内容（BET三段 + COIN三段）
2. 结论：属于三种可能中的哪一种
3. 建议的下一步（基于证据，不要猜）

## 约束
- 只做诊断，不改 `ai_bridge.lua`
- 不发送游戏动作（除了诊断脚本内的单次测试按下）
- 不重启生产环境的MAME（用timeout的临时实例做诊断）
