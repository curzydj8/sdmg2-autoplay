-- find_via_debugger.lua - 用调试器找内存
local log_path = "/tmp/mame_find.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(m .. "\n"); f:close() end
    print(m)
end

emu.register_periodic(function()
    emu.register_periodic(function() end, 999999)
    
    log("=== 开始查找 ===")
    
    -- 列出所有CPU
    log("CPU设备:")
    for name, dev in pairs(manager.machine.devices) do
        local ok, cputype = pcall(function() return dev.shortname end)
        log(string.format("  %s : %s", name, tostring(cputype)))
    end
    
    -- 尝试主CPU的内存
    local cpu = manager.machine.devices[":maincpu"]
    if cpu then
        log("找到 :maincpu")
        if cpu.spaces then
            for sname, _ in pairs(cpu.spaces) do
                log("  空间: " .. sname)
            end
        end
        -- 尝试读几个地址看是否有效
        local space = cpu.spaces["program"]
        if space then
            for _, addr in ipairs({0x0, 0x100, 0x1000, 0x8000}) do
                local ok, v = pcall(function() return space:read_u8(addr) end)
                log(string.format("  读 0x%X: %s (%s)", addr, tostring(v), ok and "OK" or "FAIL"))
            end
        end
    else
        log("无 :maincpu")
    end
    
    log("=== 完成 ===")
end, 3.0)
log("查找脚本已加载")
