"""测试生态护岸模型"""

import pytest
import numpy as np
from code.models.ecological_revetment import (
    EcologicalRevetment,
    VegetatedRevetment,
    RevetmentStability,
    design_ecological_revetment
)


class TestEcologicalRevetment:
    """测试生态护岸基础类"""
    
    def test_initialization(self):
        """测试初始化"""
        rev = EcologicalRevetment('石笼', 1.0, 0.5, 0.4)
        assert rev.type == '石笼'
        assert rev.height == 1.0
        assert rev.porosity == 0.4
    
    def test_roughness_coefficient(self):
        """测试粗糙系数"""
        rev1 = EcologicalRevetment('植被护坡', 1.0, 0.5)
        rev2 = EcologicalRevetment('混凝土', 1.0, 0.5)
        
        n1 = rev1.roughness_coefficient()
        n2 = rev2.roughness_coefficient()
        
        # 植被护坡糙率应大于混凝土
        assert n1 > n2
        assert n1 > 0.05
        assert n2 < 0.02
    
    def test_velocity_reduction(self):
        """测试流速削减"""
        rev = EcologicalRevetment('生态袋', 1.0, 0.5, 0.4)
        reduction = rev.velocity_reduction_factor()
        
        assert 0 < reduction < 1
    
    def test_shelter_area(self):
        """测试庇护所面积"""
        rev = EcologicalRevetment('石笼', 1.0, 0.5, 0.4)
        ratio = rev.shelter_area_ratio(30.0)
        
        assert 0 < ratio < 0.3


class TestVegetatedRevetment:
    """测试植被护岸"""
    
    def test_initialization(self):
        """测试初始化"""
        veg = VegetatedRevetment(0.5, 0.7, 0.005, 1000.0)
        assert veg.height == 0.5
        assert veg.coverage == 0.7
    
    def test_vegetation_drag(self):
        """测试植被阻力系数"""
        veg = VegetatedRevetment(0.5, 0.7)
        Cd = veg.vegetation_drag_coefficient()
        
        assert Cd > 2.0  # 植被增加阻力
    
    def test_effective_roughness(self):
        """测试有效糙率"""
        veg = VegetatedRevetment(0.5, 0.7)
        
        # 非淹没情况
        n1 = veg.effective_roughness(0.4, 0.8)
        
        # 淹没情况
        n2 = veg.effective_roughness(1.0, 0.8)
        
        # 非淹没糙率应大于淹没
        assert n1 > n2
        assert n1 > 0.05
    
    def test_root_reinforcement(self):
        """测试根系加固"""
        veg = VegetatedRevetment(0.5, 0.7)
        cohesion_original = 10.0
        cohesion_enhanced = veg.root_reinforcement(cohesion_original)
        
        # 根系应增加粘聚力
        assert cohesion_enhanced > cohesion_original


class TestRevetmentStability:
    """测试护岸稳定性"""
    
    def test_shear_stress(self):
        """测试剪应力计算"""
        rev = EcologicalRevetment('石笼', 1.0, 0.5, 0.4)
        stab = RevetmentStability(rev, 35.0, 2.0, 1.2)
        
        tau = stab.shear_stress()
        
        assert tau > 0
        assert tau < 1000  # 合理范围（Pa）
    
    def test_critical_velocity(self):
        """测试临界流速"""
        rev = EcologicalRevetment('石笼', 1.0, 0.5, 0.4)
        stab = RevetmentStability(rev, 35.0, 2.0, 1.2)
        
        v_c = stab.critical_velocity(0.02)
        
        assert v_c > 0
        assert v_c < 5.0
    
    def test_stability_factor(self):
        """测试安全系数"""
        rev = EcologicalRevetment('石笼', 1.0, 0.5, 0.4)
        stab = RevetmentStability(rev, 35.0, 2.0, 1.2)
        
        SF = stab.stability_factor(0.02)
        
        assert SF > 0
    
    def test_slope_stability_assessment(self):
        """测试综合评价"""
        rev = EcologicalRevetment('植被护坡', 1.0, 0.5, 0.4)
        stab = RevetmentStability(rev, 35.0, 2.0, 1.2)
        
        result = stab.slope_stability_assessment()
        
        assert 'shear_stress' in result
        assert 'safety_factor' in result
        assert 'stability' in result
        assert result['stability'] in ['安全', '基本安全', '不安全']


class TestDesignFunction:
    """测试设计函数"""
    
    def test_design_vegetated_revetment(self):
        """测试植被护岸设计"""
        result = design_ecological_revetment(30.0, 2.0, 1.2, 35.0, '植被护坡')
        
        assert 'roughness' in result
        assert 'velocity_reduction' in result
        assert 'shelter_area_per_100m' in result
        assert 'stability' in result
        assert 'root_reinforcement' in result
    
    def test_design_gabion_revetment(self):
        """测试石笼护岸设计"""
        result = design_ecological_revetment(30.0, 2.0, 1.2, 35.0, '石笼')
        
        assert result['revetment_type'] == '石笼'
        assert result['stability']['safety_factor'] > 0
    
    def test_compare_revetment_types(self):
        """测试不同护岸类型对比"""
        types = ['植被护坡', '石笼', '生态袋']
        results = []
        
        for rev_type in types:
            result = design_ecological_revetment(30.0, 2.0, 1.2, 35.0, rev_type)
            results.append(result)
        
        # 检查所有结果都有效
        for result in results:
            assert result['shelter_ratio'] > 0
            assert result['stability']['safety_factor'] > 0
