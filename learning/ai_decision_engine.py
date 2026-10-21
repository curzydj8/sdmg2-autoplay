#!/usr/bin/env python3
"""
超级大满贯Ⅱ AI决策引擎
观察 → 识别 → 规则检查 → 候选动作 → 评估 → 选择 → 执行 → 验证 → 学习
"""
import subprocess
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT = Path("/home/hatch/workspace/sdmg2-test")
SCREENSHOT_SCRIPT = "/tmp/portal_screenshot.py"
SSH = "ssh -F /home/hatch/.ssh/config zhang-new"

class AIDecisionEngine:
    def __init__(self):
        self.rules = self.load_rules()
        self.history = []
        self.wid = "10485767"
        
    def load_rules(self):
        rf = PROJECT / "learning" / "rules-database.json"
        if rf.exists():
            return json.loads(rf.read_text())
        return []
    
    def ssh(self, cmd, timeout=30):
        r = subprocess.run(f"{SSH} '{cmd}'", shell=True,
                          capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    
    def screenshot(self, name):
        """截图并返回路径"""
        remote = f"/tmp/xvfb-test/desktop/screenshots/ai-{name}.png"
        self.ssh(f'MYUID=$(id -u); export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$MYUID/bus"; '
                f'timeout 30 python3 {SCREENSHOT_SCRIPT} {remote} 2>&1 | tail -1')
        local = PROJECT / "screenshots" / f"ai-{name}.png"
        subprocess.run(f"{SSH} \"base64 -w 0 {remote}\" 2>&1 | base64 -d > {local} 2>&1",
                      shell=True, timeout=60)
        return str(local) if local.exists() else None
    
    def identify_phase(self, screenshot_path):
        """
        识别游戏阶段
        返回: (phase, confidence)
        phase: ODDS / EXCHANGE / MAIN / UNKNOWN
        """
        # 简化版：用文件大小启发式 + 关键词
        # 完整版需要OCR，这里先用大小区分
        p = Path(screenshot_path)
        if not p.exists():
            return "UNKNOWN", 0.0
        size = p.stat().st_size
        # ODDS界面通常较大（紫色背景复杂），游戏界面中等
        # 这是启发式，需要更多样本校准
        if size > 1200000:
            return "ODDS", 0.6
        elif size > 800000:
            return "MAIN", 0.6
        else:
            return "UNKNOWN", 0.3
    
    def get_legal_actions(self, phase):
        """根据阶段生成合法动作"""
        if phase == "ODDS":
            return [
                {"action": "coin", "key": "5", "desc": "投币"},
                {"action": "bet", "key": "3", "desc": "压注"},
                {"action": "start", "key": "1", "desc": "开始"},
            ]
        elif phase == "EXCHANGE":
            # 换牌阶段：选择要换的牌
            return [{"action": f"exchange_{c}", "key": c, "desc": f"换牌{c}"}
                    for c in "abcdefghijklmn"]
        elif phase == "MAIN":
            return [
                {"action": "draw", "key": "n", "desc": "摸牌"},
            ] + [{"action": f"discard_{c}", "key": c, "desc": f"打牌{c}"}
                 for c in "abcdefghijklm"]
        return []
    
    def select_action(self, phase, actions):
        """选择动作（规则基线）"""
        if phase == "ODDS":
            # 优先顺序：有CREDIT则下注，否则投币；有BET则开始
            # 简化：按固定顺序尝试
            return actions[0]  # 先投币
        elif phase == "EXCHANGE":
            # 选择孤张：优先换字牌和边张
            for a in actions:
                if a["key"] in "klm":  # 西、中等
                    return a
            return actions[0]
        elif phase == "MAIN":
            return actions[0]  # 先摸牌
        return None
    
    def execute(self, action):
        """执行输入"""
        key = action["key"]
        self.ssh(f'export DISPLAY=:0; export XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.EN5WW3; '
                f'xdotool key --delay 150 --window {self.wid} {key} 2>/dev/null; echo OK')
        return True
    
    def verify(self, before_path, after_path):
        """验证动作是否生效（比较截图）"""
        try:
            bh = hashlib.md5(Path(before_path).read_bytes()).hexdigest()
            ah = hashlib.md5(Path(after_path).read_bytes()).hexdigest()
            return bh != ah
        except:
            return False
    
    def decide_and_act(self):
        """完整决策循环"""
        ts = datetime.now().strftime("%H%M%S")
        record = {"timestamp": ts}
        
        # 1. 观察
        before = self.screenshot(f"decide-{ts}-before")
        record["screenshot_before"] = before
        
        # 2. 识别
        phase, conf = self.identify_phase(before)
        record["phase"] = phase
        record["phase_confidence"] = conf
        
        if phase == "UNKNOWN" or conf < 0.5:
            record["decision"] = "skip_low_confidence"
            self.history.append(record)
            return record
        
        # 3. 生成候选
        actions = self.get_legal_actions(phase)
        record["candidates"] = [a["desc"] for a in actions]
        
        # 4. 选择
        chosen = self.select_action(phase, actions)
        record["chosen"] = chosen["desc"] if chosen else None
        record["reason"] = f"规则基线：{phase}阶段优先动作"
        
        if not chosen:
            record["decision"] = "no_action"
            self.history.append(record)
            return record
        
        # 5. 执行
        time.sleep(1)
        self.execute(chosen)
        record["executed_key"] = chosen["key"]
        
        # 6. 验证
        time.sleep(3)
        after = self.screenshot(f"decide-{ts}-after")
        record["screenshot_after"] = after
        changed = self.verify(before, after)
        record["effect_verified"] = changed
        
        self.history.append(record)
        
        # 保存历史
        hf = PROJECT / "learning" / "decision-history.json"
        hf.write_text(json.dumps(self.history[-100:], indent=2, ensure_ascii=False))
        
        return record

if __name__ == "__main__":
    engine = AIDecisionEngine()
    for i in range(5):  # 测试5轮
        r = engine.decide_and_act()
        print(f"[{r['timestamp']}] phase={r['phase']} chosen={r.get('chosen')} verified={r.get('effect_verified')}")
        time.sleep(5)
