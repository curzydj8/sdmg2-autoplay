"""MAME全窗口捕获 + 内存比例分割器
彻底解决窗口漂移：截取整个游戏窗口全图，在内存中按比例切分ROI。
(0,0)永远是游戏画面左上角，不受窗口边框/DPI/任务栏影响。
"""
import cv2
import numpy as np

class MameScreenSplitter:
    """全屏捕获 + 比例网格切片器"""
    
    # ROI比例定义（相对于游戏画面）
    ROI_RATIOS = {
        'credit':     ((0.78, 0.92), (0.05, 0.35)),  # 左下
        'bet':        ((0.78, 0.92), (0.65, 0.95)),  # 右下
        'jackpot':    ((0.78, 0.92), (0.35, 0.65)),  # 中下（大满贯BET）
        'hand_tiles': ((0.80, 0.98), (0.10, 0.90)),  # 手牌区
        'settlement': ((0.30, 0.70), (0.25, 0.75)),  # 中央弹窗
        'dora':       ((0.15, 0.30), (0.40, 0.60)),  # 宝牌区
        'odds_table': ((0.10, 0.75), (0.05, 0.95)),  # 赔率表
    }
    
    def __init__(self, vision=None):
        # 用VisionEngine的全屏截图（已验证可用），避免mss窗口rect问题
        if vision is None:
            import sys
            sys.path.insert(0, 'modules')
            from vision import VisionEngine
            vision = VisionEngine()
        self.vision = vision
    
    def get_mame_rect(self):
        """获取MAME窗口客户区坐标
        Returns: (left, top, width, height) 或 None
        """
        import subprocess
        import os
        try:
            env = os.environ.copy()
            env['DISPLAY'] = env.get('DISPLAY', ':0')
            # 找MAME窗口
            out = subprocess.check_output(
                ['xdotool', 'search', '--name', 'Chaoji'],
                stderr=subprocess.STDOUT, timeout=3, env=env
            ).decode().strip().split('\n')
            if not out or not out[0]:
                return None
            wid = out[0].strip()
            # 获取窗口几何
            geo = subprocess.check_output(
                ['xdotool', 'getwindowgeometry', wid],
                stderr=subprocess.STDOUT, timeout=3, env=env
            ).decode()
            # 解析: Position: X,Y  Geometry: WxH
            import re
            m_pos = re.search(r'Position:\s*(\d+),(\d+)', geo)
            m_geo = re.search(r'Geometry:\s*(\d+)x(\d+)', geo)
            if not m_pos or not m_geo:
                return None
            x, y = int(m_pos.group(1)), int(m_pos.group(2))
            w, h = int(m_geo.group(1)), int(m_geo.group(2))
            return {'left': x, 'top': y, 'width': w, 'height': h}
        except Exception as e:
            print(f"[Splitter] 获取窗口失败: {e}")
            return None
    
    def capture_and_split_all(self):
        """核心：截取全屏并在内存中按比例分割所有ROI
        Returns: {'credit': img, 'bet': img, ...} 或 None
        """
        try:
            frame = self.vision.capture_screen()
        except Exception as e:
            print(f"[Splitter] 全图截取失败: {e}")
            return None
        if frame is None:
            return None
        
        h, w = frame.shape[:2]
        if h < 100 or w < 100:
            return None
        
        rois = {}
        for name, ((y1r, y2r), (x1r, x2r)) in self.ROI_RATIOS.items():
            y1, y2 = int(h * y1r), int(h * y2r)
            x1, x2 = int(w * x1r), int(w * x2r)
            rois[name] = frame[y1:y2, x1:x2]
        
        rois['_full'] = frame
        rois['_size'] = (w, h)
        return rois
