"""测试案例16-18模型"""

import pytest
import numpy as np
from code.models.sediment_gravel import (
    GravelSupplementDesign,
    EstuaryHydraulics,
    RestorationAssessment
)


class TestGravelSupplement:
    """测试卵石补充模型"""
    
    def test_critical_velocity(self):
        """测试起动流速"""
        design = GravelSupplementDesign(25.0)
        v_c = design.critical_velocity(25.0)
        assert v_c > 0
        assert v_c < 2.0
    
    def test_size_distribution(self):
        """测试粒径配比"""
        design = GravelSupplementDesign(25.0)
        dist = design.gravel_size_distribution()
        assert dist['d50'] == 25.0
        assert dist['d16'] < dist['d50'] < dist['d84']
    
    def test_stability_assessment(self):
        """测试稳定性评估"""
        design = GravelSupplementDesign(25.0)
        result = design.stability_assessment(0.8, 2.0, 0.001)
        assert 'stability_status' in result
        assert result['safety_factor'] > 0


class TestEstuaryHydraulics:
    """测试河口水力学"""
    
    def test_tidal_water_level(self):
        """测试潮汐水位"""
        estuary = EstuaryHydraulics(3.0)
        wl = estuary.tidal_water_level(0)
        assert -2 <= wl <= 2
    
    def test_saltwater_intrusion(self):
        """测试盐水楔"""
        estuary = EstuaryHydraulics(3.0)
        L1 = estuary.saltwater_intrusion(100)
        L2 = estuary.saltwater_intrusion(500)
        assert L2 < L1  # 流量大，侵入短
    
    def test_ecological_flow(self):
        """测试生态需水"""
        estuary = EstuaryHydraulics(3.0)
        Q_eco = estuary.ecological_water_requirement()
        assert Q_eco > 0


class TestRestorationAssessment:
    """测试修复评估"""
    
    def test_diversity_change(self):
        """测试多样性变化"""
        assessment = RestorationAssessment()
        before = np.array([0.7, 0.2, 0.1])
        after = np.array([0.4, 0.4, 0.2])
        result = assessment.hydraulic_diversity_change(before, after)
        assert result['shannon_after'] > result['shannon_before']
    
    def test_habitat_quality(self):
        """测试栖息地质量"""
        assessment = RestorationAssessment()
        score = assessment.habitat_quality_score(0.5, 1.0, '砾石')
        assert 0 <= score <= 1
    
    def test_comprehensive_evaluation(self):
        """测试综合评价"""
        assessment = RestorationAssessment()
        result = assessment.comprehensive_evaluation(20, 30, 25)
        assert 'overall_score' in result
        assert 'grade' in result
