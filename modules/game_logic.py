"""游戏标准流程逻辑模块（独立可测试）
标准流程（用户2026-10-18确立）：
1. 检查CREDIT：0-10 → 上500分；>10 → 跳过
2. 循环读BET：<10 → 按3；==10 → 停止（最多15次）
3. 确认BET==10 → 按1 START

Gemini问题16/17修复：
- 上分分批（每次10次，防MAME缓冲区溢出）
- 按键含释放动作
- CREDIT=0时按3无效，必须先上分
- ROI用锚点法，不用硬坐标
"""

class StandardGameFlow:
    """标准开局流程"""
    
    def __init__(self, vision, controller):
        self.vision = vision
        self.controller = controller
        self.target_bet = 10
    
    def check_credit_needs_topup(self, credit):
        """步骤1：检查是否需要上分
        返回: True=需要上分(CREDIT 0-10), False=不需要
        """
        return credit is not None and 0 <= credit <= 10
    
    def topup_credits(self, times=500):
        """上分：按5键times次，分批（每次10次）"""
        import time
        batches = times // 10
        for b in range(batches):
            for _ in range(10):
                self.controller.press_key('COIN', delay=0.03)  # 5键=投币
                time.sleep(0.03)
            time.sleep(0.2)
    
    def bet_until_target(self, max_attempts=15):
        """步骤2：循环压分到目标
        返回: (success, final_bet)
        """
        import time
        for attempt in range(max_attempts):
            img = self.vision.capture_screen()
            if img is None:
                continue
            _, bet = self.vision.read_credit_bet(img)
            if bet is not None and bet >= self.target_bet:
                return (True, bet)
            # 按3（含释放）
            self.controller.press_key('BET', delay=0.05)
            time.sleep(0.8)
        return (False, None)
    
    def should_start(self, bet):
        """步骤3：是否可以START"""
        return bet == self.target_bet
    
    def run(self):
        """执行完整标准流程
        返回: {'success': bool, 'credit': int, 'bet': int, 'steps': []}
        """
        import time
        result = {'success': False, 'credit': None, 'bet': None, 'steps': []}
        
        # 步骤1：读CREDIT
        img = self.vision.capture_screen()
        if img is None:
            result['steps'].append('截图失败')
            return result
        credit, bet = self.vision.read_credit_bet(img)
        result['credit'] = credit
        result['bet'] = bet
        result['steps'].append(f'读取: CREDIT={credit}, BET={bet}')
        
        # 步骤1b：需要上分？
        if self.check_credit_needs_topup(credit):
            result['steps'].append(f'CREDIT={credit}在0-10，上500分')
            self.topup_credits(500)
            time.sleep(1)
        else:
            result['steps'].append(f'CREDIT={credit}，跳过上分')
        
        # 步骤2：压分
        success, final_bet = self.bet_until_target()
        result['bet'] = final_bet
        if not success:
            result['steps'].append(f'压分失败，BET={final_bet}')
            return result
        result['steps'].append(f'压分成功，BET={final_bet}')
        
        # 步骤3：START
        if self.should_start(final_bet):
            self.controller.press_key('START', delay=0.05)
            result['steps'].append('已按START')
            result['success'] = True
        else:
            result['steps'].append(f'BET={final_bet}≠10，不START')
        
        return result
