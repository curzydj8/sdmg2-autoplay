-- scan_memory.lua - 自动扫描CREDIT内存地址
-- 用法: mame sdmg2 -autoboot_script scan_memory.lua
-- 会在 /tmp/mame_scan.log 输出候选地址

local scan_log = "/tmp/mame_scan.log"

local function get_space()
    local ok, cpu = pcall(function() return manager.machine.devices[":maincpu"] end)
    if not ok or not cpu then return nil end
    local ok2, space = pcall(function() return cpu.spaces["program"] end)
    if not ok2 then return nil end
    return space
end

-- 延迟5秒等游戏启动，然后扫描
emu.register_periodic(function()
    local space = get_space()
    if not space then return end
    
    -- 只扫描一次
    emu.register_periodic(function() end, 999999)  -- 取消自己
    
    local f = io.open(scan_log, "w")
    if not f then return end
    
    f:write("=== 内存扫描开始 ===\n")
    
    -- 尝试读取几个已知地址范围，找CREDIT
    -- CREDIT当前约1835，搜索这个值
    local target = 1835
    local found = {}
    for addr = 0x0, 0x1FFFF, 1 do
        local ok, val = pcall(function() return space:read_u8(addr) end)
        if ok then
            -- 检查u16 (小端)
            local ok2, val16 = pcall(function() return space:read_u16(addr) end)
            if ok2 and val16 == target then
                table.insert(found, string.format("u16@0x%05X", addr))
                if #found >= 30 then break end
            end
        end
    end
    
    f:write(string.format("CREDIT=%d 候选地址 (%d个):\n", target, #found))
    for _, a in ipairs(found) do
        f:write("  " .. a .. "\n")
    end
    f:write("=== 扫描结束 ===\n")
    f:close()
    print(string.format("扫描完成，找到 %d 个候选", #found))
end, 5.0)  -- 5秒后执行一次

print("Memory scanner loaded, will scan in 5 seconds...")
