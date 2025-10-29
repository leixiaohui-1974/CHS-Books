"""
案例3单元测试：景观水渠水流状态分析

测试内容：
1. 正常水深和临界水深计算
2. 比能计算和分析
3. 弗劳德数计算
4. 共轭水深计算
5. 流态判别
6. 比能曲线关键点

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
from solvers.steady.uniform_flow import UniformFlowSolver


class TestCase03LandscapeCanal:
    """案例3：景观水渠水流状态分析测试"""

    def test_normal_depth_calculation(self):
        """测试1：正常水深计算"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h0 = results['水深_h']
        v0 = results['流速_v']
        Fr0 = results['弗劳德数_Fr']

        # 验证水深在合理范围
        assert 0.2 < h0 < 1.0

        # 验证为缓流（景观水渠一般是缓坡，缓流）
        assert Fr0 < 1
        assert results['流态'] == "缓流"

    def test_critical_depth_calculation(self):
        """测试2：临界水深计算"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)

        # 理论临界水深：hc = (q²/g)^(1/3)
        q = Q / b
        g = 9.81
        hc_theoretical = (q**2 / g)**(1/3)

        # 数值计算
        hc_numerical = channel.compute_critical_depth(Q)

        # 两者应非常接近
        assert abs(hc_numerical - hc_theoretical) / hc_theoretical < 0.001

    def test_specific_energy_calculation(self):
        """测试3：比能计算"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        # 正常水深
        results = solver.compute_normal_depth(Q)
        h0 = results['水深_h']
        v0 = results['流速_v']

        # 比能 E = h + v²/(2g)
        g = 9.81
        E0 = h0 + v0**2 / (2*g)

        # 临界水深
        hc = channel.compute_critical_depth(Q)
        vc = Q / (b * hc)
        Ec = hc + vc**2 / (2*g)

        # 临界比能理论值 Ec = 1.5 * hc
        Ec_theoretical = 1.5 * hc

        # 验证临界比能计算
        assert abs(Ec - Ec_theoretical) / Ec_theoretical < 0.001

        # 正常水深的比能应大于临界比能（缓流）
        assert E0 > Ec

    def test_froude_number(self):
        """测试4：弗劳德数计算"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h = results['水深_h']
        v = results['流速_v']
        Fr = results['弗劳德数_Fr']

        # 手动计算弗劳德数
        g = 9.81
        Fr_calc = v / np.sqrt(g * h)

        # 验证弗劳德数计算正确
        assert abs(Fr - Fr_calc) / Fr_calc < 0.01

    def test_conjugate_depth(self):
        """测试5：水跃共轭水深计算"""
        b = 2.0
        Q = 1.0
        g = 9.81

        # 水跃共轭水深（基于动量守恒）
        # 给定跃前水深h1（急流），计算跃后水深h2（缓流）

        h1 = 0.2270  # 急流水深
        v1 = Q / (b * h1)
        Fr1 = v1 / np.sqrt(g * h1)

        assert Fr1 > 1  # 确认h1是急流

        # 水跃共轭水深公式（矩形断面）：
        # h2 = h1/2 * (sqrt(1 + 8*Fr1²) - 1)
        h2_calc = h1 / 2 * (np.sqrt(1 + 8*Fr1**2) - 1)

        # 验证h2是缓流
        v2 = Q / (b * h2_calc)
        Fr2 = v2 / np.sqrt(g * h2_calc)
        assert Fr2 < 1  # h2应该是缓流

        # 验证动量守恒（简化形式）
        # M1 = Q²/(g*A1) + A1*yc1
        # M2 = Q²/(g*A2) + A2*yc2
        # 其中yc为形心深度，对矩形断面 yc = h/2
        A1 = b * h1
        A2 = b * h2_calc
        M1 = Q**2/(g*A1) + A1*h1/2
        M2 = Q**2/(g*A2) + A2*h2_calc/2

        # 动量应相等
        assert abs(M1 - M2) / M1 < 0.01

    def test_flow_regime_transitions(self):
        """测试6：流态转换"""
        b = 2.0
        n = 0.015
        Q = 1.0
        g = 9.81

        # 测试不同坡度下的流态
        slopes = [0.0001, 0.001, 0.002, 0.005, 0.01, 0.05]
        Fr_list = []

        for S0 in slopes:
            channel = RectangularChannel(b=b, n=n, S0=S0)
            solver = UniformFlowSolver(channel)
            results = solver.compute_normal_depth(Q)
            Fr_list.append(results['弗劳德数_Fr'])

        # 坡度增大，Fr应增大（从缓流趋向急流）
        for i in range(len(Fr_list)-1):
            assert Fr_list[i] < Fr_list[i+1]

    def test_specific_energy_curve_points(self):
        """测试7：比能曲线关键点"""
        b = 2.0
        Q = 1.0
        g = 9.81

        # 测试不同水深的比能
        depths = [0.2, 0.3, 0.5, 0.8, 1.0]
        E_list = []

        for h in depths:
            v = Q / (b * h)
            E = h + v**2 / (2*g)
            E_list.append(E)

        # 找到比能最小值（临界点）
        E_min = min(E_list)
        idx_min = E_list.index(E_min)

        # 临界水深
        hc = (Q**2 / (g * b**2))**(1/3)

        # 比能最小值应出现在接近临界水深的位置
        h_at_min = depths[idx_min]
        assert abs(h_at_min - hc) / hc < 0.2  # 允许20%误差（因为采样点有限）

    def test_minimum_specific_energy(self):
        """测试8：最小比能"""
        b = 2.0
        Q = 1.0
        g = 9.81

        # 临界水深
        hc = (Q**2 / (g * b**2))**(1/3)

        # 最小比能 Ec = 1.5 * hc
        Ec_theoretical = 1.5 * hc

        # 计算临界比能
        vc = Q / (b * hc)
        Ec_calculated = hc + vc**2 / (2*g)

        # 验证
        assert abs(Ec_calculated - Ec_theoretical) / Ec_theoretical < 0.001

    def test_subcritical_flow_properties(self):
        """测试9：缓流特性"""
        b = 2.0
        n = 0.015
        S0 = 0.002  # 缓坡
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h0 = results['水深_h']
        hc = channel.compute_critical_depth(Q)
        Fr = results['弗劳德数_Fr']

        # 缓流：h0 > hc, Fr < 1
        assert h0 > hc
        assert Fr < 1
        assert results['流态'] == "缓流"

    def test_supercritical_flow_properties(self):
        """测试10：急流特性"""
        b = 2.0
        n = 0.015
        S0 = 0.05  # 陡坡
        Q = 1.0

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h0 = results['水深_h']
        hc = channel.compute_critical_depth(Q)
        Fr = results['弗劳德数_Fr']

        # 急流：h0 < hc, Fr > 1
        assert h0 < hc
        assert Fr > 1
        assert results['流态'] == "急流"


class TestEdgeCases:
    """边界条件测试"""

    def test_very_small_flow(self):
        """测试极小流量"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 0.01  # 极小流量

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        assert results['水深_h'] > 0
        assert results['流速_v'] > 0

    def test_very_large_flow(self):
        """测试极大流量"""
        b = 2.0
        n = 0.015
        S0 = 0.002
        Q = 50.0  # 极大流量

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        assert results['水深_h'] > 0
        assert results['水深_h'] < 10.0

    def test_critical_slope(self):
        """测试临界坡度附近"""
        b = 2.0
        n = 0.015
        Q = 1.0

        # 寻找临界坡度（使h0 = hc）
        # 这需要迭代，这里简化为测试接近临界的情况
        channel = RectangularChannel(b=b, n=n, S0=0.003)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # Fr应该接近1
        assert 0.5 < results['弗劳德数_Fr'] < 1.5


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
