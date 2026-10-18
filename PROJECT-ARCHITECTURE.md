# 项目架构、运行流程与模块说明

> 本文基于当前仓库快照梳理，重点区分“当前目录中可直接检查的代码”和“历史报告、设计文档中提到但当前快照没有对应源码的模块”。文档中的实现状态以当前文件清单为准；报告记载的历史测试结果不等同于当前可复现的运行状态。

## 1. 项目概览

项目目标是对 MAME 中的《超级大满贯 II》进行自动截图、游戏阶段识别和输入操作，并逐步发展出状态识别、麻将规则分析、经验记录及自主学习能力。

当前仓库是**以设计/实验档案为主、带安全操作台的原型**：

- [`auto_player.py`](./auto_player.py) 是统一入口：可截图、记录状态、持续观察，也可在显式启用且每次确认后发送一个人工指定按键。
- 默认启动是只观察模式；状态分类目前恒为 `UNKNOWN`，因此不会自主按键或打牌。
- [`ai_auto_play.py`](./ai_auto_play.py) 与 [`ai-stable.sh`](./ai-stable.sh) 仅作兼容启动器，都会转到安全操作台。旧 Shell 固定按键循环已停用。
- 视觉、麻将规则、策略、经验学习等许多模块仍只出现在设计文档或历史报告中，当前快照没有对应源码。

**当前程序不是完整的自主麻将玩家。** 它提供运行操作界面和受控的单键输入；要达到自主识牌、选择动作、验证结果并持续游戏，还需要接入并验证视觉分类器、牌面识别和游戏规则策略。

## 2. 当前仓库结构

```text
sdmg2-autoplay/
├── auto_player.py                  # 截图、日志、安全交互控制台
├── ai_auto_play.py                 # 兼容启动器
├── ai-stable.sh                    # 兼容启动器（旧固定按键循环已停用）
├── tests/
│   └── test_auto_player.py         # 安全门禁与操作流程单元测试
├── PROJECT-ARCHITECTURE.md         # 本文
├── *.md                            # 设计、实验、审计、阶段报告
├── *.json                          # 指标、索引和测试结果等记录
└── git/                            # 仓库元数据目录（非运行模块）
```

当前快照尚无 `vision/`、`modules/`、`learning/`、`mahjong/`、`records/`、`config/`、`datasets/`、`outputs/` 等运行模块目录。有些历史报告提到这些路径或其中的代码，但相应文件不在当前快照中。

## 3. 架构总览

### 3.1 当前安全操作路径

```text
ai_auto_play.py / ai-stable.sh（兼容入口）
        │ 转发参数
        ▼
auto_player.py
  ├─ 操作台：help / status / capture / watch / press <key> / quit
  ├─ 截图：xwd → xwdtopnm → ffmpeg → PNG
  ├─ 状态：UNKNOWN（无可用分类器）→ 自动动作闭锁
  ├─ 默认：只观察
  └─ 可选人工单键：启动显式授权 → 截图 → 每次确认 → xdotool
                                   → 操作后截图 → 人工核对
```

人工单键模式也不等于自主游戏：它不识牌、不判断动作合法性，也不证明 MAME 已接收按键。

### 3.2 目标架构（设计文档体现的模块关系）

```text
MAME 游戏进程（外部）
        │ 游戏画面
        ▼
截图/图像输入
        ▼
视觉感知 ──► 游戏状态识别 ──► 状态机/转换校验
                                   │
                                   ▼
                         规则证据与策略决策
                                   │
                         授权/风险/隔离检查
                                   │
                                   ▼
                         输入适配器（按键）
                                   │
                                   ▼
                         MAME / 游戏画面
                                   │
                     前后截图、分数、状态验证
                                   ▼
                   经验记录 / 规则证据 / 学习
                                   │
                                   └──► 更新任务与策略
```

该图概括历史设计文档的目标关系，并非当前代码已经实现的端到端架构。当前快照实现了安全操作台及兼容入口；其余方框均需按下文状态说明理解。

## 4. 当前代码模块

| 模块 | 文件 | 当前职责 | 当前状态与边界 |
|---|---|---|---|
| 安全操作台 | [`auto_player.py`](./auto_player.py) | 交互命令、截图、日志、观察循环、受控人工单键 | 默认只观察；未知状态不触发动作。人工输入需要 `--allow-manual-input`、窗口 ID 和逐次键入 `yes` 确认。 |
| 兼容启动器 | [`ai_auto_play.py`](./ai_auto_play.py)、[`ai-stable.sh`](./ai-stable.sh) | 保持旧启动文件路径可用，并转发参数给安全操作台 | 不再执行原有固定键序列；`ai-stable.sh` 仍要求 Linux/Bash 环境。 |
| 安全测试 | [`tests/test_auto_player.py`](./tests/test_auto_player.py) | 检查默认输入闭锁、未知状态、允许键、人工确认与取消流程 | 采用 Python 标准库 `unittest`；不连接真实 MAME。 |
| 项目说明与实验档案 | 根目录 Markdown / JSON | 记录设计、测试、审计、规则假设及阶段结论 | 是重要设计与证据来源，但不能替代缺失的可执行模块。不同日期报告之间可能有状态差异或未解决矛盾。 |
| 游戏运行环境 | MAME、游戏 ROM、桌面/X11、输入设备 | 提供游戏画面并接收输入 | 属于外部运行依赖，不包含在当前仓库内；目标进程、窗口、ROM 和环境配置需在运行机器单独确认。 |

## 5. 运行流程细分

### 5.1 截图和观测

1. `auto_player.py` 创建截图目录（默认 `~/.sdmg2-autoplay/captures`）。
2. 调用 `xwd -root -silent` 获取当前 X11 根窗口图像。
3. 将 XWD 数据经 `xwdtopnm` 转成 PNM，再由 `ffmpeg` 保存成时间戳 PNG。
4. 检查输出文件存在且非空；失败时显示错误，不将旧截图当成本轮结果。
5. 当前没有接入状态识别器，所以每次观测均报告 `UNKNOWN` 并暂停自动动作。

### 5.2 控制台命令

| 命令 | 用途 | 是否会发送按键 |
|---|---|---|
| `help` | 显示命令列表 | 否 |
| `status` | 显示模式、窗口 ID 与自动动作状态 | 否 |
| `capture` | 截图一次并报告 UNKNOWN | 否 |
| `watch` | 按配置间隔重复截图；`Ctrl+C` 停止 | 否 |
| `press <key>` | 请求发送一个人工指定按键 | 仅显式启用输入后可尝试；发送前逐次确认 |
| `quit` / `exit` | 退出操作台 | 否 |

允许手动指定的按键为 `1 3 5 a b d e f g h i j k l m n`。`c` 不在白名单内。每次操作只发送单键，不支持批量宏或自动重复。

人工单键流程为：检查参数与白名单 → 截取操作前画面 → 告知当前识别状态未知 → 用户输入 `yes` 确认 → 调用 `xdotool` → 截取操作后画面 → 提示由人工核对。程序会明确说明“命令执行”不等于“MAME 已接收”或“游戏状态已变化”。

### 5.3 启动与常用操作

目标运行环境是 Linux/X11 上运行 MAME 的机器。当前 Windows 开发工作区不能代替目标 Linux 桌面完成真实截图或输入验证。

```bash
# 默认安全模式：启动交互操作台，不会发送按键
python3 auto_player.py

# 兼容旧 Python 启动文件（行为同上）
python3 ai_auto_play.py

# 兼容旧 Shell 启动文件（行为同上）
sh ai-stable.sh

# 单次截图后退出
python3 auto_player.py --once

# 连续观察；默认每 5 秒截图，可用 --interval 调整
python3 auto_player.py --watch --interval 3

# 显式开放人工单键入口；仍须在操作台每次确认
python3 auto_player.py --allow-manual-input --window-id 8388613

# 指定 X11 环境与输出位置
python3 auto_player.py --display :0 --xauthority /path/to/Xauthority \
  --capture-dir /path/to/captures --log-file /path/to/auto_player.log

# 运行单元测试（标准库）
python3 -m unittest discover -s tests -v
```

进入控制台后，先执行 `status`，再用 `capture` 或 `watch` 查看画面。只有在人工核实目标窗口及游戏状态后，才考虑启用人工单键输入；输入授权不会打开自动打牌功能。

### 5.4 故障处理与日志

- 缺少 `xwd`、`xwdtopnm`、`ffmpeg` 或 `xdotool` 时，操作台报告缺少的命令及安装/PATH 检查方向。
- 截图命令失败、输出图片无效、输入参数非法、用户取消操作，均显式报告；不会默默沿用上次状态。
- 默认日志：`~/.sdmg2-autoplay/auto_player.log`；默认截图：`~/.sdmg2-autoplay/captures/`。
- 用 `Ctrl+C` 停止 `watch`；用 `quit` 停止交互控制台。
- 此版本不监控 MAME 进程、不自动重启游戏、不修改 DIP/NVRAM，也不处理崩溃恢复。

## 6. 设计文档中描述的细分模块及当前状态

| 逻辑模块 | 设计职责 | 当前快照状态 |
|---|---|---|
| 截图与图像加载 | 从 MAME/桌面获得截图，标准化输入 | `auto_player.py` 实现 X11 根窗口截图命令链；尚无按目标 MAME 窗口裁切或标准化的专用采集模块。 |
| 视觉流水线 | 状态分类、手牌区域定位、单牌切分、牌面分类、一致性检查 | [`VISION-README.md`](./VISION-README.md) 描述了拟议的 `vision/` 结构，并明确牌面分类未实现；当前快照没有 `vision/` 源码目录。 |
| 状态识别与状态机 | 区分标题、赔率、换牌、对局、结算等状态并验证转换 | [`GAME-STATE-MACHINE-DESIGN.md`](./GAME-STATE-MACHINE-DESIGN.md) 给出候选状态；[`GAME-STATE-AND-TRANSITION-MAP-PHASE-29.md`](./GAME-STATE-AND-TRANSITION-MAP-PHASE-29.md) 记录唯一已验证转换为 `DEMO → ODDS`（按 `5` 后 CREDIT 增加）。状态机源码不在当前快照。 |
| 输入适配与按键映射 | 将策略动作转为游戏输入，并核实输入链路 | 当前操作台仅提供显式启用后的 `xdotool` 人工单键；旧 Python `UInput` 路径已收敛。历史审计[`RUNTIME-INPUT-AUDIT.md`](./RUNTIME-INPUT-AUDIT.md)记录 OS/MAME/端口层级仍有未验证项；[`INPUT-PIPELINE-DIAGNOSTIC-PHASE-14.md`](./INPUT-PIPELINE-DIAGNOSTIC-PHASE-14.md)指出焦点对独立测试窗口投递有影响，不能据此断言 MAME 已收到输入。 |
| 游戏规则/麻将规则引擎 | 表示牌、手牌、合法性，计算胡牌/听牌/出牌 | [`MAHJONG-RULE-ENGINE-REPORT.md`](./MAHJONG-RULE-ENGINE-REPORT.md) 记载过通用数据结构和占位接口；胡牌算法及本游戏具体规则未确认。当前没有 `mahjong/` 源码。 |
| 游戏配置与 DIP | 记录游戏设置、DIP 值及其影响 | [`PHASE-32-DIP-FINDINGS.md`](./PHASE-32-DIP-FINDINGS.md) 记录历史发现与推断；[`GAME-BACKEND-AND-SETTINGS-PHASE-29.md`](./GAME-BACKEND-AND-SETTINGS-PHASE-29.md) 记录设置入口未知。需要以目标运行环境重新核验，不能将报告直接视为当前运行时配置。 |
| 学习控制器/实验规划 | 排序未知问题、研究资料、规划受控实验 | [`AUTONOMOUS-LEARNING-CONTROLLER-DESIGN-PHASE-30.md`](./AUTONOMOUS-LEARNING-CONTROLLER-DESIGN-PHASE-30.md) 描述设计；[`PHASE-30-IMPLEMENTATION-REPORT.md`](./PHASE-30-IMPLEMENTATION-REPORT.md) 和 [`PHASE-31-IMPLEMENTATION-REPORT.md`](./PHASE-31-IMPLEMENTATION-REPORT.md) 声称曾有实现，但当前快照没有 `learning/` 源码或相应配置。 |
| 经验、证据与会话记录 | 保存真实观察、模拟、假设、输入前后状态和证据来源 | [`GAME-RULE-EVIDENCE-STORE-PHASE-30.md`](./GAME-RULE-EVIDENCE-STORE-PHASE-30.md)、[`GAME-SESSION-RECORDER-PHASE-30.md`](./GAME-SESSION-RECORDER-PHASE-30.md) 及 [`GAME-EXPERIENCE-SCHEMA.md`](./GAME-EXPERIENCE-SCHEMA.md) 给出数据模型；当前没有相应实现或运行数据目录。 |
| 模拟引擎 | 基于已验证规则做隔离、可复现的离线模拟 | [`SIMULATION-ENGINE-DESIGN.md`](./SIMULATION-ENGINE-DESIGN.md) 将其标为占位/受规则缺失限制；当前没有模拟器源码。 |
| 监控与故障恢复 | 发现进程退出或卡死，保留证据并恢复 | [`ERROR-RECOVERY.md`](./ERROR-RECOVERY.md) 记录故障分级及历史恢复案例；报告中提到的 supervisor 等脚本不在当前快照，无法确认当前存在自动恢复服务。 |
| 数据集、标注与评估 | 管理截图/标签/质量指标并评估识别效果 | 仓库有若干 JSON 指标或索引；[`VISION-PHASE-8-FINAL-REPORT.md`](./VISION-PHASE-8-FINAL-REPORT.md) 记载当时牌面标签为 UNKNOWN、模板库及分类器未完成。当前没有完整数据集目录和评估流水线。 |

## 7. 数据与外部依赖

### 当前代码直接使用的外部依赖

- Python 3（核心操作台只使用标准库）。
- 截图命令：`xwd`、`xwdtopnm`、`ffmpeg`。
- 人工单键输入命令：`xdotool`（只在启用人工输入后使用）。
- Shell 兼容启动器：`sh`、`python3`。
- 运行目标：MAME、兼容的图形会话、可访问的游戏窗口及正确的输入/权限设置。

当前快照没有依赖清单或环境锁定文件，以上依赖版本、部署步骤和可移植性尚未由仓库统一管理。

### 当前可见数据落点

- `~/.sdmg2-autoplay/auto_player.log`：操作台运行与输入操作日志。
- `~/.sdmg2-autoplay/captures/capture_*.png`：观测及手动按键前后的截图。
- 根目录 JSON 文件主要为测试结果、索引或指标；它们不是统一运行时数据库。

截图/日志位置可通过 CLI 参数调整；`DISPLAY`、`XAUTHORITY` 默认继承进程环境，也可显式配置。窗口 ID 必须由用户提供，不再硬编码。

## 8. 证据边界与风险点

1. **文档记载不代表源码存在**：阶段报告中提到的 `learning/`、`vision/`、`modules/` 等实现，在当前快照中找不到对应文件。
2. **当前程序不是自主玩家**：安全操作台没有状态/牌面识别器或策略；自动打牌明确未启用。
3. **遗留入口已收敛**：两个旧入口现转发到安全操作台，原 Shell 固定按键循环不再运行。
4. **操作台无法证明输入已生效**：单键流程记录输入前后截图，但游戏侧接收与状态改变仍需人工核验。
5. **游戏规则仍有未知项**：下注、对局阶段、胡牌与结算规则等并未形成足以驱动可靠策略的完整规则集。
6. **报告间可能存在时间差和结论差异**：例如较早阶段的状态、按键或 DIP 判断可能被后续发现更新。引用时应保留报告日期及证据等级。
7. **自动恢复能力不可从当前代码确认**：故障报告有历史案例，但当前没有随附的 supervisor 或恢复实现。

## 9. 建议的模块边界与端到端流程

当前操作台已实现截图、交互命令和人工单键安全门禁。要实现自主游戏，仍需把控制链扩展为可独立测试的边界，避免将截图、规则、输入和学习逻辑继续堆在单个循环中：

1. **运行配置**：集中管理 MAME 目标、显示环境、窗口定位、输入后端、超时及安全限制。
2. **采集层**：返回带时间戳和来源的截图；采集失败必须显式上报，不能复用旧图冒充本轮结果。
3. **感知层**：返回状态、牌面/数值候选、置信度和可追溯证据；低置信度输出 UNKNOWN。
4. **状态机**：仅接受证据支持的状态转换；未知状态禁止动作。
5. **规则与策略层**：规则结论标注 UNKNOWN、HYPOTHESIS、OBSERVED、VERIFIED 等证据等级；策略只使用满足门槛的规则。
6. **安全执行层**：检查授权、目标实例隔离、动作白名单、重试次数和操作前置状态，再调用统一输入适配器。
7. **结果验证层**：采集动作后的画面和游戏变量，区分“按键已发送”“输入已接收”“游戏状态已变化”。
8. **记录与学习层**：持久化操作前后证据、预测与结果；真实观测、离线模拟和推断分开保存，出现冲突时保留历史记录。
9. **监督与恢复层**：监控进程和画面活性，限制重启次数，并在恢复前保存现场证据。

目标闭环：

```text
采集 → 感知 → 状态/置信度校验 → 规则与策略 → 安全授权
  → 执行单步动作 → 再采集 → 验证结果 → 记录证据 → 更新知识
```

## 10. 相关文档索引

- 视觉模块概述：[`VISION-README.md`](./VISION-README.md)
- 状态机候选状态：[`GAME-STATE-MACHINE-DESIGN.md`](./GAME-STATE-MACHINE-DESIGN.md)
- 状态转换证据：[`GAME-STATE-AND-TRANSITION-MAP-PHASE-29.md`](./GAME-STATE-AND-TRANSITION-MAP-PHASE-29.md)
- 输入链路事实与限制：[`RUNTIME-INPUT-AUDIT.md`](./RUNTIME-INPUT-AUDIT.md)、[`INPUT-PIPELINE-DIAGNOSTIC-PHASE-14.md`](./INPUT-PIPELINE-DIAGNOSTIC-PHASE-14.md)
- 规则引擎状态：[`MAHJONG-RULE-ENGINE-REPORT.md`](./MAHJONG-RULE-ENGINE-REPORT.md)
- 规则证据分级：[`GAME-RULE-EVIDENCE-STORE-PHASE-30.md`](./GAME-RULE-EVIDENCE-STORE-PHASE-30.md)
- 经验记录模型：[`GAME-EXPERIENCE-SCHEMA.md`](./GAME-EXPERIENCE-SCHEMA.md)、[`GAME-SESSION-RECORDER-PHASE-30.md`](./GAME-SESSION-RECORDER-PHASE-30.md)
- 自主学习设计：[`AUTONOMOUS-LEARNING-CONTROLLER-DESIGN-PHASE-30.md`](./AUTONOMOUS-LEARNING-CONTROLLER-DESIGN-PHASE-30.md)
- DIP 调查：[`PHASE-32-DIP-FINDINGS.md`](./PHASE-32-DIP-FINDINGS.md)、[`PHASE-32-FINAL-REPORT.md`](./PHASE-32-FINAL-REPORT.md)
- 故障处理：[`ERROR-RECOVERY.md`](./ERROR-RECOVERY.md)
- 当前脚本清单：[`ai_auto_play.py`](./ai_auto_play.py)、[`ai-stable.sh`](./ai-stable.sh)
