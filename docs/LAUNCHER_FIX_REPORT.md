# 启动器修复报告

**日期**：2026-10-17

## 原始错误

```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**位置**：`tools/ai_launcher.py:17`，`tk.Tk()`初始化时

## 根因

1. `.desktop`文件未设置DISPLAY环境变量
2. 通过SSH无显示环境测试时复现

## 修复

### tools/sdmg2-ai.desktop
- `Exec`改为：`env DISPLAY=:0 python3 ...`
- 增加`Path=/home/zhangdawei/sdmg2-test`

### tools/ai_launcher.py v2.0
- 启动时检查并设置`DISPLAY=:0`
- 增加8项状态显示：本地AI/MAME/阶段/数据库/Gemma/策略/对局/分数
- 增加7个操作按钮：检查环境/测试数据库/测试Gemma/检查MAME/运行/停止/日志
- 数据库连接超时5秒，Gemma超时5秒，不冻结界面
- 启动前安全检查：单实例锁+数据库可用性
- Gemma不可用时降级提示，不阻塞

## 测试

- `DISPLAY=:0 timeout 8 python3 tools/ai_launcher.py`：无报错运行
- 已同步到服务器桌面

## 待完善

- 游戏阶段识别（待接入screen_db）
- 信用分/目标分数实时显示（待接入）
- 本地AI一键启动（待接入controller）
