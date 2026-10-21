#!/usr/bin/env python3
"""
对局记录器 v1.0
统一写入 SQLite：会话/状态/动作/对局，带事务保证。
"""
import sqlite3
import json
import os
import time

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")


class Recorder:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.session_id = None

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def start_session(self, game_version="0.285", rom_id="sdmg2",
                      config_version="v1", data_source="dry_run"):
        """创建对局，返回 session_id"""
        conn = self._conn()
        cur = conn.execute("""
            INSERT INTO game_sessions
            (game_version, rom_id, started_at, config_version, result, ended_at)
            VALUES (?, ?, datetime('now'), ?, 'running', NULL)
        """, (game_version, rom_id, config_version))
        self.session_id = cur.lastrowid
        # 记录数据来源到 knowledge（临时方案，待加字段）
        conn.commit()
        conn.close()
        print(f"对局开始: session_id={self.session_id} 来源={data_source}")
        return self.session_id

    def record_state(self, session_id, round_no, state_json,
                     phase="", score=0, confidence=0.0, source="vision"):
        """记录状态快照，返回 state_id"""
        conn = self._conn()
        cur = conn.execute("""
            INSERT INTO game_states
            (session_id, round_no, state_json, phase, score,
             confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (session_id, round_no, json.dumps(state_json, ensure_ascii=False),
              phase, score, confidence, source))
        state_id = cur.lastrowid
        conn.commit()
        conn.close()
        return state_id

    def record_action(self, session_id, state_id, candidates,
                      chosen, result="pending", duration_ms=0,
                      fail_reason="", strategy_version="v1"):
        """记录动作，返回 action_id"""
        conn = self._conn()
        cur = conn.execute("""
            INSERT INTO actions
            (session_id, state_id, candidates_json, chosen, result,
             duration_ms, fail_reason, strategy_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (session_id, state_id, json.dumps(candidates, ensure_ascii=False),
              chosen, result, duration_ms, fail_reason, strategy_version))
        action_id = cur.lastrowid
        conn.commit()
        conn.close()
        return action_id

    def finish_action(self, action_id, result, fail_reason=""):
        """更新动作结果"""
        conn = self._conn()
        conn.execute("""
            UPDATE actions SET result=?, fail_reason=? WHERE id=?
        """, (result, fail_reason, action_id))
        conn.commit()
        conn.close()

    def end_session(self, session_id, final_score=0,
                    target_reached=0, result="completed"):
        """结束对局"""
        conn = self._conn()
        conn.execute("""
            UPDATE game_sessions
            SET ended_at=datetime('now'), result=? WHERE id=?
        """, (result, session_id))
        conn.execute("""
            INSERT INTO episodes
            (session_id, final_score, target_reached, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (session_id, final_score, target_reached))
        conn.commit()
        conn.close()
        print(f"对局结束: session_id={session_id} 得分={final_score}")

    def mark_interrupted(self, session_id, reason="异常退出"):
        """标记中断（程序异常退出时调用）"""
        self.end_session(session_id, result=f"interrupted: {reason}")


if __name__ == "__main__":
    r = Recorder()
    sid = r.start_session(data_source="test")
    st = r.record_state(sid, 1, {"hand": ["1wan"]*14}, phase="play", score=100)
    aid = r.record_action(sid, st, ["a", "b"], "a", duration_ms=120)
    r.finish_action(aid, "success")
    r.end_session(sid, final_score=150)
    print("记录器自测通过")
