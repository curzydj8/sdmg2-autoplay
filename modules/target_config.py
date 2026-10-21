#!/usr/bin/env python3
"""
爆机目标统一配置 v1.0
- target_score: 500 或 2000
- 不再硬编码500
- 所有模块读取同一配置
"""
import os
import json

CONFIG_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/target_config.json")

# 默认配置
DEFAULT_CONFIG = {
    "target_score": 500,
    "target_mode": "jackpot",  # jackpot(500) 或 credit_limit(2000)
    "target_source": "user",
    "target_verified": True,
    "game_version": "sdmg2",
    "strategy_version": "v1",
    "updated_at": "",
}

# 目标定义
TARGETS = {
    500: {
        "mode": "jackpot",
        "desc": "Double Up奖池上限",
        "source": "DIP: Double Up Jackpot=500",
        "verified": True,
    },
    2000: {
        "mode": "credit_limit",
        "desc": "Credit持有上限",
        "source": "DIP: Credit Limit=2000",
        "verified": True,
    },
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(target_score, source="user"):
    if target_score not in TARGETS:
        raise ValueError(f"不支持的目标: {target_score}，可选 {list(TARGETS.keys())}")
    t = TARGETS[target_score]
    cfg = {
        "target_score": target_score,
        "target_mode": t["mode"],
        "target_source": source,
        "target_verified": t["verified"],
        "game_version": "sdmg2",
        "strategy_version": "v1",
        "updated_at": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"目标已设为 {target_score}（{t['desc']}）")
    return cfg


def get_target():
    """获取当前目标分数"""
    return load_config()["target_score"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        save_config(int(sys.argv[1]))
    else:
        cfg = load_config()
        print(f"当前目标: {cfg['target_score']}（{cfg['target_mode']}）")
        print(f"验证状态: {'已验证' if cfg['target_verified'] else '未验证'}")
