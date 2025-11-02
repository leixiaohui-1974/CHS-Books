"""
test_solvers.py - 求解器模块测试
=================================
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath('..'))

from gwflow.solvers.steady_state import (
    solve_1d_steady_gw,
    solve_2d_steady_gw,
    compute_darcy_velocity
)
from gwflow.solvers.transient import (
    solve_2d_transient_gw,
    compute_drawdown
)


class TestSteadyState1D:
    """一维稳态求解器测试"""
    
    def test_solve_1d_linear(self):
        """测试线性问题的精确求解"""
        K = 10.0
        L = 1000.0
        h0 = 20.0
        hL = 10.0
        nx = 51
        
        h = solve_1d_steady_gw(K, L, h0, hL, nx)
        
        # 检查边界条件
        assert np.isclose(h[0], h0)
        assert np.isclose(h[-1], hL)
        
        # 检查与解析解的吻合度
        x = np.linspace(0, L, nx)
        h_analytical = h0 + (hL - h0) * x / L
        
        rmse = np.sqrt(np.mean((h - h_analytical)**2))
        assert rmse < 1e-10
    
    def test_solve_1d_with_source(self):
        """测试带源汇项的问题"""
        K = 10.0
        L = 1000.0
        h0 = 20.0
        hL = 10.0
        nx = 51
        
        # 添加均匀补给
        R = 0.001  # m/day
        source = R * np.ones(nx)
        
        h = solve_1d_steady_gw(K, L, h0, hL, nx, source=source)
        
        # 边界条件应该仍然满足
        assert np.isclose(h[0], h0)
        assert np.isclose(h[-1], hL)
        
        # 由于有补给，中间的水头应该比无补给时高
        h_no_source = solve_1d_steady_gw(K, L, h0, hL, nx)
        assert np.all(h[1:-1] >= h_no_source[1:-1])
    
    def test_solve_1d_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            solve_1d_steady_gw(K=-10.0, L=1000.0, h0=20.0, hL=10.0, nx=50)
        
        with pytest.raises(ValueError):
            solve_1d_steady_gw(K=10.0, L=-1000.0, h0=20.0, hL=10.0, nx=50)
        
        with pytest.raises(ValueError):
            solve_1d_steady_gw(K=10.0, L=1000.0, h0=20.0, hL=10.0, nx=1)
    
    def test_solve_1d_convergence(self):
        """测试网格收敛性"""
        K = 10.0
        L = 1000.0
        h0 = 20.0
        hL = 10.0
        
        grid_sizes = [11, 21, 51, 101]
        errors = []
        
        for nx in grid_sizes:
            h = solve_1d_steady_gw(K, L, h0, hL, nx)
            x = np.linspace(0, L, nx)
            h_analytical = h0 + (hL - h0) * x / L
            rmse = np.sqrt(np.mean((h - h_analytical)**2))
            errors.append(rmse)
        
        # 所有误差应该都非常小（接近机器精度）
        assert all(e < 1e-10 for e in errors)


class TestSteadyState2D:
    """二维稳态求解器测试"""
    
    def test_solve_2d_basic(self):
        """测试基本的二维求解"""
        K = 10.0
        Lx, Ly = 1000.0, 800.0
        nx, ny = 21, 17
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 20.0},
            'right': {'type': 'dirichlet', 'value': 10.0},
            'bottom': {'type': 'neumann', 'value': 0.0},
            'top': {'type': 'neumann', 'value': 0.0}
        }
        
        h = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc)
        
        assert h.shape == (ny, nx)
        
        # 检查边界条件
        assert np.allclose(h[:, 0], 20.0)
        assert np.allclose(h[:, -1], 10.0)
    
    def test_solve_2d_homogeneous_K(self):
        """测试均质介质"""
        K = 10.0 * np.ones((17, 21))
        Lx, Ly = 1000.0, 800.0
        nx, ny = 21, 17
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 15.0},
            'right': {'type': 'dirichlet', 'value': 15.0},
            'bottom': {'type': 'dirichlet', 'value': 15.0},
            'top': {'type': 'dirichlet', 'value': 15.0}
        }
        
        h = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc)
        
        # 所有边界都是15.0，解应该是常数15.0
        assert np.allclose(h, 15.0, atol=1e-6)
    
    def test_solve_2d_with_heterogeneous_K(self):
        """测试非均质介质"""
        nx, ny = 21, 17
        K = np.ones((ny, nx)) * 10.0
        # 在中间设置一个低渗透区域
        K[ny//4:3*ny//4, nx//4:3*nx//4] = 1.0
        
        Lx, Ly = 1000.0, 800.0
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 20.0},
            'right': {'type': 'dirichlet', 'value': 10.0},
            'bottom': {'type': 'neumann', 'value': 0.0},
            'top': {'type': 'neumann', 'value': 0.0}
        }
        
        h = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc)
        
        # 边界条件应该满足
        assert np.allclose(h[:, 0], 20.0)
        assert np.allclose(h[:, -1], 10.0)
        
        # 水头应该在合理范围内
        assert np.all(h >= 10.0) and np.all(h <= 20.0)


class TestDarcyVelocity:
    """达西速度计算测试"""
    
    def test_compute_darcy_velocity_1d(self):
        """测试一维达西速度计算"""
        # 创建简单的线性水头分布
        nx = 51
        L = 1000.0
        h0 = 20.0
        hL = 10.0
        x = np.linspace(0, L, nx)
        h = h0 + (hL - h0) * x / L
        h_2d = h[np.newaxis, :]  # 转换为2D以便使用compute_darcy_velocity
        
        K = 10.0
        dx = L / (nx - 1)
        dy = 1.0
        
        vx, vy = compute_darcy_velocity(h_2d, K, dx, dy)
        
        # 理论速度
        v_theory = -K * (hL - h0) / L
        
        # 检查x方向速度
        assert np.allclose(vx[0, :], v_theory, rtol=0.01)
    
    def test_compute_darcy_velocity_2d(self):
        """测试二维达西速度计算"""
        ny, nx = 17, 21
        Lx, Ly = 1000.0, 800.0
        K = 10.0
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 20.0},
            'right': {'type': 'dirichlet', 'value': 10.0},
            'bottom': {'type': 'neumann', 'value': 0.0},
            'top': {'type': 'neumann', 'value': 0.0}
        }
        
        h = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc)
        
        dx = Lx / (nx - 1)
        dy = Ly / (ny - 1)
        
        vx, vy = compute_darcy_velocity(h, K, dx, dy)
        
        # 检查形状
        assert vx.shape == (ny, nx - 1)
        assert vy.shape == (ny - 1, nx)
        
        # x方向速度应该为正（从高水头流向低水头）
        assert np.all(vx > 0)


class TestTransient2D:
    """二维瞬态求解器测试"""
    
    def test_solve_2d_transient_basic(self):
        """测试基本的瞬态求解"""
        K = 10.0
        S = 0.001
        Lx, Ly = 1000.0, 800.0
        nx, ny = 21, 17
        dt = 1.0
        nt = 10
        
        initial_h = 15.0 * np.ones((ny, nx))
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 20.0},
            'right': {'type': 'dirichlet', 'value': 10.0},
            'bottom': {'type': 'neumann', 'value': 0.0},
            'top': {'type': 'neumann', 'value': 0.0}
        }
        
        h_history = solve_2d_transient_gw(
            K, S, Lx, Ly, nx, ny, dt, nt,
            initial_h, bc, method='implicit'
        )
        
        # 检查时间步数
        assert len(h_history) == nt + 1  # 包括初始条件
        
        # 检查每个时间步的形状
        for h in h_history:
            assert h.shape == (ny, nx)
        
        # 边界条件应该始终满足
        for h in h_history:
            assert np.allclose(h[:, 0], 20.0)
            assert np.allclose(h[:, -1], 10.0)
    
    def test_solve_2d_transient_convergence_to_steady(self):
        """测试瞬态解收敛到稳态解"""
        K = 10.0
        S = 0.001
        Lx, Ly = 1000.0, 800.0
        nx, ny = 21, 17
        dt = 1.0
        nt = 1000  # 长时间模拟
        
        initial_h = 15.0 * np.ones((ny, nx))
        
        bc = {
            'left': {'type': 'dirichlet', 'value': 20.0},
            'right': {'type': 'dirichlet', 'value': 10.0},
            'bottom': {'type': 'neumann', 'value': 0.0},
            'top': {'type': 'neumann', 'value': 0.0}
        }
        
        # 瞬态求解
        h_history = solve_2d_transient_gw(
            K, S, Lx, Ly, nx, ny, dt, nt,
            initial_h, bc, method='implicit'
        )
        
        # 稳态求解
        h_steady = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc)
        
        # 最终时刻应该接近稳态解
        h_final = h_history[-1]
        rmse = np.sqrt(np.mean((h_final - h_steady)**2))
        
        assert rmse < 0.1  # 应该足够接近
    
    def test_compute_drawdown(self):
        """测试降深计算"""
        initial_h = 15.0 * np.ones((17, 21))
        
        h_history = [
            initial_h,
            initial_h - 1.0,
            initial_h - 2.0,
            initial_h - 3.0
        ]
        
        drawdown_history = compute_drawdown(h_history, initial_h)
        
        assert len(drawdown_history) == len(h_history)
        assert np.allclose(drawdown_history[0], 0.0)
        assert np.allclose(drawdown_history[1], 1.0)
        assert np.allclose(drawdown_history[2], 2.0)
        assert np.allclose(drawdown_history[3], 3.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
