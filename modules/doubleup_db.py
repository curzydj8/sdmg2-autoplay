#!/usr/bin/env python3
"""
比倍（Double Up）规则数据库 v1.0
基于 DIP 设置 + ODDS 屏观测

DIP 设置：
- Double Up Jackpot: 500
- Double Up Game: On
- Double Up Game Name: Continue Play
"""
import os
import json

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/doubleup_knowledge.json")

# 比倍规则（基于观测 + IGS 通用规则）
DOUBLEUP_RULES = {
    "trigger": {
        "desc": "和牌后触发",
        "condition": "3分以上（3番+），中滿貫，可玩大滿貫",
        "source": "ODDS屏：'3分以上，中滿貫，可玩大滿貫'",
    },
    "jackpot": {
        "value": 500,
        "desc": "比倍奖池上限",
        "source": "DIP: Double Up Jackpot=500",
    },
    "game_name": {
        "value": "Continue Play",
        "desc": "比倍游戏名",
        "source": "DIP: Double Up Game Name",
    },
    "flow": [
        {
            "step": 1,
            "desc": "和牌结算后，提示是否比倍",
            "action": "选择 YES（比倍）或 NO（收分）",
            "key": "待验证",
        },
        {
            "step": 2,
            "desc": "比倍画面：选一张牌",
            "action": "按 a-n 或方向键选牌",
            "key": "待验证",
        },
        {
            "step": 3,
            "desc": "与庄家比大小",
            "rule": "大赢、平为和、小输",
            "detail": "待实机验证具体比法（牌点/花色）",
        },
        {
            "step": 4,
            "desc": "赢了可继续比倍或收分",
            "action": "选择继续或收分",
            "limit": "到500奖池上限强制收分",
        },
    ],
    "strategy": {
        "desc": "比倍策略：爆机流",
        "goal": "爆机（500奖池），不比倍永远爆不了",
        "rules": [
            "一律比倍，直到奖池到500爆机",
            "只有奖池满500才收分",
            "输了就输了，下一局再来",
        ],
        "note": "2026-10-17 用户定：要玩爆机，保守策略永爆不了",
    },
    "odds_bet": {
        "desc": "大滿貫BET",
        "value": 4,
        "source": "ODDS屏显示：大滿貫BET 4",
        "note": "与比倍相关的押注，待验证",
    },
}


def should_double_up(win_points, current_pool=0):
    """
    是否比倍决策：爆机流（目标从统一配置读取）
    :param win_points: 和牌得分
    :param current_pool: 当前比倍池
    :return: (bool, 原因)
    """
    try:
        from target_config import get_target
        target = get_target()
    except ImportError:
        target = 500  # 回退
    # 爆机流：奖池没满就一直比
    if current_pool >= target:
        return False, f"奖池{current_pool}已满{target}，爆机收分！"
    return True, f"奖池{current_pool}/{target}，继续比倍冲爆机"


def save_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(DOUBLEUP_RULES, f, ensure_ascii=False, indent=2)
    print(f"比倍库已保存: {DB_PATH}")


if __name__ == "__main__":
    save_db()
    print("\n测试:")
    print(should_double_up(50))
    print(should_double_up(350))
    print(should_double_up(150, 450))
