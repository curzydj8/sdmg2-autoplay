#!/usr/bin/env python3
"""
番数/赔率数据库 v1.0
基于 ODDS 屏实测赔率，本地计算，不用问 AI。

赔率表（实测）：
  75: 役满
  30: 三倍满
  15: 倍满
  8: 跳满
  5: 满贯
  4: （大滿貫BET相关）
  3: 三番
  2: 二番
  1: 一番
"""
from collections import Counter

# 赔率 → 番数名
ODDS_TABLE = {
    75: "役满",
    30: "三倍满",
    15: "倍满",
    8: "跳满",
    5: "满贯",
    3: "三番",
    2: "二番",
    1: "一番",
}

# 役种 → 番数（基于日麻规则+本游戏ODDS推断）
YAKU_FAN = {
    # 役满（75）
    "国士无双": 75,
    "大三元": 75,
    "大四喜": 75,
    "字一色": 75,
    "清老头": 75,
    "绿一色": 75,
    "四暗刻": 75,
    # 高番
    "清一色": 8,      # 跳满级
    "混一色": 5,      # 满贯级
    # 中番
    "七对子": 3,
    "对对和": 3,
    # 低番
    "立直": 1,
    "门清自摸": 1,
    "平和": 1,
    "断幺九": 1,
    "一杯口": 1,
    "役牌": 1,        # 中/发/白/场风刻
}


def calculate_fan(codes, win_type, is_riichi=False, is_tsumo=False, is_closed=True):
    """
    计算番数
    :param codes: 14张编码
    :param win_type: winning_db 返回的牌型描述
    :param is_riichi: 是否立直
    :param is_tsumo: 是否自摸
    :param is_closed: 是否门清
    :return: (总番数, [役种列表], 赔率)
    """
    yaku = []
    nums = []
    for c in codes:
        if c.endswith("wan"):
            nums.append(int(c[0]))
        elif c.endswith("tiao"):
            nums.append(10 + int(c[0]))
        elif c.endswith("bing"):
            nums.append(20 + int(c[0]))

    counts = Counter(codes)

    # 国士无双
    if win_type == "国士无双":
        yaku.append(("国士无双", 75))
        return 75, yaku, 75

    # 七对子
    if win_type == "七对子":
        yaku.append(("七对子", 3))
        fan = 3
    else:
        fan = 0
        # 对对和判定：4刻子+1对
        # 简化：检查是否全是刻子/对
        is_all_triplets = all(v in (2, 3) for v in counts.values())
        if is_all_triplets and len([v for v in counts.values() if v == 3]) == 4:
            yaku.append(("对对和", 3))
            fan += 3

    # 清一色/混一色
    suits = set()
    has_honor = False
    for c in codes:
        if c.endswith("wan"):
            suits.add("wan")
        elif c.endswith("tiao"):
            suits.add("tiao")
        elif c.endswith("bing"):
            suits.add("bing")
        else:
            has_honor = True
    if len(suits) == 1 and not has_honor:
        yaku.append(("清一色", 8))
        fan += 8
    elif len(suits) == 1 and has_honor:
        yaku.append(("混一色", 5))
        fan += 5

    # 立直
    if is_riichi:
        yaku.append(("立直", 1))
        fan += 1

    # 门清自摸
    if is_tsumo and is_closed:
        yaku.append(("门清自摸", 1))
        fan += 1

    # 役牌：中/发/白刻
    for honor, name in [("zhong", "红中"), ("fa", "发财"), ("bai", "白板")]:
        if counts.get(honor, 0) >= 3:
            yaku.append((f"役牌:{name}", 1))
            fan += 1

    # 映射到赔率档
    if fan >= 13:
        odds = 75
    elif fan >= 11:
        odds = 30
    elif fan >= 8:
        odds = 15
    elif fan >= 6:
        odds = 8
    elif fan >= 5:
        odds = 5
    elif fan >= 4:
        odds = 3
    elif fan >= 2:
        odds = 2
    else:
        odds = 1

    return fan, yaku, odds


if __name__ == "__main__":
    # 测试：清一色万子
    hand = ["1wan"]*3 + ["2wan","3wan","4wan"] + ["5wan","6wan","7wan"] + ["9wan"]*3 + ["5wan"]*2
    fan, yaku, odds = calculate_fan(hand, "标准和牌", is_tsumo=True)
    print(f"番数={fan} 役={yaku} 赔率={odds}")

    # 测试：七对子
    hand2 = ["1wan"]*2 + ["2wan"]*2 + ["3bing"]*2 + ["4tiao"]*2 + ["dong"]*2 + ["nan"]*2 + ["fa"]*2
    fan2, yaku2, odds2 = calculate_fan(hand2, "七对子")
    print(f"番数={fan2} 役={yaku2} 赔率={odds2}")
