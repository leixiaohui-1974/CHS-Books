"""测试第四部分和第五部分模型"""

import pytest
import numpy as np
from code.models.hydraulic_structures import (
    EcologicalWeir, StockingArea, HydropowerScheduling, DamSprayImpact
)
from code.models.integrated_assessment import (
    WatershedEcohydrology, ClimateChangeImpact,
    RiverHealthAssessment, IntegratedManagement
)


class TestHydraulicStructures:
    """测试水工建筑物模型"""
    
    def test_ecological_weir(self):
        weir = EcologicalWeir(10.0, 2.0)
        Q = weir.discharge_capacity(1.5, 3.0)
        assert Q > 0
        
        v = weir.fish_passage_velocity(50)
        status = weir.suitability_assessment(v)
        assert status in ['适宜', '基本适宜', '不适宜']
    
    def test_stocking_area(self):
        area = StockingArea(1000)
        v = area.acclimation_velocity(2)
        assert v > 0
        
        Q = area.optimal_release_flow(10.0)
        assert Q > 0
        
        survival = area.survival_rate_estimate(100, 20)
        assert 0 <= survival <= 1
    
    def test_hydropower_scheduling(self):
        scheduler = HydropowerScheduling(100, 50)
        P = scheduler.power_generation(100, 50)
        assert 0 <= P <= 100
        
        E = scheduler.ecological_benefit(75)
        assert 0 <= E <= 100
        
        discharges = np.linspace(30, 200, 20)
        result = scheduler.multi_objective_optimization(discharges, 50)
        assert len(result['pareto_indices']) > 0
    
    def test_dam_spray(self):
        spray = DamSprayImpact(100)
        I = spray.spray_intensity(500, 50)
        assert I > 0
        
        zone = spray.vegetation_impact_zone(500)
        assert zone > 0
        
        measures = spray.mitigation_measures()
        assert len(measures) > 0


class TestIntegratedAssessment:
    """测试综合评估模型"""
    
    def test_watershed_ecohydrology(self):
        watershed = WatershedEcohydrology(1000)
        balance = watershed.water_balance(1000, 600)
        assert 'runoff' in balance
        
        monthly_flows = np.random.rand(12) * 100 + 50
        regime = watershed.ecological_flow_regime(monthly_flows)
        assert regime['mean'] > 0
    
    def test_climate_change(self):
        climate = ClimateChangeImpact()
        impact = climate.temperature_change_impact(2.5)
        assert 'flow_change_percent' in impact
        assert impact['adaptation_needed'] == True
    
    def test_river_health(self):
        rha = RiverHealthAssessment()
        result = rha.calculate_rhi(75, 80, 70, 85)
        assert 'rhi' in result
        assert 'grade' in result
        assert 0 <= result['rhi'] <= 100
    
    def test_integrated_management(self):
        mgmt = IntegratedManagement()
        allocation = {'生活': 30, '工业': 40, '农业': 50, '生态': 30}
        result = mgmt.multi_stakeholder_benefit(allocation)
        assert 'gini_coefficient' in result
        
        data = np.random.rand(10) * 50 + 50
        adaptive = mgmt.adaptive_management_framework(data)
        assert 'recommendation' in adaptive
