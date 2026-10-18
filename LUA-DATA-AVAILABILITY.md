# MAME Lua 数据可获取性清单

**日期：** 2026-10-18  
**状态：** ioport 有限实测；内存、游戏状态未完成验证

## 数据项目

| 数据项 | Lua 可获取？ | 实测方法/证据 | 备注 |
|---|---|---|---|
| `:COINS` 端口当前值 | **是** | `port:read()`；COIN 按下前 `255`、按住时 `239`。`/tmp/mame_bet_diag.log` | 读到的是 MAME ioport 当前位值。 |
| `:KEY1` 端口当前值 | **是** | `port:read()`；BET 按下前 `255`、按住时 `223`，释放后恢复 `255`。`/tmp/mame_bet_ab2.log` | 能验证 Lua 写入改变了端口位；不等于游戏接受按键。 |
| 输入字段名称 / `mask` / `enabled` | **部分可获取** | BET `mask=32, enabled=true`；COIN `mask=16, enabled=true`。`/tmp/mame_bet_diag.log` | 仅对这两个字段有运行时采样证据；其他字段未遍历验证。 |
| `field.live` 对象 | **部分可获取** | Lua 返回 `sol.ioport_field_live*` userdata | 对象存在，但不是可直接当布尔值使用的字段值。 |
| `field.live.value`、`field.live.digital_value` | **本次方式不可用** | 诊断读数均为 `nil` | 不可据此推断输入状态；需查 MAME 0.285 Lua 对象接口或其他 API。 |
| CREDIT 数值（通过内存） | **未确认** | 无有效候选地址或可靠读数 | 现有 `scan_memory.lua` 只扫 `0x00000–0x1FFFF`，以旧的 CREDIT=1835 搜索 u16；未构成完整全 CPU、全 64K 的验证，不能以“未找到”作结论。 |
| BET 数值（通过内存） | **未确认** | 无有效候选地址或可靠读数 | 未取得地址候选，也未做值变化对照。 |
| 手牌数据（通过内存） | **未确认** | 未扫描/未验证 | 无地址证据。 |
| 游戏状态（ODDS/摸牌/出牌/结算/比倍） | **未确认** | 无可重复 Lua 状态识别器或内存状态值证据 | 当前只能由画面观察；ioport 值本身没有证明能区分这些状态。 |

## MAME 与 ROM 环境证据

- MAME 版本：`0.285`。
- `-listxml sdmg2` 声明的系统源文件为 `igs/igs017.cpp`，CPU 设备类型为 `m68000`，列出了 `:COINS`、`:KEY0` 至 `:KEY4` 等端口。
- `/usr/games/mame -verifyroms sdmg2 -rompath /home/zhangdawei/mame/roms` 输出：`m0205.u6 ... NEEDS REDUMP`，ROM set 为 `best available`。因此，内存扫描和游戏逻辑结果应附带 ROM 状态限制。

## 结论

当前可靠的数据面仅为**部分 ioport 状态**。CREDIT/BET 的实际画面数字、牌面和阶段状态尚未从 Lua 内存 API 可靠获取。现有扫描脚本或 MAME XML 的存在不等于扫描已执行或地址已确认。
