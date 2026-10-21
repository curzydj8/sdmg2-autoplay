#!/usr/bin/env python3
"""
时序频率数据库 v1.0
画面检测时机、上分频率、摸牌打牌时序。

所有时间单位：秒
"""
import os
import json

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/timing_knowledge.json")

# ============ 画面检测频率 ============
DETECT_FREQ = {
    "screen_check": {
        "interval": 2,
        "desc": "每2秒截屏识别一次画面",
    },
    "credit_check": {
        "interval": 5,
        "desc": "每5秒检查CREDIT",
        "trigger": "ODDS屏或结算屏时",
    },
    "phase_check": {
        "interval": 1,
        "desc": "对局中每1秒检查阶段变化",
    },
}

# ============ 上分规则 ============
CREDIT_TIMING = {
    "when": [
        "ODDS屏且 CREDIT < 10",
        "结算屏且 CREDIT < 10",
        "BET > CREDIT（押注不够）",
    ],
    "how_much": {
        "per_press": 1,
        "presses": 20,
        "total": 20,
        "desc": "按20次5键，上20分",
    },
    "interval_between_press": 0.4,
    "desc": "上分到20+再开局",
    "max": 2000,
}

# ============ 摸牌时序 ============
DRAW_TIMING = {
    "detect": "游戏自动摸牌，无需AI操作",
    "active_draw": "玩家主动摸牌时 <1秒",
    "wait_after": 0.5,
    "desc": "游戏自动摸牌；主动摸牌<1秒，AI等0.5秒再识别",
}

# ============ 打牌时序 ============
PLAY_TIMING = {
    "steps": [
        {"op": "截图", "time": 0.5},
        {"op": "模板匹配认牌", "time": 0.3},
        {"op": "本地策略决策", "time": 0.1},
        {"op": "Gemma决策（复杂时）", "time": 48},
        {"op": "uinput按键", "time": 0.5},
        {"op": "等待画面更新", "time": 2},
    ],
    "total_fast": 3.4,
    "total_with_gemma": 51,
    "desc": "简单局面3.4秒，复杂局面51秒",
}

# ============ 换牌时序 ============
EXCHANGE_TIMING = {
    "detect": "画面'請選擇您要交換的牌'",
    "decision_time": 2,
    "action": "按a-n选牌，每张间隔0.4秒",
    "confirm": "按enter确认，等待2秒",
    "total": 5,
}

# ============ 比倍时序 ============
DOUBLEUP_TIMING = {
    "detect": "和牌结算后出现比倍提示",
    "decision": "查doubleup_db.should_double_up()",
    "action": "选YES/NO，选牌比大小",
    "per_round": 3,
    "desc": "每轮比倍约3秒，直到爆机或输",
}

# ============ 主循环频率 ============
MAIN_LOOP = {
    "interval": 2,
    "desc": "主循环每2秒一轮：截图→识别→决策→执行",
    "timeout_per_step": 60,
    "max_steps_per_game": 100,
}


def get_timing(action):
    """查时序：get_timing('play')"""
    mapping = {
        "detect": DETECT_FREQ,
        "credit": CREDIT_TIMING,
        "draw": DRAW_TIMING,
        "play": PLAY_TIMING,
        "exchange": EXCHANGE_TIMING,
        "doubleup": DOUBLEUP_TIMING,
        "main": MAIN_LOOP,
    }
    return mapping.get(action)


def save_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    data = {
        "detect_freq": DETECT_FREQ,
        "credit_timing": CREDIT_TIMING,
        "draw_timing": DRAW_TIMING,
        "play_timing": PLAY_TIMING,
        "exchange_timing": EXCHANGE_TIMING,
        "doubleup_timing": DOUBLEUP_TIMING,
        "main_loop": MAIN_LOOP,
    }
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"时序库已保存: {DB_PATH}")


if __name__ == "__main__":
    save_db()
    print("\n关键时序:")
    print(f"画面检测: 每{DETECT_FREQ['screen_check']['interval']}秒")
    print(f"上分: CREDIT<{CREDIT_TIMING['when'][0].split('<')[1].split()[0]}时，按{CREDIT_TIMING['how_much']['presses']}次")
    print(f"打牌: 简单{PLAY_TIMING['total_fast']}秒，复杂{PLAY_TIMING['total_with_gemma']}秒")
