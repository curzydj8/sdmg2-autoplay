# Copilot 任务：定位真正的 BET 内存地址

## 背景

《超级大满贯Ⅱ》(sdmg2) AI 的 BET 感知出现残留：游戏画面 BET=0，但 `/tmp/sdmg2_state.json` 读到 10（上局残留）。当前 Lua 桥接 `/tmp/ai_reader2.lua` 从 `0x1F0BB5` 读 BET，该地址不可靠，需要重新定位。

工作 RAM 范围：`0x1F0000–0x1FFFFF`（64KB），CPU = `:maincpu`（M68000 大端）。

## 已有工具（都在 /tmp/）

- `/tmp/bet_scanner.lua`：每 10 秒（约 600 帧）自动 dump 整个 64KB 工作 RAM 到 `/tmp/bet_snap_N.bin`（N 递增）
- `/tmp/bet_diff.py`：对比两个快照，列出所有变化地址，重点标记 `0x00→0x05` 的精确 BET 候选；已修复截断 bug，会完整列出并校验快照必须为 64KB

## 执行步骤

1. **清理并启动 MAME（加载扫描器）**
   ```bash
   pkill -9 mame; sleep 2
   rm -f /tmp/bet_snap_*.bin
   /usr/games/mame sdmg2 -rompath ~/roms -window -autoboot_script /tmp/bet_scanner.lua &
   ```
2. **过警告屏**：用 xdotool 向 MAME 窗口（`xdotool search --onlyvisible --class "mame"`）发送几次 `Return` 和 `space`，等游戏进入标题/ODDS 画面。
3. **确认 CREDIT**：若 CREDIT=0，先用 xdotool 按 `5` 投币几次，确保有分可以押注（押注需要 CREDIT>0）。
4. **抓 BET=0 快照**：画面 BET=0 时，等扫描器 dump 一次（约 10 秒），记下文件名（如 `bet_snap_1.bin`），确认文件大小 65536 字节。
5. **押注到 BET=5**：用 xdotool 按 `3` 键 5 次，看画面 BET 变为 5。
6. **抓 BET=5 快照**：再等扫描器 dump 一次（约 10 秒），记下文件名（如 `bet_snap_2.bin`）。
7. **跑差分**：
   ```bash
   python3 /tmp/bet_diff.py /tmp/bet_snap_1.bin /tmp/bet_snap_2.bin
   ```
8. **验证候选**：对每个 `0x00→0x05` 候选地址，用 MAME Lua 或临时脚本再读一次，同时手动改 BET（如再按一次 3 到 BET=6），确认该地址同步变为 6。若多个候选，优先选随 BET 1:1 线性变化的。

## 交付

报告以下内容：
- BET=0 和 BET=5 快照的完整文件名与大小
- `bet_diff.py` 的完整输出
- 验证过的 BET 地址（十六进制）及验证方法（BET=6 时该地址的值）
- 若候选不止一个，列出全部并标注推荐哪一个

## 红线

- 只读内存，不要向游戏内存写值
- 不改 ROM、不改 MAME 配置、不重置存档
- 若 MAME 中途退出，重启 MAME 重来，不要伪造快照或结果
- 拿不到同步地址就如实说，不要猜
