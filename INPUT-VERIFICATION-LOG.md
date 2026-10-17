
## 2026-10-14 22:48 - 下注键确认

**发现**：P1 Button 1（左 Ctrl）= 下注/开始键
- 用户物理键盘左 Ctrl 可下注
- xdotool 发送 `ctrl` 后游戏直接开始
- 与驱动注释的 IPT_BUTTON2 不符，实际为 BUTTON1

**输入链路状态**：
- ✅ "5"（投币）：可用，但丢键率高
- ✅ "Tab"（菜单）：可用
- ✅ 方向键（导航）：可用
- ✅ "1"（开始）：可用
- ✅ "ctrl"（下注/开始）：可用
- ❌ "Return"/"KP_Enter"/"space"（菜单选择）：xdotool 无效
- ❌ "Alt_L"（Button2）：无效
- ❌ "F3"（复位）：无效（误触暂停）

**DIP**：Controls=Joystick（用户手动切换，配置文件未生效）
