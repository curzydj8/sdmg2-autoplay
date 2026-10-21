#!/usr/bin/env python3
import os, time, cv2
os.system("mkdir -p /home/zhangdawei/sdmg2-test/data/collect")
for i in range(20):
    os.system("xwd -root -silent 2>/dev/null > /tmp/cc.xwd")
    os.system("xwdtopnm /tmp/cc.xwd 2>/dev/null > /tmp/cc.ppm")
    os.system("ffmpeg -y -v error -i /tmp/cc.ppm /tmp/cc.png 2>/dev/null")
    img = cv2.imread("/tmp/cc.png")
    if img is not None:
        h, w = img.shape[:2]
        hand = img[int(h*0.87):int(h*0.97), int(w*0.1):int(w*0.9)]
        fn = "/home/zhangdawei/sdmg2-test/data/collect/hand_%d.png" % int(time.time())
        cv2.imwrite(fn, hand)
        print("saved %d/20" % (i+1))
    time.sleep(30)
print("done")
