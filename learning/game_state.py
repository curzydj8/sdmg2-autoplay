#!/usr/bin/env python3
"""
麻将状态表示 - 基于实际观察，不套用标准规则
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class Phase(Enum):
    ODDS = "ODDS"           # 投注
    EXCHANGE = "EXCHANGE"   # 换牌
    MAIN = "MAIN"           # 主局
    UNKNOWN = "UNKNOWN"

@dataclass
class Tile:
    """单张牌"""
    position: str  # A-N
    suit: Optional[str] = None  # wan/tong/tiao/honor (需识别)
    value: Optional[str] = None  # 1-9 / east/south/west/north/white/green/red
    confidence: float = 0.0
    
@dataclass
class GameState:
    """游戏状态"""
    phase: Phase
    phase_confidence: float
    credit: Optional[int] = None
    bet: Optional[int] = None
    donden: Optional[int] = None
    hand: List[Tile] = field(default_factory=list)
    # 以下待实现自动识别
    discards: List[str] = field(default_factory=list)
    timestamp: str = ""
    screenshot_path: str = ""
    
    def is_valid(self) -> bool:
        """状态是否有效"""
        if self.phase == Phase.UNKNOWN:
            return False
        if self.phase_confidence < 0.5:
            return False
        return True
    
    def legal_actions(self) -> List[Dict]:
        """生成合法动作（基于已验证规则）"""
        if self.phase == Phase.ODDS:
            return [
                {"key": "5", "desc": "投币", "rule": "R001"},
                {"key": "3", "desc": "压注", "rule": "R002"},
                {"key": "1", "desc": "开始", "rule": "R003"},
            ]
        elif self.phase == Phase.EXCHANGE:
            # 换牌：选择手牌
            return [{"key": t.position.lower(), "desc": f"换{t.position}", "rule": "R005"}
                    for t in self.hand if t.position]
        elif self.phase == Phase.MAIN:
            actions = [{"key": "n", "desc": "摸牌", "rule": "R004"}]
            actions += [{"key": t.position.lower(), "desc": f"打{t.position}", "rule": "R005"}
                       for t in self.hand if t.position]
            return actions
        return []

# 牌效评分（待用真实数据校准）
def score_discard(tile: Tile, hand: List[Tile]) -> float:
    """
    弃牌评分（初始启发式，需实战校准）
    高分 = 优先打出
    """
    score = 0.0
    
    # 孤张字牌优先打（启发式，未验证）
    if tile.suit == "honor":
        # 检查是否有对子
        same = sum(1 for t in hand if t.value == tile.value)
        if same < 2:
            score += 10.0
    
    # 边张次之（1、9）
    if tile.value in ("1", "9"):
        score += 5.0
    
    # TODO: 需要实现向听数、有效牌计算
    # 当前为占位，待真实牌面识别后完善
    
    return score
