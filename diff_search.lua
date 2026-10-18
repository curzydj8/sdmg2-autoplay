-- diff_search.lua v2 - 差分法找CREDIT，内置COIN触发
local log_path = "/tmp/mame_diff.log"

local function log(msg)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. msg .. "\n"); f:close() end
    print(msg)
end

local function get_main_space()
    for _, name in ipairs({":maincpu", ":m68000", ":mcpu", ":main"}) do
        local ok, dev = pcall(function() return manager.machine.devices[name] end)
        if ok and dev and dev.spaces and dev.spaces["program"] then
            return dev.spaces["program"], name
        end
    end
    -- 遍历所有设备找program空间
    for dname, dev in pairs(manager.machine.devices) do
        if dev.spaces and dev.spaces["program"] then
            return dev.spaces["program"], dname
        end
    end
    return nil, nil
end

local function press_coin()
    local ports = manager.machine.ioport.ports
    if not ports then return false end
    local port = ports[":COINS"]
    if not port or not port.fields then return false end
    for _, field in pairs(port.fields) do
        local ok, name = pcall(function() return field.name end)
        if ok and name == "Coin 1" then
            pcall(function() field:set_value(1) end)
            local t0 = os.clock()
            while os.clock() - t0 < 0.1 do end
            pcall(function() field:set_value(0) end)
            return true
        end
    end
    return false
end

local dump1 = {}
local stage = 0
local space = nil
local cpu_name = nil

emu.register_periodic(function()
    stage = stage + 1
    
    if stage == 1 then
        space, cpu_name = get_main_space()
        if not space then
            log("找不到主CPU program空间")
            return
        end
        log("CPU: " .. cpu_name .. "，开始dump...")
        for addr = 0, 0xFFFF do
            local ok, v = pcall(function() return space:read_u8(addr) end)
            if ok then dump1[addr] = v end
        end
        log("dump完成，准备投币")
        
    elseif stage == 2 then
        log("投币...")
        press_coin()
        log("投币完成")
        
    elseif stage == 3 then
        log("对比...")
        local changed = {}
        for addr = 0, 0xFFFF do
            local ok, v = pcall(function() return space:read_u8(addr) end)
            if ok and dump1[addr] ~= nil and v ~= dump1[addr] then
                table.insert(changed, {addr=addr, old=dump1[addr], new=v})
                if #changed >= 50 then break end
            end
        end
        log(string.format("共 %d 处变化:", #changed))
        for _, c in ipairs(changed) do
            log(string.format("  0x%04X: %d -> %d", c.addr, c.old, c.new))
        end
        log("=== 完成 ===")
        emu.register_periodic(function() end, 999999)
    end
end, 4.0)

log("差分搜索v2启动")
