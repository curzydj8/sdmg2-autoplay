#!/usr/bin/env python3
"""
超级大满贯II 集成玩家 v1.0
整合所有数据库：画面识别 → 状态编码 → 决策 → 执行

流程：
  截图 → 识别画面 → 查ops_db得操作 → 执行 → 循环
"""
import os
import sys
import time
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ops_db import get_operation, get_flow_step
from screen_db import should_add_credit, get_bet_amount
from doubleup_db import should_double_up
from winning_db import check_win_cached
from fan_db import calculate_fan
from tile_codec import encode_hand

LOG = open("/tmp/ai_play.log", "a", buffering=1)

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")


class Player:
    def __init__(self):
        from evdev import UInput, ecodes as E
        self.E = E
        keys = [E.KEY_1, E.KEY_5, E.KEY_ENTER, E.KEY_ESC, E.KEY_SPACE,
                E.KEY_TAB, E.KEY_UP, E.KEY_DOWN, E.KEY_LEFT, E.KEY_RIGHT]
        for ch in "abcdefghijklmn":
            keys.append(getattr(E, f"KEY_{ch.upper()}"))
        self.ui = UInput({E.EV_KEY: keys}, name="sdmg2-player")
        time.sleep(0.5)
        log("玩家初始化完成")

    def press(self, key, hold=0.12):
        km = {"1": self.E.KEY_1, "5": self.E.KEY_5,
              "enter": self.E.KEY_ENTER, "esc": self.E.KEY_ESC,
              "space": self.E.KEY_SPACE, "tab": self.E.KEY_TAB,
              "up": self.E.KEY_UP, "down": self.E.KEY_DOWN,
              "left": self.E.KEY_LEFT, "right": self.E.KEY_RIGHT}
        for ch in "abcdefghijklmn":
            km[ch] = getattr(self.E, f"KEY_{ch.upper()}")
        code = km.get(key)
        if not code:
            return
        self.ui.write(self.E.EV_KEY, code, 1)
        self.ui.syn()
        time.sleep(hold)
        self.ui.write(self.E.EV_KEY, code, 0)
        self.ui.syn()
        time.sleep(0.25)

    def screenshot(self, path="/tmp/ai_screen.png"):
        os.system(
            "export DISPLAY=:0 XAUTHORITY=/home/zhangdawei/.Xauthority; "
            "xwd -root -silent 2>/dev/null > /tmp/ai.xwd && "
            "xwdtopnm /tmp/ai.xwd 2>/dev/null > /tmp/ai.ppm && "
            f"ffmpeg -y -v error -i /tmp/ai.ppm {path} 2>/dev/null"
        )
        return path if os.path.exists(path) else None

    def ensure_credit(self, min_credit=20):
        """保证CREDIT充足（简化：按5上分）"""
        # TODO: 用OCR读CREDIT数字
        # v1: 直接按3次5（+3分）
        log("上分：按3次5")
        for _ in range(3):
            self.press("5")
            time.sleep(0.5)

    def play_step(self, phase):
        """单步决策"""
        step_info = get_flow_step(phase)
        if not step_info:
            log(f"未知阶段: {phase}")
            return

        log(f"阶段[{phase}]: {step_info['desc']}")
        log(f"操作: {step_info['action']}")

        if phase == "info":
            self.press("enter")
        elif phase == "odds":
            self.ensure_credit()
            self.press("1")
        elif phase == "exchange":
            # v1: 选前3张交换
            log("换牌：选a,b,c")
            for k in ["a", "b", "c"]:
                self.press(k)
            self.press("enter")
        elif phase == "play":
            # v1: 打第一张（待Gemma/策略接入）
            log("打牌：待决策模块")
            pass
        elif phase == "result":
            # 检查是否触发比倍
            do_double, reason = should_double_up(100, 0)
            log(f"比倍决策: {reason}")
            self.press("1")  # 下一局

    def run(self):
        log("=== 集成玩家启动 ===")
        # v1: 手动指定阶段，待画面识别完善后自动
        log("v1: 请手动确认当前画面，输入阶段 (info/odds/exchange/play/result/quit)")
        while True:
            try:
                phase = input("阶段> ").strip()
                if phase == "quit":
                    break
                self.play_step(phase)
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                log(f"异常: {e}")
        self.ui.close()
        log("=== 玩家停止 ===")


if __name__ == "__main__":
    Player().run()
