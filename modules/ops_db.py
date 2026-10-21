#!/usr/bin/env python3
"""
操作知识库 v1.0
记录所有已验证的操作：按键、设置、流程、配置。
AI 查库就知道怎么操作，不用试错。

数据来源：2026-10-17 实机验证（MAME 0.285，新机 muse）
"""
import json
import os

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/ops_knowledge.json")


# ============ 按键映射（uinput 实测） ============
KEY_MAP = {
    "coin": {
        "key": "5",
        "evdev": "KEY_5",
        "desc": "投币",
        "verified": "2026-10-17 CREDIT 8→9",
        "method": "uinput",
    },
    "start": {
        "key": "1",
        "evdev": "KEY_1",
        "desc": "开始游戏",
        "verified": "2026-10-17 进入对局",
        "method": "uinput",
    },
    "tile_select": {
        "keys": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"],
        "evdev_prefix": "KEY_",
        "desc": "选第1-14张牌",
        "verified": "2026-10-17 按A选中第1张",
        "method": "uinput",
    },
    "confirm": {
        "key": "enter",
        "evdev": "KEY_ENTER",
        "desc": "确认",
        "verified": "2026-10-17 过信息屏",
        "method": "uinput",
    },
    "menu": {
        "key": "tab",
        "evdev": "KEY_TAB",
        "desc": "MAME菜单",
        "verified": "2026-10-17 打开Tab菜单",
        "method": "uinput",
    },
    "cancel": {
        "key": "esc",
        "evdev": "KEY_ESC",
        "desc": "取消/关菜单",
        "verified": "2026-10-17 关DIP菜单",
        "method": "uinput",
    },
}

# xdotool 不可用原因
INPUT_NOTES = {
    "xdotool": "X11合成按键，MAME收不到（走底层输入）",
    "uinput": "内核级虚拟键盘，MAME识别为真实硬件，必须用这个",
    "uinput_setup": [
        "sudo usermod -a -G input zhangdawei",
        "sudo chmod 666 /dev/uinput",
        "python3 -c 'from evdev import UInput'  # 验证",
    ],
}

# ============ DIP 设置（实测） ============
DIP_SETTINGS = {
    "coinage": {"value": "1 Coin/1 Credit", "desc": "投币比"},
    "key_in_rate": {"value": 10, "desc": "Key-In比率"},
    "credit_limit": {"value": 2000, "desc": "Credit上限"},
    "credit_mode": {"value": "Coin Acceptor", "desc": "Credit模式"},
    "payout_mode": {"value": "Return Coins", "desc": "派彩模式"},
    "demo_sounds": {"value": "On", "desc": "演示音效"},
    "double_up_jackpot": {"value": 500, "desc": "比倍奖池"},
    "minimum_bet": {"value": 1, "desc": "最小押注"},
    "double_up_game": {"value": "On", "desc": "比倍游戏"},
    "controls": {"value": "Mahjong", "desc": "控制器类型"},
    "number_type": {"value": "Numbers", "desc": "数字类型"},
    "how_to_change": "Tab → DIP Switches → 上下选择 → 左右改值 → Esc退出",
}

# ============ 游戏流程 ============
GAME_FLOW = {
    "steps": [
        {
            "phase": "info",
            "desc": "MAME信息屏（Press any key）",
            "action": "按 enter",
            "next": "odds",
        },
        {
            "phase": "odds",
            "desc": "ODDS赔率屏，PUSH START",
            "action": "按 5 投币（如需）→ 按 1 开始",
            "next": "exchange",
        },
        {
            "phase": "exchange",
            "desc": "換牌階段：請選擇您要交換的牌",
            "action": "按 a-n 选牌 → 按 enter 确认",
            "next": "play",
        },
        {
            "phase": "play",
            "desc": "打牌阶段",
            "action": "识别手牌 → Gemma/本地策略决策 → 按 a-n 出牌",
            "next": "play | meld_choice | result",
        },
        {
            "phase": "meld_choice",
            "desc": "吃碰杠选择",
            "action": "按对应键选择（待验证具体键）",
            "next": "play",
        },
        {
            "phase": "result",
            "desc": "结算屏",
            "action": "按 1 继续下一局",
            "next": "odds",
        },
    ],
}

# ============ AI 配置 ============
AI_CONFIG = {
    "vision": {
        "method": "模板匹配（cv2.matchTemplate）",
        "threshold": 0.75,
        "template_dir": "~/workspace/sdmg2-test/templates",
        "template_count": "18/34（待补16张）",
    },
    "reasoning": {
        "model": "gemma3:4b",
        "api": "http://localhost:11434/api/generate",
        "timeout": 120,
        "avg_time": "48秒",
        "fast_model": "gemma3:1b（8秒，简单决策用）",
    },
    "local_db": {
        "winning_db": "胡牌判定，毫秒级，不用问AI",
        "fan_db": "番数计算，毫秒级，不用问AI",
        "tile_codec": "牌编码 1wan/1tiao/1bing/dong/bai",
    },
    "screenshot": {
        "method": "xwd → xwdtopnm → ffmpeg转PNG",
        "env": "DISPLAY=:0 XAUTHORITY=/home/zhangdawei/.Xauthority",
        "note": "pnmtopng坏了，用ffmpeg",
    },
}

# ============ 屏幕坐标（1280x720基准） ============
SCREEN_COORDS = {
    "note": "相对坐标，适配不同分辨率",
    "hand_area": {"x": 0.10, "y": 0.82, "w": 0.80, "h": 0.15, "desc": "手牌区"},
    "opp_hand": {"x": 0.15, "y": 0.05, "w": 0.70, "h": 0.12, "desc": "对手手牌（牌背）"},
    "discards": {"x": 0.30, "y": 0.35, "w": 0.50, "h": 0.20, "desc": "弃牌区"},
    "credit_bet": {"x": 0.30, "y": 0.50, "w": 0.25, "h": 0.12, "desc": "CREDIT/BET显示"},
    "prompt": {"x": 0.15, "y": "0.60", "w": 0.70, "h": 0.10, "desc": "提示文字区"},
}


def get_operation(op_name):
    """查操作：如 get_operation('coin') 返回按键方法"""
    if op_name in KEY_MAP:
        return KEY_MAP[op_name]
    return None


def get_flow_step(phase):
    """查流程：如 get_flow_step('odds') 返回该阶段操作"""
    for s in GAME_FLOW["steps"]:
        if s["phase"] == phase:
            return s
    return None


def save_db():
    """保存到JSON"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    data = {
        "key_map": KEY_MAP,
        "input_notes": INPUT_NOTES,
        "dip_settings": DIP_SETTINGS,
        "game_flow": GAME_FLOW,
        "ai_config": AI_CONFIG,
        "screen_coords": SCREEN_COORDS,
    }
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"知识库已保存: {DB_PATH}")


def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    save_db()
    print("\n查操作示例:")
    print("投币:", get_operation("coin")["key"])
    print("ODDS阶段:", get_flow_step("odds")["action"])
