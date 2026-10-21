#!/usr/bin/env python3
"""
游戏智能体 v2.0 - 四层架构

感知层 → 决策层 → 执行层 → 记录层
替代：local_ai_controller + game_controller + player_v2 + ai_loop
"""
import os
import sys
import time
import sqlite3
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = "/home/zhangdawei/workspace/sdmg2-test/data/sdmg2.db"

# 状态机
STATES = {
    'ODDS':       {'allow': ['credit', 'start', 'bet']},
    'EXCHANGE':   {'allow': ['select', 'confirm']},
    'PLAY':       {'allow': ['discard', 'chi', 'pon', 'kan', 'ron', 'reach']},
    'SETTLEMENT': {'allow': ['confirm']},
    'DOUBLEUP':   {'allow': ['big', 'small', 'stop']},
    'UNKNOWN':    {'allow': []},
}


class Perception:
    """感知层：截图→阶段→手牌→分数"""

    def screenshot(self):
        import cv2
        os.system("xwd -root -silent 2>/dev/null > /tmp/ai_cap.xwd")
        os.system("xwdtopnm /tmp/ai_cap.xwd 2>/dev/null > /tmp/ai_cap.ppm")
        os.system("ffmpeg -y -v error -i /tmp/ai_cap.ppm /tmp/ai_cap.png 2>/dev/null")
        return cv2.imread("/tmp/ai_cap.png")

    def detect_phase(self, img):
        """识别游戏阶段"""
        import cv2
        import numpy as np
        if img is None:
            return 'UNKNOWN', 0.0
        h, w = img.shape[:2]
        # ODDS检测：紫色背景高比例
        top = img[int(h*0.05):int(h*0.25), int(w*0.2):int(w*0.8)]
        hsv = cv2.cvtColor(top, cv2.COLOR_BGR2HSV)
        purple = np.mean((hsv[:, :, 0] > 120) & (hsv[:, :, 0] < 160))
        if purple > 0.6:
            return 'ODDS', 0.9
        # 手牌检测
        roi = img[int(h*0.87):int(h*0.97), int(w*0.1):int(w*0.9)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        bright = np.mean(gray > 100)
        if bright > 0.3:
            return 'PLAY', 0.7
        return 'UNKNOWN', 0.3

    def recognize_hand(self, img):
        """识别手牌，返回 [(code, conf)]"""
        try:
            from mahjong_vision import MahjongVision
            from tile_codec import encode_tile
            v = MahjongVision()
            r = v.recognize_hand(img, min_confidence=0.6)
            if not r:
                return []
            return [(encode_tile(x[0]), x[1]) for x in r]
        except:
            return []

    def detect_meld_prompt(self, img):
        """
        检测吃/碰/杠提示
        返回：'chi'|'pon'|'kan'|'ron'|None
        TODO：需实机截图确认提示UI特征
        """
        # 占位：暂未实现视觉检测
        # 实际游戏中，对手打牌后会有短暂提示窗口
        return None


class Decision:
    """决策层：规则+策略→动作"""

    def __init__(self):
        self.strategy = self._load_strategy()

    def _load_strategy(self):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            row = conn.execute(
                "SELECT version FROM strategy_configs WHERE is_active=1"
            ).fetchone()
            conn.close()
            return {"version": row[0] if row else "v1"}
        except:
            return {"version": "v1"}

    def decide(self, phase, hand, meld_prompt=None):
        """根据阶段、手牌、吃碰杠提示决定动作"""
        if phase == 'ODDS':
            return ('start', {})
        if phase == 'PLAY':
            # 优先处理吃碰杠提示
            if meld_prompt:
                decision = self.decide_meld(meld_prompt, hand)
                if decision:
                    return decision
            # 常规打牌
            if hand:
                try:
                    from high_fan_strategy import choose_discard
                    codes = [c for c, _ in hand if c != "unknown"]
                    if len(codes) >= 13:
                        idx, tile, score, _ = choose_discard(codes, "balanced")
                        return ('discard', {'slot_idx': idx})
                except:
                    pass
                return ('discard_last', {})
        return (None, {})

    def check_grand_slam_trigger(self, fan, bet):
        """
        检查大满贯触发条件
        用户流程图：押注达标 且 胡牌番数达到满贯4-5番以上
        """
        # ODDS屏显示：3分以上可玩大满贯，大满贯BET 4
        GRAND_SLAM_MIN_FAN = 4
        GRAND_SLAM_MIN_BET = 4
        return fan >= GRAND_SLAM_MIN_FAN and bet >= GRAND_SLAM_MIN_BET

    def decide_meld(self, prompt, hand):
        """
        吃碰杠决策
        prompt: 'chi'|'pon'|'kan'|'ron'
        返回动作或None（不吃碰）
        """
        if not hand:
            return None
        codes = [c for c, _ in hand if c != "unknown"]
        # 简单策略：
        # - ron（胡）：总是胡
        # - kan（杠）：有4张相同则杠
        # - pon（碰）：有2张相同则碰（除非七对子倾向）
        # - chi（吃）：暂不吃（需判断顺子价值）
        if prompt == 'ron':
            return ('ron', {})
        if prompt == 'kan':
            return ('kan', {})
        if prompt == 'pon':
            # 检查是否七对子（避免碰坏七对）
            from collections import Counter
            cnt = Counter(codes)
            pairs = sum(1 for v in cnt.values() if v >= 2)
            if pairs >= 4:  # 七对子倾向，不碰
                return None
            return ('pon', {})
        if prompt == 'chi':
            # 保守：暂不吃
            return None
        return None


class Execution:
    """执行层：按键+验证"""

    def __init__(self):
        from evdev import UInput, ecodes as E
        self.E = E
        keys = [E.KEY_1, E.KEY_3, E.KEY_5, E.KEY_ENTER, E.KEY_ESC,
                E.KEY_N, E.KEY_BACKSPACE]
        for ch in "abcdefghijklm":
            keys.append(getattr(E, f"KEY_{ch.upper()}"))
        # 比倍键
        keys += [E.KEY_RIGHTSHIFT, E.KEY_RIGHTCTRL, E.KEY_LEFTCTRL,
                 E.KEY_LEFTALT, E.KEY_SPACE, E.KEY_LEFTSHIFT, E.KEY_Z]
        self.ui = UInput({E.EV_KEY: keys}, name="sdmg2-agent")

    def press(self, key):
        """按键，返回耗时ms"""
        E = self.E
        km = {
            '1': E.KEY_1, '3': E.KEY_3, '5': E.KEY_5,
            'enter': E.KEY_ENTER, 'esc': E.KEY_ESC,
            'n': E.KEY_N, 'backspace': E.KEY_BACKSPACE,
            'rshift': E.KEY_RIGHTSHIFT, 'rctrl': E.KEY_RIGHTCTRL,
            # 吃碰杠胡
            'space': E.KEY_SPACE, 'lalt': E.KEY_LEFTALT,
            'lctrl': E.KEY_LEFTCTRL, 'lshift': E.KEY_LEFTSHIFT,
            'z': E.KEY_Z,
        }
        for ch in "abcdefghijklm":
            km[ch] = getattr(E, f"KEY_{ch.upper()}")
        code = km.get(key)
        if not code:
            return 0
        t0 = time.time()
        self.ui.write(E.EV_KEY, code, 1)
        self.ui.syn()
        time.sleep(0.05)
        self.ui.write(E.EV_KEY, code, 0)
        self.ui.syn()
        time.sleep(0.08)
        return (time.time() - t0) * 1000

    def do(self, action, params):
        """执行动作"""
        if action == 'start':
            self.press('1')
            return True
        if action == 'credit':
            for _ in range(10):
                self.press('5')
            return True
        if action == 'discard':
            slot = "abcdefghijklmn"[params['slot_idx']]
            self.press(slot)
            return True
        if action == 'discard_last':
            self.press('n')
            return True
        # 吃碰杠胡
        if action == 'chi':
            self.press('space')
            return True
        if action == 'pon':
            self.press('lalt')
            return True
        if action == 'kan':
            self.press('lctrl')
            return True
        if action == 'ron':
            self.press('z')
            return True
        if action == 'reach':
            self.press('lshift')
            return True
        return False

    def close(self):
        try:
            self.ui.close()
        except:
            pass


class Recording:
    """记录层"""

    def __init__(self, session_id):
        self.sid = session_id

    def action(self, action, ms, ok):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            conn.execute("""
                INSERT INTO actions (session_id, chosen, result, duration_ms, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (self.sid, action, "ok" if ok else "fail", int(ms)))
            conn.commit()
            conn.close()
        except:
            pass


class GameAgent:
    """游戏智能体主循环"""

    def __init__(self, session_id):
        self.sid = session_id
        self.perception = Perception()
        self.decision = Decision()
        self.execution = Execution()
        self.recording = Recording(session_id)
        # 大满贯模式状态
        self.grand_slam_mode = False
        self.grand_slam_rounds = 0
        self.lock = "/tmp/sdmg2_ai.lock"
        # 单实例检查
        if os.path.exists(self.lock):
            try:
                with open(self.lock) as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                raise RuntimeError(f"已在运行 PID={pid}")
            except (ValueError, ProcessLookupError, FileNotFoundError):
                try:
                    os.remove(self.lock)
                except:
                    pass
        open(self.lock, "w").write(str(os.getpid()))
        self.log(f"启动 session={session_id}")

    def log(self, msg):
        line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        try:
            with open("/tmp/sdmg2_ai.log", "a") as f:
                f.write(line + "\n")
        except:
            pass

    def run(self, max_rounds=500):
        self.log("开始主循环")
        try:
            for r in range(max_rounds):
                # 感知
                img = self.perception.screenshot()
                phase, conf = self.perception.detect_phase(img)
                # 决策
                hand = []
                meld_prompt = None
                if phase == 'PLAY':
                    hand = self.perception.recognize_hand(img)
                    meld_prompt = self.perception.detect_meld_prompt(img)
                action, params = self.decision.decide(phase, hand, meld_prompt)
                # 执行
                if action:
                    # 状态白名单检查
                    if action.split('_')[0] not in str(STATES.get(phase, {}).get('allow', [])):
                        # 简化检查：ODDS屏不打牌
                        if phase == 'ODDS' and 'discard' in action:
                            self.log(f"ODDS屏禁止打牌，跳过")
                            time.sleep(2)
                            continue
                    t0 = time.time()
                    # ODDS屏：大满贯模式免押注，否则上分+开始
                    if phase == 'ODDS' and action == 'start':
                        if self.grand_slam_mode:
                            self.log(f"大满贯模式：免押注直接开始")
                            # 不上分，直接按1
                        else:
                            self.execution.do('credit', {})
                            time.sleep(1)
                    ok = self.execution.do(action, params)
                    ms = (time.time() - t0) * 1000
                    mode = "大满贯" if self.grand_slam_mode else "常规"
                    self.log(f"轮{r} [{phase}][{mode}] {action} {ms:.0f}ms")
                    self.recording.action(action, ms, ok)
                else:
                    self.log(f"轮{r} [{phase}] 无动作")
                time.sleep(4)
        finally:
            self.cleanup()

    def cleanup(self):
        self.execution.close()
        try:
            os.remove(self.lock)
        except:
            pass
        self.log("已退出")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--session", type=int, required=True)
    p.add_argument("--max-rounds", type=int, default=500)
    a = p.parse_args()
    GameAgent(a.session).run(a.max_rounds)
