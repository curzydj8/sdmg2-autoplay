# 爆机目标配置

## 目标定义

| 目标 | 模式 | 来源 | 状态 |
|------|------|------|------|
| 500 | jackpot | DIP: Double Up Jackpot | verified |
| 2000 | credit_limit | DIP: Credit Limit | verified |

## 配置文件

`data/target_config.json`

```json
{
  "target_score": 500,
  "target_mode": "jackpot",
  "target_source": "user",
  "target_verified": true
}
```

## CLI

```bash
python3 modules/target_config.py 500   # 设500
python3 modules/target_config.py 2000  # 设2000
python3 modules/player_v2.py --target-score 2000 --dry-run
```

## 模块集成

- `doubleup_db.should_double_up()`：读取统一配置，不再硬编码
- `player_v2 --target-score`：与配置文件兼容
- `game_sessions.target_score`：记录实际使用目标（v3迁移）

## 安全

配置与游戏实际不一致时，暂停自动比倍。
