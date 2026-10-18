-- dump_devices.lua - 转储MAME设备和内存空间信息
local log = "/tmp/mame_devices.log"
emu.register_periodic(function()
    emu.register_periodic(function() end, 999999)
    local f = io.open(log, "w")
    if not f then return end
    f:write("=== 设备列表 ===\n")
    for name, dev in pairs(manager.machine.devices) do
        f:write(string.format("设备: %s (%s)\n", name, dev.shortname or "?"))
        if dev.spaces then
            for sname, space in pairs(dev.spaces) do
                f:write(string.format("  空间: %s\n", sname))
            end
        end
    end
    f:write("=== 完成 ===\n")
    f:close()
    print("设备信息已写入 " .. log)
end, 3.0)
print("Device dumper loaded...")
