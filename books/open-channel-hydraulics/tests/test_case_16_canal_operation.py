"""
案例16单元测试：渠道非恒定流调度

测试内容：
1. 闸门流量计算（自由出流和淹没出流）
2. 闸门开度调节函数
3. 调度延迟时间计算
4. 水位调整时间估算
5. 线性调节策略
6. 指数调节策略
7. 淹没度计算
8. 流量系数验证
9. 边界条件设置
10. 波传播特性

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.channel import RectangularChannel


def gate_discharge_free(b, a, h1, Cd=0.6, g=9.81):
    """
    闸门自由出流流量

    Args:
        b: 渠道宽度 (m)
        a: 闸门开度 (m)
        h1: 上游水深 (m)
        Cd: 流量系数
        g: 重力加速度

    Returns:
        Q: 流量 (m³/s)
    """
    Q = Cd * b * a * np.sqrt(2 * g * h1)
    return Q


def gate_discharge_submerged(b, a, h1, h2, Cd=0.6, g=9.81):
    """
    闸门淹没出流流量

    Args:
        b: 渠道宽度 (m)
        a: 闸门开度 (m)
        h1: 上游水深 (m)
        h2: 下游水深 (m)
        Cd: 流量系数
        g: 重力加速度

    Returns:
        Q: 流量 (m³/s)
    """
    delta_h = h1 - h2
    if delta_h < 0:
        delta_h = 0
    Q = Cd * b * a * np.sqrt(2 * g * delta_h)
    return Q


def submergence_ratio(h1, h2):
    """
    计算淹没度

    Args:
        h1: 上游水深
        h2: 下游水深

    Returns:
        sigma: 淹没度
    """
    if h1 <= 0:
        return 0.0
    return h2 / h1


def linear_adjustment(t, T, a0, af):
    """
    线性调节函数

    Args:
        t: 当前时间
        T: 调节总时长
        a0: 初始开度
        af: 最终开度

    Returns:
        a: 当前开度
    """
    if t <= 0:
        return a0
    elif t >= T:
        return af
    else:
        return a0 + (af - a0) * (t / T)


def exponential_adjustment(t, tau, a0, af):
    """
    指数调节函数

    Args:
        t: 当前时间
        tau: 时间常数
        a0: 初始开度
        af: 最终开度

    Returns:
        a: 当前开度
    """
    if t <= 0:
        return a0
    else:
        return a0 + (af - a0) * (1 - np.exp(-t / tau))


def compute_lag_time(L, v, c):
    """
    计算调度延迟时间

    Args:
        L: 渠道长度 (m)
        v: 平均流速 (m/s)
        c: 波速 (m/s)

    Returns:
        t_lag: 延迟时间 (s)
    """
    return L / (v + c)


def compute_adjustment_time(t_lag, factor=2.5):
    """
    计算水位调整时间

    Args:
        t_lag: 延迟时间 (s)
        factor: 倍数因子（通常2-3）

    Returns:
        t_adjust: 调整时间 (s)
    """
    return factor * t_lag


class TestCase16CanalOperation:
    """案例16：渠道非恒定流调度测试"""

    def test_gate_discharge_free_flow(self):
        """测试1：闸门自由出流流量计算"""
        b = 10.0  # m
        a = 0.5   # m
        h1 = 2.0  # m
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_free(b, a, h1, Cd, g)

        # 验证流量为正
        assert Q > 0

        # 理论流量
        Q_theoretical = Cd * b * a * np.sqrt(2 * g * h1)
        assert abs(Q - Q_theoretical) < 0.01

        # 流量应在合理范围
        assert 10.0 < Q < 50.0

    def test_gate_discharge_proportional_to_opening(self):
        """测试2：流量与开度成正比"""
        b = 10.0
        h1 = 2.0
        Cd = 0.6
        g = 9.81

        a1 = 0.3
        a2 = 0.6  # 2倍开度

        Q1 = gate_discharge_free(b, a1, h1, Cd, g)
        Q2 = gate_discharge_free(b, a2, h1, Cd, g)

        # 开度翻倍，流量应翻倍
        ratio = Q2 / Q1
        assert abs(ratio - 2.0) < 0.01

    def test_gate_discharge_submerged_flow(self):
        """测试3：闸门淹没出流流量计算"""
        b = 10.0
        a = 0.5
        h1 = 2.5  # m
        h2 = 1.5  # m
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_submerged(b, a, h1, h2, Cd, g)

        # 验证流量为正
        assert Q > 0

        # 淹没流量应小于自由流量（相同开度和h1）
        Q_free = gate_discharge_free(b, a, h1, Cd, g)
        assert Q < Q_free

    def test_submergence_ratio_calculation(self):
        """测试4：淹没度计算"""
        h1 = 3.0
        h2 = 2.0

        sigma = submergence_ratio(h1, h2)

        # 淹没度应在0-1之间
        assert 0 <= sigma <= 1

        # 验证计算
        assert abs(sigma - h2/h1) < 0.001

    def test_submergence_threshold(self):
        """测试5：淹没度阈值（0.67）"""
        h1 = 3.0

        # 临界淹没度
        sigma_critical = 0.67
        h2_critical = sigma_critical * h1

        sigma = submergence_ratio(h1, h2_critical)

        assert abs(sigma - sigma_critical) < 0.01

        # σ < 0.67 为自由出流
        h2_free = 0.6 * h1
        sigma_free = submergence_ratio(h1, h2_free)
        assert sigma_free < 0.67

        # σ >= 0.67 为淹没出流
        h2_submerged = 0.7 * h1
        sigma_submerged = submergence_ratio(h1, h2_submerged)
        assert sigma_submerged >= 0.67

    def test_linear_adjustment_function(self):
        """测试6：线性调节函数"""
        a0 = 0.5  # 初始开度50%
        af = 0.8  # 最终开度80%
        T = 3600.0  # 调节时长1小时

        # 初始时刻
        a_t0 = linear_adjustment(0, T, a0, af)
        assert abs(a_t0 - a0) < 0.01

        # 中间时刻
        a_half = linear_adjustment(T/2, T, a0, af)
        a_expected = (a0 + af) / 2
        assert abs(a_half - a_expected) < 0.01

        # 最终时刻
        a_tf = linear_adjustment(T, T, a0, af)
        assert abs(a_tf - af) < 0.01

    def test_linear_adjustment_monotonic(self):
        """测试7：线性调节单调性"""
        a0 = 0.3
        af = 0.9
        T = 3600.0

        times = np.linspace(0, T, 20)
        openings = [linear_adjustment(t, T, a0, af) for t in times]

        # 应单调递增
        for i in range(1, len(openings)):
            assert openings[i] >= openings[i-1]

    def test_exponential_adjustment_function(self):
        """测试8：指数调节函数"""
        a0 = 0.5
        af = 0.8
        tau = 1800.0  # 时间常数30分钟

        # 初始时刻
        a_t0 = exponential_adjustment(0, tau, a0, af)
        assert abs(a_t0 - a0) < 0.01

        # 一个时间常数后，应达到63.2%
        a_tau = exponential_adjustment(tau, tau, a0, af)
        progress = (a_tau - a0) / (af - a0)
        assert abs(progress - 0.632) < 0.05

        # 很长时间后，应接近最终值
        a_long = exponential_adjustment(5*tau, tau, a0, af)
        assert abs(a_long - af) < 0.01

    def test_lag_time_calculation(self):
        """测试9：调度延迟时间计算"""
        L = 5000.0  # m
        v = 1.0     # m/s
        c = 3.0     # m/s

        t_lag = compute_lag_time(L, v, c)

        # 延迟时间 = L / (v+c)
        t_expected = L / (v + c)
        assert abs(t_lag - t_expected) < 0.01

        # 对于5km渠道，延迟时间约1250秒
        assert 1000 < t_lag < 1500

    def test_adjustment_time_calculation(self):
        """测试10：水位调整时间计算"""
        L = 5000.0
        v = 1.0
        c = 3.0

        t_lag = compute_lag_time(L, v, c)
        t_adjust = compute_adjustment_time(t_lag, factor=2.5)

        # 调整时间应为延迟时间的2-3倍
        assert t_adjust > t_lag
        assert t_adjust < 4 * t_lag

    def test_wave_speed_calculation(self):
        """测试11：波速计算"""
        h = 2.0  # m
        g = 9.81

        c = np.sqrt(g * h)

        # 波速应为正
        assert c > 0

        # 对于h=2m，波速约4.4 m/s
        assert 4.0 < c < 5.0

    def test_gate_opening_limits(self):
        """测试12：闸门开度边界"""
        b = 10.0
        h1 = 2.0
        Cd = 0.6
        g = 9.81

        # 零开度
        Q_zero = gate_discharge_free(b, 0.0, h1, Cd, g)
        assert Q_zero == 0.0

        # 全开（开度等于水深）
        a_full = h1
        Q_full = gate_discharge_free(b, a_full, h1, Cd, g)
        assert Q_full > 0


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_upstream_depth(self):
        """测试零上游水深"""
        b = 10.0
        a = 0.5
        h1 = 0.0
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_free(b, a, h1, Cd, g)

        # 零水深应产生零流量
        assert Q == 0.0

    def test_very_small_opening(self):
        """测试极小开度"""
        b = 10.0
        a = 0.01  # 1cm开度
        h1 = 2.0
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_free(b, a, h1, Cd, g)

        # 极小开度应产生小流量
        assert Q > 0
        assert Q < 1.0

    def test_large_opening(self):
        """测试大开度"""
        b = 10.0
        a = 3.0  # 大开度
        h1 = 2.0
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_free(b, a, h1, Cd, g)

        # 大开度应产生大流量
        assert Q > 10.0

    def test_equal_upstream_downstream_depth(self):
        """测试上下游水深相等"""
        b = 10.0
        a = 0.5
        h1 = 2.0
        h2 = 2.0  # 相等
        Cd = 0.6
        g = 9.81

        Q = gate_discharge_submerged(b, a, h1, h2, Cd, g)

        # 无水位差应无流量
        assert Q == 0.0

    def test_negative_time_linear_adjustment(self):
        """测试负时间线性调节"""
        a0 = 0.5
        af = 0.8
        T = 3600.0

        a = linear_adjustment(-100, T, a0, af)

        # 负时间应返回初始开度
        assert a == a0

    def test_overtime_linear_adjustment(self):
        """测试超时线性调节"""
        a0 = 0.5
        af = 0.8
        T = 3600.0

        a = linear_adjustment(5000, T, a0, af)

        # 超过调节时长应返回最终开度
        assert a == af

    def test_decreasing_opening_adjustment(self):
        """测试减小开度调节"""
        a0 = 0.8  # 初始大开度
        af = 0.3  # 最终小开度
        T = 3600.0

        # 中间时刻
        a_half = linear_adjustment(T/2, T, a0, af)

        # 应在初始和最终之间
        assert af < a_half < a0

    def test_very_short_adjustment_time(self):
        """测试极短调节时间"""
        a0 = 0.5
        af = 0.8
        T = 10.0  # 10秒

        a_half = linear_adjustment(5, T, a0, af)

        # 应在中间值附近
        a_expected = (a0 + af) / 2
        assert abs(a_half - a_expected) < 0.05

    def test_very_long_adjustment_time(self):
        """测试极长调节时间"""
        a0 = 0.5
        af = 0.8
        T = 86400.0  # 24小时

        # 1小时后变化应很小
        a_1h = linear_adjustment(3600, T, a0, af)
        progress = (a_1h - a0) / (af - a0)

        # 1小时/24小时 ≈ 4.2%
        assert progress < 0.1

    def test_short_channel_lag_time(self):
        """测试短渠道延迟时间"""
        L = 500.0  # 短渠道
        v = 1.0
        c = 3.0

        t_lag = compute_lag_time(L, v, c)

        # 短渠道延迟时间短
        assert t_lag < 200


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
