"""
案例2单元测试：城市雨水排水渠设计

测试内容：
1. 矩形断面面积计算
2. 矩形断面湿周计算
3. 矩形断面水力半径
4. 临界水深计算
5. 临界流速计算
6. 流态判别
7. 流速控制校核
8. 比能曲线
9. 单宽流量
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


def rectangular_area(b, h):
    """计算矩形断面面积"""
    A = b * h
    return A


def rectangular_wetted_perimeter(b, h):
    """计算矩形断面湿周"""
    chi = b + 2 * h
    return chi


def hydraulic_radius(A, chi):
    """计算水力半径"""
    if chi > 0:
        R = A / chi
    else:
        R = 0.0
    return R


def unit_discharge(Q, b):
    """计算单宽流量"""
    q = Q / b
    return q


def critical_depth_rectangular(q, g=9.81):
    """计算矩形断面临界水深: hc = (q²/g)^(1/3)"""
    hc = (q**2 / g)**(1.0/3.0)
    return hc


def critical_velocity(q, hc):
    """计算临界流速"""
    vc = q / hc
    return vc


def manning_velocity(R, S0, n):
    """曼宁公式计算流速"""
    v = (1.0 / n) * R**(2.0/3.0) * S0**0.5
    return v


def froude_number(v, h, g=9.81):
    """计算弗劳德数"""
    Fr = v / np.sqrt(g * h)
    return Fr


def determine_flow_regime(Fr):
    """判别流态"""
    if Fr < 0.98:
        return 'subcritical'
    elif Fr > 1.02:
        return 'supercritical'
    else:
        return 'critical'


def check_velocity_limits(v, v_min=0.6, v_max=3.0):
    """校核流速是否满足要求"""
    if v < v_min:
        return False, f"流速过小 ({v:.2f} < {v_min}), 可能淤积"
    elif v > v_max:
        return False, f"流速过大 ({v:.2f} > {v_max}), 可能冲刷"
    else:
        return True, f"流速合适 ({v:.2f} m/s)"


def specific_energy(h, v, g=9.81):
    """计算比能"""
    E = h + v**2 / (2 * g)
    return E


def compute_normal_depth_rectangular(Q, b, S0, n, h_init=1.0, tol=1e-6, max_iter=100):
    """计算矩形断面正常水深"""
    h = h_init

    for i in range(max_iter):
        A = rectangular_area(b, h)
        chi = rectangular_wetted_perimeter(b, h)
        R = hydraulic_radius(A, chi)
        v = manning_velocity(R, S0, n)
        Q_computed = A * v

        error = Q_computed - Q

        if abs(error) < tol:
            return h

        dh = 0.001
        A_plus = rectangular_area(b, h + dh)
        chi_plus = rectangular_wetted_perimeter(b, h + dh)
        R_plus = hydraulic_radius(A_plus, chi_plus)
        v_plus = manning_velocity(R_plus, S0, n)
        Q_plus = A_plus * v_plus

        dQ_dh = (Q_plus - Q_computed) / dh

        if abs(dQ_dh) > 1e-10:
            h = h - error / dQ_dh

        h = max(h, 0.01)

    return h


class TestCase02Drainage:
    """案例2：城市雨水排水渠设计测试"""

    def test_rectangular_area_calculation(self):
        """测试1：矩形断面面积计算"""
        b, h = 1.5, 0.6
        A = rectangular_area(b, h)
        assert abs(A - b * h) < 1e-10
        assert A > 0

    def test_rectangular_wetted_perimeter(self):
        """测试2：矩形断面湿周计算"""
        b, h = 1.5, 0.6
        chi = rectangular_wetted_perimeter(b, h)
        assert abs(chi - (b + 2 * h)) < 1e-10

    def test_hydraulic_radius_rectangular(self):
        """测试3：矩形断面水力半径"""
        b, h = 1.5, 0.6
        A = rectangular_area(b, h)
        chi = rectangular_wetted_perimeter(b, h)
        R = hydraulic_radius(A, chi)
        assert abs(R - b * h / (b + 2 * h)) < 1e-10

    def test_unit_discharge_calculation(self):
        """测试4：单宽流量计算"""
        Q, b = 1.2, 1.5
        q = unit_discharge(Q, b)
        assert abs(q - Q / b) < 1e-10

    def test_critical_depth_rectangular(self):
        """测试5：矩形断面临界水深"""
        q, g = 0.8, 9.81
        hc = critical_depth_rectangular(q, g)
        assert abs(hc - (q**2 / g)**(1.0/3.0)) < 1e-10
        assert hc > 0

    def test_critical_velocity_calculation(self):
        """测试6：临界流速计算"""
        q, hc = 0.8, 0.5
        vc = critical_velocity(q, hc)
        assert abs(vc - q / hc) < 1e-10

    def test_critical_velocity_froude_number(self):
        """测试7：临界流速的弗劳德数"""
        q, g = 0.8, 9.81
        hc = critical_depth_rectangular(q, g)
        vc = critical_velocity(q, hc)
        Fr = froude_number(vc, hc, g)
        assert abs(Fr - 1.0) < 0.01

    def test_flow_regime_determination(self):
        """测试8：流态判别"""
        assert determine_flow_regime(0.7) == 'subcritical'
        assert determine_flow_regime(1.0) == 'critical'
        assert determine_flow_regime(1.5) == 'supercritical'

    def test_velocity_limits_check(self):
        """测试9：流速校核"""
        is_valid, _ = check_velocity_limits(1.2, 0.6, 3.0)
        assert is_valid == True
        is_valid, _ = check_velocity_limits(0.4, 0.6, 3.0)
        assert is_valid == False
        is_valid, _ = check_velocity_limits(3.5, 0.6, 3.0)
        assert is_valid == False

    def test_specific_energy_calculation(self):
        """测试10：比能计算"""
        h, v, g = 0.6, 1.2, 9.81
        E = specific_energy(h, v, g)
        assert abs(E - (h + v**2 / (2 * g))) < 1e-10

    def test_drainage_case_realistic_values(self):
        """测试11：排水案例实际参数验证"""
        Q, b, S0, n = 1.2, 1.5, 0.003, 0.013
        h_normal = compute_normal_depth_rectangular(Q, b, S0, n)
        A = rectangular_area(b, h_normal)
        v = Q / A
        q = unit_discharge(Q, b)
        hc = critical_depth_rectangular(q)
        Fr = froude_number(v, h_normal)

        # 实际计算：h_normal ≈ 0.44m, v ≈ 1.8m/s
        assert 0.4 < h_normal < 0.8
        assert 1.0 < v < 2.0
        assert Fr < 1.0
        assert h_normal > hc

    def test_specific_energy_minimum_at_critical(self):
        """测试12：临界流时比能最小"""
        q, g = 0.8, 9.81
        hc = critical_depth_rectangular(q, g)
        vc = critical_velocity(q, hc)
        E_critical = specific_energy(hc, vc, g)

        dh = 0.1
        h_minus = hc - dh
        v_minus = q / h_minus
        E_minus = specific_energy(h_minus, v_minus, g)

        h_plus = hc + dh
        v_plus = q / h_plus
        E_plus = specific_energy(h_plus, v_plus, g)

        assert E_critical < E_minus
        assert E_critical < E_plus


class TestDesignOptimization:
    """设计优化测试"""

    def test_slope_effect_on_velocity(self):
        """测试坡度对流速的影响"""
        Q, b, n = 1.2, 1.5, 0.013
        S1, S2 = 0.001, 0.005

        h1 = compute_normal_depth_rectangular(Q, b, S1, n)
        h2 = compute_normal_depth_rectangular(Q, b, S2, n)

        v1 = Q / (b * h1)
        v2 = Q / (b * h2)

        assert v2 > v1

    def test_width_effect_on_velocity(self):
        """测试宽度对流速的影响"""
        Q, S0, n = 1.2, 0.003, 0.013
        b1, b2 = 1.0, 2.0

        h1 = compute_normal_depth_rectangular(Q, b1, S0, n)
        h2 = compute_normal_depth_rectangular(Q, b2, S0, n)

        v1 = Q / (b1 * h1)
        v2 = Q / (b2 * h2)

        assert v1 > v2

    def test_roughness_effect_on_depth(self):
        """测试糙率对水深的影响"""
        Q, b, S0 = 1.2, 1.5, 0.003
        n1, n2 = 0.011, 0.015

        h1 = compute_normal_depth_rectangular(Q, b, S0, n1)
        h2 = compute_normal_depth_rectangular(Q, b, S0, n2)

        assert h2 > h1


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_depth(self):
        """测试零水深"""
        assert rectangular_area(1.5, 0.0) == 0.0

    def test_very_shallow_flow(self):
        """测试极浅水流"""
        b, h = 1.5, 0.01
        R = hydraulic_radius(rectangular_area(b, h), rectangular_wetted_perimeter(b, h))
        assert R < 0.01

    def test_very_wide_channel(self):
        """测试极宽渠道"""
        b, h = 100.0, 0.5
        R = hydraulic_radius(rectangular_area(b, h), rectangular_wetted_perimeter(b, h))
        assert R > 0.9 * h

    def test_very_narrow_channel(self):
        """测试极窄渠道"""
        b, h = 0.1, 1.0
        R = hydraulic_radius(rectangular_area(b, h), rectangular_wetted_perimeter(b, h))
        assert R < 0.1 * h

    def test_zero_slope(self):
        """测试零坡度"""
        R = hydraulic_radius(rectangular_area(1.5, 0.6), rectangular_wetted_perimeter(1.5, 0.6))
        v = manning_velocity(R, 0.0, 0.013)
        assert v == 0.0

    def test_very_small_discharge(self):
        """测试极小流量"""
        h_normal = compute_normal_depth_rectangular(0.01, 1.5, 0.003, 0.013)
        assert h_normal < 0.1

    def test_large_discharge(self):
        """测试大流量"""
        h_normal = compute_normal_depth_rectangular(10.0, 1.5, 0.003, 0.013)
        assert h_normal > 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
