-- bet_scanner.lua - BET地址差分扫描
-- 用法: 在MAME中按F12触发一次快照，或直接autoboot运行后手动scp
-- 会dump 0x1F0000-0x1FFFFF 到 /tmp/bet_snap_N.bin

local snap_count = 0

local function dump_ram()
    snap_count = snap_count + 1
    local path = string.format("/tmp/bet_snap_%d.bin", snap_count)
    local space = manager.machine.devices[":maincpu"].spaces["program"]
    local f = io.open(path, "wb")
    if not f then
        print("无法写入 " .. path)
        return
    end
    for addr = 0x1F0000, 0x1FFFFF do
        local ok, v = pcall(function() return space:read_u8(addr) end)
        f:write(string.char(ok and v or 0))
    end
    f:close()
    print(string.format("快照 %d 已保存: %s (共64KB)", snap_count, path))
end

-- 注册F12为快照键
emu.register_frame_done(function()
end)

-- 每10秒自动dump一次（方便对比）
local frame = 0
emu.register_frame_done(function()
    frame = frame + 1
    -- 600帧约10秒
    if frame % 600 == 0 then
        dump_ram()
    end
end)

print("BET扫描器已加载：每10秒自动dump一次到 /tmp/bet_snap_N.bin")
print("操作：在BET=0时等一次dump，押注到BET=5后再等一次，然后diff")
