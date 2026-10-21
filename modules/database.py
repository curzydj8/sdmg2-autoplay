#!/usr/bin/env python3
"""
数据库模块 database.py
SQLite记录：游戏配置、每局投币/得分、牌局日志、胜率统计

表：
- game_configs: setting_name, target_bet, enable_double_up, ai_risk_level
- match_logs: timestamp, bet_score, win_score, is_grand_slam, hand_cards, result_type
"""
import os
import sqlite3
from datetime import datetime

_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_base, "data", "sdmg2.db")


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    # Gemini建议：WAL模式+忙等待，解决90%锁库问题
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS game_configs (
            id INTEGER PRIMARY KEY,
            setting_name TEXT UNIQUE,
            target_bet INTEGER DEFAULT 10,
            enable_double_up INTEGER DEFAULT 1,
            ai_risk_level REAL DEFAULT 0.5
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS match_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            bet_score INTEGER,
            win_score INTEGER,
            is_grand_slam INTEGER DEFAULT 0,
            hand_cards TEXT,
            result_type TEXT
        )
    """)
    # 默认配置
    conn.execute("""
        INSERT OR IGNORE INTO game_configs
        (setting_name, target_bet, enable_double_up, ai_risk_level)
        VALUES ('default', 10, 1, 0.5)
    """)
    conn.commit()
    conn.close()


def get_config():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    row = conn.execute(
        "SELECT target_bet, enable_double_up, ai_risk_level FROM game_configs WHERE setting_name='default'"
    ).fetchone()
    conn.close()
    if row:
        return {"target_bet": row[0], "enable_double_up": row[1], "ai_risk_level": row[2]}
    return {"target_bet": 10, "enable_double_up": 1, "ai_risk_level": 0.5}


def log_match(bet_score, win_score, is_grand_slam=0, hand_cards="", result_type=""):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("""
        INSERT INTO match_logs
        (bet_score, win_score, is_grand_slam, hand_cards, result_type)
        VALUES (?, ?, ?, ?, ?)
    """, (bet_score, win_score, is_grand_slam, hand_cards, result_type))
    conn.commit()
    conn.close()


# 兼容性别名
def get_db_session():
    init_db()
    return None

GameConfig = None
MatchLog = None
