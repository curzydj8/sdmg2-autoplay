#!/usr/bin/env python3
"""
画面数据库 v1.0
记录游戏各画面特征，AI 识别当前画面就知道该干什么。

画面类型：
- info: MAME信息屏
- odds: ODDS下注屏
- exchange: 换牌屏
- play: 打牌屏
- result: 结算屏
"""
import os
import json

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/screen_knowledge.json")

# 画面特征库（基于实机截图）
SCREENS = {
    "info": {
        "desc": "MAME信息屏",
        "features": [
            "深蓝背景白字",
            "显示 'Chaoji Da Manguan II (China, V765C)'",
            "显示 '1997 IGS'",
            "底部 'Press any key to continue'",
        ],
        "action": "按 enter 进入",
        "screenshot": "sdmg2-view.png",
    },
    "odds": {
        "desc": "ODDS下注屏",
        "features": [
            "顶部大彩字 'ODDS'",
            "紫色背景",
            "赔率表：75/30/15/8/5/3/2/1",
            "底部 'CREDIT' '大滿貫BET' 'BET'",
            "底部 'PUSH START OR BET BUTTON'",
        ],
        "action": "CREDIT不足按5投币 → 按1开始",
        "screenshot": "sdmg2-view3.png",
        "regions": {
            "credit": "底部左 CREDIT 数字",
            "bet": "底部右 BET 数字",
        },
    },
    "exchange": {
        "desc": "换牌屏",
        "features": [
            "中间红字 '請選擇您要交換的牌！！'",
            "底部手牌 A-N",
            "顶部对手牌背",
        ],
        "action": "按 a-n 选3张 → enter 确认",
        "screenshot": "sdmg2-view13.png",
    },
    "play": {
        "desc": "打牌屏",
        "features": [
            "底部手牌 A-N（14张）",
            "中间弃牌区",
            "CREDIT/BET 显示",
            "可能有 'DONDEN' 轮数",
        ],
        "action": "识别手牌 → 决策 → 按 a-n 出牌",
        "screenshot": "sdmg2-view14.png",
    },
    "result_win": {
        "desc": "和牌结算屏",
        "features": [
            "绿字 '立直' '門清自摸' 等役种",
            "显示 '合計 X 翻'",
            "显示 'X 點'",
            "手牌展开显示",
        ],
        "action": "记录番数 → 按1下一局",
        "screenshot": "sdmg2-view15.png",
    },
}

# 上分逻辑
CREDIT_RULES = {
    "min_bet": 1,           # 最小押注（DIP设置）
    "default_bet": 10,      # 默认押注（截图显示BET 10）
    "low_threshold": 10,    # CREDIT低于此值就上分
    "add_amount": 10,       # 每次上分按10次5键（10 credit）
    "max_credit": 2000,     # DIP上限
    "logic": [
        "每步检查 CREDIT",
        "CREDIT < 10 → 按5上分，直到 >=20",
        "CREDIT >= 2000 → 停止上分（到上限）",
    ],
}

# 押注策略
BET_STRATEGY = {
    "desc": "根据牌型强度决定押注",
    "levels": [
        {"hand_strength": "役满听牌/高番", "bet": 10, "desc": "满注"},
        {"hand_strength": "一般听牌", "bet": 5, "desc": "半注"},
        {"hand_strength": "烂牌", "bet": 1, "desc": "最小注"},
    ],
    "default": 10,
    "note": "v1先用默认10，待胡牌数据库联动后优化",
    "how_to_bet": "ODDS屏按 BET 键调整（待验证具体键）",
}


def identify_screen(features_desc):
    """
    根据特征描述识别画面（v1：人工/规则，v2：图像模板）
    :param features_desc: 特征关键词列表
    :return: screen_id 或 unknown
    """
    scores = {}
    for sid, info in SCREENS.items():
        score = sum(1 for f in features_desc if any(k in f for k in info["features"]))
        scores[sid] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


def should_add_credit(credit):
    """是否需要上分"""
    return credit < CREDIT_RULES["low_threshold"]


def get_bet_amount(hand_strength="normal"):
    """根据牌 strength 决定押注"""
    for lvl in BET_STRATEGY["levels"]:
        if lvl["hand_strength"] == hand_strength:
            return lvl["bet"]
    return BET_STRATEGY["default"]


def save_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    data = {
        "screens": SCREENS,
        "credit_rules": CREDIT_RULES,
        "bet_strategy": BET_STRATEGY,
    }
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"画面库已保存: {DB_PATH}")


if __name__ == "__main__":
    save_db()
    print("\n测试:")
    print("CREDIT=5 要上分?", should_add_credit(5))
    print("CREDIT=50 要上分?", should_add_credit(50))
    print("默认押注:", get_bet_amount())
