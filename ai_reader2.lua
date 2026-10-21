-- ai_reader2.lua - 超级监控脚本：多态感知 + 自动防卡死快照
-- 用法: mame sdmg2 -autoboot_script ai_reader2.lua

local state_path = "/tmp/sdmg2_state.json"
local SNAP_PATH = "/tmp/phase_snap_auto.bin"
local HAND_ADDR = 0x1F043F
local BET_ADDR = 0x1F0BB5
local CREDIT_ADDR = 0x1F09FD
-- Phase flag候选
local PHASE_CANDIDATES = {0x1F03CE, 0x1F03E6, 0x1F03E9}

local snap_done = false

local function safe_read(space, addr)
local ok, v = pcall(function() return space:read_u8(addr) end)
return ok and v or 0
end

local function has_tiles(space)
for i = 0, 13 do
local v = safe_read(space, HAND_ADDR + i)
if v ~= 0 and v ~= 0xFF then return true end
end
return false
end

local function do_snapshot(space)
print("检测到结算，dump 0x1F0300-0x1F0600...")
local f = io.open(SNAP_PATH, "wb")
if f then
for addr = 0x1F0300, 0x1F0600 do
f:write(string.char(safe_read(space, addr)))
end
f:close()
print("已保存: ".. SNAP_PATH)
end
end

local function write_state()
local cpu = manager.machine.devices[":maincpu"]
if not cpu or not cpu.spaces or not cpu.spaces["program"] then return end
local space = cpu.spaces["program"]

-- 1. 常规感知：手牌/BET/CREDIT/Phase
local hand = {}
for i = 0, 13 do
hand[#hand+1] = safe_read(space, HAND_ADDR + i)
end

local bet = safe_read(space, BET_ADDR)
local credit = safe_read(space, CREDIT_ADDR)

local phases = {}
for _, addr in ipairs(PHASE_CANDIDATES) do
phases[#phases+1] = string.format('"0x%X":%d', addr, safe_read(space, addr))
end

local f = io.open(state_path, "w")
if f then
f:write(string.format(
'{"hand":[%s],"bet":%d,"credit":%d,"phase":{%s}}',
table.concat(hand, ","),
bet, credit,
table.concat(phases, ",")
))
f:close()
end

-- 2. 结算监测：BET=0且有手牌 → 自动快照（只一次）
if not snap_done and bet == 0 and has_tiles(space) then
do_snapshot(space)
snap_done = true
end
end

emu.register_periodic(write_state, 0.5)
print("AI Reader2终极版启动: 感知+Phase监控+自动快照")
