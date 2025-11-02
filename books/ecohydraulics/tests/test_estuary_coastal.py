"""测试河口海岸生态模型"""

import pytest
import numpy as np
from code.models.estuary_coastal import (
    SaltWedge,
    MangroveHydrodynamics,
    EcologicalRevetment,
    EstuarineWetlandCarbon,
    simulate_storm_surge_protection
)


class TestSaltWedge:
    """测试盐水楔模型"""
    
    def test_initialization(self):
        """测试初始化"""
        estuary = SaltWedge(10.0, 500.0, 500.0)
        assert estuary.h == 10.0
        assert estuary.W == 500.0
        assert estuary.Q_r == 500.0
    
    def test_froude_number(self):
        """测试密度弗劳德数"""
        estuary = SaltWedge(10.0, 500.0, 500.0)
        Fr = estuary.densimetric_froude_number()
        assert Fr > 0
    
    def test_mixing_classification(self):
        """测试混合类型分类"""
        estuary = SaltWedge(10.0, 500.0, 500.0)
        mixing = estuary.mixing_type_classification()
        assert 'mixing_type' in mixing
        assert 'froude_number' in mixing
    
    def test_salt_wedge_length(self):
        """测试盐水楔长度"""
        estuary = SaltWedge(10.0, 500.0, 500.0)
        L = estuary.salt_wedge_length(2.0)
        assert L > 0
    
    def test_salinity_distribution(self):
        """测试盐度分布"""
        estuary = SaltWedge(10.0, 500.0, 500.0)
        distances = np.array([0, 10, 20])
        S = estuary.salinity_distribution(distances, 0.5)
        assert len(S) == len(distances)
        assert np.all(S >= 0) and np.all(S <= 35)


class TestMangroveHydrodynamics:
    """测试红树林水动力模型"""
    
    def test_initialization(self):
        """测试初始化"""
        mangrove = MangroveHydrodynamics(100.0, 1.0, 0.15)
        assert mangrove.W == 100.0
        assert mangrove.n == 1.0
        assert mangrove.d == 0.15
    
    def test_drag_coefficient(self):
        """测试阻力系数"""
        mangrove = MangroveHydrodynamics(100.0, 1.0, 0.15)
        Cd = mangrove.drag_coefficient(1.0)
        assert Cd > 0
    
    def test_wave_attenuation(self):
        """测试波浪消减"""
        mangrove = MangroveHydrodynamics(100.0, 1.0, 0.15)
        result = mangrove.wave_attenuation(1.5, 8.0, 2.0)
        
        assert 'transmitted_height' in result
        assert result['transmitted_height'] < result['incident_height']
        assert 0 <= result['attenuation_rate'] <= 100
    
    def test_current_reduction(self):
        """测试潮流消减"""
        mangrove = MangroveHydrodynamics(100.0, 1.0, 0.15)
        result = mangrove.current_reduction(1.0, 2.0)
        
        assert result['outlet_velocity'] < result['inlet_velocity']
        assert 0 <= result['reduction_rate'] <= 100
    
    def test_sediment_trapping(self):
        """测试泥沙捕获"""
        mangrove = MangroveHydrodynamics(100.0, 1.0, 0.15)
        efficiency = mangrove.sediment_trapping_efficiency(100, 0.5)
        assert 0 <= efficiency <= 100


class TestEcologicalRevetment:
    """测试生态护岸模型"""
    
    def test_initialization(self):
        """测试初始化"""
        revetment = EcologicalRevetment(200.0, 30.0, 2.0)
        assert revetment.L == 200.0
        assert revetment.alpha == 30.0
        assert revetment.H_design == 2.0
    
    def test_wave_runup(self):
        """测试波浪爬高"""
        revetment = EcologicalRevetment(200.0, 30.0, 2.0)
        runup = revetment.wave_runup(2.0, 10.0)
        assert runup > 0
    
    def test_stability_analysis(self):
        """测试稳定性分析"""
        revetment = EcologicalRevetment(200.0, 30.0, 2.0)
        stability = revetment.stability_analysis(0.5)
        
        assert 'safety_factor' in stability
        assert 'stability' in stability
    
    def test_vegetation_design(self):
        """测试植被设计"""
        revetment = EcologicalRevetment(200.0, 30.0, 2.0)
        design = revetment.vegetation_design('middle')
        
        assert 'species' in design
        assert len(design['species']) > 0
    
    def test_cost_comparison(self):
        """测试成本对比"""
        revetment = EcologicalRevetment(200.0, 30.0, 2.0)
        cost = revetment.cost_comparison(5000)
        
        assert 'ecological_initial' in cost
        assert 'traditional_initial' in cost


class TestEstuarineWetlandCarbon:
    """测试河口湿地碳汇模型"""
    
    def test_initialization(self):
        """测试初始化"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        assert wetland.A == 100e4
        assert wetland.veg_type == 'mangrove'
    
    def test_npp(self):
        """测试净初级生产力"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        npp = wetland.net_primary_production()
        assert npp > 0
    
    def test_carbon_sequestration(self):
        """测试碳固定速率"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        seq = wetland.carbon_sequestration_rate()
        
        assert seq['total_sequestration'] > 0
        assert seq['co2_equivalent'] > 0
    
    def test_soil_carbon_stock(self):
        """测试土壤碳储量"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        stock = wetland.soil_carbon_stock(1.0)
        assert stock > 0
    
    def test_blue_carbon_potential(self):
        """测试蓝碳潜力"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        potential = wetland.blue_carbon_potential(20)
        
        assert 'total_carbon_sequestration' in potential
        assert potential['carbon_credit_value'] > 0
    
    def test_ghg_emissions(self):
        """测试温室气体排放"""
        wetland = EstuarineWetlandCarbon(100.0, 'mangrove')
        ghg = wetland.greenhouse_gas_emissions(5.0)
        
        assert 'ch4_emission' in ghg
        assert 'net_carbon_balance' in ghg
        assert isinstance(ghg['is_carbon_sink'], bool)


class TestIntegrationFunctions:
    """测试集成功能"""
    
    def test_simulate_storm_surge_protection(self):
        """测试风暴潮防护模拟"""
        result = simulate_storm_surge_protection(100, 2.0, 1.0)
        
        assert 'protection_score' in result
        assert 'risk_level' in result
        assert 0 <= result['protection_score'] <= 100
