"""
测试水库温度分层与水质模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.stratified_reservoir import (StratifiedReservoir1D, calculate_buoyancy_frequency,
                                          calculate_richardson_number, estimate_mixing_depth)


class TestStratifiedReservoir1D:
    """测试StratifiedReservoir1D类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        assert model.H == 100
        assert model.nz == 51
        assert len(model.z) == 51
        assert len(model.T) == 51
        assert len(model.DO) == 51
    
    def test_set_vertical_diffusivity(self):
        """测试设置扩散系数"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        Kz_new = 1e-4
        model.set_vertical_diffusivity(Kz_new)
        
        assert np.all(model.Kz == Kz_new)
    
    def test_calculate_thermocline_depth(self):
        """测试温跃层深度计算"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        # 设置分层温度
        model.T = 25 - 10 * model.z / model.H
        
        z_thermo, dT_dz = model.calculate_thermocline_depth()
        
        assert z_thermo >= 0
        assert z_thermo <= model.H
    
    def test_solve_temperature_1d(self):
        """测试温度场求解"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        t = np.linspace(0, 10, 20)
        t_out, T_field = model.solve_temperature_1d(t, T_surface=25)
        
        assert T_field.shape == (model.nz, len(t))
    
    def test_solve_do_1d(self):
        """测试DO场求解"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        t = np.linspace(0, 10, 20)
        t_out, DO_field = model.solve_do_1d(t)
        
        assert DO_field.shape == (model.nz, len(t))
    
    def test_assess_anoxia_risk(self):
        """测试缺氧风险评估"""
        model = StratifiedReservoir1D(H=100, nz=51)
        
        # 设置底层低DO
        model.DO[-20:] = 1.0
        
        anoxic_depth, fraction = model.assess_anoxia_risk(DO_threshold=2.0)
        
        assert anoxic_depth is not None
        assert 0 < fraction <= 1


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_buoyancy_frequency(self):
        """测试浮力频率计算"""
        z = np.linspace(0, 100, 51)
        T = 25 - 10 * z / 100
        
        N2 = calculate_buoyancy_frequency(T, z)
        
        assert len(N2) == len(z)
        assert np.all(N2 >= 0)  # 稳定分层
    
    def test_calculate_richardson_number(self):
        """测试Richardson数计算"""
        z = np.linspace(0, 100, 51)
        T = 25 - 10 * z / 100
        
        Ri = calculate_richardson_number(T, z, u=0.01)
        
        assert len(Ri) == len(z)
    
    def test_estimate_mixing_depth(self):
        """测试混合层深度估算"""
        z = np.linspace(0, 100, 51)
        T = 25 * np.ones(51)
        T[10:] = 15  # 10m以下温度降低
        
        h_mix = estimate_mixing_depth(T, z, dT_threshold=0.5)
        
        assert 0 < h_mix < 100


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_temperature_diffusion(self):
        """测试温度扩散"""
        model = StratifiedReservoir1D(H=100, nz=51)
        model.T = 20 * np.ones(51)
        model.set_vertical_diffusivity(1e-3)  # 使用较大扩散系数便于测试
        
        t = np.linspace(0, 30, 50)
        t_out, T_field = model.solve_temperature_1d(t, T_surface=25)
        
        # 热量应向下传播，表层附近温度应上升
        assert T_field[1, -1] > T_field[1, 0]
    
    def test_do_consumption(self):
        """测试DO消耗"""
        model = StratifiedReservoir1D(H=100, nz=51)
        model.DO = 8 * np.ones(51)
        
        t = np.linspace(0, 30, 50)
        t_out, DO_field = model.solve_do_1d(t, photosynthesis=False)
        
        # DO应减少（呼吸+SOD）
        assert DO_field[-1, -1] < DO_field[-1, 0]


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
