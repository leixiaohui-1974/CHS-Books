"""测试产卵场模型"""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.spawning_ground import (
    FishEgg, SpawningGround,
    create_chinese_carp_egg,
    create_standard_spawning_ground
)

class TestFishEgg:
    def test_initialization(self):
        egg = FishEgg(diameter=4.5, density=1005.0)
        assert egg.diameter == 4.5
        assert egg.density == 1005.0
    
    def test_settling_velocity(self):
        egg = create_chinese_carp_egg()
        w_s = egg.settling_velocity()
        assert w_s > 0
        assert w_s < 0.1  # 合理范围
    
    def test_suspension_velocity_threshold(self):
        egg = create_chinese_carp_egg()
        v_susp = egg.suspension_velocity_threshold()
        assert v_susp > 0
        assert v_susp < 2.0


class TestSpawningGround:
    def test_drift_distance(self):
        sg = create_standard_spawning_ground()
        dist = sg.drift_distance(1.0, 3.0, 24.0)
        assert dist > 0
        assert 30000 < dist < 100000  # 30-100 km
    
    def test_optimal_flow_velocity_range(self):
        sg = create_standard_spawning_ground()
        v_min, v_max = sg.optimal_flow_velocity_range()
        assert v_min < v_max
        assert 0.5 < v_min < 1.5
        assert 1.0 < v_max < 2.0
    
    def test_substrate_suitability(self):
        sg = create_standard_spawning_ground(d50=30.0)
        result = sg.substrate_suitability()
        assert 'score' in result
        assert result['score'] > 0.5
    
    def test_spawning_condition_assessment(self):
        sg = create_standard_spawning_ground()
        assessment = sg.spawning_condition_assessment(1.0, 3.0, 0.7)
        assert 'overall_score' in assessment
        assert 'grade' in assessment
        assert 0 <= assessment['overall_score'] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
