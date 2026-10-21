-- auto_snap.lua - 自动捕获结算快照
-- 监控BET/手牌状态，进入结算时自动dump内存
-- 用法: -autoboot_script auto_snap.lua (可与ai_reader2.lua合并使用)

local SNAP_PATH = "/tmp/phase_snap_auto.bin"
local snap_done = false

local HAND_ADDR = 0x1F043F
local BET_ADDR = 0x1F0BB5

local function safe_read(addr)
local cpu = manager.machine.devices[":maincpu"]
if not cpu or not cpu.spaces or not cpu.spaces["program"] then return 0 end
local ok, v = pcall(function() return cpu.spaces["program"]:read_u8(addr) end)
return ok and v or 0
end

local function has_tiles()
for i = 0, 13 do
local v = safe_read(HAND_ADDR + i)
if v ~= 0 and v ~= 0xFF then return true end
end
return false
end

emu.register_periodic(function()
if snap_done then return end

local bet = safe_read(BET_ADDR)

-- 触发条件：BET=0但手牌非空（结算画面）
-- 注意：正常ODDS画面手牌为全0，不会误触发
if bet == 0 and has_tiles() then
print("检测到结算，正在dump 0x1F0300-0x1F0600...")
local f = io.open(SNAP_PATH, "wb")
if f then
for addr = 0x1F0300, 0x1F0600 do
f:write(string.char(safe_read(addr)))
end
f:close()
print("已保存: ".. SNAP_PATH)
end
snap_done = true
end
end, 1.0)

print("自动快照脚本已加载：BET=0+有手牌时触发")
