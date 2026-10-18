-- dump_fields.lua - 列出KEY1所有字段名
local log_path = "/tmp/mame_fields.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(m .. "\n"); f:close() end
end

emu.register_periodic(function()
    emu.register_periodic(function() end, 999999)
    local ports = manager.machine.ioport.ports
    if not ports then log("无ports"); return end
    for _, pname in ipairs({":KEY1", ":KEY0", ":COINS"}) do
        local port = ports[pname]
        if port and port.fields then
            log("端口 " .. pname .. ":")
            for _, field in pairs(port.fields) do
                local ok, name = pcall(function() return field.name end)
                if ok then log("  - " .. tostring(name)) end
            end
        else
            log("端口 " .. pname .. " 无fields")
        end
    end
    log("=== 完成 ===")
end, 2.0)
log("字段dump启动")
