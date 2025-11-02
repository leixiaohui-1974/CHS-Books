"""
测试二维含水层污染羽模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.aquifer_2d import Aquifer2D, assess_well_risk


class TestAquifer2D:
    def test_initialization(self):
        model = Aquifer2D(Lx=500, Ly=300, nx=50, ny=30)
        assert model.Lx == 500
        assert model.Ly == 300
        assert model.C.shape == (30, 50)
    
    def test_solve_transport(self):
        model = Aquifer2D(Lx=100, Ly=100, nx=30, ny=30)
        t = np.linspace(0, 10, 20)
        t_out, C_history = model.solve_transport(t, vx=0.5, vy=0, Dx=1, Dy=1, 
                                                  source_x=10, source_y=50)
        assert len(C_history) > 0


class TestHelperFunctions:
    def test_assess_well_risk(self):
        C_field = np.zeros((60, 100))
        C_field[30, 60] = 20  # 高浓度点
        at_risk, conc = assess_well_risk(C_field, 300, 150, 500, 300, threshold=10)
        assert isinstance(at_risk, (bool, np.bool_))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
