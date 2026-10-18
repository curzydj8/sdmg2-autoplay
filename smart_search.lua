-- smart_search.lua - 智能搜索CREDIT
-- 策略：找所有值为合理CREDIT范围(0-5000)的u16，然后监控哪个会随投币变化
local log_path = "/tmp/mame_smart.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. m .. "\n"); f:close() end
end

local candidates = {}
local stage = 0
local space = nil

local function get_space()
    -- IGS PGM用68000
    for _, name in ipairs({":maincpu"}) do
        local ok, dev = pcall(function() return manager.machine.devices[name] end)
        if ok and dev and dev.spaces and dev.spaces["program"] then
            return dev.spaces["program"]
        end
    end
    return nil
end

local function press_coin()
    local ports = manager.machine.ioport.ports
    if not ports then return end
    local port = ports[":COINS"]
    if not port or not port.fields then return end
    for _, field in pairs(port.fields) do
        local ok, name = pcall(function() return field.name end)
        if ok and name == "Coin 1" then
            pcall(function() field:set_value(1) end)
            local t0 = os.clock()
            while os.clock() - t0 < 0.15 do end
            pcall(function() field:set_value(0) end)
            return
        end
    end
end

emu.register_periodic(function()
    stage = stage + 1
    
    if stage == 1 then
        space = get_space()
        if not space then log("无program空间"); return end
        log("阶段1: 收集候选 (值0-5000的u16)...")
        for addr = 0, 0xFFFF, 2 do
            local ok, v = pcall(function() return space:read_u16(addr) end)
            if ok and v >= 0 and v <= 5000 then
                -- 排除明显是代码的区域（只记录RAM可疑区）
                table.insert(candidates, {addr=addr, v0=v})
                if #candidates >= 200 then break end
            end
        end
        log(string.format("候选数: %d", #candidates))
        
    elseif stage == 2 then
        log("阶段2: 投币2次...")
        press_coin()
        
    elseif stage == 3 then
        log("阶段3: 检查变化...")
        local changed = {}
        for _, c in ipairs(candidates) do
            local ok, v = pcall(function() return space:read_u16(c.addr) end)
            if ok and v ~= c.v0 then
                table.insert(changed, string.format("0x%04X: %d->%d", c.addr, c.v0, v))
            end
        end
        log(string.format("变化数: %d", #changed))
        for _, s in ipairs(changed) do log("  " .. s) end
        log("=== 完成 ===")
        emu.register_periodic(function() end, 999999)
    end
end, 4.0)

log("智能搜索启动")
