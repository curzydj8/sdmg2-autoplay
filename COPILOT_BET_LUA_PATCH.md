# Copilot 任务：把 ai_reader2.lua 的 BET 地址换成快照差分找到的新地址

## 背景

文件：`/tmp/ai_reader2.lua`（MAME 启动脚本，`mame sdmg2 -autoboot_script /tmp/ai_reader2.lua`，每轮把内存读数写到 `/tmp/sdmg2_state.json`，`auto_player.py` 读它做决策）。

当前 `BET_ADDR = 0x1F0BB5` 是可疑地址：JSON 里 bet=10 时画面 BET=0，内存/画面不同步（P0 未解）。`bet_diff.py` 对比 BET=0 / BET=5 两份 64KB 快照会输出"精确BET候选"地址——这个任务就是把那个地址写进 Lua 并实机验证。

**新地址（执行前把下面替换成 bet_diff.py 输出的"精确BET候选"地址）：**

```lua
local BET_ADDR = 0x????????   -- ← 替换成 bet_diff.py 报的地址
```

## 要做的改动

1. 打开 `/tmp/ai_reader2.lua`，第 7 行：
   ```lua
   local BET_ADDR = 0x1F0BB5
   ```
   把 `0x1F0BB5` 换成新地址。**只改这一行，别的不动。**
   （Lua 里 BET 只在这一处被 `safe_read(space, BET_ADDR)` 以 u8 读取并写入 JSON 的 `"bet"` 字段，无别处引用。）

2. 同步 workspace 备份：`/home/hatch/workspace/sdmg2-test/ai_reader2.lua`（若存在）同样改这一行，`/tmp` 重启会清空。

## 验证（MAME 实机）

1. 重启 MAME：`mame sdmg2 -autoboot_script /tmp/ai_reader2.lua`，过掉 NEEDS REDUMP 警告（Return/Space 跳过）。
2. 游戏画面 BET=0 时：`cat /tmp/sdmg2_state.json`，记下 `"bet"` 的值，必须是 0。
3. 按 `3` 键押注到画面 BET=5：再看 JSON，`"bet"` 必须是 5。
4. 按 `5` 上分确认 `"credit"` 也在涨（排除读错区段）。

## 验收标准

- 画面 BET=0 → JSON bet=0；画面 BET=5 → JSON bet=5。**两处都对才算过。**
- 如果新地址在 0 和 5 都对，但押注过程中 JSON bet 跳变不同步（比如出现 bet=10 残留），把 JSON 全文记下来原样报回，**不要自己再换地址试**。
- 如果 bet_diff.py 报了多个候选（主+镜像），先用第一个；验证不过就报回，不要逐个试错。

## 报告格式

- 改了哪一行（贴改后第 7 行）
- BET=0 时的 JSON `bet` 值、BET=5 时的 JSON `bet` 值
- 过 / 不过，一句话结论
