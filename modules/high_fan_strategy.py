#!/usr/bin/env python3
"""
4番策略 v1.0
三种策略：基线 / 高番优先 / 平衡

规则验证状态：
- verified：清一色(8)、混一色(5)、七对子(3)、对对和(3)、立直(1)、自摸(1)
- provisional：役满系（75番，未实机验证）
- unknown：其他特殊规则
"""
from collections import Counter


# 策略配置
STRATEGIES = {
    "baseline": {
        "version": "v1",
        "target_fan": 0,
        "high_fan_weight": 0.0,
        "hand_efficiency_weight": 1.0,
        "desc": "基线：只考虑手牌效率，不追高番",
    },
    "high_fan": {
        "version": "v1",
        "target_fan": 4,
        "high_fan_weight": 0.7,
        "hand_efficiency_weight": 0.3,
        "desc": "高番优先：优先保留4番以上路线",
    },
    "balanced": {
        "version": "v1",
        "target_fan": 4,
        "high_fan_weight": 0.4,
        "hand_efficiency_weight": 0.6,
        "desc": "平衡：综合高番潜力与听牌效率",
    },
}


def score_action(codes_14, discard_idx, strategy="balanced"):
    """
    候选出牌评分
    :return: (总分, 分项)
    """
    cfg = STRATEGIES[strategy]
    remaining = codes_14[:discard_idx] + codes_14[discard_idx+1:]

    # 手牌效率分：听牌数
    from winning_db import find_ting_tiles
    ting = find_ting_tiles(remaining)
    eff_score = min(len(ting) * 10, 100)

    # 高番潜力分
    counts = Counter(remaining)
    suits = {"wan": 0, "tiao": 0, "bing": 0}
    for c in remaining:
        for s in suits:
            if c.endswith(s):
                suits[s] += 1
    max_suit = max(suits.values())
    # 清一色潜力
    if max_suit >= 10:
        fan_score = 90
    elif max_suit >= 8:
        fan_score = 60
    elif sum(1 for v in counts.values() if v >= 2) >= 4:
        fan_score = 50  # 对对和潜力
    else:
        fan_score = 20

    total = (fan_score * cfg["high_fan_weight"] +
             eff_score * cfg["hand_efficiency_weight"])

    detail = {
        "fan_score": fan_score,
        "eff_score": eff_score,
        "ting_count": len(ting),
        "strategy": strategy,
    }
    return round(total, 1), detail


def choose_discard(codes_14, strategy="balanced"):
    """选择最佳出牌"""
    best = None
    best_score = -1
    best_detail = None
    for i in range(len(codes_14)):
        score, detail = score_action(codes_14, i, strategy)
        if score > best_score:
            best_score = score
            best = i
            best_detail = detail
    return best, codes_14[best], best_score, best_detail


if __name__ == "__main__":
    # 测试：14张
    hand = ["1wan","1wan","1wan","2wan","3wan","4wan",
            "5bing","5bing","6bing","7bing",
            "2tiao","3tiao","8wan","9wan"]
    for s in ["baseline", "high_fan", "balanced"]:
        idx, tile, score, detail = choose_discard(hand, s)
        print(f"{s}: 打{tile}(槽{idx}) 得分{score} {detail}")
