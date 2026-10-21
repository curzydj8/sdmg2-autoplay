#!/usr/bin/env python3
"""
胡牌判定数据库 v1.0
本地判定，不用问 AI。

支持：
- 标准和牌：4面子+1雀头
- 七对子
- 国士无双（十三幺）

输入：编码列表如 ['1wan','1wan','1wan','2wan','3wan','4wan',...]
输出：(是否和牌, 牌型描述)
"""
from collections import Counter


def _to_nums(codes):
    """编码转数字：wan=0-8, tiao=10-18, bing=20-28, 字=30-36"""
    nums = []
    for c in codes:
        if c.endswith("wan"):
            nums.append(int(c[0]) - 1)
        elif c.endswith("tiao"):
            nums.append(10 + int(c[0]) - 1)
        elif c.endswith("bing"):
            nums.append(20 + int(c[0]) - 1)
        elif c == "dong":
            nums.append(30)
        elif c == "nan":
            nums.append(31)
        elif c == "xi":
            nums.append(32)
        elif c == "bei":
            nums.append(33)
        elif c == "zhong":
            nums.append(34)
        elif c == "fa":
            nums.append(35)
        elif c == "bai":
            nums.append(36)
    return sorted(nums)


def _is_sequence_possible(nums):
    """检查是否能全部分解为顺子/刻子（递归）"""
    if not nums:
        return True
    # 尝试刻子
    if len(nums) >= 3 and nums[0] == nums[1] == nums[2]:
        if _is_sequence_possible(nums[3:]):
            return True
    # 尝试顺子（只对数牌）
    first = nums[0]
    if first < 30:  # 数牌
        # 找 first+1, first+2
        try:
            i1 = nums.index(first + 1)
            i2 = nums.index(first + 2)
            # 确保同花色（十位相同）
            if first // 10 == (first + 1) // 10 == (first + 2) // 10:
                rest = nums[1:i1] + nums[i1+1:i2] + nums[i2+1:]
                # 重建（去掉 first, first+1, first+2）
                tmp = nums.copy()
                tmp.remove(first)
                tmp.remove(first + 1)
                tmp.remove(first + 2)
                if _is_sequence_possible(sorted(tmp)):
                    return True
        except ValueError:
            pass
    return False


def is_winning_hand(codes):
    """
    判定是否和牌
    :return: (bool, 描述)
    """
    if len(codes) != 14:
        return False, f"牌数不对: {len(codes)}"

    nums = _to_nums(codes)
    if len(nums) != 14:
        return False, "有未知牌"

    # 七对子
    counts = Counter(nums)
    if len(counts) == 7 and all(v == 2 for v in counts.values()):
        return True, "七对子"

    # 国士无双：1,9万/筒/条 + 7种字牌 + 其中一种成对
    terminals_honors = {0, 8, 10, 18, 20, 28, 30, 31, 32, 33, 34, 35, 36}
    if set(nums) == terminals_honors and len(counts) == 13:
        # 13种各一张 + 其中一种两张 = 14张
        if sorted(counts.values()) == [1]*12 + [2]:
            return True, "国士无双"

    # 标准：4面子+1雀头
    for pair_tile in set(nums):
        if counts[pair_tile] >= 2:
            rest = nums.copy()
            rest.remove(pair_tile)
            rest.remove(pair_tile)
            if _is_sequence_possible(sorted(rest)):
                return True, "标准和牌"

    return False, "未和牌"


# 预计算常见牌型库（加速）
# key: 排序后的编码元组, value: (是否和牌, 描述)
_WIN_CACHE = {}

def check_win_cached(codes):
    key = tuple(sorted(codes))
    if key not in _WIN_CACHE:
        _WIN_CACHE[key] = is_winning_hand(codes)
    return _WIN_CACHE[key]


if __name__ == "__main__":
    # 测试
    # 标准和牌：111万 234万 567筒 888条 + 5万对
    hand1 = ["1wan"]*3 + ["2wan","3wan","4wan"] + ["5bing","6bing","7bing"] + ["8tiao"]*3 + ["5wan"]*2
    print("测试1:", check_win_cached(hand1))

    # 七对子
    hand2 = ["1wan"]*2 + ["2wan"]*2 + ["3bing"]*2 + ["4tiao"]*2 + ["dong"]*2 + ["nan"]*2 + ["fa"]*2
    print("测试2:", check_win_cached(hand2))

    # 未和牌
    hand3 = ["1wan","2wan","3wan","4wan","5wan","6wan","7wan","8wan","9wan","1bing","2bing","3bing","dong","nan"]
    print("测试3:", check_win_cached(hand3))


def find_ting_tiles(codes_13):
    """
    听牌枚举：13张手牌，找出所有能和牌的第14张
    :return: [(tile_code, win_desc), ...]
    """
    if len(codes_13) != 13:
        return []
    all_tiles = (
        [f"{i}wan" for i in range(1, 10)] +
        [f"{i}tiao" for i in range(1, 10)] +
        [f"{i}bing" for i in range(1, 10)] +
        ["dong", "nan", "xi", "bei", "zhong", "fa", "bai"]
    )
    result = []
    for t in all_tiles:
        # 检查4张限制（手牌已有3张就不能再听第4张）
        if codes_13.count(t) >= 4:
            continue
        test = codes_13 + [t]
        win, desc = check_win_cached(test)
        if win:
            result.append((t, desc))
    return result


def get_legal_discards(codes_14):
    """
    合法出牌：14张手牌，每张都可打出
    :return: [(slot_index, tile_code), ...]
    """
    if len(codes_14) != 14:
        return []
    return list(enumerate(codes_14))


def evaluate_discard(codes_14, discard_idx):
    """
    评估打出某张后的听牌数（向听数启发）
    :return: (打出后听牌张数, 听牌列表)
    """
    if len(codes_14) != 14 or not (0 <= discard_idx < 14):
        return 0, []
    remaining = codes_14[:discard_idx] + codes_14[discard_idx+1:]
    ting = find_ting_tiles(remaining)
    return len(ting), ting
