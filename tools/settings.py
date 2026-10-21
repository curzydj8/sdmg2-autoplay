#!/usr/bin/env python3
"""游戏设置程序 settings.py - 更新 config 表"""
import os
import sqlite3
_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_base, "data", "sdmg2.db")
def get(key, default=None):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default
def set_val(key, value):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, datetime('now'))", (key, str(value)))
    conn.commit()
    conn.close()
    print(f"已设置 {key} = {value}")
def show():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    rows = conn.execute("SELECT key, value FROM config ORDER BY key").fetchall()
    conn.close()
    print("=== 游戏设置 (config表) ===")
    for k, v in rows:
        print(f"  {k}: {v}")
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--show", action="store_true")
    p.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"))
    a = p.parse_args()
    if a.set:
        set_val(a.set[0], a.set[1])
    else:
        show()
