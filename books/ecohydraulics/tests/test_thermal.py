"""测试热分层模型（精简版）"""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from code.models.thermal import *

class TestThermalModel:
    def test_init(self):
        model = ThermalStratificationModel(30, 20)
        assert model.depth == 30
        assert len(model.temperature) == 20
    
    def test_water_density(self):
        model = ThermalStratificationModel(30, 20)
        rho_4 = model.water_density(4)
        rho_20 = model.water_density(20)
        assert rho_4 > rho_20  # 4°C密度最大
    
    def test_thermocline(self):
        model = create_summer_stratification(30, 20)
        tc_depth = model.thermocline_depth()
        assert 0 < tc_depth < 30

class TestDOModel:
    def test_init(self):
        model = DissolvedOxygenModel(30, 20)
        assert model.depth == 30
        assert len(model.DO) == 20
    
    def test_DO_saturation(self):
        model = DissolvedOxygenModel(30, 20)
        DO_20 = model.DO_saturation(20)
        DO_5 = model.DO_saturation(5)
        assert DO_5 > DO_20  # 冷水溶解度高
    
    def test_simulation(self):
        model = DissolvedOxygenModel(30, 20)
        DO_final = model.simulate_DO_profile(10, 3.0)
        assert len(DO_final) == 20
        assert np.all(DO_final >= 0)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
