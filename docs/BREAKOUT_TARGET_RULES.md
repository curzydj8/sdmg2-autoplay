# 爆机目标规则调查

**日期**：2026-10-17

## 一、500目标

| 项 | 值 |
|----|-----|
| 规则ID | RULE-JACKPOT-500 |
| 描述 | Double Up奖池上限500 |
| 来源 | DIP: Double Up Jackpot=500 |
| 验证方法 | Tab菜单→DIP Switches实测 |
| 状态 | verified |

## 二、2000目标

| 项 | 值 |
|----|-----|
| 规则ID | RULE-CREDIT-2000 |
| 描述 | Credit上限2000 |
| 来源 | DIP: Credit Limit=2000 |
| 验证方法 | Tab菜单→DIP Switches实测 |
| 状态 | verified |
| 说明 | 这是信用上限，不是奖池目标。用户确认可作为会话目标使用 |

## 三、关键区分

- **500**：比倍奖池爆机线（游戏内Jackpot）
- **2000**：持有信用上限（DIP Credit Limit）
- 两者来源不同，不得混淆
- 策略必须分别处理

## 四、待验证

- 2000作为奖池目标是否可通过DIP修改：unknown
- 不同ROM版本差异：unknown
