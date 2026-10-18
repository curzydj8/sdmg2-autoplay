"""直接绿色数字检测（方案3，独立验证）
不限定文字锚点，直接在MAME窗口内找绿色数字，
按形状和位置区分BET/CREDIT。
锚点方案保留作对照。
"""
import cv2
import numpy as np

class DigitDetector:
    """绿色数字直接检测器"""
    
    def __init__(self, template_dir='templates/digits'):
        self.template_dir = template_dir
        # 加载数字模板
        self.templates = {}
        import os
        for prefix in ['credit', 'bet']:
            for d in range(11):
                path = os.path.join(template_dir, f"{prefix}_{d}.png")
                if os.path.exists(path):
                    self.templates[f"{prefix}_{d}"] = cv2.imread(path, 0)
    
    def find_green_digits(self, img):
        """在图中找绿色数字候选区域
        Returns: [(x, y, w, h, cx, cy), ...] 按x排序
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 绿色范围
        mask = cv2.inRange(hsv, np.array([40, 50, 50]), np.array([80, 255, 255]))
        # 形态学去噪
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        num, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8)
        
        candidates = []
        h_img, w_img = img.shape[:2]
        for i in range(1, num):
            x, y, w, h, area = stats[i]
            # 过滤：面积、宽高比、位置（底部区域）
            if area < 100 or area > 5000:
                continue
            if h < 15 or w < 8:  # 太小不是数字
                continue
            aspect = w / h if h > 0 else 0
            if aspect < 0.2 or aspect > 1.5:  # 数字宽高比
                continue
            # 只在底部40%区域找（CREDIT/BET在底部）
            cy = centroids[i][1]
            if cy < h_img * 0.6:
                continue
            cx = centroids[i][0]
            candidates.append((x, y, w, h, int(cx), int(cy)))
        
        # 按x排序：左→CREDIT，中→大满贯，右→BET
        candidates.sort(key=lambda c: c[4])
        return candidates
    
    def classify_regions(self, candidates, img_width):
        """按x位置分类候选区域
        Returns: {'credit': [...], 'bet': [...]}
        """
        # 三分：左1/3=CREDIT，右1/3=BET，中间忽略（大满贯BET是黄色）
        result = {'credit': [], 'bet': []}
        for c in candidates:
            x, y, w, h, cx, cy = c
            if cx < img_width * 0.4:
                result['credit'].append(c)
            elif cx > img_width * 0.6:
                result['bet'].append(c)
        return result
    
    def recognize_digit(self, img, bbox, prefix):
        """识别单个数字区域
        Returns: (digit: int|None, score: float)
        """
        x, y, w, h, cx, cy = bbox
        # 扩大一点边界
        pad = 3
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img.shape[1], x + w + pad)
        y2 = min(img.shape[0], y + h + pad)
        roi = img[y1:y2, x1:x2]
        if roi.size == 0:
            return (None, 0.0)
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        best = (None, 0.0)
        for i in range(11):
            key = f"{prefix}_{i}"
            if key not in self.templates:
                continue
            tmpl = self.templates[key]
            # 缩放模板到ROI高度（只缩小）
            scale = min(gray.shape[0] / tmpl.shape[0], 
                       gray.shape[1] / tmpl.shape[1], 1.0)
            if scale <= 0:
                continue
            tw = max(1, int(tmpl.shape[1] * scale))
            th = max(1, int(tmpl.shape[0] * scale))
            tmpl_r = cv2.resize(tmpl, (tw, th))
            res = cv2.matchTemplate(gray, tmpl_r, cv2.TM_CCOEFF_NORMED)
            score = float(np.max(res))
            if score > best[1]:
                best = (i, score)
        
        if best[1] > 0.7:
            return best
        return (None, best[1])
    
    def read_credit_bet(self, img):
        """读取CREDIT和BET（方案3）
        Returns: (credit, bet, details)
        """
        candidates = self.find_green_digits(img)
        classified = self.classify_regions(candidates, img.shape[1])
        
        details = {'candidates': len(candidates), 'credit_regions': [], 'bet_regions': []}
        
        # CREDIT：取最左边的候选
        credit = None
        if classified['credit']:
            # 合并相邻数字（多位数）
            # 简化：取最大区域
            c = max(classified['credit'], key=lambda x: x[2]*x[3])
            d, s = self.recognize_digit(img, c, 'credit')
            credit = d
            details['credit_regions'].append((c, d, s))
        
        # BET：取最右边的候选
        bet = None
        if classified['bet']:
            c = max(classified['bet'], key=lambda x: x[2]*x[3])
            d, s = self.recognize_digit(img, c, 'bet')
            bet = d
            details['bet_regions'].append((c, d, s))
        
        return (credit, bet, details)
