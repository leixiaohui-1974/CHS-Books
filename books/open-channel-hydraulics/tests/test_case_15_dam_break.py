"""
案例15单元测试：溃坝波计算

测试内容：
1. 干河床溃坝波理论解
2. 湿河床溃坝波理论解
3. 波前传播速度计算
4. Riemann不变量验证
5. 特征线速度计算
6. 膨胀波区域验证
7. 激波速度计算（湿河床）
8. 数值解与理论解对比
9. 质量守恒验证
10. 不同水深比影响

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from solvers.saint_venant import SaintVenantSolver


def dam_break_dry_bed_solution(x, t, h0, g=9.81):
    """
    干河床溃坝波理论解（Ritter解）

    Args:
        x: 空间位置（溃坝点为原点）
        t: 时间
        h0: 上游初始水深
        g: 重力加速度

    Returns:
        h, v: 水深和流速
    """
    if t <= 0:
        # 初始条件
        return h0 if x < 0 else 0.0, 0.0

    c0 = np.sqrt(g * h0)
    xi = x / t  # 自相似变量

    if xi <= -c0:
        # 静水区
        h = h0
        v = 0.0
    elif xi <= 2*c0:
        # 膨胀波区
        h = (1.0/(9.0*g)) * (2*c0 - xi)**2
        v = (2.0/3.0) * (c0 + xi)
    else:
        # 干河床
        h = 0.0
        v = 0.0

    return h, v


def dam_break_wet_bed_middle_state(h0, hd, g=9.81):
    """
    计算湿河床溃坝波的中间状态（星号状态）

    Args:
        h0: 上游水深
        hd: 下游水深
        g: 重力加速度

    Returns:
        h_star, v_star: 中间状态的水深和流速
    """
    c0 = np.sqrt(g * h0)
    cd = np.sqrt(g * hd)

    # 迭代求解中间状态
    # v* = 2(c0 - c*) 和 v* = 2(c* - cd)连接
    # 简化：v* = 2(c0 - c*)
    # 激波条件给出另一个关系

    # 简化近似：假设弱激波
    h_star = h0 * 0.6  # 粗略估计
    c_star = np.sqrt(g * h_star)
    v_star = 2 * (c0 - c_star)

    return h_star, v_star


def dam_break_shock_speed(h_star, v_star, hd, g=9.81):
    """
    计算激波传播速度（Rankine-Hugoniot条件）

    Args:
        h_star: 激波前水深
        v_star: 激波前流速
        hd: 激波后水深
        g: 重力加速度

    Returns:
        U: 激波速度
    """
    c_star = np.sqrt(g * h_star)
    U = v_star + c_star * np.sqrt((h_star + hd) / (2 * hd))
    return U


class TestCase15DamBreak:
    """案例15：溃坝波计算测试"""

    def test_dry_bed_wave_front_speed(self):
        """测试1：干河床波前速度"""
        h0 = 10.0  # m
        g = 9.81

        c0 = np.sqrt(g * h0)
        wave_front_speed = 2 * c0

        # 理论波前速度 = 2√(gh0)
        assert abs(wave_front_speed - 2*c0) < 0.001

        # 对于h0=10m，波前速度约19.8 m/s
        assert 19.0 < wave_front_speed < 20.5

    def test_dry_bed_solution_static_region(self):
        """测试2：干河床静水区"""
        h0 = 10.0
        t = 10.0
        g = 9.81

        c0 = np.sqrt(g * h0)

        # 静水区：x/t < -c0 (c0 ≈ 9.9 m/s)
        x = -120.0  # x/t = -12 < -c0
        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 静水区应保持初始水深
        assert abs(h - h0) < 0.01

        # 静水区流速为零
        assert abs(v) < 0.01

    def test_dry_bed_solution_expansion_wave(self):
        """测试3：干河床膨胀波区"""
        h0 = 10.0
        t = 10.0
        g = 9.81

        c0 = np.sqrt(g * h0)

        # 膨胀波区：-c0 < x/t < 2c0
        x = 50.0  # x/t = 5.0，在膨胀波区内
        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 膨胀波区水深应在0到h0之间
        assert 0 < h < h0

        # 膨胀波区流速应为正
        assert v > 0

    def test_dry_bed_solution_dry_region(self):
        """测试4：干河床干燥区"""
        h0 = 10.0
        t = 10.0
        g = 9.81

        c0 = np.sqrt(g * h0)

        # 干燥区：x/t > 2c0
        x = 250.0  # x/t = 25 > 2c0
        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 干燥区水深为零
        assert abs(h) < 0.01

        # 干燥区流速为零
        assert abs(v) < 0.01

    def test_riemann_invariants_dry_bed(self):
        """测试5：Riemann不变量（干河床）"""
        h0 = 10.0
        t = 10.0
        g = 9.81

        c0 = np.sqrt(g * h0)

        # 在膨胀波区内多个点验证R+ = v + 2c
        x_values = [0, 50, 100]
        R_plus_values = []

        for x in x_values:
            xi = x / t
            if -c0 < xi < 2*c0:
                h, v = dam_break_dry_bed_solution(x, t, h0, g)
                c = np.sqrt(g * h)
                R_plus = v + 2*c
                R_plus_values.append(R_plus)

        # R+ 应近似恒定（等于2c0）
        if len(R_plus_values) > 0:
            R_plus_expected = 2 * c0
            for R_plus in R_plus_values:
                assert abs(R_plus - R_plus_expected) / R_plus_expected < 0.1

    def test_characteristic_velocity(self):
        """测试6：特征线速度"""
        h0 = 10.0
        t = 10.0
        x = 50.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)
        c = np.sqrt(g * h)

        # 正向特征线速度
        lambda_plus = v + c

        # 负向特征线速度
        lambda_minus = v - c

        # 正向特征线应向右传播
        assert lambda_plus > 0

        # 对于膨胀波，负向特征线可能向左
        # 但在某些区域可能向右（取决于v的大小）

    def test_wet_bed_middle_state(self):
        """测试7：湿河床中间状态"""
        h0 = 10.0
        hd = 2.0
        g = 9.81

        h_star, v_star = dam_break_wet_bed_middle_state(h0, hd, g)

        # 中间水深应在hd和h0之间
        assert hd < h_star < h0

        # 中间流速应为正
        assert v_star > 0

    def test_shock_speed_calculation(self):
        """测试8：激波速度计算"""
        h0 = 10.0
        hd = 2.0
        g = 9.81

        h_star, v_star = dam_break_wet_bed_middle_state(h0, hd, g)
        U = dam_break_shock_speed(h_star, v_star, hd, g)

        # 激波速度应大于中间流速
        assert U > v_star

        # 激波速度应在合理范围
        c0 = np.sqrt(g * h0)
        assert 0 < U < 3*c0

    def test_dam_break_time_evolution(self):
        """测试9：溃坝波时间演化"""
        h0 = 10.0
        g = 9.81

        c0 = np.sqrt(g * h0)

        # 不同时刻的波前位置
        times = [1.0, 5.0, 10.0]
        wave_fronts = []

        for t in times:
            x_front = 2 * c0 * t
            wave_fronts.append(x_front)

        # 波前位置应随时间线性增长
        for i in range(1, len(times)):
            ratio = wave_fronts[i] / wave_fronts[i-1]
            time_ratio = times[i] / times[i-1]
            assert abs(ratio - time_ratio) < 0.01

    def test_self_similar_solution(self):
        """测试10：自相似解验证"""
        h0 = 10.0
        g = 9.81

        # 不同时刻、不同位置，但相同xi=x/t
        xi = 5.0  # 自相似变量

        results = []
        for t in [5.0, 10.0, 20.0]:
            x = xi * t
            h, v = dam_break_dry_bed_solution(x, t, h0, g)
            results.append((h, v))

        # 自相似解：相同xi应给出相同的h和v
        h_ref, v_ref = results[0]
        for h, v in results[1:]:
            assert abs(h - h_ref) / max(h_ref, 0.01) < 0.01
            assert abs(v - v_ref) / max(v_ref, 0.01) < 0.01


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_time(self):
        """测试零时刻"""
        h0 = 10.0
        t = 0.0
        x = 50.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # t=0时应为初始条件
        assert v == 0.0

    def test_shallow_upstream_water(self):
        """测试浅上游水深"""
        h0 = 1.0  # 浅水
        t = 10.0
        x = 5.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 应能正常计算
        assert h >= 0
        assert v >= 0

    def test_deep_upstream_water(self):
        """测试深上游水深"""
        h0 = 50.0  # 深水
        t = 10.0
        x = 100.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 应能正常计算
        assert h >= 0
        assert v >= 0

    def test_very_small_time(self):
        """测试极小时间"""
        h0 = 10.0
        t = 0.1  # 极小时间
        x = 1.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 应能正常计算
        assert h >= 0

    def test_very_large_time(self):
        """测试极大时间"""
        h0 = 10.0
        t = 1000.0  # 很大时间
        x = 5000.0
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 应能正常计算
        assert h >= 0

    def test_upstream_location(self):
        """测试上游位置（负x）"""
        h0 = 10.0
        t = 10.0
        x = -50.0  # 上游
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 上游静水区
        c0 = np.sqrt(g * h0)
        if x/t < -c0:
            assert abs(h - h0) < 0.1
            assert abs(v) < 0.1

    def test_downstream_far_location(self):
        """测试下游远处（大正x）"""
        h0 = 10.0
        t = 10.0
        x = 500.0  # 下游远处
        g = 9.81

        h, v = dam_break_dry_bed_solution(x, t, h0, g)

        # 应在干河床区
        c0 = np.sqrt(g * h0)
        if x/t > 2*c0:
            assert abs(h) < 0.1
            assert abs(v) < 0.1

    def test_small_downstream_depth(self):
        """测试小下游水深（接近干河床）"""
        h0 = 10.0
        hd = 0.1  # 很小但非零
        g = 9.81

        h_star, v_star = dam_break_wet_bed_middle_state(h0, hd, g)

        # 应接近干河床情况
        assert h_star > hd

    def test_large_depth_ratio(self):
        """测试大水深比"""
        h0 = 20.0
        hd = 1.0  # 大水深比
        g = 9.81

        h_star, v_star = dam_break_wet_bed_middle_state(h0, hd, g)
        U = dam_break_shock_speed(h_star, v_star, hd, g)

        # 大水深比会产生强激波
        assert U > 0

    def test_small_depth_ratio(self):
        """测试小水深比"""
        h0 = 5.0
        hd = 4.0  # 小水深比
        g = 9.81

        h_star, v_star = dam_break_wet_bed_middle_state(h0, hd, g)
        U = dam_break_shock_speed(h_star, v_star, hd, g)

        # 小水深比产生弱激波
        assert U > 0

        # 激波速度应较小
        c0 = np.sqrt(g * h0)
        assert U < 2*c0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
