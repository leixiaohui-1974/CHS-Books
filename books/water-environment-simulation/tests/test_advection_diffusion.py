"""
测试对流-扩散模型
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.advection_diffusion import AdvectionDiffusion1D


class TestAdvectionDiffusion1D:
    """测试1D对流-扩散模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = AdvectionDiffusion1D(L=100.0, T=200.0, nx=200, nt=2000, u=0.5, D=0.1)
        
        assert model.L == 100.0
        assert model.T == 200.0
        assert model.nx == 200
        assert model.nt == 2000
        assert model.u == 0.5
        assert model.D == 0.1
        
        assert model.C.shape == (2000, 200)
    
    def test_dimensionless_numbers(self):
        """测试无量纲数计算"""
        model = AdvectionDiffusion1D(L=100.0, T=200.0, nx=100, nt=1000, u=0.5, D=0.1)
        
        # Peclet数
        Pe_expected = 0.5 * 100.0 / 0.1
        assert abs(model.Pe - Pe_expected) < 0.01
        
        # Courant数
        Cr_expected = 0.5 * model.dt / model.dx
        assert abs(model.Cr - Cr_expected) < 1e-6
        
        # Fourier数
        Fo_expected = 0.1 * model.dt / model.dx**2
        assert abs(model.Fo - Fo_expected) < 1e-6
    
    def test_upwind_scheme(self):
        """测试迎风格式"""
        model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.5, D=0.1)
        
        # 初始条件：高斯分布
        x0 = 20.0
        sigma = 2.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_upwind()
        
        # 检查浓度非负
        assert np.all(C >= -1e-10)
        
        # 检查没有NaN或Inf
        assert np.all(np.isfinite(C))
        
        # 检查峰值向下游移动
        peak_initial = np.argmax(C[0, :])
        peak_final = np.argmax(C[-1, :])
        assert peak_final > peak_initial
    
    def test_central_scheme(self):
        """测试中心差分格式"""
        # 使用小Peclet数避免振荡
        model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.1, D=0.5)
        
        x0 = 20.0
        sigma = 2.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_central()
        
        # 应该没有严重振荡
        assert np.all(np.isfinite(C))
    
    def test_quick_scheme(self):
        """测试QUICK格式"""
        model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.5, D=0.1)
        
        x0 = 20.0
        sigma = 2.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_quick()
        
        # 检查结果合理
        assert np.all(C >= -0.1)  # 允许小量负值（QUICK格式）
        assert np.all(np.isfinite(C))
    
    def test_lax_wendroff_scheme(self):
        """测试Lax-Wendroff格式"""
        model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.5, D=0.1)
        
        x0 = 20.0
        sigma = 2.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_lax_wendroff()
        
        # 检查结果合理
        assert np.all(C >= -1e-10)
        assert np.all(np.isfinite(C))
    
    def test_peak_movement(self):
        """测试峰值向下游移动"""
        u = 0.5  # m/s
        model = AdvectionDiffusion1D(L=100.0, T=50.0, nx=200, nt=1000, u=u, D=0.05)
        
        x0 = 10.0
        sigma = 1.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_upwind()
        
        # 峰值位置应该接近 x0 + u*T
        peak_pos = model.x[np.argmax(C[-1, :])]
        expected_pos = x0 + u * model.T
        
        # 允许一定误差（数值耗散会使峰值移动稍慢）
        assert abs(peak_pos - expected_pos) < 5.0
    
    def test_diffusion_spreads(self):
        """测试扩散使污染带变宽"""
        model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.3, D=0.2)
        
        x0 = 20.0
        sigma = 1.0
        C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        model.set_boundary_conditions(0.0, None)
        
        C = model.solve_upwind()
        
        # 计算分布宽度
        def calc_width(c, x):
            total = np.sum(c)
            if total < 1e-10:
                return 0
            mean = np.sum(x * c) / total
            var = np.sum((x - mean)**2 * c) / total
            return np.sqrt(var)
        
        width_initial = calc_width(C[0, :], model.x)
        width_final = calc_width(C[-1, :], model.x)
        
        # 宽度应该增加
        assert width_final > width_initial


def test_pure_advection():
    """测试纯对流（D=0）"""
    model = AdvectionDiffusion1D(L=100.0, T=50.0, nx=200, nt=1000, u=0.5, D=0.0)
    
    x0 = 20.0
    sigma = 2.0
    C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
    model.set_initial_condition(C0)
    model.set_boundary_conditions(0.0, None)
    
    C = model.solve_upwind()
    
    # 纯对流应该只是平移
    assert np.all(np.isfinite(C))
    
    # 峰值位置应该移动 u*T
    peak_pos = model.x[np.argmax(C[-1, :])]
    expected_pos = x0 + model.u * model.T
    
    # 纯对流的数值耗散可能较大
    assert abs(peak_pos - expected_pos) < 10.0


def test_pure_diffusion():
    """测试纯扩散（u=0）"""
    model = AdvectionDiffusion1D(L=100.0, T=100.0, nx=200, nt=2000, u=0.0, D=0.1)
    
    x0 = 50.0
    sigma = 2.0
    C0 = lambda x: np.exp(-0.5 * ((x - x0) / sigma)**2)
    model.set_initial_condition(C0)
    model.set_boundary_conditions(0.0, 0.0)
    
    C = model.solve_upwind()
    
    # 纯扩散峰值位置应该不变（对称）
    peak_initial = np.argmax(C[0, :])
    peak_final = np.argmax(C[-1, :])
    
    # 允许小范围移动（数值误差）
    assert abs(peak_final - peak_initial) < 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
