# Copilot任务：测试并修复 ai_bridge.lua 所有按键映射

## 背景
`~/sdmg2-test/ai_bridge.lua` 是MAME Lua直控脚本，Python通过 `/tmp/mame_action.json` 发送动作，Lua读取后调用 `field:set_value(1/0)` 控制ioport。

**已知状态**：
- ✅ COIN (`:COINS`/`Coin 1`) 有效：CREDIT 1840→1855
- ❌ BET (`:KEY1`/`P1 Mahjong Bet`) 无效：日志显示"执行: BET"但画面BET保持0
- ❓ 其他映射未测试

## 任务目标
找出每个动作**真实有效**的 `{端口, 字段名}`，更新 `ai_bridge.lua` 的 `ACTION_MAP`，并逐个验证。

## 步骤1：Dump所有ioport字段真实名称
写一个Lua脚本 `dump_all_fields.lua`，遍历 `manager.machine.ioport.ports` 所有端口的所有字段，把 `{端口名, 字段名}` 写到 `/tmp/mame_all_fields.log`。用以下命令运行并查看结果：
```bash
pkill -9 mame; sleep 2; rm -f /tmp/mame_all_fields.log
cd ~/mame && DISPLAY=:0 timeout 15 /usr/games/mame sdmg2 -rompath ~/mame/roms -window -autoboot_script ~/sdmg2-test/dump_all_fields.lua > /dev/null 2>&1 &
sleep 12; cat /tmp/mame_all_fields.log
```

## 步骤2：对比并修正 ACTION_MAP
把dump出的真实字段名与 `ai_bridge.lua` 中 `ACTION_MAP` 的以下条目逐一对比，修正所有不一致：
- START / BET / KAN / PON / CHI / REACH / RON / DOUBLEUP / BIG / SMALL
- A / B / C / D / E / F / G / H / I / J / K / L / M / N
- COIN 已确认有效，不要改

注意：MAME字段名可能是 `Mahjong Bet` 而非 `P1 Mahjong Bet`，以dump结果为准。

## 步骤3：逐个验证
MAME以修正后的 `ai_bridge.lua` 启动后（`pkill -9 mame; sleep 2; rm -f /tmp/mame_bridge.log /tmp/mame_action.json; echo '{}' > /tmp/mame_action.json; cd ~/mame && DISPLAY=:0 nohup /usr/games/mame sdmg2 -rompath ~/mame/roms -window -autoboot_script ~/sdmg2-test/ai_bridge.lua > /dev/null 2>&1 &`，等10秒确认 `/tmp/mame_bridge.log` 出现 "AI Bridge v4"），对以下每个动作执行一次并检查日志出现"执行: X"：
```bash
for a in BET START KAN PON CHI REACH RON DOUBLEUP BIG SMALL; do echo "{\"action\": \"$a\"}" > /tmp/mame_action.json; sleep 1; done; tail -12 /tmp/mame_bridge.log
```
**关键验证**：BET必须让画面BET从0变1。用截图确认：
```bash
DISPLAY=:0 scrot /tmp/verify_bet.png
```
看图确认BET数字变化。如果BET仍无变化，说明字段名还是不对，回到步骤1重查。

## 步骤4：A-N选牌键验证（可选，如时间紧可跳过）
A-N映射到 `:KEY0`-`:KEY3` 的 `P1 Mahjong X` 字段。在ODDS画面这些键无可见效果，放到进游戏后再验证，本次先保证 BET/START 有效。

## 交付
1. 修正后的 `ai_bridge.lua`（直接覆盖 `~/sdmg2-test/ai_bridge.lua`）
2. 报告：每个动作的 `{端口, 字段名}` 最终值 + 验证结果（日志行/BET截图变化）
3. 特别注明：BET最终用什么字段名才生效

## 约束
- 不要改 `ai_bridge.lua` 的整体结构，只改 `ACTION_MAP`
- 不要动 `press_action`/`find_field`/`read_action` 逻辑
- MAME启动命令必须带 `-autoboot_script ~/sdmg2-test/ai_bridge.lua`，否则Lua不加载
