-- hand_snapshot.lua - 手牌内存快照（64KB工作RAM）
-- 命令: echo snapshot > /tmp/hand_cmd.json

local log_path = "/tmp/hand_scan.log"
local cmd_path = "/tmp/hand_cmd.json"
local function log(m)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. m .. "\n"); f:close() end
    print(m)
end

local done = false
local snap_count = 0

-- 工作RAM窗口（来自驱动源码）
local RAM_START = 0x1F0000
local RAM_END = 0x1FFFFF

emu.register_periodic(function()
    if done then return end

    local f = io.open(cmd_path, "r")
    if not f then return end
    local cmd = f:read("*all"):gsub("%s+", "")
    f:close()

    if cmd == "" or cmd == "{}" then return end

    -- 清空命令防重复
    local cf = io.open(cmd_path, "w")
    if cf then cf:write("{}"); cf:close() end

    if cmd:find("snapshot") then
        snap_count = snap_count + 1
        local cpu = manager.machine.devices[":maincpu"]
        if not cpu or not cpu.spaces or not cpu.spaces["program"] then
            log("ERROR: 无program空间")
            return
        end
        local space = cpu.spaces["program"]
        local out_path = string.format("/tmp/hand_snap_%d.bin", snap_count)
        local out = io.open(out_path, "wb")
        if not out then
            log("ERROR: 打不开输出文件")
            return
        end
        log(string.format("快照 #%d: 0x%06X-0x%06X -> %s", snap_count, RAM_START, RAM_END, out_path))
        local addr = RAM_START
        while addr <= RAM_END do
            local ok, v = pcall(function() return space:read_u8(addr) end)
            out:write(string.char(ok and v or 0))
            addr = addr + 1
        end
        out:close()
        log(string.format("快照 #%d 完成 (65536字节)", snap_count))
    elseif cmd:find("stop") then
        done = true
        log("扫描器停止")
    end
end, 0.5)

log("手牌快照器启动，RAM 0x1F0000-0x1FFFFF")
-- 初始化命令文件
local cf = io.open(cmd_path, "w")
if cf then cf:write("{}"); cf:close() end
