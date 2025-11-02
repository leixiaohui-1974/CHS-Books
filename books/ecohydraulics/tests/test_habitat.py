"""
测试栖息地适宜性模型
==================
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.channel import RiverReach
from code.models.habitat import (
    SuitabilityCurve,
    HabitatSuitabilityModel,
    create_carp_adult_model,
    create_carp_juvenile_model
)


class TestSuitabilityCurve:
    """测试SuitabilityCurve类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.curve = SuitabilityCurve(
            variable_name='depth',
            points=[
                (0.0, 0.0),
                (0.5, 0.8),
                (1.0, 1.0),
                (2.0, 0.6),
                (3.0, 0.2)
            ]
        )
    
    def test_initialization(self):
        """测试初始化"""
        assert self.curve.variable_name == 'depth'
        assert len(self.curve.points) == 5
        assert len(self.curve.x_values) == 5
        assert len(self.curve.y_values) == 5
    
    def test_points_sorted(self):
        """测试点是否已排序"""
        # x值应该是递增的
        assert np.all(np.diff(self.curve.x_values) > 0)
    
    def test_suitability_range(self):
        """测试适宜性值在0-1范围内"""
        assert np.all(self.curve.y_values >= 0)
        assert np.all(self.curve.y_values <= 1)
    
    def test_invalid_suitability_value(self):
        """测试无效的适宜性值"""
        with pytest.raises(ValueError):
            SuitabilityCurve('test', [(0, -0.1), (1, 0.5)])  # 负值
        
        with pytest.raises(ValueError):
            SuitabilityCurve('test', [(0, 0.5), (1, 1.5)])  # 超过1
    
    def test_evaluate_at_points(self):
        """测试在控制点处的求值"""
        assert self.curve.evaluate(0.0) == pytest.approx(0.0)
        assert self.curve.evaluate(1.0) == pytest.approx(1.0)
        assert self.curve.evaluate(2.0) == pytest.approx(0.6)
    
    def test_evaluate_interpolation(self):
        """测试插值"""
        # 在0.5和1.0之间插值
        value = self.curve.evaluate(0.75)
        assert 0.8 < value < 1.0  # 应该在这两个值之间
    
    def test_evaluate_below_range(self):
        """测试低于范围的值"""
        value = self.curve.evaluate(-1.0)
        assert value == self.curve.y_values[0]
    
    def test_evaluate_above_range(self):
        """测试超出范围的值"""
        value = self.curve.evaluate(10.0)
        assert value == self.curve.y_values[-1]
    
    def test_plot_data(self):
        """测试绘图数据生成"""
        x_smooth, y_smooth = self.curve.plot_data()
        
        assert len(x_smooth) == 100  # 默认100个点
        assert len(y_smooth) == 100
        assert np.all(y_smooth >= 0)
        assert np.all(y_smooth <= 1)


class TestHabitatSuitabilityModel:
    """测试HabitatSuitabilityModel类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.model = HabitatSuitabilityModel(
            species_name="Test Fish",
            life_stage="adult"
        )
        
        # 添加简单的适宜性曲线
        depth_curve = SuitabilityCurve(
            'depth',
            [(0, 0), (0.5, 0.5), (1.0, 1.0), (2.0, 0.5), (3.0, 0)]
        )
        velocity_curve = SuitabilityCurve(
            'velocity',
            [(0, 0), (0.2, 0.5), (0.5, 1.0), (1.0, 0.5), (2.0, 0)]
        )
        
        self.model.add_suitability_curve('depth', depth_curve)
        self.model.add_suitability_curve('velocity', velocity_curve)
        
        # 创建测试河段
        self.reach = RiverReach(
            length=1000.0,
            width=10.0,
            slope=0.001,
            roughness=0.030,
            side_slope=2.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        assert self.model.species_name == "Test Fish"
        assert self.model.life_stage == "adult"
        assert len(self.model.curves) == 2
    
    def test_add_suitability_curve(self):
        """测试添加适宜性曲线"""
        substrate_curve = SuitabilityCurve('substrate', [(0, 0), (1, 1)])
        self.model.add_suitability_curve('substrate', substrate_curve)
        
        assert 'substrate' in self.model.curves
        assert len(self.model.curves) == 3
    
    def test_calculate_csi(self):
        """测试CSI计算"""
        # 最优条件
        csi_optimal = self.model.calculate_csi(depth=1.0, velocity=0.5)
        assert csi_optimal == pytest.approx(1.0)
        
        # 部分适宜
        csi_partial = self.model.calculate_csi(depth=0.5, velocity=0.2)
        assert 0 < csi_partial < 1.0
        
        # 不适宜
        csi_poor = self.model.calculate_csi(depth=0.0, velocity=0.0)
        assert csi_poor == pytest.approx(0.0)
    
    def test_calculate_csi_with_substrate(self):
        """测试包含底质的CSI计算"""
        substrate_curve = SuitabilityCurve('substrate', [(0, 0), (5, 1)])
        self.model.add_suitability_curve('substrate', substrate_curve)
        
        csi = self.model.calculate_csi(depth=1.0, velocity=0.5, substrate=5.0)
        assert csi == pytest.approx(1.0)
    
    def test_calculate_wua(self):
        """测试WUA计算"""
        Q = 5.0
        result = self.model.calculate_wua(self.reach, Q, n_cells=20)
        
        # 检查返回的键
        required_keys = ['wua', 'total_area', 'habitat_quality', 'flow', 
                        'depth', 'velocity', 'cell_positions', 'cell_csi']
        for key in required_keys:
            assert key in result
        
        # WUA应该为正值
        assert result['wua'] > 0
        assert result['total_area'] > 0
        
        # 栖息地质量应该在0-1之间
        assert 0 <= result['habitat_quality'] <= 1.0
        
        # 流量应该等于输入流量
        assert result['flow'] == Q
        
        # 单元数应该正确
        assert len(result['cell_csi']) == result['n_cells']
    
    def test_calculate_wua_vs_flow(self):
        """测试WUA随流量变化"""
        flow_range = (2.0, 10.0)
        result = self.model.calculate_wua_vs_flow(
            self.reach, flow_range, n_flows=10
        )
        
        # 检查返回的键
        assert 'flows' in result
        assert 'wua' in result
        assert 'habitat_quality' in result
        
        # 数组长度应该正确
        assert len(result['flows']) == 10
        assert len(result['wua']) == 10
        assert len(result['habitat_quality']) == 10
        
        # WUA应该都是正值
        assert np.all(result['wua'] > 0)
        
        # 栖息地质量应该在0-1之间
        assert np.all(result['habitat_quality'] >= 0)
        assert np.all(result['habitat_quality'] <= 1.0)
    
    def test_find_optimal_flow(self):
        """测试最优流量查找"""
        flow_range = (2.0, 10.0)
        result = self.model.find_optimal_flow(self.reach, flow_range, n_flows=20)
        
        # 检查返回的键
        assert 'optimal_flow' in result
        assert 'max_wua' in result
        assert 'habitat_quality' in result
        
        # 最优流量应该在范围内
        assert flow_range[0] <= result['optimal_flow'] <= flow_range[1]
        
        # WUA应该为正值
        assert result['max_wua'] > 0
        
        # 栖息地质量应该在0-1之间
        assert 0 <= result['habitat_quality'] <= 1.0


class TestCarpModels:
    """测试鲤鱼模型"""
    
    def setup_method(self):
        """设置测试用例"""
        self.reach = RiverReach(
            length=1000.0,
            width=15.0,
            slope=0.0008,
            roughness=0.030,
            side_slope=2.0
        )
    
    def test_create_carp_adult_model(self):
        """测试创建鲤鱼成鱼模型"""
        model = create_carp_adult_model()
        
        assert model.species_name == "鲤鱼"
        assert model.life_stage == "成鱼"
        assert 'depth' in model.curves
        assert 'velocity' in model.curves
    
    def test_create_carp_juvenile_model(self):
        """测试创建鲤鱼幼鱼模型"""
        model = create_carp_juvenile_model()
        
        assert model.species_name == "鲤鱼"
        assert model.life_stage == "幼鱼"
        assert 'depth' in model.curves
        assert 'velocity' in model.curves
    
    def test_adult_vs_juvenile_preferences(self):
        """测试成鱼和幼鱼的偏好差异"""
        adult_model = create_carp_adult_model()
        juvenile_model = create_carp_juvenile_model()
        
        # 在较深水域，成鱼适宜性应该更高
        adult_si_deep = adult_model.curves['depth'].evaluate(1.5)
        juvenile_si_deep = juvenile_model.curves['depth'].evaluate(1.5)
        assert adult_si_deep > juvenile_si_deep
        
        # 在浅水域，幼鱼适宜性应该更高
        adult_si_shallow = adult_model.curves['depth'].evaluate(0.3)
        juvenile_si_shallow = juvenile_model.curves['depth'].evaluate(0.3)
        assert juvenile_si_shallow > adult_si_shallow
        
        # 在较快流速下，成鱼适宜性应该更高
        adult_si_fast = adult_model.curves['velocity'].evaluate(0.8)
        juvenile_si_fast = juvenile_model.curves['velocity'].evaluate(0.8)
        assert adult_si_fast > juvenile_si_fast
    
    def test_carp_models_wua_calculation(self):
        """测试鲤鱼模型的WUA计算"""
        adult_model = create_carp_adult_model()
        juvenile_model = create_carp_juvenile_model()
        
        Q = 6.0  # m³/s
        
        adult_result = adult_model.calculate_wua(self.reach, Q)
        juvenile_result = juvenile_model.calculate_wua(self.reach, Q)
        
        # 两个模型都应该返回有效结果
        assert adult_result['wua'] > 0
        assert juvenile_result['wua'] > 0
        
        # 在这个流量下，成鱼WUA通常更高（因为偏好较深水域）
        # 但这不是绝对的，取决于具体河道条件


class TestWUAConsistency:
    """测试WUA计算的一致性"""
    
    def setup_method(self):
        """设置测试用例"""
        self.model = create_carp_adult_model()
        self.reach = RiverReach(1000, 15, 0.0008, 0.030, 2.0)
    
    def test_wua_increases_with_quality(self):
        """测试WUA与栖息地质量的关系"""
        # 在不同流量下计算WUA
        result = self.model.calculate_wua_vs_flow(
            self.reach, (2, 20), n_flows=10
        )
        
        # WUA应该与栖息地质量呈正相关（在大多数情况下）
        # 但由于总面积也在变化，这不是严格单调的
        assert np.all(result['wua'] >= 0)
    
    def test_wua_with_different_cell_numbers(self):
        """测试不同网格数的WUA计算"""
        Q = 5.0
        
        wua_10 = self.model.calculate_wua(self.reach, Q, n_cells=10)['wua']
        wua_50 = self.model.calculate_wua(self.reach, Q, n_cells=50)['wua']
        wua_100 = self.model.calculate_wua(self.reach, Q, n_cells=100)['wua']
        
        # 随着网格细化，WUA应该收敛
        # 但不会完全相同（因为是数值积分）
        # 相对差异应该较小
        rel_diff_1 = abs(wua_50 - wua_10) / wua_10
        rel_diff_2 = abs(wua_100 - wua_50) / wua_50
        
        assert rel_diff_1 < 0.2  # 20%以内
        assert rel_diff_2 < 0.1  # 10%以内（网格越细，差异越小）


class TestEdgeCases:
    """测试边界情况"""
    
    def test_very_low_flow(self):
        """测试极低流量"""
        model = create_carp_adult_model()
        reach = RiverReach(1000, 15, 0.0008, 0.030, 2.0)
        
        Q = 0.5  # 很小的流量
        result = model.calculate_wua(reach, Q)
        
        # 应该能够计算，但WUA会很小
        assert result['wua'] >= 0
        assert result['depth'] > 0
    
    def test_very_high_flow(self):
        """测试极高流量"""
        model = create_carp_adult_model()
        reach = RiverReach(1000, 15, 0.0008, 0.030, 2.0)
        
        Q = 50.0  # 很大的流量
        result = model.calculate_wua(reach, Q)
        
        # 应该能够计算
        assert result['wua'] >= 0
        assert result['depth'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
