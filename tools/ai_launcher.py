#!/usr/bin/env python3
"""
本地AI启动器 v2.0
- 显示：AI状态/MAME/阶段/数据库/Gemma/策略/对局/分数
- 操作：检查环境/测试数据库/测试Gemma/检查MAME/运行/停止/日志
"""
import os
import sys
import subprocess
import sqlite3
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json

PROJECT_ROOT = os.path.expanduser("~/sdmg2-test")
DB_PATH = os.path.expanduser("~/workspace/sdmg2-test/data/sdmg2.db")
# 服务器DB路径
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.expanduser("~/sdmg2-test/data/sdmg2.db")
    if not os.path.exists(DB_PATH):
        DB_PATH = "/home/zhangdawei/workspace/sdmg2-test/data/sdmg2.db"


class AILauncher:
    def __init__(self):
        self.ai_proc = None  # 跟踪AI子进程，防止僵尸
        self.root = tk.Tk()
        self.root.title("超级大满贯II - 本地AI v2.0")
        self.root.geometry("500x550")

        tk.Label(self.root, text="超级大满贯II 本地AI",
                 font=("Arial", 16)).pack(pady=10)

        # 状态区
        self.status_vars = {}
        for name in ["本地AI", "MAME", "游戏阶段", "数据库", "Gemma",
                     "策略版本", "对局编号", "信用分/目标"]:
            f = tk.Frame(self.root)
            f.pack(fill="x", padx=20)
            tk.Label(f, text=f"{name}:", width=12, anchor="w").pack(side="left")
            v = tk.Label(f, text="未知", fg="gray")
            v.pack(side="left")
            self.status_vars[name] = v

        # 大启动按钮（一键：MAME+AI）
        self.start_btn = tk.Button(
            self.root, text="▶ 一键启动游戏",
            command=self.start_ai,
            font=("Arial", 14, "bold"),
            bg="#4CAF50", fg="white",
            width=20, height=2)
        self.start_btn.pack(pady=10)

        # 大停止按钮
        self.stop_btn = tk.Button(
            self.root, text="⏹ 停止本地AI",
            command=self.stop_ai,
            font=("Arial", 12, "bold"),
            bg="#f44336", fg="white",
            width=20, height=1)
        self.stop_btn.pack(pady=5)

        # 按钮区
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        for text, cmd in [
            ("检查环境", self.check_env),
            ("启动MAME", self.start_mame),
            ("测试数据库", self.test_db),
            ("测试Gemma", self.test_gemma),
            ("检查MAME", self.check_mame),
            ("查看日志", self.view_log),
        ]:
            tk.Button(btn_frame, text=text, command=cmd,
                      width=12).pack(side="left", padx=2, pady=2)

        self.log_label = tk.Label(self.root, text="日志: ~/sdmg2-test/logs/",
                                  fg="gray", font=("Arial", 8))
        self.log_label.pack(pady=5)

        self.check_env()

    def set_status(self, name, text, color="black"):
        if name in self.status_vars:
            self.status_vars[name].config(text=text, fg=color)

    def check_env(self):
        self.check_mame()
        self.test_db(silent=True)
        self.test_gemma(silent=True)
        # 本地AI状态（检查锁文件）
        if os.path.exists("/tmp/sdmg2_ai.lock"):
            self.set_status("本地AI", "运行中", "green")
        else:
            self.set_status("本地AI", "未运行", "gray")
        self.set_status("策略版本", "v1", "black")
        self.set_status("游戏阶段", "未知（待识别）", "gray")

    def check_mame(self):
        try:
            # 先查带sdmg2参数的，再查纯mame进程
            r = subprocess.run(["pgrep", "-f", "mame"],
                               capture_output=True, text=True, timeout=5)
            pids = r.stdout.strip().split()
            # 排除自己（launcher的python进程不含mame，不用排除）
            if pids:
                self.set_status("MAME", f"运行中 ({len(pids)}进程)", "green")
            else:
                self.set_status("MAME", "未运行", "red")
        except Exception as e:
            self.set_status("MAME", f"检查失败", "red")

    def test_db(self, silent=False):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            v = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            conn.close()
            self.set_status("数据库", f"连接成功 v{v[0]}", "green")
            # 对局编号
            conn = sqlite3.connect(DB_PATH, timeout=5)
            sid = conn.execute(
                "SELECT MAX(id) FROM game_sessions").fetchone()[0]
            conn.close()
            self.set_status("对局编号", str(sid or "无"), "black")
        except Exception as e:
            self.set_status("数据库", "连接失败", "red")
            if not silent:
                messagebox.showerror("数据库", f"连接失败:\n{e}")

    def test_gemma(self, silent=False):
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=5)
            self.set_status("Gemma", "服务正常", "green")
        except Exception as e:
            self.set_status("Gemma", "不可用（降级）", "orange")
            if not silent:
                messagebox.showwarning("Gemma", "Gemma不可用，本地AI将降级运行")

    def start_ai(self):
        """一键启动：MAME → 本地AI → 最小化"""
        # 步骤1：确保MAME运行（窗口模式）
        r = subprocess.run(["pgrep", "-f", "mame"],
                           capture_output=True, text=True, timeout=5)
        if not r.stdout.strip():
            self.set_status("MAME", "启动中...", "orange")
            self.root.update()
            try:
                cmd = "cd ~/mame && /usr/games/mame sdmg2 -rompath ~/mame/roms -window > /tmp/mame.log 2>&1 &"
                subprocess.run(cmd, shell=True, timeout=10)
                import time
                time.sleep(5)  # 等MAME启动
                self.set_status("MAME", "运行中", "green")
            except Exception as e:
                messagebox.showerror("错误", f"MAME启动失败:\n{e}")
                return
        # 步骤2：切到游戏窗口
        self.focus_mame()
        # 步骤3：检查AI单实例
        # 安全检查：锁文件+PID存活
        lock_path = "/tmp/sdmg2_ai.lock"
        if os.path.exists(lock_path):
            try:
                with open(lock_path) as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)  # 检查存活
                messagebox.showwarning("提示", f"本地AI已在运行 (PID {pid})")
                return
            except (ValueError, ProcessLookupError, FileNotFoundError):
                try:
                    os.remove(lock_path)
                except:
                    pass
        # 检查数据库
        try:
            sqlite3.connect(DB_PATH, timeout=5).close()
        except:
            messagebox.showerror("错误", "数据库不可用，无法启动")
            return
        # 创建新对局
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.execute("""
                INSERT INTO game_sessions
                (game_version, rom_id, started_at, config_version, result, target_score, target_verified)
                VALUES ('0.285', 'sdmg2', datetime('now'), 'v1', 'running', 500, 1)
            """)
            sid = cur.lastrowid
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("错误", f"创建对局失败:\n{e}")
            return
        # 启动本地AI子进程（新架构 game_agent.py）
        try:
            # 先把MAME窗口切到前台
            self.focus_mame()
            cmd = [sys.executable,
                   os.path.join(PROJECT_ROOT, "modules", "game_agent.py"),
                   "--session", str(sid)]
            proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True)
            self.ai_proc = proc  # 保存引用用于轮询收尸
            self.set_status("本地AI", f"运行中 (PID {proc.pid})", "green")
            self.set_status("对局编号", str(sid), "black")
            # 最小化启动器，让游戏可见
            self.root.iconify()
            messagebox.showinfo("启动", f"本地AI已启动\n对局: {sid}\n目标: 500")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败:\n{e}")

    def focus_mame(self):
        """把MAME窗口切到前台"""
        try:
            # 用wmctrl或xdotool找MAME窗口
            r = subprocess.run(["wmctrl", "-l"], capture_output=True,
                               text=True, timeout=5)
            for line in r.stdout.splitlines():
                if "mame" in line.lower() or "sdmg2" in line.lower():
                    wid = line.split()[0]
                    subprocess.run(["wmctrl", "-i", "-a", wid], timeout=5)
                    return True
        except:
            pass
        try:
            # 备用：xdotool
            subprocess.run(
                ["xdotool", "search", "--name", "mame", "windowactivate"],
                timeout=5)
        except:
            pass


    def wait_mame_ready(self, timeout=10):
        """等待MAME窗口ready（替代固定sleep，Gemini建议）"""
        import time
        import subprocess
        start = time.time()
        while time.time() - start < timeout:
            try:
                # 查MAME窗口是否已挂载到X server
                r = subprocess.run(
                    ["xdotool", "search", "--name", "mame"],
                    capture_output=True, text=True, timeout=2
                )
                if r.stdout.strip():
                    return True
            except:
                pass
            time.sleep(0.5)
        return False

    def start_mame(self):
        """启动MAME（窗口模式，已验证命令）"""
        # 检查是否已运行
        r = subprocess.run(["pgrep", "-f", "mame"],
                           capture_output=True, text=True, timeout=5)
        if r.stdout.strip():
            messagebox.showinfo("提示", "MAME已在运行")
            return
        # 启动（窗口模式）
        try:
            cmd = "cd ~/mame && /usr/games/mame sdmg2 -rompath ~/mame/roms -window > /tmp/mame.log 2>&1 &"
            subprocess.run(cmd, shell=True, timeout=10)
            import time
            time.sleep(3)
            self.check_mame()
            messagebox.showinfo("启动", "MAME已启动（窗口模式）")
        except Exception as e:
            messagebox.showerror("错误", f"MAME启动失败:\n{e}")

    def stop_ai(self):
        # 优先用保存的proc对象
        if self.ai_proc:
            try:
                self.ai_proc.terminate()  # SIGTERM优雅退出
                try:
                    self.ai_proc.wait(timeout=5)
                except:
                    self.ai_proc.kill()  # 超时强杀
                    self.ai_proc.wait()
                self.ai_proc = None
            except:
                pass
        # 清理锁文件
        lock = "/tmp/sdmg2_ai.lock"
        try:
            if os.path.exists(lock):
                os.remove(lock)
        except:
            pass
        self.set_status("本地AI", "已停止", "gray")

    def view_log(self):
        logdir = os.path.expanduser("~/sdmg2-test/logs")
        os.makedirs(logdir, exist_ok=True)
        os.system(f"xdg-open {logdir} &")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # 启动器单实例锁
    import fcntl
    lock_file = open("/tmp/sdmg2_launcher.lock", "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        print("启动器已在运行")
        sys.exit(1)
    # 确保DISPLAY
    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0"
    AILauncher().run()
