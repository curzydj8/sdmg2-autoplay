#!/usr/bin/env python3
"""
credit_bet_policy - 上分下注策略模块
独立于弃牌策略
"""
from dataclasses import dataclass
from enum import Enum

class BetStrategy(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class CreditState:
    credit: int
    bet: int
    # DIP设置（来自2026-10-14截图）
    credit_limit: int = 2000      # ✅已验证
    min_bet: int = 1              # ✅已验证
    max_bet: int = None           # ❓未知（不得猜测）
    double_up_jackpot: int = 500  # ✅已验证
    
    def can_bet(self) -> bool:
        return self.credit > 0
    
    def can_start(self) -> bool:
        return self.bet >= self.min_bet

class CreditBetPolicy:
    """下注决策"""
    
    def __init__(self, strategy=BetStrategy.CONSERVATIVE):
        self.strategy = strategy
    
    def decide(self, state: CreditState, phase: str) -> dict:
        """
        返回决策: {action, amount, reason}
        """
        if phase != "ODDS":
            return {"action": "wait", "reason": "非投注阶段"}
        
        if self.strategy == BetStrategy.CONSERVATIVE:
            # 保守：只在credit充足时下最小注
            if state.credit >= 10 and state.bet == 0:
                return {"action": "bet", "amount": 1, 
                       "reason": "保守策略：credit>=10时下最小注1"}
            elif state.bet >= 1:
                return {"action": "start", "reason": "已有下注，开始游戏"}
            else:
                return {"action": "coin", "reason": "credit不足，先投币"}
        
        elif self.strategy == BetStrategy.MODERATE:
            # 中等：根据历史表现调整（待实现）
            return {"action": "bet", "amount": 1,
                   "reason": "中等策略：暂用最小注（待历史数据）"}
        
        else:  # AGGRESSIVE
            # 高风险：仅在明确实验条件下
            return {"action": "wait",
                   "reason": "高风险策略需明确实验授权，当前拒绝执行"}

# 当前采用：保守策略
DEFAULT_POLICY = CreditBetPolicy(BetStrategy.CONSERVATIVE)
