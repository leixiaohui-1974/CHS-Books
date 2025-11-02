"""测试洪泛区湿地模型"""

import pytest
import numpy as np
from code.models.floodplain_wetland import (
    FloodplainHydraulics,
    WetlandConnectivity,
    JuvenileFishGrowth,
    design_ecological_gate_operation
)


class TestFloodplainHydraulics:
    """测试漫滩水力学"""
    
    def test_initialization(self):
        """测试初始化"""
        fp = FloodplainHydraulics(50.0, 3.0, 200.0, 2.5, 0.0005)
        assert fp.Bc == 50.0
        assert fp.Hf == 2.5
    
    def test_inundation_area_no_overbank(self):
        """测试未漫滩情况"""
        fp = FloodplainHydraulics(50.0, 3.0, 200.0, 2.5, 0.0005)
        result = fp.inundation_area(50.0)
        
        assert not result['is_overbank']
        assert result['overbank_depth'] == 0.0
        assert result['inundated_width'] == 50.0
    
    def test_inundation_area_overbank(self):
        """测试漫滩情况"""
        fp = FloodplainHydraulics(50.0, 3.0, 200.0, 2.5, 0.0005)
        result = fp.inundation_area(800.0)
        
        assert result['is_overbank']
        assert result['overbank_depth'] > 0
        assert result['inundated_width'] > 50.0
    
    def test_threshold_discharge(self):
        """测试临界流量"""
        fp = FloodplainHydraulics(50.0, 3.0, 200.0, 2.5, 0.0005)
        Q_threshold = fp.overbank_threshold_discharge()
        
        assert Q_threshold > 0
        assert Q_threshold < 500  # 合理范围


class TestWetlandConnectivity:
    """测试湿地连通性"""
    
    def test_initialization(self):
        """测试初始化"""
        wetland = WetlandConnectivity(2.0, 50.0)
        assert wetland.elevation == 2.0
        assert wetland.area == 50.0
    
    def test_inundation_frequency(self):
        """测试淹没频率"""
        wetland = WetlandConnectivity(2.0, 50.0)
        
        # 模拟水深数据
        water_depths = np.array([1.5] * 100 + [2.5] * 100 + [1.8] * 165)
        
        result = wetland.inundation_frequency(water_depths)
        
        assert 0 <= result['inundation_frequency'] <= 1
        assert result['inundation_days'] >= 0
        assert result['inundation_days'] <= len(water_depths)
    
    def test_connectivity_index(self):
        """测试连通性指数"""
        wetland = WetlandConnectivity(2.0, 50.0)
        
        # 不同频率
        CI_low = wetland.connectivity_index(0.05)
        CI_optimal = wetland.connectivity_index(0.3)
        CI_high = wetland.connectivity_index(0.7)
        
        assert 0 <= CI_low <= 1
        assert 0 <= CI_optimal <= 1
        assert 0 <= CI_high <= 1
        
        # 最优频率应该有较高的连通性指数
        assert CI_optimal >= CI_low


class TestJuvenileFishGrowth:
    """测试幼鱼生长"""
    
    def test_initialization(self):
        """测试初始化"""
        fish = JuvenileFishGrowth("四大家鱼", 1.0)
        assert fish.species == "四大家鱼"
        assert fish.L0 == 1.0
    
    def test_growth_rate(self):
        """测试生长率"""
        fish = JuvenileFishGrowth()
        
        # 最优条件
        rate_opt = fish.growth_rate(25, 1.0)
        
        # 较差条件
        rate_poor = fish.growth_rate(15, 0.3)
        
        assert rate_opt > rate_poor
        assert rate_opt > 0
    
    def test_simulate_growth(self):
        """测试生长模拟"""
        fish = JuvenileFishGrowth("四大家鱼", 1.0)
        
        t, L = fish.simulate_growth(60, 25, 0.8)
        
        assert len(t) == 60
        assert len(L) == 60
        assert L[0] == 1.0
        assert L[-1] > L[0]  # 应该生长
    
    def test_wetland_suitability(self):
        """测试湿地适宜性"""
        fish = JuvenileFishGrowth()
        
        result = fish.wetland_suitability(1.5, 25, 0.5)
        
        assert 'overall_suitability' in result
        assert 'grade' in result
        assert 0 <= result['overall_suitability'] <= 1
        assert result['grade'] in ['优秀', '良好', '一般', '较差']


class TestGateOperation:
    """测试水闸调度"""
    
    def test_design_gate_operation(self):
        """测试调度方案设计"""
        monthly_flows = np.array([80, 90, 150, 300, 500, 600,
                                 400, 250, 180, 120, 100, 85])
        
        result = design_ecological_gate_operation(
            monthly_flows, 2.0, 0.3
        )
        
        assert 'flow_threshold' in result
        assert 'operations' in result
        assert len(result['operations']) == 12
        
        # 检查操作合理性
        for op in result['operations']:
            assert op['operation'] in ['开闸', '关闸']
