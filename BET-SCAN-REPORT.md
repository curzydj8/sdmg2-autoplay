# BET 内存差分扫描报告

**日期：** 2026-10-18  
**环境：** MAME 0.285、`sdmg2`；ROM `m0205.u6` 为 `BAD_DUMP / NEEDS REDUMP`  
**隔离：** 所有输入仅发送到使用独立 cfg/NVRAM/state 目录的临时 MAME 实例；未向生产实例发送按键。项目代码未修改。

## 方法

通过 Lua `:maincpu` program address space，对 M68000 的完整 24 位范围 `0x000000–0xFFFFFF` 执行 `read_u8` 快照。每次快照为 16,777,216 字节，记录 0 次读取错误，耗时约 15.1–16.2 CPU 秒。

1. 用 uinput 发 3 次 `KEY_5`，截图确认基线为 CREDIT=3、BET=0，再做全空间快照。
2. 发 1 次 `KEY_3`，等待 3 秒；截图确认 CREDIT=2、BET=1，再做快照。
3. 再发 1 次 `KEY_3`，等待 3 秒；截图确认 CREDIT=1、BET=2，再做第三次快照。
4. 搜索基线至第一次 BET 的字节 `0→1` 候选，以及与之同步的 CREDIT `3→2` 候选；再要求 BET 同一地址继续 `1→2`，CREDIT 地址继续 `2→1`。
5. 在另一新隔离实例中直接读取最终候选地址，并将读取值与三张状态截图交叉验证。

测试未使用 Lua `field:set_value()` 触发 BET。

## 全空间扫描结果

| 对比 | 变化字节数 | BET `+1` 字节候选 | CREDIT `-1` 候选 |
|---|---:|---|---|
| 基线 `(CREDIT=3, BET=0)` → 第一次 BET `(2,1)` | 235 | `0x1F0BB5`, `0x1F106E`, `0x1F3E61`, `0x1F3E95`, `0x1F3EB6`, `0x1F3EC7`, `0x1F3EF5`, `0x1F3F03` | `0x1F09FD`, `0x1F09FF` |
| 第一次 BET `(2,1)` → 第二次 BET `(1,2)` | — | 通过首轮候选中继续 `1→2` 的地址：`0x1F0BB5`, `0x1F106E`, `0x1F3F03` | 两处继续 `2→1`：`0x1F09FD`, `0x1F09FF` |

完整差分及读取计时日志：`/tmp/bet_diff_24bit.log`。

## 候选地址直接读取验证

另一隔离实例的读取日志 `/tmp/read_bet_candidates.log` 给出以下值：

| 画面状态 | `0x1F09FD` | `0x1F09FF` | `0x1F0BB5` | `0x1F106E` | `0x1F3F03` |
|---|---:|---:|---:|---:|---:|
| CREDIT=3、BET=0 | `03` | `03` | `00` | `00` | `00` |
| CREDIT=2、BET=1 | `02` | `02` | `01` | `01` | `01` |
| CREDIT=1、BET=2 | `01` | `01` | `02` | `02` | `02` |

对应截图：

- 基线 CREDIT=3/BET=0：[credit3-bet0.png](</tmp/sdmg2-bet-candidates/credit3-bet0.png>)
- 第一次 BET CREDIT=2/BET=1：[credit2-bet1.png](</tmp/sdmg2-bet-candidates/credit2-bet1.png>)
- 第二次 BET CREDIT=1/BET=2：[credit1-bet2.png](</tmp/sdmg2-bet-candidates/credit1-bet2.png>)

## 结论

强相关 BET 字节候选为 **`0x1F0BB5`、`0x1F106E`、`0x1F3F03`**。三处均在同一实例中与可见 BET 精确对应 `00→01→02`；全空间差分筛选也确认这三处同时满足两次连续递增。结合另一实例的直接读取，候选证据强，足以支持“这些内存字节随 BET 变化”。

**目前不能唯一指定其中一个为 BET 的主存地址。** 多个副本/镜像与 UI 或游戏内部缓存都仍可能；每次 BET 同时改变 CREDIT，因此还需通过只改变 BET 而不改变 CREDIT 的独立合法局面，或检查运行时读写/程序访问，排除与其他相关状态的偶然关联。当前三处也不邻接已知 CREDIT 候选 `0x1F09FD`/`0x1F09FF`，没有证据支持 `0x1F09FE` 是 BET。

## 限制与后续

- 输入测试在 CREDIT=3、2、1 的 ODDS 画面进行；尚未验证 BET 值高于 2、复位后地址稳定性或不同 ROM dump 下地址稳定性。
- ROM 含 `BAD_DUMP`，应在已知良好的 dump 上重测。
- 在进一步验证前，建议将这三处视为 BET 相关候选，而非写入/控制地址；只读访问并保留屏幕交叉检查。
