"""
简单测试运行器（不依赖pytest）
================================
"""

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import numpy as np
from gwflow.grid.structured import create_1d_grid, create_2d_grid
from gwflow.solvers.steady_state import solve_1d_steady_gw, solve_2d_steady_gw


def test_1d_grid():
    """测试一维网格生成"""
    print("测试: 一维网格生成 ... ", end="")
    try:
        L = 1000.0
        nx = 51
        x, dx = create_1d_grid(L, nx)
        
        assert len(x) == nx
        assert x[0] == 0.0
        assert abs(x[-1] - L) < 1e-10
        assert abs(dx - L / (nx - 1)) < 1e-10
        
        print("✓ 通过")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False


def test_2d_grid():
    """测试二维网格生成"""
    print("测试: 二维网格生成 ... ", end="")
    try:
        Lx, Ly = 1000.0, 800.0
        nx, ny = 51, 41
        X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
        
        assert X.shape == (ny, nx)
        assert Y.shape == (ny, nx)
        assert abs(X[0, 0] - 0.0) < 1e-10
        assert abs(X[0, -1] - Lx) < 1e-10
        
        print("✓ 通过")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False


def test_1d_steady_solver():
    """测试一维稳态求解器"""
    print("测试: 一维稳态求解器 ... ", end="")
    try:
        K = 10.0
        L = 1000.0
        h0 = 20.0
        hL = 10.0
        nx = 51
        
        h = solve_1d_steady_gw(K, L, h0, hL, nx)
        
        # 检查边界条件
        assert abs(h[0] - h0) < 1e-10
        assert abs(h[-1] - hL) < 1e-10
        
        # 检查与解析解的吻合度
        x = np.linspace(0, L, nx)
        h_analytical = h0 + (hL - h0) * x / L
        rmse = np.sqrt(np.mean((h - h_analytical)**2))
        
        assert rmse < 1e-10
        
        print(f"✓ 通过 (RMSE={rmse:.2e})")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False


def test_2d_steady_solver():
    """测试二维稳态求解器"""
    print("测试: 二维稳态求解器 ... ", end="")
    try:
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
        assert np.allclose(h[:, 0], 20.0)
        assert np.allclose(h[:, -1], 10.0)
        
        print("✓ 通过")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("地下水动力学模型工具包 - 简单测试")
    print("=" * 60)
    print()
    
    tests = [
        test_1d_grid,
        test_2d_grid,
        test_1d_steady_solver,
        test_2d_steady_solver,
    ]
    
    results = []
    for test_func in tests:
        results.append(test_func())
    
    print()
    print("=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 有测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
