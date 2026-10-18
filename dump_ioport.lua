-- dump_ioport.lua - 转储MAME输入端口结构
local log = "/tmp/mame_ioport.log"
emu.register_periodic(function()
    emu.register_periodic(function() end, 999999)
    local f = io.open(log, "w")
    if not f then return end
    f:write("=== IOPORT结构 ===\n")
    if manager.machine.ioport and manager.machine.ioport.ports then
        for pname, port in pairs(manager.machine.ioport.ports) do
            f:write(string.format("端口: %s\n", pname))
            if port.fields then
                for fname, field in pairs(port.fields) do
                    local name = "?"
                    pcall(function() name = field.name or "?" end)
                    f:write(string.format("  字段: %s (%s)\n", fname, name))
                end
            end
        end
    else
        f:write("无ioport数据\n")
    end
    f:write("=== 完成 ===\n")
    f:close()
    print("ioport已转储")
end, 3.0)
print("ioport dumper loaded")
