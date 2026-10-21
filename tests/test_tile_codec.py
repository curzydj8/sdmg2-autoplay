"""tile_codec 单元测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../modules'))
from tile_codec import encode_tile, encode_hand, decode_discard

def test_encode():
    assert encode_tile("三万") == "3wan"
    assert encode_tile("tong5") == "5bing"
    assert encode_tile("honor_east") == "dong"
    assert encode_tile("UNKNOWN") == "unknown"
    print("test_encode 通过")

def test_roundtrip():
    demo = [("a", "三万", 0.95), ("b", "tong5", 0.92)]
    r = encode_hand(demo)
    assert "3wan" in r["gemma_prompt"]
    assert decode_discard("3wan", r["tiles"]) == "a"
    print("test_roundtrip 通过")

if __name__ == "__main__":
    test_encode()
    test_roundtrip()
    print("全部通过")
