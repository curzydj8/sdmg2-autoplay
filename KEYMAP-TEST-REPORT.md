# Lua / uinput 按键有效性报告

**日期：** 2026-10-18  
**状态：** 部分实测；不等同于全量矩阵完成  
**约束：** 测试仅使用独立临时 MAME 实例；生产实例 PID 1750610 未操作，项目代码未修改。

## 判定规则

- **有效**：游戏画面或可验证游戏状态产生符合预期的变化。
- **无效**：端口写入成功且端口值变化，但游戏画面/状态无预期变化。
- **待测**：没有在合适游戏状态中取得有效的前后画面证据。
- `field:set_value()` 成功或 `port:read()` 改变只代表输入端口状态改变，不代表游戏处理了按键。

## 实测结果

| 动作 | Lua | uinput | 证据与结论 |
|---|---|---|---|
| COIN | **有效（已知）** | **有效（已知）** | Lua 临时诊断中 COIN `:COINS` 从 `255` 变为 `239`，ODDS 截图显示 CREDIT=1；uinput `KEY_5` 也已在临时实例用于获得 CREDIT。参见 `/tmp/mame_bet_diag.log`、`/tmp/sdmg2-bet-diag/final-window.png`。 |
| START | 待测 | 待测 | 尚无在 ODDS 状态下进局的按键前后证据。 |
| BET | **无效** | **有效** | 同一临时实例、同一 ODDS 状态：uinput `KEY_3` 后 CREDIT 1→0、BET 0→1；随后 Lua 长按 BET 两秒，端口 `255→223→255`，画面数值未变。参见 `/tmp/mame_bet_ab2.log`、`/tmp/sdmg2-bet-ab2/after-uinput-3.png`、`/tmp/sdmg2-bet-ab2/after-lua-bet.png`。 |
| KAN | 待游戏状态 | 待测 | 需确认牌局中存在可杠局面。 |
| PON | 待游戏状态 | 待测 | 需确认存在可碰牌局面。 |
| CHI | 待游戏状态 | 待测 | 需确认存在可吃牌局面。 |
| REACH | 待游戏状态 | 待测 | 需确认满足立直条件。 |
| RON | 待游戏状态 | 待测 | 需确认有可荣和牌局面。 |
| DOUBLEUP | 待游戏状态 | 待测 | 需先进入比倍状态。 |
| BIG | 待游戏状态 | 待测 | 需先进入比倍选择状态。 |
| SMALL | 待游戏状态 | 待测 | 需先进入比倍选择状态。 |
| A–N | 待游戏状态 | 待测 | 需进入真实可出牌牌局；尚无任何一个牌键的可归因前后截图。 |

`modules/controls.py` 及 [KEYMAP-FROM-MAME.md](./KEYMAP-FROM-MAME.md) 记录了预期物理键位，但映射文档不是本报告中的行为实测证据。

## 有效性矩阵覆盖范围

- 已获得游戏响应证据：COIN、BET（区分 Lua 和 uinput 路径）。
- **未完成**：START、KAN/PON/CHI/REACH/RON、DOUBLEUP/BIG/SMALL、A–N 的 Lua 与 uinput 对照。
- 目前 MAME 启动时显示 `m0205.u6` 为 `BAD_DUMP / NEEDS REDUMP`，并提示系统不工作；这会影响某些状态测试的可靠性。该 ROM 警告不能单独解释 BET 的输入路径差异。

## 当前建议

只采用已有证据支持的映射：在已验证环境中 COIN 可走 Lua、BET 使用 uinput 并对画面闭环验证。其余动作暂不按字段映射推定有效；应逐个在前置条件成立的游戏状态中测试。
