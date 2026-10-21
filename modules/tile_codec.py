#!/usr/bin/env python3
"""
麻将牌编码模块 v1.0
严谨的描述性编码，供 Gemma 推理使用。

编码规范：
- 万子：1wan ~ 9wan
- 条子：1tiao ~ 9tiao
- 饼子：1bing ~ 9bing
- 风牌：dong, nan, xi, bei
- 三元：zhong（红中）, fa（发财）, bai（白板）
- 未知：unknown

扩展字段（可选）：
- 位置：slot (a-n)
- 置信度：confidence (0.0-1.0)
- 是否刚摸：is_drawn (bool)
"""

# 中文牌名 -> 标准编码
TILE_NAME_TO_CODE = {
    # 万
    "一万": "1wan", "二万": "2wan", "三万": "3wan",
    "四万": "4wan", "五万": "5wan", "六万": "6wan",
    "七万": "7wan", "八万": "8wan", "九万": "9wan",
    # 条
    "一条": "1tiao", "二条": "2tiao", "三条": "3tiao",
    "四条": "4tiao", "五条": "5tiao", "六条": "6tiao",
    "七条": "7tiao", "八条": "8tiao", "九条": "9tiao",
    # 饼（筒）
    "一饼": "1bing", "二饼": "2bing", "三饼": "3bing",
    "四饼": "4bing", "五饼": "5bing", "六饼": "6bing",
    "七饼": "7bing", "八饼": "8bing", "九饼": "9bing",
    "一筒": "1bing", "二筒": "2bing", "三筒": "3bing",
    "四筒": "4bing", "五筒": "5bing", "六筒": "6bing",
    "七筒": "7bing", "八筒": "8bing", "九筒": "9bing",
    # 风
    "东": "dong", "东风": "dong",
    "南": "nan", "南风": "nan",
    "西": "xi", "西风": "xi",
    "北": "bei", "北风": "bei",
    # 三元
    "中": "zhong", "红中": "zhong",
    "发": "fa", "发财": "fa",
    "白": "bai", "白板": "bai",
}

# 模板文件名 -> 标准编码（模板命名可能不规范）
TEMPLATE_TO_CODE = {
    "wan1": "1wan", "wan2": "2wan", "wan3": "3wan",
    "wan4": "4wan", "wan5": "5wan", "wan6": "6wan",
    "wan7": "7wan", "wan8": "8wan", "wan9": "9wan",
    "tiao1": "1tiao", "tiao2": "2tiao", "tiao3": "3tiao",
    "tiao4": "4tiao", "tiao5": "5tiao", "tiao6": "6tiao",
    "tiao7": "7tiao", "tiao8": "8tiao", "tiao9": "9tiao",
    "tong1": "1bing", "tong2": "2bing", "tong3": "3bing",
    "tong4": "4bing", "tong5": "5bing", "tong6": "6bing",
    "tong7": "7bing", "tong8": "8bing", "tong9": "9bing",
    "bing1": "1bing", "bing2": "2bing", "bing3": "3bing",
    "bing4": "4bing", "bing5": "5bing", "bing6": "6bing",
    "bing7": "7bing", "bing8": "8bing", "bing9": "9bing",
    "honor_east": "dong", "honor_south": "nan",
    "honor_west": "xi", "honor_north": "bei",
    "honor_red": "zhong", "honor_green": "fa", "honor_white": "bai",
}

# 反向：编码 -> 中文（用于日志显示）
CODE_TO_CN = {
    "1wan": "一万", "2wan": "二万", "3wan": "三万",
    "4wan": "四万", "5wan": "五万", "6wan": "六万",
    "7wan": "七万", "8wan": "八万", "9wan": "九万",
    "1tiao": "一条", "2tiao": "二条", "3tiao": "三条",
    "4tiao": "四条", "5tiao": "五条", "6tiao": "六条",
    "7tiao": "七条", "8tiao": "八条", "9tiao": "九条",
    "1bing": "一饼", "2bing": "二饼", "3bing": "三饼",
    "4bing": "四饼", "5bing": "五饼", "6bing": "六饼",
    "7bing": "七饼", "8bing": "八饼", "9bing": "九饼",
    "dong": "东", "nan": "南", "xi": "西", "bei": "北",
    "zhong": "红中", "fa": "发财", "bai": "白板",
}


def encode_tile(tile_name):
    """牌名 -> 标准编码，无法识别返回 'unknown'"""
    if tile_name in TILE_NAME_TO_CODE:
        return TILE_NAME_TO_CODE[tile_name]
    if tile_name in TEMPLATE_TO_CODE:
        return TEMPLATE_TO_CODE[tile_name]
    # 尝试直接匹配（已经是编码格式）
    if tile_name in CODE_TO_CN:
        return tile_name
    return "unknown"


def encode_hand(vision_result):
    """
    视觉识别结果 -> Gemma 输入格式
    :param vision_result: [(slot, tile_name, confidence), ...]
    :return: {"tiles": [...], "gemma_prompt": str}
    """
    tiles = []
    for slot, name, conf in vision_result:
        code = encode_tile(name)
        tiles.append({
            "slot": slot,
            "code": code,
            "cn": CODE_TO_CN.get(code, name),
            "confidence": round(conf, 2),
        })

    # 只用高置信度牌组装 prompt
    known = [t["code"] for t in tiles if t["confidence"] >= 0.8 and t["code"] != "unknown"]
    prompt = (
        "你正在玩超级大满贯II（2人麻将博弈机）。"
        f"当前手牌（共{len(known)}张）：{','.join(known)}。"
        "请决定打出一张牌，只回复该牌的编码（如 3wan），不要解释。"
    )
    return {"tiles": tiles, "gemma_prompt": prompt}


def decode_discard(gemma_response, tiles):
    """
    Gemma 回复 -> 槽位
    :param gemma_response: Gemma 返回的编码字符串
    :param tiles: encode_hand 返回的 tiles 列表
    :return: slot 或 None
    """
    code = gemma_response.strip().lower()
    # 容错：去掉多余字符
    for t in tiles:
        if t["code"] == code:
            return t["slot"]
    return None


if __name__ == "__main__":
    # 自测
    demo = [("a", "三万", 0.95), ("b", "tong5", 0.92),
            ("c", "honor_east", 0.88), ("d", "UNKNOWN", 0.3)]
    r = encode_hand(demo)
    print("Prompt:", r["gemma_prompt"])
    print("Decode:", decode_discard("3wan", r["tiles"]))
