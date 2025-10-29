"""
案例2单元测试：城市雨水排水渠设计

测试内容：
1. 正常水深计算
2. 临界水深计算
3. 流态判别
4. 流速校核
5. 断面尺寸计算
6. 边界条件测试

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


class TestCase02DrainageDesign:
    """案例2：城市雨水排水渠设计测试"""

    def test_normal_depth_calculation(self):
        """测试1：正常水深计算"""
        # 标准参数
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 验证水深在合理范围内
        assert results['水深_h'] > 0
        assert results['水深_h'] < 2.0  # 小型排水渠，水深不应太大

        # 验证曼宁公式：Q = A * (1/n) * R^(2/3) * S0^(1/2)
        h = results['水深_h']
        A = b * h
        chi = b + 2 * h
        R = A / chi
        Q_calc = A * (1/n) * R**(2/3) * np.sqrt(S0)

        # 流量误差应小于1%
        assert abs(Q_calc - Q) / Q < 0.01

    def test_critical_depth_calculation(self):
        """测试2：临界水深计算"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)

        # 矩形渠道临界水深：hc = (q²/g)^(1/3)
        q = Q / b  # 单宽流量
        g = 9.81
        hc_theoretical = (q**2 / g)**(1/3)

        # 数值计算临界水深
        hc_numerical = channel.compute_critical_depth(Q)

        # 两者应该非常接近（误差<0.1%）
        assert abs(hc_numerical - hc_theoretical) / hc_theoretical < 0.001

    def test_flow_regime_identification(self):
        """测试3：流态判别"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h0 = results['水深_h']
        Fr = results['弗劳德数_Fr']
        flow_type = results['流态']

        # 验证弗劳德数计算
        v = results['流速_v']
        g = 9.81
        Fr_calc = v / np.sqrt(g * h0)
        assert abs(Fr_calc - Fr) < 0.01

        # 验证流态判别逻辑
        if Fr < 1:
            assert flow_type == "缓流"
        elif Fr > 1:
            assert flow_type == "急流"
        else:
            assert flow_type == "临界流"

        # 对于本例（S0=0.003），应该是缓流
        assert Fr < 1
        assert flow_type == "缓流"

    def test_velocity_check(self):
        """测试4：流速校核"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        v = results['流速_v']

        # 流速应在合理范围内
        v_min = 0.6  # 防淤积
        v_max = 3.0  # 防冲刷（混凝土）

        assert v > v_min, f"流速{v:.2f}m/s过小，可能淤积"
        assert v < v_max, f"流速{v:.2f}m/s过大，可能冲刷"

    def test_channel_dimensions(self):
        """测试5：断面尺寸计算"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        h0 = results['水深_h']

        # 安全超高（取水深的25%）
        delta_h = 0.25 * h0
        H_total = h0 + delta_h

        # 总深度应合理
        assert H_total > h0
        assert H_total < 1.5 * h0  # 安全超高不应太大

        # 宽深比应合理（一般2-5之间）
        width_depth_ratio = b / h0
        assert 2 < width_depth_ratio < 6

    def test_slope_variation(self):
        """测试6：坡度影响测试"""
        b = 1.5
        n = 0.013
        Q = 1.2

        # 测试不同坡度
        slopes = [0.001, 0.002, 0.003, 0.005, 0.01]
        h_list = []

        for S0 in slopes:
            channel = RectangularChannel(b=b, n=n, S0=S0)
            solver = UniformFlowSolver(channel)
            results = solver.compute_normal_depth(Q)
            h_list.append(results['水深_h'])

        # 坡度增大，水深应减小（流速增大）
        for i in range(len(h_list)-1):
            assert h_list[i] > h_list[i+1], "坡度增大时水深应减小"

    def test_roughness_variation(self):
        """测试7：糙率影响测试"""
        b = 1.5
        S0 = 0.003
        Q = 1.2

        # 测试不同糙率
        roughness = [0.011, 0.013, 0.015, 0.020, 0.025]
        h_list = []

        for n in roughness:
            channel = RectangularChannel(b=b, n=n, S0=S0)
            solver = UniformFlowSolver(channel)
            results = solver.compute_normal_depth(Q)
            h_list.append(results['水深_h'])

        # 糙率增大，水深应增大（阻力增大）
        for i in range(len(h_list)-1):
            assert h_list[i] < h_list[i+1], "糙率增大时水深应增大"

    def test_discharge_variation(self):
        """测试8：流量影响测试"""
        b = 1.5
        n = 0.013
        S0 = 0.003

        # 测试不同流量
        discharges = [0.5, 0.8, 1.2, 1.5, 2.0]
        h_list = []
        v_list = []

        for Q in discharges:
            channel = RectangularChannel(b=b, n=n, S0=S0)
            solver = UniformFlowSolver(channel)
            results = solver.compute_normal_depth(Q)
            h_list.append(results['水深_h'])
            v_list.append(results['流速_v'])

        # 流量增大，水深和流速都应增大
        for i in range(len(h_list)-1):
            assert h_list[i] < h_list[i+1], "流量增大时水深应增大"
            assert v_list[i] < v_list[i+1], "流量增大时流速应增大"


class TestEdgeCases:
    """边界条件和特殊情况测试"""

    def test_small_discharge(self):
        """测试小流量情况"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 0.1  # 小流量

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 应该能正常计算
        assert results['水深_h'] > 0
        assert results['流速_v'] > 0
        assert results['弗劳德数_Fr'] > 0

    def test_large_discharge(self):
        """测试大流量情况"""
        b = 1.5
        n = 0.013
        S0 = 0.003
        Q = 10.0  # 大流量

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 应该能正常计算
        assert results['水深_h'] > 0
        assert results['水深_h'] < 5.0  # 水深不应过大
        assert results['流速_v'] > 0

    def test_steep_slope(self):
        """测试陡坡情况"""
        b = 1.5
        n = 0.013
        S0 = 0.05  # 陡坡
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 陡坡可能产生急流
        assert results['水深_h'] > 0
        # 弗劳德数可能大于1（急流）

    def test_mild_slope(self):
        """测试缓坡情况"""
        b = 1.5
        n = 0.013
        S0 = 0.0001  # 缓坡
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 缓坡应该是缓流
        assert results['水深_h'] > 0
        assert results['弗劳德数_Fr'] < 1  # 应该是缓流

    def test_wide_channel(self):
        """测试宽渠道"""
        b = 5.0  # 宽渠道
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 宽渠道水深应该较浅
        assert results['水深_h'] > 0
        assert results['水深_h'] < 0.5  # 宽渠道水深较浅

    def test_narrow_channel(self):
        """测试窄渠道"""
        b = 0.5  # 窄渠道
        n = 0.013
        S0 = 0.003
        Q = 1.2

        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)
        results = solver.compute_normal_depth(Q)

        # 窄渠道水深应该较深
        assert results['水深_h'] > 0
        assert results['水深_h'] > 1.0  # 窄渠道水深较深


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
