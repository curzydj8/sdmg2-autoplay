#!/usr/bin/env python3
"""
状态识别模块 v1.0
基于 states/recognition-rules.md v2.0
"""
from PIL import Image
import os

class StateDetector:
    """游戏状态识别器"""
    
    # 状态定义
    ODDS = "ODDS"           # 赔率表
    GAMEPLAY = "GAMEPLAY"   # 对局中
    UNKNOWN = "UNKNOWN"     # 未知
    
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or os.path.expanduser("~/workspace/sdmg2-test/screenshots")
    
    def detect(self, img):
        """
        识别游戏状态
        :param img: PIL Image (1003x731 MAME窗口截图)
        :return: (state_id, confidence, details)
        """
        # S1: 检查 ODDS
        odds_conf = self._check_odds(img)
        if odds_conf > 0.85:
            return (self.ODDS, odds_conf, "ODDS标题匹配")
        
        # S3: 检查对局 (A-N标记)
        game_conf = self._check_gameplay(img)
        if game_conf > 0.70:
            return (self.GAMEPLAY, game_conf, "检测到手牌标记")
        
        return (self.UNKNOWN, 0.0, "无匹配状态")
    
    def _check_odds(self, img):
        """检查是否为赔率表：蓝色背景 + 顶部ODDS区域特征"""
        # 简化版：检查顶部中央区域的粉色/青色像素（ODDS标题颜色）
        # ODDS标题约在 y=50-120, x=200-800
        w, h = img.size
        crop = img.crop((int(w*0.2), int(h*0.07), int(w*0.8), int(h*0.16)))
        pixels = list(crop.getdata())
        # 粉色 (255,100,200附近) 和青色 (100,255,255附近)
        pink_cyan = sum(1 for r,g,b in pixels 
                       if (r>200 and g<150 and b>150) or (r<150 and g>200 and b>200))
        ratio = pink_cyan / len(pixels)
        # 标题区域粉/青像素占比高则为ODDS
        return min(ratio * 5, 1.0)  # 归一化
    
    def _check_gameplay(self, img):
        """检查是否为对局：底部A-N字母标记
        采用简化的亮度+垂直投影检测：出现多个间隔稳定的亮点/字母槽位,
        表示在游戏桌面中显示A-N选择区。
        """
        try:
            if img is None:
                return 0.0
            if hasattr(img, 'convert'):
                gray = img.convert('L')
            else:
                import numpy as np
                gray = img
                if len(gray.shape) == 3:
                    gray = gray.mean(axis=2)
            if hasattr(gray, 'size'):
                w, h = gray.size
                crop = gray.crop((0, int(h * 0.72), w, h))
                arr = list(crop.getdata())
            else:
                import numpy as np
                arr = np.asarray(gray)
                if arr.ndim == 3:
                    arr = arr.mean(axis=2)
                h, w = arr.shape[:2]
                crop = arr[int(h * 0.72):, :]
                arr = crop.reshape(-1)

            if hasattr(arr, '__len__') and len(arr) == 0:
                return 0.0

            # 亮度阈值：A-N区域通常为高亮白色/灰色字母
            if hasattr(crop, 'getdata'):
                bright = sum(1 for p in arr if p > 180)
                ratio = bright / len(arr)
                data = list(crop.getdata())
            else:
                bright = float((crop > 180).sum())
                ratio = bright / crop.size
                data = crop.ravel()

            if ratio < 0.03:
                return 0.0

            # 计算垂直投影，检查是否存在多个间隔分布的亮列
            if hasattr(crop, 'getdata'):
                columns = [sum(1 for idx in range(crop.width) if crop.getpixel((idx, y)) > 180) for y in range(crop.height)]
                # 这里使用的是按列统计，起到 A-N 字母间隔多个亮列的效果
                proj = []
                for x in range(crop.width):
                    count = sum(1 for y in range(crop.height) if crop.getpixel((x, y)) > 180)
                    proj.append(count)
            else:
                proj = np.sum(crop > 180, axis=0).tolist()

            peaks = 0
            for i in range(1, len(proj) - 1):
                if proj[i] > 5 and proj[i] >= proj[i - 1] and proj[i] >= proj[i + 1]:
                    peaks += 1

            # 典型是多列稳定亮区（A-N字母通常在底部连续出现 8+ 个候选列）
            confidence = 0.6 if ratio > 0.03 else 0.0
            if peaks >= 8:
                confidence = 0.9
            elif peaks >= 5:
                confidence = 0.75
            return float(min(confidence, 1.0))
        except Exception:
            return 0.0

class MahjongVision:
    """麻将牌面识别（占位，未实现自动识别）"""
    
    def __init__(self):
        self.implemented = False
    
    def recognize_hand(self, img):
        """
        识别手牌
        :return: [(位置, 牌面, 置信度), ...]，未实现时返回空
        """
        # TODO: 实现牌面识别
        # 当前：返回空，调用者需人工确认
        return []
    
    def get_confidence(self):
        return 0.0

if __name__ == "__main__":
    print("StateDetector v1.0")
    print("ODDS检测: 基于颜色启发式")
    print("对局检测: 未实现 (需A-N OCR)")
    print("牌面识别: 未实现 (需人工)")
