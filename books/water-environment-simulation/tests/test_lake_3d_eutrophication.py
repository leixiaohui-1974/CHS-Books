"""
测试3D湖泊富营养化模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.lake_3d_eutrophication import Lake3DEutrophication, calculate_bloom_area


class TestLake3DEutrophication:
    def test_initialization(self):
        model = Lake3DEutrophication(Lx=10000, Ly=8000, H=3, nx=50, ny=40, nz=3)
        assert model.Lx == 10000
        assert model.Chl.shape == (3, 40, 50)
    
    def test_simulate_wind_driven_transport(self):
        model = Lake3DEutrophication(Lx=10000, Ly=8000, H=3, nx=50, ny=40, nz=3)
        model.Chl[0, 20, 25] = 50
        Chl_field = model.simulate_wind_driven_transport(wind_speed=5, wind_dir=90, dt=100, n_steps=10)
        assert Chl_field.shape == (3, 40, 50)


class TestHelperFunctions:
    def test_calculate_bloom_area(self):
        Chl_field = np.random.rand(3, 40, 50) * 50
        area = calculate_bloom_area(Chl_field, threshold=30)
        assert 0 <= area <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
