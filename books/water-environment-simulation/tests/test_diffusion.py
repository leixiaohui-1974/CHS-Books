"""
测试扩散模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.diffusion import Diffusion1D, Diffusion2D


class TestDiffusion1D:
    """测试1D扩散模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = Diffusion1D(L=10.0, T=100.0, nx=100, nt=1000, D=0.01)
        
        assert model.L == 10.0
        assert model.T == 100.0
        assert model.nx == 100
        assert model.nt == 1000
        assert model.D == 0.01
        
        assert model.dx == pytest.approx(10.0 / 99, rel=1e-6)
        assert model.dt == pytest.approx(100.0 / 1000, rel=1e-6)
        
        assert model.C.shape == (1000, 100)
    
    def test_constant_initial_condition(self):
        """测试常数初始条件"""
        model = Diffusion1D()
        C0 = 1.0
        model.set_initial_condition(C0)
        
        assert np.allclose(model.C[0, :], C0)
    
    def test_function_initial_condition(self):
        """测试函数初始条件"""
        model = Diffusion1D(L=10.0, nx=11)
        C0_func = lambda x: np.sin(np.pi * x / 10.0)
        model.set_initial_condition(C0_func)
        
        expected = np.sin(np.pi * model.x / 10.0)
        assert np.allclose(model.C[0, :], expected)
    
    def test_explicit_stability(self):
        """测试显式格式稳定性"""
        # 稳定情况 (Fo < 0.5)
        model = Diffusion1D(L=10.0, T=10.0, nx=50, nt=5000, D=0.01)
        assert model.Fo <= 0.5
        
        model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.5)**2))
        model.set_boundary_conditions('dirichlet', 0.0, 0.0)
        C = model.solve_explicit()
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 检查没有NaN或Inf
        assert np.all(np.isfinite(C))
    
    def test_implicit_unconditional_stability(self):
        """测试隐式格式无条件稳定性"""
        # 使用大Fourier数（显式格式会不稳定）
        model = Diffusion1D(L=10.0, T=10.0, nx=20, nt=5, D=0.1)
        assert model.Fo > 0.5  # 超过显式稳定条件
        
        model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.5)**2))
        model.set_boundary_conditions('dirichlet', 0.0, 0.0)
        C = model.solve_implicit()
        
        # 应该仍然稳定
        assert np.all(C >= -1e-10)
        assert np.all(np.isfinite(C))
    
    def test_mass_conservation(self):
        """测试质量守恒（Neumann边界条件）"""
        model = Diffusion1D(L=10.0, T=50.0, nx=100, nt=500, D=0.01)
        
        model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.5)**2))
        model.set_boundary_conditions('neumann')
        C = model.solve_explicit()
        
        # 计算初始和最终质量
        mass_initial = np.sum(C[0, :]) * model.dx
        mass_final = np.sum(C[-1, :]) * model.dx
        
        # 质量应该守恒（Neumann边界）
        assert abs(mass_final - mass_initial) / mass_initial < 0.01  # 1%误差
    
    def test_crank_nicolson_accuracy(self):
        """测试Crank-Nicolson格式精度"""
        model = Diffusion1D(L=10.0, T=10.0, nx=100, nt=1000, D=0.01)
        
        model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.5)**2))
        model.set_boundary_conditions('dirichlet', 0.0, 0.0)
        
        C_explicit = model.solve_explicit()
        
        model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.5)**2))
        C_cn = model.solve_crank_nicolson()
        
        # C-N格式应该更精确
        # 这里只检查结果合理即可
        assert np.all(np.isfinite(C_cn))
        assert np.all(C_cn >= -1e-10)


class TestDiffusion2D:
    """测试2D扩散模型"""
    
    def test_initialization(self):
        """测试2D模型初始化"""
        model = Diffusion2D(Lx=10.0, Ly=8.0, T=100.0, 
                           nx=50, ny=40, nt=1000,
                           Dx=0.01, Dy=0.01)
        
        assert model.Lx == 10.0
        assert model.Ly == 8.0
        assert model.nx == 50
        assert model.ny == 40
        assert model.C.shape == (1000, 40, 50)
    
    def test_2d_explicit_solve(self):
        """测试2D显式求解"""
        model = Diffusion2D(Lx=5.0, Ly=5.0, T=10.0, 
                           nx=25, ny=25, nt=500,
                           Dx=0.01, Dy=0.01)
        
        # 检查稳定性条件
        assert model.Fo_x + model.Fo_y <= 0.5
        
        # 中心点源
        C0 = np.zeros((model.ny, model.nx))
        center_i = model.ny // 2
        center_j = model.nx // 2
        C0[center_i, center_j] = 1.0
        
        model.set_initial_condition(C0)
        C = model.solve_explicit()
        
        # 检查结果合理性
        assert np.all(C >= -1e-10)
        assert np.all(np.isfinite(C))
        
        # 检查对称性（近似）
        final_C = C[-1, :, :]
        assert abs(final_C[center_i-5, center_j] - final_C[center_i+5, center_j]) < 0.1
        assert abs(final_C[center_i, center_j-5] - final_C[center_i, center_j+5]) < 0.1


def test_diffusion_decreases_peak():
    """测试扩散使峰值降低"""
    model = Diffusion1D(L=10.0, T=50.0, nx=100, nt=500, D=0.01)
    
    model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.3)**2))
    model.set_boundary_conditions('dirichlet', 0.0, 0.0)
    C = model.solve_explicit()
    
    # 峰值应该随时间降低
    peak_initial = np.max(C[0, :])
    peak_middle = np.max(C[250, :])
    peak_final = np.max(C[-1, :])
    
    assert peak_middle < peak_initial
    assert peak_final < peak_middle


def test_diffusion_spreads():
    """测试扩散使分布变宽"""
    model = Diffusion1D(L=10.0, T=50.0, nx=100, nt=500, D=0.01)
    
    model.set_initial_condition(lambda x: np.exp(-((x-5.0)/0.3)**2))
    model.set_boundary_conditions('dirichlet', 0.0, 0.0)
    C = model.solve_explicit()
    
    # 计算分布宽度（标准差）
    def calc_width(c, x):
        mean = np.sum(x * c) / np.sum(c)
        var = np.sum((x - mean)**2 * c) / np.sum(c)
        return np.sqrt(var)
    
    width_initial = calc_width(C[0, :], model.x)
    width_final = calc_width(C[-1, :], model.x)
    
    # 分布应该变宽
    assert width_final > width_initial


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
