#!/usr/bin/env python3
"""优化评价指标 - 12项指标追踪"""
import json
from pathlib import Path
from datetime import datetime

METRICS_FILE = Path("/home/hatch/workspace/sdmg2-test/learning/metrics.json")

DEFAULT_METRICS = {
    "phase_accuracy": {"value": 0.0, "samples": 0, "desc": "游戏阶段识别准确率"},
    "tile_accuracy": {"value": 0.0, "samples": 0, "desc": "牌面识别准确率"},
    "legal_action_accuracy": {"value": 0.0, "samples": 0, "desc": "合法动作判断准确率"},
    "input_success_rate": {"value": 0.0, "samples": 0, "desc": "输入发送成功率"},
    "game_accept_rate": {"value": 0.0, "samples": 0, "desc": "游戏实际接受动作比例"},
    "invalid_action_ratio": {"value": 0.0, "samples": 0, "desc": "无效操作比例"},
    "rules_verified": {"value": 8, "samples": 8, "desc": "规则假设验证数量"},
    "rule_error_rate": {"value": 0.0, "samples": 0, "desc": "规则识别错误率"},
    "prediction_match": {"value": 0.0, "samples": 0, "desc": "预测与实际吻合度"},
    "strategy_scores": {"value": [], "samples": 0, "desc": "不同策略可比成绩"},
    "recovery_success": {"value": 1.0, "samples": 1, "desc": "异常恢复成功率(23:58红屏恢复)"},
    "optimizations_deployed": {"value": 2, "samples": 2, "desc": "AI提出测试部署的优化数"},
    "last_updated": "",
}

def load():
    if METRICS_FILE.exists():
        return json.loads(METRICS_FILE.read_text())
    return DEFAULT_METRICS.copy()

def save(metrics):
    metrics["last_updated"] = datetime.now().isoformat()
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

def update(metric_name, value, samples=1):
    m = load()
    if metric_name in m:
        old = m[metric_name]
        # 加权平均
        total = old["samples"] + samples
        if total > 0:
            m[metric_name]["value"] = (old["value"] * old["samples"] + value * samples) / total
            m[metric_name]["samples"] = total
        save(m)

if __name__ == "__main__":
    save(load())
    print("指标框架已建立")
