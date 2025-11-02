"""测试鱼类种群动力学模型"""

import pytest
import numpy as np
from code.models.fish_population import (
    RiverConnectivityIndex,
    FishPopulationModel,
    create_connectivity_scenario
)


class TestRiverConnectivityIndex:
    """测试河流连通性指数"""
    
    def test_initialization(self):
        """测试初始化"""
        segments = [100, 100, 100]
        barriers = [{'position': 1, 'passability': 0.5}]
        
        rci = RiverConnectivityIndex(segments, barriers)
        
        assert rci.total_length == 300
        assert len(rci.barriers) == 1
    
    def test_dci_no_barriers(self):
        """测试无障碍连通性"""
        segments = [100, 100, 100]
        barriers = []
        
        rci = RiverConnectivityIndex(segments, barriers)
        dci = rci.calculate_dci()
        
        # 无障碍应该是1.0
        assert abs(dci - 1.0) < 1e-6
    
    def test_dci_with_barriers(self):
        """测试有障碍连通性"""
        segments = [100, 100, 100]
        barriers = [{'position': 1, 'passability': 0.3}]
        
        rci = RiverConnectivityIndex(segments, barriers)
        dci = rci.calculate_dci()
        
        # 有障碍应该小于1.0
        assert dci < 1.0
        assert dci > 0
    
    def test_dci_multiple_barriers(self):
        """测试多个障碍"""
        segments = [100, 100, 100]
        
        # 一个障碍
        rci1 = RiverConnectivityIndex(segments, [{'position': 1, 'passability': 0.5}])
        dci1 = rci1.calculate_dci()
        
        # 两个障碍
        rci2 = RiverConnectivityIndex(segments, [
            {'position': 0, 'passability': 0.5},
            {'position': 1, 'passability': 0.5}
        ])
        dci2 = rci2.calculate_dci()
        
        # 障碍越多，连通性越差
        assert dci2 < dci1


class TestFishPopulationModel:
    """测试种群动力学模型"""
    
    def test_initialization(self):
        """测试初始化"""
        pop = FishPopulationModel(1000, 5000, 0.5)
        
        assert pop.N0 == 1000
        assert pop.K == 5000
        assert pop.r == 0.5
    
    def test_logistic_growth(self):
        """测试Logistic增长"""
        pop = FishPopulationModel(1000, 5000, 0.5)
        
        # t=0时应该是初始值
        N0 = pop.logistic_growth(0)
        assert abs(N0 - 1000) < 1
        
        # 随时间增长
        N10 = pop.logistic_growth(10)
        assert N10 > 1000
        assert N10 <= 5000
        
        # 最终趋近容纳量
        N100 = pop.logistic_growth(100)
        assert abs(N100 - 5000) < 100
    
    def test_simulate_population(self):
        """测试种群模拟"""
        pop = FishPopulationModel(1000, 5000, 0.5)
        
        t, N = pop.simulate_population(20)
        
        assert len(t) == len(N)
        assert len(t) > 0
        assert N[0] <= 1100  # 初始值附近
        assert N[-1] > 1000  # 有增长
    
    def test_recovery_time(self):
        """测试恢复时间"""
        pop = FishPopulationModel(1000, 5000, 0.5)
        
        # 恢复到90%容纳量
        t_recovery = pop.recovery_time(0.9)
        
        assert t_recovery > 0
        assert t_recovery < 100
        
        # 验证：t_recovery时刻种群应接近目标
        N_target = 5000 * 0.9
        N_at_recovery = pop.logistic_growth(t_recovery)
        assert abs(N_at_recovery - N_target) < 500
    
    def test_recovery_already_reached(self):
        """测试已达到目标的情况"""
        # 初始种群已经很高
        pop = FishPopulationModel(4500, 5000, 0.5)
        
        t_recovery = pop.recovery_time(0.9)
        
        # 应该是0或很小
        assert t_recovery < 1


class TestConnectivityScenario:
    """测试连通性场景"""
    
    def test_create_scenario(self):
        """测试场景创建"""
        scenario = create_connectivity_scenario(3)
        
        assert len(scenario.river_segments) == 4
        assert len(scenario.barriers) == 3
        
        dci = scenario.calculate_dci()
        assert 0 < dci < 1
