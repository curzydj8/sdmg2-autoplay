# Copilot 任务：为 auto_player.py 补齐全部麻将动作按键

## 背景

文件：`/home/zhangdawei/auto_player.py`（《超级大满贯Ⅱ》sdmg2 全自动 AI，用 xdotool 向 MAME 窗口发按键）。

当前代码只有 coin/bet/start/discard/collect 五个动作，缺少吃/碰/杠/立直/胡/收分/比倍等高级动作。以下按键映射已由 MAME 按键配置截图确认，是地面真理，原样采用：

## 完整按键映射（xdotool 键名）

```python
KEY_COIN = '5'            # 投币/上分
KEY_BET = '3'             # 押注
KEY_START = '1'           # 开始
TILE_KEYS = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n']  # 14张牌槽位
KEY_CHI = 'space'         # 吃
KEY_PON = 'Alt_L'         # 碰（左Alt）
KEY_KAN = 'Control_L'     # 杠（左Ctrl）
KEY_REACH = 'Shift_L'     # 立直（左Shift）
KEY_RON = 'z'             # 胡/自摸
KEY_TAKE_SCORE = 'Control_R'  # 收分（右Ctrl）
KEY_DOUBLE_UP = 'Shift_R'     # 比倍（右Shift）
KEY_BIG = 'Return'        # 大/确认
KEY_SMALL = 'BackSpace'   # 小
KEY_LAST_CHANCE = 'Alt_R' # 最后机会（右Alt）
```

## 要做的改动

1. 在代码顶部常量区加入上述全部按键常量（已有 TILE_KEYS/KEY_COIN/KEY_BET/KEY_START/KEY_BIG 若存在则对齐，不要重复定义）。
2. 扩展 `execute_action(action, param)`，新增动作分支，每个都走已有的 `xdotool_key(key, delay)`（该函数已带窗口ID + `--clearmodifiers`，不要另写发键逻辑）：
   - `'chi'` → KEY_CHI, 0.15
   - `'pon'` → KEY_PON, 0.15
   - `'kan'` → KEY_KAN, 0.15
   - `'reach'` → KEY_REACH, 0.15
   - `'ron'` → KEY_RON, 0.2
   - `'take_score'` → KEY_TAKE_SCORE, 0.3
   - `'double_up'` → KEY_DOUBLE_UP, 0.3
   - `'small'` → KEY_SMALL, 0.2
   - `'last_chance'` → KEY_LAST_CHANCE, 0.2
3. 修改 `'collect'` 分支：依次发 KEY_TAKE_SCORE (0.3) 再 KEY_BIG (0.3)，实现收分+确认两步。
4. `decide_action` 本次只接一个新动作：结算画面（有手牌、credit==0、bet==0）时优先返回 `('take_score', None)`；原 collect 兜底保留。其余新动作（ron/pon/chi/kan/reach/double_up）先只在 execute_action 里就绪，decide_action 暂不触发，并加注释 `# TODO: 待听牌/胡牌内存标志位定位后接入`。

## 验证

- `python3 -m py_compile /home/zhangdawei/auto_player.py` 通过
- 纯函数断言：`decide_action` 对结算状态返回 `('take_score', None)`；对 ODDS/押注/打牌状态的返回与改动前一致（不回归）
- 列出 execute_action 现在支持的全部动作名

## 红线

- 不要改状态机的经济链顺序（coin→bet→start）
- 不要引入新依赖；只用现有 xdotool_key
- 不要声称新动作已在实机验证过（本次只做代码就绪，实机验证另行安排）
