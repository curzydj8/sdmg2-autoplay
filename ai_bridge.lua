-- ai_bridge.lua v4 - Lua直控输入 + 状态输出
-- Python写 /tmp/mame_action.json，Lua读并执行
-- 状态写入 /tmp/mame_state.json

local action_path = "/tmp/mame_action.json"
local state_path = "/tmp/mame_state.json"
local log_path = "/tmp/mame_bridge.log"

local function log(msg)
    local f = io.open(log_path, "a")
    if f then f:write(os.date("%H:%M:%S ") .. msg .. "\n"); f:close() end
end

-- 动作名 -> {端口, 字段}
local ACTION_MAP = {
    COIN = {":COINS", "Coin 1"},
    START = {":KEY0", "1 Player Start"},
    BET = {":KEY1", "P1 Mahjong Bet"},
    KAN = {":KEY0", "P1 Mahjong Kan"},
    PON = {":KEY3", "P1 Mahjong Pon"},
    CHI = {":KEY2", "P1 Mahjong Chi"},
    REACH = {":KEY1", "P1 Mahjong Reach"},
    RON = {":KEY2", "P1 Mahjong Ron"},
    DOUBLEUP = {":KEY4", "P1 Mahjong Double Up"},
    BIG = {":KEY4", "P1 Mahjong Big"},
    SMALL = {":KEY4", "P1 Mahjong Small"},
    A = {":KEY0", "P1 Mahjong A"},
    B = {":KEY1", "P1 Mahjong B"},
    C = {":KEY2", "P1 Mahjong C"},
    D = {":KEY3", "P1 Mahjong D"},
    E = {":KEY0", "P1 Mahjong E"},
    F = {":KEY1", "P1 Mahjong F"},
    G = {":KEY2", "P1 Mahjong G"},
    H = {":KEY3", "P1 Mahjong H"},
    I = {":KEY0", "P1 Mahjong I"},
    J = {":KEY1", "P1 Mahjong J"},
    K = {":KEY2", "P1 Mahjong K"},
    L = {":KEY3", "P1 Mahjong L"},
    M = {":KEY0", "P1 Mahjong M"},
    N = {":KEY1", "P1 Mahjong N"},
}

local function find_field(port_name, field_name)
    local ports = manager.machine.ioport.ports
    if not ports then return nil end
    local port = ports[port_name]
    if not port or not port.fields then return nil end
    for fname, field in pairs(port.fields) do
        local ok, name = pcall(function() return field.name end)
        if ok and name == field_name then
            return field
        end
    end
    return nil
end

local function press_action(action)
    local map = ACTION_MAP[action]
    if not map then
        log("未知动作: " .. tostring(action))
        return false
    end
    local field = find_field(map[1], map[2])
    if not field then
        log("找不到字段: " .. map[1] .. "/" .. map[2])
        return false
    end
    -- 按下
    local ok1 = pcall(function() field:set_value(1) end)
    -- 短暂延时（用空循环模拟，约50ms）
    local t0 = os.clock()
    while os.clock() - t0 < 0.05 do end
    -- 释放
    local ok2 = pcall(function() field:set_value(0) end)
    if ok1 and ok2 then
        log("执行: " .. action)
        return true
    else
        log("执行失败: " .. action)
        return false
    end
end

local function read_action()
    local f = io.open(action_path, "r")
    if not f then return nil end
    local content = f:read("*all")
    f:close()
    -- 清空防重复
    local cf = io.open(action_path, "w")
    if cf then cf:write("{}"); cf:close() end
    -- 简单解析 {"action": "BET"}
    local action = string.match(content, '"action"%s*:%s*"(%w+)"')
    return action
end

-- 主循环：每0.1秒检查一次
emu.register_periodic(function()
    local action = read_action()
    if action then
        press_action(action)
    end
    -- 写状态（占位，内存地址待找）
    local f = io.open(state_path, "w")
    if f then
        f:write('{"source": "lua", "input": "ioport"}')
        f:close()
    end
end, 0.1)

log("AI Bridge v4 (ioport直控) loaded")
print("AI Bridge v4 loaded - ioport direct control")
