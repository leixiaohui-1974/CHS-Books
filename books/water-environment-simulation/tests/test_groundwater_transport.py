"""
测试地下水污染物运移模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.groundwater_transport import (GroundwaterColumn1D, 
                                          calculate_retardation_factor,
                                          calculate_breakthrough_time)


class TestGroundwaterColumn1D:
    def test_initialization(self):
        model = GroundwaterColumn1D(L=1.0, nx=100, theta=0.3, Kd=0.5)
        assert model.L == 1.0
        assert model.nx == 100
        assert model.R > 1  # 有吸附时R>1
    
    def test_solve(self):
        model = GroundwaterColumn1D(L=1.0, nx=50, theta=0.3, Kd=0)
        t = np.linspace(0, 5, 50)
        t_out, x_out, C_history = model.solve(t, v=0.1, D=0.01, C_in=100)
        assert C_history.shape == (50, 50)
        assert C_history[0, 0] == 0  # 初始浓度
    
    def test_retardation_effect(self):
        # 无吸附
        model1 = GroundwaterColumn1D(L=1.0, nx=50, theta=0.3, Kd=0)
        t = np.linspace(0, 10, 100)
        t1, x1, C1 = model1.solve(t, v=0.1, D=0.01, C_in=100)
        
        # 有吸附
        model2 = GroundwaterColumn1D(L=1.0, nx=50, theta=0.3, Kd=1.0)
        t2, x2, C2 = model2.solve(t, v=0.1, D=0.01, C_in=100)
        
        # 有吸附时出口浓度应更低
        assert C2[-1, -1] < C1[-1, -1]


class TestHelperFunctions:
    def test_calculate_retardation_factor(self):
        R = calculate_retardation_factor(theta=0.3, rho_b=1.5, Kd=0.5)
        expected = 1 + 1.5 * 0.5 / 0.3
        assert abs(R - expected) < 0.01
    
    def test_calculate_breakthrough_time(self):
        t = calculate_breakthrough_time(L=1.0, v=0.1, R=2.0)
        expected = 2.0 * 1.0 / 0.1
        assert abs(t - expected) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
