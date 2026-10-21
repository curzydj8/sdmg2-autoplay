-- ai_reader.lua - 感知层Lua桥接
-- 每0.5秒把手牌/BET/CREDIT写入 /tmp/sdmg2_state.json
-- MAME启动: -autoboot_script ai_reader.lua

local state_path = "/tmp/sdmg2_state.json"
local HAND_ADDR = 0x1F043F
local BET_ADDR = 0x1F0BB5
local CREDIT_ADDR = 0x1F09FD

local function write_state()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu or not cpu.spaces or not cpu.spaces["program"] then return end
    local space = cpu.spaces["program"]
    
    -- 读14张手牌
    local hand = {}
    for i = 0, 13 do
        local ok, v = pcall(function() return space:read_u8(HAND_ADDR + i) end)
        hand[#hand+1] = ok and v or 0
    end
    
    -- 读BET/CREDIT
    local ok1, bet = pcall(function() return space:read_u8(BET_ADDR) end)
    local ok2, credit = pcall(function() return space:read_u8(CREDIT_ADDR) end)
    
    -- 写JSON
    local f = io.open(state_path, "w")
    if f then
        f:write(string.format(
            '{"hand":[%s],"bet":%d,"credit":%d}',
            table.concat(hand, ","),
            ok1 and bet or 0,
            ok2 and credit or 0
        ))
        f:close()
    end
end

emu.register_periodic(write_state, 0.5)
print("AI Reader桥接启动: 手牌0x1F043F, BET 0x1F0BB5, CREDIT 0x1F09FD")
