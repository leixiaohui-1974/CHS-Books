"""
案例8单元测试：桥梁壅水分析

测试内容：
1. 收缩系数计算
2. 天然河道水力计算
3. 桥下收缩断面计算（能量方程）
4. 壅水高度计算
5. 流速增加验证
6. 局部损失计算
7. 能量守恒验证
8. 不同收缩程度影响
9. 壅水曲线计算
10. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from models.channel import RectangularChannel
from solvers.steady.profile import WaterSurfaceProfile


class TestCase08BridgeHydraulics:
    """案例8：桥梁壅水分析测试"""

    def test_contraction_coefficient(self):
        """测试1：收缩系数计算"""
        B0 = 50.0  # 天然河道宽度
        Bb = 40.0  # 桥下净宽

        # 收缩系数
        epsilon = Bb / B0

        # 验证计算
        assert epsilon == 0.8

        # 收缩系数应在合理范围
        assert 0.5 < epsilon < 1.0

    def test_natural_channel_hydraulics(self):
        """测试2：天然河道水力计算"""
        B0 = 50.0
        S0 = 0.0005
        n = 0.030
        Q = 200.0

        channel = RectangularChannel(b=B0, S0=S0, n=n)

        # 正常水深
        h0 = channel.compute_normal_depth(Q)
        A0 = channel.area(h0)
        v0 = Q / A0
        Fr0 = channel.froude_number(h0, Q)

        # 验证合理性
        assert h0 > 0
        assert v0 > 0
        assert Fr0 < 1  # 天然河道通常为缓流

        # 验证连续性方程
        Q_check = A0 * v0
        assert abs(Q_check - Q) / Q < 0.001

    def test_bridge_contraction_depth(self):
        """测试3：桥下收缩断面水深计算"""
        B0 = 50.0
        Bb = 40.0
        S0 = 0.0005
        n = 0.030
        nb = 0.025
        Q = 200.0
        g = 9.81

        # 天然河道
        channel_natural = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel_natural.compute_normal_depth(Q)
        v0 = Q / (B0 * h0)
        E0 = h0 + v0**2 / (2*g)

        # 桥下断面（迭代求解）
        h1 = h0  # 初始猜测
        zeta = 0.15  # 局部损失系数

        for i in range(100):
            A1 = Bb * h1
            v1 = Q / A1
            E1 = h1 + v1**2 / (2*g)
            hf = zeta * v1**2 / (2*g)

            # 能量方程：E0 = E1 + hf
            f = E1 + hf - E0

            if abs(f) < 1e-6:
                break

            # 数值导数
            dh = 1e-6
            A1_plus = Bb * (h1 + dh)
            v1_plus = Q / A1_plus
            E1_plus = (h1 + dh) + v1_plus**2 / (2*g)
            hf_plus = zeta * v1_plus**2 / (2*g)
            f_plus = E1_plus + hf_plus - E0

            df = (f_plus - f) / dh
            if abs(df) > 1e-12:
                h1 = h1 - f / df

        # 桥下水深可能小于天然水深（收缩加速）
        # 壅水主要发生在桥前上游，桥下可能是收缩断面
        assert h1 > 0

        # 桥下流速应大于天然流速（收缩加速）
        v1 = Q / (Bb * h1)
        assert v1 > v0

        # 验证能量方程收敛
        E1 = h1 + v1**2 / (2*g)
        hf = zeta * v1**2 / (2*g)
        energy_error = abs(E1 + hf - E0)
        assert energy_error < 0.01

    def test_backwater_height_calculation(self):
        """测试4：壅水高度计算（经验公式）"""
        B0 = 50.0
        Bb = 40.0
        Q = 200.0
        g = 9.81

        # 假设相同水深下的流速
        h = 3.0
        v0 = Q / (B0 * h)
        v1 = Q / (Bb * h)

        # 经验公式：Δh = K*(v1² - v0²)/(2g)
        K = 1.2
        dh_empirical = K * (v1**2 - v0**2) / (2*g)

        # 经验公式应给出正值（流速增加导致壅水）
        assert dh_empirical > 0

        # 壅水高度应在合理范围（0.01-1.0m）
        assert 0.01 < dh_empirical < 1.0

        # 验证K系数的影响
        K_values = [1.0, 1.2, 1.5]
        for K_test in K_values:
            dh = K_test * (v1**2 - v0**2) / (2*g)
            # 壅水应与K成正比
            ratio = dh / dh_empirical
            expected_ratio = K_test / K
            assert abs(ratio - expected_ratio) < 0.001

    def test_velocity_increase(self):
        """测试5：流速增加验证"""
        B0 = 50.0
        Bb = 40.0
        Q = 200.0

        # 假设水深相同的情况下
        h = 3.0

        v0 = Q / (B0 * h)
        v1 = Q / (Bb * h)

        # 流速增加
        dv = v1 - v0
        dv_ratio = dv / v0

        # 流速应增加
        assert dv > 0

        # 流速增加率应与收缩系数相关
        epsilon = Bb / B0
        # v1/v0 = B0/Bb = 1/epsilon
        expected_ratio = (1 - epsilon) / epsilon
        assert abs(dv_ratio - expected_ratio) / expected_ratio < 0.1

    def test_local_head_loss(self):
        """测试6：局部水头损失计算"""
        Bb = 40.0
        Q = 200.0
        h1 = 3.0
        g = 9.81

        v1 = Q / (Bb * h1)

        # 局部损失系数
        zeta_values = [0.1, 0.15, 0.2, 0.3]

        for zeta in zeta_values:
            hf = zeta * v1**2 / (2*g)

            # 损失应为正
            assert hf > 0

            # 损失应随系数线性增加
            hf_ref = 0.15 * v1**2 / (2*g)
            expected_ratio = zeta / 0.15
            actual_ratio = hf / hf_ref
            assert abs(actual_ratio - expected_ratio) < 0.001

    def test_energy_conservation(self):
        """测试7：能量守恒验证"""
        B0 = 50.0
        Bb = 40.0
        S0 = 0.0005
        n = 0.030
        Q = 200.0
        g = 9.81

        channel_natural = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel_natural.compute_normal_depth(Q)
        v0 = Q / (B0 * h0)
        E0 = h0 + v0**2 / (2*g)

        # 桥下水深（通过能量方程求解）
        zeta = 0.15
        h1 = h0  # 初始猜测

        # 迭代求解满足能量方程的h1
        for i in range(100):
            v1 = Q / (Bb * h1)
            E1 = h1 + v1**2 / (2*g)
            hf = zeta * v1**2 / (2*g)

            f = E1 + hf - E0

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            v1_plus = Q / (Bb * (h1 + dh))
            E1_plus = (h1 + dh) + v1_plus**2 / (2*g)
            hf_plus = zeta * v1_plus**2 / (2*g)
            f_plus = E1_plus + hf_plus - E0

            df = (f_plus - f) / dh
            if abs(df) > 1e-12:
                h1 = h1 - f / df

        # 验证能量守恒
        v1 = Q / (Bb * h1)
        E1 = h1 + v1**2 / (2*g)
        hf = zeta * v1**2 / (2*g)
        energy_balance = E0 - E1 - hf

        # 能量应该守恒（误差很小）
        assert abs(energy_balance) < 0.01

    def test_different_contraction_ratios(self):
        """测试8：不同收缩程度影响"""
        B0 = 50.0
        S0 = 0.0005
        n = 0.030
        Q = 200.0
        g = 9.81

        channel = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q)
        v0 = Q / (B0 * h0)

        # 不同桥下净宽
        Bb_values = [45.0, 40.0, 35.0, 30.0]
        backwater_heights = []

        for Bb in Bb_values:
            # 简化计算：假设水深与流速成反比
            # Q = Bb * h1 * v1
            # v1 ≈ Q / (Bb * h0) (粗略估算)
            v1 = Q / (Bb * h0)

            # 经验公式估算壅水
            K = 1.2
            dh = K * (v1**2 - v0**2) / (2*g)
            backwater_heights.append(dh)

        # 验证：收缩越大，壅水越严重
        for i in range(len(backwater_heights) - 1):
            assert backwater_heights[i] < backwater_heights[i+1]

    def test_backwater_profile_calculation(self):
        """测试9：壅水曲线计算"""
        B0 = 50.0
        Bb = 40.0
        S0 = 0.0005
        n = 0.030
        Q = 200.0

        channel = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q)

        # 桥前控制水深（假设为壅水后的水深）
        h_control = h0 * 1.15

        # 水面曲线求解
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)

        result = profile.compute_profile(
            h_start=h_control,
            L=500.0,
            direction='upstream'
        )

        # 验证返回数据
        assert len(result['x']) > 0
        assert len(result['h']) == len(result['x'])

        # 验证水深趋势：向上游逐渐恢复到正常水深
        h_values = result['h']
        # 上游水深应接近正常水深
        assert abs(h_values[0] - h0) < abs(h_values[-1] - h0)

    def test_froude_number_change(self):
        """测试10：弗劳德数变化"""
        B0 = 50.0
        Bb = 40.0
        Q = 200.0
        g = 9.81

        # 假设相同水深
        h = 3.0

        # 天然断面
        v0 = Q / (B0 * h)
        Fr0 = v0 / np.sqrt(g * h)

        # 桥下断面
        v1 = Q / (Bb * h)
        Fr1 = v1 / np.sqrt(g * h)

        # 桥下弗劳德数应增大
        assert Fr1 > Fr0

        # Fr增加比例应等于收缩比例
        ratio = Fr1 / Fr0
        epsilon = Bb / B0
        expected_ratio = 1 / epsilon
        assert abs(ratio - expected_ratio) / expected_ratio < 0.001

    def test_continuity_equation(self):
        """测试11：连续性方程验证"""
        B0 = 50.0
        Bb = 40.0
        Q = 200.0

        h0 = 3.0
        h1 = 3.5

        # 天然断面流量
        A0 = B0 * h0
        v0 = Q / A0
        Q0 = A0 * v0

        # 桥下断面流量
        A1 = Bb * h1
        v1 = Q / A1
        Q1 = A1 * v1

        # 流量应守恒
        assert abs(Q0 - Q) / Q < 0.001
        assert abs(Q1 - Q) / Q < 0.001


class TestEdgeCases:
    """边界条件测试"""

    def test_no_contraction(self):
        """测试无收缩情况（Bb = B0）"""
        B0 = 50.0
        Bb = 50.0  # 无收缩

        epsilon = Bb / B0
        assert epsilon == 1.0

        Q = 200.0
        h = 3.0

        v0 = Q / (B0 * h)
        v1 = Q / (Bb * h)

        # 流速应相同
        assert abs(v0 - v1) < 0.001

    def test_severe_contraction(self):
        """测试严重收缩（Bb = 0.5*B0）"""
        B0 = 50.0
        Bb = 25.0  # 严重收缩

        epsilon = Bb / B0
        assert epsilon == 0.5

        Q = 200.0
        h = 3.0
        g = 9.81

        v0 = Q / (B0 * h)
        v1 = Q / (Bb * h)

        # 流速应加倍
        assert abs(v1 - 2 * v0) / v0 < 0.01

        # 壅水应该很大
        K = 1.2
        dh = K * (v1**2 - v0**2) / (2*g)
        assert dh > 0.3  # 严重收缩应产生明显壅水

    def test_mild_contraction(self):
        """测试轻微收缩（Bb = 0.9*B0）"""
        B0 = 50.0
        Bb = 45.0  # 轻微收缩

        epsilon = Bb / B0
        assert epsilon == 0.9

        Q = 200.0
        h = 3.0
        g = 9.81

        v0 = Q / (B0 * h)
        v1 = Q / (Bb * h)

        # 流速增加不大
        dv_ratio = (v1 - v0) / v0
        assert dv_ratio < 0.2

        # 壅水应该很小
        K = 1.2
        dh = K * (v1**2 - v0**2) / (2*g)
        assert dh < 0.1

    def test_small_discharge(self):
        """测试小流量"""
        B0 = 50.0
        Bb = 40.0
        S0 = 0.0005
        n = 0.030
        Q = 50.0  # 小流量

        channel = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q)

        # 应该能正常计算
        assert h0 > 0
        assert h0 < 10.0

    def test_large_discharge(self):
        """测试大流量"""
        B0 = 50.0
        Bb = 40.0
        S0 = 0.0005
        n = 0.030
        Q = 500.0  # 大流量

        channel = RectangularChannel(b=B0, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q)

        # 应该能正常计算
        assert h0 > 0
        # 大流量应有较大水深
        assert h0 > 4.0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
