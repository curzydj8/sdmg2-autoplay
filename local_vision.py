#!/usr/bin/env python3
"""OpenCV游戏阶段识别：ODDS/EXCHANGE/MAIN/UNKNOWN"""
import sys
import cv2
import numpy as np

def detect_phase(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print("UNKNOWN 0.0")
        return
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ODDS: 大面积紫色 (H~140-160)
    purple = cv2.inRange(hsv, np.array([130, 50, 50]), np.array([165, 255, 255]))
    purple_ratio = np.sum(purple > 0) / (h * w)

    # EXCHANGE: 中部蓝色横幅 (H~100-120)
    mid = hsv[int(h*0.3):int(h*0.6), :]
    blue = cv2.inRange(mid, np.array([95, 80, 80]), np.array([125, 255, 255]))
    blue_ratio = np.sum(blue > 0) / (mid.shape[0] * mid.shape[1])

    # MAIN: 左下绿色区域 (H~35-75)
    roi = hsv[int(h*0.7):, :int(w*0.4)]
    green = cv2.inRange(roi, np.array([35, 50, 50]), np.array([75, 255, 255]))
    green_ratio = np.sum(green > 0) / (roi.shape[0] * roi.shape[1])

    if purple_ratio > 0.15:
        print(f"ODDS {min(0.9, purple_ratio*3):.2f}")
    elif blue_ratio > 0.10:
        print(f"EXCHANGE {min(0.85, blue_ratio*4):.2f}")
    elif green_ratio > 0.08:
        print(f"MAIN {min(0.8, green_ratio*5):.2f}")
    else:
        print("UNKNOWN 0.0")

if __name__ == "__main__":
    detect_phase(sys.argv[1] if len(sys.argv) > 1 else "/tmp/shot.png")
