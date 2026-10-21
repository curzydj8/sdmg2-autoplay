# 本地AI自主游戏框架

**职责分工**（2026-10-17确立）

## 本地实时AI（唯一游戏操作者）

- 模块：`modules/local_ai_controller.py`
- 职责：感知→决策→执行→验证→记录
- 独立运行，不依赖Muse，不等待Gemma
- 单实例锁：`/tmp/sdmg2_ai.lock`
- 输入：uinput（已验证）

## Gemma（异步分析）

- 模块：`modules/gemma_analyzer.py`
- 职责：分析已完成对局，输出建议（待验证）
- 不发送按键，不修改策略，不阻塞实时循环
- 通过knowledge表提交结果（verified=0）

## Muse（框架维护）

- 不参与游戏操作
- 只负责：检查代码、维护框架、验证结果、生成报告
- 不发送按键，不做实时决策

## 数据流

```
本地AI → SQLite → Gemma分析 → knowledge表(待验证)
                ↓
           Muse验证 → 策略更新 → 本地AI
```

## 安全

- 单实例锁防止多进程冲突
- 策略版本化，可回滚
- Gemma失败时本地AI继续用旧策略
