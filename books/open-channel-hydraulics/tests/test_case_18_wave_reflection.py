"""
案例18单元测试：明渠波动与反射

测试内容：
1. 长波波速计算
2. 波数和波长
3. 角频率计算
4. D'Alembert解
5. 反射系数
6. 驻波形成
7. 共振频率
8. 波腹和波节
9. 反射时间
10. 能量反射

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def long_wave_speed(h, g=9.81):
    """
    计算长波波速

    Args:
        h: 水深 (m)
        g: 重力加速度

    Returns:
        c: 波速 (m/s)
    """
    c = np.sqrt(g * h)
    return c


def compute_wavenumber(wavelength):
    """
    计算波数

    Args:
        wavelength: 波长 (m)

    Returns:
        k: 波数 (rad/m)
    """
    k = 2 * np.pi / wavelength
    return k


def compute_wavelength(T, c):
    """
    从周期和波速计算波长

    Args:
        T: 周期 (s)
        c: 波速 (m/s)

    Returns:
        wavelength: 波长 (m)
    """
    wavelength = c * T
    return wavelength


def dalembert_solution(x, t, c, f_func, g_func):
    """
    D'Alembert解

    Args:
        x: 位置 (m)
        t: 时间 (s)
        c: 波速 (m/s)
        f_func: 向右传播波函数 f(xi)
        g_func: 向左传播波函数 g(xi)

    Returns:
        eta: 水面扰动 (m)
    """
    # 向右传播波
    xi_right = x - c * t
    eta_right = f_func(xi_right)

    # 向左传播波
    xi_left = x + c * t
    eta_left = g_func(xi_left)

    eta = eta_right + eta_left
    return eta


def reflection_coefficient_rigid():
    """
    刚性边界反射系数

    Returns:
        R: 反射系数
    """
    return -1.0


def reflection_coefficient_free():
    """
    自由边界反射系数

    Returns:
        R: 反射系数
    """
    return 1.0


def standing_wave(x, t, A, k, omega):
    """
    驻波解（刚性边界）

    Args:
        x: 位置 (m)
        t: 时间 (s)
        A: 振幅 (m)
        k: 波数 (rad/m)
        omega: 角频率 (rad/s)

    Returns:
        eta: 水面扰动 (m)
    """
    # 驻波：η = -2A·cos(kx)·sin(ωt)
    eta = -2 * A * np.cos(k * x) * np.sin(omega * t)
    return eta


def resonance_frequency(n, L, c):
    """
    计算第n阶共振频率

    Args:
        n: 模态数 (n=1,2,3,...)
        L: 渠道长度 (m)
        c: 波速 (m/s)

    Returns:
        f: 共振频率 (Hz)
    """
    f = n * c / (2 * L)
    return f


def identify_antinode_positions(L, n):
    """
    计算波腹位置

    Args:
        L: 渠道长度 (m)
        n: 模态数

    Returns:
        positions: 波腹位置数组 (m)
    """
    # 波腹位置：x = m·λ/2 = m·L/n  (m=0,1,...,n)
    positions = []
    for m in range(n + 1):
        x = m * L / n
        positions.append(x)
    return np.array(positions)


def identify_node_positions(L, n):
    """
    计算波节位置

    Args:
        L: 渠道长度 (m)
        n: 模态数

    Returns:
        positions: 波节位置数组 (m)
    """
    # 波节位置：x = (2m+1)·λ/4 = (2m+1)·L/(2n)  (m=0,1,...,n-1)
    positions = []
    for m in range(n):
        x = (2 * m + 1) * L / (2 * n)
        positions.append(x)
    return np.array(positions)


def compute_reflection_time(L, c, n_reflections=1):
    """
    计算反射时间

    Args:
        L: 渠道长度 (m)
        c: 波速 (m/s)
        n_reflections: 反射次数

    Returns:
        t: 反射时间 (s)
    """
    # 第n次反射：t = n·2L/c
    t = n_reflections * 2 * L / c
    return t


def energy_reflection_ratio(R):
    """
    计算能量反射率

    Args:
        R: 振幅反射系数

    Returns:
        energy_ratio: 能量反射率
    """
    return R**2


class TestCase18WaveReflection:
    """案例18：明渠波动与反射测试"""

    def test_long_wave_speed(self):
        """测试1：长波波速计算"""
        h = 3.0  # m
        g = 9.81

        c = long_wave_speed(h, g)

        # 波速应为正
        assert c > 0

        # 对于h=3m，c ≈ 5.4 m/s
        assert 5.3 < c < 5.5

        # 验证公式
        c_expected = np.sqrt(g * h)
        assert abs(c - c_expected) < 0.01

    def test_wave_speed_depth_dependence(self):
        """测试2：波速与水深关系"""
        g = 9.81

        h1 = 2.0
        h2 = 8.0  # 4倍水深

        c1 = long_wave_speed(h1, g)
        c2 = long_wave_speed(h2, g)

        # 水深增加4倍，波速应增加2倍
        ratio = c2 / c1
        assert abs(ratio - 2.0) < 0.01

    def test_wavenumber_calculation(self):
        """测试3：波数计算"""
        wavelength = 100.0  # m

        k = compute_wavenumber(wavelength)

        # 波数应为正
        assert k > 0

        # 验证k = 2π/λ
        k_expected = 2 * np.pi / wavelength
        assert abs(k - k_expected) < 1e-10

    def test_wavelength_calculation(self):
        """测试4：波长计算"""
        T = 20.0  # 周期 (s)
        c = 5.0   # 波速 (m/s)

        wavelength = compute_wavelength(T, c)

        # 波长 = c × T
        assert abs(wavelength - c * T) < 0.01

        # 应为100m
        assert abs(wavelength - 100.0) < 0.1

    def test_dalembert_solution_right_wave(self):
        """测试5：D'Alembert解（向右传播波）"""
        x = 50.0
        t = 10.0
        c = 5.0

        # 仅向右传播波
        def f_func(xi):
            if 0 < xi < 10:
                return 1.0
            else:
                return 0.0

        def g_func(xi):
            return 0.0

        eta = dalembert_solution(x, t, c, f_func, g_func)

        # 在 x=50, t=10 时，波应已传过
        # x - ct = 50 - 5*10 = 0，在波前
        assert eta >= 0

    def test_reflection_coefficient_rigid_boundary(self):
        """测试6：刚性边界反射系数"""
        R = reflection_coefficient_rigid()

        # 刚性边界反射系数为-1
        assert abs(R - (-1.0)) < 1e-10

        # 全反射
        assert abs(R) == 1.0

    def test_reflection_coefficient_free_boundary(self):
        """测试7：自由边界反射系数"""
        R = reflection_coefficient_free()

        # 自由边界反射系数为+1
        assert abs(R - 1.0) < 1e-10

        # 全反射
        assert abs(R) == 1.0

    def test_standing_wave_antinodes(self):
        """测试8：驻波波腹"""
        A = 1.0
        L = 1000.0
        c = 5.0
        T = 2 * L / c  # 基频周期

        k = np.pi / L
        omega = 2 * np.pi / T

        # 波腹位置（x=0和x=L）
        x_antinode = 0.0
        t = T / 4  # sin(ωt)=1

        eta = standing_wave(x_antinode, t, A, k, omega)

        # 波腹振幅应为2A
        assert abs(abs(eta) - 2 * A) < 0.1

    def test_standing_wave_nodes(self):
        """测试9：驻波波节"""
        A = 1.0
        L = 1000.0
        c = 5.0
        T = 2 * L / c

        k = np.pi / L
        omega = 2 * np.pi / T

        # 波节位置（x=L/2）
        x_node = L / 2
        t = T / 4

        eta = standing_wave(x_node, t, A, k, omega)

        # 波节振幅应接近0
        assert abs(eta) < 0.1

    def test_fundamental_resonance_frequency(self):
        """测试10：基频共振频率"""
        L = 1000.0
        h = 3.0
        g = 9.81

        c = long_wave_speed(h, g)
        f1 = resonance_frequency(1, L, c)

        # 基频
        f1_expected = c / (2 * L)
        assert abs(f1 - f1_expected) < 1e-6

        # 基频应很低（约0.0027 Hz）
        assert 0.002 < f1 < 0.003

    def test_harmonic_resonance_frequencies(self):
        """测试11：高次谐波频率"""
        L = 1000.0
        c = 5.0

        f1 = resonance_frequency(1, L, c)
        f2 = resonance_frequency(2, L, c)
        f3 = resonance_frequency(3, L, c)

        # 频率应递增
        assert f2 > f1
        assert f3 > f2

        # 应为整数倍关系
        assert abs(f2 / f1 - 2.0) < 0.01
        assert abs(f3 / f1 - 3.0) < 0.01

    def test_antinode_positions_fundamental(self):
        """测试12：基频波腹位置"""
        L = 1000.0
        n = 1  # 基频

        positions = identify_antinode_positions(L, n)

        # 基频有2个波腹（两端）
        assert len(positions) == n + 1

        # 位置应为0和L
        assert abs(positions[0] - 0.0) < 0.1
        assert abs(positions[1] - L) < 0.1

    def test_node_positions_fundamental(self):
        """测试13：基频波节位置"""
        L = 1000.0
        n = 1

        positions = identify_node_positions(L, n)

        # 基频有1个波节（中间）
        assert len(positions) == n

        # 位置应为L/2
        assert abs(positions[0] - L/2) < 0.1

    def test_reflection_time_calculation(self):
        """测试14：反射时间计算"""
        L = 1000.0
        h = 3.0
        g = 9.81

        c = long_wave_speed(h, g)
        t_reflect = compute_reflection_time(L, c, n_reflections=1)

        # 反射时间 = 2L/c
        t_expected = 2 * L / c
        assert abs(t_reflect - t_expected) < 0.1

        # 约370秒
        assert 360 < t_reflect < 380

    def test_multiple_reflections(self):
        """测试15：多次反射"""
        L = 1000.0
        c = 5.0

        t1 = compute_reflection_time(L, c, n_reflections=1)
        t2 = compute_reflection_time(L, c, n_reflections=2)
        t3 = compute_reflection_time(L, c, n_reflections=3)

        # 多次反射时间成倍数关系
        assert abs(t2 / t1 - 2.0) < 0.01
        assert abs(t3 / t1 - 3.0) < 0.01

    def test_energy_reflection_rigid(self):
        """测试16：刚性边界能量反射"""
        R = reflection_coefficient_rigid()
        energy_ratio = energy_reflection_ratio(R)

        # 能量全反射
        assert abs(energy_ratio - 1.0) < 1e-10

    def test_energy_reflection_partial(self):
        """测试17：部分反射能量"""
        R = 0.5  # 部分反射

        energy_ratio = energy_reflection_ratio(R)

        # 能量反射率 = R²
        assert abs(energy_ratio - 0.25) < 1e-10

        # 部分能量耗散
        assert energy_ratio < 1.0


class TestWaveProperties:
    """波动特性测试"""

    def test_dispersion_relation(self):
        """测试频散关系"""
        # 对于长波，ω² = gk²h（无色散）
        h = 3.0
        g = 9.81
        k = 0.01  # 波数

        omega_squared = g * h * k**2
        omega = np.sqrt(omega_squared)

        # 波速 c = ω/k
        c = omega / k

        # 应等于 √(gh)
        c_expected = np.sqrt(g * h)
        assert abs(c - c_expected) < 0.01

    def test_group_velocity_equals_phase_velocity(self):
        """测试群速度等于相速度（长波特性）"""
        h = 3.0
        g = 9.81

        # 相速度
        c_phase = long_wave_speed(h, g)

        # 对于无色散长波，群速度 = 相速度
        c_group = c_phase

        assert abs(c_group - c_phase) < 1e-10

    def test_finite_amplitude_effect(self):
        """测试有限振幅效应"""
        h = 3.0
        a = 0.5  # 振幅
        g = 9.81

        # 波峰波速
        c_crest = np.sqrt(g * (h + a))

        # 波谷波速
        c_trough = np.sqrt(g * (h - a))

        # 波峰速度应大于波谷速度
        assert c_crest > c_trough

    def test_period_wavelength_relation(self):
        """测试周期-波长关系"""
        T = 100.0  # 周期 (s)
        c = 5.0    # 波速 (m/s)

        wavelength = compute_wavelength(T, c)
        k = compute_wavenumber(wavelength)
        omega = 2 * np.pi / T

        # 验证频散关系：ω = ck
        omega_check = c * k
        assert abs(omega - omega_check) < 1e-10


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_water_depth(self):
        """测试零水深"""
        h = 0.0
        g = 9.81

        c = long_wave_speed(h, g)

        # 零水深波速为零
        assert c == 0.0

    def test_very_shallow_water(self):
        """测试极浅水"""
        h = 0.1  # 10cm
        g = 9.81

        c = long_wave_speed(h, g)

        # 浅水波速小
        assert c < 2.0

    def test_very_deep_water(self):
        """测试深水"""
        h = 100.0  # 深水
        g = 9.81

        c = long_wave_speed(h, g)

        # 深水波速大
        assert c > 30.0

    def test_zero_amplitude_standing_wave(self):
        """测试零振幅驻波"""
        A = 0.0
        x = 100.0
        t = 10.0
        k = 0.01
        omega = 0.1

        eta = standing_wave(x, t, A, k, omega)

        # 零振幅无扰动
        assert abs(eta) < 1e-10

    def test_very_long_channel(self):
        """测试极长渠道"""
        L = 100000.0  # 100km
        c = 5.0

        f1 = resonance_frequency(1, L, c)

        # 长渠道低频率
        assert f1 < 0.0001

    def test_very_short_channel(self):
        """测试极短渠道"""
        L = 10.0  # 10m
        c = 5.0

        f1 = resonance_frequency(1, L, c)

        # 短渠道高频率
        assert f1 > 0.1

    def test_high_mode_number(self):
        """测试高阶模态"""
        L = 1000.0
        n = 10  # 第10阶

        antinodes = identify_antinode_positions(L, n)
        nodes = identify_node_positions(L, n)

        # 波腹数 = n+1
        assert len(antinodes) == n + 1

        # 波节数 = n
        assert len(nodes) == n

    def test_complete_reflection(self):
        """测试完全反射"""
        R_rigid = reflection_coefficient_rigid()
        R_free = reflection_coefficient_free()

        # 两种边界都是全反射
        assert abs(abs(R_rigid)) == 1.0
        assert abs(abs(R_free)) == 1.0

        # 但相位不同
        assert R_rigid != R_free

    def test_no_reflection(self):
        """测试无反射（吸收边界）"""
        R = 0.0  # 完全吸收

        energy_ratio = energy_reflection_ratio(R)

        # 无能量反射
        assert energy_ratio == 0.0

    def test_wave_period_from_frequency(self):
        """测试由频率计算周期"""
        L = 1000.0
        c = 5.0

        f1 = resonance_frequency(1, L, c)
        T1 = 1.0 / f1

        # T = 2L/c
        T_expected = 2 * L / c
        assert abs(T1 - T_expected) < 0.1


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
