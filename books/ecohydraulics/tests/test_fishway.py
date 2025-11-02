"""测试竖缝式鱼道模型"""
import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.fishway import VerticalSlotFishway, create_standard_fishway

class TestVerticalSlotFishway:
    """测试竖缝式鱼道基本功能"""
    
    def test_initialization(self):
        """测试模型初始化"""
        fishway = VerticalSlotFishway(
            pool_length=3.0,
            pool_width=2.0,
            slot_width=0.3,
            drop_per_pool=0.2,
            num_pools=15
        )
        assert fishway.pool_length == 3.0
        assert fishway.pool_width == 2.0
        assert fishway.slot_width == 0.3
        assert fishway.drop_per_pool == 0.2
        assert fishway.num_pools == 15
    
    def test_pool_volume(self):
        """测试池室体积计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        V = fishway.pool_volume(water_depth=1.0)
        assert V == pytest.approx(6.0, rel=0.01)  # 3*2*1 = 6 m³
        
        # 体积应该与水深成正比
        V2 = fishway.pool_volume(water_depth=2.0)
        assert V2 == pytest.approx(12.0, rel=0.01)
    
    def test_slot_discharge(self):
        """测试竖缝流量计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q = fishway.slot_discharge(water_depth=1.0)
        
        # 流量应该为正
        assert Q > 0
        
        # 水深越大流量越大
        Q2 = fishway.slot_discharge(water_depth=1.5)
        assert Q2 > Q
    
    def test_slot_velocity(self):
        """测试竖缝流速计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q = 1.0  # m³/s
        h = 1.0  # m
        
        v = fishway.slot_velocity(Q, h)
        assert v > 0
        
        # 速度应该合理（一般在0.5-3.0 m/s之间）
        assert 0.1 < v < 5.0
    
    def test_energy_dissipation(self):
        """测试能量消散计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q = 1.0
        
        P = fishway.energy_dissipation(Q)
        
        # 功率应该为正
        assert P > 0
        
        # 流量越大功率越大
        P2 = fishway.energy_dissipation(2.0)
        assert P2 > P
    
    def test_volumetric_power_dissipation(self):
        """测试体积功率密度计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q = 1.0
        h = 1.0
        
        vpd = fishway.volumetric_power_dissipation(Q, h)
        
        # VPD应该为正
        assert vpd > 0
        
        # VPD应该在合理范围内（一般<200 W/m³）
        assert vpd < 500.0
    
    def test_design_water_depth(self):
        """测试设计水深计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q_target = 1.0
        
        h, acceptable = fishway.design_water_depth(Q_target, max_vpd=150.0)
        
        # 水深应该为正且合理
        assert h > 0
        assert h < 5.0
        
        # 检查VPD是否满足要求
        vpd = fishway.volumetric_power_dissipation(Q_target, h)
        if acceptable:
            assert vpd <= 150.0


class TestVelocityField:
    """测试流速场计算"""
    
    def test_velocity_field_shape(self):
        """测试流速场网格形状"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        X, Y, V = fishway.velocity_field(1.0, 1.0, nx=10, ny=8)
        
        # 检查形状
        assert X.shape == (8, 10)
        assert Y.shape == (8, 10)
        assert V.shape == (8, 10)
    
    def test_velocity_field_values(self):
        """测试流速场数值合理性"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        X, Y, V = fishway.velocity_field(1.0, 1.0)
        
        # 流速应该全部为正
        assert np.all(V >= 0)
        
        # 最大流速应该在竖缝附近
        max_v = np.max(V)
        assert max_v > 0
        
        # 流速应该在合理范围内
        assert max_v < 10.0
    
    def test_recirculation_area(self):
        """测试回流区面积计算"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        ratio = fishway.recirculation_area_ratio(1.0, 1.0, low_velocity_threshold=0.3)
        
        # 回流区比例应该在0-1之间
        assert 0 <= ratio <= 1
        
        # 应该存在一定比例的回流区
        assert ratio > 0


class TestFishwayGeometry:
    """测试鱼道几何参数"""
    
    def test_total_head_loss(self):
        """测试总水头损失"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        total_drop = fishway.total_head_loss()
        
        # 总落差 = 每池落差 × 池数
        expected = 0.2 * 15
        assert total_drop == pytest.approx(expected, rel=0.01)
    
    def test_fishway_length(self):
        """测试鱼道长度"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        length = fishway.fishway_length()
        
        # 总长 = 池长 × 池数
        expected = 3.0 * 15
        assert length == pytest.approx(expected, rel=0.01)
    
    def test_fishway_slope(self):
        """测试鱼道坡度"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        slope, reasonable = fishway.fishway_slope_check()
        
        # 坡度应该为正
        assert slope > 0
        
        # 坡度 = 总落差 / 总长度
        expected_slope = (0.2 * 15) / (3.0 * 15)
        assert slope == pytest.approx(expected_slope, rel=0.01)


class TestDesignSummary:
    """测试设计总结功能"""
    
    def test_design_summary_completeness(self):
        """测试设计总结完整性"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        summary = fishway.design_summary(1.0, 1.0)
        
        # 检查必要的键
        required_keys = [
            'pool_length_m', 'pool_width_m', 'slot_width_m',
            'discharge_m3s', 'water_depth_m', 'slot_velocity_ms',
            'volumetric_power_density_Wm3', 'vpd_acceptable',
            'total_head_loss_m', 'fishway_length_m'
        ]
        
        for key in required_keys:
            assert key in summary
    
    def test_optimize_design(self):
        """测试设计优化"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 10)
        dam_height = 3.0
        target_Q = 1.0
        
        result = fishway.optimize_design(target_Q, dam_height)
        
        # 检查优化结果
        assert 'optimization_result' in result
        assert 'vpd_constraint_met' in result['optimization_result']
        assert 'velocity_constraint_met' in result['optimization_result']


class TestStandardFishway:
    """测试标准鱼道创建"""
    
    def test_create_standard_fishway(self):
        """测试创建标准鱼道"""
        dam_height = 3.0
        fishway = create_standard_fishway(dam_height, target_discharge=1.0)
        
        # 检查基本参数
        assert fishway.pool_length == 3.0
        assert fishway.pool_width == 2.0
        assert fishway.slot_width == 0.3
        assert fishway.drop_per_pool == 0.2
        
        # 池室数量应该足够克服大坝高度
        total_drop = fishway.total_head_loss()
        assert total_drop >= dam_height
    
    def test_different_dam_heights(self):
        """测试不同坝高"""
        for dam_height in [1.0, 3.0, 5.0, 10.0]:
            fishway = create_standard_fishway(dam_height)
            total_drop = fishway.total_head_loss()
            assert total_drop >= dam_height


class TestEdgeCases:
    """测试边界条件"""
    
    def test_small_water_depth(self):
        """测试小水深"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        Q = fishway.slot_discharge(0.3)  # 最小水深
        assert Q > 0
    
    def test_large_discharge(self):
        """测试大流量"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 15)
        v = fishway.slot_velocity(10.0, 2.0)  # 大流量
        assert v > 0
    
    def test_zero_pools(self):
        """测试零池室"""
        fishway = VerticalSlotFishway(3.0, 2.0, 0.3, 0.2, 0)
        assert fishway.total_head_loss() == 0
        assert fishway.fishway_length() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
