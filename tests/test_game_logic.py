"""StandardGameFlow单元测试（独立，不依赖MAME）"""
import sys
sys.path.insert(0, 'modules')
from game_logic import StandardGameFlow

class FakeVision:
    def __init__(self, credit, bet):
        self.credit = credit
        self.bet = bet
    def capture_screen(self):
        return "fake_img"
    def read_credit_bet(self, img):
        return (self.credit, self.bet)

class FakeController:
    def __init__(self):
        self.pressed = []
    def press_key(self, key, delay=0.05):
        self.pressed.append(key)

def test_credit_check():
    """CREDIT 0-10需要上分"""
    flow = StandardGameFlow(None, None)
    assert flow.check_credit_needs_topup(0) == True
    assert flow.check_credit_needs_topup(5) == True
    assert flow.check_credit_needs_topup(10) == True
    assert flow.check_credit_needs_topup(11) == False
    assert flow.check_credit_needs_topup(500) == False
    assert flow.check_credit_needs_topup(None) == False
    print("✅ check_credit_needs_topup 通过")

def test_should_start():
    """BET==10才能START"""
    flow = StandardGameFlow(None, None)
    assert flow.should_start(10) == True
    assert flow.should_start(9) == False
    assert flow.should_start(None) == False
    print("✅ should_start 通过")

def test_full_flow_skip_topup():
    """CREDIT=500跳过上分，直接压分"""
    vision = FakeVision(credit=500, bet=10)
    ctrl = FakeController()
    flow = StandardGameFlow(vision, ctrl)
    result = flow.run()
    assert result['success'] == True
    assert 'COIN' not in ctrl.pressed  # 没上分
    assert 'START' in ctrl.pressed
    print("✅ 跳过上分流程 通过")

def test_full_flow_needs_topup():
    """CREDIT=2需要上分"""
    vision = FakeVision(credit=2, bet=10)
    ctrl = FakeController()
    flow = StandardGameFlow(vision, ctrl)
    # mock topup避免真按500次
    flow.topup_credits = lambda times=500: ctrl.pressed.append('COINx500')
    result = flow.run()
    assert 'COINx500' in ctrl.pressed
    print("✅ 上分流程 通过")

if __name__ == '__main__':
    test_credit_check()
    test_should_start()
    test_full_flow_skip_topup()
    test_full_flow_needs_topup()
    print("\n全部4项通过！")
