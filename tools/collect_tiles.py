'''后台收集手牌切片，每30秒一手'''
import cv2
import os
import time
from datetime import datetime

output_dir = os.path.expanduser('~/workspace/sdmg2-test/templates/collect_raw')
os.makedirs(output_dir, exist_ok=True)

# 用mss截图
try:
    import mss
    sct = mss.mss()
    HAS_MSS = True
except:
    HAS_MSS = False

def capture_hand():
    if not HAS_MSS:
        return None
    try:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        import numpy as np
        return np.array(img)[:, :, :3]  # BGRA->BGR
    except:
        return None

count = 0
while True:
    try:
        img = capture_hand()
        if img is not None:
            h, w = img.shape[:2]
            roi = img[int(h*0.87):int(h*0.97), int(w*0.1):int(w*0.9)]
            timestamp = datetime.now().strftime('%H%M%S')
            path = os.path.join(output_dir, f'hand_{timestamp}.png')
            cv2.imwrite(path, roi)
            count += 1
            print(f'[{count}] 已保存 {path}', flush=True)
        time.sleep(30)
    except Exception as e:
        print(f'错误: {e}', flush=True)
        time.sleep(5)
