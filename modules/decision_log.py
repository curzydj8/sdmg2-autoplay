#!/usr/bin/env python3
"""
决策日志 v1.0
按任务书要求记录每次决策的完整信息。
"""
import time
import json


class DecisionLog:
    def __init__(self):
        self.start = time.time()

    def log(self, state_summary, strength, strength_source,
            bet_level, exchange_info, candidates,
            scores, excluded, chosen):
        """
        :param state_summary: 状态摘要
        :param strength: 牌面strength
        :param strength_source: strength来源
        :param bet_level: 押注档位
        :param exchange_info: 换牌信息
        :param candidates: 候选动作列表
        :param scores: 每个动作评分 {action: score}
        :param excluded: 被排除动作 {action: 原因}
        :param chosen: 最终选择
        """
        elapsed = (time.time() - self.start) * 1000
        record = {
            "state": state_summary,
            "strength": strength,
            "strength_source": strength_source,
            "bet": bet_level,
            "exchange": exchange_info,
            "candidates": candidates,
            "scores": scores,
            "excluded": excluded,
            "chosen": chosen,
            "duration_ms": round(elapsed, 1),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return record


if __name__ == "__main__":
    dl = DecisionLog()
    dl.log(
        state_summary="play, 14张手牌",
        strength="normal", strength_source="evaluate_hand_strength v1",
        bet_level=5,
        exchange_info="不换（打牌阶段）",
        candidates=["a", "b", "c"],
        scores={"a": 80, "b": 60, "c": 40},
        excluded={"d": "非法：未知牌"},
        chosen="a",
    )
