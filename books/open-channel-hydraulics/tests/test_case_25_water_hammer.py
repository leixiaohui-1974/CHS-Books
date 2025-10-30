"""
案例25单元测试：水锤基础

测试内容：
1. 压力波速计算（刚性管与弹性管）
2. Joukowsky公式（水锤压力升高）
3. 临界时间计算
4. 快速/缓慢关闭判别
5. 最大压力计算
6. 管道安全性校核
7. 关闭时间影响
8. 边界条件测试

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def wave_speed_rigid_pipe(K, rho):
    """刚性管道中的压力波速 [m/s]
    a = √(K/ρ)
    """
    a = np.sqrt(K / rho)
    return a


def wave_speed_elastic_pipe(K, rho, E, D, e):
    """弹性管道中的压力波速 [m/s]
    a = √(K/ρ) / √(1 + K*D/(E*e))
    """
    a_rigid = np.sqrt(K / rho)
    correction = np.sqrt(1 + (K * D) / (E * e))
    a = a_rigid / correction
    return a


def joukowsky_pressure_rise(rho, a, delta_v):
    """Joukowsky公式：水锤压力升高 [Pa]
    ΔP = ρ * a * Δv
    """
    delta_P = rho * a * delta_v
    return delta_P


def joukowsky_head_rise(a, delta_v, g=9.81):
    """Joukowsky公式：水锤水头升高 [m]
    ΔH = (a/g) * Δv
    """
    delta_H = (a / g) * delta_v
    return delta_H


def critical_time(L, a):
    """临界时间（相时间）[s]
    T_c = 2L/a
    """
    T_c = 2 * L / a
    return T_c


def is_rapid_closure(t_c, T_c):
    """判别是否快速关闭
    快速关闭：t_c ≤ T_c
    """
    return t_c <= T_c


def max_pressure_rapid_closure(p0, rho, a, v0):
    """快速关闭最大压力 [Pa]
    p_max = p₀ + ρ*a*v₀
    """
    p_max = p0 + rho * a * v0
    return p_max


def max_head_rapid_closure(H0, a, v0, g=9.81):
    """快速关闭最大水头 [m]
    H_max = H₀ + (a/g)*v₀
    """
    H_max = H0 + (a / g) * v0
    return H_max


def max_pressure_slow_closure(p0, rho, a, v0, T_c, t_c):
    """缓慢关闭最大压力 [Pa]
    p_max = p₀ + ρ*a*v₀*(T_c/t_c)
    """
    p_max = p0 + rho * a * v0 * (T_c / t_c)
    return p_max


def max_head_slow_closure(H0, a, v0, T_c, t_c, g=9.81):
    """缓慢关闭最大水头 [m]
    H_max = H₀ + (a/g)*v₀*(T_c/t_c)
    """
    H_max = H0 + (a / g) * v0 * (T_c / t_c)
    return H_max


def allowable_pressure(sigma_s, e, D, n_s):
    """管道许用压力 [Pa]
    [p] = 2*σ_s*e / (D*n_s)
    """
    p_allow = 2 * sigma_s * e / (D * n_s)
    return p_allow


def check_pipe_safety(p_max, p_allow):
    """管道安全性校核
    安全条件：p_max ≤ [p]
    """
    return p_max <= p_allow


def reduction_factor(T_c, t_c):
    """缓慢关闭水锤降低系数
    当t_c > T_c时，水锤压力降低
    """
    if t_c <= T_c:
        return 1.0
    else:
        return T_c / t_c


class TestCase25WaterHammer:
    """案例25：水锤基础测试"""

    def test_wave_speed_rigid_pipe(self):
        """测试1：刚性管道波速"""
        K = 2.1e9  # Pa (水的体积模量)
        rho = 1000  # kg/m³

        a = wave_speed_rigid_pipe(K, rho)

        # a = √(2.1e9/1000) = √(2.1e6) ≈ 1449 m/s
        a_expected = np.sqrt(K / rho)
        assert abs(a - a_expected) < 1e-6

        # 应在合理范围
        assert 1400 < a < 1500

    def test_wave_speed_elastic_pipe_steel(self):
        """测试2：钢管波速"""
        K = 2.1e9  # Pa
        rho = 1000  # kg/m³
        E = 200e9  # Pa (钢的弹性模量)
        D = 0.5  # m
        e = 0.01  # m (壁厚)

        a = wave_speed_elastic_pipe(K, rho, E, D, e)

        # 钢管波速应低于刚性管（900~1200 m/s）
        assert 900 < a < 1200

    def test_wave_speed_elastic_pipe_plastic(self):
        """测试3：塑料管波速"""
        K = 2.1e9  # Pa
        rho = 1000  # kg/m³
        E = 3e9  # Pa (塑料弹性模量较小)
        D = 0.5  # m
        e = 0.015  # m

        a = wave_speed_elastic_pipe(K, rho, E, D, e)

        # 塑料管波速更低（200~500 m/s）
        assert 200 < a < 600

    def test_joukowsky_pressure_rise(self):
        """测试4：Joukowsky公式（压力）"""
        rho = 1000  # kg/m³
        a = 1000  # m/s
        delta_v = 2.0  # m/s

        delta_P = joukowsky_pressure_rise(rho, a, delta_v)

        # ΔP = 1000 * 1000 * 2.0 = 2,000,000 Pa = 2.0 MPa
        assert abs(delta_P - 2.0e6) < 1e-6

    def test_joukowsky_head_rise(self):
        """测试5：Joukowsky公式（水头）"""
        a = 1000  # m/s
        delta_v = 2.0  # m/s
        g = 9.81

        delta_H = joukowsky_head_rise(a, delta_v, g)

        # ΔH = 1000*2.0/9.81 ≈ 203.9 m
        assert abs(delta_H - 203.9) < 0.5

    def test_critical_time_calculation(self):
        """测试6：临界时间计算"""
        L = 1000  # m
        a = 1000  # m/s

        T_c = critical_time(L, a)

        # T_c = 2*1000/1000 = 2.0 s
        assert abs(T_c - 2.0) < 1e-6

    def test_rapid_closure_determination(self):
        """测试7：快速关闭判别"""
        T_c = 2.0  # s

        # 快速关闭
        assert is_rapid_closure(1.0, T_c) == True
        assert is_rapid_closure(2.0, T_c) == True

        # 缓慢关闭
        assert is_rapid_closure(3.0, T_c) == False
        assert is_rapid_closure(5.0, T_c) == False

    def test_max_pressure_rapid_closure(self):
        """测试8：快速关闭最大压力"""
        p0 = 0.5e6  # Pa (初始压力)
        rho = 1000
        a = 1000
        v0 = 2.0

        p_max = max_pressure_rapid_closure(p0, rho, a, v0)

        # p_max = 0.5e6 + 1000*1000*2.0 = 2.5e6 Pa = 2.5 MPa
        assert abs(p_max - 2.5e6) < 1e-6

    def test_max_head_rapid_closure(self):
        """测试9：快速关闭最大水头"""
        H0 = 50  # m
        a = 1000
        v0 = 2.0

        H_max = max_head_rapid_closure(H0, a, v0)

        # H_max = 50 + 1000*2.0/9.81 ≈ 253.9 m
        assert abs(H_max - 253.9) < 0.5

    def test_max_pressure_slow_closure(self):
        """测试10：缓慢关闭最大压力"""
        p0 = 0.5e6
        rho = 1000
        a = 1000
        v0 = 2.0
        T_c = 2.0
        t_c = 5.0  # 缓慢关闭

        p_max = max_pressure_slow_closure(p0, rho, a, v0, T_c, t_c)

        # p_max = 0.5e6 + 1000*1000*2.0*(2.0/5.0) = 1.3e6 Pa
        delta_P_rapid = rho * a * v0
        delta_P_slow = delta_P_rapid * (T_c / t_c)
        p_max_expected = p0 + delta_P_slow
        assert abs(p_max - p_max_expected) < 1e-6

    def test_max_head_slow_closure(self):
        """测试11：缓慢关闭最大水头"""
        H0 = 50
        a = 1000
        v0 = 2.0
        T_c = 2.0
        t_c = 5.0

        H_max = max_head_slow_closure(H0, a, v0, T_c, t_c)

        # H_max = 50 + (1000*2.0/9.81)*(2.0/5.0) ≈ 131.6 m
        delta_H_rapid = (a / 9.81) * v0
        delta_H_slow = delta_H_rapid * (T_c / t_c)
        H_max_expected = H0 + delta_H_slow
        assert abs(H_max - H_max_expected) < 0.5

    def test_allowable_pressure_calculation(self):
        """测试12：许用压力计算"""
        sigma_s = 140e6  # Pa (钢管许用应力)
        e = 0.01  # m
        D = 0.5  # m
        n_s = 2.5  # 安全系数

        p_allow = allowable_pressure(sigma_s, e, D, n_s)

        # [p] = 2*140e6*0.01 / (0.5*2.5) = 2.24e6 Pa
        p_allow_expected = 2 * sigma_s * e / (D * n_s)
        assert abs(p_allow - p_allow_expected) < 1e-6

    def test_pipe_safety_check_safe(self):
        """测试13：管道安全（满足要求）"""
        p_max = 2.0e6  # Pa
        p_allow = 2.5e6  # Pa

        is_safe = check_pipe_safety(p_max, p_allow)

        # p_max < [p]，安全
        assert is_safe == True

    def test_pipe_safety_check_unsafe(self):
        """测试14：管道不安全（不满足要求）"""
        p_max = 3.0e6  # Pa
        p_allow = 2.5e6  # Pa

        is_safe = check_pipe_safety(p_max, p_allow)

        # p_max > [p]，不安全
        assert is_safe == False

    def test_reduction_factor_rapid(self):
        """测试15：快速关闭降低系数"""
        T_c = 2.0
        t_c = 1.0  # 快速关闭

        factor = reduction_factor(T_c, t_c)

        # 快速关闭：系数为1.0
        assert factor == 1.0

    def test_reduction_factor_slow(self):
        """测试16：缓慢关闭降低系数"""
        T_c = 2.0
        t_c = 5.0  # 缓慢关闭

        factor = reduction_factor(T_c, t_c)

        # 缓慢关闭：系数为T_c/t_c = 2.0/5.0 = 0.4
        assert abs(factor - 0.4) < 1e-6

    def test_case_study_rapid_closure(self):
        """测试17：案例工况（快速关闭）"""
        # 案例参数
        L = 1000  # m
        D = 0.5  # m
        e = 0.01  # m
        v0 = 2.0  # m/s
        p0 = 0.5e6  # Pa
        H0 = 50  # m
        rho = 1000
        K = 2.1e9
        E = 200e9

        # 计算波速
        a = wave_speed_elastic_pipe(K, rho, E, D, e)

        # 计算临界时间
        T_c = critical_time(L, a)

        # 瞬时关闭（t_c = 0）
        t_c = 0.0

        # 判别为快速关闭
        assert is_rapid_closure(t_c, T_c) == True

        # 计算最大压力
        p_max = max_pressure_rapid_closure(p0, rho, a, v0)

        # 应有显著压力升高
        assert p_max > p0

    def test_case_study_slow_closure(self):
        """测试18：案例工况（缓慢关闭）"""
        L = 1000
        D = 0.5
        e = 0.01
        v0 = 2.0
        p0 = 0.5e6
        rho = 1000
        K = 2.1e9
        E = 200e9

        a = wave_speed_elastic_pipe(K, rho, E, D, e)
        T_c = critical_time(L, a)

        # 缓慢关闭（t_c = 5.0 s）
        t_c = 5.0

        # 判别为缓慢关闭
        assert is_rapid_closure(t_c, T_c) == False

        # 计算最大压力
        p_max = max_pressure_slow_closure(p0, rho, a, v0, T_c, t_c)

        # 缓慢关闭压力升高应小于快速关闭
        p_max_rapid = max_pressure_rapid_closure(p0, rho, a, v0)
        assert p_max < p_max_rapid

    def test_closure_time_effect(self):
        """测试19：关闭时间对最大压力的影响"""
        p0 = 0.5e6
        rho = 1000
        a = 1000
        v0 = 2.0
        T_c = 2.0

        closure_times = [0.5, 1.0, 2.0, 5.0, 10.0]
        p_max_values = []

        for t_c in closure_times:
            if is_rapid_closure(t_c, T_c):
                p_max = max_pressure_rapid_closure(p0, rho, a, v0)
            else:
                p_max = max_pressure_slow_closure(p0, rho, a, v0, T_c, t_c)
            p_max_values.append(p_max)

        # 关闭时间越长，最大压力越小（单调递减）
        for i in range(len(p_max_values) - 1):
            if closure_times[i] > T_c and closure_times[i+1] > T_c:
                assert p_max_values[i] >= p_max_values[i+1]

    def test_velocity_effect_on_water_hammer(self):
        """测试20：初始流速对水锤的影响"""
        rho = 1000
        a = 1000

        v0_low = 1.0  # m/s
        v0_high = 3.0  # m/s

        delta_P_low = joukowsky_pressure_rise(rho, a, v0_low)
        delta_P_high = joukowsky_pressure_rise(rho, a, v0_high)

        # 流速越大，水锤压力越大
        assert delta_P_high > delta_P_low

        # ΔP与v成正比
        ratio = delta_P_high / delta_P_low
        ratio_expected = v0_high / v0_low
        assert abs(ratio - ratio_expected) < 0.01

    def test_wave_speed_effect_on_water_hammer(self):
        """测试21：波速对水锤的影响"""
        rho = 1000
        delta_v = 2.0

        a_steel = 1000  # m/s (钢管)
        a_plastic = 300  # m/s (塑料管)

        delta_P_steel = joukowsky_pressure_rise(rho, a_steel, delta_v)
        delta_P_plastic = joukowsky_pressure_rise(rho, a_plastic, delta_v)

        # 波速越大，水锤压力越大
        assert delta_P_steel > delta_P_plastic

    def test_pipe_elasticity_reduces_wave_speed(self):
        """测试22：管道弹性降低波速"""
        K = 2.1e9
        rho = 1000
        D = 0.5
        e = 0.01

        # 刚性管
        a_rigid = wave_speed_rigid_pipe(K, rho)

        # 钢管（E大）
        E_steel = 200e9
        a_steel = wave_speed_elastic_pipe(K, rho, E_steel, D, e)

        # 塑料管（E小）
        E_plastic = 3e9
        a_plastic = wave_speed_elastic_pipe(K, rho, E_plastic, D, e)

        # a_rigid > a_steel > a_plastic
        assert a_rigid > a_steel > a_plastic

    def test_wall_thickness_effect(self):
        """测试23：壁厚对波速的影响"""
        K = 2.1e9
        rho = 1000
        E = 200e9
        D = 0.5

        e_thin = 0.005  # m (薄壁)
        e_thick = 0.02  # m (厚壁)

        a_thin = wave_speed_elastic_pipe(K, rho, E, D, e_thin)
        a_thick = wave_speed_elastic_pipe(K, rho, E, D, e_thick)

        # 壁厚越大，波速越大（管道越刚性）
        assert a_thick > a_thin

    def test_pressure_rise_proportional_to_velocity_change(self):
        """测试24：压力升高与流速变化成正比"""
        rho = 1000
        a = 1000

        delta_v1 = 1.0
        delta_v2 = 3.0

        delta_P1 = joukowsky_pressure_rise(rho, a, delta_v1)
        delta_P2 = joukowsky_pressure_rise(rho, a, delta_v2)

        ratio = delta_P2 / delta_P1
        ratio_expected = delta_v2 / delta_v1
        assert abs(ratio - ratio_expected) < 1e-6

    def test_critical_time_inversely_proportional_to_wave_speed(self):
        """测试25：临界时间与波速成反比"""
        L = 1000

        a1 = 1000
        a2 = 500

        T_c1 = critical_time(L, a1)
        T_c2 = critical_time(L, a2)

        # T_c ∝ 1/a
        ratio = T_c2 / T_c1
        ratio_expected = a1 / a2
        assert abs(ratio - ratio_expected) < 1e-6


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_velocity_change(self):
        """测试1：零流速变化（无水锤）"""
        rho = 1000
        a = 1000
        delta_v = 0.0

        delta_P = joukowsky_pressure_rise(rho, a, delta_v)

        # 无流速变化，无水锤
        assert delta_P == 0.0

    def test_very_slow_closure(self):
        """测试2：极缓慢关闭"""
        T_c = 2.0
        t_c = 100.0  # 极缓慢

        factor = reduction_factor(T_c, t_c)

        # 降低系数很小
        assert factor < 0.1

    def test_instantaneous_closure(self):
        """测试3：瞬时关闭"""
        T_c = 2.0
        t_c = 0.0  # 瞬时

        is_rapid = is_rapid_closure(t_c, T_c)

        # 瞬时关闭为快速关闭
        assert is_rapid == True

    def test_very_long_pipe(self):
        """测试4：极长管道"""
        L = 100000  # m (100 km)
        a = 1000

        T_c = critical_time(L, a)

        # 临界时间很长
        assert T_c > 100  # 超过100秒

    def test_very_short_pipe(self):
        """测试5：极短管道"""
        L = 10  # m
        a = 1000

        T_c = critical_time(L, a)

        # 临界时间很短
        assert T_c < 0.1  # 小于0.1秒


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
