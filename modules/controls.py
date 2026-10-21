#!/usr/bin/env python3
"""
模拟控制模块 controls.py

【开发铁律 - 绝对禁止修改底层】
1. 必须使用 Python `evdev` + `uinput`（内核级），禁止改回 pyautogui/pynput！
   原因：MAME在Linux下忽略X11/Wayland合成事件，只有uinput有效（已实测）。
2. 按键必须完整执行：按下(1) -> SYN -> 释放(0) -> SYN，缺一不可。
3. 键位映射（MAME实机截图验证）：
   - COIN=5, START=1, BET=3
   - A-N选牌(14张)，直接按键打牌
   - 碰=LAlt, 杠=LCtrl, 吃=Space, 立直=LShift, 荣=Z
   - 比倍=RShift, 大=Enter, 小=Backspace
"""
import time
from evdev import UInput, ecodes as E

# 实测验证的键位映射
KEY_MAP = {
    'COIN': E.KEY_5,
    'START': E.KEY_1,
    'BET': E.KEY_3,
    'ENTER': E.KEY_ENTER,
    'PON': E.KEY_LEFTALT,
    'KAN': E.KEY_LEFTCTRL,
    'CHI': E.KEY_SPACE,
    'RON': E.KEY_Z,
    'REACH': E.KEY_LEFTSHIFT,
    'DOUBLEUP': E.KEY_RIGHTSHIFT,
    'BIG': E.KEY_ENTER,
    'SMALL': E.KEY_BACKSPACE,
    'TAKE_SCORE': E.KEY_RIGHTCTRL,
    'LAST_CHANCE': E.KEY_RIGHTALT,
    'PAYOUT': E.KEY_4,
    'SHOW_CREDITS': E.KEY_9,
    'BOOK_KEEPING': E.KEY_0,
    'SERVICE_3': E.KEY_MINUS,
    'SERVICE_MODE': E.KEY_F2,
}
# A-N
for i, ch in enumerate("abcdefghijklmn"):
    KEY_MAP[ch.upper()] = getattr(E, f"KEY_{ch.upper()}")
# 数字键别名（Copilot诊断修复：auto_refill_credits用'5'但KEY_MAP只有'COIN'）
for d in "0123456789":
    KEY_MAP[d] = getattr(E, f"KEY_{d}")


class Controller:
    """uinput 控制器"""

    def __init__(self):
        keys = list(set(KEY_MAP.values()))
        self.ui = UInput({E.EV_KEY: keys}, name="sdmg2-autobot")
        self.E = E

    def _is_mame_active(self):
        """检查MAME窗口是否在前台"""
        import subprocess
        import os
        try:
            env = os.environ.copy()
            env['DISPLAY'] = env.get('DISPLAY', ':0')  # SSH时确保DISPLAY
            name = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                stderr=subprocess.STDOUT, timeout=2, env=env
            ).decode("utf-8", errors="ignore").strip().lower()
            # 严格匹配MAME窗口，排除VSCode（标题含sdmg2-test）
            # MAME标题: "Chaoji Da Manguan II (China, V765C) [sdmg2] - MAME 0.285"
            is_vscode = "visual studio" in name or "vscode" in name
            is_mame = ("mame 0.285" in name or "[sdmg2] - mame" in name)
            return is_mame and not is_vscode
        except:
            # xdotool失败时默认拦截（安全优先）
            return False

    def press_key(self, action_name, delay=0.1):
        # 安全铁律：MAME不在前台时禁止按键
        if not self._is_mame_active():
            print(f"[安全拦截] MAME不在前台，阻止按键 [{action_name}]")
            return False
        key = KEY_MAP.get(action_name)
        if not key:
            return False
        E = self.E
        self.ui.write(E.EV_KEY, key, 1)
        self.ui.syn()
        time.sleep(0.02)
        self.ui.write(E.EV_KEY, key, 0)
        self.ui.syn()
        time.sleep(delay)
        return True

    def press_key_closed_loop(self, action_name, verify_fn=None, timeout=3.0,
                               evidence_dir='/tmp/evidence'):
        """单步闭环按键（用户2026-10-18优先级2）
        
        Args:
            action_name: 按键名（如'BET'）
            verify_fn: 验证函数(before_img, after_img) -> (verified: bool, reason: str)
                       None表示不验证，只发送
            timeout: 等待验证超时（秒）
            evidence_dir: 证据保存目录
        
        Returns:
            (sent: bool, verified: bool, evidence: dict)
            - sent: 输入命令是否已发送（不代表游戏已响应）
            - verified: 是否观察到预期状态/分数变化
            - evidence: {'before': path, 'after': path, 'reason': str}
        
        失败时不自动重试，调用方必须停止并检查证据。
        """
        import time
        import os
        os.makedirs(evidence_dir, exist_ok=True)
        ts = int(time.time() * 1000)
        
        evidence = {'before': None, 'after': None, 'reason': ''}
        
        # 截图（前）
        before_img = None
        if hasattr(self, 'vision') and self.vision:
            try:
                before_img = self.vision.capture_screen()
                if before_img is not None:
                    import cv2
                    p = f'{evidence_dir}/before_{action_name}_{ts}.png'
                    cv2.imwrite(p, before_img)
                    evidence['before'] = p
            except:
                pass
        
        # 发送按键
        sent = self.press_key(action_name)
        if not sent:
            evidence['reason'] = '按键发送失败（MAME不在前台或键名无效）'
            return (False, False, evidence)
        
        # 无验证函数：只发送不验证
        if verify_fn is None:
            evidence['reason'] = '无验证函数，仅发送'
            return (True, False, evidence)
        
        # 等待并验证
        deadline = time.time() + timeout
        verified = False
        reason = '超时未观察到预期变化'
        after_img = None
        
        while time.time() < deadline:
            time.sleep(0.5)
            if hasattr(self, 'vision') and self.vision:
                try:
                    after_img = self.vision.capture_screen()
                except:
                    pass
            if before_img is not None and after_img is not None:
                try:
                    verified, reason = verify_fn(before_img, after_img)
                    if verified:
                        break
                except Exception as e:
                    reason = f'验证函数异常: {e}'
        
        # 保存证据（后）
        if after_img is not None:
            try:
                import cv2
                p = f'{evidence_dir}/after_{action_name}_{ts}.png'
                cv2.imwrite(p, after_img)
                evidence['after'] = p
            except:
                pass
        evidence['reason'] = reason
        
        return (sent, verified, evidence)

    def discard_card_by_index(self, card_index):
        """按槽位0-13打牌：单键直接打出，无需Enter"""
        keys = [chr(ord('A') + i) for i in range(14)]
        if 0 <= card_index < len(keys):
            self.press_key(keys[card_index], delay=0.05)
            return True
        return False

    def close(self):
        try:
            self.ui.close()
        except:
            pass

    def __del__(self):
        """析构：确保uinput句柄释放，防止kill后设备被占用"""
        self.close()

    def auto_refill_credits(self, times=5):
        """自动上分（Gemini方案：安全循环，0.1-0.2秒间隔防连击丢包）
        times: 按5键次数，每次约1分
        Returns: 成功发送的次数（Copilot诊断修复：检查返回值，失败即停）
        """
        import time
        success = 0
        for _ in range(times):
            if not self.press_key('5'):  # 投币键
                print(f"[上分] 按键失败，停止（已成功{success}次）")
                break
            success += 1
            time.sleep(0.15)
        return success
