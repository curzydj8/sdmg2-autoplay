# CREDIT 内存差分扫描报告

**日期：** 2026-10-18  
**环境：** MAME 0.285、`sdmg2`、`m0205.u6` 状态为 `BAD_DUMP / NEEDS REDUMP`  
**范围：** 独立临时 MAME 实例，使用独立 cfg/NVRAM/state 目录；未对生产实例发按键。项目代码未修改。

## 方法

通过 `manager.machine.devices[":maincpu"].spaces["program"]` 读取 M68000 的 24 位 program address space（`0x000000–0xFFFFFF`）。每次全范围 `read_u8` 扫描约 15.6–16.1 CPU 秒，16,777,216 字节均成功读取，未发生 Lua 读取异常。

先以 uinput 单键建立可见 CREDIT 状态，再在同一 MAME 进程中改变 CREDIT 并做全空间差分。随后直接读取差分发现的候选地址，用 BET 减少 CREDIT、COIN 增加 CREDIT 进行反向和正向验证。

## 证据

### 全范围差分

第一实例中：

- 截图 [baseline CREDIT=1](/tmp/sdmg2-credit-scan/baseline-screen.png) 到截图 [after1 CREDIT=2](/tmp/sdmg2-credit-scan/after1-screen.png)：24 位扫描有 186 个字节变化。`0x1F09FD`、`0x1F09FF`、`0x1F0C11` 的值均为 `01→02`。
- 截图 [after1 CREDIT=2](/tmp/sdmg2-credit-scan/after1-screen.png) 到截图 [after2 CREDIT=3](/tmp/sdmg2-credit-scan/after2-screen.png)：扫描有 122 个字节变化。`0x1F09FD`、`0x1F09FF`、`0x1F0C11` 的值均为 `02→03`。
- 完整差分日志：`/tmp/credit_diff_24bit.log`。

### 目标地址复核

另一隔离实例中，直接读取候选字节并同步截屏：

| 操作/可见画面 | `0x1F09FD` | `0x1F09FF` | `0x1F0C11` | 结果 |
|---|---:|---:|---:|---|
| 操作前，CREDIT=3、BET=0 | `03` | `03` | `03` | 两个主要候选与 CREDIT 一致 |
| uinput BET 后，CREDIT=2、BET=1 | `02` | `02` | `03` | 两个主要候选随 CREDIT 减少；第三处不变 |
| 再 uinput COIN 后，CREDIT=3、BET=1 | `03` | `03` | `04` | 两个主要候选随 CREDIT 增加并恢复；第三处继续增加 |

- 操作后截图：[CREDIT=2、BET=1](/tmp/sdmg2-candidate-read/after-bet.png)、[CREDIT=3、BET=1](/tmp/sdmg2-candidate-read/after-coin.png)。
- 目标地址读取日志：`/tmp/read_credit_candidates.log`。

## 结论

`0x1F09FD` 与 `0x1F09FF` 是当前最强的 CREDIT 候选地址：两者都精确对应可见数值 `3→2→3`，并且跨越了一次 BET 减分和一次 COIN 加分。`0x1F0C11` 在本次对照中表现为累计增加 `3→3→4`，更像累计投币/入分计数，不应当作当前 CREDIT。

**尚不能声称 CREDIT 映射已最终定案：**

- 两个地址可能是镜像/副本，尚未确定哪一个是游戏逻辑的主值。
- 尚未在 MAME 进程重启后验证地址和值的稳定性。
- 本次运行 ROM 含 `BAD_DUMP`，应在更可靠的 ROM dump 下复测。
- 尚未验证十进制多位 CREDIT、进位/借位、存档读写等边界。

## 之前扫描失败的原因

- `/tmp/mame_memdiff.log` 中的 `mem_diff_scanner.lua` 在同一回调周期阶段推进；所谓“等待3秒”只有日志文字，没有实际等待。它调用 `field:set_value()` 后很快就做第二次扫描，并非真实 uinput 变化后的差分。
- `/tmp/mame_value_search.log` 只搜索 `0x800000–0x8FFFFF` 中的 u16 值 `1855`，没有搜索其他编码/地址范围；返回零个候选仅说明该特定搜索未命中。

因此，这两份旧结果不能作为“内存没有 CREDIT”或“地址已穷尽”的证据。

## 后续

1. 用隔离实例重启复核 `0x1F09FD` / `0x1F09FF`，并记录 0、1、9、10 等进位边界。
2. 对照相邻字节和 MAME 内存映射，判断双地址是镜像还是独立副本。
3. 后续扫描 BET、手牌和阶段状态时，必须使用真实按键改变局面，等待屏幕状态变化后再采样；逐项保留前后截图。
