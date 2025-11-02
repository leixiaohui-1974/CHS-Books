"""
测试河口盐水入侵模型
Test Estuary Saltwater Intrusion Model
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from models.estuary import (EstuarySaltIntrusion1D, calculate_stratification_parameter,
                             calculate_mixing_parameter, calculate_salt_wedge_length,
                             estimate_intake_risk)


class TestEstuarySaltIntrusion1D:
    """测试EstuarySaltIntrusion1D类"""
    
    def test_initialization(self):
        """测试初始化"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        assert model.L == 30000
        assert model.nx == 100
        assert model.H == 5
        assert len(model.x) == 100
        assert model.S.shape == (100,)
    
    def test_set_initial_salinity(self):
        """测试初始盐度设置"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        # 上游应为淡水
        assert model.S[0] < 5
        # 下游应为海水
        assert model.S[-1] > 25
        # 中间应有梯度
        assert model.S[50] > model.S[0]
        assert model.S[50] < model.S[-1]
    
    def test_calculate_tidal_velocity(self):
        """测试潮汐流速计算"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        T = model.tidal_period
        
        # 涨潮（T/4）
        u_flood = model.calculate_tidal_velocity(T/4)
        # 退潮（3T/4）
        u_ebb = model.calculate_tidal_velocity(3*T/4)
        
        # 涨潮为正，退潮为负
        assert u_flood > 0
        assert u_ebb < 0
    
    def test_calculate_density_driven_flow(self):
        """测试密度流计算"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        # 设置盐度梯度
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        u_density = model.calculate_density_driven_flow(model.S)
        
        # 密度流应存在
        assert len(u_density) == model.nx
        # 密度流速度应合理
        assert np.max(np.abs(u_density)) < 1.0  # 不应过大
    
    def test_solve_salinity_transport(self):
        """测试盐度输运求解"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        model.set_initial_salinity(S_sea=30, S_river=0)
        S_initial = model.S.copy()
        
        # 求解一个时间步
        model.solve_salinity_transport(t=0, dt=300)
        
        # 盐度应有变化
        assert not np.allclose(model.S, S_initial)
        # 盐度应在合理范围
        assert np.all(model.S >= 0)
        assert np.all(model.S <= 35)
    
    def test_calculate_intrusion_length(self):
        """测试入侵长度计算"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        L_intrusion = model.calculate_intrusion_length(S_threshold=2.0)
        
        # 入侵长度应合理
        assert L_intrusion >= 0
        assert L_intrusion <= model.L
    
    def test_solve_water_quality(self):
        """测试水质求解"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        # 求解水质
        model.solve_water_quality(C_source=100, x_source=10000, decay_rate=0.1)
        
        # 浓度应合理
        assert np.all(model.C >= 0)
        assert np.max(model.C) <= 100


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_calculate_stratification_parameter(self):
        """测试分层参数计算"""
        delta_rho = 25  # 密度差
        H = 5
        u = 0.5
        
        Ri = calculate_stratification_parameter(delta_rho, H, u)
        
        # Richardson数应为正
        assert Ri > 0
    
    def test_calculate_mixing_parameter(self):
        """测试混合参数计算"""
        u = 0.5
        H = 5
        du_dz = 0.1
        
        mixing = calculate_mixing_parameter(u, H, du_dz)
        
        assert mixing >= 0
    
    def test_calculate_salt_wedge_length(self):
        """测试盐水楔长度计算"""
        Q = 50
        B = 500
        H = 5
        rho_fresh = 1000
        rho_salt = 1025
        
        L_wedge = calculate_salt_wedge_length(Q, B, H, rho_fresh, rho_salt)
        
        # 楔长应合理
        assert L_wedge >= 0
        assert L_wedge < 100000  # 不应过长
    
    def test_estimate_intake_risk(self):
        """测试取水口风险评估"""
        S = np.linspace(0, 30, 100)
        x_intake = 50  # 中间位置
        
        risk_level, is_safe = estimate_intake_risk(S, x_intake, S_max=0.5)
        
        # 风险等级应合理
        assert risk_level >= 0
        assert isinstance(is_safe, (bool, np.bool_))
    
    def test_higher_flow_reduces_intrusion(self):
        """测试流量增加减少入侵"""
        B = 500
        H = 5
        rho_fresh = 1000
        rho_salt = 1025
        
        # 低流量
        L_low = calculate_salt_wedge_length(50, B, H, rho_fresh, rho_salt)
        
        # 高流量
        L_high = calculate_salt_wedge_length(200, B, H, rho_fresh, rho_salt)
        
        # 高流量时入侵长度应更短
        assert L_high < L_low


class TestPhysicalBehavior:
    """测试物理行为"""
    
    def test_tidal_oscillation(self):
        """测试潮汐振荡"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        T = model.tidal_period
        
        # 涨潮（T/4）
        u_flood = model.calculate_tidal_velocity(T/4)
        # 退潮（3T/4）
        u_ebb = model.calculate_tidal_velocity(3*T/4)
        # 全周期
        u_full = model.calculate_tidal_velocity(T)
        
        # 涨潮和退潮应相反
        assert u_flood * u_ebb < 0  # 异号
        # 全周期应回到初始（接近0）
        assert abs(u_full) < 0.01
    
    def test_salinity_gradient(self):
        """测试盐度梯度"""
        model = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=3, tidal_period=12.4*3600
        )
        
        model.set_initial_salinity(S_sea=30, S_river=0)
        
        # 上游到下游应递增
        for i in range(len(model.S)-1):
            assert model.S[i+1] >= model.S[i] - 1.0  # 允许小波动
    
    def test_higher_tidal_range_stronger_intrusion(self):
        """测试潮差越大入侵越强"""
        # 小潮差
        model_small = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=1, tidal_period=12.4*3600
        )
        
        # 大潮差
        model_large = EstuarySaltIntrusion1D(
            L=30000, nx=100, H=5, Q_river=50,
            tidal_range=5, tidal_period=12.4*3600
        )
        
        T = 12.4 * 3600
        u_small = model_small.calculate_tidal_velocity(T/4)
        u_large = model_large.calculate_tidal_velocity(T/4)
        
        # 大潮差时潮流更强
        assert abs(u_large) > abs(u_small)


# 运行测试
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
