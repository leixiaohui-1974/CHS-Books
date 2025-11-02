"""
测试多层含水层模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.multilayer_aquifer import MultilayerAquifer, assess_aquitard_protection


class TestMultilayerAquifer:
    def test_initialization(self):
        model = MultilayerAquifer(layers=20, dz=2)
        assert model.layers == 20
        assert len(model.C) == 20
    
    def test_solve(self):
        model = MultilayerAquifer(layers=10, dz=1)
        model.C[0] = 100
        t = np.linspace(0, 10, 20)
        t_out, z_out, C_history = model.solve(t, Kz=0.1)
        assert C_history.shape == (20, 10)


class TestHelperFunctions:
    def test_assess_aquitard_protection(self):
        protection = assess_aquitard_protection(100, 10)
        assert protection == 90


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
