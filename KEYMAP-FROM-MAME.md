# MAME实际键位表（2026-10-18实机截图）

来源：MAME Input Assignments菜单实拍（两张截图）
用途：核对`modules/controls.py`的KEY_MAP是否正确

---

## 麻将牌键（选牌/打牌）

| MAME功能 | 按键 | 说明 |
|----------|------|------|
| P1 Mahjong A | A | 选第1张牌/打A |
| P1 Mahjong B | B | 选第2张牌/打B |
| P1 Mahjong C | C | 选第3张牌/打C |
| P1 Mahjong D | D | 选第4张牌/打D |
| P1 Mahjong E | E | 选第5张牌/打E |
| P1 Mahjong F | F | 选第6张牌/打F |
| P1 Mahjong G | G | 选第7张牌/打G |
| P1 Mahjong H | H | 选第8张牌/打H |
| P1 Mahjong I | I | 选第9张牌/打I |
| P1 Mahjong J | J | 选第10张牌/打J |
| P1 Mahjong K | K | 选第11张牌/打K |
| P1 Mahjong L | L | 选第12张牌/打L |
| P1 Mahjong M | M | 选第13张牌/打M |
| P1 Mahjong N | N | 选第14张牌/打N（摸牌） |

**注意**：打牌是单键A-N直接打出，不用Enter（已实机验证）。

---

## 功能键

| MAME功能 | 按键 | 用途 |
|----------|------|------|
| P1 Mahjong Kan | Left Ctrl | 杠 |
| P1 Mahjong Pon | Left Alt | 碰 |
| P1 Mahjong Chi | Space | 吃 |
| P1 Mahjong Reach | Left Shift | 立直 |
| P1 Mahjong Ron | Z | 荣和 |
| P1 Mahjong Bet | 3 | 押注 |
| P1 Mahjong Take Score | Right Ctrl | 取分（退币，未验证勿自动执行） |
| P1 Mahjong Double Up | Right Shift | 比倍 |
| P1 Mahjong Big | Return (Enter) | 比倍选大 |
| P1 Mahjong Small | Backspace | 比倍选小 |
| P1 Mahjong Last Chance | Right Alt | Last Chance |

---

## 系统键

| MAME功能 | 按键 | 用途 |
|----------|------|------|
| 1 Player Start | 1 | 开始游戏 |
| Coin 1 | 5 | 投币（每次+1分） |
| Payout | 4 | 赔付 |
| Show Credits | 9 | 显示信用 |
| Book-Keeping | 0 | 记账 |
| Service 3 | - | Service 3 |
| Service Mode | F2 | 服务模式 |

---

## 与controls.py对照

`modules/controls.py`的KEY_MAP应包含以上全部映射。
已验证正确的：
- ✅ A-N（打牌）
- ✅ 3=Bet，5=Coin，1=Start
- ✅ Left Ctrl=Kan，Left Alt=Pon，Space=Chi
- ✅ Left Shift=Reach，Z=Ron
- ✅ Right Shift=Double Up，Return=Big，Backspace=Small
- ✅ Right Alt=Last Chance，Right Ctrl=Take Score
- ✅ 4=Payout，9=Show Credits，0=Book-Keeping

**Copilot注意**：如发现KEY_MAP缺失或错误，请按此表修正。
