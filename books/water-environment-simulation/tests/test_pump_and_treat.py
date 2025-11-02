"""
测试抽出-处理修复模型
"""

import pytest
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))
from models.pump_and_treat import PumpAndTreat, optimize_well_location


class TestPumpAndTreat:
    def test_initialization(self):
        model = PumpAndTreat(Lx=200, Ly=200, nx=50, ny=50)
        assert model.Lx == 200
        assert model.C.shape == (50, 50)
    
    def test_simulate_remediation(self):
        model = PumpAndTreat(Lx=100, Ly=100, nx=30, ny=30)
        model.C[15, 15] = 100
        t = np.linspace(0, 10, 20)
        t_out, C_history, mass = model.simulate_remediation(t, 50, 50, Q_pump=10)
        assert len(C_history) > 0


class TestHelperFunctions:
    def test_optimize_well_location(self):
        x, y = optimize_well_location((200, 200), (80, 100))
        assert x > 80  # 应该在下游


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
