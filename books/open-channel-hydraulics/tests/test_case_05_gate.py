"""
案例5单元测试：渠道闸门出流计算

测试内容：
1. 自由出流流量计算
2. 淹没出流流量计算
3. 淹没度判别
4. 开度反算
5. 流量-开度关系
6. 上游水头影响
7. 下游水深影响
8. 流量系数影响
9. 收缩断面验证
10. 能量损失分析

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.structures import Gate


class TestCase05GateFlow:
    """案例5：渠道闸门出流测试"""

    def test_free_flow_discharge(self):
        """测试1：自由出流流量计算"""
        b = 2.0  # 闸门宽度
        mu = 0.60  # 流量系数
        e = 0.8  # 闸门开度
        H = 3.0  # 上游水头

        gate = Gate(b=b, mu=mu)

        # 自由出流公式：Q = μ * b * e * sqrt(2g * H)
        g = 9.81
        Q_calc = gate.discharge_free(e, H)
        Q_theoretical = mu * b * e * np.sqrt(2*g * H)

        # 验证计算正确
        assert abs(Q_calc - Q_theoretical) / Q_theoretical < 0.001

    def test_submerged_flow_discharge(self):
        """测试2：淹没出流流量计算"""
        b = 2.0
        mu_s = 0.85  # 淹没流量系数
        e = 0.8
        H1 = 3.0  # 上游水深
        H2 = 2.0  # 下游水深

        gate = Gate(b=b, mu_s=mu_s)

        # 淹没出流公式：Q = μs * b * e * sqrt(2g * (H1 - H2))
        g = 9.81
        Q_calc = gate.discharge_submerged(e, H1, H2)
        Q_theoretical = mu_s * b * e * np.sqrt(2*g * (H1 - H2))

        # 验证计算正确
        assert abs(Q_calc - Q_theoretical) / Q_theoretical < 0.001

    def test_submergence_check(self):
        """测试3：淹没度判别"""
        b = 2.0
        mu = 0.60
        e = 0.8
        H1 = 3.0

        gate = Gate(b=b, mu=mu)

        # 测试不同下游水深的淹没判别
        # σ < 0.6：自由出流
        H2_free = 1.5  # σ = 0.5
        assert not gate.check_submergence(e, H1, H2_free)

        # σ > 0.6：淹没出流
        H2_submerged = 2.5  # σ = 0.833
        assert gate.check_submergence(e, H1, H2_submerged)

        # 临界点 σ ≈ 0.6
        H2_critical = 0.6 * H1
        is_submerged = gate.check_submergence(e, H1, H2_critical)
        # σ = 0.6 处于边界，可能是自由或淹没
        assert isinstance(is_submerged, bool)

    def test_opening_from_discharge(self):
        """测试4：开度反算"""
        b = 2.0
        mu = 0.60
        H = 3.0
        Q_design = 6.0

        gate = Gate(b=b, mu=mu)

        # 反算开度
        e_calc = gate.opening_from_discharge(Q_design, H)

        # 验证：用反算的开度计算流量，应该等于设计流量
        Q_verify = gate.discharge_free(e_calc, H)
        assert abs(Q_verify - Q_design) / Q_design < 0.001

        # 理论开度：e = Q / (μ * b * sqrt(2g * H))
        g = 9.81
        e_theoretical = Q_design / (mu * b * np.sqrt(2*g * H))
        assert abs(e_calc - e_theoretical) / e_theoretical < 0.001

    def test_discharge_opening_relationship(self):
        """测试5：流量-开度关系"""
        b = 2.0
        mu = 0.60
        H = 3.0

        gate = Gate(b=b, mu=mu)

        # 测试不同开度的流量
        openings = [0.3, 0.5, 0.7, 0.9, 1.2]
        Q_list = []

        for e in openings:
            Q = gate.discharge_free(e, H)
            Q_list.append(Q)

        # 开度增大，流量应增大
        for i in range(len(Q_list)-1):
            assert Q_list[i] < Q_list[i+1]

        # 验证Q与e成正比（其他参数不变）
        for i in range(len(openings)):
            ratio = Q_list[i] / openings[i]
            # 所有比值应该相同（常数）
            if i > 0:
                assert abs(ratio - Q_list[0]/openings[0]) / ratio < 0.001

    def test_upstream_head_effect(self):
        """测试6：上游水头影响"""
        b = 2.0
        mu = 0.60
        e = 0.8

        gate = Gate(b=b, mu=mu)

        # 测试不同上游水头
        heads = [2.0, 2.5, 3.0, 3.5, 4.0]
        Q_list = []

        for H in heads:
            Q = gate.discharge_free(e, H)
            Q_list.append(Q)

        # 水头增大，流量应增大
        for i in range(len(Q_list)-1):
            assert Q_list[i] < Q_list[i+1]

        # 验证Q与sqrt(H)成正比
        for i in range(len(heads)):
            ratio = Q_list[i] / np.sqrt(heads[i])
            # 所有比值应该相同
            if i > 0:
                assert abs(ratio - Q_list[0]/np.sqrt(heads[0])) / ratio < 0.001

    def test_downstream_depth_effect(self):
        """测试7：下游水深影响"""
        b = 2.0
        mu = 0.60
        mu_s = 0.85
        e = 0.8
        H1 = 3.0

        gate = Gate(b=b, mu=mu, mu_s=mu_s)

        # 参考自由出流流量
        Q_free = gate.discharge_free(e, H1)

        # 测试不同下游水深
        h2_values = [0.5, 1.0, 1.5, 2.0, 2.5]
        Q_list = []

        for h2 in h2_values:
            sigma = h2 / H1

            if sigma > 0.6:
                # 淹没出流
                Q = gate.discharge_submerged(e, H1, h2)
            else:
                # 自由出流
                Q = Q_free

            Q_list.append(Q)

        # 下游水深增大，流量应减小或不变
        for i in range(len(Q_list)-1):
            assert Q_list[i] >= Q_list[i+1] - 0.01  # 允许小误差

    def test_coefficient_effect(self):
        """测试8：流量系数影响"""
        b = 2.0
        e = 0.8
        H = 3.0

        # 测试不同流量系数
        coefficients = [0.55, 0.58, 0.60, 0.62, 0.65]
        Q_list = []

        for mu in coefficients:
            gate = Gate(b=b, mu=mu)
            Q = gate.discharge_free(e, H)
            Q_list.append(Q)

        # 流量系数增大，流量增大
        for i in range(len(Q_list)-1):
            assert Q_list[i] < Q_list[i+1]

        # 验证Q与μ成正比
        for i in range(len(coefficients)):
            ratio = Q_list[i] / coefficients[i]
            if i > 0:
                assert abs(ratio - Q_list[0]/coefficients[0]) / ratio < 0.001

    def test_contraction_coefficient(self):
        """测试9：收缩系数验证"""
        b = 2.0
        mu = 0.60
        e = 0.8
        H = 3.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 收缩系数 Cc ≈ 0.61
        Cc = 0.61
        hc = Cc * e  # 收缩水深

        # 收缩断面流速（连续性方程）
        vc = Q / (b * hc)

        # 收缩水深应小于闸门开度
        assert hc < e
        assert abs(hc / e - Cc) < 0.01

        # 收缩断面流速应该较大（孔口出流特征）
        g = 9.81
        # 理论最大流速 v_max = sqrt(2gH)（无损失）
        v_max = np.sqrt(2 * g * H)

        # 实际流速应接近但小于理论最大值
        # 由于μ和Cc都约为0.6，流速应该很接近理论值
        assert vc <= v_max * 1.01  # 允许小误差

        # 但应该在合理范围内（0.9-1.0倍最大值）
        assert 0.85 * v_max < vc < 1.01 * v_max

    def test_energy_loss(self):
        """测试10：能量损失分析"""
        b = 2.0
        mu = 0.60
        e = 0.8
        H1 = 3.0
        h2 = 2.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H1)

        # 下游流速
        v2 = Q / (b * h2)
        g = 9.81

        # 下游比能
        E2 = h2 + v2**2 / (2*g)

        # 上游比能（假设上游流速很小）
        E1 = H1

        # 能量损失
        dE = E1 - E2

        # 能量损失应为正（损失）
        assert dE > 0

        # 损失率应在合理范围（通常5-30%）
        loss_ratio = dE / E1
        assert 0.01 < loss_ratio < 0.5

    def test_opening_range(self):
        """测试11：开度范围校核"""
        b = 2.0
        mu = 0.60
        H = 3.0

        gate = Gate(b=b, mu=mu)

        # 测试不同流量对应的开度
        Q_values = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]

        for Q_design in Q_values:
            e = gate.opening_from_discharge(Q_design, H)

            # 开度应大于0
            assert e > 0

            # 开度比 e/H 应在合理范围
            e_ratio = e / H
            # 一般开度不应超过上游水深的80%
            assert e_ratio < 1.0  # 开度小于水深

            # 对于小流量，开度应大于0.05m（防堵）
            if Q_design < 3.0:
                assert e > 0.05

    def test_free_vs_submerged_flow(self):
        """测试12：自由出流与淹没出流对比"""
        b = 2.0
        mu = 0.60
        mu_s = 0.85
        e = 0.8
        H1 = 3.0
        H2 = 2.0

        gate = Gate(b=b, mu=mu, mu_s=mu_s)

        # 自由出流流量
        Q_free = gate.discharge_free(e, H1)

        # 淹没出流流量
        Q_submerged = gate.discharge_submerged(e, H1, H2)

        # 淹没出流应小于自由出流（有效水头降低）
        assert Q_submerged < Q_free


class TestEdgeCases:
    """边界条件测试"""

    def test_small_opening(self):
        """测试极小开度"""
        b = 2.0
        mu = 0.60
        e = 0.05  # 极小开度
        H = 3.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 应该能计算，且流量很小
        assert Q > 0
        assert Q < 1.0

    def test_large_opening(self):
        """测试较大开度"""
        b = 2.0
        mu = 0.60
        e = 2.0  # 较大开度
        H = 3.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 应该能计算
        assert Q > 0
        assert Q < 50.0  # 合理上限

    def test_low_head(self):
        """测试低水头"""
        b = 2.0
        mu = 0.60
        e = 0.5
        H = 0.5  # 低水头

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 应该能计算
        assert Q > 0
        assert Q < 5.0

    def test_high_head(self):
        """测试高水头"""
        b = 2.0
        mu = 0.60
        e = 0.8
        H = 10.0  # 高水头

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 应该能计算，流量较大
        assert Q > 5.0

    def test_wide_gate(self):
        """测试宽闸门"""
        b = 10.0  # 宽闸门
        mu = 0.60
        e = 0.8
        H = 3.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 宽闸门流量应大
        assert Q > 10.0

    def test_narrow_gate(self):
        """测试窄闸门"""
        b = 0.5  # 窄闸门
        mu = 0.60
        e = 0.8
        H = 3.0

        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        # 窄闸门流量应小
        assert Q < 5.0

    def test_critical_submergence(self):
        """测试临界淹没度"""
        b = 2.0
        mu = 0.60
        e = 0.8
        H1 = 3.0
        H2_critical = 0.6 * H1  # σ = 0.6

        gate = Gate(b=b, mu=mu)

        # 临界淹没度判别
        is_submerged = gate.check_submergence(e, H1, H2_critical)

        # 应该返回布尔值
        assert isinstance(is_submerged, bool)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
