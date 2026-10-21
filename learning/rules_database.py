#!/usr/bin/env python3
"""超级大满贯Ⅱ 规则库 - 基于真机实测"""
import json
from datetime import datetime
from pathlib import Path

RULES_FILE = Path(__file__).parent / "rules-database.json"

class Rule:
    def __init__(self, rule_id, description, **kwargs):
        self.rule_id = rule_id
        self.description = description
        self.source = kwargs.get("source", "")
        self.phase = kwargs.get("phase", "")
        self.preconditions = kwargs.get("preconditions", "")
        self.expected = kwargs.get("expected", "")
        self.actual = kwargs.get("actual", "")
        self.confidence = kwargs.get("confidence", 0.0)
        self.status = kwargs.get("status", "unknown")  # verified/pending/unknown/refuted
        self.last_verified = kwargs.get("last_verified", "")

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "source": self.source,
            "phase": self.phase,
            "preconditions": self.preconditions,
            "expected": self.expected,
            "actual": self.actual,
            "confidence": self.confidence,
            "status": self.status,
            "last_verified": self.last_verified,
        }

# 基于 2026-10-14 真机实测的规则
RULES = [
    Rule("R001", "按5投币增加CREDIT",
         source="2026-10-14 22:22 真机实测，用户确认CREDIT=1→5",
         phase="投注/ODDS",
         preconditions="游戏在ODDS界面",
         expected="CREDIT+1",
         actual="CREDIT确实增加，但丢键率高",
         confidence=0.95, status="verified",
         last_verified="2026-10-14 23:45"),
    
    Rule("R002", "按3下注增加BET",
         source="2026-10-14 23:46 真机实测，截图BET=0→1",
         phase="投注/ODDS",
         preconditions="CREDIT>0，游戏在ODDS界面",
         expected="BET+1，CREDIT-1",
         actual="BET=1，截图证实",
         confidence=0.95, status="verified",
         last_verified="2026-10-14 23:46"),
    
    Rule("R003", "按1开始游戏",
         source="2026-10-14 23:14 系统测试，截图画面大变进入选牌阶段",
         phase="投注/ODDS",
         preconditions="BET>0",
         expected="进入选牌交换阶段",
         actual="进入'請選擇您要交換的牌'阶段",
         confidence=0.95, status="verified",
         last_verified="2026-10-14 23:14"),
    
    Rule("R004", "按N摸牌",
         source="用户 2026-10-14 23:21 明确指示",
         phase="主局打牌",
         preconditions="轮到玩家行动",
         expected="从牌墙摸一张牌",
         actual="待截图验证",
         confidence=0.8, status="pending",
         last_verified=""),
    
    Rule("R005", "按A-N选择/打出对应牌",
         source="2026-10-14 23:14 系统测试，A/N/Z/Space均引起画面变化",
         phase="选牌/主局",
         preconditions="游戏在选牌或打牌阶段",
         expected="选中或打出对应位置的牌",
         actual="画面变化证实有效",
         confidence=0.9, status="verified",
         last_verified="2026-10-14 23:14"),
    
    Rule("R006", "DIP Controls=Mahjong是正确模式",
         source="2026-10-14 22:38 用户截图DIP菜单，Controls: Mahjong",
         phase="系统设置",
         preconditions="MAME DIP设置",
         expected="Joystick模式下注无效，Mahjong模式有效",
         actual="切换回Mahjong后下注有效",
         confidence=0.9, status="verified",
         last_verified="2026-10-14 23:46"),
    
    Rule("R007", "游戏流程：投币→压注→开始→换牌→打牌→结算",
         source="2026-10-14 全程真机观察",
         phase="全局",
         preconditions="",
         expected="",
         actual="ODDS→换牌(請選擇您要交換的牌)→主局(DONDEN)→结算→ODDS",
         confidence=0.95, status="verified",
         last_verified="2026-10-14 23:46"),
    
    Rule("R008", "CPU超时自动出牌",
         source="用户 2026-10-14 22:50 确认",
         phase="主局打牌",
         preconditions="玩家未在时限内出牌",
         expected="系统自动打出",
         actual="用户确认",
         confidence=0.9, status="verified",
         last_verified="2026-10-14 22:50"),
]

def save():
    data = [r.to_dict() for r in RULES]
    RULES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"已保存 {len(data)} 条规则到 {RULES_FILE}")

if __name__ == "__main__":
    save()
