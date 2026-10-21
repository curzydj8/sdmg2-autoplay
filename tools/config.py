#!/usr/bin/env python3
"""
游戏设置程序 config.py

对应用户流程图：Ubuntu终端启动 → 1. 运行游戏设置程序
- 设置初始代币 / 积分上限
- 调整游戏难度 / 胜率参数
- 保存配置到本地 (JSON/SQLite)
"""
import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CONFIG_JSON = os.path.expanduser("~/sdmg2-test/data/game_config.json")
DB_PATH = "/home/zhangdawei/workspace/sdmg2-test/data/sdmg2.db"

DEFAULTS = {
    "credit_limit": 2000,      # 积分上限（DIP）
    "jackpot": 500,            # 比倍奖池上限（DIP）
    "min_bet": 1,              # 最小押分（DIP）
    "max_bet": 10,             # 最大押分（用户流程图：1~10分）
    "default_bet": 5,          # 默认押分
    "doubleup_enabled": True,  # 比倍开关（DIP）
    "target_score": 500,       # 目标分数
    "difficulty": "normal",    # 难度（待DIP确认）
}


def load():
    """加载配置（JSON优先，缺失用默认值）"""
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON) as f:
                cfg.update(json.load(f))
        except:
            pass
    return cfg


def save(cfg):
    """保存到JSON + SQLite"""
    os.makedirs(os.path.dirname(CONFIG_JSON), exist_ok=True)
    with open(CONFIG_JSON, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    # 同步到DB strategy_configs（如果表存在）
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        conn.execute("""
            INSERT OR REPLACE INTO strategy_configs
            (id, version, bet_strong, bet_normal, bet_weak, is_active)
            VALUES (1, 'v1', ?, ?, ?, 1)
        """, (cfg.get("max_bet", 10), cfg.get("default_bet", 5),
              cfg.get("min_bet", 1)))
        conn.commit()
        conn.close()
    except:
        pass
    print(f"配置已保存: {CONFIG_JSON}")


def show():
    cfg = load()
    print("=== 游戏设置 ===")
    for k, v in cfg.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="游戏设置程序")
    p.add_argument("--show", action="store_true", help="显示当前配置")
    p.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="设置项")
    a = p.parse_args()
    if a.show or not a.set:
        show()
    if a.set:
        k, v = a.set
        cfg = load()
        # 尝试转数字
        try:
            v = int(v)
        except:
            try:
                v = float(v)
            except:
                pass
        cfg[k] = v
        save(cfg)
