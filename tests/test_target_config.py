"""目标配置测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../modules'))
from target_config import save_config, load_config, get_target
from doubleup_db import should_double_up

def test_target():
    # 500目标
    save_config(500)
    assert get_target() == 500
    d, _ = should_double_up(100, 400)
    assert d == True
    d, _ = should_double_up(100, 500)
    assert d == False
    print("✓ 500目标")

    # 2000目标
    save_config(2000)
    assert get_target() == 2000
    d, _ = should_double_up(100, 500)
    assert d == True  # 500<2000，继续
    d, _ = should_double_up(100, 2000)
    assert d == False
    print("✓ 2000目标")

    # 恢复500
    save_config(500)
    print("目标配置测试通过")

if __name__ == "__main__":
    test_target()
