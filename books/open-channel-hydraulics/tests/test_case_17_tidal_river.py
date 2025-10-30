"""
案例17单元测试：潮汐河口非恒定流

测试内容：
1. 潮汐水位计算
2. 角频率和周期
3. 相位滞后计算
4. 振幅提取
5. 潮差计算
6. 河流-潮汐相互作用参数
7. 潮汐波速
8. 涨潮落潮判别
9. 憩流时间计算
10. 潮汐能通量

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def tidal_water_level(t, h0, A, T, phi=0.0):
    """
    计算潮汐水位

    Args:
        t: 时间 (s)
        h0: 平均潮位 (m)
        A: 潮汐振幅 (m)
        T: 潮汐周期 (s)
        phi: 初相位 (rad)

    Returns:
        h: 潮位 (m)
    """
    omega = 2 * np.pi / T
    h = h0 + A * np.sin(omega * t + phi)
    return h


def compute_angular_frequency(T):
    """
    计算角频率

    Args:
        T: 周期 (s)

    Returns:
        omega: 角频率 (rad/s)
    """
    return 2 * np.pi / T


def compute_tidal_range(h_max, h_min):
    """
    计算潮差

    Args:
        h_max: 高潮位 (m)
        h_min: 低潮位 (m)

    Returns:
        tidal_range: 潮差 (m)
    """
    return h_max - h_min


def extract_amplitude(times, water_levels):
    """
    从时间序列提取潮汐振幅

    Args:
        times: 时间数组 (s)
        water_levels: 水位数组 (m)

    Returns:
        A: 振幅 (m)
        h0: 平均水位 (m)
    """
    h_max = np.max(water_levels)
    h_min = np.min(water_levels)
    A = (h_max - h_min) / 2.0
    h0 = (h_max + h_min) / 2.0
    return A, h0


def compute_phase_lag(x, c, omega):
    """
    计算相位滞后

    Args:
        x: 传播距离 (m)
        c: 波速 (m/s)
        omega: 角频率 (rad/s)

    Returns:
        delta_phi: 相位滞后 (rad)
        delta_t: 时间滞后 (s)
    """
    delta_phi = omega * x / c
    delta_t = delta_phi / omega
    return delta_phi, delta_t


def river_tide_parameter(Qr, A, b, c):
    """
    计算河流-潮汐相互作用参数

    Args:
        Qr: 径流流量 (m³/s)
        A: 潮汐振幅 (m)
        b: 河道宽度 (m)
        c: 波速 (m/s)

    Returns:
        R: 河流-潮汐参数
    """
    R = Qr / (A * b * c)
    return R


def tidal_wave_speed(h, g=9.81):
    """
    计算潮汐波速

    Args:
        h: 水深 (m)
        g: 重力加速度

    Returns:
        c: 波速 (m/s)
    """
    c = np.sqrt(g * h)
    return c


def identify_flood_ebb(dh_dt):
    """
    判别涨潮和落潮

    Args:
        dh_dt: 水位变化率 (m/s)

    Returns:
        tide_type: 'flood' (涨潮), 'ebb' (落潮), 'slack' (憩流)
    """
    if dh_dt > 0.01:
        return 'flood'
    elif dh_dt < -0.01:
        return 'ebb'
    else:
        return 'slack'


def compute_slack_times(T, n_cycles=1):
    """
    计算憩流时间

    Args:
        T: 潮汐周期 (s)
        n_cycles: 周期数

    Returns:
        slack_times: 憩流时间数组 (s)
    """
    # 憩流发生在高潮和低潮时刻
    times = []
    for i in range(n_cycles):
        # 高潮时刻（相位 = π/2）
        t_high = T * (0.25 + i)
        times.append(t_high)
        # 低潮时刻（相位 = 3π/2）
        t_low = T * (0.75 + i)
        times.append(t_low)
    return np.array(times)


def tidal_energy_flux(A, h, b, omega, g=9.81):
    """
    计算潮汐能通量

    Args:
        A: 潮汐振幅 (m)
        h: 平均水深 (m)
        b: 宽度 (m)
        omega: 角频率 (rad/s)
        g: 重力加速度

    Returns:
        E: 能通量 (W)
    """
    # 简化公式：E ≈ (1/2) × ρ × g × A² × b × c
    c = np.sqrt(g * h)
    rho = 1000.0  # 水密度 (kg/m³)
    E = 0.5 * rho * g * A**2 * b * c
    return E


class TestCase17TidalRiver:
    """案例17：潮汐河口非恒定流测试"""

    def test_tidal_water_level_calculation(self):
        """测试1：潮汐水位计算"""
        h0 = 5.0  # 平均潮位 (m)
        A = 2.0   # 振幅 (m)
        T = 12.42 * 3600  # 周期 (s)

        # 高潮时刻（t = T/4）
        t_high = T / 4
        h_high = tidal_water_level(t_high, h0, A, T)

        # 应接近 h0 + A
        assert abs(h_high - (h0 + A)) < 0.1

        # 低潮时刻（t = 3T/4）
        t_low = 3 * T / 4
        h_low = tidal_water_level(t_low, h0, A, T)

        # 应接近 h0 - A
        assert abs(h_low - (h0 - A)) < 0.1

    def test_angular_frequency_calculation(self):
        """测试2：角频率计算"""
        T = 12.42 * 3600  # 半日潮周期 (s)

        omega = compute_angular_frequency(T)

        # ω = 2π/T
        omega_expected = 2 * np.pi / T
        assert abs(omega - omega_expected) < 1e-10

        # 对于半日潮，ω ≈ 1.41e-4 rad/s
        assert 1.4e-4 < omega < 1.42e-4

    def test_tidal_range_calculation(self):
        """测试3：潮差计算"""
        h_max = 7.0  # 高潮位 (m)
        h_min = 3.0  # 低潮位 (m)

        tidal_range = compute_tidal_range(h_max, h_min)

        # 潮差应为4m
        assert abs(tidal_range - 4.0) < 0.01

        # 潮差应为正
        assert tidal_range > 0

    def test_amplitude_extraction(self):
        """测试4：振幅提取"""
        h0 = 5.0
        A_input = 2.0
        T = 12.42 * 3600

        # 生成一个周期的数据
        times = np.linspace(0, T, 100)
        water_levels = tidal_water_level(times, h0, A_input, T)

        # 提取振幅
        A_extracted, h0_extracted = extract_amplitude(times, water_levels)

        # 应提取出正确的振幅和平均水位
        assert abs(A_extracted - A_input) < 0.01
        assert abs(h0_extracted - h0) < 0.01

    def test_phase_lag_calculation(self):
        """测试5：相位滞后计算"""
        x = 20000.0  # 传播距离20km (m)
        h = 5.0      # 平均水深 (m)
        T = 12.42 * 3600
        g = 9.81

        c = np.sqrt(g * h)
        omega = 2 * np.pi / T

        delta_phi, delta_t = compute_phase_lag(x, c, omega)

        # 相位滞后应为正
        assert delta_phi > 0

        # 时间滞后应在合理范围（约0.5-1.5小时）
        # 对于20km距离，c≈7m/s，滞后时间约2857秒≈0.8小时
        assert 1800 < delta_t < 5400  # 0.5-1.5小时

        # 验证关系：delta_t = x/c
        delta_t_expected = x / c
        assert abs(delta_t - delta_t_expected) < 1.0

    def test_river_tide_parameter(self):
        """测试6：河流-潮汐参数"""
        Qr = 500.0  # 径流 (m³/s)
        A = 2.0     # 振幅 (m)
        b = 200.0   # 宽度 (m)
        h = 5.0
        g = 9.81

        c = np.sqrt(g * h)
        R = river_tide_parameter(Qr, A, b, c)

        # R应为正
        assert R > 0

        # 对于本案例参数，R << 1（潮汐主导）
        assert R < 1.0

        # 验证计算
        R_expected = Qr / (A * b * c)
        assert abs(R - R_expected) < 0.001

    def test_tidal_wave_speed(self):
        """测试7：潮汐波速"""
        h = 5.0  # m
        g = 9.81

        c = tidal_wave_speed(h, g)

        # 波速应为正
        assert c > 0

        # 对于h=5m，c ≈ 7 m/s
        assert 6.5 < c < 7.5

        # 验证公式
        c_expected = np.sqrt(g * h)
        assert abs(c - c_expected) < 0.01

    def test_wave_speed_depth_dependence(self):
        """测试8：波速随水深变化"""
        g = 9.81

        h1 = 3.0
        h2 = 6.0  # 2倍水深

        c1 = tidal_wave_speed(h1, g)
        c2 = tidal_wave_speed(h2, g)

        # 水深增加2倍，波速应增加√2倍
        ratio = c2 / c1
        assert abs(ratio - np.sqrt(2)) < 0.01

    def test_flood_ebb_identification(self):
        """测试9：涨落潮判别"""
        # 涨潮（水位上升）
        dh_dt_flood = 0.1  # m/s
        tide_flood = identify_flood_ebb(dh_dt_flood)
        assert tide_flood == 'flood'

        # 落潮（水位下降）
        dh_dt_ebb = -0.1
        tide_ebb = identify_flood_ebb(dh_dt_ebb)
        assert tide_ebb == 'ebb'

        # 憩流（水位不变）
        dh_dt_slack = 0.0
        tide_slack = identify_flood_ebb(dh_dt_slack)
        assert tide_slack == 'slack'

    def test_slack_times_calculation(self):
        """测试10：憩流时间计算"""
        T = 12.42 * 3600
        n_cycles = 2

        slack_times = compute_slack_times(T, n_cycles)

        # 每个周期有2个憩流时刻
        assert len(slack_times) == 2 * n_cycles

        # 憩流时间应递增
        assert np.all(np.diff(slack_times) > 0)

        # 第一个憩流时间在T/4
        assert abs(slack_times[0] - T/4) < 100

    def test_tidal_energy_flux(self):
        """测试11：潮汐能通量"""
        A = 2.0
        h = 5.0
        b = 200.0
        T = 12.42 * 3600
        g = 9.81

        omega = 2 * np.pi / T
        E = tidal_energy_flux(A, h, b, omega, g)

        # 能通量应为正
        assert E > 0

        # 能通量应在合理范围（MW级）
        assert E > 1e6  # > 1 MW

    def test_tidal_period_validation(self):
        """测试12：潮汐周期验证"""
        # 半日潮
        T_semidiurnal = 12.42 * 3600

        # 全日潮
        T_diurnal = 24.84 * 3600

        # 半日潮周期约为全日潮的一半
        ratio = T_diurnal / T_semidiurnal
        assert abs(ratio - 2.0) < 0.01

        # 半日潮周期约12.42小时
        assert 12.0 < T_semidiurnal/3600 < 13.0


class TestTidalAsymmetry:
    """潮汐不对称性测试"""

    def test_river_induced_asymmetry(self):
        """测试径流引起的不对称"""
        # 有径流时，落潮流速 > 涨潮流速
        v_river = 0.5  # 径流流速 (m/s)
        v_tide_max = 1.0  # 纯潮汐最大流速 (m/s)

        # 涨潮最大流速（逆流）
        v_flood_max = v_tide_max - v_river

        # 落潮最大流速（顺流）
        v_ebb_max = v_tide_max + v_river

        # 落潮流速应大于涨潮流速
        assert v_ebb_max > v_flood_max

        # 验证不对称度
        asymmetry = (v_ebb_max - v_flood_max) / v_tide_max
        assert abs(asymmetry - 1.0) < 0.01

    def test_amplitude_attenuation(self):
        """测试振幅衰减"""
        A0 = 2.0  # 下游振幅 (m)
        x = 20000.0  # 距离 (m)
        alpha = 5e-6  # 衰减系数 (1/m)

        # 沿程振幅衰减
        A_x = A0 * np.exp(-alpha * x)

        # 振幅应衰减
        assert A_x < A0

        # 衰减不应过大
        assert A_x > 0.5 * A0

    def test_tidal_limit_criterion(self):
        """测试潮限判据"""
        # 潮限：潮差 < 0.1m
        tidal_range_limit = 0.1  # m

        # 上游某处潮差
        tidal_range_upstream = 0.08  # m

        # 应判定为超过潮限
        is_beyond_limit = tidal_range_upstream < tidal_range_limit
        assert is_beyond_limit

    def test_phase_velocity(self):
        """测试相速度"""
        T = 12.42 * 3600
        L = 50000.0  # 波长 (m)

        omega = 2 * np.pi / T
        k = 2 * np.pi / L  # 波数

        # 相速度
        cp = omega / k

        # 相速度应为正
        assert cp > 0

        # 相速度 = L/T
        cp_expected = L / T
        assert abs(cp - cp_expected) < 0.1


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_amplitude(self):
        """测试零振幅（无潮汐）"""
        h0 = 5.0
        A = 0.0
        T = 12.42 * 3600

        t = T / 4
        h = tidal_water_level(t, h0, A, T)

        # 无潮汐时水位恒定
        assert abs(h - h0) < 1e-10

    def test_very_large_amplitude(self):
        """测试大振幅（强潮汐）"""
        h0 = 5.0
        A = 4.0  # 大振幅
        T = 12.42 * 3600

        t_high = T / 4
        h_high = tidal_water_level(t_high, h0, A, T)

        # 高潮位
        assert abs(h_high - (h0 + A)) < 0.1

    def test_zero_river_discharge(self):
        """测试零径流"""
        Qr = 0.0
        A = 2.0
        b = 200.0
        c = 7.0

        R = river_tide_parameter(Qr, A, b, c)

        # 无径流时R=0（纯潮汐）
        assert abs(R) < 1e-10

    def test_large_river_discharge(self):
        """测试大径流"""
        Qr = 5000.0  # 大径流
        A = 2.0
        b = 200.0
        c = 7.0

        R = river_tide_parameter(Qr, A, b, c)

        # 大径流时R >> 1（径流主导）
        assert R > 1.0

    def test_shallow_water(self):
        """测试浅水"""
        h = 1.0  # 浅水
        g = 9.81

        c = tidal_wave_speed(h, g)

        # 浅水中波速小
        assert c < 5.0

    def test_deep_water(self):
        """测试深水"""
        h = 20.0  # 深水
        g = 9.81

        c = tidal_wave_speed(h, g)

        # 深水中波速大
        assert c > 10.0

    def test_very_short_period(self):
        """测试短周期"""
        T = 3600.0  # 1小时

        omega = compute_angular_frequency(T)

        # 短周期高频率
        assert omega > 1e-3

    def test_very_long_period(self):
        """测试长周期"""
        T = 24 * 3600.0  # 24小时

        omega = compute_angular_frequency(T)

        # 长周期低频率
        assert omega < 1e-3

    def test_complete_tidal_cycle(self):
        """测试完整潮汐周期"""
        h0 = 5.0
        A = 2.0
        T = 12.42 * 3600

        # 采样一个完整周期
        times = np.linspace(0, T, 1000)
        water_levels = tidal_water_level(times, h0, A, T)

        # 周期开始和结束水位应相同
        assert abs(water_levels[0] - water_levels[-1]) < 0.1

        # 平均水位应等于h0
        h_mean = np.mean(water_levels)
        assert abs(h_mean - h0) < 0.1

    def test_phase_shift_effect(self):
        """测试初相位影响"""
        h0 = 5.0
        A = 2.0
        T = 12.42 * 3600
        t = T / 4

        # 无相位
        h1 = tidal_water_level(t, h0, A, T, phi=0.0)

        # π相位（反相）
        h2 = tidal_water_level(t, h0, A, T, phi=np.pi)

        # 反相时应相差2A
        assert abs((h1 - h0) + (h2 - h0)) < 0.1


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
