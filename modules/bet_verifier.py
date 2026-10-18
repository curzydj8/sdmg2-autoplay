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
        before_bet, before_mode = self._read_bet(before_img)
        after_bet, after_mode = self._read_bet(after_img)
        
        # UNKNOWN: 无法识别
        if before_bet is None or after_bet is None:
            return (VerifyResult.UNKNOWN, 
                    f"识别失败(前={before_bet}[{before_mode}], 后={after_bet}[{after_mode}])")
        
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
        """读取BET数字（区分失败模式，不吞异常）
        
        Returns:
            (bet: int|None, failure_mode: str)
            failure_mode: 'ok' | 'no_vision' | 'no_method' | 
                          'exception' | 'none_result' | 'bad_format'
        """
        if self.vision is None:
            return (None, 'no_vision')
        if not hasattr(self.vision, 'read_credit_bet'):
            return (None, 'no_method')
        try:
            result = self.vision.read_credit_bet(img)
        except Exception as e:
            return (None, f'exception:{type(e).__name__}:{e}')
        if result is None:
            return (None, 'none_result')
        if not isinstance(result, (tuple, list)) or len(result) != 2:
            return (None, f'bad_format:{type(result)}')
        _, bet = result
        if bet is None:
            return (None, 'none_result')
        return (bet, 'ok')
