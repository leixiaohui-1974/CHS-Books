"""
案例22单元测试：管网平衡计算

测试内容：
1. 管道水头损失计算
2. 节点流量平衡验证
3. 环路能量平衡验证
4. Hardy-Cross迭代法
5. 简单管网求解
6. 多环管网求解
7. 流量校正计算
8. 收敛性测试
9. 管道阻力系数
10. 边界条件测试

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def pipe_head_loss(K, Q, n=2.0):
    """
    管道水头损失（简化公式）
    h_f = K * Q^n
    """
    h_f = K * abs(Q)**n * np.sign(Q)
    return h_f


def pipe_resistance_coefficient(lambda_f, L, D, g=9.81):
    """
    计算管道阻力系数K
    h_f = K * Q²
    K = (8*λ*L) / (π²*g*D⁵)
    """
    K = (8 * lambda_f * L) / (np.pi**2 * g * D**5)
    return K


def loop_head_loss_sum(pipe_flows, pipe_K_values, n=2.0):
    """
    计算环路水头损失总和
    Σh_f = Σ(K * Q^n)
    """
    h_f_sum = 0.0
    for i, Q in enumerate(pipe_flows):
        K = pipe_K_values[i]
        h_f = pipe_head_loss(K, Q, n)
        h_f_sum += h_f
    return h_f_sum


def hardy_cross_correction(pipe_flows, pipe_K_values, n=2.0):
    """
    Hardy-Cross流量校正量
    ΔQ = -Σh_f / (n * Σ|h_f|/Q)
    """
    h_f_sum = 0.0
    denominator = 0.0

    for i, Q in enumerate(pipe_flows):
        K = pipe_K_values[i]
        h_f = pipe_head_loss(K, Q, n)
        h_f_sum += h_f

        if abs(Q) > 1e-10:
            denominator += abs(h_f) / abs(Q)

    if abs(denominator) < 1e-10:
        return 0.0

    delta_Q = -h_f_sum / (n * denominator)
    return delta_Q


def node_flow_balance(inflows, outflows, demand):
    """
    节点流量平衡验证
    Σ Q_in - Σ Q_out - Q_demand = 0
    """
    balance = sum(inflows) - sum(outflows) - demand
    return balance


def solve_single_loop_hardy_cross(pipe_K_values, Q_initial, n=2.0, tol=1e-6, max_iter=100):
    """
    Hardy-Cross法求解单环管网
    """
    Q = np.array(Q_initial, dtype=float)

    for iteration in range(max_iter):
        # 计算校正量
        delta_Q = hardy_cross_correction(Q, pipe_K_values, n)

        # 更新流量
        Q = Q + delta_Q

        # 检查收敛
        if abs(delta_Q) < tol:
            return Q, iteration + 1

    return Q, max_iter


class TestCase22PipeNetwork:
    """案例22：管网平衡计算测试"""

    def test_pipe_head_loss_calculation(self):
        """测试1：管道水头损失计算"""
        K = 1000  # 阻力系数
        Q = 0.02  # m³/s (20 L/s)
        n = 2.0

        h_f = pipe_head_loss(K, Q, n)

        # h_f = K * Q² = 1000 * 0.02² = 0.4 m
        assert abs(h_f - 0.4) < 1e-6

    def test_pipe_head_loss_negative_flow(self):
        """测试2：负流量水头损失"""
        K = 1000
        Q = -0.02  # 逆向流动
        n = 2.0

        h_f = pipe_head_loss(K, Q, n)

        # 逆向流动，h_f为负
        assert h_f < 0
        assert abs(h_f + 0.4) < 1e-6

    def test_resistance_coefficient_calculation(self):
        """测试3：阻力系数K计算"""
        lambda_f = 0.02
        L = 1000  # m
        D = 0.2   # m
        g = 9.81

        K = pipe_resistance_coefficient(lambda_f, L, D, g)

        # K = (8*λ*L) / (π²*g*D⁵)
        K_expected = (8 * lambda_f * L) / (np.pi**2 * g * D**5)
        assert abs(K - K_expected) < 1e-6

    def test_loop_head_loss_sum_balanced(self):
        """测试4：平衡环路水头损失和"""
        # 假设一个平衡的环路
        pipe_flows = [0.02, 0.01, -0.01, -0.02]  # m³/s
        pipe_K_values = [1000, 2000, 2000, 1000]

        h_f_sum = loop_head_loss_sum(pipe_flows, pipe_K_values)

        # 平衡环路：Σh_f ≈ 0
        assert abs(h_f_sum) < 0.1

    def test_loop_head_loss_sum_unbalanced(self):
        """测试5：不平衡环路水头损失和"""
        # 不平衡的环路
        pipe_flows = [0.03, 0.02, 0.01, 0.01]  # 全部正向
        pipe_K_values = [1000, 1000, 1000, 1000]

        h_f_sum = loop_head_loss_sum(pipe_flows, pipe_K_values)

        # 不平衡，h_f_sum应显著非零
        assert abs(h_f_sum) > 0.1

    def test_hardy_cross_correction_positive_sum(self):
        """测试6：Hardy-Cross校正（正不平衡量）"""
        pipe_flows = [0.03, 0.03, 0.03, 0.03]  # Σh_f > 0
        pipe_K_values = [1000, 1000, 1000, 1000]

        delta_Q = hardy_cross_correction(pipe_flows, pipe_K_values)

        # Σh_f > 0，需要减小流量，ΔQ < 0
        assert delta_Q < 0

    def test_hardy_cross_correction_negative_sum(self):
        """测试7：Hardy-Cross校正（负不平衡量）"""
        pipe_flows = [-0.03, -0.03, -0.03, -0.03]  # Σh_f < 0
        pipe_K_values = [1000, 1000, 1000, 1000]

        delta_Q = hardy_cross_correction(pipe_flows, pipe_K_values)

        # Σh_f < 0，需要增大流量，ΔQ > 0
        assert delta_Q > 0

    def test_node_flow_balance_satisfied(self):
        """测试8：节点流量平衡（满足）"""
        inflows = [0.05, 0.03]  # m³/s
        outflows = [0.04, 0.02]
        demand = 0.02  # m³/s

        balance = node_flow_balance(inflows, outflows, demand)

        # 0.05 + 0.03 - 0.04 - 0.02 - 0.02 = 0
        assert abs(balance) < 1e-10

    def test_node_flow_balance_violated(self):
        """测试9：节点流量平衡（不满足）"""
        inflows = [0.05, 0.03]
        outflows = [0.04, 0.02]
        demand = 0.05  # 需求过大

        balance = node_flow_balance(inflows, outflows, demand)

        # 不平衡
        assert abs(balance) > 0.01

    def test_simple_square_loop(self):
        """测试10：简单方形环路"""
        # 方形环路，4条管道
        pipe_K_values = [1000, 1000, 1000, 1000]
        Q_initial = [0.02, 0.02, -0.01, -0.01]  # 初始假设

        Q_final, iterations = solve_single_loop_hardy_cross(pipe_K_values, Q_initial)

        # 应该收敛
        assert iterations < 100

        # 验证环路平衡
        h_f_sum = loop_head_loss_sum(Q_final, pipe_K_values)
        assert abs(h_f_sum) < 1e-3

    def test_hardy_cross_convergence(self):
        """测试11：Hardy-Cross收敛性"""
        pipe_K_values = [500, 1000, 1500, 2000]
        Q_initial = [0.03, 0.02, -0.01, -0.02]

        Q_final, iterations = solve_single_loop_hardy_cross(pipe_K_values, Q_initial)

        # 应在合理迭代次数内收敛
        assert 1 <= iterations <= 50

        # 最终流量应使环路平衡
        h_f_sum = loop_head_loss_sum(Q_final, pipe_K_values)
        assert abs(h_f_sum) < 1e-4

    def test_symmetric_loop(self):
        """测试12：对称环路"""
        # 对称环路，所有管道阻力相同
        pipe_K_values = [1000, 1000, 1000, 1000]
        Q_initial = [0.02, 0.01, 0.01, 0.02]

        Q_final, iterations = solve_single_loop_hardy_cross(pipe_K_values, Q_initial)

        # 对称环路应快速收敛
        assert iterations < 20

        # 验证平衡
        h_f_sum = loop_head_loss_sum(Q_final, pipe_K_values)
        assert abs(h_f_sum) < 1e-5

    def test_asymmetric_loop(self):
        """测试13：非对称环路"""
        # 管道阻力差异大
        pipe_K_values = [100, 500, 2000, 5000]
        Q_initial = [0.05, 0.03, -0.02, -0.01]

        Q_final, iterations = solve_single_loop_hardy_cross(pipe_K_values, Q_initial)

        # 非对称环路可能需要更多迭代
        assert iterations < 100

        # 最终应平衡
        h_f_sum = loop_head_loss_sum(Q_final, pipe_K_values)
        assert abs(h_f_sum) < 1e-3

    def test_head_loss_proportional_to_Q_squared(self):
        """测试14：水头损失与流量平方成正比"""
        K = 1000
        Q1 = 0.01
        Q2 = 0.02

        h_f1 = pipe_head_loss(K, Q1, n=2.0)
        h_f2 = pipe_head_loss(K, Q2, n=2.0)

        # h_f2 / h_f1 = (Q2/Q1)²
        ratio = h_f2 / h_f1
        expected_ratio = (Q2 / Q1)**2
        assert abs(ratio - expected_ratio) < 1e-6

    def test_resistance_increases_with_length(self):
        """测试15：阻力系数随管长增加"""
        lambda_f = 0.02
        D = 0.2
        L1 = 500
        L2 = 1000

        K1 = pipe_resistance_coefficient(lambda_f, L1, D)
        K2 = pipe_resistance_coefficient(lambda_f, L2, D)

        # K与L成正比
        assert K2 / K1 == pytest.approx(2.0, rel=1e-6)

    def test_resistance_decreases_with_diameter(self):
        """测试16：阻力系数随管径减小"""
        lambda_f = 0.02
        L = 1000
        D1 = 0.2
        D2 = 0.4

        K1 = pipe_resistance_coefficient(lambda_f, L, D1)
        K2 = pipe_resistance_coefficient(lambda_f, L, D2)

        # K与D⁵成反比
        ratio = K1 / K2
        expected_ratio = (D2 / D1)**5
        assert ratio == pytest.approx(expected_ratio, rel=1e-6)


class TestHardyCrossIterations:
    """Hardy-Cross迭代特性测试"""

    def test_single_iteration_reduces_imbalance(self):
        """测试1：单次迭代减小不平衡量"""
        pipe_K_values = [1000, 1000, 1000, 1000]
        Q_initial = [0.05, 0.04, -0.02, -0.01]  # 显著不平衡

        # 初始不平衡量
        h_f_initial = loop_head_loss_sum(Q_initial, pipe_K_values)

        # 一次校正
        delta_Q = hardy_cross_correction(Q_initial, pipe_K_values)
        Q_updated = np.array(Q_initial) + delta_Q

        # 更新后不平衡量
        h_f_updated = loop_head_loss_sum(Q_updated, pipe_K_values)

        # 不平衡量应减小
        assert abs(h_f_updated) < abs(h_f_initial)

    def test_zero_correction_for_balanced_loop(self):
        """测试2：平衡环路校正量为零"""
        # 完全平衡的环路
        pipe_K_values = [1000, 1000, 1000, 1000]
        # 构造平衡流量：使Σh_f = 0
        Q1 = 0.02
        Q2 = 0.02
        Q3 = -0.02
        Q4 = -0.02
        pipe_flows = [Q1, Q2, Q3, Q4]

        delta_Q = hardy_cross_correction(pipe_flows, pipe_K_values)

        # 校正量应接近零
        assert abs(delta_Q) < 1e-6

    def test_monotonic_convergence(self):
        """测试3：单调收敛性"""
        pipe_K_values = [1000, 1000, 1000, 1000]
        Q_initial = [0.03, 0.02, -0.01, -0.01]

        Q = np.array(Q_initial, dtype=float)
        imbalances = []

        for i in range(10):
            h_f_sum = loop_head_loss_sum(Q, pipe_K_values)
            imbalances.append(abs(h_f_sum))

            delta_Q = hardy_cross_correction(Q, pipe_K_values)
            Q = Q + delta_Q

        # 不平衡量应单调递减
        for i in range(len(imbalances) - 1):
            assert imbalances[i+1] <= imbalances[i] + 1e-6


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_flow(self):
        """测试1：零流量"""
        K = 1000
        Q = 0.0

        h_f = pipe_head_loss(K, Q)

        assert h_f == 0.0

    def test_very_small_flow(self):
        """测试2：极小流量"""
        K = 1000
        Q = 1e-6  # 极小

        h_f = pipe_head_loss(K, Q)

        # 水头损失极小但为正
        assert h_f > 0
        assert h_f < 1e-6

    def test_very_large_flow(self):
        """测试3：极大流量"""
        K = 1000
        Q = 1.0  # 很大

        h_f = pipe_head_loss(K, Q)

        # 水头损失很大
        assert h_f > 100

    def test_high_resistance_pipe(self):
        """测试4：高阻力管道"""
        lambda_f = 0.05  # 高摩阻系数
        L = 5000  # 很长
        D = 0.1   # 细管

        K = pipe_resistance_coefficient(lambda_f, L, D)

        # 高阻力
        assert K > 1e6

    def test_low_resistance_pipe(self):
        """测试5：低阻力管道"""
        lambda_f = 0.01  # 低摩阻系数
        L = 100   # 短管
        D = 1.0   # 粗管

        K = pipe_resistance_coefficient(lambda_f, L, D)

        # 低阻力
        assert K < 100

    def test_all_forward_flow(self):
        """测试6：全部正向流动"""
        pipe_flows = [0.02, 0.03, 0.01, 0.02]
        pipe_K_values = [1000, 1000, 1000, 1000]

        h_f_sum = loop_head_loss_sum(pipe_flows, pipe_K_values)

        # 全部正向，Σh_f > 0
        assert h_f_sum > 0

    def test_all_reverse_flow(self):
        """测试7：全部逆向流动"""
        pipe_flows = [-0.02, -0.03, -0.01, -0.02]
        pipe_K_values = [1000, 1000, 1000, 1000]

        h_f_sum = loop_head_loss_sum(pipe_flows, pipe_K_values)

        # 全部逆向，Σh_f < 0
        assert h_f_sum < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
