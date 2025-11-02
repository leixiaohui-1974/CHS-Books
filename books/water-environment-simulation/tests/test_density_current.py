"""
测试异重流模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.density_current import (DensityCurrent2D, calculate_densimetric_froude, estimate_underflow_velocity)


class TestDensityCurrent2D:
    def test_initialization(self):
        model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
        assert model.L == 1000
        assert model.H == 50
        assert model.C.shape == (25, 100)
    
    def test_calculate_density(self):
        model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
        rho = model.calculate_density(C=10)
        assert rho > model.rho_ambient
    
    def test_calculate_plunge_point(self):
        model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
        x_plunge = model.calculate_plunge_point(C_inflow=10, Q_inflow=50, H_reservoir=50)
        assert x_plunge >= 0
    
    def test_simulate_underflow(self):
        model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
        C_field = model.simulate_underflow(C_source=10, x_source=5, dt=10, n_steps=10)
        assert C_field.shape == (25, 100)
        assert np.max(C_field) > 0
    
    def test_assess_intake_risk(self):
        model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
        model.C[20, 50] = 1.0
        C_intake, risk = model.assess_intake_risk(x_intake=500, z_intake=40, C_threshold=0.5)
        assert C_intake >= 0


class TestHelperFunctions:
    def test_calculate_densimetric_froude(self):
        Fr = calculate_densimetric_froude(u=1.0, h=10, delta_rho=5, rho_ambient=1000)
        assert Fr > 0
    
    def test_estimate_underflow_velocity(self):
        u = estimate_underflow_velocity(delta_rho=5, rho_ambient=1000, h=10)
        assert u > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
