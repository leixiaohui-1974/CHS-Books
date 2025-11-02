"""
测试 core.hydrology 模块
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# 添加code目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../code"))

from core.hydrology.water_balance import calculate_water_balance, WaterBalanceModel
from core.hydrology.runoff_calculation import (
    calculate_runoff_coefficient,
    estimate_annual_runoff,
    calculate_design_flood,
    calculate_baseflow_separation,
)


class TestWaterBalance:
    """测试水量平衡计算"""
    
    def test_calculate_water_balance(self):
        """测试基本水量平衡计算"""
        result = calculate_water_balance(
            precipitation=100,
            inflow=1000,
            evaporation=50,
            outflow=900,
            initial_storage=5000
        )
        
        assert 'storage_change' in result
        assert 'final_storage' in result
        assert 'balance_error' in result
        
        # 验证水量平衡
        # ΔS = P + I - E - O = 100 + 1000 - 50 - 900 = 150
        assert abs(result['storage_change'] - 150) < 0.01
        assert abs(result['final_storage'] - 5150) < 0.01
        
        # 平衡误差应该接近0
        assert abs(result['balance_error']) < 0.01
    
    def test_water_balance_model(self):
        """测试水量平衡模型"""
        model = WaterBalanceModel(area=1000, initial_storage=5000)
        
        # 单步计算
        result = model.step(
            precipitation=100,  # mm
            evaporation=50,     # mm
            inflow=100,         # m³/s
            outflow=80          # m³/s
        )
        
        assert 'storage_change' in result
        assert model.storage != 5000  # 蓄水量应该改变
    
    def test_water_balance_simulation(self):
        """测试连续模拟"""
        model = WaterBalanceModel(area=1000, initial_storage=5000)
        
        # 多时段模拟
        results = model.simulate(
            precipitation=[100, 120, 80, 90, 110],
            evaporation=[50, 60, 55, 45, 50]
        )
        
        assert len(results) == 5
        assert 'storage_change' in results.columns
        assert 'final_storage' in results.columns


class TestRunoffCalculation:
    """测试径流计算"""
    
    def test_calculate_runoff_coefficient(self):
        """测试径流系数计算"""
        alpha = calculate_runoff_coefficient(runoff=300, precipitation=500)
        assert abs(alpha - 0.6) < 0.01
        
        # 测试零降水
        alpha_zero = calculate_runoff_coefficient(runoff=300, precipitation=0)
        assert alpha_zero == 0.0
    
    def test_estimate_annual_runoff_by_coefficient(self):
        """测试径流系数法估算年径流"""
        runoff = estimate_annual_runoff(
            area=5000,
            precipitation=800,
            runoff_coefficient=0.6
        )
        
        assert runoff > 0
        # 计算检验：R = α * P * A = 0.6 * 800mm * 5000km² = 240万m³ = 24亿m³
        expected = 0.6 * 800 * 5000 * 0.0001
        assert abs(runoff - expected) < 0.1
    
    def test_estimate_annual_runoff_by_balance(self):
        """测试水量平衡法估算年径流"""
        runoff = estimate_annual_runoff(
            area=5000,
            precipitation=800,
            evaporation=400
        )
        
        assert runoff > 0
        # 计算检验：R = (P - E) * A = (800-400) * 5000 * 0.0001 = 20亿m³
        expected = (800 - 400) * 5000 * 0.0001
        assert abs(runoff - expected) < 0.1
    
    def test_calculate_design_flood(self):
        """测试设计洪水计算"""
        peak_flow, total_volume = calculate_design_flood(
            area=500,
            precipitation=120,
            duration=6,
            runoff_coefficient=0.7
        )
        
        assert peak_flow > 0
        assert total_volume > 0
        
        # 检查洪水总量
        # V = R * A * 100 = 0.7 * 120 * 500 * 100 = 4200万m³
        expected_volume = 0.7 * 120 * 500 * 100
        assert abs(total_volume - expected_volume) < 10
    
    def test_calculate_baseflow_separation(self):
        """测试基流分割"""
        discharge = np.array([10, 50, 100, 80, 50, 30, 20, 15])
        baseflow, surface_flow = calculate_baseflow_separation(discharge)
        
        assert len(baseflow) == len(discharge)
        assert len(surface_flow) == len(discharge)
        
        # 基流应该比总流量小
        assert all(baseflow <= discharge)
        
        # 基流 + 地表径流 ≈ 总流量
        total = baseflow + surface_flow
        assert all(abs(total - discharge) < 1)


# 如果直接运行此文件
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
