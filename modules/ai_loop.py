#!/usr/bin/env python3
"""
AI 打牌主循环 v1.0
截图 → 模板匹配认牌 → tile_codec 编码 → Gemma 决策 → uinput 执行
边打边补：未知牌自动保存到 unknown/ 待标注
"""
import cv2
import numpy as np
import os
import sys
import time
import base64
import json
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from tile_codec import encode_hand, decode_discard, encode_tile

TEMPLATE_DIR = os.path.expanduser("~/workspace/sdmg2-test/templates")
UNKNOWN_DIR = os.path.expanduser("~/workspace/sdmg2-test/unknown")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"


class AILoop:
    def __init__(self):
        self.templates = {}
        self.load_templates()
        os.makedirs(UNKNOWN_DIR, exist_ok=True)

    def load_templates(self):
        for fname in os.listdir(TEMPLATE_DIR):
            if fname.endswith(".png"):
                name = fname[:-4]
                img = cv2.imread(os.path.join(TEMPLATE_DIR, fname), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.templates[name] = img
        print(f"加载模板: {len(self.templates)} 张")

    def screenshot(self, path="/tmp/ai_hand.png"):
        """截屏（调用方需保证 DISPLAY）"""
        os.system(
            "export DISPLAY=:0 XAUTHORITY=/home/zhangdawei/.Xauthority; "
            f"xwd -root -silent 2>/dev/null | xwdtopnm 2>/dev/null | "
            f"pnmtopng 2>/dev/null > {path} || "
            f"xwd -root -silent 2>/dev/null > /tmp/ai.xwd && "
            f"xwdtopnm /tmp/ai.xwd 2>/dev/null > /tmp/ai.ppm && "
            f"ffmpeg -y -v error -i /tmp/ai.ppm {path}"
        )
        return path if os.path.exists(path) else None

    def match_tile(self, tile_img, threshold=0.75):
        """模板匹配单张牌，返回 (编码, 置信度)"""
        gray = cv2.cvtColor(tile_img, cv2.COLOR_BGR2GRAY) if len(tile_img.shape) == 3 else tile_img
        best, best_score = "unknown", 0
        for name, tmpl in self.templates.items():
            if tmpl.shape[0] > gray.shape[0] or tmpl.shape[1] > gray.shape[1]:
                continue
            res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, _ = cv2.minMaxLoc(res)
            if score > best_score:
                best_score, best = score, name
        if best_score >= threshold:
            return encode_tile(best), best_score
        return "unknown", best_score

    def segment_hand(self, screenshot_path, num_tiles=14):
        """从截图切出手牌区并分割（需根据实际画面调坐标）"""
        img = cv2.imread(screenshot_path)
        if img is None:
            return []
        h, w = img.shape[:2]
        # 手牌区：底部，相对坐标（1280x720 基准，需实测微调）
        x, y = int(w * 0.10), int(h * 0.82)
        rw, rh = int(w * 0.80), int(h * 0.15)
        hand = img[y:y+rh, x:x+rw]
        tiles = []
        tw = rw // num_tiles
        for i in range(num_tiles):
            t = hand[:, i*tw:(i+1)*tw]
            tiles.append((chr(ord('a')+i), t))
        return tiles

    def ask_gemma(self, prompt, timeout=120):
        data = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(OLLAMA_URL, data=data,
                                     headers={"Content-Type": "application/json"})
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            return json.loads(resp.read()).get("response", "").strip()
        except Exception as e:
            return f"ERROR:{e}"

    def press_key(self, key_name):
        """uinput 按键（需 evdev）"""
        from evdev import UInput, ecodes as E
        key_map = {"1": E.KEY_1, "5": E.KEY_5, "enter": E.KEY_ENTER,
                   "space": E.KEY_SPACE}
        for ch in "abcdefghijklmn":
            key_map[ch] = getattr(E, f"KEY_{ch.upper()}")
        code = key_map.get(key_name.lower())
        if not code:
            return False
        ui = UInput({E.EV_KEY: [code]}, name="ai-player")
        time.sleep(0.2)
        ui.write(E.EV_KEY, code, 1); ui.syn(); time.sleep(0.1)
        ui.write(E.EV_KEY, code, 0); ui.syn()
        ui.close()
        return True

    def run_once(self):
        """单步：截图→认牌→Gemma→执行，返回决策日志"""
        shot = self.screenshot()
        if not shot:
            return {"error": "截图失败"}

        segments = self.segment_hand(shot)
        vision_result = []
        for slot, tile_img in segments:
            code, conf = self.match_tile(tile_img)
            vision_result.append((slot, code, conf))
            if code == "unknown" and conf < 0.5:
                # 保存未知牌供标注
                ts = int(time.time())
                cv2.imwrite(f"{UNKNOWN_DIR}/{slot}_{ts}.png", tile_img)

        encoded = encode_hand([(s, c, cf) for s, c, cf in vision_result])
        print("手牌:", [t["code"] for t in encoded["tiles"] if t["code"] != "unknown"])
        print("未知:", sum(1 for t in encoded["tiles"] if t["code"] == "unknown"))

        gemma_resp = self.ask_gemma(encoded["gemma_prompt"])
        print("Gemma:", gemma_resp[:100])

        slot = decode_discard(gemma_resp, encoded["tiles"])
        if slot:
            self.press_key(slot)
            return {"discard_slot": slot, "gemma": gemma_resp[:200],
                    "known": len([t for t in encoded["tiles"] if t["code"] != "unknown"]),
                    "unknown": len([t for t in encoded["tiles"] if t["code"] == "unknown"])}
        return {"error": "无法决策", "gemma": gemma_resp[:200]}


if __name__ == "__main__":
    loop = AILoop()
    result = loop.run_once()
    print("结果:", result)
