#!/usr/bin/env python3
"""
Gemma异步分析接口 v1.0

职责：
- 后台读取已完成对局
- 输出结构化建议（不直接修改策略）
- 不阻塞本地AI实时循环

Muse负责验证建议，本地AI不等待Gemma。
"""
import os
import sys
import time
import json
import sqlite3
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")
OLLAMA_URL = "http://localhost:11434/api/generate"


class GemmaAnalyzer:
    def __init__(self):
        self.queue_path = os.path.expanduser(
            "~/workspace/sdmg2-test/data/gemma_queue.json")

    def get_completed_sessions(self):
        """获取已完成未分析的对局"""
        conn = sqlite3.connect(DB_PATH)
        # 简化：返回所有completed对局（实际应跟踪已分析）
        rs = conn.execute("""
            SELECT id FROM game_sessions
            WHERE result LIKE 'completed%'
        """).fetchall()
        conn.close()
        return [r[0] for r in rs]

    def get_session_data(self, session_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        s = dict(conn.execute(
            "SELECT * FROM game_sessions WHERE id=?", (session_id,)).fetchone())
        actions = [dict(r) for r in conn.execute(
            "SELECT * FROM actions WHERE session_id=?", (session_id,))]
        conn.close()
        return {"session": s, "actions": actions}

    def analyze(self, session_id):
        """调用Gemma分析（异步，不阻塞）"""
        data = self.get_session_data(session_id)
        prompt = f"""分析麻将对局数据，输出JSON：
对局ID: {session_id}
动作数: {len(data['actions'])}
结果: {data['session'].get('result')}

请输出：
{{
  "issues": ["问题1", ...],
  "suggestions": ["建议1", ...],
  "confidence": 0.8
}}"""

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps({
                    "model": "gemma3:4b",
                    "prompt": prompt,
                    "stream": False,
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            analysis = result.get("response", "")
            # 存入knowledge表，标记为待验证
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""
                INSERT INTO knowledge (kind, content, verified, created_at)
                VALUES ('gemma_analysis', ?, 0, datetime('now'))
            """, (json.dumps({
                "session_id": session_id,
                "analysis": analysis,
            }, ensure_ascii=False),))
            conn.commit()
            conn.close()
            print(f"[Gemma] 对局{session_id}分析完成（待验证）")
            return True
        except Exception as e:
            print(f"[Gemma] 分析失败: {e}")
            return False

    def run_once(self):
        sessions = self.get_completed_sessions()
        if not sessions:
            print("[Gemma] 无待分析对局")
            return
        for sid in sessions[:1]:  # 一次一个，不阻塞
            self.analyze(sid)


if __name__ == "__main__":
    GemmaAnalyzer().run_once()

def should_trigger_review(match_result, consecutive_losses):
    """Gemma复盘触发条件（Gemini建议：过滤80%无价值请求）
    只在惨败或3连败时触发
    """
    # 惨败：输分超过500
    if match_result.get('win_score', 0) < -500:
        return True
    # 3连败
    if consecutive_losses >= 3:
        return True
    return False
