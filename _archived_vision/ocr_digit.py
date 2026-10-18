"""OCR式数字识别实验；结果仅供诊断，不驱动按键。
用Tesseract识别数字，无法明确识别时返回未知。
返回输入形状、OCR文本和置信度供排查，不保存输入图像。
"""
import cv2
import numpy as np
import re

class OCRDigitReader:
    """OCR数字读取器（实验）"""
    
    def __init__(self):
        try:
            import pytesseract
            self.available = True
        except ImportError:
            self.available = False
    
    def preprocess(self, roi):
        """预处理：放大+二值化
        Returns: 处理后的图像，或None
        """
        if roi is None or roi.size == 0:
            return None
        # 放大3倍
        h, w = roi.shape[:2]
        big = cv2.resize(roi, (w*3, h*3), interpolation=cv2.INTER_CUBIC)
        # 转灰度
        gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY) if len(big.shape) == 3 else big
        # 二值化（绿色数字在深色背景上，数字亮）
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return binary
    
    def read(self, roi, expected_digits=None):
        """读取ROI中的数字
        Args:
            roi: 图像区域
            expected_digits: 期望的数字位数（用于验证），None表示不验证
        Returns:
            (text: str|None, confidence: float, debug: dict)
            - text为None表示"未知"，不猜数字
            - debug包含输入形状和原始OCR输出
        """
        debug = {'input_shape': None, 'raw_text': '', 'preprocessed': False}
        
        if not self.available:
            return (None, 0.0, {**debug, 'reason': 'pytesseract未安装'})
        
        proc = self.preprocess(roi)
        if proc is None:
            return (None, 0.0, {**debug, 'reason': '预处理失败'})
        
        debug['input_shape'] = proc.shape
        debug['preprocessed'] = True
        
        try:
            import pytesseract
            # PSM 7: 单行文本；只识别数字
            data = pytesseract.image_to_data(
                proc, 
                config='--psm 7 -c tessedit_char_whitelist=0123456789',
                output_type=pytesseract.Output.DICT
            )
            # 提取文本和置信度
            texts = []
            confs = []
            for i, txt in enumerate(data['text']):
                txt = txt.strip()
                if txt and re.match(r'^\d+$', txt):
                    texts.append(txt)
                    try:
                        confs.append(float(data['conf'][i]))
                    except:
                        confs.append(0.0)
            
            if not texts:
                debug['raw_text'] = ''
                return (None, 0.0, {**debug, 'reason': '无数字输出'})
            
            # 取最长的（多位数）
            text = max(texts, key=len)
            conf = max(confs) if confs else 0.0
            debug['raw_text'] = text
            
            # 验证：置信度阈值
            if conf < 30:  # Tesseract置信度0-100
                return (None, conf/100.0, {**debug, 'reason': f'置信度低({conf:.1f})'})
            
            # 验证：期望位数
            if expected_digits is not None and len(text) != expected_digits:
                return (None, conf/100.0, {**debug, 'reason': f'位数不符(期望{expected_digits}, 得{len(text)})'})
            
            return (text, conf/100.0, debug)
            
        except Exception as e:
            return (None, 0.0, {**debug, 'reason': f'异常: {e}'})
