# 实施计划

## P0：工程审计 ✅ 已完成
- [x] 代码/模块/模板/数据库审计
- [x] docs/PROJECT_AUDIT.md
- [x] docs/CURRENT_STATUS.md

## P1：统一数据接口（进行中）
- [x] tile_codec（牌编码）
- [x] game_state（状态结构）
- [ ] SQLite schema（10表）
- [ ] tests/单元测试框架

## P2：补齐视觉识别
- [ ] 模板覆盖率统计（21/34）
- [ ] 缺失模板清单
- [ ] 模板补全工具
- [ ] 识别混淆矩阵

## P3：完成本地规则
- [x] winning_db（和牌判定）
- [x] fan_db（算番）
- [ ] 听牌枚举
- [ ] 合法动作过滤
- [ ] 比倍流程验证

## P4：完成执行闭环
- [x] uinput按键验证
- [ ] player状态机（11状态）
- [ ] --dry-run/--step/--record/--autoplay
- [ ] 动作验证与恢复

## P5：数据采集
- [ ] SQLite记录
- [ ] 对局日志
- [ ] JSONL导出

## P6：策略优化
- [ ] 4番以上策略
- [ ] Gemma异步复盘

## 验收
见 docs/ACCEPTANCE.md（待建）
