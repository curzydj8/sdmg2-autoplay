"""Read CREDIT/BET with template matching and an OCR fallback."""
import cv2
import numpy as np

class SafeCreditBetReader:
    def __init__(self, vision):
        self.vision = vision
        self.consecutive_failures = 0
    
    def read_with_fallback(self, img):
        """读取CREDIT/BET；识别失败时保持未知状态，不触发按键。
        返回: (credit, bet, needs_topup)
        """
        # 层1：模板匹配
        try:
            credit, bet = self.vision.read_credit_bet(img)
            if credit is not None or bet is not None:
                self.consecutive_failures = 0
                needs_topup = credit is not None and 0 <= credit <= 10
                return (credit, bet, needs_topup)
        except Exception as exc:
            print(f"[识别] 模板读取失败: {type(exc).__name__}: {exc}")

        try:
            credit = self._ocr_credit(img)
            if credit is not None:
                self.consecutive_failures = 0
                return (credit, None, 0 <= credit <= 10)
        except Exception as exc:
            print(f"[识别] OCR读取失败: {type(exc).__name__}: {exc}")

        self.consecutive_failures += 1
        return (None, None, False)
    
    def _ocr_credit(self, img):
        """OCR兜底读CREDIT"""
        import pytesseract
        import re
        h, w = img.shape[:2]
        roi = img[int(h*0.7937):int(h*0.8562), int(w*0.27):int(w*0.39)]
        if roi.size == 0:
            return None
        # 放大3倍+二值化
        big = cv2.resize(roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        txt = pytesseract.image_to_string(
            binary, 
            config='--psm 7 -c tessedit_char_whitelist=0123456789'
        )
        digits = re.findall(r'\d+', txt)
        return int(digits[0]) if digits else None
