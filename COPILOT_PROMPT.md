# 给Copilot的任务：超级大满贯II自主打牌项目

## 项目背景
这是一个MAME模拟器《超级大满贯II》的自主打牌AI项目。目标是让AI自动完成：上分→押注→开始游戏→识别手牌→打牌→结算的完整流程。

## 当前状态（已验证）
- `modules/controls.py`：uinput内核级按键（唯一有效方式，xdotool/pyautogui无效）
- `modules/game_logic.py`：`StandardGameFlow`类，标准开局流程（CREDIT 0-10上500→BET到10→START）
- `modules/bet_verifier.py`：BET三态验证器（VERIFIED/NOT_VERIFIED/UNKNOWN）
- `modules/vision.py`：`read_credit_bet()`模板匹配（当前返回None，不可靠）
- `tools/main.py`：主状态机（INIT→BET→PLAY→CHECK_RESULT）

## 已知问题（需要你解决）

### 问题1：BET数字识别返回None
`vision.py`的`read_credit_bet()`始终返回`(None, None)`。
- BET数字实际位置：屏幕坐标(938, 651)，绿色数字
- CREDIT数字位置：屏幕坐标(423, 652)，绿色数字
- 现有22张数字模板在`templates/digits/`（credit_0-10.png, bet_0-10.png）
- 需要诊断：是模板加载失败？坐标裁切错误？还是匹配阈值问题？
- `bet_verifier.py`已能区分6种失败模式（no_vision/no_method/exception/none_result/bad_format/ok），用它来定位

### 问题2：state_detector.py硬编码路径
你创建的`modules/state_detector.py`有以下问题：
- 硬编码`~/workspace/sdmg2-test/screenshots`不存在
- 用PIL而非项目统一的cv2/numpy
- 引用不存在的`states/recognition-rules.md`
请修复为使用相对路径和cv2。

## 任务要求
1. **小步迭代**：一次只解决一个问题，提交前列出修改文件、测试命令、实测结果
2. **不要**重写整个控制循环或视觉模块
3. **测试优先**：每个修复都要有对应的测试
4. **证据纪律**：不要声称"已完成"，除非有实测证据

## 第一个任务
诊断`read_credit_bet()`为什么返回None。使用`bet_verifier.py`的失败模式区分功能，确定是：
- 模板文件缺失？
- 坐标错误？
- 匹配分数过低？
- 异常被吞？

只诊断，不修复。报告发现。
