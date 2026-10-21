#!/usr/bin/env python3
"""
超级大满贯II 集成玩家 v2.0
状态机：BOOT → MENU → START_GAME → DEAL → DECIDE → ACT → VERIFY → NEXT_TURN → ROUND_END → SETTLEMENT → DOUBLEUP → NEXT_ROUND

CLI:
  --dry-run      只决策不按键
  --step         单步暂停
  --record       记录数据
  --autoplay     自动操作
  --max-games N  限制局数
  --target-score 500
"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATES = [
    "BOOT", "MENU", "START_GAME", "DEAL", "DECIDE",
    "ACT", "VERIFY", "NEXT_TURN", "ROUND_END",
    "SETTLEMENT", "DOUBLEUP", "NEXT_ROUND",
    "RECOVERY", "PAUSED",
]


class PlayerV2:
    def __init__(self, args):
        self.args = args
        self.state = "BOOT"
        self.game_count = 0
        self.target = args.target_score
        print(f"配置: dry_run={args.dry_run} autoplay={args.autoplay} "
              f"max_games={args.max_games} target={self.target}")
        print(f"押注: strategy={args.bet_strategy} default={args.default_bet}")
        print(f"换牌: count={args.exchange_count} adaptive={args.adaptive_exchange}")
        print(f"比倍风险: {args.doubleup_risk}")

        if not args.dry_run:
            from evdev import UInput, ecodes as E
            self.E = E
            keys = [E.KEY_1, E.KEY_5, E.KEY_ENTER, E.KEY_ESC]
            for ch in "abcdefghijklmn":
                keys.append(getattr(E, f"KEY_{ch.upper()}"))
            self.ui = UInput({E.EV_KEY: keys}, name="sdmg2-v2")
            print("uinput 就绪")
        else:
            print("DRY-RUN 模式：不按键")

    def press(self, key):
        if self.args.dry_run:
            print(f"[DRY] 按键: {key}")
            return True
        km = {"1": self.E.KEY_1, "5": self.E.KEY_5,
              "enter": self.E.KEY_ENTER, "esc": self.E.KEY_ESC}
        for ch in "abcdefghijklmn":
            km[ch] = getattr(self.E, f"KEY_{ch.upper()}")
        code = km.get(key)
        if not code:
            return False
        self.ui.write(self.E.EV_KEY, code, 1)
        self.ui.syn()
        time.sleep(0.12)
        self.ui.write(self.E.EV_KEY, code, 0)
        self.ui.syn()
        time.sleep(0.3)
        return True

    def transition(self, new_state):
        print(f"状态: {self.state} → {new_state}")
        self.state = new_state
        if self.args.step:
            input("按回车继续...")

    def run(self):
        print("=== Player v2.0 启动 ===")
        self.transition("BOOT")
        time.sleep(1)

        # 简化主循环：演示状态机
        self.transition("MENU")
        self.transition("START_GAME")
        self.press("1")

        while self.game_count < (self.args.max_games or 999):
            self.game_count += 1
            print(f"\n--- 第 {self.game_count} 局 ---")
            self.transition("DEAL")
            time.sleep(1)
            self.transition("DECIDE")
            # TODO: 接入识别+决策
            self.transition("ACT")
            self.transition("VERIFY")
            self.transition("NEXT_TURN")
            # 简化：直接到结算
            self.transition("ROUND_END")
            self.transition("SETTLEMENT")
            self.transition("DOUBLEUP")
            print(f"比倍决策：目标 {self.target}")
            self.transition("NEXT_ROUND")
            if self.game_count >= (self.args.max_games or 999):
                break

        print("=== 完成 ===")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--step", action="store_true")
    p.add_argument("--record", action="store_true")
    p.add_argument("--autoplay", action="store_true")
    p.add_argument("--max-games", type=int, default=0)
    p.add_argument("--target-score", type=int, default=500)
    p.add_argument("--bet-strategy", choices=["fixed", "adaptive"], default="fixed")
    p.add_argument("--default-bet", type=int, default=10)
    p.add_argument("--exchange-count", type=int, default=3)
    p.add_argument("--adaptive-exchange", action="store_true")
    p.add_argument("--doubleup-risk", choices=["conservative", "aggressive"], default="aggressive")
    args = p.parse_args()

    if args.autoplay:
        print("安全检查：")
        print("- uinput 可用性: 待验证")
        print("- 游戏状态来源: 视觉识别")
        print("- 自动操作已确认")
        c = input("确认启动自动操作? (y/n): ")
        if c.lower() != "y":
            print("已取消")
            sys.exit(0)

    PlayerV2(args).run()
