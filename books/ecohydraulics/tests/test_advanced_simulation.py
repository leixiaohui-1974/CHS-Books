"""测试高级模拟技术模型"""

import pytest
import numpy as np
from code.models.advanced_simulation import (
    ShallowWater2D,
    AgentBasedFish,
    MLFlowPredictor,
    CFDFishway,
    RemoteSensingGIS,
    simulate_fishway_optimization
)


class TestShallowWater2D:
    """测试2D浅水方程"""
    
    def test_initialization(self):
        """测试初始化"""
        sw = ShallowWater2D(50, 30, 1.0, 1.0)
        assert sw.nx == 50
        assert sw.ny == 30
    
    def test_set_conditions(self):
        """测试设置条件"""
        sw = ShallowWater2D(50, 30, 1.0, 1.0)
        h0 = np.ones((30, 50)) * 2.0
        sw.set_initial_conditions(h0)
        assert np.allclose(sw.h, 2.0)
    
    def test_simulation(self):
        """测试模拟"""
        sw = ShallowWater2D(20, 15, 1.0, 1.0)
        h0 = np.ones((15, 20)) * 1.5
        h0[7:9, 8:12] = 2.5  # 初始扰动
        sw.set_initial_conditions(h0)
        
        results = sw.simulate(1.0, 0.01)
        assert len(results) > 0
        assert 'h' in results[0]


class TestAgentBasedFish:
    """测试智能体鱼类模型"""
    
    def test_initialization(self):
        """测试初始化"""
        fish = AgentBasedFish(50, (100, 50))
        assert fish.n_fish == 50
        assert fish.positions.shape == (50, 2)
    
    def test_behavior(self):
        """测试行为"""
        fish = AgentBasedFish(10, (100, 50))
        force = fish.compute_behavior(0)
        assert force.shape == (2,)
    
    def test_simulation(self):
        """测试模拟"""
        fish = AgentBasedFish(20, (100, 50))
        results = fish.simulate(5.0, 0.1)
        assert len(results) > 0
        assert 'positions' in results[0]


class TestMLFlowPredictor:
    """测试机器学习预测"""
    
    def test_initialization(self):
        """测试初始化"""
        ml = MLFlowPredictor()
        assert ml.is_trained == False
    
    def test_training(self):
        """测试训练"""
        ml = MLFlowPredictor()
        X, y = ml.generate_training_data(100)
        ml.train(X, y, epochs=50)
        assert ml.is_trained == True
    
    def test_prediction(self):
        """测试预测"""
        ml = MLFlowPredictor()
        X, y = ml.generate_training_data(100)
        ml.train(X, y, epochs=50)
        
        X_test = X[:10]
        y_pred = ml.predict(X_test)
        assert y_pred.shape == (10,)
        assert np.all(y_pred >= 0)
    
    def test_evaluation(self):
        """测试评估"""
        ml = MLFlowPredictor()
        X, y = ml.generate_training_data(200)
        ml.train(X[:150], y[:150], epochs=50)
        
        metrics = ml.evaluate(X[150:], y[150:])
        assert 'r2' in metrics
        assert 'rmse' in metrics


class TestCFDFishway:
    """测试CFD鱼道"""
    
    def test_initialization(self):
        """测试初始化"""
        cfd = CFDFishway(10.0, 3.0, 50, 20)
        assert cfd.L == 10.0
        assert cfd.W == 3.0
    
    def test_add_baffle(self):
        """测试添加挡板"""
        cfd = CFDFishway(10.0, 3.0, 50, 20)
        cfd.add_baffle(2.0, 0.5, 2.2, 2.5)
        assert np.any(cfd.obstacles)
    
    def test_flow_solution(self):
        """测试流场求解"""
        cfd = CFDFishway(10.0, 3.0, 30, 15)
        cfd.solve_flow_field(1.0, 50)
        assert np.max(np.abs(cfd.u)) > 0
    
    def test_suitability(self):
        """测试适宜性"""
        cfd = CFDFishway(10.0, 3.0, 30, 15)
        cfd.solve_flow_field(1.0, 50)
        suitability = cfd.fish_passage_suitability()
        assert suitability.shape == cfd.u.shape
        assert np.all((suitability >= 0) & (suitability <= 1))


class TestRemoteSensingGIS:
    """测试遥感GIS"""
    
    def test_initialization(self):
        """测试初始化"""
        rs = RemoteSensingGIS((100, 100), 30.0)
        assert rs.rows == 100
        assert rs.cols == 100
    
    def test_ndvi(self):
        """测试NDVI"""
        rs = RemoteSensingGIS((50, 50), 30.0)
        ndvi = rs.compute_ndvi()
        assert ndvi.shape == (50, 50)
        assert np.all((ndvi >= -1) & (ndvi <= 1))
    
    def test_classification(self):
        """测试分类"""
        rs = RemoteSensingGIS((50, 50), 30.0)
        classification = rs.classify_land_cover()
        assert 'water' in classification
        assert 'vegetation' in classification
    
    def test_statistics(self):
        """测试统计"""
        rs = RemoteSensingGIS((50, 50), 30.0)
        stats = rs.compute_area_statistics()
        assert len(stats) > 0
        total_pct = sum(v['percentage'] for v in stats.values())
        assert abs(total_pct - 100) < 1  # 允许小误差


class TestIntegrationFunctions:
    """测试集成功能"""
    
    def test_fishway_optimization(self):
        """测试鱼道优化"""
        result = simulate_fishway_optimization(10.0, 3.0, 3)
        assert 'average_suitability' in result
        assert 0 <= result['average_suitability'] <= 1
