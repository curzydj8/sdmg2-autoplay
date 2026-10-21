# SDMG2 Autonomous Mahjong Agent — 项目审计报告

**审计日期**：2026-10-17
**审计人**：Muse（首席架构师）
**项目路径**：`~/workspace/sdmg2-test/`

---

## 一、代码模块清单

### 新模块（2026-10-17 当日新建，9个）

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| tile_codec | modules/tile_codec.py | ✅ 可用 | 牌编码 1wan/1tiao/1bing/dong/bai，自测通过 |
| game_state | modules/game_state.py | ✅ 可用 | 全状态编码，自测通过 |
| winning_db | modules/winning_db.py | ✅ 可用 | 胡牌判定（标准/七对/国士），3测试通过 |
| fan_db | modules/fan_db.py | ✅ 可用 | 算番，2测试通过 |
| ops_db | modules/ops_db.py | ✅ 可用 | 操作知识库，JSON已生成 |
| screen_db | modules/screen_db.py | ✅ 可用 | 画面库+上分策略 |
| doubleup_db | modules/doubleup_db.py | ✅ 可用 | 比倍规则（爆机流） |
| timing_db | modules/timing_db.py | ✅ 可用 | 时序频率库 |
| player | modules/player.py | ⚠️ 框架 | 集成玩家，待画面识别完善 |

### 旧模块（此前已存在，9个）

| 模块 | 状态 |
|------|------|
| mahjong_vision.py | ⚠️ 有18模板，待与新建库整合 |
| mahjong_strategy.py | ⚠️ 规则策略，将被本地库+Gemma替代 |
| state_detector.py | 待审计 |
| screen_reader.py | 待审计 |
| action_executor.py | 待审计 |
| game_controller.py | 待审计 |
| input_adapter.py | 待审计 |
| recovery_manager.py | 待审计 |

### 视觉子系统（vision/）

7个文件：capture_loader, state_classifier, hand_region, tile_detector, tile_classifier, confidence — 待审计是否与新模板库兼容。

---

## 二、模板库

- **本地**：18张（`templates/`）
- **服务器**：21张（`~/sdmg2-test/templates/`，含当日实机提取10张）
- **缺失**：约13张（1-7wan部分、1/4/6/7/8/9bing、1/4/5/6/7/8/9tiao、红中、白板）
- **工具**：`template_builder.py` 可用

---

## 三、数据库

- **SQLite**：无（任务书要求10张表，待建）
- **JSON知识库**：4个（ops/screen/doubleup/timing），已生成

---

## 四、测试

- **tests/目录**：不存在，待建
- **模块自测**：tile_codec/winning_db/fan_db/ops_db/screen_db/doubleup_db/timing_db 均有 `__main__` 自测，通过

---

## 五、MAME与游戏

- **版本**：0.285
- **ROM**：`~/mame/roms/sdmg2.zip`（用户当日找到对版）
- **驱动**：igs017.cpp（Chaoji Da Manguan II, China V765C）
- **状态**：可运行，已进对局实测

---

## 六、输入方案

- **uinput**：✅ 可用（`/dev/uinput`，python3-evdev已装，用户已加input组）
- **已验证**：5=投币，1=开始，a-n=选牌，enter=确认，tab=菜单，esc=取消
- **xdotool**：❌ 无效（MAME走底层输入，收不到X11合成按键）

---

## 七、Gemma

- **模型**：gemma3:4b（3.4GB）
- **API**：http://localhost:11434/api/generate
- **实测**：文本48秒，视觉可用（读懂ODDS屏）
- **定位**：异步分析，不进实时出牌路径

---

## 八、文档资产

100+份历史MD（Phase 12-32），含规则验证、输入测试、DIP审计等。需去重整合到新docs/。

---

## 九、已知问题

1. 模板库不全（21/34）
2. 画面自动识别未实现（player.py待完善）
3. SQLite未建
4. tests/未建
5. 新旧模块（mahjong_vision vs 新库）待整合
