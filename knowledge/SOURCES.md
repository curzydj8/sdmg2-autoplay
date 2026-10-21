# 资料来源记录

## A. 超级大满贯Ⅱ 专属资料

### A1. Arcade Museum - sdmg2
- URL: https://www.arcade-museum.com/tech-center/machine/sdmg2
- 内容：Chaoji Da Manguan II (China, V765C)，MAME ID sdmg2
- 驱动：igs/igs017.cpp，1997年，IGS出品
- 类别：Tabletop / Mahjong
- 控制器：mahjong(25键) / gambling(5键) / joy(8向2键)
- MAME状态：good
- 访问日期：2026-10-15

### A2. MAME驱动源码
- 文件：src/mame/igs/igs017.cpp:3858
- 内容：DIP DSW2 mask 0x40 = Controls
- 状态：源码证据

### A3. 真机实测（本项目）
- 路径：~/workspace/sdmg2-test/screenshots/ (125+张)
- 状态：直接证据

## B. 通用麻将规则（仅背景参考，不得直接套用）

### B1. Riichi Wiki
- URL: https://riichi.wiki/index.php?title=Japanese_mahjong
- 内容：4面子+1雀头、需要役
- 警告：通用规则，未验证是否适用于本游戏

### A4. GamesDatabase - sdmg2
- URL: https://www.gamesdatabase.org/mame-rom/sdmg2
- 访问日期：2026-10-15
- 关键发现：
  - 已知Bug："sdmg2 crashes when pressing C button" (ID 03543)
  - ⚠️ 避免按C键！
  - Controls DIP：Keyboard(默认) vs Joystick（注意：sdmg2754ca显示为Mahjong）
  - Min Bet选项：500/1000/1500/2000（sdmg2版本；sdmg2754ca显示为1）
  - Coinage：1/1, 1/2, 1/3, 1/5
  - 版本差异：sdmg2 ≠ sdmg2754ca，DIP选项不同
