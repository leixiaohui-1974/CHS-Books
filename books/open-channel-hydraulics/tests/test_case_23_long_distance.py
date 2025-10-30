"""
案例23单元测试：长距离输水管道设计

测试内容：
1. 沿程损失计算
2. 泵站扬程计算
3. 泵站功率计算
4. 建设费用计算
5. 运行费用计算
6. 总费用计算
7. 经济管径确定
8. 经济流速验证
9. 分段设计
10. 敏感性分析

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def pipe_velocity(Q, D):
    """计算管道流速"""
    v = 4 * Q / (np.pi * D**2)
    return v


def darcy_head_loss_total(lambda_f, L, D, Q, g=9.81):
    """计算总沿程损失（达西公式）"""
    v = pipe_velocity(Q, D)
    h_f = lambda_f * (L / D) * (v**2 / (2 * g))
    return h_f


def pump_head(delta_z, h_f, h_m=0):
    """
    计算泵站扬程
    H = Δz + h_f + h_m
    """
    H = delta_z + h_f + h_m
    return H


def pump_power(rho, g, Q, H, eta):
    """
    计算泵站功率 [kW]
    P = (ρ * g * Q * H) / (1000 * η)
    """
    P = (rho * g * Q * H) / (1000 * eta)
    return P


def annual_operation_cost(C_e, P, T):
    """
    计算年运行费用 [元]
    C_annual = 电价 × 功率 × 运行小时
    """
    C_annual = C_e * P * T
    return C_annual


def construction_cost_pipe(k, D, a, L):
    """
    计算管道建设费用 [元]
    C = k * D^a * L
    """
    C = k * (D**a) * L
    return C


def total_cost_npv(C_construction, C_annual, n, r=0.07):
    """
    计算总费用净现值 [元]
    NPV = C_construction + C_annual × PV_factor
    PV_factor = [(1+r)^n - 1] / [r(1+r)^n]
    """
    if r == 0:
        PV_factor = n
    else:
        PV_factor = ((1 + r)**n - 1) / (r * (1 + r)**n)

    NPV = C_construction + C_annual * PV_factor
    return NPV


def economic_velocity_formula(Q):
    """
    经济流速经验公式 [m/s]
    v = 1.1 * Q^0.4
    """
    v_econ = 1.1 * Q**0.4
    return v_econ


def economic_diameter_formula(Q):
    """
    经济管径经验公式 [m]
    D = 1.13 * Q^0.45
    """
    D_econ = 1.13 * Q**0.45
    return D_econ


def local_loss_coefficient(h_f, ratio=0.1):
    """
    局部损失（按沿程损失的百分比）
    h_m = ratio * h_f
    """
    h_m = ratio * h_f
    return h_m


def segmented_pipe_head_loss(lambda_f, Q, L1, D1, L2, D2, g=9.81):
    """
    分段管道总水头损失
    h_f_total = h_f1 + h_f2
    """
    h_f1 = darcy_head_loss_total(lambda_f, L1, D1, Q, g)
    h_f2 = darcy_head_loss_total(lambda_f, L2, D2, Q, g)
    h_f_total = h_f1 + h_f2
    return h_f_total


class TestCase23LongDistance:
    """案例23：长距离输水管道设计测试"""

    def test_pipe_velocity_calculation(self):
        """测试1：流速计算"""
        Q = 2.0  # m³/s
        D = 1.5  # m

        v = pipe_velocity(Q, D)

        # v = 4Q/(πD²) = 4×2.0/(π×1.5²) ≈ 1.132 m/s
        v_expected = 4 * Q / (np.pi * D**2)
        assert abs(v - v_expected) < 1e-6

    def test_head_loss_calculation(self):
        """测试2：沿程损失计算"""
        lambda_f = 0.02
        L = 50000  # m (50 km)
        D = 1.5    # m
        Q = 2.0    # m³/s

        h_f = darcy_head_loss_total(lambda_f, L, D, Q)

        # 应为正值
        assert h_f > 0

        # 长距离损失应显著
        assert h_f > 10  # 至少几十米

    def test_pump_head_calculation(self):
        """测试3：泵站扬程计算"""
        delta_z = 20  # m
        h_f = 50      # m
        h_m = 5       # m

        H = pump_head(delta_z, h_f, h_m)

        # H = 20 + 50 + 5 = 75 m
        assert abs(H - 75) < 1e-6

    def test_pump_power_calculation(self):
        """测试4：泵站功率计算"""
        rho = 1000  # kg/m³
        g = 9.81    # m/s²
        Q = 2.0     # m³/s
        H = 75      # m
        eta = 0.75  # 效率

        P = pump_power(rho, g, Q, H, eta)

        # P = (1000 × 9.81 × 2.0 × 75) / (1000 × 0.75) = 1962 kW
        P_expected = (rho * g * Q * H) / (1000 * eta)
        assert abs(P - P_expected) < 1e-6

    def test_annual_operation_cost(self):
        """测试5：年运行费用计算"""
        C_e = 0.6  # 元/kWh
        P = 2000   # kW
        T = 8000   # 小时/年

        C_annual = annual_operation_cost(C_e, P, T)

        # C = 0.6 × 2000 × 8000 = 9,600,000 元
        assert abs(C_annual - 9600000) < 1

    def test_construction_cost_calculation(self):
        """测试6：建设费用计算"""
        k = 8000   # 元/m (系数)
        D = 1.5    # m
        a = 1.6    # 指数
        L = 50000  # m

        C_construction = construction_cost_pipe(k, D, a, L)

        # C = 8000 × 1.5^1.6 × 50000
        C_expected = k * (D**a) * L
        assert abs(C_construction - C_expected) < 1

    def test_total_cost_npv(self):
        """测试7：总费用净现值计算"""
        C_construction = 600000000  # 6亿元
        C_annual = 10000000         # 1千万元/年
        n = 30                      # 30年
        r = 0.07                    # 7%折现率

        NPV = total_cost_npv(C_construction, C_annual, n, r)

        # NPV应大于建设费用
        assert NPV > C_construction

        # NPV应小于建设费用+简单累加的运行费用
        assert NPV < C_construction + C_annual * n

    def test_economic_velocity_formula(self):
        """测试8：经济流速公式"""
        Q = 2.0  # m³/s

        v_econ = economic_velocity_formula(Q)

        # v = 1.1 × 2.0^0.4 ≈ 1.43 m/s
        assert 1.0 < v_econ < 2.0

    def test_economic_diameter_formula(self):
        """测试9：经济管径公式"""
        Q = 2.0  # m³/s

        D_econ = economic_diameter_formula(Q)

        # D = 1.13 × 2.0^0.45 ≈ 1.45 m
        assert 1.2 < D_econ < 1.8

    def test_local_loss_coefficient(self):
        """测试10：局部损失计算"""
        h_f = 50  # m
        ratio = 0.1

        h_m = local_loss_coefficient(h_f, ratio)

        # h_m = 0.1 × 50 = 5 m
        assert abs(h_m - 5) < 1e-6

    def test_head_loss_decreases_with_diameter(self):
        """测试11：损失随管径增大而减小"""
        lambda_f = 0.02
        L = 50000
        Q = 2.0

        D1 = 1.2
        D2 = 1.8

        h_f1 = darcy_head_loss_total(lambda_f, L, D1, Q)
        h_f2 = darcy_head_loss_total(lambda_f, L, D2, Q)

        # 管径越大，损失越小
        assert h_f1 > h_f2

        # h_f与D⁵成反比
        ratio = h_f1 / h_f2
        expected_ratio = (D2 / D1)**5
        assert abs(ratio - expected_ratio) < 0.01

    def test_power_proportional_to_head_loss(self):
        """测试12：功率与水头损失成正比"""
        rho, g, Q, eta = 1000, 9.81, 2.0, 0.75
        delta_z = 20

        h_f1 = 30
        h_f2 = 60

        H1 = pump_head(delta_z, h_f1)
        H2 = pump_head(delta_z, h_f2)

        P1 = pump_power(rho, g, Q, H1, eta)
        P2 = pump_power(rho, g, Q, H2, eta)

        # 功率与扬程成正比
        assert P2 > P1

    def test_diameter_range_realistic(self):
        """测试13：管径范围合理性验证"""
        Q = 2.0
        diameters = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

        for D in diameters:
            v = pipe_velocity(Q, D)
            # 流速应在合理范围
            assert 0.3 < v < 5.0

    def test_segmented_pipe_design(self):
        """测试14：分段管道设计"""
        lambda_f = 0.02
        Q = 2.0
        L_total = 50000

        # 等径方案
        D_uniform = 1.5
        h_f_uniform = darcy_head_loss_total(lambda_f, L_total, D_uniform, Q)

        # 分段方案
        L1 = 25000
        D1 = 1.6
        L2 = 25000
        D2 = 1.4
        h_f_segmented = segmented_pipe_head_loss(lambda_f, Q, L1, D1, L2, D2)

        # 分段方案损失应介于两个极端之间
        h_f_large = darcy_head_loss_total(lambda_f, L_total, D1, Q)
        h_f_small = darcy_head_loss_total(lambda_f, L_total, D2, Q)

        assert h_f_large < h_f_segmented < h_f_small

    def test_npv_zero_discount_rate(self):
        """测试15：零折现率情况"""
        C_construction = 1000000
        C_annual = 100000
        n = 10
        r = 0.0

        NPV = total_cost_npv(C_construction, C_annual, n, r)

        # 零折现率：简单累加
        assert abs(NPV - (C_construction + C_annual * n)) < 1

    def test_economic_diameter_increases_with_flow(self):
        """测试16：经济管径随流量增大"""
        Q1 = 1.0
        Q2 = 3.0

        D1 = economic_diameter_formula(Q1)
        D2 = economic_diameter_formula(Q2)

        # 流量越大，经济管径越大
        assert D2 > D1


class TestTechnicalEconomicAnalysis:
    """技术经济分析测试"""

    def test_optimal_diameter_exists(self):
        """测试1：存在最优管径"""
        # 设置参数
        L = 50000
        Q = 2.0
        lambda_f = 0.02
        delta_z = 20
        k = 8000
        a = 1.6
        C_e = 0.6
        T = 8000
        n = 30
        rho, g, eta = 1000, 9.81, 0.75

        # 测试多个管径
        diameters = np.linspace(1.0, 2.5, 10)
        total_costs = []

        for D in diameters:
            # 水头损失
            h_f = darcy_head_loss_total(lambda_f, L, D, Q, g)
            h_m = local_loss_coefficient(h_f, 0.1)

            # 扬程和功率
            H = pump_head(delta_z, h_f, h_m)
            P = pump_power(rho, g, Q, H, eta)

            # 费用
            C_construction = construction_cost_pipe(k, D, a, L)
            C_annual = annual_operation_cost(C_e, P, T)
            NPV = total_cost_npv(C_construction, C_annual, n)

            total_costs.append(NPV)

        # 应该存在最小值（非单调）
        min_cost = min(total_costs)
        min_idx = total_costs.index(min_cost)

        # 最小值不在端点
        assert 0 < min_idx < len(total_costs) - 1

    def test_construction_cost_increases_with_diameter(self):
        """测试2：建设费用随管径增加"""
        k, a, L = 8000, 1.6, 50000

        D1 = 1.2
        D2 = 1.8

        C1 = construction_cost_pipe(k, D1, a, L)
        C2 = construction_cost_pipe(k, D2, a, L)

        # 管径越大，建设费用越高
        assert C2 > C1

    def test_operation_cost_decreases_with_diameter(self):
        """测试3：运行费用随管径减小"""
        lambda_f, L, Q = 0.02, 50000, 2.0
        delta_z = 20
        C_e, T = 0.6, 8000
        rho, g, eta = 1000, 9.81, 0.75

        D1 = 1.2
        D2 = 1.8

        # D1方案
        h_f1 = darcy_head_loss_total(lambda_f, L, D1, Q, g)
        H1 = pump_head(delta_z, h_f1)
        P1 = pump_power(rho, g, Q, H1, eta)
        C_op1 = annual_operation_cost(C_e, P1, T)

        # D2方案
        h_f2 = darcy_head_loss_total(lambda_f, L, D2, Q, g)
        H2 = pump_head(delta_z, h_f2)
        P2 = pump_power(rho, g, Q, H2, eta)
        C_op2 = annual_operation_cost(C_e, P2, T)

        # 管径越大，运行费用越低
        assert C_op2 < C_op1


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_elevation_difference(self):
        """测试1：零高程差"""
        delta_z = 0
        h_f = 50

        H = pump_head(delta_z, h_f)

        # H = h_f
        assert abs(H - 50) < 1e-6

    def test_very_long_distance(self):
        """测试2：超长距离"""
        lambda_f = 0.02
        L = 500000  # 500 km
        D = 2.0
        Q = 2.0

        h_f = darcy_head_loss_total(lambda_f, L, D, Q)

        # 超长距离损失巨大
        assert h_f > 100

    def test_very_large_flow(self):
        """测试3：大流量"""
        Q = 10.0  # m³/s
        D = 2.0

        v = pipe_velocity(Q, D)

        # 大流量高流速
        assert v > 3.0

    def test_high_efficiency_pump(self):
        """测试4：高效率泵"""
        rho, g, Q, H = 1000, 9.81, 2.0, 75
        eta = 0.90  # 高效率

        P = pump_power(rho, g, Q, H, eta)

        # 高效率功率较小
        assert P < 2000

    def test_low_efficiency_pump(self):
        """测试5：低效率泵"""
        rho, g, Q, H = 1000, 9.81, 2.0, 75
        eta = 0.60  # 低效率

        P = pump_power(rho, g, Q, H, eta)

        # 低效率功率较大
        assert P > 2000

    def test_very_small_diameter(self):
        """测试6：极小管径"""
        Q = 2.0
        D = 0.5  # 很小

        v = pipe_velocity(Q, D)

        # 极小管径流速极大
        assert v > 10.0

    def test_very_large_diameter(self):
        """测试7：极大管径"""
        Q = 2.0
        D = 5.0  # 很大

        v = pipe_velocity(Q, D)

        # 极大管径流速极小
        assert v < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
