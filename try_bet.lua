-- try_bet.lua - 尝试所有含bet的字段
local log_path = "/tmp/mame_trybet.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. m .. "\n"); f:close() end
end

emu.register_periodic(function()
    emu.register_periodic(function() end, 999999)
    log("开始尝试...")
    local ports = manager.machine.ioport.ports
    if not ports then log("无ports"); return end
    for pname, port in pairs(ports) do
        if port.fields then
            for fname, field in pairs(port.fields) do
                local ok, name = pcall(function() return field.name end)
                if ok and name and string.lower(name):find("bet") then
                    log(string.format("找到: %s / %s", pname, name))
                    -- 尝试按下
                    pcall(function() field:set_value(1) end)
                    local t0 = os.clock()
                    while os.clock() - t0 < 0.1 do end
                    pcall(function() field:set_value(0) end)
                    log("  已尝试按下")
                end
            end
        end
    end
    log("=== 完成 ===")
end, 3.0)
log("try_bet启动")
