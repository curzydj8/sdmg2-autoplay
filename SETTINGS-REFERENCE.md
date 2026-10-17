# SETTINGS-REFERENCE.md - 设置与DIP参考

**最后更新**：2026-10-15 00:35  
**来源**：2026-10-14 用户DIP菜单截图 + MAME驱动源码

## DIP设置项（来自截图）

| 设置 | 当前值 | 可选值 | 源码证据 | 实际效果 | 需重启 | 已验证 |
|------|--------|--------|----------|----------|--------|--------|
| Coinage | 1 Coin/1 Credit | 未知 | - | 投币比率 | ❓ | 🟡 |
| Key-In Rate | 10 | 未知 | - | 上分比率？ | ❓ | ❓ |
| Credit Limit | 2000 | 未知 | - | 信用点上限 | ❓ | ✅ |
| Credit Mode | Coin Acceptor | 未知 | - | - | ❓ | ❓ |
| Payout Mode | Return Coins | 未知 | - | - | ❓ | ❓ |
| Demo Sounds | On | On/Off | - | 演示音效 | ❓ | ❓ |
| Double Up Jackpot | 500 | 未知 | - | 比倍上限 | ❓ | 🟡 |
| Minimum Bet | 1 | 未知 | - | 最低下注 | ❓ | ✅ |
| Double Up Game | On | On/Off | - | 比倍开关 | ❓ | ❓ |
| Double Up Game Name | Continue Play | 未知 | - | - | ❓ | ❓ |
| Controls | Mahjong | Mahjong/Joystick | igs017.cpp:3858 DSW2 mask 0x40 | ✅Mahjong有效，Joystick下注无效 | 是 | ✅ |
| Number Type | Numbers | 未知 | - | - | ❓ | ❓ |

## 关键发现

1. **Controls**：源码确认DSW2 mask 0x40。Mahjong=0x40(默认)，Joystick=0x00。
   实测：Joystick模式下注无效，必须用Mahjong。

2. **Credit Limit vs Max Bet**：Credit Limit=2000是信用点上限，**不是**最大下注。
   最大下注未知，不得混淆。

3. **Double Up Jackpot=500**：比倍奖励上限，不是下注上限。

## 未测试设置

除Controls外，其他设置未做变更测试。不得在有效牌局中修改。
