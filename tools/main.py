#!/usr/bin/env python3
"""极速版 AutoPlayBot - 带状态锁定防空转"""
import sys, time, os, threading, signal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from database import init_db, get_config, log_match
from vision import VisionEngine
from safe_reader import SafeCreditBetReader
from controls import Controller
from ai_engine import MahjongAI

class AutoPlayBot:
    def __init__(self):
        print("[*] 初始化极速打牌机器人...")
        init_db()
        self.config = get_config()
        self.vision = VisionEngine()
        self.safe_reader = SafeCreditBetReader(self.vision)
        self.controller = Controller()
        self.ai = MahjongAI(risk_level=self.config.get('ai_risk_level', 0.5))
        self.state = "INIT"
        # 状态转移白名单（Gemini建议：防非法跳转）
        self.ALLOWED_TRANSITIONS = {
            "INIT": ["BET"],
            "BET": ["PLAY"],
            "PLAY": ["CHECK_RESULT"],
            "CHECK_RESULT": ["DOUBLE_UP", "BET"],
            "DOUBLE_UP": ["BET"],
        }
        self._init_runtime()

    def set_state(self, new_state):
        """状态转移守卫"""
        allowed = self.ALLOWED_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            print(f"[守卫] 非法跳转被拦截: {self.state} -> {new_state}")
            return False
        print(f"[状态] {self.state} -> {new_state}")
        self.state = new_state
        return True

    def _init_runtime(self):
        self.running = True
        self.play_rounds = 0
        self.stop_event = threading.Event()
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print(f"\n[!] 收到信号 {signum}，正在停止...")
        self.stop_event.set()
        self.running = False

    def _topup_credits(self, times):
        sent = self.controller.auto_refill_credits(times=times)
        if sent != times:
            print(f"[上分] 发送不完整：请求{times}次，已发送{sent}次，停止机器人")
            self.stop_event.set()
            self.running = False
            return False
        print(f"[上分] 已发送{sent}次投币输入（尚未验证游戏内CREDIT变化）")
        return True

    def _halt(self, reason):
        print(f"[安全停止] {reason}")
        self.stop_event.set()
        self.running = False
        return False

    def _prepare_round(self):
        img = self.vision.capture_screen()
        if img is None:
            return self._halt("无法截图，拒绝继续押注")

        credit, bet, _ = self.safe_reader.read_with_fallback(img)
        print(f"[BET] 当前credit={credit}, bet={bet}")
        if credit is None or credit < 10:
            if not self._topup_credits(times=15):
                return False
            time.sleep(1)

        if bet is None:
            return self._halt("BET无法识别，拒绝自动押注")

        target_bet = self.config.get('target_bet', 10)
        for _ in range(15):
            if bet == target_bet:
                break
            if bet > target_bet:
                return self._halt(f"BET={bet}超过目标{target_bet}，拒绝继续")

            previous_bet = bet
            if not self.controller.press_key('BET', delay=0.2):
                return self._halt("BET按键未发送")
            time.sleep(0.5)
            img = self.vision.capture_screen()
            if img is None:
                return self._halt("押注后无法截图，拒绝继续")
            credit, bet, _ = self.safe_reader.read_with_fallback(img)
            if credit is None or bet is None:
                return self._halt("押注后CREDIT或BET无法识别，拒绝继续")
            if bet <= previous_bet:
                return self._halt(
                    f"BET按键后未确认增加（BET {previous_bet}→{bet}），停止避免重复押注"
                )

        if bet != target_bet:
            return self._halt(f"押注未达到目标BET={target_bet}，当前BET={bet}")

        if not self.controller.press_key('START'):
            return self._halt("START按键未发送")

        for _ in range(20):
            img = self.vision.capture_screen()
            if img is not None and len(self.vision.detect_cards(img)) >= 13:
                return True
            time.sleep(0.1)
        return self._halt("START后未检测到手牌，拒绝进入PLAY")

    def run(self):
        print(f"[✔] 启动！押注: {self.config.get('target_bet', 10)}")
        try:
            while self.running and not self.stop_event.is_set():
                if self.state == "INIT":
                    self.set_state("BET")
                elif self.state == "BET":
                    print("[BET] 进入押注状态")
                    try:
                        ready = self._prepare_round()
                    except Exception as e:
                        print(f"[BET] 异常: {e}")
                        self._halt("开局流程异常，停止机器人")
                        break
                    if not ready:
                        break
                    self.play_rounds = 0
                    self.set_state("PLAY")
                elif self.state == "PLAY":
                    img = self.vision.capture_screen()
                    if img is None:
                        print("[*] 截屏失败，轮询中...")
                        time.sleep(0.05)
                        continue
                    hand_cards = self.vision.detect_cards(img)
                    # 关键修复：没检测到牌时留在PLAY继续等，不跳回BET
                    if not hand_cards or len(hand_cards) < 13:
                        print("[*] 等待发牌/未检测到手牌，轮询中...")
                        time.sleep(0.5)
                        continue
                    # 正常打牌，留在PLAY状态（多轮循环）
                    discard_idx = self.ai.select_best_discard(hand_cards)
                    self.controller.discard_card_by_index(discard_idx)
                    self.play_rounds += 1
                    print(f"[PLAY] 第{self.play_rounds}手，打出索引{discard_idx}")
                    time.sleep(0.3)
                    # 每10手检查一次是否对局结束（简化：暂不自动结束）
                    # 实际应通过视觉检测结算画面
                    if self.play_rounds >= 50:
                        print("[*] 达到最大手数，进入结算")
                        self.set_state("CHECK_RESULT")
                elif self.state == "CHECK_RESULT":
                    bet_score = self.config.get('target_bet', 10)
                    log_match(bet_score=bet_score, win_score=50, is_grand_slam=0, hand_cards="", result_type="RON")
                    print("[✔] 战绩已入库")
                    if self.config.get('enable_double_up', 1) and self.ai.should_double_up(50):
                        self.set_state("DOUBLE_UP")
                    else:
                        self.set_state("BET")
                elif self.state == "DOUBLE_UP":
                    self.controller.press_key('BIG')
                    time.sleep(0.2)
                    self.set_state("BET")
        except KeyboardInterrupt:
            print("\n[!] 退出...")
        finally:
            self.controller.close()

if __name__ == '__main__':
    bot = AutoPlayBot()
    bot.run()
