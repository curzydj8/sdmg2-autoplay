"""锚点模板匹配法（Gemini问题17）
用文字标签定位，再偏移找数字ROI，根治坐标漂移。
"""
import cv2
import numpy as np
import os

class AnchorFinder:
    """锚点定位器"""
    
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        self.labels = {}
        for name in ['label_bet', 'label_credit']:
            path = os.path.join(template_dir, f'{name}.png')
            if os.path.exists(path):
                self.labels[name] = cv2.imread(path)
    
    def find_label(self, img, label_name):
        """在图中找标签位置（全图多尺度，Copilot诊断修复）
        Returns: (x, y, w, h, score, scale) 或 None
        """
        if label_name not in self.labels:
            return None
        tmpl = self.labels[label_name]
        th, tw = tmpl.shape[:2]
        best = None
        # 多尺度搜索（0.5x ~ 1.5x）
        for scale in [0.6, 0.8, 1.0, 1.2, 1.4]:
            nw = int(tw * scale)
            nh = int(th * scale)
            if nw < 10 or nh < 10:
                continue
            tmpl_s = cv2.resize(tmpl, (nw, nh))
            # 全图搜索（不限底部）
            res = cv2.matchTemplate(img, tmpl_s, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if best is None or max_val > best[4]:
                x, y = max_loc
                best = (x, y, nw, nh, float(max_val), scale)
        if best is None or best[4] < 0.5:
            return None
        return best
    
    def get_digit_roi(self, img, label_name):
        """通过锚点获取数字ROI（按标签尺寸比例，Copilot诊断修复）
        Returns: ROI图像 或 None
        """
        found = self.find_label(img, label_name)
        if not found:
            return None
        x, y, w, h, score, scale = found
        # 数字在标签下方，偏移按标签高度比例
        # Copilot诊断修复：数字顶部y=647，标签底部y=650，重叠3px
        # gap设为负值，确保ROI包含数字顶部
        gap = int(-h * 0.1)  # 负间隙：向上扩展覆盖数字顶部
        digit_h = int(h * 1.4)  # 数字高度约为标签1.4倍（确保完整）
        digit_w = int(w * 0.6)
        digit_y1 = y + h + gap
        digit_y2 = digit_y1 + digit_h
        digit_x1 = x + w//2 - digit_w//2
        digit_x2 = x + w//2 + digit_w//2
        # 边界检查
        ih, iw = img.shape[:2]
        digit_x1 = max(0, digit_x1)
        digit_y1 = max(0, digit_y1)
        digit_x2 = min(iw, digit_x2)
        digit_y2 = min(ih, digit_y2)
        return img[digit_y1:digit_y2, digit_x1:digit_x2]
