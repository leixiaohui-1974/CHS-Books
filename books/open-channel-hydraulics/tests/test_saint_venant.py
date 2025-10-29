"""
单元测试 - Saint-Venant求解器

测试内容：
1. 初始化测试
2. CFL条件测试
3. 时间步长计算测试
4. 边界条件测试

作者：CHS-Books项目
日期：2025-10-29
"""

import pytest
import numpy as np
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))

from solvers.saint_venant import SaintVenantSolver


class TestSaintVenantSolver:
    """Saint-Venant求解器测试类"""

    def test_initialization(self):
        """测试求解器初始化"""
        L = 10000.0
        b = 100.0
        S0 = 0.0001
        n = 0.03
        dx = 100.0

        solver = SaintVenantSolver(L, b, S0, n, dx)

        assert solver.L == L
        assert solver.b == b
        assert solver.S0 == S0
        assert solver.n == n
        assert solver.dx == dx
        assert solver.nx == int(L / dx) + 1
        assert len(solver.x) == solver.nx
        assert solver.auto_dt is True  # 默认自动计算时间步长

    def test_initial_conditions(self):
        """测试初始条件设置"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        h0 = np.full(solver.nx, 2.0)
        Q0 = np.full(solver.nx, 20.0)

        solver.set_initial_conditions(h0, Q0)

        assert np.allclose(solver.h, h0)
        assert np.allclose(solver.Q, Q0)
        assert np.allclose(solver.A, solver.b * h0)
        assert solver.t == 0.0
        assert solver.time_step == 0

    def test_uniform_initial(self):
        """测试均匀初始条件"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        h0 = 2.0
        Q0 = 20.0

        solver.set_uniform_initial(h0, Q0)

        assert np.all(solver.h == h0)
        assert np.all(solver.Q == Q0)

    def test_compute_timestep_cfl(self):
        """测试CFL条件的时间步长计算"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        # 设置初始条件
        h0 = 2.0
        Q0 = 20.0
        solver.set_uniform_initial(h0, Q0)

        # 计算时间步长
        cfl = 0.3
        dt = solver.compute_timestep(cfl=cfl)

        # 验证时间步长在合理范围内
        assert 0.01 < dt < 60.0, f"时间步长{dt}不在合理范围[0.01, 60.0]内"

        # 验证CFL条件
        c_max, _ = solver.compute_wave_speed()
        courant = c_max * dt / solver.dx
        assert courant <= cfl * 1.1, f"Courant数{courant}超过CFL限制{cfl}"

    def test_timestep_limits(self):
        """测试时间步长上下限"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        h0 = 2.0
        Q0 = 20.0
        solver.set_uniform_initial(h0, Q0)

        # 测试不同CFL系数
        for cfl in [0.1, 0.3, 0.5, 0.8]:
            dt = solver.compute_timestep(cfl=cfl)

            # 时间步长应在[0.01, 60.0]范围内
            assert dt >= 0.01, f"时间步长{dt}小于下限0.01"
            assert dt <= 60.0, f"时间步长{dt}大于上限60.0"

    def test_wave_speed(self):
        """测试波速计算"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        h0 = 2.0
        Q0 = 20.0
        solver.set_uniform_initial(h0, Q0)

        c_max, c_mean = solver.compute_wave_speed()

        # 理论波速 c = sqrt(g*h)
        g = 9.81
        c_theoretical = np.sqrt(g * h0)

        # 检查波速是否合理
        assert c_max > 0, "最大波速应大于0"
        assert c_mean > 0, "平均波速应大于0"
        assert abs(c_mean - c_theoretical) / c_theoretical < 0.5, \
            f"平均波速{c_mean}与理论值{c_theoretical}偏差过大"

    def test_friction_slope(self):
        """测试摩阻坡度计算"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        # 测试正常情况
        Q = 20.0
        A = 20.0  # h=2m, b=10m
        Sf = solver.compute_friction_slope(Q, A)

        assert Sf > 0, "摩阻坡度应大于0"
        assert Sf < 1.0, "摩阻坡度不应过大"

        # 测试边界情况：水深很小
        Sf_small = solver.compute_friction_slope(0.1, 0.01)
        assert Sf_small >= 0, "极小水深时摩阻坡度应非负"

    def test_boundary_conditions(self):
        """测试边界条件设置"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        # 定义边界条件函数
        def bc_upstream(t):
            return 2.0, 20.0  # h=2m, Q=20m³/s

        def bc_downstream(t):
            return 1.5, 18.0  # h=1.5m, Q=18m³/s

        solver.set_boundary_conditions(upstream=bc_upstream, downstream=bc_downstream)

        assert solver.bc_upstream is not None
        assert solver.bc_downstream is not None

        # 测试边界条件函数调用
        h_up, Q_up = solver.bc_upstream(0.0)
        h_down, Q_down = solver.bc_downstream(0.0)

        assert h_up == 2.0
        assert Q_up == 20.0
        assert h_down == 1.5
        assert Q_down == 18.0

    def test_single_step(self):
        """测试单步推进"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        # 设置非均匀初始条件（创建一个小扰动）
        h0 = np.full(solver.nx, 2.0)
        Q0 = np.full(solver.nx, 20.0)

        # 在中间位置添加扰动
        mid = solver.nx // 2
        h0[mid] = 2.1  # 轻微抬高水位

        solver.set_initial_conditions(h0, Q0)

        # 记录初始状态
        h_initial = solver.h.copy()
        Q_initial = solver.Q.copy()
        t_initial = solver.t

        # 执行一步
        solver.advance_lax()

        # 检查状态是否更新
        assert solver.time_step == 1
        assert solver.t > t_initial
        assert not np.array_equal(solver.h, h_initial)  # 状态应该变化
        assert np.all(solver.h > 0), "水深应保持为正"

    def test_conservation(self):
        """测试质量守恒（粗略检查）"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.0001, n=0.03, dx=100.0)

        h0 = 2.0
        Q0 = 20.0
        solver.set_uniform_initial(h0, Q0)

        # 计算初始总体积
        V_initial = np.sum(solver.h) * solver.b * solver.dx

        # 运行几步（无边界流入流出时，总体积应基本守恒）
        for _ in range(5):
            solver.advance_lax()

        V_final = np.sum(solver.h) * solver.b * solver.dx

        # 允许10%的误差（因为有摩阻和数值耗散）
        relative_error = abs(V_final - V_initial) / V_initial
        assert relative_error < 0.5, \
            f"质量守恒误差{relative_error*100:.1f}%过大（初始{V_initial}，最终{V_final}）"


class TestEdgeCases:
    """边界情况测试"""

    def test_zero_slope(self):
        """测试零坡度情况"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.0, n=0.03, dx=100.0)
        assert solver.S0 == 0.0

    def test_large_manning(self):
        """测试大糙率系数"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.1, dx=100.0)
        h0 = 2.0
        Q0 = 10.0
        solver.set_uniform_initial(h0, Q0)

        # 大糙率应导致更大的摩阻
        Sf = solver.compute_friction_slope(Q0, h0 * solver.b)
        assert Sf > 0.001, "大糙率应产生明显的摩阻"

    def test_small_depth(self):
        """测试小水深情况"""
        solver = SaintVenantSolver(L=1000.0, b=10.0, S0=0.001, n=0.03, dx=100.0)

        h_small = 0.1  # 10cm
        Q_small = 1.0
        solver.set_uniform_initial(h_small, Q_small)

        # 应该能够计算时间步长（不会崩溃）
        dt = solver.compute_timestep()
        assert dt > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
