#!/usr/bin/env python3
"""
设置规则库 v1.0
统一查询接口：AI通过此接口查询游戏设置，不直接猜测。
"""
import sqlite3
import os
import json

DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")

# DIP实测设置（来源：PHASE-32-DIP-FINDINGS.md，2026-10-14 Tab菜单实测）
DIP_SETTINGS = [
    ("DIP_COINAGE", "Coinage", "运营设置", "投币比率",
     "Tab→DIP Switches", "1 Coin/1 Credit", "多种", "1 Coin/1 Credit",
     "1 Coin/1 Credit", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 0, 0),
    ("DIP_KEYIN_RATE", "Key-In Rate", "运营设置", "Key-In比率",
     "Tab→DIP Switches", "10", "多种", "10",
     "10", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 0, 0),
    ("DIP_CREDIT_LIMIT", "Credit Limit", "爆机与分数", "积分上限",
     "Tab→DIP Switches", "2000", "多种", "2000",
     "2000", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 1, 1),
    ("DIP_JACKPOT", "Double Up Jackpot", "爆机与分数", "比倍奖池上限",
     "Tab→DIP Switches", "500", "多种", "500",
     "500", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 1, 1),
    ("DIP_MIN_BET", "Minimum Bet", "押注与比倍", "最小押注",
     "Tab→DIP Switches", "1", "多种", "1",
     "1", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 1, 1),
    ("DIP_DOUBLEUP", "Double Up Game", "押注与比倍", "比倍开关",
     "Tab→DIP Switches", "On", "On/Off", "On",
     "On", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 1, 1),
    ("DIP_CONTROLS", "Controls", "系统与环境", "控制方式",
     "Tab→DIP Switches", "Mahjong", "Mahjong/Joystick", "Mahjong",
     "Mahjong", "DIP实测", "sdmg2", "sdmg2.zip",
     "PHASE-32-DIP-FINDINGS.md", "verified", "Tab菜单实测", 1, 1),
]


def init_settings():
    """导入DIP设置"""
    conn = sqlite3.connect(DB_PATH)
    for s in DIP_SETTINGS:
        conn.execute("""
            INSERT OR REPLACE INTO settings
            (setting_id, setting_name, category, description, access_method,
             default_value, allowed_values, current_value, effective_value,
             value_source, game_version, rom_identifier, evidence,
             validation_status, validation_method,
             affects_gameplay, affects_ai_strategy, last_verified_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
        """, s)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
    conn.close()
    print(f"设置规则库：{n}项")
    return n


def query_setting(setting_id):
    """查询单个设置"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    r = conn.execute("SELECT * FROM settings WHERE setting_id=?",
                     (setting_id,)).fetchone()
    conn.close()
    return dict(r) if r else None


def query_by_category(category):
    """按类别查询"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rs = conn.execute("SELECT * FROM settings WHERE category=?",
                      (category,)).fetchall()
    conn.close()
    return [dict(r) for r in rs]


def list_categories():
    conn = sqlite3.connect(DB_PATH)
    rs = conn.execute("SELECT DISTINCT category FROM settings").fetchall()
    conn.close()
    return [r[0] for r in rs]


if __name__ == "__main__":
    init_settings()
    print("\n类别:", list_categories())
    j = query_setting("DIP_JACKPOT")
    print(f"\n奖池设置: {j['current_value']}（{j['validation_status']}）")
