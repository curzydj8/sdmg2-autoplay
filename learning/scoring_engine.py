#!/usr/bin/env python3
"""
scoring_engine - 计分引擎
注意：尚未观察到实际得分，所有规则标记为未知
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ScoreEvent:
    """得分事件"""
    timestamp: str
    bet: int
    predicted_score: Optional[int] = None
    actual_score: Optional[int] = None
    credit_before: Optional[int] = None
    credit_after: Optional[int] = None
    credit_change: Optional[int] = None
    prediction_error: Optional[int] = None
    screenshot: str = ""

class ScoringEngine:
    """
    计分引擎
    
    当前状态：未观察到任何得分事件
    - 未见胡牌
    - 未见结算画面
    - 未见CREDIT因得分增加
    """
    
    def __init__(self):
        self.events = []
    
    def record(self, event: ScoreEvent):
        self.events.append(event)
    
    def get_stats(self):
        return {
            "total_events": len(self.events),
            "note": "暂无得分数据，需继续观察"
        }

# 已知（来自DIP）：
# - Double Up Jackpot: 500（比倍奖励上限）
# - Minimum Bet: 1

# 未知：
# - 牌型得分表
# - 下注倍率
# - 和牌条件
# - 结算流程
