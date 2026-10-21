# 爆机目标验证

## 500目标验证

| 项 | 结果 |
|----|------|
| 设置方法 | Tab→DIP Switches→Double Up Jackpot |
| 当前值 | 500 |
| 生效确认 | 游戏比倍画面显示奖池上限500 |
| 状态 | verified |

## 2000目标验证

| 项 | 结果 |
|----|------|
| 设置方法 | Tab→DIP Switches→Credit Limit |
| 当前值 | 2000 |
| 说明 | 这是信用上限，非奖池目标 |
| 作会话目标 | 用户确认可用 |
| 状态 | verified（作信用上限）/ unknown（作奖池目标） |

## 目标切换测试

- target_config.py 500↔2000切换：通过
- doubleup_db读取统一配置：通过
- CLI --target-score：兼容
