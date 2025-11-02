"""
测试植物水力模型
===============
"""

import pytest
import numpy as np
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.channel import RiverReach
from code.models.vegetation import (
    VegetationType,
    VegetatedChannel,
    VegetationGrowthModel,
    create_reed,
    create_cattail,
    create_willow_shrub
)


class TestVegetationType:
    """测试VegetationType类"""
    
    def test_initialization(self):
        """测试初始化"""
        plant = VegetationType(
            name="Test Plant",
            height=1.5,
            stem_diameter=0.01,
            drag_coefficient=1.2,
            density=50,
            critical_velocity=2.0
        )
        
        assert plant.name == "Test Plant"
        assert plant.height == 1.5
        assert plant.stem_diameter == 0.01
        assert plant.drag_coefficient == 1.2
        assert plant.density == 50
        assert plant.critical_velocity == 2.0
    
    def test_frontal_area(self):
        """测试迎流面积计算"""
        plant = VegetationType("Test", 2.0, 0.01, 1.0, 100, 1.5)
        
        # a = n * d = 100 * 0.01 = 1.0 m⁻¹
        a = plant.frontal_area_per_volume()
        assert a == pytest.approx(1.0)


class TestVegetatedChannel:
    """测试VegetatedChannel类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.reach = RiverReach(
            length=500.0,
            width=20.0,
            slope=0.001,
            roughness=0.025,
            side_slope=2.0
        )
        
        self.plant = VegetationType(
            name="Test Plant",
            height=1.0,
            stem_diameter=0.01,
            drag_coefficient=1.2,
            density=50,
            critical_velocity=2.0
        )
    
    def test_initialization(self):
        """测试初始化"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        assert veg_channel.reach == self.reach
        assert veg_channel.vegetation == self.plant
        assert veg_channel.coverage == 0.5
    
    def test_invalid_coverage(self):
        """测试无效覆盖率"""
        with pytest.raises(ValueError):
            VegetatedChannel(self.reach, self.plant, 1.5)
        
        with pytest.raises(ValueError):
            VegetatedChannel(self.reach, self.plant, -0.1)
    
    def test_effective_roughness(self):
        """测试有效糙率"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        # 裸露河床糙率
        n_bare = self.reach.n
        
        # 有植被时糙率应该更大
        h = 0.8  # 水深
        n_eff = veg_channel.effective_roughness(h)
        assert n_eff > n_bare
    
    def test_roughness_with_submergence(self):
        """测试植物淹没时的糙率"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        # 植物未淹没
        h_low = 0.5
        n_low = veg_channel.effective_roughness(h_low)
        
        # 植物完全淹没
        h_high = 2.0
        n_high = veg_channel.effective_roughness(h_high)
        
        # 两者都应该大于裸露河床
        assert n_low > self.reach.n
        assert n_high > self.reach.n
    
    def test_drag_force(self):
        """测试阻力计算"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        h = 0.8
        v = 1.0
        
        F_d = veg_channel.drag_force(h, v)
        
        # 阻力应该为正
        assert F_d > 0
        
        # 流速增加，阻力应该增加（平方关系）
        v2 = 2.0
        F_d2 = veg_channel.drag_force(h, v2)
        assert F_d2 > F_d
        assert F_d2 / F_d == pytest.approx(4.0, rel=0.1)
    
    def test_velocity_reduction(self):
        """测试流速衰减"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        h = 0.8
        factor = veg_channel.velocity_reduction_factor(h)
        
        # 衰减因子应该在0-1之间
        assert 0 < factor < 1
    
    def test_velocity_with_vegetation(self):
        """测试含植被流速"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        h = 0.8
        
        # 裸露河床流速
        v_bare = self.reach.velocity_manning(h)
        
        # 含植被流速
        v_veg = veg_channel.velocity_manning_with_vegetation(h)
        
        # 含植被流速应该更小
        assert v_veg < v_bare
    
    def test_discharge_with_vegetation(self):
        """测试含植被流量"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        h = 0.8
        Q = veg_channel.discharge_with_vegetation(h)
        
        # 流量应该为正
        assert Q > 0
        
        # 应该小于裸露河床的流量
        Q_bare = self.reach.discharge_manning(h)
        assert Q < Q_bare
    
    def test_stability_check(self):
        """测试稳定性检查"""
        veg_channel = VegetatedChannel(self.reach, self.plant, 0.5)
        
        h = 0.8
        Q = 10.0
        
        stability = veg_channel.check_stability(h, Q)
        
        # 应该包含必要的键
        assert 'velocity' in stability
        assert 'critical_velocity' in stability
        assert 'safety_factor' in stability
        assert 'stability' in stability
        assert 'is_stable' in stability
        
        # 安全系数应该为正
        assert stability['safety_factor'] > 0
    
    def test_coverage_effect(self):
        """测试覆盖率的影响"""
        h = 0.8
        
        # 不同覆盖率
        coverages = [0.2, 0.5, 0.8]
        roughnesses = []
        
        for cov in coverages:
            veg_channel = VegetatedChannel(self.reach, self.plant, cov)
            n_eff = veg_channel.effective_roughness(h)
            roughnesses.append(n_eff)
        
        # 覆盖率越大，糙率应该越大
        assert roughnesses[1] > roughnesses[0]
        assert roughnesses[2] > roughnesses[1]


class TestVegetationGrowthModel:
    """测试VegetationGrowthModel类"""
    
    def setup_method(self):
        """设置测试用例"""
        self.reach = RiverReach(500, 20, 0.001, 0.025, 2.0)
        
        # 生成模拟流量序列
        np.random.seed(42)
        n_days = 365
        seasonal = 20 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365)
        noise = np.random.normal(0, 2, n_days)
        self.flow_series = np.maximum(seasonal + noise, 5)
        
        self.dates = np.arange(n_days)
    
    def test_submergence_duration(self):
        """测试淹水持续时间计算"""
        elevation = 0.8
        channel_bottom = 0.0
        
        result = VegetationGrowthModel.submergence_duration(
            self.flow_series,
            self.dates,
            elevation,
            channel_bottom,
            self.reach
        )
        
        # 检查返回的键
        assert 'total_days' in result
        assert 'submerged_days' in result
        assert 'submergence_ratio' in result
        assert 'max_consecutive_days' in result
        assert 'mean_submergence_depth' in result
        
        # 检查合理性
        assert result['total_days'] == 365
        assert 0 <= result['submerged_days'] <= 365
        assert 0 <= result['submergence_ratio'] <= 1
        assert result['max_consecutive_days'] >= 0
    
    def test_different_elevations(self):
        """测试不同高程的淹水差异"""
        channel_bottom = 0.0
        
        # 低高程应该淹水更多
        result_low = VegetationGrowthModel.submergence_duration(
            self.flow_series, self.dates, 0.5, channel_bottom, self.reach
        )
        
        # 高高程应该淹水更少
        result_high = VegetationGrowthModel.submergence_duration(
            self.flow_series, self.dates, 1.5, channel_bottom, self.reach
        )
        
        assert result_low['submergence_ratio'] > result_high['submergence_ratio']
    
    def test_growth_suitability(self):
        """测试生长适宜性评估"""
        plant = create_reed()
        
        # 理想条件
        suitability = VegetationGrowthModel.growth_suitability(
            submergence_ratio=0.5,
            mean_velocity=0.5,
            vegetation=plant
        )
        
        assert 'submergence_suitability' in suitability
        assert 'velocity_suitability' in suitability
        assert 'overall_suitability' in suitability
        assert 'grade' in suitability
        
        # 适宜性应该在0-1之间
        assert 0 <= suitability['overall_suitability'] <= 1
    
    def test_suitability_extremes(self):
        """测试极端条件的适宜性"""
        plant = create_reed()
        
        # 极端淹水
        suitability_flood = VegetationGrowthModel.growth_suitability(
            submergence_ratio=0.95,
            mean_velocity=0.5,
            vegetation=plant
        )
        
        # 极端干旱
        suitability_drought = VegetationGrowthModel.growth_suitability(
            submergence_ratio=0.05,
            mean_velocity=0.5,
            vegetation=plant
        )
        
        # 理想条件
        suitability_ideal = VegetationGrowthModel.growth_suitability(
            submergence_ratio=0.5,
            mean_velocity=0.5,
            vegetation=plant
        )
        
        # 理想条件应该更适宜
        assert suitability_ideal['overall_suitability'] > suitability_flood['overall_suitability']
        assert suitability_ideal['overall_suitability'] > suitability_drought['overall_suitability']


class TestPresetPlants:
    """测试预设植物类型"""
    
    def test_create_reed(self):
        """测试创建芦苇"""
        reed = create_reed()
        
        assert reed.name == "芦苇"
        assert reed.height > 0
        assert reed.stem_diameter > 0
        assert reed.density > 0
        assert reed.critical_velocity > 0
    
    def test_create_cattail(self):
        """测试创建香蒲"""
        cattail = create_cattail()
        
        assert cattail.name == "香蒲"
        assert cattail.height > 0
    
    def test_create_willow(self):
        """测试创建柳树灌木"""
        willow = create_willow_shrub()
        
        assert willow.name == "柳树灌木"
        assert willow.height > create_reed().height  # 柳树应该更高
    
    def test_plant_differences(self):
        """测试不同植物的差异"""
        reed = create_reed()
        cattail = create_cattail()
        willow = create_willow_shrub()
        
        # 它们应该有不同的特征
        assert reed.height != cattail.height or reed.density != cattail.density
        assert reed.critical_velocity != willow.critical_velocity or reed.height != willow.height


class TestIntegration:
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 创建河段
        reach = RiverReach(500, 20, 0.001, 0.025, 2.0)
        
        # 创建植物
        plant = create_reed()
        
        # 创建含植被河道
        veg_channel = VegetatedChannel(reach, plant, 0.5)
        
        # 计算流速
        Q = 20.0
        h = reach.solve_depth(Q)
        v = veg_channel.velocity_manning_with_vegetation(h)
        
        # 检查稳定性
        stability = veg_channel.check_stability(h, Q)
        
        # 所有计算都应该成功
        assert v > 0
        assert stability['is_stable'] in [True, False]
    
    def test_multiple_plants_comparison(self):
        """测试多种植物对比"""
        reach = RiverReach(500, 20, 0.001, 0.025, 2.0)
        Q = 20.0
        h = reach.solve_depth(Q)
        
        plants = [create_reed(), create_cattail(), create_willow_shrub()]
        velocities = []
        
        for plant in plants:
            veg_channel = VegetatedChannel(reach, plant, 0.5)
            v = veg_channel.velocity_manning_with_vegetation(h)
            velocities.append(v)
        
        # 所有流速都应该小于裸露河床
        v_bare = reach.velocity_manning(h)
        for v in velocities:
            assert v < v_bare


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
