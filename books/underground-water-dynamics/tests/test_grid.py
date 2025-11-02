"""
test_grid.py - 网格生成模块测试
=================================
"""

import pytest
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('..'))

from gwflow.grid.structured import (
    create_1d_grid,
    create_2d_grid,
    create_3d_grid,
    refine_grid_2d
)


class TestGrid1D:
    """一维网格测试"""
    
    def test_create_1d_grid_basic(self):
        """测试基本的一维网格生成"""
        L = 1000.0
        nx = 51
        x, dx = create_1d_grid(L, nx)
        
        assert len(x) == nx
        assert x[0] == 0.0
        assert np.isclose(x[-1], L)
        assert np.isclose(dx, L / (nx - 1))
    
    def test_create_1d_grid_spacing(self):
        """测试网格间距的一致性"""
        L = 1000.0
        nx = 101
        x, dx = create_1d_grid(L, nx)
        
        # 检查所有间距是否相等
        spacing = np.diff(x)
        assert np.allclose(spacing, dx)
    
    def test_create_1d_grid_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            create_1d_grid(L=1000.0, nx=1)  # nx < 2
        
        with pytest.raises(ValueError):
            create_1d_grid(L=-100.0, nx=10)  # L <= 0
        
        with pytest.raises(ValueError):
            create_1d_grid(L=0.0, nx=10)  # L <= 0


class TestGrid2D:
    """二维网格测试"""
    
    def test_create_2d_grid_basic(self):
        """测试基本的二维网格生成"""
        Lx, Ly = 1000.0, 800.0
        nx, ny = 51, 41
        X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
        
        assert X.shape == (ny, nx)
        assert Y.shape == (ny, nx)
        assert np.isclose(X[0, 0], 0.0)
        assert np.isclose(X[0, -1], Lx)
        assert np.isclose(Y[0, 0], 0.0)
        assert np.isclose(Y[-1, 0], Ly)
        assert np.isclose(dx, Lx / (nx - 1))
        assert np.isclose(dy, Ly / (ny - 1))
    
    def test_create_2d_grid_square(self):
        """测试正方形网格"""
        L = 1000.0
        n = 51
        X, Y, dx, dy = create_2d_grid(L, L, n, n)
        
        assert X.shape == (n, n)
        assert Y.shape == (n, n)
        assert np.isclose(dx, dy)
    
    def test_create_2d_grid_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            create_2d_grid(Lx=1000.0, Ly=800.0, nx=1, ny=40)
        
        with pytest.raises(ValueError):
            create_2d_grid(Lx=-1000.0, Ly=800.0, nx=50, ny=40)


class TestGrid3D:
    """三维网格测试"""
    
    def test_create_3d_grid_basic(self):
        """测试基本的三维网格生成"""
        Lx, Ly, Lz = 1000.0, 800.0, 50.0
        nx, ny, nz = 51, 41, 11
        X, Y, Z, dx, dy, dz = create_3d_grid(Lx, Ly, Lz, nx, ny, nz)
        
        assert X.shape == (nz, ny, nx)
        assert Y.shape == (nz, ny, nx)
        assert Z.shape == (nz, ny, nx)
        assert np.isclose(dx, Lx / (nx - 1))
        assert np.isclose(dy, Ly / (ny - 1))
        assert np.isclose(dz, Lz / (nz - 1))
    
    def test_create_3d_grid_cube(self):
        """测试立方体网格"""
        L = 100.0
        n = 21
        X, Y, Z, dx, dy, dz = create_3d_grid(L, L, L, n, n, n)
        
        assert X.shape == (n, n, n)
        assert np.isclose(dx, dy)
        assert np.isclose(dy, dz)


class TestGridRefinement:
    """网格加密测试"""
    
    def test_refine_grid_2d(self):
        """测试二维网格加密"""
        Lx, Ly = 1000.0, 800.0
        nx, ny = 11, 9
        X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
        
        refinement_factor = 2
        X_refined, Y_refined = refine_grid_2d(X, Y, refinement_factor)
        
        expected_nx = (nx - 1) * refinement_factor + 1
        expected_ny = (ny - 1) * refinement_factor + 1
        
        assert X_refined.shape[1] == expected_nx
        assert X_refined.shape[0] == expected_ny
        assert np.isclose(X_refined[0, 0], 0.0)
        assert np.isclose(X_refined[0, -1], Lx)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
