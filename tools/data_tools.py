#!/usr/bin/env python3
"""JSONL导出 + 数据质量检查 v1.0"""
import sqlite3
import json
import os

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")


def export_jsonl(session_id=None, out_path=None):
    """导出对局数据为JSONL"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    q = "SELECT * FROM game_sessions"
    if session_id:
        q += f" WHERE id={session_id}"
    sessions = [dict(r) for r in conn.execute(q)]

    out = out_path or os.path.expanduser(
        f"~/workspace/sdmg2-test/data/export_s{session_id or 'all'}.jsonl")

    with open(out, "w", encoding="utf-8") as f:
        for s in sessions:
            sid = s["id"]
            states = [dict(r) for r in conn.execute(
                "SELECT * FROM game_states WHERE session_id=?", (sid,))]
            actions = [dict(r) for r in conn.execute(
                "SELECT * FROM actions WHERE session_id=?", (sid,))]
            f.write(json.dumps({
                "session": s, "states": states, "actions": actions,
            }, ensure_ascii=False) + "\n")

    conn.close()
    print(f"导出: {out}（{len(sessions)}局）")
    return out


def check_quality():
    """数据质量检查"""
    conn = sqlite3.connect(DB_PATH)
    issues = []

    # 1. 缺少动作后状态：action result=pending
    n = conn.execute(
        "SELECT COUNT(*) FROM actions WHERE result='pending'").fetchone()[0]
    if n:
        issues.append(f"未完成动作: {n}")

    # 2. 没有结束的对局
    n = conn.execute(
        "SELECT COUNT(*) FROM game_sessions WHERE ended_at IS NULL").fetchone()[0]
    if n:
        issues.append(f"未结束对局: {n}")

    # 3. 非法动作（chosen为空）
    n = conn.execute(
        "SELECT COUNT(*) FROM actions WHERE chosen='' OR chosen IS NULL").fetchone()[0]
    if n:
        issues.append(f"非法动作: {n}")

    # 4. 状态动作关联错误
    n = conn.execute("""
        SELECT COUNT(*) FROM actions a
        LEFT JOIN game_states s ON a.state_id=s.id
        WHERE s.id IS NULL
    """).fetchone()[0]
    if n:
        issues.append(f"关联错误: {n}")

    conn.close()

    if not issues:
        print("数据质量检查通过：无问题")
    else:
        print("发现问题:")
        for i in issues:
            print(f"  - {i}")
    return issues


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_quality()
    else:
        export_jsonl()
