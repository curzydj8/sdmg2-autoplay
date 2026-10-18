"""BET三态验证器（用户2026-10-18）
VERIFIED：确认BET数字或游戏状态出现预期变化
NOT_VERIFIED：截图有效可比较，但未观察到预期变化
UNKNOWN：截图失败、模板无法识别或结果不确定
"""
from enum import Enum

class VerifyResult(Enum):
    VERIFIED = "VERIFIED"        # 确认预期变化
    NOT_VERIFIED = "NOT_VERIFIED"  # 有效比较，无预期变化
    UNKNOWN = "UNKNOWN"          # 无法判断

class BETVerifier:
    """BET指示区域验证器"""
    
    def __init__(self, vision=None):
        self.vision = vision
    
    def can_verify(self):
        """发送前检查：是否具备验证条件
        缺少vision或截图失败时，拒绝操作（返回False）
        """
        if self.vision is None:
            return False
        try:
            img = self.vision.capture_screen()
            return img is not None
        except:
            return False
    
    def verify_bet_change(self, before_img, after_img, expected_direction='increase'):
        """验证BET是否按预期变化
        
        Returns:
            (VerifyResult, detail: str)
        """
        # UNKNOWN: 截图无效
        if before_img is None or after_img is None:
            return (VerifyResult.UNKNOWN, "截图失败")
        
        # 尝试读取BET数字
        before_bet = self._read_bet(before_img)
        after_bet = self._read_bet(after_img)
        
        # UNKNOWN: 无法识别
        if before_bet is None or after_bet is None:
            return (VerifyResult.UNKNOWN, 
                    f"模板无法识别(前={before_bet}, 后={after_bet})")
        
        # VERIFIED / NOT_VERIFIED: 数字可比较
        if expected_direction == 'increase':
            if after_bet > before_bet:
                return (VerifyResult.VERIFIED, 
                        f"BET {before_bet}→{after_bet} 增加")
            else:
                return (VerifyResult.NOT_VERIFIED,
                        f"BET {before_bet}→{after_bet} 未增加")
        elif expected_direction == 'decrease':
            if after_bet < before_bet:
                return (VerifyResult.VERIFIED,
                        f"BET {before_bet}→{after_bet} 减少")
            else:
                return (VerifyResult.NOT_VERIFIED,
                        f"BET {before_bet}→{after_bet} 未减少")
        else:  # any change
            if after_bet != before_bet:
                return (VerifyResult.VERIFIED,
                        f"BET {before_bet}→{after_bet} 变化")
            else:
                return (VerifyResult.NOT_VERIFIED,
                        f"BET {before_bet}→{after_bet} 未变化")
    
    def _read_bet(self, img):
        """读取BET数字（占位：当前模板匹配不可靠，返回None）"""
        # TODO: 接入可靠的BET识别
        # 当前状态：模板匹配返回None → 触发UNKNOWN
        if self.vision and hasattr(self.vision, 'read_credit_bet'):
            try:
                _, bet = self.vision.read_credit_bet(img)
                return bet
            except:
                pass
        return None
