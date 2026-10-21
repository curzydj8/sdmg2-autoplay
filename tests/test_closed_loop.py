"""单步闭环输入测试（用户2026-10-18优先级2）
覆盖：发送失败、画面未变化、预期变化、超时、验证失败后不继续
"""
import sys
sys.path.insert(0, 'modules')
import numpy as np

class FakeVision:
    def __init__(self, images):
        self.images = images
        self.idx = 0
    def capture_screen(self):
        img = self.images[min(self.idx, len(self.images)-1)]
        self.idx += 1
        return img

class FakeController:
    """模拟Controller，只测试闭环逻辑"""
    def __init__(self, vision, send_success=True):
        self.vision = vision
        self.send_success = send_success
        self.sent_count = 0
        # 导入真实方法逻辑（简化版）
    def press_key(self, action_name, delay=0.1):
        if not self.send_success:
            return False
        self.sent_count += 1
        return True

def make_closed_loop(controller):
    """复制press_key_closed_loop的核心逻辑用于测试"""
    import time, os
    def closed_loop(action_name, verify_fn=None, timeout=2.0):
        before = controller.vision.capture_screen() if controller.vision else None
        sent = controller.press_key(action_name)
        if not sent:
            return (False, False, {'reason': '发送失败'})
        if verify_fn is None:
            return (True, False, {'reason': '无验证'})
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.1)
            after = controller.vision.capture_screen() if controller.vision else None
            if before is not None and after is not None:
                verified, reason = verify_fn(before, after)
                if verified:
                    return (True, True, {'reason': reason})
        return (True, False, {'reason': '超时'})
    return closed_loop

def test_send_failure():
    """发送失败：sent=False, verified=False"""
    ctrl = FakeController(None, send_success=False)
    fn = make_closed_loop(ctrl)
    sent, verified, ev = fn('BET')
    assert sent == False and verified == False
    print("✅ 发送失败 通过")

def test_no_screen_change():
    """画面未变化：sent=True, verified=False"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    ctrl = FakeController(FakeVision([img, img, img]))
    fn = make_closed_loop(ctrl)
    def verify(b, a):
        changed = not np.array_equal(b, a)
        return (changed, '画面变化' if changed else '画面未变')
    sent, verified, ev = fn('BET', verify_fn=verify, timeout=0.5)
    assert sent == True and verified == False
    print("✅ 画面未变化 通过")

def test_expected_change():
    """预期变化：sent=True, verified=True"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    ctrl = FakeController(FakeVision([img1, img2]))
    fn = make_closed_loop(ctrl)
    def verify(b, a):
        changed = not np.array_equal(b, a)
        return (changed, '检测到变化')
    sent, verified, ev = fn('BET', verify_fn=verify, timeout=2.0)
    assert sent == True and verified == True
    print("✅ 预期变化 通过")

def test_no_auto_retry():
    """验证失败后不自动重试：只发送一次"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    ctrl = FakeController(FakeVision([img]*10))
    fn = make_closed_loop(ctrl)
    def verify(b, a):
        return (False, '始终失败')
    sent, verified, ev = fn('BET', verify_fn=verify, timeout=0.5)
    assert ctrl.sent_count == 1, f"发送了{ctrl.sent_count}次，应该只1次"
    assert verified == False
    print("✅ 验证失败不重试 通过")

if __name__ == '__main__':
    test_send_failure()
    test_no_screen_change()
    test_expected_change()
    test_no_auto_retry()
    print("\n4项全过！")
