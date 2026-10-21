#!/usr/bin/env python3
"""
智能决策 AI 模块 ai_engine.py
- 打牌算法与大满贯博弈策略
- 计算向听数、牌效、危险牌规避
- 大满贯模式下的策略切换
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class MahjongAI:
    def __init__(self, risk_level=0.5):
        self.risk_level = risk_level

    def select_best_discard(self, hand_cards):
        """Gemini三启发式规则（鲁棒决策）"""
        if not hand_cards:
            return 13
        # 分离已知和未知
        known = [(i, c) for i, c in enumerate(hand_cards) if c != 'unknown']
        unknown_idx = [i for i, c in enumerate(hand_cards) if c == 'unknown']
        # 规则1：孤张字牌/幺九最优先打（从已知中找）
        for i, c in known:
            if c in ('dong','nan','xi','bei','zhong','fa','bai'):
                # 检查是否孤张（无对子）
                if sum(1 for _, x in known if x == c) == 1:
                    return i
        for i, c in known:
            if c in ('1wan','9wan','1tiao','9tiao','1bing','9bing'):
                if sum(1 for _, x in known if x == c) == 1:
                    return i
        # 规则2：保护对子和搭子，不打它们
        from collections import Counter
        cnt = Counter(c for _, c in known)
        protected = set()
        for c, n in cnt.items():
            if n >= 2:
                protected.add(c)
        # 找搭子（连续两张）
        # 简化：保留已知中有用的，优先打unknown
        # 规则3：unknown槽位智能兜底（不盲打索引0）
        if unknown_idx:
            # 打最后一个unknown（假设是刚摸的）
            return unknown_idx[-1]
        # 全已知：用high_fan_strategy
        try:
            from high_fan_strategy import choose_discard
            codes = [c for _, c in known]
            idx, _, _, _ = choose_discard(codes, "balanced")
            return known[idx][0]
        except:
            pass
        return len(hand_cards) - 1

    def should_double_up(self, win_score):
        """胡牌后是否比倍：小分激进，大分保守"""
        # risk_level越高越激进
        threshold = 100 * (1.5 - self.risk_level)
        return win_score < threshold

    def should_meld(self, prompt, hand_cards):
        """吃碰杠决策，复用game_agent逻辑"""
        if prompt == 'ron':
            return True
        if prompt == 'kan':
            return True
        if prompt == 'pon':
            from collections import Counter
            cnt = Counter(hand_cards)
            pairs = sum(1 for v in cnt.values() if v >= 2)
            return pairs < 4  # 七对子倾向不碰
        return False  # 吃保守不吃

    def evaluate_hand_archetype(self, hand_cards):
        """评估手牌最适合的牌型路线（Gemini问题13，13张全换）"""
        from collections import Counter
        suit_counts = {"wan": 0, "tiao": 0, "tong": 0, "honor": 0}
        tile_freq = Counter()
        non_tanyao = []
        for i, c in enumerate(hand_cards):
            if c == 'unknown':
                continue
            tile_freq[c] += 1
            if c.endswith('wan'):
                suit_counts["wan"] += 1
                if c in ('1wan','9wan'):
                    non_tanyao.append(i)
            elif c.endswith('tiao'):
                suit_counts["tiao"] += 1
                if c in ('1tiao','9tiao'):
                    non_tanyao.append(i)
            elif c.endswith('tong') or c.endswith('bing'):
                suit_counts["tong"] += 1
                if c in ('1tong','9tong','1bing','9bing'):
                    non_tanyao.append(i)
            else:
                suit_counts["honor"] += 1
                non_tanyao.append(i)
        max_suit = max(suit_counts, key=suit_counts.get)
        if suit_counts[max_suit] >= 8 and max_suit != "honor":
            change = [i for i,c in enumerate(hand_cards)
                     if c!='unknown' and not self._in_suit(c,max_suit)]
            return "chinitsu", change
        pairs = sum(1 for v in tile_freq.values() if v>=2)
        if pairs >= 3:
            change = [i for i,c in enumerate(hand_cards)
                     if c!='unknown' and tile_freq[c]==1]
            return "chiitoitsu", change
        return "tanyao", non_tanyao

    def _in_suit(self, card, suit):
        if suit=="wan": return card.endswith('wan')
        if suit=="tiao": return card.endswith('tiao')
        if suit=="tong": return card.endswith('tong') or card.endswith('bing')
        return False

    def select_exchange_tiles(self, hand_cards):
        """兼容接口：调用牌型评估"""
        _, indices = self.evaluate_hand_archetype(hand_cards)
        return indices
    def decide_bet_amount(self, credits, hand_quality='normal'):
        """动态押注（Gemini阶梯策略）
        credits: 当前信用分
        hand_quality: 'poor'/'normal'/'good'
        返回：押注分数
        """
        if credits < 100:
            return 1  # 贫血期保命
        elif credits > 300:
            if hand_quality == 'good':
                return 10  # 好牌拉满
            return 5  # 富裕期常规
        else:
            return 5 if hand_quality != 'poor' else 2
