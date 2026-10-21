"""智能截图工具v2：基于MAME窗口动态几何"""
import subprocess
import cv2

def get_mame_geometry():
    """获取MAME窗口几何（x,y,w,h）"""
    try:
        out = subprocess.check_output(
            ['xdotool', 'search', '--name', 'Chaoji', 'getwindowgeometry', '--shell'],
            env={'DISPLAY': ':0'}, text=True, timeout=5)
        geom = {}
        for line in out.strip().split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                geom[k.strip()] = int(v.strip())
        return (geom.get('X', 0), geom.get('Y', 0),
                geom.get('WIDTH', 1280), geom.get('HEIGHT', 800))
    except:
        return (0, 0, 1280, 800)

def capture_odds_digits(img):
    """从ODDS屏提取CREDIT/BET数字（基于窗口相对坐标）
    返回: {'credit': roi, 'bet': roi}
    """
    # 先获取MAME窗口在屏幕中的位置
    wx, wy, ww, wh = get_mame_geometry()
    h, w = img.shape[:2]
    # MAME窗口内的相对坐标（实测）
    # CREDIT数字：窗口内 x 0.25-0.30, y 0.79-0.86
    # BET数字：窗口内 x 0.72-0.75, y 0.79-0.86
    # 转换为屏幕绝对坐标
    credit_x1 = int(wx + ww * 0.25)
    credit_x2 = int(wx + ww * 0.30)
    credit_y1 = int(wy + wh * 0.79)
    credit_y2 = int(wy + wh * 0.86)
    bet_x1 = int(wx + ww * 0.72)
    bet_x2 = int(wx + ww * 0.75)
    bet_y1 = int(wy + wh * 0.79)
    bet_y2 = int(wy + wh * 0.86)
    # 裁剪（确保不越界）
    credit_roi = img[max(0,credit_y1):min(h,credit_y2), max(0,credit_x1):min(w,credit_x2)]
    bet_roi = img[max(0,bet_y1):min(h,bet_y2), max(0,bet_x1):min(w,bet_x2)]
    return {'credit': credit_roi, 'bet': bet_roi}
