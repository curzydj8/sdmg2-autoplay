# Copilot任务：找BET内存地址（用CREDIT成功的同样方法）

## 背景
CREDIT地址已找到（`0x1F09FD`/`0x1F09FF`），方法验证有效：
- 隔离MAME实例（独立cfg/nvram/state）
- **真实uinput按键**（不用Lua set_value）
- 全24位地址空间（0x000000-0xFFFFFF）差分扫描
- 基线 → 动作 → 等待游戏处理 → 二次扫描 → diff

## 目标
找BET的内存地址。BET的特点：
- 按BET键：BET 0→1，同时CREDIT 3→2（两个都变）
- 这是优势：一次动作，两个信号，可以交叉验证

## 步骤

### 1. 建立基线
隔离实例启动后：
- 用uinput按3次KEY_5，得到CREDIT=3、BET=0（截图确认）
- Lua脚本做全空间快照 → baseline

### 2. 执行BET
- 用uinput按1次KEY_3（**不是Lua set_value**）
- **等待3秒**让游戏处理（上次CREDIT扫描证明等待是必要的）
- 截图确认：CREDIT=2、BET=1

### 3. 二次扫描与diff
- 全空间快照 → after
- Diff找：
  - **+1的地址**：BET候选（0→1）
  - **-1的地址**：CREDIT候选（3→2，用于验证方法，预期找到0x1F09FD/0x1F09FF）
- 如果CREDIT候选对上了，说明方法正确，BET候选可信

### 4. 反向验证
- 再按1次KEY_3：BET 1→2，CREDIT 2→1
- 检查BET候选是否 1→2，CREDIT候选是否 2→1
- 两次都对上，才是高可信

## 预期
- BET可能在CREDIT附近（比如0x1F09FE？），也可能在别处
- 注意BCD编码：如果BET=10，内存可能是0x10不是0x0A
- 记录所有+1的候选，不要只取第一个

## 约束
1. **不用Lua set_value触发**：上次已证实set_value对BET无效，必须用uinput
2. **必须等待**：按完键等3秒再扫，给游戏处理时间
3. **截图确认**：每次动作后截图，确认画面数字真的变了
4. **不动生产MAME**：只用隔离实例
5. **不改项目代码**：只写扫描脚本和报告

## 交付
`BET-SCAN-REPORT.md`：
- 扫描方法（复用CREDIT的）
- 候选地址表（BET+1的，CREDIT-1的）
- 反向验证结果
- 结论：哪个是BET，置信度，待验证项

如果BET地址和CREDIT地址在相邻位置，注明可能的内存布局（如：0x1F09FD=CREDIT低字节，0x1F09FE=BET？）。
