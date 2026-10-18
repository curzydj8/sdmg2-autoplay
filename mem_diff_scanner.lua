-- mem_diff_scanner.lua - 差分内存扫描找CREDIT/BET
-- 原理：基线扫描 -> 执行动作 -> 二次扫描 -> 找按预期变化的地址
-- 用法：MAME启动后，脚本自动跑三阶段

local log_path = "/tmp/mame_memdiff.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. m .. "\n"); f:close() end
    print(m)
end

local function get_space()
    local cpu = manager.machine.devices[":maincpu"]
    if cpu and cpu.spaces and cpu.spaces["program"] then
        return cpu.spaces["program"]
    end
    return nil
end

local function press_ioport(port_name, field_name, hold_ms)
    local ports = manager.machine.ioport.ports
    if not ports then return false end
    local port = ports[port_name]
    if not port or not port.fields then return false end
    for _, field in pairs(port.fields) do
        local ok, name = pcall(function() return field.name end)
        if ok and name == field_name then
            pcall(function() field:set_value(1) end)
            local t0 = os.clock()
            while os.clock() - t0 < (hold_ms or 100)/1000 do end
            pcall(function() field:set_value(0) end)
            return true
        end
    end
    return false
end

-- 扫描内存，返回 {addr: value} 表
-- 只扫可能是RAM的区域，跳过明显是ROM的（通过可写性判断太慢，直接全扫由差分过滤）
local function scan_memory(space, start_addr, end_addr)
    local result = {}
    local addr = start_addr
    while addr <= end_addr do
        local ok, v = pcall(function() return space:read_u8(addr) end)
        if ok then
            result[addr] = v
        end
        addr = addr + 1
        -- 每64K让出一下，避免卡死
        if addr % 0x10000 == 0 then
            -- Lua没有yield，用空循环让MAME调度
            local t0 = os.clock()
            while os.clock() - t0 < 0.01 do end
        end
    end
    return result
end

local function scan_memory_u16(space, start_addr, end_addr)
    local result = {}
    local addr = start_addr
    while addr <= end_addr do
        local ok, v = pcall(function() return space:read_u16(addr) end)
        if ok then
            result[addr] = v
        end
        addr = addr + 2
    end
    return result
end

local stage = 0
local space = nil
local baseline_u8 = nil
local baseline_u16 = nil
local done = false

-- 扫描范围：68000的典型RAM区，先扫 0x000000-0xFFFFFF 太慢，分段
-- IGS PGM: 主RAM通常在 0x800000+ 或 0x100000+，先扫 0x00000-0xFFFFF (1MB)
local SCAN_START = 0x00000
local SCAN_END = 0xFFFFF

emu.register_periodic(function()
    if done then return end
    stage = stage + 1
    log(string.format("=== 阶段 %d ===", stage))

    if stage == 1 then
        space = get_space()
        if not space then
            log("ERROR: 找不到 :maincpu program空间")
            return
        end
        log("开始基线扫描 (u8) 0x00000-0xFFFFF...")
        baseline_u8 = scan_memory(space, SCAN_START, SCAN_END)
        local count = 0
        for _ in pairs(baseline_u8) do count = count + 1 end
        log(string.format("基线u8完成，共 %d 个地址", count))
        log("开始基线扫描 (u16)...")
        baseline_u16 = scan_memory_u16(space, SCAN_START, SCAN_END)
        count = 0
        for _ in pairs(baseline_u16) do count = count + 1 end
        log(string.format("基线u16完成，共 %d 个地址", count))
        log("等待5秒后按 COIN (CREDIT+1)...")

    elseif stage == 2 then
        log("执行 COIN...")
        local ok = press_ioport(":COINS", "Coin 1", 150)
        log("COIN " .. (ok and "已发送" or "失败"))
        log("等待3秒让游戏处理...")

    elseif stage == 3 then
        log("二次扫描 (u8)...")
        local after_u8 = scan_memory(space, SCAN_START, SCAN_END)
        log("二次扫描 (u16)...")
        local after_u16 = scan_memory_u16(space, SCAN_START, SCAN_END)

        -- 找 u8 +1 的地址 (CREDIT+1)
        log("--- u8 变化 +1 的候选 (CREDIT候选) ---")
        local candidates_u8 = {}
        for addr, v0 in pairs(baseline_u8) do
            local v1 = after_u8[addr]
            if v1 and v1 == v0 + 1 then
                table.insert(candidates_u8, string.format("0x%05X: %d->%d", addr, v0, v1))
                if #candidates_u8 >= 30 then break end
            end
        end
        log(string.format("找到 %d 个", #candidates_u8))
        for _, c in ipairs(candidates_u8) do log("  " .. c) end

        -- 找 u16 +1 的地址
        log("--- u16 变化 +1 的候选 ---")
        local candidates_u16 = {}
        for addr, v0 in pairs(baseline_u16) do
            local v1 = after_u16[addr]
            if v1 and v1 == v0 + 1 then
                table.insert(candidates_u16, string.format("0x%05X: %d->%d", addr, v0, v1))
                if #candidates_u16 >= 30 then break end
            end
        end
        log(string.format("找到 %d 个", #candidates_u16))
        for _, c in ipairs(candidates_u16) do log("  " .. c) end

        -- 找所有变化的地址（用于观察）
        local total_changed = 0
        for addr, v0 in pairs(baseline_u8) do
            if after_u8[addr] and after_u8[addr] ~= v0 then
                total_changed = total_changed + 1
            end
        end
        log(string.format("总变化地址数 (u8): %d", total_changed))
        log("=== 第一轮完成 ===")
        log("提示：如需第二轮确认，修改脚本用候选地址做窄范围重扫")

        -- 停止
        done = true
    end
end, 8.0)

log("差分扫描器启动，范围 0x00000-0xFFFFF")
