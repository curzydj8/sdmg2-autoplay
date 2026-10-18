#!/usr/bin/env python3
"""
视觉识别模块 vision.py
- 基于 OpenCV + mss（极速截图，失败回退xwd）
- 识别手牌、宝牌、按钮位置、屏幕积分
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False


class VisionEngine:
    def __init__(self, region=None):
        self.region = region or {"top": 0, "left": 0, "width": 1280, "height": 800}
        if HAS_MSS:
            self.sct = mss.mss()

    def capture_screen(self):
        """截取画面，返回BGR numpy数组"""
        import cv2
        import numpy as np
        if HAS_MSS:
            try:
                img = self.sct.grab(self.region)
                frame = np.array(img)
                return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            except:
                pass
        # 回退：xwd
        os.system("xwd -root -silent 2>/dev/null > /tmp/ai_cap.xwd")
        os.system("xwdtopnm /tmp/ai_cap.xwd 2>/dev/null > /tmp/ai_cap.ppm")
        os.system("ffmpeg -y -v error -i /tmp/ai_cap.ppm /tmp/ai_cap.png 2>/dev/null")
        return cv2.imread("/tmp/ai_cap.png")

    def read_numeric_score(self, img, roi_box):
        """OCR识别数字区域"""
        try:
            import cv2
            import pytesseract
            x, y, w, h = roi_box
            roi = img[y:y+h, x:x+w]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            text = pytesseract.image_to_string(
                thresh, config='--psm 6 -c tessedit_char_whitelist=0123456789')
            return int(text.strip())
        except:
            return 0

    def detect_cards(self, img):
        """模板匹配识别手牌，返回编码列表"""
        try:
            from mahjong_vision import MahjongVision
            from tile_codec import encode_tile
            v = MahjongVision()
            r = v.recognize_hand(img, min_confidence=0.75)
            if not r:
                return []
            return [encode_tile(x[0]) for x in r if x[0] != "unknown"]
        except:
            return []

    def close(self):
        """关闭mss单例，防止X11连接泄漏（Gemini极高危警告）"""
        if hasattr(self, 'sct') and self.sct:
            try:
                self.sct.close()
            except:
                pass

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def detect_settlement(self, img):
        """检测结算画面（Gemini ROI Trigger方案）
        返回: True=结算画面，False=游戏中
        """
        try:
            import cv2
            import numpy as np
            h, w = img.shape[:2]
            # 中心ROI：x 0.3-0.7, y 0.3-0.6
            roi = img[int(h*0.3):int(h*0.6), int(w*0.3):int(w*0.7)]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape)==3 else roi
            # 结算画面背景变暗，亮度均值下降
            mean_brightness = np.mean(gray)
            # 经验阈值：正常游戏>100，结算<80（待实机校准）
            if mean_brightness < 80:
                return True
            return False
        except:
            return False

    def check_hand_stable(self, get_screenshot_func, min_cards=10):
        """手牌区域稳定度校验（Gemini双重确认防护网）
        连续3帧截图，像素差异小且识别出>=min_cards张牌才算稳定
        返回: True=稳定可出牌，False=还在动画中
        """
        try:
            import cv2
            import numpy as np
            import time
            frames = []
            for _ in range(3):
                img = get_screenshot_func()
                if img is None:
                    return False
                h, w = img.shape[:2]
                # 手牌ROI
                roi = img[int(h*0.87):int(h*0.97), int(w*0.1):int(w*0.9)]
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape)==3 else roi
                frames.append(gray)
                time.sleep(0.1)
            # 检查帧间差异
            for i in range(1, 3):
                diff = cv2.absdiff(frames[0], frames[i])
                if np.mean(diff) > 10:  # 阈值：画面还在动
                    return False
            # 检查识别出足够多牌
            from mahjong_vision import MahjongVision
            v = MahjongVision()
            r = v.recognize_hand(frames[2], min_confidence=0.75)
            valid = [x for x in r if x[0] != "unknown"]
            return len(valid) >= min_cards
        except:
            return False

    def detect_meld_prompt(self, img):
        """通用吃碰杠提示检测（Gemini方案：HSV高饱和颜色掩膜）
        街机提示：右下角/手牌上方弹出，金黄/红色高亮按钮
        返回: 'chi'/'pon'/'kan'/'ron' 或 None
        """
        try:
            import cv2
            import numpy as np
            h, w = img.shape[:2]
            # ROI：右下角区域（提示常出现位置）
            roi = img[int(h*0.6):int(h*0.95), int(w*0.6):w]
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # 黄色掩膜（Hue 15-35）：高亮按钮
            yellow_mask = cv2.inRange(hsv, np.array([15, 100, 100]), np.array([35, 255, 255]))
            # 红色掩膜（Hue 0-10, 160-180）
            red_mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
            red_mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            # 计算占比
            total = roi.shape[0] * roi.shape[1]
            yellow_ratio = np.sum(yellow_mask > 0) / total
            red_ratio = np.sum(red_mask > 0) / total
            # 阈值：占比突然飙升（>5%）判定为提示触发
            # 注意：无法区分chi/pon/kan，返回通用'meld'
            if yellow_ratio > 0.05 or red_ratio > 0.05:
                return 'meld'  # 有提示，但不知具体哪种
            return None
        except:
            return None

    def read_credit_bet(self, img):
        """读取CREDIT和BET（模板匹配，用户实测坐标）
        CREDIT: x 400-445, y 635-685 (1280x800)
        BET: x 943-993, y 629-679 (中心968,654)
        返回: (credit, bet) 或 (None, None)
        """
        try:
            import cv2
            h, w = img.shape[:2]
            # 用户实测坐标（2026-10-18）
            # CREDIT: 相对 (0.3125,0.7937)-(0.3477,0.8562)
            credit_roi = img[int(h*0.7937):int(h*0.8562), int(w*0.3125):int(w*0.3477)]
            # BET: 中心 (968,654)，50x50
            bet_roi = img[651-25:651+25, 938-25:938+25]
            matcher = ArcadeDigitMatcher('templates/digits')
            credit = matcher.recognize(credit_roi, 'credit')
            bet = matcher.recognize(bet_roi, 'bet')
            return (credit, bet)
        except:
            return (None, None)

    def ensure_credit_and_bet(self, controller, target_bet=10, timeout=15.0):
        """确保CREDIT>=10且BET达到目标（Gemini BetControl方案）
        """
        import time
        start = time.time()
        # 1. CREDIT<=10自动上500分（用户2026-10-18确认）
        while time.time() - start < timeout:
            img = self.capture_screen()
            if img is None:
                break
            credit, bet = self.read_credit_bet(img)
            if credit is not None and credit <= 10:
                print(f"[上分] credit={credit}<=10，上500分")
                controller.auto_refill_credits(times=5)
                time.sleep(1)
            else:
                break
        # 2. BET轮询到10
        start = time.time()
        while time.time() - start < timeout:
            img = self.capture_screen()
            if img is None:
                break
            credit, bet = self.read_credit_bet(img)
            if bet is not None and bet >= target_bet:
                print(f"[BET] 已达到 {bet}/{target_bet}")
                return True
            print(f"[BET] 当前{bet}，补押注")
            controller.press_key('3')  # BET键
            time.sleep(0.3)
        return False

    def is_odds_screen(self, img):
        """检测是否进入ODDS页（Gemini方案）
        特征：中央赔率矩阵占50%+，彩色方块+黄/绿边框
        ROI: X 30-70%, Y 20-60%
        """
        try:
            import cv2
            import numpy as np
            h, w = img.shape[:2]
            roi = img[int(h*0.2):int(h*0.6), int(w*0.3):int(w*0.7)]
            # 检测彩色像素占比（ODDS页色彩丰富）
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # 高饱和度像素占比
            _, s, _ = cv2.split(hsv)
            colorful_ratio = np.sum(s > 50) / s.size
            return colorful_ratio > 0.3  # 阈值待调
        except:
            return False

    def detect_dora(self, img):
        """检测宝牌指示牌（Gemini方案）
        ROI: X 0.40-0.60, Y 0.15-0.30（手牌上方中央）
        返回：宝牌编码或None
        """
        try:
            import cv2
            h, w = img.shape[:2]
            roi = img[int(h*0.15):int(h*0.30), int(w*0.40):int(w*0.60)]
            # TODO: 用模板匹配识别牌面
            # 先返回ROI供调试
            return roi
        except:
            return None

    def detect_exchange_phase(self, img):
        """检测换牌阶段（Gemini方案）
        特征：中央大字"請選擇換牌"/倒计时条
        """
        try:
            import cv2
            import numpy as np
            h, w = img.shape[:2]
            # 中央ROI
            roi = img[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape)==3 else roi
            # 大字通常是白色/红色高亮
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_ratio = np.sum(thresh > 0) / thresh.size
            # 换牌提示文字占比高
            return white_ratio > 0.15
        except:
            return False


    def find_ui_boxes(self, img):
        """检测UI框（用户标准：每个内容都有框，取框内内容）
        返回：[(x, y, w, h), ...] 框列表
        """
        import cv2
        import numpy as np
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img
            # 找边缘
            edges = cv2.Canny(gray, 50, 150)
            # 找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = []
            h, w = img.shape[:2]
            for cnt in contours:
                x, y, bw, bh = cv2.boundingRect(cnt)
                # 过滤太小或太大的框
                if bw > 50 and bh > 20 and bw < w*0.5 and bh < h*0.3:
                    # 检查是否为矩形（4个顶点）
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
                    if len(approx) == 4:
                        boxes.append((x, y, bw, bh))
            return sorted(boxes, key=lambda b: (b[1], b[0]))  # 按y,x排序
        except:
            return []
    
    def crop_box_content(self, img, box, margin=5):
        """取框内内容（去边框）"""
        x, y, w, h = box
        x1 = max(0, x + margin)
        y1 = max(0, y + margin)
        x2 = min(img.shape[1], x + w - margin)
        y2 = min(img.shape[0], y + h - margin)
        return img[y1:y2, x1:x2]

class ArcadeDigitMatcher:
    """街机数字模板匹配器（Gemini问题14：替代OCR，99.9%准确率）
    模板：templates/digits/{credit,bet}_0.png ~ _9.png
    """
    def __init__(self, template_dir="templates/digits"):
        import os
        import cv2
        self.templates = {}
        for prefix in ['credit', 'bet']:
            for d in range(10):
                path = os.path.join(template_dir, f"{prefix}_{d}.png")
                if os.path.exists(path):
                    self.templates[f"{prefix}_{d}"] = cv2.imread(path, 0)
    
    def segment_digits(self, roi):
        """水平投影分割多位数"""
        import cv2
        import numpy as np
        if roi is None or roi.size == 0:
            return []
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape)==3 else roi
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # 水平投影
        proj = np.sum(binary > 0, axis=0)
        # 找间隙（投影为0的区域）
        segments = []
        in_digit = False
        start = 0
        for x in range(len(proj)):
            if proj[x] > 0 and not in_digit:
                in_digit = True
                start = x
            elif proj[x] == 0 and in_digit:
                in_digit = False
                segments.append((start, x))
        if in_digit:
            segments.append((start, len(proj)))
        return [roi[:, s:e] for s, e in segments if e-s > 5]
    
    def recognize(self, roi, prefix='credit'):
        """识别ROI中的数字"""
        # Gemini问题16修复：方差校验，空白ROI直接返回None
        import numpy as np
        _gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        if np.var(_gray) < 100:
            return None
        import cv2
        digits = self.segment_digits(roi)
        result = ""
        for d_img in digits:
            best = ('', 0)
            for i in range(10):
                key = f"{prefix}_{i}"
                if key not in self.templates:
                    continue
                tmpl = self.templates[key]
                # 缩放到相同高度
                h = d_img.shape[0]
                scale = h / tmpl.shape[0]
                w = int(tmpl.shape[1] * scale)
                tmpl_r = cv2.resize(tmpl, (w, h))
                # 确保不大于输入
                if tmpl_r.shape[1] > d_img.shape[1]:
                    continue
                gray = cv2.cvtColor(d_img, cv2.COLOR_BGR2GRAY) if len(d_img.shape)==3 else d_img
                res = cv2.matchTemplate(gray, tmpl_r, cv2.TM_CCOEFF_NORMED)
                _, score, _, _ = cv2.minMaxLoc(res)
                if score > best[1]:
                    best = (str(i), score)
            if best[1] > 0.7:
                result += best[0]
        return int(result) if result else None
