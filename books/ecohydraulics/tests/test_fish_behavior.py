"""测试鱼类行为响应模型"""

import pytest
import numpy as np
from code.models.fish_behavior import FeedingGroundModel, create_grass_carp_feeding_model


class TestFeedingGroundModel:
    """测试索饵场模型"""
    
    def test_initialization(self):
        """测试模型初始化"""
        model = FeedingGroundModel("草鱼")
        assert model.species == "草鱼"
        assert model.body_length > 0
        assert model.body_weight > 0
    
    def test_prey_density(self):
        """测试饵料密度计算"""
        model = create_grass_carp_feeding_model()
        
        # 中等流速密度最高
        density_low = model.prey_density_by_velocity(0.2)
        density_optimal = model.prey_density_by_velocity(0.5)
        density_high = model.prey_density_by_velocity(1.5)
        
        assert density_optimal > density_low
        assert density_optimal > density_high
        assert density_optimal > 0
    
    def test_feeding_efficiency(self):
        """测试摄食效率"""
        model = create_grass_carp_feeding_model()
        
        # 中等流速效率最高
        eff_low = model.feeding_efficiency(0.2, 500)
        eff_optimal = model.feeding_efficiency(0.6, 500)
        eff_high = model.feeding_efficiency(1.5, 500)
        
        assert eff_optimal >= eff_low
        assert eff_optimal >= eff_high
        assert eff_optimal > 0
    
    def test_energy_balance(self):
        """测试能量收支"""
        model = create_grass_carp_feeding_model()
        
        balance = model.energy_balance(0.6)
        
        assert 'prey_density' in balance
        assert 'feeding_efficiency' in balance
        assert 'energy_gain_J' in balance
        assert 'energy_cost_J' in balance
        assert 'net_energy_J' in balance
        assert 'is_favorable' in balance
        
        assert balance['energy_gain_J'] > 0
        assert balance['energy_cost_J'] > 0
    
    def test_optimal_velocity(self):
        """测试最优流速"""
        model = create_grass_carp_feeding_model()
        
        optimal_v = model.optimal_feeding_velocity()
        
        assert 0.2 < optimal_v < 1.5
        
        # 最优流速应有正能量收益
        balance = model.energy_balance(optimal_v)
        assert balance['net_energy_J'] > 0
    
    def test_velocity_range(self):
        """测试流速范围"""
        model = create_grass_carp_feeding_model()
        
        # 获取最优流速
        optimal_v = model.optimal_feeding_velocity()
        
        # 极低流速的净能量应该小于最优流速
        balance_low = model.energy_balance(0.1)
        balance_optimal = model.energy_balance(optimal_v)
        assert balance_low['net_energy_J'] < balance_optimal['net_energy_J']
        
        # 极高流速的净能量应该小于最优流速
        balance_high = model.energy_balance(2.0)
        assert balance_high['net_energy_J'] < balance_optimal['net_energy_J']
        
        # 最优流速应该有正能量收益
        assert balance_optimal['net_energy_J'] > 0
