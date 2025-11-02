"""
测试Phase 6所有模型（案例23-30）
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.watershed_model import WatershedModel, assess_land_use_impact
from models.river_network import RiverNetworkModel, optimize_gate_schedule
from models.water_transfer import WaterTransferModel, assess_mixing_quality
from models.river_ecosystem import RiverEcosystemModel, calculate_biodiversity_index
from models.lake_regime_shift import LakeRegimeShiftModel, find_critical_load
from models.wetland_model import WetlandModel, assess_seasonal_variation
from models.urban_blackwater import UrbanBlackwaterModel, optimize_treatment_plan
from models.watershed_platform import WatershedPlatform, perform_scenario_analysis


class TestWatershedModel:
    def test_initialization(self):
        model = WatershedModel(area=500, n_subbasins=5)
        assert model.area == 500
        assert model.n_subbasins == 5
    
    def test_simulate_runoff(self):
        model = WatershedModel(area=500, n_subbasins=5)
        runoff = model.simulate_runoff(rainfall=50, CN=75)
        assert runoff >= 0


class TestRiverNetworkModel:
    def test_initialization(self):
        model = RiverNetworkModel(n_nodes=10, n_gates=5)
        assert model.n_nodes == 10
    
    def test_simulate_gate_operation(self):
        model = RiverNetworkModel(n_nodes=10, n_gates=5)
        outflow = model.simulate_gate_operation(gate_opening=0.5, inflow=10)
        assert outflow == 5.0


class TestWaterTransferModel:
    def test_initialization(self):
        model = WaterTransferModel(channel_length=100, flow_rate=50)
        assert model.channel_length == 100
    
    def test_simulate_algae_growth_risk(self):
        model = WaterTransferModel(channel_length=100, flow_rate=50)
        final_Chl, risk = model.simulate_algae_growth_risk(initial_Chl=5, light_intensity=200)
        assert final_Chl >= 5


class TestRiverEcosystemModel:
    def test_initialization(self):
        model = RiverEcosystemModel()
        assert len(model.state) == 3
    
    def test_solve(self):
        model = RiverEcosystemModel()
        t = np.linspace(0, 10, 50)
        t_out, result = model.solve(t)
        assert result.shape == (50, 3)


class TestLakeRegimeShiftModel:
    def test_initialization(self):
        model = LakeRegimeShiftModel(P_load=0.5)
        assert model.P_load == 0.5
    
    def test_solve(self):
        model = LakeRegimeShiftModel(P_load=0.3)
        t = np.linspace(0, 50, 100)
        t_out, result, regime = model.solve(t)
        assert regime in ["清水态", "浊水态"]


class TestWetlandModel:
    def test_initialization(self):
        model = WetlandModel(area=1000, depth=0.5)
        assert model.area == 1000
    
    def test_calculate_removal(self):
        model = WetlandModel(area=1000, depth=0.5)
        C_out, eff = model.calculate_removal(C_in=50, HRT=5, k_removal=0.3)
        assert C_out < 50
        assert 0 < eff < 100


class TestUrbanBlackwaterModel:
    def test_initialization(self):
        model = UrbanBlackwaterModel(river_length=2000, width=15, depth=2)
        assert model.volume > 0
    
    def test_assess_current_status(self):
        model = UrbanBlackwaterModel(river_length=2000, width=15, depth=2)
        status, score = model.assess_current_status(DO=1.5, NH3_N=10, transparency=0.15)
        assert status in ["重度黑臭", "轻度黑臭", "无黑臭"]


class TestWatershedPlatform:
    def test_initialization(self):
        platform = WatershedPlatform(watershed_name="Test", area=1000)
        assert platform.name == "Test"
    
    def test_run_comprehensive_simulation(self):
        platform = WatershedPlatform(watershed_name="Test", area=1000)
        results = platform.run_comprehensive_simulation("Scenario1")
        assert 'runoff' in results


class TestHelperFunctions:
    def test_assess_land_use_impact(self):
        impact = assess_land_use_impact(0.4, 0.3)
        assert 0 <= impact <= 1
    
    def test_optimize_gate_schedule(self):
        opening = optimize_gate_schedule(target_quality=20, current_quality=35)
        assert 0 <= opening <= 1
    
    def test_assess_mixing_quality(self):
        mixed = assess_mixing_quality(source1_quality=15, source2_quality=30, ratio=0.6)
        assert 15 <= mixed <= 30
    
    def test_calculate_biodiversity_index(self):
        H = calculate_biodiversity_index(np.array([10, 5, 2]))
        assert H > 0
    
    def test_find_critical_load(self):
        load = find_critical_load([0.1, 1.0])
        assert load > 0
    
    def test_assess_seasonal_variation(self):
        summer_k, winter_k = assess_seasonal_variation(25, 5)
        assert summer_k > winter_k
    
    def test_optimize_treatment_plan(self):
        plan = optimize_treatment_plan(budget=800, target_quality='Class III')
        assert isinstance(plan, dict)
    
    def test_perform_scenario_analysis(self):
        best = perform_scenario_analysis(['S1', 'S2', 'S3'])
        assert best in ['S1', 'S2', 'S3']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
