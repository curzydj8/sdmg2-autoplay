# Copilot 全权操作授权书

**授权人**：Zhang（项目所有者）
**授权时间**：2026-10-18
**授权对象**：VSCode Copilot（Ubuntu云端 `~/sdmg2-test/`）

---

## 授权范围

### 最高权限
- ✅ 可操作整个系统（`~/sdmg2-test/`及相关系统）
- ✅ 可使用所有工具（终端、文件、Python、系统命令）
- ✅ 可修改代码、创建文件、运行测试、重启服务
- ✅ 可执行MAME游戏操作（按键、截图、状态检查）

### 无需确认
- **不用用户确认**，直接操作
- 按实际操作找问题、解决问题
- 小步迭代，快速推进

### 目标
**先把整个项目跑通**（端到端）：
1. MAME启动 → ODDS画面
2. 上分（CREDIT>10）
3. 押注到BET=10
4. 按START开始游戏
5. 识别手牌 → AI打牌
6. 完整一局

跑通后，再解决Copilot无法控制的问题（如需用户手动操作的部分）。

---

## 当前状态（交接时）

### 已解决
- ✅ P0-1输入：uinput可达MAME（单键+5次小批量验证）
- ✅ 前台检查：排除VSCode误判
- ✅ 数字键别名、返回值检查
- ✅ 锚点法、颜色分割、splitter架构

### 待解决
1. **批量输入丢失**：10次仅6次成功（60%），需闭环验证
2. **拒识能力**：9→8误判0.831分，阈值太低
3. **digits_v2**：10数字齐全，实验数据，需独立验证
4. **模板标签**：旧digits/中credit_2.png实际是"1"

### 关键文件
- `CONTENT-INVENTORY.md`：完整内容清单
- `modules/controls.py`：输入控制（已修复）
- `modules/vision.py`：识别（待改进）
- `templates/digits_v2/`：实验模板

---

## 操作指南

### 1. 先验证输入可靠性
```bash
cd ~/sdmg2-test
# MAME需在前台，DISPLAY=:0
DISPLAY=:0 python3 -c "
import sys; sys.path.insert(0, 'modules')
from controls import Controller
c = Controller()
# 单键测试
print('单键:', c.press_key('5'))
"
```

### 2. 再验证识别
```bash
# 用digits_v2测试已采集截图
DISPLAY=:0 python3 tests/test_ocr_digit.py
```

### 3. 端到端跑通
```bash
bash restart.sh  # 重启游戏+AI
# 观察 /tmp/autobot.log
```

---

## 红线（仍需遵守）

- ❌ 不重装MAME/不换ROM/不重置存档
- ❌ 不删除数据（统计保留失败记录）
- ❌ 密码不写日志/不提交
- ⚠️ 批量删除前备份

---

## 报告要求

每完成一个里程碑，在 `COPILOT_PROGRESS.md` 记录：
- 做了什么
- 测试结果（截图/日志）
- 遇到的问题
- 下一步

**开始工作吧，不用等确认。**
