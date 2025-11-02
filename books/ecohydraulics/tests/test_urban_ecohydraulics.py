"""测试城市水生态模型"""

import pytest
import numpy as np
from code.models.urban_ecohydraulics import (
    SpongeCityDesign,
    UrbanRiverRestoration,
    RainGarden,
    UrbanFloodControl,
    design_sponge_city_system
)


class TestSpongeCityDesign:
    """测试海绵城市设计模型"""
    
    def test_initialization(self):
        """测试初始化"""
        sponge = SpongeCityDesign(50.0, 0.65)
        assert sponge.A == 50e4
        assert sponge.imp == 0.65
    
    def test_runoff_volume(self):
        """测试径流量计算"""
        sponge = SpongeCityDesign(50.0, 0.65)
        result = sponge.runoff_volume(30.0)
        
        assert 'runoff_volume' in result
        assert result['runoff_volume'] > 0
        assert 0 < result['runoff_coefficient'] < 1
    
    def test_lid_facility_sizing(self):
        """测试LID设施规模"""
        sponge = SpongeCityDesign(50.0, 0.65)
        design = sponge.lid_facility_sizing(30.0, 'bioretention')
        
        assert design['facility_area'] > 0
        assert design['storage_volume'] > 0
        assert 0 <= design['reduction_rate'] <= 100
    
    def test_annual_control_rate(self):
        """测试年控制率"""
        sponge = SpongeCityDesign(50.0, 0.65)
        rainfall_series = np.random.exponential(15, 100)
        
        result = sponge.annual_control_rate(rainfall_series)
        
        assert 'control_rate_volume' in result
        assert 0 <= result['control_rate_volume'] <= 100
    
    def test_water_quality_improvement(self):
        """测试水质改善"""
        sponge = SpongeCityDesign(50.0, 0.65)
        inlet_conc = {'TSS': 150.0, 'TN': 3.5}
        
        result = sponge.water_quality_improvement(inlet_conc)
        
        assert 'outlet_concentration' in result
        for pollutant in inlet_conc.keys():
            assert result['outlet_concentration'][pollutant] < inlet_conc[pollutant]


class TestUrbanRiverRestoration:
    """测试城市河道修复模型"""
    
    def test_initialization(self):
        """测试初始化"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        assert river.L == 5000
        assert river.W == 30.0
        assert river.H == 2.0
    
    def test_hydraulic_diversity_index(self):
        """测试水力多样性指数"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        velocity_data = np.random.normal(0.5, 0.2, 100)
        depth_data = np.random.normal(2.0, 0.5, 100)
        
        HDI = river.hydraulic_diversity_index(velocity_data, depth_data)
        assert HDI > 0
    
    def test_habitat_suitability_index(self):
        """测试生境适宜性"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        HSI = river.habitat_suitability_index(0.5, 1.5, 'gravel')
        
        assert 0 <= HSI <= 1
    
    def test_ecological_flow_requirement(self):
        """测试生态流量需求"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        eco_flows = river.ecological_flow_requirement(10.0)
        
        assert 'optimal' in eco_flows
        assert eco_flows['optimal'] > eco_flows['minimum']
    
    def test_riparian_vegetation_design(self):
        """测试滨岸植被设计"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        design = river.riparian_vegetation_design(15.0, 'loam')
        
        assert 'vegetation_zones' in design
        assert 'stability' in design
    
    def test_self_purification_capacity(self):
        """测试自净能力"""
        river = UrbanRiverRestoration(5.0, 30.0, 2.0)
        result = river.self_purification_capacity(8.0, 20.0)
        
        assert result['reaeration_rate'] > 0
        assert result['saturated_DO'] > 0


class TestRainGarden:
    """测试雨水花园模型"""
    
    def test_initialization(self):
        """测试初始化"""
        garden = RainGarden(100.0, 0.6, 0.3)
        assert garden.A == 100.0
        assert garden.d_media == 0.6
        assert garden.d_pond == 0.3
    
    def test_infiltration_rate(self):
        """测试渗透速率"""
        garden = RainGarden(100.0, 0.6, 0.3)
        rate = garden.infiltration_rate('loam')
        assert rate > 0
    
    def test_storage_capacity(self):
        """测试调蓄容量"""
        garden = RainGarden(100.0, 0.6, 0.3)
        storage = garden.storage_capacity(0.4)
        
        assert storage['total_storage'] > 0
        assert storage['surface_storage'] > 0
        assert storage['media_storage'] > 0
    
    def test_drawdown_time(self):
        """测试排空时间"""
        garden = RainGarden(100.0, 0.6, 0.3)
        time = garden.drawdown_time(25.0)
        assert time > 0
    
    def test_pollutant_removal_efficiency(self):
        """测试污染物去除"""
        garden = RainGarden(100.0, 0.6, 0.3)
        inlet_load = {'TSS': 50.0, 'TN': 5.0}
        
        result = garden.pollutant_removal_efficiency(inlet_load)
        
        assert 'removal_rates' in result
        for pollutant in inlet_load.keys():
            assert result['outlet_load'][pollutant] < inlet_load[pollutant]
    
    def test_plant_selection(self):
        """测试植物选择"""
        garden = RainGarden(100.0, 0.6, 0.3)
        plants = garden.plant_selection('high', 'full')
        assert len(plants) > 0
    
    def test_cost_benefit_analysis(self):
        """测试成本效益"""
        garden = RainGarden(100.0, 0.6, 0.3)
        result = garden.cost_benefit_analysis(300, 150)
        
        assert 'payback_period' in result
        assert result['construction_cost'] > 0


class TestUrbanFloodControl:
    """测试城市内涝防治模型"""
    
    def test_initialization(self):
        """测试初始化"""
        flood = UrbanFloodControl(2.0, 20)
        assert flood.A == 2e6
        assert flood.T == 20
    
    def test_design_rainfall_intensity(self):
        """测试设计暴雨强度"""
        flood = UrbanFloodControl(2.0, 20)
        intensity = flood.design_rainfall_intensity(120, 'beijing')
        assert intensity > 0
    
    def test_runoff_calculation(self):
        """测试径流计算"""
        flood = UrbanFloodControl(2.0, 20)
        result = flood.runoff_calculation(50.0, 0.65)
        
        assert result['runoff_flow'] > 0
        assert 0 < result['runoff_coefficient'] < 1
    
    def test_detention_basin_design(self):
        """测试调蓄池设计"""
        flood = UrbanFloodControl(2.0, 20)
        basin = flood.detention_basin_design(5000, 0.5)
        
        assert basin['storage_volume'] > 0
        assert basin['basin_area'] > 0
    
    def test_green_infrastructure_effectiveness(self):
        """测试绿色基础设施效能"""
        flood = UrbanFloodControl(2.0, 20)
        result = flood.green_infrastructure_effectiveness(30)
        
        assert 'runoff_reduction' in result
        assert 0 <= result['runoff_reduction'] <= 100
    
    def test_integrated_management_strategy(self):
        """测试综合管理策略"""
        flood = UrbanFloodControl(2.0, 20)
        strategy = flood.integrated_management_strategy(1000)
        
        assert 'allocation' in strategy
        assert 'total_effectiveness' in strategy


class TestIntegrationFunctions:
    """测试集成功能"""
    
    def test_design_sponge_city_system(self):
        """测试海绵城市系统设计"""
        result = design_sponge_city_system(50.0, 0.65, 80.0)
        
        assert 'current_control_rate' in result
        assert 'target_control_rate' in result
        assert result['target_control_rate'] == 80.0
