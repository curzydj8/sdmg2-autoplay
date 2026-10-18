-- memory_scanner.lua (draft 2026-10-18, 未在实机验证)
-- 用途: 找出 sdmg2 的 CREDIT / BET / 手牌等在工作RAM中的地址
--
-- 事实依据(已核实):
--   1) 本地 MAME 源码 mame-wasm/mame2010/src/mame/drivers/igs017.c 的
--      sdmg2 address map: AM_RANGE(0x1f0000, 0x1fffff) AM_RAM  -> 工作RAM 64KB
--   2) CPU = M68000, tag "maincpu" (MACHINE_DRIVER_START(sdmg2))
--   3) Lua 读内存 API (MAME官方文档 docs.mamedev.org/luascript/ref-mem.html):
--      manager.machine.devices[":maincpu"].spaces["program"]:read_u8(addr)
--      manager.machine.devices[":maincpu"].spaces["program"]:read_u16(addr)
--      68000 大端, read_u16 按CPU视角组装, 无需手动拼字节
--
-- 命令文件 /tmp/memscan_cmd.json (单条, 执行后清空):
--   {"cmd":"snapshot","tag":"c_before"}
--       -> 把 0x1f0000-0x1fffff 原样存 /tmp/memscan_c_before.bin, 日志记大小
--   {"cmd":"find","value":1855,"width":16}
--       -> 在当前RAM里找所有等于该值的地址:
--          u8 / u16(大端) / BCD压缩(0x18,0x55 这种), 候选上限200个记 /tmp/memscan.log
--   {"cmd":"diff","a":"c_before","b":"c_after"}
--       -> 对比两次快照, 列出变化的字节地址及 u16 前后值, 上限300行
--
-- 推荐工作流 (CREDIT 地址):
--   1. 屏幕确认当前 CREDIT (如 1855)
--   2. snapshot "c_before" -> 经 ai_bridge 按一次 COIN (CREDIT+1) -> snapshot "c_after"
--   3. diff -> 找 1855->1856 (u16) 的地址; 重复一次确认稳定
-- 注意: 每次改程序后必须重启 MAME 再测 (发布纪律)

local RAM_START = 0x1f0000
local RAM_END   = 0x1fffff
local RAM_LEN   = RAM_END - RAM_START + 1  -- 65536

local cmd_path = "/tmp/memscan_cmd.json"
local log_path = "/tmp/memscan.log"
local MAX_HITS = 200

local function log(msg)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. msg .. "\n"); f:close() end
end

-- 取 program space
local space = nil
do
    local ok, cpu = pcall(function() return manager.machine.devices[":maincpu"] end)
    if ok and cpu then
        local ok2, sp = pcall(function() return cpu.spaces["program"] end)
        if ok2 then space = sp end
    end
end

if not space then
    log("FATAL: 找不到 :maincpu 的 program space, scanner 未启动")
else
    log(string.format("memory_scanner 就绪: 扫描 0x%X-0x%X (%dKB)",
        RAM_START, RAM_END, RAM_LEN / 1024))
end

local function snap_path(tag) return "/tmp/memscan_" .. tag .. ".bin" end

local function do_snapshot(tag)
    local t = {}
    for a = RAM_START, RAM_END do
        local ok, b = pcall(function() return space:read_u8(a) end)
        t[#t + 1] = string.char(ok and b or 0)
    end
    local data = table.concat(t)
    local f = io.open(snap_path(tag), "wb")
    if not f then log("snapshot 失败: 写文件 " .. snap_path(tag)); return end
    f:write(data); f:close()
    log(string.format("snapshot '%s' 完成: %d 字节 -> %s", tag, #data, snap_path(tag)))
end

-- 十进制转 BCD 字节序列, 如 1855 -> {0x18, 0x55}
local function to_bcd_bytes(v)
    local s = tostring(v)
    if #s % 2 == 1 then s = "0" .. s end
    local out = {}
    for i = 1, #s, 2 do
        local hi = tonumber(s:sub(i, i)); local lo = tonumber(s:sub(i + 1, i + 1))
        out[#out + 1] = hi * 16 + lo
    end
    return out
end

local function do_find(value, width)
    width = width or 16
    local bcd = to_bcd_bytes(value)
    local hits, n = {}, 0
    local function hit(fmt, ...)
        if n >= MAX_HITS then return end
        n = n + 1
        hits[#hits + 1] = string.format(fmt, ...)
    end
    for a = RAM_START, RAM_END do
        local ok, b = pcall(function() return space:read_u8(a) end)
        if ok then
            if width == 8 and b == value then
                hit("u8  0x%06X = %d", a, value)
            end
            -- u16 大端: 只在偶地址读, 避免重复
            if width == 16 and a % 2 == 0 and a + 1 <= RAM_END then
                local ok2, w = pcall(function() return space:read_u16(a) end)
                if ok2 and w == value then
                    hit("u16 0x%06X = %d (bytes %02X %02X)", a, value,
                        math.floor(w / 256), w % 256)
                end
            end
            -- BCD: 首字节匹配再验后续
            if b == bcd[1] and a + #bcd - 1 <= RAM_END then
                local match = true
                for i = 2, #bcd do
                    local ok3, bb = pcall(function() return space:read_u8(a + i - 1) end)
                    if not ok3 or bb ~= bcd[i] then match = false; break end
                end
                if match then
                    hit("bcd 0x%06X = %d (%d字节)", a, value, #bcd)
                end
            end
        end
        if n >= MAX_HITS then break end
    end
    log(string.format("find value=%d width=%d: %d 个候选%s", value, width, n,
        n >= MAX_HITS and " (已截断)" or ""))
    for _, h in ipairs(hits) do log("  " .. h) end
    if n == 0 then log("  无候选: 值可能以其他编码存放, 或不在工作RAM") end
end

local function do_diff(tag_a, tag_b)
    local function load(tag)
        local f = io.open(snap_path(tag), "rb")
        if not f then return nil end
        local d = f:read("*all"); f:close()
        return d
    end
    local da, db = load(tag_a), load(tag_b)
    if not da or not db then
        log("diff 失败: 快照缺失"); return
    end
    if #da ~= #db then
        log(string.format("diff 失败: 快照长度不一致 %d vs %d", #da, #db)); return
    end
    local n = 0
    log(string.format("diff '%s' -> '%s':", tag_a, tag_b))
    for i = 1, #da do
        local ba, bb = da:byte(i), db:byte(i)
        if ba ~= bb then
            local addr = RAM_START + i - 1
            -- 偶地址时给出 u16 前后值
            local extra = ""
            if addr % 2 == 0 and i + 1 <= #da then
                local wa = da:byte(i) * 256 + da:byte(i + 1)
                local wb = db:byte(i) * 256 + db:byte(i + 1)
                extra = string.format(" u16 %d->%d", wa, wb)
            end
            n = n + 1
            if n <= 300 then
                log(string.format("  0x%06X: %02X->%02X%s", addr, ba, bb, extra))
            end
        end
    end
    log(string.format("diff 完成: %d 字节变化%s", n, n > 300 and " (仅列前300)" or ""))
end

local function read_cmd()
    local f = io.open(cmd_path, "r")
    if not f then return nil end
    local content = f:read("*all"); f:close()
    local cf = io.open(cmd_path, "w")
    if cf then cf:write("{}"); cf:close() end
    local cmd = string.match(content, '"cmd"%s*:%s*"(%w+)"')
    if not cmd then return nil end
    local tag = string.match(content, '"tag"%s*:%s*"([%w_%-]+)"')
    local a = string.match(content, '"a"%s*:%s*"([%w_%-]+)"')
    local b = string.match(content, '"b"%s*:%s*"([%w_%-]+)"')
    local value = tonumber(string.match(content, '"value"%s*:%s*(%d+)') or "")
    local width = tonumber(string.match(content, '"width"%s*:%s*(%d+)') or "") or 16
    return { cmd = cmd, tag = tag, a = a, b = b, value = value, width = width }
end

if space then
    emu.register_periodic(function()
        local c = read_cmd()
        if not c then return end
        if c.cmd == "snapshot" and c.tag then
            do_snapshot(c.tag)
        elseif c.cmd == "find" and c.value then
            do_find(c.value, c.width)
        elseif c.cmd == "diff" and c.a and c.b then
            do_diff(c.a, c.b)
        else
            log("未知命令或缺参数: " .. tostring(c.cmd))
        end
    end, 0.5)
    log("AI memory_scanner loaded (命令: /tmp/memscan_cmd.json)")
    print("AI memory_scanner loaded")
end
