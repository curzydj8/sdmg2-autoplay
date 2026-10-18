"""BET三态验证器测试"""
import sys
sys.path.insert(0, 'modules')
from bet_verifier import BETVerifier, VerifyResult
import numpy as np

class FakeVision:
    def __init__(self, bet_values):
        self.bet_values = bet_values
        self.idx = 0
    def capture_screen(self):
        return np.zeros((10, 10, 3), dtype=np.uint8)
    def read_credit_bet(self, img):
        v = self.bet_values[min(self.idx, len(self.bet_values)-1)]
        self.idx += 1
        return (None, v)

def test_can_verify_no_vision():
    """无vision时拒绝操作"""
    v = BETVerifier(vision=None)
    assert v.can_verify() == False
    print("✅ 无vision拒绝 通过")

def test_verified_increase():
    """VERIFIED: BET增加"""
    vision = FakeVision([5, 6])
    v = BETVerifier(vision)
    r, detail = v.verify_bet_change(None, None)  # 先测截图失败
    assert r == VerifyResult.UNKNOWN
    print("✅ 截图失败→UNKNOWN 通过")
    
    # 用fake的before/after
    img = np.zeros((10,10,3), dtype=np.uint8)
    vision2 = FakeVision([5, 6])
    v2 = BETVerifier(vision2)
    r, detail = v2.verify_bet_change(img, img, 'increase')
    assert r == VerifyResult.VERIFIED, f"期望VERIFIED, 得{r}"
    print(f"✅ BET增加→VERIFIED 通过 ({detail})")

def test_not_verified():
    """NOT_VERIFIED: 有效比较但无变化"""
    vision = FakeVision([5, 5])
    v = BETVerifier(vision)
    img = np.zeros((10,10,3), dtype=np.uint8)
    r, detail = v.verify_bet_change(img, img, 'increase')
    assert r == VerifyResult.NOT_VERIFIED, f"期望NOT_VERIFIED, 得{r}"
    print(f"✅ BET未变→NOT_VERIFIED 通过 ({detail})")

def test_unknown_unrecognizable():
    """UNKNOWN: 模板无法识别"""
    vision = FakeVision([None, None])
    v = BETVerifier(vision)
    img = np.zeros((10,10,3), dtype=np.uint8)
    r, detail = v.verify_bet_change(img, img, 'increase')
    assert r == VerifyResult.UNKNOWN, f"期望UNKNOWN, 得{r}"
    print(f"✅ 无法识别→UNKNOWN 通过 ({detail})")

if __name__ == '__main__':
    test_can_verify_no_vision()
    test_verified_increase()
    test_not_verified()
    test_unknown_unrecognizable()
    print("\n4项全过！")
