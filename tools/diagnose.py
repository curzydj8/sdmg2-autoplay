"""失败阶段定位诊断工具（用户2026-10-18优先级1）
记录：阶段、状态、置信度、候选动作、输入事件、前后截图、积分/画面变化
指标：成功启动、成功进牌局、整手识别正确、合法动作成功、完成牌局
"""
import sys
sys.path.insert(0, 'modules')
import time
import os
from datetime import datetime

class StageDiagnostics:
    def __init__(self, output_dir='/tmp/diagnose'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.metrics = {
            '成功启动': 0, '成功进入牌局': 0,
            '整手识别正确': 0, '合法动作成功': 0, '完成牌局': 0,
            '总尝试': 0
        }
        self.log = []
    
    def record(self, stage, state, confidence, action, input_event, 
               credit_before, credit_after, screen_changed):
        """记录一次诊断"""
        entry = {
            'time': datetime.now().isoformat(),
            'stage': stage,
            'state': state,
            'confidence': confidence,
            'action': action,
            'input_event': input_event,
            'credit_before': credit_before,
            'credit_after': credit_after,
            'credit_changed': credit_before != credit_after,
            'screen_changed': screen_changed,
        }
        self.log.append(entry)
        self.metrics['总尝试'] += 1
        return entry
    
    def report(self):
        """输出指标报告"""
        print("=" * 50)
        print("失败阶段定位报告")
        print("=" * 50)
        for k, v in self.metrics.items():
            print(f"  {k}: {v}")
        print(f"\n最近{len(self.log)}条记录:")
        for e in self.log[-5:]:
            print(f"  [{e['stage']}] {e['state']} "
                  f"置信度={e['confidence']} 动作={e['action']} "
                  f"积分{e['credit_before']}→{e['credit_after']} "
                  f"画面变化={e['screen_changed']}")
        # 定位主要失败阶段
        print("\n主要失败阶段分析:")
        stages = {}
        for e in self.log:
            s = e['stage']
            if s not in stages:
                stages[s] = {'total': 0, 'fail': 0}
            stages[s]['total'] += 1
            if not e['screen_changed'] and e['action'] != '无':
                stages[s]['fail'] += 1
        for s, d in stages.items():
            rate = d['fail'] / d['total'] * 100 if d['total'] else 0
            print(f"  {s}: 失败率 {rate:.1f}% ({d['fail']}/{d['total']})")

if __name__ == '__main__':
    d = StageDiagnostics()
    # 示例：记录一次BET阶段
    d.record(
        stage='BET',
        state='ODDS等待',
        confidence=0.0,  # 模板匹配返回None
        action='按3',
        input_event='KEY_3 press+release',
        credit_before=2,
        credit_after=2,
        screen_changed=False,  # 画面未变，按键无效
    )
    d.report()
