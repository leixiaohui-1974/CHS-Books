"""测试底栖生物模型"""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from code.models.channel import RiverReach
from code.models.benthic import BenthicHabitatModel

class TestBenthicModel:
    def test_bed_shear_stress(self):
        reach = RiverReach(1000, 15, 0.002, 0.030, 2.0)
        h = 1.0
        tau = BenthicHabitatModel.bed_shear_stress(reach, h)
        assert tau > 0
        # 更大水深应该有更大剪应力
        tau2 = BenthicHabitatModel.bed_shear_stress(reach, 2.0)
        assert tau2 > tau
    
    def test_shields_number(self):
        tau = 10.0
        d50 = 0.02  # 20mm
        theta = BenthicHabitatModel.shields_number(tau, d50)
        assert theta > 0
        # 更细底质应该有更大Shields数
        theta2 = BenthicHabitatModel.shields_number(tau, 0.01)
        assert theta2 > theta
    
    def test_substrate_stability(self):
        stability = BenthicHabitatModel.substrate_stability(0.02)
        assert 'status' in stability
        assert stability['status'] in ['稳定', '基本稳定', '临界', '不稳定']
    
    def test_complete_workflow(self):
        reach = RiverReach(1000, 15, 0.002, 0.030, 2.0)
        Q = 15.0
        h = reach.solve_depth(Q)
        tau = BenthicHabitatModel.bed_shear_stress(reach, h)
        theta = BenthicHabitatModel.shields_number(tau, 0.02)
        stability = BenthicHabitatModel.substrate_stability(theta)
        assert stability['status'] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
