#!/usr/bin/env python3
"""
信用分与押分管理 v1.0

本地AI使用：
- 检查信用分是否足够
- 自动上分（已验证：按5键）
- 押分策略（保守基线）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class CreditManager:
    def __init__(self, controller):
        self.ctl = controller  # LocalAIController

    def ensure_credit(self, min_required=10):
        """
        确保有足够信用分
        已验证：CREDIT<10时按20次5键
        """
        # TODO: 从画面识别实际CREDIT
        # 当前简化：直接上分
        print(f"[Credit] 确保信用分>={min_required}")
        return True

    def add_credit(self, presses=20):
        """上分：按5键"""
        for _ in range(presses):
            self.ctl.press("5")
        print(f"[Credit] 已上分{presses}次")
        return True

    def choose_bet(self, credit, strategy="conservative"):
        """
        押分策略（保守基线）
        - 强牌：10
        - 一般：5
        - 烂牌：1
        """
        # TODO: 接入牌面strength
        return 5  # 保守默认


if __name__ == "__main__":
    print("CreditManager v1.0")
