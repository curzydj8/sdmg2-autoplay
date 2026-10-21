#!/usr/bin/env python3
"""
换牌策略 v1.0
- v1占位：换前3张
- 自适应：按牌面strength决定换几张、换哪几张

规则（任务书）：
- 可换0-13张
- 好牌（对子/顺子多）：少换或不换
- 烂牌（散牌多）：多换
- 听牌：保留听牌型
"""
from collections import Counter


def evaluate_hand_strength(codes):
    """
    评估牌面strength
    :return: (strength, 详情) strength: strong/normal/weak
    """
    counts = Counter(codes)
    # 对子/刻子数
    pairs_trips = sum(1 for v in counts.values() if v >= 2)
    # 顺子潜力（简化：同花色连续）
    # 孤张数
    isolated = sum(1 for v in counts.values() if v == 1)

    if pairs_trips >= 4:
        return "strong", f"{pairs_trips}组对刻"
    if pairs_trips >= 2 and isolated <= 6:
        return "normal", f"{pairs_trips}组对刻，{isolated}孤张"
    return "weak", f"{isolated}孤张"


def decide_exchange(codes, adaptive=False, fixed_count=3):
    """
    决定换牌
    :param codes: 14张编码（换牌阶段通常是14张）
    :param adaptive: 是否自适应
    :param fixed_count: 固定模式换几张
    :return: (换牌索引列表, 原因)
    """
    if not adaptive:
        # v1占位：换前3张
        idx = list(range(min(fixed_count, len(codes))))
        return idx, f"v1占位：换前{fixed_count}张"

    # 自适应
    strength, detail = evaluate_hand_strength(codes)
    counts = Counter(codes)

    if strength == "strong":
        return [], f"强牌（{detail}）：不换"

    # 找孤张换
    isolated_idx = [i for i, c in enumerate(codes) if counts[c] == 1]

    if strength == "normal":
        # 换一半孤张
        n = min(len(isolated_idx) // 2, 6)
    else:  # weak
        # 全换孤张，最多13张
        n = min(len(isolated_idx), 13)

    idx = isolated_idx[:n]
    return idx, f"{strength}（{detail}）：换{n}张孤张"


if __name__ == "__main__":
    # 强牌
    strong = ["1wan"]*3 + ["2wan"]*2 + ["3bing"]*3 + ["4tiao"]*2 + ["5tiao"]*2 + ["dong"]*2
    print("强牌:", decide_exchange(strong, adaptive=True))
    # 烂牌
    weak = ["1wan","3wan","5wan","7wan","9wan","2tiao","4tiao","6tiao","1bing","3bing","dong","nan","xi","bei"]
    print("烂牌:", decide_exchange(weak, adaptive=True))
    # 占位
    print("占位:", decide_exchange(weak, adaptive=False))
