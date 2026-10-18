-- value_searcher.lua - 搜索特定值的内存地址
-- 用法：修改 TARGET_VALUE 为要找的值，跑两次（值变化前后），取交集

local log_path = "/tmp/mame_value_search.log"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. m .. "\n"); f:close() end
    print(m)
end

-- 要搜索的值（u16），比如 CREDIT=1855 就填 1855
local TARGET_VALUE = 1855
-- 搜索范围：先扫 0x000000-0xFFFFFF (16MB) 太慢，分段
-- IGS PGM 68000 RAM 可能在 0x800000-0x8FFFFF，先试这个
local SCAN_START = 0x800000
local SCAN_END = 0x8FFFFF

local done = false

emu.register_periodic(function()
    if done then return end
    done = true

    log(string.format("搜索 u16 值 %d，范围 0x%06X-0x%06X", TARGET_VALUE, SCAN_START, SCAN_END))

    local cpu = manager.machine.devices[":maincpu"]
    if not cpu or not cpu.spaces or not cpu.spaces["program"] then
        log("ERROR: 找不到 program 空间")
        return
    end
    local space = cpu.spaces["program"]

    local found = {}
    local addr = SCAN_START
    local checked = 0
    while addr <= SCAN_END do
        local ok, v = pcall(function() return space:read_u16(addr) end)
        if ok and v == TARGET_VALUE then
            table.insert(found, string.format("0x%06X", addr))
            if #found >= 50 then
                log("找到50个，停止（太多）")
                break
            end
        end
        addr = addr + 2
        checked = checked + 1
        if checked % 100000 == 0 then
            log(string.format("已检查 %d 个地址...", checked))
        end
    end

    log(string.format("搜索完成，共找到 %d 个地址值为 %d:", #found, TARGET_VALUE))
    for _, a in ipairs(found) do
        log("  " .. a)
    end
    log("=== 完成 ===")
end, 5.0)

log("值搜索器启动")
