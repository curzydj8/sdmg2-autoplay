/**
 * 游戏标准流程逻辑模块（C++）
 * 标准流程（用户2026-10-18确立）：
 * 1. 检查CREDIT：0-10 → 上500分；>10 → 跳过
 * 2. 循环读BET：<10 → 按3；==10 → 停止（最多15次）
 * 3. 确认BET==10 → 按1 START
 */

#include <iostream>
#include <string>

class StandardGameFlow {
private:
    int target_bet = 10;
    
public:
    // 步骤1：检查是否需要上分
    bool check_credit_needs_topup(int credit) {
        return credit >= 0 && credit <= 10;
    }
    
    // 步骤3：是否可以START
    bool should_start(int bet) {
        return bet == target_bet;
    }
    
    // 获取目标押注
    int get_target_bet() const { return target_bet; }
};

// C接口，供Python ctypes调用
extern "C" {
    StandardGameFlow* flow_create() {
        return new StandardGameFlow();
    }
    
    void flow_destroy(StandardGameFlow* flow) {
        delete flow;
    }
    
    int flow_check_topup(StandardGameFlow* flow, int credit) {
        return flow->check_credit_needs_topup(credit) ? 1 : 0;
    }
    
    int flow_should_start(StandardGameFlow* flow, int bet) {
        return flow->should_start(bet) ? 1 : 0;
    }
    
    int flow_get_target(StandardGameFlow* flow) {
        return flow->get_target_bet();
    }
}
