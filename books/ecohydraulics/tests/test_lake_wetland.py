"""测试湖泊与湿地模型"""

import pytest
import numpy as np
from code.models.lake_wetland import (
    LakeHydrodynamics, ConstructedWetland,
    simulate_lake_wind_event, design_wetland_system
)


class TestLakeHydrodynamics:
    """测试湖泊水动力学模型"""
    
    def test_initialization(self):
        """测试初始化"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        assert lake.A == 100e6
        assert lake.h == 5.0
        assert lake.F == 8000.0
    
    def test_wind_stress(self):
        """测试风应力计算"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        # 不同风速下的风应力
        tau_low = lake.wind_stress(2.0)
        tau_mid = lake.wind_stress(10.0)
        tau_high = lake.wind_stress(15.0)
        
        assert tau_low > 0
        assert tau_mid > tau_low
        assert tau_high > tau_mid
    
    def test_surface_current(self):
        """测试表层流速"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        u_surf = lake.surface_current_velocity(10.0)
        assert u_surf > 0
        assert u_surf < 1.0  # 合理范围
        assert abs(u_surf - 0.3) < 0.01  # 约为风速的3%
    
    def test_wind_setup(self):
        """测试风壅水"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        setup = lake.wind_setup(10.0)
        assert setup > 0
        assert setup < 1.0  # 合理范围
    
    def test_wave_parameters(self):
        """测试风浪参数"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        waves = lake.wave_parameters(10.0)
        
        assert 'significant_wave_height' in waves
        assert 'mean_period' in waves
        assert 'wavelength' in waves
        assert 'wave_steepness' in waves
        
        assert waves['significant_wave_height'] > 0
        assert waves['mean_period'] > 0
        assert waves['wavelength'] > 0
        assert waves['wave_steepness'] > 0  # 波陡应为正值
    
    def test_thermal_stratification(self):
        """测试温度分层"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        strat = lake.thermal_stratification(28.0, 18.0)
        
        assert 'thermocline_depth' in strat
        assert 'richardson_number' in strat
        assert 'stratification_status' in strat
        
        assert strat['thermocline_depth'] > 0
        assert strat['surface_density'] < strat['bottom_density']
    
    def test_nutrient_mixing(self):
        """测试营养盐混合"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        Kz = lake.nutrient_mixing(10.0, 0.5, 1.0)
        assert Kz > 0
    
    def test_algae_bloom_risk(self):
        """测试藻华风险评估"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        
        risk = lake.algae_bloom_risk(28.0, 0.08, 1.2, 0.5)
        
        assert 'risk_index' in risk
        assert 'risk_level' in risk
        assert 0 <= risk['risk_index'] <= 1
        assert risk['risk_level'] in ['高风险', '中风险', '低风险']


class TestConstructedWetland:
    """测试人工湿地模型"""
    
    def test_initialization(self):
        """测试初始化"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        assert wetland.L == 50.0
        assert wetland.W == 10.0
        assert wetland.h == 0.6
        assert wetland.n == 0.4
        assert wetland.volume == 50 * 10 * 0.6 * 0.4
    
    def test_hydraulic_retention_time(self):
        """测试HRT计算"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        
        HRT = wetland.hydraulic_retention_time(100.0)
        expected_HRT = (50 * 10 * 0.6 * 0.4) / 100.0
        assert abs(HRT - expected_HRT) < 0.01
    
    def test_pollutant_removal(self):
        """测试污染物去除"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        
        result = wetland.pollutant_removal(150.0, 3.0, 'COD')
        
        assert 'inlet_concentration' in result
        assert 'outlet_concentration' in result
        assert 'removal_rate' in result
        
        assert result['outlet_concentration'] < result['inlet_concentration']
        assert 0 <= result['removal_rate'] <= 100
    
    def test_different_pollutants(self):
        """测试不同污染物"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        
        pollutants = ['COD', 'BOD', 'TN', 'TP', 'NH3N']
        
        for pol in pollutants:
            result = wetland.pollutant_removal(100.0, 3.0, pol)
            assert result['removal_rate'] > 0
    
    def test_optimal_HRT_design(self):
        """测试最优HRT设计"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        
        design = wetland.optimal_HRT_design(80.0, 150.0, 'COD')
        
        assert 'required_HRT' in design
        assert 'design_flow_rate' in design
        assert design['required_HRT'] > 0
        assert design['design_flow_rate'] > 0
    
    def test_aspect_ratio_optimization(self):
        """测试长宽比优化"""
        wetland = ConstructedWetland(50.0, 10.0, 0.6, 0.4)
        
        result = wetland.aspect_ratio_optimization(3.0, 500.0)
        
        assert 'all_scenarios' in result
        assert 'optimal_scenario' in result
        assert len(result['all_scenarios']) > 0


class TestIntegrationFunctions:
    """测试集成功能"""
    
    def test_simulate_lake_wind_event(self):
        """测试湖泊风事件模拟"""
        lake = LakeHydrodynamics(100.0, 5.0, 8000.0)
        wind_speeds = np.array([5, 7, 10, 12, 10, 7, 5])
        
        result = simulate_lake_wind_event(lake, wind_speeds, 7)
        
        assert 'time' in result
        assert 'wind_speed' in result
        assert 'surface_velocity' in result
        assert len(result['surface_velocity']) == len(wind_speeds)
    
    def test_design_wetland_system(self):
        """测试湿地系统设计"""
        design = design_wetland_system(80.0, 1000.0, 150.0, 'COD')
        
        assert 'dimensions' in design
        assert 'hydraulics' in design
        assert 'performance' in design
        
        assert design['performance']['removal_rate'] >= 80.0
        assert design['dimensions']['length'] > 0
        assert design['dimensions']['width'] > 0
