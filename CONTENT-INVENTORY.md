# sdmg2-test 项目完整内容清单

生成时间：2026-10-18
本地路径：`~/workspace/sdmg2-test/`（已同步云端全部内容）
云端路径：`zhang-new2:~/sdmg2-test/`

---

## 一、Python模块（43个）

### 核心控制
| 文件 | 功能 | 状态 |
|------|------|------|
| `modules/controls.py` | uinput控制器，press_key/press_key_closed_loop/auto_refill_credits | ✅ 已修复（数字键别名、前台检查、返回值） |
| `modules/vision.py` | VisionEngine截图+ArcadeDigitMatcher数字识别 | ✅ 锚点法、颜色掩膜分割 |
| `modules/anchor_finder.py` | 锚点定位（BET/CREDIT文字标签） | ✅ 全图多尺度+比例ROI |
| `modules/screen_splitter.py` | 全屏捕获+内存比例分割 | ✅ 实验性，未完全验证 |
| `modules/bet_verifier.py` | BET三态验证器（VERIFIED/NOT_VERIFIED/UNKNOWN） | ✅ |
| `modules/safe_reader.py` | SafeCreditBetReader故障默认上分 | ✅ |
| `modules/game_logic.py` | StandardGameFlow标准开局流程 | ✅ |
| `modules/digit_detector.py` | 绿色数字直接检测（方案3） | ✅ 实验性 |
| `modules/ocr_digit.py` | Tesseract OCR数字识别 | ✅ 实验性，不接入控制 |

### AI与策略
| 文件 | 功能 |
|------|------|
| `modules/ai_engine.py` | 三启发式打牌+换牌策略 |
| `modules/game_agent.py` | 上一版架构Agent |
| `modules/ai_loop.py` | AI主循环 |
| `modules/gemma_analyzer.py` | Gemma分析器 |
| `modules/decision_log.py` | 决策日志 |
| `modules/exchange_strategy.py` | 换牌策略 |
| `modules/fan_db.py` | 番种数据库 |
| `modules/target_config.py` | 目标配置 |

### 数据与状态
| 文件 | 功能 |
|------|------|
| `modules/database.py` | SQLite WAL数据库 |
| `modules/db_schema.py` | 表结构定义 |
| `modules/game_state.py` | 游戏状态机 |
| `modules/game_monitor.py` | 游戏监控 |
| `modules/game_controller.py` | 游戏控制器 |
| `modules/credit_manager.py` | 信用管理 |
| `modules/doubleup_db.py` | 比倍数据库 |
| `modules/action_executor.py` | 动作执行器 |
| `modules/state_detector.py` | 状态检测（Copilot版，需修路径） |
| `modules/input_adapter.py` | 输入适配器 |
| `modules/local_ai_controller.py` | 本地AI控制器 |

---

## 二、测试文件（9个）

| 文件 | 测试内容 | 状态 |
|------|----------|------|
| `tests/test_bet_verifier.py` | 三态验证器状态机 | ✅ 4项通过（模拟） |
| `tests/test_closed_loop.py` | 闭环输入验证 | ✅ 4项通过（模拟） |
| `tests/test_game_logic.py` | 标准开局流程 | ✅ 4项通过（模拟） |
| `tests/test_ocr_digit.py` | OCR低置信度返回未知 | ✅ 通过（Copilot） |
| `tests/test_digit_matcher.py` | 数字模板匹配 | 待验证 |
| `tests/test_p5_acceptance.py` | 按5验收测试 | 待验证 |
| `tests/test_target_config.py` | 目标配置 | 待验证 |
| `tests/test_tile_codec.py` | 牌面编码 | 待验证 |
| `tests/test_winning.py` | 胡牌判定 | 待验证 |

**注意**：模拟测试≠真实准确率，用户已明确指出。

---

## 三、工具脚本（11个）

| 文件 | 功能 |
|------|------|
| `tools/main.py` | AutoPlayBot主入口（状态机） |
| `tools/ai_launcher.py` | tkinter启动器（单实例） |
| `tools/diagnose.py` | 失败阶段诊断 |
| `tools/collect_templates.py` | 模板采集 |
| `tools/collect_tiles.py` | 牌面采集 |
| `tools/extract_template.py` | 模板提取 |
| `tools/label_tiles.py` | 牌面标注 |
| `tools/dataset_audit.py` | 数据集审计 |
| `tools/config.py` | 配置 |
| `tools/data_tools.py` | 数据工具 |
| `tools/settings.py` | 设置 |

---

## 四、数字模板

### digits_v2/（实验性，10个齐全）
| 模板 | 来源 | 状态 |
|------|------|------|
| digit_0.png - digit_9.png | 已核对截图（125-145） | ✅ 实验数据 |
| metadata.json | 采集元数据 | ✅ |
| README.md | 说明+验证失败记录 | ✅ |

**验证失败**：9→8误判（0.831分），高分误判，需改进拒识。

### digits/（旧版，22个）
- credit_0-10.png, bet_0-10.png
- **问题**：credit_2.png实际是"1"，标签错乱
- 状态：保留作对照，不使用

### 锚点模板
- `templates/label_bet.png`：BET文字（匹配1.000）
- `templates/label_credit.png`：CREDIT文字

---

## 五、文档（209个MD）

### 核心文档
- `COPILOT_PROMPT.md`：给Copilot的协作提示
- `COPILOT_ANCHOR_PROBLEM.md`：锚点问题诊断记录
- `CONTENT-INVENTORY.md`：本清单
- `PROJECT-ARCHITECTURE.md`：架构（需更新C++表述）

### 规则与证据（节选）
- `GAME-RULES-OBSERVED.md`：已验证规则
- `BET-CREDIT-POLICY.md`：投注信用政策
- `CURRENT-GAME-STATE.md`：当前游戏状态
- `INPUT-MAPPING-INVENTORY.md`：键位映射表

### 诊断报告（节选）
- `AUDIT-REPORT-2026-10-14.md`
- `BET-ISOLATED-ENVIRONMENT-REPORT.md`
- `24H-TEST-LOG.md`

---

## 六、关键修复记录（2026-10-18）

| 提交 | 内容 |
|------|------|
| `7b47275` | 前台检查排除VSCode误判 |
| `b49a4b7` | 数字键别名+auto_refill检查返回值 |
| `30129e6` | digits_v2实验模板（9误判记录） |
| `80ea5b3` | 补齐10个数字 |
| `3472f5e` | splitter接入识别 |
| `da70eab` | ROI比例校准 |
| `4bd8bfb` | MameScreenSplitter |
| `9afb13e` | segment_digits颜色掩膜 |
| `1f23a88` | 锚点法全图多尺度 |

---

## 七、待解决问题

### P0（阻塞）
1. **批量输入丢失**：10次按键仅6次成功（60%），需闭环验证

### P1（识别）
2. **拒识能力**：9→8误判0.831分，阈值0.7太低，未知数字会冒充
3. **模板验证**：digits_v2需独立截图验证整套

### P2（工程）
4. **C++模块**：比Python慢5倍，建议删除
5. **state_detector.py**：硬编码路径需修
6. **GitHub同步**：gh_push.py静默失败，用API直接PUT

---

## 八、运行方式

```bash
# SSH到云端
ssh -F ~/.ssh/config zhang-new2

# 重启游戏+AI
bash ~/sdmg2-test/restart.sh

# 单键测试
cd ~/sdmg2-test && DISPLAY=:0 python3 -c "
import sys; sys.path.insert(0, 'modules')
from controls import Controller
c = Controller()
print(c.press_key('5'))
"
```

**要求**：MAME最大化，DISPLAY=:0
