"""winning_db 单元测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../modules'))
from winning_db import check_win_cached

def test_standard():
    hand = ["1wan"]*3 + ["2wan","3wan","4wan"] + ["5bing","6bing","7bing"] + ["8tiao"]*3 + ["5wan"]*2
    win, desc = check_win_cached(hand)
    assert win and desc == "标准和牌"
    print("test_standard 通过")

def test_seven_pairs():
    hand = ["1wan"]*2 + ["2wan"]*2 + ["3bing"]*2 + ["4tiao"]*2 + ["dong"]*2 + ["nan"]*2 + ["fa"]*2
    win, desc = check_win_cached(hand)
    assert win and desc == "七对子"
    print("test_seven_pairs 通过")

def test_not_win():
    hand = ["1wan","2wan","3wan","4wan","5wan","6wan","7wan","8wan","9wan","1bing","2bing","3bing","dong","nan"]
    win, _ = check_win_cached(hand)
    assert not win
    print("test_not_win 通过")

if __name__ == "__main__":
    test_standard()
    test_seven_pairs()
    test_not_win()
    print("全部通过")
