#!/usr/bin/env python3
"""
超级大满贯II AI 自主游戏 v2.0（新机 muse 专用）
边打边补边优化

流程：
  ODDS屏 → 按1开始 → 换牌阶段 → 打牌循环 → 结算 → 下一局

运行：python3 ai_auto_play.py
停止：pkill -f ai_auto_play.py
日志：/tmp/ai_play.log
"""
import os
import sys
import time
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/modules")

LOG = open("/tmp/ai_play.log", "a", buffering=1)

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")


class AutoPlayer:
    def __init__(self):
        from evdev import UInput, ecodes as E
        self.E = E
        keys = [E.KEY_1, E.KEY_5, E.KEY_ENTER, E.KEY_ESC, E.KEY_SPACE]
        for ch in "abcdefghijklmn":
            keys.append(getattr(E, f"KEY_{ch.upper()}"))
        self.ui = UInput({E.EV_KEY: keys}, name="sdmg2-ai")
        time.sleep(0.5)
        log("uinput 虚拟键盘已创建")

    def press(self, key_name, hold=0.12):
        key_map = {
            "1": self.E.KEY_1, "5": self.E.KEY_5,
            "enter": self.E.KEY_ENTER, "esc": self.E.KEY_ESC,
            "space": self.E.KEY_SPACE,
        }
        for ch in "abcdefghijklmn":
            key_map[ch] = getattr(self.E, f"KEY_{ch.upper()}")
        code = key_map.get(key_name)
        if code is None:
            log(f"未知按键: {key_name}")
            return
        self.ui.write(self.E.EV_KEY, code, 1)
        self.ui.syn()
        time.sleep(hold)
        self.ui.write(self.E.EV_KEY, code, 0)
        self.ui.syn()
        time.sleep(0.3)
        log(f"按键: {key_name}")

    def screenshot(self, path="/tmp/ai_screen.png"):
        os.system(
            "export DISPLAY=:0 XAUTHORITY=/home/zhangdawei/.Xauthority; "
            "xwd -root -silent 2>/dev/null > /tmp/ai.xwd && "
            "xwdtopnm /tmp/ai.xwd 2>/dev/null > /tmp/ai.ppm && "
            f"ffmpeg -y -v error -i /tmp/ai.ppm {path} 2>/dev/null"
        )
        return path if os.path.exists(path) else None

    def detect_phase(self, img_path):
        """阶段检测 v1：模板匹配关键UI元素"""
        img = cv2.imread(img_path)
        if img is None:
            return "unknown"
        # TODO: 用模板匹配 ODDS/换牌/打牌等特征
        # v1 先返回 unknown，靠人工观察日志
        return "unknown"

    def run(self):
        log("=== AI 自主游戏 v2.0 启动 ===")
        step = 0
        while True:
            try:
                step += 1
                shot = self.screenshot()
                if not shot:
                    log("截图失败")
                    time.sleep(2)
                    continue

                phase = self.detect_phase(shot)
                log(f"--- 步{step} phase={phase} ---")

                # v1: 保守策略，未知阶段不动作，只观察
                # 待模板库补全后启用自动决策
                log("v1观察模式：未动作，等待优化")
                time.sleep(10)

            except KeyboardInterrupt:
                log("用户停止")
                break
            except Exception as e:
                log(f"异常: {e}")
                time.sleep(5)

        self.ui.close()


if __name__ == "__main__":
    AutoPlayer().run()
