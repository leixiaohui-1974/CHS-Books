"""
案例7单元测试：渠道水面曲线计算

测试内容：
1. 比能计算
2. 弗劳德数计算
3. 摩阻坡度计算
4. 上游水深计算（标准步长法）
5. 水面曲线分类（M1/M2/M3/S1/S2/S3/C1/C3）
6. 完整水面曲线计算
7. 壅水长度计算
8. 能量守恒验证
9. 不同渠道类型测试
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

from models.channel import TrapezoidalChannel
from solvers.steady.profile import WaterSurfaceProfile


class TestCase07WaterSurfaceProfile:
    """案例7：渠道水面曲线测试"""

    def test_specific_energy_calculation(self):
        """测试1：比能计算"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        h = 2.0
        A = channel.area(h)
        v = Q / A
        g = 9.81

        # 比能公式：E = h + v²/(2g)
        E_calc = profile.specific_energy(h)
        E_theoretical = h + v**2 / (2*g)

        # 验证计算正确
        assert abs(E_calc - E_theoretical) / E_theoretical < 0.001

        # 比能应大于水深
        assert E_calc > h

    def test_froude_number_calculation(self):
        """测试2：弗劳德数计算"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        h = 2.0
        A = channel.area(h)
        B = channel.top_width(h)
        hm = A / B  # 平均水深
        v = Q / A
        g = 9.81

        # 弗劳德数公式：Fr = v / sqrt(g*hm)
        Fr_calc = profile.froude_number(h)
        Fr_theoretical = v / np.sqrt(g * hm)

        # 验证计算正确
        assert abs(Fr_calc - Fr_theoretical) / Fr_theoretical < 0.01

    def test_friction_slope_calculation(self):
        """测试3：摩阻坡度计算"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        h = 2.0
        A = channel.area(h)
        P = channel.wetted_perimeter(h)
        R = A / P

        # 摩阻坡度公式：Sf = n²Q² / (A²R^(4/3))
        Sf_calc = profile.friction_slope(h)
        Sf_theoretical = (n**2 * Q**2) / (A**2 * R**(4.0/3.0))

        # 验证计算正确
        assert abs(Sf_calc - Sf_theoretical) / Sf_theoretical < 0.001

        # 摩阻坡度应为正
        assert Sf_calc > 0

    def test_upstream_depth_calculation(self):
        """测试4：上游水深计算（标准步长法）"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)

        # 下游水深
        h1 = 2.5
        dx = 20.0

        # 计算上游水深
        h2 = profile.compute_upstream_depth(h1, dx)

        # 上游水深应小于下游（壅水曲线向上游水深降低）
        assert h2 < h1

        # 上游水深应为正
        assert h2 > 0

        # 水深变化应合理（不会太剧烈）
        assert abs(h2 - h1) < 0.5

    def test_profile_classification_M1(self):
        """测试5：水面曲线分类 - M1型（缓坡壅水）"""
        b = 3.0
        m = 1.5
        S0 = 0.0008  # 缓坡
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        # 计算正常水深和临界水深
        hn = channel.compute_normal_depth(Q)
        hc = channel.compute_critical_depth(Q)

        # 验证是缓坡（hn > hc）
        assert hn > hc

        # 控制水深大于正常水深（壅水）
        h_control = hn + 0.5

        # 分类
        curve_type = profile.classify_profile(h_control)

        # 应该是M1型
        assert "M1" in curve_type

    def test_profile_classification_M2(self):
        """测试6：水面曲线分类 - M2型（缓坡过渡）"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        hn = channel.compute_normal_depth(Q)
        hc = channel.compute_critical_depth(Q)

        # 控制水深在正常水深和临界水深之间
        h_control = (hn + hc) / 2

        curve_type = profile.classify_profile(h_control)

        # 应该是M2型
        assert "M2" in curve_type

    def test_compute_full_profile(self):
        """测试7：完整水面曲线计算"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)

        # 控制水深
        h_control = 2.5

        # 计算水面曲线（向上游推算1000m）
        result = profile.compute_profile(
            h_start=h_control,
            L=1000.0,
            direction='upstream'
        )

        # 验证返回的字段
        assert 'x' in result
        assert 'h' in result
        assert 'E' in result
        assert 'Fr' in result
        assert 'type' in result

        # 验证数据长度一致
        assert len(result['x']) == len(result['h'])
        assert len(result['x']) == len(result['E'])
        assert len(result['x']) == len(result['Fr'])

        # 验证数据合理性
        assert len(result['x']) > 0
        assert all(h > 0 for h in result['h'])
        assert all(E > 0 for E in result['E'])
        assert all(Fr > 0 for Fr in result['Fr'])

        # 验证水深趋势（M1型，向上游水深降低）
        h_values = result['h']
        # 列表已反转：h_values[0]是上游（小），h_values[-1]是下游（大）
        # 下游水深应大于上游水深
        assert h_values[-1] > h_values[0]

    def test_backwater_length_calculation(self):
        """测试8：壅水长度计算"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)

        hn = channel.compute_normal_depth(Q)
        h_control = hn + 0.5  # 壅水0.5m

        # 计算壅水长度
        L_backwater = profile.compute_backwater_length(h_control, h_threshold=0.05)

        # 壅水长度应为正
        assert L_backwater > 0

        # 壅水长度应在合理范围（几百米到几千米）
        assert 100 < L_backwater < 5000

    def test_energy_conservation(self):
        """测试9：能量守恒验证"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)

        h1 = 2.5
        dx = 20.0

        # 下游断面
        E1 = profile.specific_energy(h1)
        Sf1 = profile.friction_slope(h1)

        # 上游断面
        h2 = profile.compute_upstream_depth(h1, dx)
        E2 = profile.specific_energy(h2)
        Sf2 = profile.friction_slope(h2)

        # 能量方程：E2 + S0*dx = E1 + Sf_avg*dx
        Sf_avg = (Sf1 + Sf2) / 2
        energy_balance = E2 + S0 * dx - E1 - Sf_avg * dx

        # 能量应该基本守恒（误差很小）
        assert abs(energy_balance) < 0.01

    def test_steep_slope_channel(self):
        """测试10：陡坡渠道（S1型）"""
        b = 3.0
        m = 1.5
        S0 = 0.05  # 陡坡
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        hn = channel.compute_normal_depth(Q)
        hc = channel.compute_critical_depth(Q)

        # 验证是陡坡（hn < hc）
        assert hn < hc

        # 控制水深大于临界水深（壅水）
        h_control = hc + 0.5

        curve_type = profile.classify_profile(h_control)

        # 应该是S1型
        assert "S1" in curve_type

    def test_mild_slope_verification(self):
        """测试11：缓坡渠道验证"""
        b = 3.0
        m = 1.5
        S0 = 0.0008  # 缓坡
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        hn = channel.compute_normal_depth(Q)
        hc = channel.compute_critical_depth(Q)

        # 缓坡特征：hn > hc
        assert hn > hc

        # 正常流应为缓流（Fr < 1）
        Fr_normal = profile.froude_number(hn)
        assert Fr_normal < 1

    def test_critical_depth_froude_number(self):
        """测试12：临界水深处弗劳德数"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        hc = channel.compute_critical_depth(Q)
        Fr_critical = profile.froude_number(hc)

        # 临界水深处Fr应接近1.0
        assert 0.95 < Fr_critical < 1.05


class TestEdgeCases:
    """边界条件测试"""

    def test_very_small_depth(self):
        """测试极浅水深"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        h = 0.1  # 极浅

        # 应该能计算（即使数值可能很大）
        E = profile.specific_energy(h)
        Fr = profile.froude_number(h)
        Sf = profile.friction_slope(h)

        assert E > h
        assert Fr > 1  # 浅水急流
        assert Sf > 0

    def test_very_deep_depth(self):
        """测试很深水深"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        h = 5.0  # 很深

        E = profile.specific_energy(h)
        Fr = profile.froude_number(h)
        Sf = profile.friction_slope(h)

        assert E > h
        assert Fr < 1  # 深水缓流
        assert Sf > 0

    def test_no_backwater(self):
        """测试无壅水情况"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q)

        hn = channel.compute_normal_depth(Q)
        h_control = hn - 0.2  # 控制水深小于正常水深

        # 壅水长度应为0
        L_backwater = profile.compute_backwater_length(h_control)
        assert L_backwater == 0.0

    def test_large_backwater(self):
        """测试大壅水情况"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=50.0)

        hn = channel.compute_normal_depth(Q)
        h_control = hn + 1.0  # 大壅水

        L_backwater = profile.compute_backwater_length(h_control, h_threshold=0.05)

        # 大壅水影响距离应该很长
        assert L_backwater > 500

    def test_small_step_size(self):
        """测试小步长"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=5.0)  # 小步长

        h_control = 2.5

        result = profile.compute_profile(
            h_start=h_control,
            L=200.0,
            direction='upstream'
        )

        # 小步长应该产生更多计算点
        assert len(result['x']) > 10

    def test_large_step_size(self):
        """测试大步长"""
        b = 3.0
        m = 1.5
        S0 = 0.0008
        n = 0.020
        Q = 6.0

        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
        profile = WaterSurfaceProfile(channel=channel, Q=Q, dx=100.0)  # 大步长

        h_control = 2.5

        result = profile.compute_profile(
            h_start=h_control,
            L=500.0,
            direction='upstream'
        )

        # 大步长产生较少计算点
        assert len(result['x']) < 20


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
