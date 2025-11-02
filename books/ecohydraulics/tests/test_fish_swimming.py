"""测试鱼类游泳能力模型"""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.fish_swimming import (
    FishSwimmingModel,
    create_grass_carp,
    create_black_carp,
    create_common_carp,
    create_silver_carp
)

class TestFishSwimmingModel:
    """测试鱼类游泳模型基本功能"""
    
    def test_initialization(self):
        """测试模型初始化"""
        fish = FishSwimmingModel("草鱼", body_length=30.0, temperature=20.0)
        assert fish.species == "草鱼"
        assert fish.body_length == 30.0
        assert fish.temperature == 20.0
        assert fish.body_weight > 0
    
    def test_weight_estimation(self):
        """测试体重估算"""
        # 30cm鱼类体重应该在合理范围内
        weight = FishSwimmingModel.estimate_weight(30.0)
        assert 200 < weight < 400  # g
        
        # 体长越大体重越大
        w1 = FishSwimmingModel.estimate_weight(20.0)
        w2 = FishSwimmingModel.estimate_weight(40.0)
        assert w2 > w1
    
    def test_sustained_speed(self):
        """测试持续游速计算"""
        fish = create_grass_carp(body_length=30.0)
        v_sustained = fish.sustained_speed()
        
        # 持续游速应该在合理范围内
        assert 0.3 < v_sustained < 1.5  # m/s
        
        # 体长越大游速越快
        fish_small = create_grass_carp(body_length=20.0)
        fish_large = create_grass_carp(body_length=40.0)
        assert fish_large.sustained_speed() > fish_small.sustained_speed()
    
    def test_burst_speed(self):
        """测试爆发游速计算"""
        fish = create_grass_carp(body_length=30.0)
        v_burst = fish.burst_speed()
        v_sustained = fish.sustained_speed()
        
        # 爆发游速应该大于持续游速
        assert v_burst > v_sustained
        
        # 爆发游速应该在合理范围内
        assert v_burst < 10.0  # m/s
    
    def test_critical_speed(self):
        """测试临界游速"""
        fish = create_grass_carp(body_length=30.0)
        v_crit = fish.critical_speed()
        v_sustained = fish.sustained_speed()
        v_burst = fish.burst_speed()
        
        # 临界游速应该在持续和爆发之间
        assert v_sustained < v_crit < v_burst
    
    def test_temperature_effect(self):
        """测试水温影响"""
        fish_cold = create_grass_carp(body_length=30.0, temperature=10.0)
        fish_warm = create_grass_carp(body_length=30.0, temperature=25.0)
        
        # 温水中游速应该更快
        assert fish_warm.sustained_speed() > fish_cold.sustained_speed()
    
    def test_endurance_time(self):
        """测试耐力时间计算"""
        fish = create_grass_carp(body_length=30.0)
        
        # 持续游速下可以无限时间
        t1 = fish.endurance_time(fish.sustained_speed() * 0.9)
        assert t1 == np.inf
        
        # 爆发游速下耐力接近0
        t2 = fish.endurance_time(fish.burst_speed())
        assert t2 < 10.0  # 秒
        
        # 中间速度应该有有限的耐力时间
        t3 = fish.endurance_time(fish.critical_speed())
        assert 0 < t3 < np.inf
    
    def test_energy_expenditure(self):
        """测试能量消耗计算"""
        fish = create_grass_carp(body_length=30.0)
        
        # 速度越高能量消耗越大
        e1 = fish.energy_expenditure(0.5, 60.0)
        e2 = fish.energy_expenditure(1.0, 60.0)
        assert e2 > e1
        
        # 时间越长能量消耗越大
        e3 = fish.energy_expenditure(1.0, 60.0)
        e4 = fish.energy_expenditure(1.0, 120.0)
        assert e4 > e3


class TestSpeciesModels:
    """测试不同鱼类预设模型"""
    
    def test_grass_carp(self):
        """测试草鱼模型"""
        fish = create_grass_carp(body_length=30.0)
        assert fish.species == "草鱼"
        assert fish.body_length == 30.0
        summary = fish.swimming_performance_summary()
        assert 'sustained_speed_ms' in summary
    
    def test_black_carp(self):
        """测试青鱼模型"""
        fish = create_black_carp(body_length=30.0)
        assert fish.species == "青鱼"
        
        # 青鱼游泳能力应该比草鱼强
        grass = create_grass_carp(body_length=30.0)
        assert fish.sustained_speed() > grass.sustained_speed()
    
    def test_common_carp(self):
        """测试鲤鱼模型"""
        fish = create_common_carp(body_length=30.0)
        assert fish.species == "鲤鱼"
        
        # 鲤鱼游泳能力较弱
        assert fish.sustained_speed() < 1.0
    
    def test_silver_carp(self):
        """测试鲢鱼模型"""
        fish = create_silver_carp(body_length=30.0)
        assert fish.species == "鲢鱼"
        assert fish.sustained_speed() > 0


class TestDesignApplications:
    """测试工程设计应用"""
    
    def test_design_flow_velocity(self):
        """测试设计流速确定"""
        fish = create_common_carp(body_length=30.0)
        design_v, recommendation = fish.design_flow_velocity(safety_factor=0.8)
        
        # 设计流速应该是持续游速的80%
        assert design_v == pytest.approx(fish.sustained_speed() * 0.8, rel=0.01)
        assert isinstance(recommendation, str)
    
    def test_passage_ability(self):
        """测试通道通过能力评估"""
        fish = create_grass_carp(body_length=30.0)
        
        # 低流速应该能通过
        can_pass, time, msg = fish.can_pass_velocity(0.5, 20.0)
        assert can_pass is True
        assert time > 0
        assert isinstance(msg, str)
        
        # 极高流速应该无法通过
        can_pass2, _, _ = fish.can_pass_velocity(10.0, 20.0)
        assert can_pass2 is False
    
    def test_swimming_performance_summary(self):
        """测试游泳能力汇总"""
        fish = create_grass_carp(body_length=30.0)
        summary = fish.swimming_performance_summary()
        
        # 检查必要的键
        required_keys = [
            'species', 'body_length_cm', 'body_weight_g',
            'sustained_speed_ms', 'burst_speed_ms', 'critical_speed_ms'
        ]
        for key in required_keys:
            assert key in summary
        
        # 检查单位换算
        assert summary['sustained_speed_BLs'] > 0
        assert summary['burst_speed_BLs'] > summary['sustained_speed_BLs']


class TestEdgeCases:
    """测试边界条件"""
    
    def test_small_fish(self):
        """测试小体长鱼类"""
        fish = create_grass_carp(body_length=5.0)
        assert fish.sustained_speed() > 0
        assert fish.burst_speed() > fish.sustained_speed()
    
    def test_large_fish(self):
        """测试大体长鱼类"""
        fish = create_grass_carp(body_length=100.0)
        assert fish.sustained_speed() > 0
        # 大鱼游速更快
        small_fish = create_grass_carp(body_length=20.0)
        assert fish.sustained_speed() > small_fish.sustained_speed()
    
    def test_extreme_temperature(self):
        """测试极端温度"""
        # 低温
        fish_cold = create_grass_carp(body_length=30.0, temperature=5.0)
        # 高温
        fish_hot = create_grass_carp(body_length=30.0, temperature=30.0)
        
        # 都应该能正常计算
        assert fish_cold.sustained_speed() > 0
        assert fish_hot.sustained_speed() > 0
    
    def test_zero_passage_length(self):
        """测试零长度通道"""
        fish = create_grass_carp(body_length=30.0)
        can_pass, time, _ = fish.can_pass_velocity(1.0, 0.0)
        assert can_pass is True
        assert time == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
