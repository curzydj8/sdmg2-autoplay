#!/usr/bin/env python3
"""
模板补全工具 v1.0
从游戏截图提取单张牌，人工标注后存入模板库。

用法：
  python3 extract_template.py <截图> <牌编码> <x> <y> <w> <h>

示例：
  python3 extract_template.py /tmp/game.png wan4 200 710 78 70

牌编码：wan1-9, tong1-9, tiao1-9, honor_east/south/west/north/red/green/white
"""
import cv2
import sys
import os

TEMPLATE_DIR = os.path.expanduser("~/workspace/sdmg2-test/templates")

# 编码 → 模板文件名
CODE_TO_FILE = {
    **{f"{i}wan": f"wan{i}" for i in range(1, 10)},
    **{f"{i}tiao": f"tiao{i}" for i in range(1, 10)},
    **{f"{i}bing": f"tong{i}" for i in range(1, 10)},
    "dong": "honor_east", "nan": "honor_south",
    "xi": "honor_west", "bei": "honor_north",
    "zhong": "honor_red", "fa": "honor_green", "bai": "honor_white",
}


def extract(screenshot, code, x, y, w, h):
    if code not in CODE_TO_FILE:
        print(f"未知编码: {code}")
        print(f"可用: {list(CODE_TO_FILE.keys())}")
        return False

    img = cv2.imread(screenshot)
    if img is None:
        print(f"无法读取: {screenshot}")
        return False

    tile = img[y:y+h, x:x+w]
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

    fname = CODE_TO_FILE[code] + ".png"
    out = os.path.join(TEMPLATE_DIR, fname)

    # 备份旧模板
    if os.path.exists(out):
        os.rename(out, out + ".bak")
        print(f"已备份旧模板")

    cv2.imwrite(out, gray)
    print(f"模板已保存: {out} ({w}x{h})")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)
    extract(sys.argv[1], sys.argv[2],
            int(sys.argv[3]), int(sys.argv[4]),
            int(sys.argv[5]), int(sys.argv[6]))
