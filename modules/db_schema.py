#!/usr/bin/env python3
"""
SQLite 数据库 schema v1.0
10张表：game_sessions, game_states, actions, episodes, tile_templates,
        rules, training_samples, model_versions, evaluations, knowledge
"""
import sqlite3
import os

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")

SCHEMA = """
-- 会话
CREATE TABLE IF NOT EXISTS game_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_version TEXT,
    rom_id TEXT,
    started_at TEXT,
    ended_at TEXT,
    config_version TEXT,
    result TEXT
);

-- 状态快照
CREATE TABLE IF NOT EXISTS game_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    round_no INTEGER,
    state_json TEXT,
    phase TEXT,
    score INTEGER,
    confidence REAL,
    source TEXT,
    created_at TEXT,
    FOREIGN KEY(session_id) REFERENCES game_sessions(id)
);
CREATE INDEX IF NOT EXISTS idx_states_session ON game_states(session_id);

-- 动作
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    state_id INTEGER,
    candidates_json TEXT,
    chosen TEXT,
    result TEXT,
    duration_ms INTEGER,
    fail_reason TEXT,
    strategy_version TEXT,
    created_at TEXT,
    FOREIGN KEY(session_id) REFERENCES game_sessions(id)
);

-- 整局
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    final_score INTEGER,
    target_reached INTEGER,
    review_json TEXT,
    created_at TEXT
);

-- 牌模板
CREATE TABLE IF NOT EXISTS tile_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tile_code TEXT UNIQUE,
    template_path TEXT,
    template_version TEXT,
    label_source TEXT,
    verified INTEGER DEFAULT 0
);

-- 规则
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT UNIQUE,
    version TEXT,
    content TEXT,
    source TEXT,
    verified INTEGER DEFAULT 0,
    test_case TEXT
);

-- 训练样本
CREATE TABLE IF NOT EXISTS training_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_features TEXT,
    legal_actions TEXT,
    human_action TEXT,
    model_action TEXT,
    reward REAL,
    final_result TEXT,
    data_source TEXT,
    created_at TEXT
);

-- 模型版本
CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_path TEXT,
    model_type TEXT,
    data_version TEXT,
    train_params TEXT,
    eval_result TEXT,
    created_at TEXT
);

-- 评估
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_version TEXT,
    games INTEGER,
    win_rate REAL,
    avg_score REAL,
    target_rate REAL,
    illegal_rate REAL,
    duration_s REAL,
    created_at TEXT
);

-- 知识库
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT,
    content TEXT,
    verified INTEGER DEFAULT 0,
    created_at TEXT
);

-- schema版本
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT
);
"""


def init_db(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO schema_version VALUES (1, datetime('now'))")
    conn.commit()
    conn.close()
    print(f"数据库已初始化: {path}")
    return path


if __name__ == "__main__":
    init_db()


def migrate_v2(path=DB_PATH):
    """v2迁移：加 strategy_configs 表"""
    import sqlite3
    conn = sqlite3.connect(path)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS strategy_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT UNIQUE,
        bet_strategy_json TEXT,
        strong_bet INTEGER,
        normal_bet INTEGER,
        weak_bet INTEGER,
        default_bet INTEGER,
        doubleup_risk TEXT,
        exchange_policy TEXT,
        adaptive_exchange INTEGER DEFAULT 0,
        effective_at TEXT,
        verified INTEGER DEFAULT 0
    );
    """)
    conn.execute("INSERT OR IGNORE INTO schema_version VALUES (2, datetime('now'))")
    # 插入默认v1配置
    conn.execute("""
    INSERT OR IGNORE INTO strategy_configs
    (version, bet_strategy_json, strong_bet, normal_bet, weak_bet, default_bet,
     doubleup_risk, exchange_policy, adaptive_exchange, effective_at, verified)
    VALUES ('v1', '{"strong":10,"normal":5,"weak":1}', 10, 5, 1, 10,
            'aggressive', 'first3', 0, datetime('now'), 1)
    """)
    conn.commit()
    conn.close()
    print("v2迁移完成：strategy_configs")


def migrate_v3(path=DB_PATH):
    """v3迁移：game_sessions加target_score"""
    import sqlite3
    conn = sqlite3.connect(path)
    try:
        conn.execute("ALTER TABLE game_sessions ADD COLUMN target_score INTEGER DEFAULT 500")
        conn.execute("ALTER TABLE game_sessions ADD COLUMN target_verified INTEGER DEFAULT 1")
        print("v3迁移：game_sessions加target_score")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("v3已应用")
        else:
            raise
    conn.execute("INSERT OR IGNORE INTO schema_version VALUES (3, datetime('now'))")
    conn.commit()
    conn.close()


def migrate_v4(path=DB_PATH):
    """v4迁移：建settings规则表"""
    import sqlite3
    conn = sqlite3.connect(path)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        setting_id TEXT PRIMARY KEY,
        setting_name TEXT,
        category TEXT,
        description TEXT,
        access_method TEXT,
        default_value TEXT,
        allowed_values TEXT,
        current_value TEXT,
        effective_value TEXT,
        value_source TEXT,
        game_version TEXT,
        rom_identifier TEXT,
        evidence TEXT,
        validation_status TEXT DEFAULT 'unknown',
        validation_method TEXT,
        affects_gameplay INTEGER DEFAULT 0,
        affects_ai_strategy INTEGER DEFAULT 0,
        last_verified_at TEXT
    );
    """)
    conn.execute("INSERT OR IGNORE INTO schema_version VALUES (4, datetime('now'))")
    conn.commit()
    conn.close()
    print("v4迁移完成：settings表")
