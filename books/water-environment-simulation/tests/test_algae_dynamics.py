"""
测试藻类生长动力学模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.algae_dynamics import AlgaeGrowthModel, assess_bloom_risk


class TestAlgaeGrowthModel:
    def test_initialization(self):
        model = AlgaeGrowthModel(Chl0=5, N0=500, P0=50)
        assert model.state[0] == 5
        assert model.state[1] == 500
    
    def test_growth_rate(self):
        model = AlgaeGrowthModel()
        mu = model.growth_rate(N=500, P=50, I=200, T=25)
        assert mu > 0
        assert mu <= model.mu_max
    
    def test_solve(self):
        model = AlgaeGrowthModel(Chl0=5, N0=500, P0=50)
        t = np.linspace(0, 30, 50)
        t_out, result = model.solve(t, I=200, T=25)
        assert result.shape == (50, 4)
    
    def test_nutrient_consumption(self):
        model = AlgaeGrowthModel(Chl0=10, N0=500, P0=50)
        t = np.linspace(0, 30, 50)
        t_out, result = model.solve(t, I=200, T=25)
        # 营养盐应减少
        assert result[-1, 1] < result[0, 1]  # N
        assert result[-1, 2] < result[0, 2]  # P


class TestHelperFunctions:
    def test_assess_bloom_risk(self):
        status1, level1 = assess_bloom_risk(5)
        assert status1 == "Normal"
        
        status2, level2 = assess_bloom_risk(20)
        assert status2 == "Warning"
        
        status3, level3 = assess_bloom_risk(50)
        assert status3 == "Bloom"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
