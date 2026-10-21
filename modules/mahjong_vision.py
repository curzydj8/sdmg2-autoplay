#!/usr/bin/env python3
"""
麻将牌面识别模块 v1.0
- 模板必须从真实游戏截图裁剪
- 低置信度不打牌
"""
import cv2
import numpy as np
import os

class MahjongVision:
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "templates",
        )
        self.templates = {}  # name -> (image, w, h)
        self.load_templates()
    
    def load_templates(self):
        """加载模板库"""
        if not os.path.exists(self.template_dir):
            return
        for fname in os.listdir(self.template_dir):
            if fname.endswith(".png"):
                name = fname[:-4]
                path = os.path.join(self.template_dir, fname)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    h, w = img.shape
                    self.templates[name] = (img, w, h)
    
    def locate_hand_area(self, screenshot):
        """
        定位手牌区域（底部 A-N）
        基于 1003x731 窗口：手牌约在 y=580-700，x=30-970
        :return: (x, y, w, h) 或 None
        """
        h, w = screenshot.shape[:2]
        # 相对坐标（适应不同分辨率）
        x = int(w * 0.03)
        y = int(h * 0.79)
        rw = int(w * 0.94)
        rh = int(h * 0.16)
        return (x, y, rw, rh)
    
    def segment_tiles(self, hand_img, num_tiles=14):
        """
        分割单张牌
        :return: list of tile images
        """
        h, w = hand_img.shape[:2]
        tile_w = w // num_tiles
        tiles = []
        for i in range(num_tiles):
            x = i * tile_w
            tile = hand_img[0:h, x:x+tile_w]
            tiles.append(tile)
        return tiles
    
    def identify_tile(self, tile_img):
        """
        识别单张牌
        :return: (name, confidence) 或 (None, 0.0)
        """
        if not self.templates:
            return None, 0.0
        
        gray = cv2.cvtColor(tile_img, cv2.COLOR_BGR2GRAY) if len(tile_img.shape) == 3 else tile_img
        # 预处理：拉普拉斯锐化（Gemini建议：去掉二值化，保持灰度梯度）
        import numpy as np
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)
        
        best_name = None
        best_score = 0.0
        
        for name, (tmpl, tw, th) in self.templates.items():
            # 缩放模板到 tile 尺寸
            h, w = gray.shape
            if tw != w or th != h:
                tmpl_resized = cv2.resize(tmpl, (w, h))
            else:
                tmpl_resized = tmpl
            
            # 多尺度匹配：0.95~1.05，解决1-2像素偏差（Gemini方案）
            best_scale_score = 0
            for scale in [0.95, 0.98, 1.0, 1.02, 1.05]:
                sw, sh = int(w * scale), int(h * scale)
                if sw < 10 or sh < 10:
                    continue
                scaled = cv2.resize(tmpl_resized, (sw, sh))
                # 确保模板不大于输入
                if scaled.shape[0] > gray.shape[0] or scaled.shape[1] > gray.shape[1]:
                    continue
                result = cv2.matchTemplate(gray, scaled, cv2.TM_CCOEFF_NORMED)
                _, s, _, _ = cv2.minMaxLoc(result)
                if s > best_scale_score:
                    best_scale_score = s
            score = best_scale_score
            
            if score > best_score:
                best_score = float(score)
                best_name = name
        
        return best_name, best_score
    
    def recognize_hand(self, screenshot, min_confidence=0.7):
        """
        识别整手牌
        :return: list of (name, confidence) 或 None（低置信度）
        """
        area = self.locate_hand_area(screenshot)
        if not area:
            return None
        
        x, y, w, h = area
        hand_img = screenshot[y:y+h, x:x+w]
        tiles = self.segment_tiles(hand_img)
        
        results = []
        for tile in tiles:
            name, conf = self.identify_tile(tile)
            if conf < min_confidence:
                # 低置信度：标记未知，不猜
                results.append((f"UNKNOWN", conf))
            else:
                results.append((name, conf))
        
        return results


if __name__ == "__main__":
    print("MahjongVision v1.0")
    print("模板目录:", os.path.expanduser("~/workspace/sdmg2-test/templates"))
    v = MahjongVision()
    print(f"已加载 {len(v.templates)} 个模板")


def split_bamboo_tile_projection(tile_crop, expected_cuts=1, threshold_ratio=0.35):
    """投影剖面分析法: 处理条子(4-7条)竹子粘连分割（Gemini方案）"""
    import cv2
    import numpy as np
    if len(tile_crop.shape) == 3:
        gray = cv2.cvtColor(tile_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = tile_crop.copy()
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    projection = np.sum(cleaned > 0, axis=0)
    projection_smooth = np.convolve(projection, np.ones(3) / 3, mode="same")
    max_val = np.max(projection_smooth)
    min_val = np.min(projection_smooth)
    valley_threshold = min_val + (max_val - min_val) * threshold_ratio
    valleys = []
    in_valley = False
    start_x = 0
    width = len(projection_smooth)
    for x in range(width):
        if projection_smooth[x] < valley_threshold:
            if not in_valley:
                in_valley = True
                start_x = x
        else:
            if in_valley:
                in_valley = False
                end_x = x - 1
                valleys.append((start_x + end_x) // 2)
    if in_valley:
        valleys.append((start_x + (width - 1)) // 2)
    if len(valleys) > expected_cuts:
        valleys = sorted(valleys, key=lambda vx: projection_smooth[vx])[:expected_cuts]
        valleys = sorted(valleys)
    return valleys, projection_smooth
