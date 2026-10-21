#!/usr/bin/env python3
"""
游戏全状态编码 v1.0
把屏幕每个细节转成编码，只发编码给 Gemma。

编码总览：
  phase: 游戏阶段
  credit/bet/round: 分数信息
  hand: 手牌（14张，A-N）
  discards: 双方弃牌
  melds: 双方副露
  prompt: 屏幕提示
  selected: 选中状态
"""
from tile_codec import encode_tile, CODE_TO_CN

# 游戏阶段编码
PHASES = {
    "odds": "ODDS下注屏",
    "exchange": "换牌阶段",
    "play": "打牌阶段",
    "draw": "摸牌后待打",
    "meld_choice": "吃碰杠选择",
    "result_win": "和牌结算",
    "result_lose": "输结算",
    "unknown": "未知阶段",
}

# 屏幕提示编码
PROMPTS = {
    "select_exchange": "請選擇您要交換的牌",
    "push_start": "PUSH START",
    "push_bet": "PUSH BET",
    "your_discard": "請打出不要的牌",
    "chi_peng": "吃/碰选择",
    "da_pai": "搭牌提示",
    "none": "无提示",
}


class GameState:
    def __init__(self):
        self.phase = "unknown"
        self.credit = 0
        self.bet = 0
        self.round = 0          # DONDEN
        self.hand = []          # [(slot, code, selected, confidence)]
        self.discards_self = []
        self.discards_opp = []
        self.melds_self = []
        self.melds_opp = []
        self.prompt = "none"
        self.wall_count = -1    # -1=未知

    def to_gemma_prompt(self):
        """转成 Gemma 输入"""
        lines = ["[GAME_STATE]"]
        lines.append(f"phase={self.phase}")
        lines.append(f"credit={self.credit} bet={self.bet} round={self.round}")

        # 手牌：只列编码，选中加*
        hand_str = ",".join(
            f"{code}*" if sel else code
            for _, code, sel, _ in self.hand
        )
        lines.append(f"hand=[{hand_str}]")

        if self.discards_self:
            lines.append(f"discards_self=[{','.join(self.discards_self)}]")
        if self.discards_opp:
            lines.append(f"discards_opp=[{','.join(self.discards_opp)}]")
        if self.melds_self:
            lines.append(f"melds_self=[{','.join(self.melds_self)}]")
        if self.melds_opp:
            lines.append(f"melds_opp=[{','.join(self.melds_opp)}]")

        lines.append(f"prompt={self.prompt}")

        # 根据阶段给指令
        if self.phase == "exchange":
            lines.append("TASK:选择要交换的牌，回复如 'a,c,f'（槽位字母，逗号分隔）")
        elif self.phase in ("play", "draw"):
            lines.append("TASK:决定打出一张牌，只回复编码如 '3wan'")
        elif self.phase == "meld_choice":
            lines.append("TASK:决定是否吃/碰/杠，回复 'chi'/'peng'/'gang'/'pass'")

        return "\n".join(lines)

    def to_human(self):
        """转人工可读（调试用）"""
        cn_hand = [CODE_TO_CN.get(c, c) + ("*" if s else "") for _, c, s, _ in self.hand]
        return (f"[{self.phase}] credit={self.credit} bet={self.bet} "
                f"手牌={','.join(cn_hand)} 提示={self.prompt}")


# 按键映射表（已验证）
KEY_MAP = {
    "coin": "5",       # 投币 ✅
    "start": "1",      # 开始 ✅
    "tile_a": "a",     # 选第1张 ✅
    "tile_b": "b",
    "tile_c": "c",
    "tile_d": "d",
    "tile_e": "e",
    "tile_f": "f",
    "tile_g": "g",
    "tile_h": "h",
    "tile_i": "i",
    "tile_j": "j",
    "tile_k": "k",
    "tile_l": "l",
    "tile_m": "m",
    "tile_n": "n",
    "confirm": "enter",  # 确认（待验证）
    "cancel": "escape",  # 取消（待验证）
}


if __name__ == "__main__":
    # 演示
    gs = GameState()
    gs.phase = "play"
    gs.credit = 9
    gs.bet = 10
    gs.round = 5
    gs.hand = [("a", "8wan", False, 0.95), ("b", "2bing", False, 0.92),
               ("c", "3bing", False, 0.90), ("h", "nan", False, 0.88),
               ("m", "fa", True, 0.93)]
    gs.discards_opp = ["dong", "1tiao"]
    gs.prompt = "your_discard"
    print(gs.to_gemma_prompt())
    print()
    print(gs.to_human())
