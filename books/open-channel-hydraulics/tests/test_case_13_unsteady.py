"""
案例13单元测试：明渠非恒定流基础

测试内容：
1. SaintVenantSolver求解器初始化
2. 初始条件设置（均匀和非均匀）
3. 边界条件设置
4. 波速计算（重力波速度）
5. CFL条件时间步长计算
6. Lax显式格式推进
7. 非恒定流模拟运行
8. 质量守恒验证
9. 洪水波传播特性
10. 数值稳定性验证

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
from solvers.saint_venant import SaintVenantSolver


class TestCase13UnsteadyFlow:
    """案例13：明渠非恒定流基础测试"""

    def test_solver_initialization(self):
        """测试1：求解器初始化"""
        L = 10000.0  # m
        b = 20.0     # m
        S0 = 0.0002
        n = 0.025
        dx = 100.0
        g = 9.81

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, g=g)

        # 验证参数正确存储
        assert solver.L == L
        assert solver.b == b
        assert solver.S0 == S0
        assert solver.n == n
        assert solver.dx == dx
        assert solver.g == g

        # 验证网格节点数
        nx_expected = int(L / dx) + 1
        assert solver.nx == nx_expected

        # 验证空间网格
        assert len(solver.x) == solver.nx
        assert solver.x[0] == 0.0
        assert solver.x[-1] == L

    def test_uniform_initial_conditions(self):
        """测试2：均匀初始条件设置"""
        L = 10000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 2.5  # m
        Q0 = 100.0  # m³/s

        solver.set_uniform_initial(h0, Q0)

        # 验证水深均匀
        assert np.all(solver.h == h0)

        # 验证流量均匀
        assert np.all(solver.Q == Q0)

        # 验证断面面积
        A_expected = b * h0
        assert np.allclose(solver.A, A_expected)

        # 验证流速
        v_expected = Q0 / A_expected
        assert np.allclose(solver.v, v_expected)

        # 验证初始时间
        assert solver.t == 0.0
        assert solver.time_step == 0

    def test_nonuniform_initial_conditions(self):
        """测试3：非均匀初始条件设置"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 非均匀水深（线性变化）
        h_array = np.linspace(2.0, 3.0, solver.nx)
        Q_array = np.full(solver.nx, 50.0)

        solver.set_initial_conditions(h_array, Q_array)

        # 验证水深设置正确
        assert np.allclose(solver.h, h_array)

        # 验证流量设置正确
        assert np.allclose(solver.Q, Q_array)

    def test_wave_speed_calculation(self):
        """测试4：波速计算"""
        L = 10000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0
        g = 9.81

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, g=g)

        h0 = 2.5
        Q0 = 100.0
        solver.set_uniform_initial(h0, Q0)

        c_max, c_mean = solver.compute_wave_speed()

        # 理论波速
        c_theoretical = np.sqrt(g * h0)

        # 验证波速在合理范围
        assert c_max > 0
        assert c_mean > 0

        # 波速应接近理论值（考虑流速影响：c_mean = v + c）
        v0 = Q0 / (b * h0)
        c_mean_expected = v0 + c_theoretical
        assert abs(c_mean - c_mean_expected) < 1.0

    def test_cfl_condition_timestep(self):
        """测试5：CFL条件时间步长计算"""
        L = 10000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0
        g = 9.81

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, g=g)

        h0 = 2.5
        Q0 = 100.0
        solver.set_uniform_initial(h0, Q0)

        cfl = 0.5
        dt = solver.compute_timestep(cfl=cfl)

        # 验证时间步长为正
        assert dt > 0

        # 验证CFL条件
        c_max, _ = solver.compute_wave_speed()
        courant_number = c_max * dt / dx

        # Courant数应 <= cfl
        assert courant_number <= cfl * 1.1  # 允许10%误差

    def test_friction_slope_calculation(self):
        """测试6：摩阻坡度计算"""
        L = 10000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        Q = 100.0
        h = 2.5
        A = b * h

        Sf = solver.compute_friction_slope(Q, A)

        # 摩阻坡度应为正
        assert Sf > 0

        # 摩阻坡度应小于底坡（正常流）
        assert Sf < S0 * 10

        # 验证Manning公式
        P = b + 2*h
        R = A / P
        Sf_theoretical = (n**2 * Q**2) / (A**2 * R**(4.0/3.0))

        assert abs(Sf - Sf_theoretical) < 1e-10

    def test_lax_scheme_single_step(self):
        """测试7：Lax格式单步推进"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=1.0)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 记录初始状态
        h_initial = solver.h.copy()
        Q_initial = solver.Q.copy()

        # 推进一步
        solver.advance_lax()

        # 验证时间更新
        assert solver.t > 0
        assert solver.time_step == 1

        # 对于均匀初始条件和无边界扰动，变化应很小
        # （因为是均匀流，Lax格式数值耗散会引入小扰动）
        h_change = np.abs(solver.h - h_initial)
        assert np.max(h_change) < 1.0  # 最大变化小于1m

    def test_boundary_conditions_constant(self):
        """测试8：常数边界条件"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=1.0)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 设置常数边界条件
        def bc_up(t):
            return h0, Q0

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        # 推进几步
        for _ in range(5):
            solver.advance_lax()

        # 验证边界保持
        assert abs(solver.h[0] - h0) < 0.1
        assert abs(solver.h[-1] - h0) < 0.1

    def test_boundary_conditions_step_change(self):
        """测试9：阶跃边界条件"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 50.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=0.5)

        h0 = 2.0
        Q0 = 50.0
        Q1 = 80.0  # 上游流量增加
        h1 = 2.3   # 对应更大水深

        solver.set_uniform_initial(h0, Q0)

        # 上游阶跃变化
        def bc_up(t):
            if t < 1.0:
                return h0, Q0
            else:
                return h1, Q1

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        # 推进到t=2秒
        while solver.t < 2.0:
            solver.advance_lax()

        # 验证上游流量增加
        assert solver.Q[0] > Q0

        # 验证下游尚未完全响应（波传播需要时间）
        assert abs(solver.Q[-1] - Q0) < 10.0

    def test_short_simulation_run(self):
        """测试10：短时间模拟运行"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 简单边界条件
        def bc_up(t):
            return h0, Q0

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        # 运行短时间模拟
        t_end = 60.0  # 1分钟
        results = solver.run(t_end=t_end, dt_output=10.0, verbose=False)

        # 验证结果结构
        assert 'x' in results
        assert 'times' in results
        assert 'h' in results
        assert 'Q' in results

        # 验证结果维度
        assert len(results['x']) == solver.nx
        assert len(results['times']) > 0
        assert results['h'].shape[0] == len(results['times'])
        assert results['h'].shape[1] == solver.nx

    def test_mass_conservation(self):
        """测试11：质量守恒验证"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 记录初始总体积
        V_initial = np.sum(solver.A) * dx

        # 设置无流量变化的边界
        def bc_up(t):
            return h0, Q0

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        # 推进若干步
        for _ in range(10):
            solver.advance_lax()

        # 计算最终总体积
        V_final = np.sum(solver.A) * dx

        # 质量应近似守恒（允许数值误差）
        mass_error = abs(V_final - V_initial) / V_initial
        assert mass_error < 0.1  # 允许10%误差（Lax格式有耗散）

    def test_flood_wave_propagation(self):
        """测试12：洪水波传播"""
        L = 5000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 初始均匀流
        Q0 = 100.0
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q0)

        solver.set_uniform_initial(h0, Q0)

        # 上游流量突然增加
        Q1 = 150.0
        h1 = channel.compute_normal_depth(Q1)

        def bc_up(t):
            if t < 1.0:
                return h0, Q0
            else:
                return h1, Q1

        # 下游采用自由边界（外推）
        solver.set_boundary_conditions(bc_up, None)

        # 运行模拟
        t_end = 600.0  # 10分钟
        results = solver.run(t_end=t_end, dt_output=60.0, verbose=False)

        # 验证洪峰传播
        Q_results = results['Q']
        h_results = results['h']

        # 上游应有流量增加
        assert Q_results[-1, 0] > Q0 * 1.2

        # 验证洪水波向下游传播（中游有水深增加）
        mid_point = len(results['x']) // 2
        h_mid_final = h_results[-1, mid_point]
        h_mid_initial = h_results[0, mid_point]
        assert h_mid_final > h_mid_initial


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_initial_velocity(self):
        """测试静水初始条件"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 静水：流量为零
        h0 = 2.0
        Q0 = 0.0

        solver.set_uniform_initial(h0, Q0)

        # 验证初始流速为零
        assert np.all(solver.v == 0.0)

    def test_steep_slope(self):
        """测试陡坡"""
        L = 1000.0
        b = 10.0
        S0 = 0.01  # 陡坡
        n = 0.020
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 1.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 应能正常初始化
        assert solver.h is not None
        assert solver.Q is not None

    def test_mild_slope(self):
        """测试缓坡"""
        L = 10000.0
        b = 20.0
        S0 = 0.00001  # 非常缓的坡
        n = 0.025
        dx = 100.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 3.0
        Q0 = 100.0
        solver.set_uniform_initial(h0, Q0)

        # 应能正常初始化
        assert solver.h is not None
        assert solver.Q is not None

    def test_small_discharge(self):
        """测试小流量"""
        L = 1000.0
        b = 5.0
        S0 = 0.001
        n = 0.020
        dx = 50.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 0.5
        Q0 = 1.0  # 小流量
        solver.set_uniform_initial(h0, Q0)

        # 应能正常计算波速
        c_max, c_mean = solver.compute_wave_speed()
        assert c_max > 0
        assert c_mean > 0

    def test_large_discharge(self):
        """测试大流量"""
        L = 10000.0
        b = 50.0  # 宽河道
        S0 = 0.0005
        n = 0.030
        dx = 200.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 5.0
        Q0 = 1000.0  # 大流量
        solver.set_uniform_initial(h0, Q0)

        # 应能正常计算
        assert solver.h is not None
        assert solver.Q is not None

        # 波速应合理
        c_max, _ = solver.compute_wave_speed()
        assert 0 < c_max < 50  # 波速在合理范围

    def test_fine_grid(self):
        """测试细网格"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 10.0  # 细网格

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 节点数应增加
        assert solver.nx == int(L / dx) + 1
        assert solver.nx > 50

    def test_coarse_grid(self):
        """测试粗网格"""
        L = 10000.0
        b = 20.0
        S0 = 0.0002
        n = 0.025
        dx = 500.0  # 粗网格

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        # 节点数应较少
        assert solver.nx == int(L / dx) + 1
        assert solver.nx < 50

    def test_auto_timestep_mode(self):
        """测试自动时间步长模式"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0

        # 不指定dt，应自动计算
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 验证自动dt模式
        assert solver.auto_dt == True

        # 推进一步应自动计算dt
        solver.advance_lax()

        # dt应被自动设置
        assert solver.dt is not None
        assert solver.dt > 0

    def test_fixed_timestep_mode(self):
        """测试固定时间步长模式"""
        L = 1000.0
        b = 10.0
        S0 = 0.001
        n = 0.020
        dx = 100.0
        dt_fixed = 2.0

        # 指定固定dt
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=dt_fixed)

        h0 = 2.0
        Q0 = 50.0
        solver.set_uniform_initial(h0, Q0)

        # 验证固定dt模式
        assert solver.auto_dt == False
        assert solver.dt == dt_fixed

        # 推进一步，dt应保持不变
        solver.advance_lax()
        assert solver.dt == dt_fixed

    def test_very_short_channel(self):
        """测试极短河道"""
        L = 100.0  # 100米
        b = 5.0
        S0 = 0.002
        n = 0.020
        dx = 10.0

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx)

        h0 = 1.0
        Q0 = 10.0
        solver.set_uniform_initial(h0, Q0)

        # 应能正常计算
        assert solver.nx == int(L / dx) + 1


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
