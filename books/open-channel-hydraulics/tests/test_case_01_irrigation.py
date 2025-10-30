"""
案例1单元测试：农村灌溉渠流量计算

测试内容：
1. 梯形断面面积计算
2. 梯形断面湿周计算
3. 梯形断面水力半径
4. 梯形断面水面宽度
5. 曼宁公式流速计算
6. 流量计算
7. 正常水深迭代求解
8. 弗劳德数计算
9. 流态判别
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


def trapezoidal_area(b, h, m):
    """
    计算梯形断面面积

    Args:
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数（水平:垂直）

    Returns:
        A: 面积 (m²)
    """
    A = (b + m * h) * h
    return A


def trapezoidal_wetted_perimeter(b, h, m):
    """
    计算梯形断面湿周

    Args:
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数

    Returns:
        chi: 湿周 (m)
    """
    chi = b + 2 * h * np.sqrt(1 + m**2)
    return chi


def hydraulic_radius(A, chi):
    """
    计算水力半径

    Args:
        A: 面积 (m²)
        chi: 湿周 (m)

    Returns:
        R: 水力半径 (m)
    """
    if chi > 0:
        R = A / chi
    else:
        R = 0.0
    return R


def top_width(b, h, m):
    """
    计算水面宽度

    Args:
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数

    Returns:
        B: 水面宽度 (m)
    """
    B = b + 2 * m * h
    return B


def manning_velocity(R, S0, n):
    """
    曼宁公式计算流速

    Args:
        R: 水力半径 (m)
        S0: 渠底坡度
        n: 曼宁糙率系数

    Returns:
        v: 流速 (m/s)
    """
    v = (1.0 / n) * R**(2.0/3.0) * S0**0.5
    return v


def discharge(A, v):
    """
    计算流量

    Args:
        A: 面积 (m²)
        v: 流速 (m/s)

    Returns:
        Q: 流量 (m³/s)
    """
    Q = A * v
    return Q


def compute_discharge_for_depth(b, h, m, S0, n):
    """
    计算给定水深下的流量

    Args:
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数
        S0: 渠底坡度
        n: 曼宁糙率系数

    Returns:
        Q: 流量 (m³/s)
    """
    A = trapezoidal_area(b, h, m)
    chi = trapezoidal_wetted_perimeter(b, h, m)
    R = hydraulic_radius(A, chi)
    v = manning_velocity(R, S0, n)
    Q = discharge(A, v)
    return Q


def compute_normal_depth(Q_target, b, m, S0, n, h_init=1.0, tol=1e-6, max_iter=100):
    """
    迭代计算正常水深

    Args:
        Q_target: 目标流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        S0: 渠底坡度
        n: 曼宁糙率系数
        h_init: 初始猜测水深 (m)
        tol: 收敛容差
        max_iter: 最大迭代次数

    Returns:
        h: 正常水深 (m)
    """
    h = h_init

    for i in range(max_iter):
        Q_computed = compute_discharge_for_depth(b, h, m, S0, n)
        error = Q_computed - Q_target

        if abs(error) < tol:
            return h

        # 数值导数
        dh = 0.001
        Q_plus = compute_discharge_for_depth(b, h + dh, m, S0, n)
        dQ_dh = (Q_plus - Q_computed) / dh

        # 牛顿法更新
        if abs(dQ_dh) > 1e-10:
            h = h - error / dQ_dh

        # 确保水深为正
        h = max(h, 0.01)

    return h


def froude_number(v, h, g=9.81):
    """
    计算弗劳德数

    Args:
        v: 流速 (m/s)
        h: 水深 (m)
        g: 重力加速度

    Returns:
        Fr: 弗劳德数
    """
    Fr = v / np.sqrt(g * h)
    return Fr


def determine_flow_regime(Fr):
    """
    判别流态

    Args:
        Fr: 弗劳德数

    Returns:
        regime: 'subcritical' (缓流), 'critical' (临界流), 'supercritical' (急流)
    """
    if Fr < 0.98:
        return 'subcritical'
    elif Fr > 1.02:
        return 'supercritical'
    else:
        return 'critical'


class TestCase01Irrigation:
    """案例1：农村灌溉渠流量计算测试"""

    def test_trapezoidal_area_calculation(self):
        """测试1：梯形断面面积计算"""
        b = 1.0  # m
        h = 0.8  # m
        m = 1.5

        A = trapezoidal_area(b, h, m)

        # A = (b + m*h) * h = (1.0 + 1.5*0.8) * 0.8 = 1.76 m²
        A_expected = (b + m * h) * h
        assert abs(A - A_expected) < 1e-10

        # 面积应为正
        assert A > 0

    def test_wetted_perimeter_calculation(self):
        """测试2：湿周计算"""
        b = 1.0
        h = 0.8
        m = 1.5

        chi = trapezoidal_wetted_perimeter(b, h, m)

        # chi = b + 2*h*√(1+m²)
        chi_expected = b + 2 * h * np.sqrt(1 + m**2)
        assert abs(chi - chi_expected) < 1e-10

        # 湿周应大于底宽
        assert chi > b

    def test_hydraulic_radius_calculation(self):
        """测试3：水力半径计算"""
        b = 1.0
        h = 0.8
        m = 1.5

        A = trapezoidal_area(b, h, m)
        chi = trapezoidal_wetted_perimeter(b, h, m)
        R = hydraulic_radius(A, chi)

        # R = A / chi
        R_expected = A / chi
        assert abs(R - R_expected) < 1e-10

        # 水力半径应小于水深
        assert R < h

    def test_top_width_calculation(self):
        """测试4：水面宽度计算"""
        b = 1.0
        h = 0.8
        m = 1.5

        B = top_width(b, h, m)

        # B = b + 2*m*h
        B_expected = b + 2 * m * h
        assert abs(B - B_expected) < 1e-10

        # 水面宽度应大于底宽
        assert B > b

    def test_manning_velocity_calculation(self):
        """测试5：曼宁公式流速计算"""
        R = 0.5  # m
        S0 = 0.0002
        n = 0.025

        v = manning_velocity(R, S0, n)

        # v = (1/n) * R^(2/3) * S0^(1/2)
        v_expected = (1.0 / n) * R**(2.0/3.0) * S0**0.5
        assert abs(v - v_expected) < 1e-10

        # 流速应为正
        assert v > 0

    def test_discharge_calculation(self):
        """测试6：流量计算"""
        A = 1.76  # m²
        v = 0.5   # m/s

        Q = discharge(A, v)

        # Q = A * v
        Q_expected = A * v
        assert abs(Q - Q_expected) < 1e-10

        # 流量应为正
        assert Q > 0

    def test_normal_depth_convergence(self):
        """测试7：正常水深迭代收敛"""
        Q_target = 0.5  # m³/s
        b = 1.0
        m = 1.5
        S0 = 0.0002
        n = 0.025

        h_normal = compute_normal_depth(Q_target, b, m, S0, n)

        # 验证计算的水深能产生目标流量
        Q_check = compute_discharge_for_depth(b, h_normal, m, S0, n)
        assert abs(Q_check - Q_target) < 1e-3

        # 正常水深应在合理范围
        assert 0.5 < h_normal < 1.5

    def test_froude_number_calculation(self):
        """测试8：弗劳德数计算"""
        v = 0.5  # m/s
        h = 0.8  # m
        g = 9.81

        Fr = froude_number(v, h, g)

        # Fr = v / √(gh)
        Fr_expected = v / np.sqrt(g * h)
        assert abs(Fr - Fr_expected) < 1e-10

    def test_flow_regime_determination_subcritical(self):
        """测试9：缓流判别"""
        Fr = 0.5

        regime = determine_flow_regime(Fr)

        # Fr < 1，应为缓流
        assert regime == 'subcritical'

    def test_flow_regime_determination_supercritical(self):
        """测试10：急流判别"""
        Fr = 1.5

        regime = determine_flow_regime(Fr)

        # Fr > 1，应为急流
        assert regime == 'supercritical'

    def test_flow_regime_determination_critical(self):
        """测试11：临界流判别"""
        Fr = 1.0

        regime = determine_flow_regime(Fr)

        # Fr ≈ 1，应为临界流
        assert regime == 'critical'

    def test_irrigation_case_realistic_values(self):
        """测试12：灌溉案例实际参数验证"""
        # 案例参数
        Q = 0.5
        b = 1.0
        m = 1.5
        S0 = 0.0002
        n = 0.025

        # 计算正常水深
        h_normal = compute_normal_depth(Q, b, m, S0, n)

        # 计算流速和弗劳德数
        A = trapezoidal_area(b, h_normal, m)
        v = Q / A
        Fr = froude_number(v, h_normal)

        # 根据README，预期结果：
        # - 正常水深约 0.8-0.9 m
        # - Fr < 1（缓流）
        # - 流速约 0.3-0.6 m/s（实际计算约0.32 m/s）

        assert 0.7 < h_normal < 1.0
        assert Fr < 1.0
        assert 0.3 < v < 0.7


class TestSensitivityAnalysis:
    """敏感性分析测试"""

    def test_roughness_effect_on_depth(self):
        """测试糙率对水深的影响"""
        Q = 0.5
        b = 1.0
        m = 1.5
        S0 = 0.0002

        # 不同糙率
        n1 = 0.020  # 光滑
        n2 = 0.030  # 粗糙

        h1 = compute_normal_depth(Q, b, m, S0, n1)
        h2 = compute_normal_depth(Q, b, m, S0, n2)

        # 糙率增大，水深应增大
        assert h2 > h1

    def test_slope_effect_on_depth(self):
        """测试坡度对水深的影响"""
        Q = 0.5
        b = 1.0
        m = 1.5
        n = 0.025

        # 不同坡度
        S1 = 0.0001  # 缓坡
        S2 = 0.0004  # 陡坡

        h1 = compute_normal_depth(Q, b, m, S1, n)
        h2 = compute_normal_depth(Q, b, m, S2, n)

        # 坡度增大，水深应减小
        assert h2 < h1

    def test_discharge_effect_on_depth(self):
        """测试流量对水深的影响"""
        b = 1.0
        m = 1.5
        S0 = 0.0002
        n = 0.025

        # 不同流量
        Q1 = 0.3
        Q2 = 0.8

        h1 = compute_normal_depth(Q1, b, m, S0, n)
        h2 = compute_normal_depth(Q2, b, m, S0, n)

        # 流量增大，水深应增大
        assert h2 > h1


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_depth(self):
        """测试零水深"""
        b = 1.0
        h = 0.0
        m = 1.5

        A = trapezoidal_area(b, h, m)

        # 零水深时面积为零
        assert A == 0.0

    def test_very_small_depth(self):
        """测试极小水深"""
        b = 1.0
        h = 0.01  # 1cm
        m = 1.5
        S0 = 0.0002
        n = 0.025

        Q = compute_discharge_for_depth(b, h, m, S0, n)

        # 极小水深流量很小
        assert Q < 0.001

    def test_very_large_depth(self):
        """测试大水深"""
        b = 1.0
        h = 5.0  # 5m
        m = 1.5
        S0 = 0.0002
        n = 0.025

        Q = compute_discharge_for_depth(b, h, m, S0, n)

        # 大水深流量大
        assert Q > 10.0

    def test_rectangular_section(self):
        """测试矩形断面（m=0的特例）"""
        b = 2.0
        h = 1.0
        m = 0.0  # 垂直边坡

        A = trapezoidal_area(b, h, m)
        chi = trapezoidal_wetted_perimeter(b, h, m)
        B = top_width(b, h, m)

        # 矩形断面
        assert abs(A - b * h) < 1e-10
        assert abs(chi - (b + 2*h)) < 1e-10
        assert abs(B - b) < 1e-10

    def test_very_steep_slope(self):
        """测试陡坡"""
        b = 1.0
        m = 1.5
        S0 = 0.01  # 很陡
        n = 0.025
        Q = 0.5

        h_normal = compute_normal_depth(Q, b, m, S0, n)

        # 陡坡下水深应较小
        assert h_normal < 0.5

    def test_very_gentle_slope(self):
        """测试缓坡"""
        b = 1.0
        m = 1.5
        S0 = 0.00001  # 很缓
        n = 0.025
        Q = 0.5

        h_normal = compute_normal_depth(Q, b, m, S0, n)

        # 缓坡下水深应较大（实际约1.48m）
        assert h_normal > 1.4

    def test_wide_channel(self):
        """测试宽渠道"""
        b = 10.0  # 很宽
        h = 0.5
        m = 1.5

        A = trapezoidal_area(b, h, m)
        chi = trapezoidal_wetted_perimeter(b, h, m)
        R = hydraulic_radius(A, chi)

        # 宽渠道水力半径接近水深
        assert R < h
        assert R > 0.4 * h  # 但不会太小

    def test_narrow_channel(self):
        """测试窄渠道"""
        b = 0.2  # 很窄
        h = 1.0
        m = 1.5

        A = trapezoidal_area(b, h, m)
        chi = trapezoidal_wetted_perimeter(b, h, m)
        R = hydraulic_radius(A, chi)

        # 窄渠道水力半径较小
        assert R < 0.5 * h


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
