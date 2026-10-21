"""P5验收测试"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../tools'))
from recorder import Recorder
from data_tools import export_jsonl, check_quality

def test_p5():
    r = Recorder()
    # 1. 创建对局
    sid = r.start_session(data_source="acceptance_test")
    assert sid > 0, "创建对局失败"
    print("✓ 创建对局")

    # 2. 连续记录状态动作
    for i in range(3):
        st = r.record_state(sid, i+1, {"hand": ["1wan"]*14}, phase="play")
        aid = r.record_action(sid, st, ["a","b"], "a", duration_ms=100)
        r.finish_action(aid, "success")
    print("✓ 连续记录3组状态动作")

    # 3. 记录失败
    st = r.record_state(sid, 4, {}, phase="play")
    aid = r.record_action(sid, st, ["x"], "x", duration_ms=50)
    r.finish_action(aid, "failed", "按键无响应")
    print("✓ 记录失败动作")

    # 4. 结束对局
    r.end_session(sid, final_score=200)
    print("✓ 保存结算")

    # 5. 导出JSONL
    out = export_jsonl(session_id=sid)
    assert os.path.exists(out)
    print("✓ 导出JSONL")

    # 6. 重新读取校验
    with open(out, encoding="utf-8") as f:
        data = json.loads(f.readline())
    assert "session" in data and "states" in data and "actions" in data
    assert len(data["states"]) == 4 and len(data["actions"]) == 4
    print("✓ 导出数据结构校验")

    # 7. 质量检查
    issues = check_quality()
    print("✓ 质量检查")

    print("\nP5验收全部通过")

if __name__ == "__main__":
    test_p5()
