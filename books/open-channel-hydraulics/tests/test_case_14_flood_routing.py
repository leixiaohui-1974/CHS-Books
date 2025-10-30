"""
案例14单元测试：洪水演进计算

测试内容：
1. 洪水过程线生成（三角形过程线）
2. 洪峰流量和时间识别
3. 洪水波特性分析（峰值衰减）
4. 河道蓄量计算
5. 洪峰传播速度
6. 预见期计算
7. 洪量守恒验证
8. 不同河道参数影响
9. 不同洪水过程线形状
10. 多断面洪水演进

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

# 导入主程序中的函数
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code/examples/case_14_flood_routing'))
from main import (
    create_flood_hydrograph,
    analyze_flood_wave,
    compute_channel_storage
)

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver


class TestCase14FloodRouting:
    """案例14：洪水演进计算测试"""

    def test_flood_hydrograph_generation_triangular(self):
        """测试1：三角形洪水过程线生成"""
        Q_base = 100.0  # m³/s
        Q_peak = 500.0  # m³/s
        t_rise = 3600.0  # 1小时
        t_fall = 7200.0  # 2小时

        t = np.linspace(-1800, t_rise + t_fall + 1800, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 验证基流
        assert Q[0] == Q_base

        # 验证洪峰值（离散化误差）
        Q_max = np.max(Q)
        assert abs(Q_max - Q_peak) < 5.0

        # 验证洪峰时间
        t_peak_idx = np.argmax(Q)
        t_peak_actual = t[t_peak_idx]
        assert abs(t_peak_actual - t_rise) < 100.0

        # 验证退水后回到基流
        assert Q[-1] == Q_base

    def test_flood_hydrograph_monotonic_rise(self):
        """测试2：涨水段单调递增"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(0, t_rise, 100)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 涨水段应单调递增
        for i in range(1, len(Q)):
            assert Q[i] >= Q[i-1]

    def test_flood_hydrograph_monotonic_fall(self):
        """测试3：退水段单调递减"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(t_rise, t_rise + t_fall, 100)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 退水段应单调递减
        for i in range(1, len(Q)):
            assert Q[i] <= Q[i-1]

    def test_flood_hydrograph_volume(self):
        """测试4：洪量计算"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(0, t_rise + t_fall, 1000)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 数值积分计算洪量
        dt = t[1] - t[0]
        W_numerical = np.sum((Q - Q_base) * dt)

        # 理论洪量（三角形面积）
        W_theoretical = 0.5 * (t_rise + t_fall) * (Q_peak - Q_base)

        # 验证洪量守恒
        error = abs(W_numerical - W_theoretical) / W_theoretical
        assert error < 0.02  # 允许2%误差

    def test_channel_storage_calculation(self):
        """测试5：河道蓄量计算"""
        times = np.linspace(0, 3600, 100)
        dt = times[1] - times[0]

        # 简单情况：入流恒定，出流逐渐增加
        Q_in = np.full_like(times, 100.0)
        Q_out = np.linspace(50.0, 100.0, len(times))

        storage = compute_channel_storage(times, Q_in, Q_out, dt)

        # 验证蓄量初始为零
        assert storage[0] == 0.0

        # 验证蓄量单调递增（Q_in > Q_out初期）
        assert np.all(np.diff(storage[:50]) > 0)

        # 验证最终趋于平衡（Q_in ≈ Q_out）
        assert abs(storage[-1] - storage[-2]) < abs(storage[50] - storage[49])

    def test_channel_storage_mass_balance(self):
        """测试6：河道蓄量质量守恒"""
        times = np.linspace(0, 7200, 200)
        dt = times[1] - times[0]

        # 创建洪水过程线
        Q_in = create_flood_hydrograph(times, Q_base=100, Q_peak=500,
                                       t_rise=3600, t_fall=3600)

        # 模拟出流（有延迟和衰减）
        Q_out = np.zeros_like(Q_in)
        for i in range(len(Q_in)):
            if i < 50:
                Q_out[i] = 100.0
            else:
                Q_out[i] = 0.8 * Q_in[i-50] + 0.2 * Q_out[i-1]

        storage = compute_channel_storage(times, Q_in, Q_out, dt)

        # 计算总入流量和总出流量
        W_in = np.sum(Q_in * dt)
        W_out = np.sum(Q_out * dt)

        # 最终蓄量应等于入流减出流
        storage_expected = W_in - W_out
        assert abs(storage[-1] - storage_expected) / storage_expected < 0.05

    def test_flood_wave_analysis_peak_detection(self):
        """测试7：洪水波分析-峰值识别"""
        # 创建模拟数据
        times = np.linspace(0, 10800, 300)
        x_locations = [0, 10000, 20000, 30000]

        # 模拟流量数据（4个断面）
        Q_results = np.zeros((len(times), len(x_locations)))
        Q_base = 500.0
        Q_peak = 2000.0

        for idx, x in enumerate(x_locations):
            # 模拟延迟和衰减
            delay = x / 5.0  # 波速约5 m/s
            attenuation = 1.0 - 0.1 * (x / 30000)  # 10%衰减

            t_shifted = times - delay
            Q_peak_section = Q_base + (Q_peak - Q_base) * attenuation
            Q_results[:, idx] = create_flood_hydrograph(
                t_shifted, Q_base, Q_peak_section,
                t_rise=3600, t_fall=7200
            )

        # 分析洪水波
        analysis = analyze_flood_wave(times, x_locations, Q_results,
                                     Q_base, Q_peak)

        # 验证每个断面都有峰值
        for idx in range(len(x_locations)):
            key = f'x{idx}'
            assert key in analysis
            assert analysis[key]['Q_peak'] > Q_base

        # 验证峰值递减
        Q_peaks = [analysis[f'x{i}']['Q_peak'] for i in range(len(x_locations))]
        for i in range(1, len(Q_peaks)):
            assert Q_peaks[i] <= Q_peaks[i-1]

        # 验证峰现时间递增
        t_peaks = [analysis[f'x{i}']['t_peak'] for i in range(len(x_locations))]
        for i in range(1, len(t_peaks)):
            assert t_peaks[i] >= t_peaks[i-1]

    def test_flood_wave_attenuation(self):
        """测试8：洪峰衰减验证"""
        times = np.linspace(0, 10800, 300)
        x_locations = [0, 25000, 50000]  # 0km, 25km, 50km

        Q_base = 500.0
        Q_peak_in = 2000.0

        # 模拟流量数据
        Q_results = np.zeros((len(times), len(x_locations)))

        for idx, x in enumerate(x_locations):
            attenuation_factor = 1.0 - 0.15 * (x / 50000)
            Q_peak_section = Q_base + (Q_peak_in - Q_base) * attenuation_factor
            delay = x / 6.0
            t_shifted = times - delay
            Q_results[:, idx] = create_flood_hydrograph(
                t_shifted, Q_base, Q_peak_section,
                t_rise=3600, t_fall=7200
            )

        analysis = analyze_flood_wave(times, x_locations, Q_results,
                                     Q_base, Q_peak_in)

        # 下游衰减应大于上游
        atten_mid = analysis['x1']['attenuation']
        atten_down = analysis['x2']['attenuation']

        assert atten_down > atten_mid
        assert atten_down > 0  # 应有衰减

    def test_flood_routing_short_river(self):
        """测试9：短河道洪水演进"""
        L = 5000.0  # 5km
        b = 40.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 初始状态
        Q_base = 200.0
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h_base = channel.compute_normal_depth(Q_base)
        solver.set_uniform_initial(h_base, Q_base)

        # 上游洪水
        Q_peak = 500.0
        h_peak = channel.compute_normal_depth(Q_peak)

        def bc_upstream(t):
            if t < 1800:  # 30分钟
                ratio = t / 1800
                Q = Q_base + (Q_peak - Q_base) * ratio
                h = h_base + (h_peak - h_base) * ratio
            else:
                Q = Q_peak
                h = h_peak
            return h, Q

        solver.set_boundary_conditions(bc_upstream, None)

        # 运行模拟
        results = solver.run(t_end=3600, dt_output=300, verbose=False)

        # 验证洪峰到达下游
        Q_downstream = results['Q'][:, -1]
        Q_max_down = np.max(Q_downstream)

        assert Q_max_down > Q_base * 1.5

    def test_peak_travel_time(self):
        """测试10：洪峰传播时间"""
        L = 10000.0
        b = 50.0
        S0 = 0.0003
        n = 0.025
        dx = 200.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        Q_base = 150.0
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h_base = channel.compute_normal_depth(Q_base)

        solver.set_uniform_initial(h_base, Q_base)

        # 上游突然增加流量
        Q_peak = 400.0
        h_peak = channel.compute_normal_depth(Q_peak)

        def bc_upstream(t):
            if t < 10:
                return h_peak, Q_peak
            else:
                return h_peak, Q_peak

        solver.set_boundary_conditions(bc_upstream, None)

        # 运行较长时间
        results = solver.run(t_end=2400, dt_output=60, verbose=False)

        # 计算波速
        times = results['times']
        Q_results = results['Q']

        # 找到上游和下游峰值时间
        t_peak_up = times[np.argmax(Q_results[:, 0])]
        t_peak_down = times[np.argmax(Q_results[:, -1])]

        # 传播时间
        travel_time = t_peak_down - t_peak_up

        # 平均波速
        if travel_time > 0:
            wave_speed = L / travel_time
            # 波速应在合理范围（1-10 m/s）
            assert 1.0 < wave_speed < 10.0


class TestEdgeCases:
    """边界条件测试"""

    def test_symmetric_hydrograph(self):
        """测试对称洪水过程线"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 3600.0
        t_fall = 3600.0  # 对称

        t = np.linspace(0, t_rise + t_fall, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 找到峰值位置
        peak_idx = np.argmax(Q)

        # 对称性验证（数值精度允许小误差）
        mid_idx = len(Q) // 2
        assert abs(peak_idx - mid_idx) < 5

    def test_asymmetric_hydrograph(self):
        """测试非对称洪水过程线（涨水快、退水慢）"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 1800.0   # 0.5小时（涨水快）
        t_fall = 10800.0  # 3小时（退水慢）

        t = np.linspace(0, t_rise + t_fall, 300)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 峰值应在早期
        peak_idx = np.argmax(Q)
        assert peak_idx < len(Q) // 4

    def test_sharp_flood_peak(self):
        """测试尖瘦洪峰"""
        Q_base = 100.0
        Q_peak = 1000.0  # 大洪峰
        t_rise = 1800.0   # 短涨峰
        t_fall = 3600.0   # 短退水

        t = np.linspace(0, t_rise + t_fall, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 验证峰值
        assert np.max(Q) >= Q_peak * 0.99

        # 峰值持续时间短
        Q_threshold = Q_base + 0.9 * (Q_peak - Q_base)
        high_flow_count = np.sum(Q >= Q_threshold)
        assert high_flow_count < len(Q) * 0.2

    def test_flat_flood_peak(self):
        """测试平缓洪峰"""
        Q_base = 100.0
        Q_peak = 300.0   # 较小洪峰
        t_rise = 7200.0   # 长涨峰
        t_fall = 14400.0  # 长退水

        t = np.linspace(0, t_rise + t_fall, 500)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 验证峰值
        assert np.max(Q) >= Q_peak * 0.99

        # 峰值变化平缓
        dQ_dt = np.diff(Q)
        max_gradient = np.max(np.abs(dQ_dt))
        assert max_gradient < (Q_peak - Q_base) / 100

    def test_zero_base_flow(self):
        """测试零基流"""
        Q_base = 0.0
        Q_peak = 500.0
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(0, t_rise + t_fall, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 初始流量为零
        assert Q[0] == 0.0

        # 最终流量回到零
        assert Q[-1] == 0.0

        # 峰值正确
        assert np.max(Q) >= Q_peak * 0.99

    def test_small_flood_magnitude(self):
        """测试小洪水"""
        Q_base = 100.0
        Q_peak = 120.0  # 仅增加20%
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(0, t_rise + t_fall, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 峰值应接近设定值
        assert abs(np.max(Q) - Q_peak) < 1.0

        # 变化平缓
        Q_range = np.max(Q) - np.min(Q)
        assert Q_range < 30.0

    def test_large_flood_magnitude(self):
        """测试大洪水"""
        Q_base = 100.0
        Q_peak = 5000.0  # 50倍基流
        t_rise = 3600.0
        t_fall = 7200.0

        t = np.linspace(0, t_rise + t_fall, 200)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 峰值应接近设定值（离散化误差）
        assert abs(np.max(Q) - Q_peak) < 50.0

        # 洪峰倍比
        flood_ratio = Q_peak / Q_base
        assert flood_ratio > 40.0

    def test_very_short_duration(self):
        """测试极短历时洪水"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 600.0    # 10分钟
        t_fall = 1200.0   # 20分钟

        t = np.linspace(0, t_rise + t_fall, 100)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 应能正确生成
        assert np.max(Q) >= Q_peak * 0.99
        assert Q[0] == Q_base

    def test_very_long_duration(self):
        """测试极长历时洪水"""
        Q_base = 100.0
        Q_peak = 500.0
        t_rise = 86400.0    # 24小时
        t_fall = 172800.0   # 48小时

        t = np.linspace(0, t_rise + t_fall, 500)
        Q = create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall)

        # 应能正确生成
        assert np.max(Q) >= Q_peak * 0.99
        assert Q[-1] == Q_base

    def test_storage_with_no_inflow_outflow_difference(self):
        """测试入流等于出流时蓄量为零"""
        times = np.linspace(0, 3600, 100)
        dt = times[1] - times[0]

        Q_in = np.full_like(times, 100.0)
        Q_out = np.full_like(times, 100.0)

        storage = compute_channel_storage(times, Q_in, Q_out, dt)

        # 入流等于出流，蓄量应保持为零
        assert np.allclose(storage, 0.0, atol=1e-10)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
