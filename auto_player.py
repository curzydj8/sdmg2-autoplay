import json
import os
import time
import subprocess

STATE_FILE = '/tmp/sdmg2_state.json'
MAX_BET = 10

KEY_COIN = '5'
KEY_BET = '3'
KEY_START = '1'
KEY_ENTER = 'Return'
TILE_KEYS = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n']


MAME_WIN_ID = None
LAST_ACTION = None
SAME_ACTION_COUNT = 0
LAST_HAND_HASH = None

def get_mame_window():
    global MAME_WIN_ID
    if MAME_WIN_ID:
        return MAME_WIN_ID
    try:
        result = subprocess.run(
            ['bash', '-c', 'export DISPLAY=:0 && xdotool search --onlyvisible --class "mame" | head -1'],
            capture_output=True, text=True, timeout=5
        )
        win_id = result.stdout.strip()
        if win_id:
            MAME_WIN_ID = win_id
            print(f'找到MAME窗口: {win_id}')
            return win_id
    except Exception as e:
        print(f'获取窗口ID失败: {e}')
    return None


def xdotool_key(key, delay=0.2):
    win_id = get_mame_window()
    if win_id:
        subprocess.run(['xdotool', 'key', '--window', win_id, '--clearmodifiers', key],
                       env={**os.environ, 'DISPLAY': ':0'},
                       capture_output=True)
    else:
        subprocess.run(['xdotool', 'key', '--clearmodifiers', key],
                       env={**os.environ, 'DISPLAY': ':0'},
                       capture_output=True)
    time.sleep(delay)


class MemoryReader:
    @staticmethod
    def read():
        if not os.path.exists(STATE_FILE):
            return None
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return None


def decide_action(state):
    global LAST_ACTION, SAME_ACTION_COUNT, LAST_HAND_HASH
    credit = state.get('credit', 0)
    bet = state.get('bet', 0)
    hand = state.get('hand', [0] * 14)
    is_all_zero = all(c == 0 for c in hand)
    has_tiles = any(c != 0 and c != 0xFF for c in hand)
    hand_hash = tuple(hand)

    # BET有效性校验：如果credit>0但bet异常大（>10），视为脏数据，重新押注
    if bet > MAX_BET:
        print(f'警告：BET={bet}异常，视为脏数据')
        bet = 0

    if is_all_zero:
        if credit == 0:
            return ('coin', 1)
        if bet < MAX_BET:
            return ('bet', 1)
        if bet >= MAX_BET:
            return ('start', 1)

    if has_tiles and credit == 0 and bet == 0:
        return ('collect', 1)

    if has_tiles:
        # 防卡死：连续3次打牌手牌无变化，尝试按Enter打破僵局（可能是胡/杠/结算）
        if hand_hash == LAST_HAND_HASH and LAST_ACTION == 'discard':
            SAME_ACTION_COUNT += 1
        else:
            SAME_ACTION_COUNT = 0
        LAST_HAND_HASH = hand_hash

        if SAME_ACTION_COUNT >= 3:
            SAME_ACTION_COUNT = 0
            print('检测到打牌卡死，尝试按Enter打破！')
            return ('collect', 1)

        for i, card in enumerate(hand):
            if card >= 0x30:
                return ('discard', i)
        return ('discard', 13)

    return ('collect', 1)


def execute_action(action, param):
    print(f'执行动作: [{action}] 参数: {param}')
    if action == 'coin':
        for _ in range(5):
            xdotool_key(KEY_COIN, 0.3)
    elif action == 'bet':
        # 快速连押：一次按3次
        for _ in range(3):
            xdotool_key(KEY_BET, 0.08)
    elif action == 'start':
        xdotool_key(KEY_START, 0.5)
    elif action == 'discard':
        if 0 <= param < len(TILE_KEYS):
            xdotool_key(TILE_KEYS[param], 0.3)
    elif action == 'collect':
        xdotool_key(KEY_ENTER, 0.5)


def main():
    print('=== 大满贯AI (xdotool版) 启动 ===')
    print('正在获取MAME窗口...')
    get_mame_window()
    time.sleep(1)
    
    # 自动过警告屏：按几次Enter/Space
    print('正在跳过MAME警告屏...')
    for _ in range(3):
        win_id = get_mame_window()
        if win_id:
            subprocess.run(['xdotool', 'key', '--window', win_id, 'Return'],
                           env={**os.environ, 'DISPLAY': ':0'},
                           capture_output=True)
            time.sleep(1)
            subprocess.run(['xdotool', 'key', '--window', win_id, 'space'],
                           env={**os.environ, 'DISPLAY': ':0'},
                           capture_output=True)
            time.sleep(1)
    print('警告屏已过，等待游戏就绪...')
    
    # 等待JSON出现（游戏真正启动）
    for _ in range(20):
        if os.path.exists(STATE_FILE):
            print('游戏就绪！')
            break
        time.sleep(1)
    else:
        print('警告：JSON文件未出现，游戏可能未启动')
    print('焦点已锁定！')

    while True:
        state = MemoryReader.read()
        if not state:
            time.sleep(0.5)
            continue
        credit = state.get('credit', 0)
        bet = state.get('bet', 0)
        hand = state.get('hand', [])
        print(f'感知 CREDIT:{credit} BET:{bet} 手牌:{[hex(c) for c in hand[:5]]}...')
        action, param = decide_action(state)
        LAST_ACTION = action
        execute_action(action, param)
        time.sleep(0.3)


if __name__ == '__main__':
    main()
