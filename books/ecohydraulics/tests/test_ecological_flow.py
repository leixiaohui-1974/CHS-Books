"""
测试生态流量计算
===============
"""

import pytest
import numpy as np
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.channel import River, RiverReach
from code.models.ecological_flow import EcologicalFlowCalculator


class TestEcologicalFlowCalculator:
    """测试EcologicalFlowCalculator类"""
    
    def setup_method(self):
        """设置测试用例"""
        # 创建河流
        self.river = River(name="Test River", mean_annual_flow=15.0)
        
        # 添加河段
        reach = RiverReach(
            length=2000.0,
            width=20.0,
            slope=0.001,
            roughness=0.035,
            side_slope=2.0
        )
        self.river.add_reach(reach)
        
        # 创建计算器
        self.calculator = EcologicalFlowCalculator(self.river)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.calculator.river == self.river
    
    def test_tennant_method(self):
        """测试Tennant法"""
        results = self.calculator.tennant_method(season='annual')
        
        # 检查所有必要的键
        required_keys = ['excellent_lower', 'excellent_upper', 
                        'good_lower', 'good_upper',
                        'fair_lower', 'fair_upper',
                        'poor_lower', 'poor_upper',
                        'minimum', 'recommended']
        for key in required_keys:
            assert key in results
        
        # 检查值的合理性
        Q_maf = self.river.Q_maf
        assert results['minimum'] == pytest.approx(0.1 * Q_maf)
        assert results['recommended'] == pytest.approx(0.3 * Q_maf)
        assert results['excellent_lower'] == pytest.approx(0.6 * Q_maf)
        
        # 检查等级之间的大小关系
        assert results['minimum'] <= results['poor_lower']
        assert results['poor_upper'] == pytest.approx(results['fair_lower'])
        assert results['fair_upper'] == pytest.approx(results['good_lower'])
        assert results['good_upper'] == pytest.approx(results['excellent_lower'])
    
    def test_tennant_method_seasonal(self):
        """测试Tennant法的季节调整"""
        annual = self.calculator.tennant_method(season='annual')
        spawning = self.calculator.tennant_method(season='spawning')
        winter = self.calculator.tennant_method(season='winter')
        
        # 产卵期流量应该更大
        assert spawning['recommended'] > annual['recommended']
        
        # 冬季流量可以更小
        assert winter['recommended'] < annual['recommended']
    
    def test_wetted_perimeter_method(self):
        """测试湿周法"""
        results = self.calculator.wetted_perimeter_method(
            flow_range=(0.5, 15.0),
            n_points=50
        )
        
        # 检查所有必要的键
        required_keys = ['ecological_flow', 'wetted_perimeter', 'wp_ratio',
                        'flow_data', 'wp_data', 'dP_dQ', 'd2P_dQ2']
        for key in required_keys:
            assert key in results
        
        # 生态流量应该在范围内
        Q_eco = results['ecological_flow']
        assert 0.5 <= Q_eco <= 15.0
        
        # 湿周应该为正值
        assert results['wetted_perimeter'] > 0
        
        # 湿周比例应该在0-1之间
        assert 0 < results['wp_ratio'] < 1
        
        # 检查数据数组长度
        assert len(results['flow_data']) == 50
        assert len(results['wp_data']) == 50
        
        # 检查湿周单调性（流量增加，湿周应该增加）
        wp_data = results['wp_data']
        assert np.all(np.diff(wp_data) >= 0)  # 单调非递减
    
    def test_r2cross_method(self):
        """测试R2-Cross法"""
        results = self.calculator.r2cross_method(
            flow_range=(0.5, 15.0),
            n_points=50
        )
        
        # 检查所有必要的键
        required_keys = ['ecological_flow', 'depth', 'depth_ratio',
                        'flow_data', 'depth_data', 'target_depth', 'max_depth']
        for key in required_keys:
            assert key in results
        
        # 生态流量应该在范围内
        Q_eco = results['ecological_flow']
        assert 0.5 <= Q_eco <= 15.0
        
        # 水深应该为正值
        assert results['depth'] > 0
        assert results['max_depth'] > 0
        
        # 水深比例应该接近0.25（设计值）
        assert 0.2 < results['depth_ratio'] < 0.3
        
        # 目标水深应该约等于最大水深的25%
        assert results['target_depth'] == pytest.approx(0.25 * results['max_depth'])
        
        # 检查数据数组长度
        assert len(results['flow_data']) == 50
        assert len(results['depth_data']) == 50
        
        # 检查水深单调性（流量增加，水深应该增加）
        depth_data = results['depth_data']
        assert np.all(np.diff(depth_data) > 0)  # 严格单调递增
    
    def test_q7_10_method(self):
        """测试7Q10法"""
        # 创建模拟的年最小流量序列（15年）
        np.random.seed(42)
        annual_min_flows = np.random.lognormal(mean=1.0, sigma=0.5, size=15)
        
        q7_10 = self.calculator.q7_10_method(annual_min_flows)
        
        # 7Q10应该为正值
        assert q7_10 > 0
        
        # 7Q10应该接近序列的最小值（10%保证率）
        assert q7_10 <= np.min(annual_min_flows) * 2  # 不会太大
        assert q7_10 >= np.min(annual_min_flows) * 0.1  # 不会太小
    
    def test_q7_10_method_insufficient_data(self):
        """测试7Q10法数据不足的情况"""
        # 少于10年的数据应该抛出错误
        annual_min_flows = [1.0, 2.0, 3.0]
        
        with pytest.raises(ValueError):
            self.calculator.q7_10_method(annual_min_flows)
    
    def test_comprehensive_assessment(self):
        """测试综合评估"""
        results = self.calculator.comprehensive_assessment(
            flow_range=(0.5, 15.0),
            season='annual'
        )
        
        # 检查所有方法的结果都存在
        assert 'tennant' in results
        assert 'wetted_perimeter' in results
        assert 'r2cross' in results
        assert 'all_recommendations' in results
        assert 'final_recommended' in results
        
        # 检查推荐值
        assert results['tennant_recommended'] > 0
        assert results['wp_recommended'] > 0
        assert results['r2cross_recommended'] > 0
        assert results['final_recommended'] > 0
        
        # 最终推荐值应该是中位数
        recommendations = results['all_recommendations']
        assert results['final_recommended'] == pytest.approx(np.median(recommendations))
        
        # 推荐范围应该合理
        min_rec, max_rec = results['recommendation_range']
        assert min_rec <= results['final_recommended'] <= max_rec
        
        # 百分比应该在合理范围内
        pct = results['percentage_of_maf']
        assert 0 < pct < 100
    
    def test_comprehensive_assessment_with_q7_10(self):
        """测试包含7Q10的综合评估"""
        # 创建年最小流量序列
        np.random.seed(42)
        annual_min_flows = np.random.lognormal(mean=1.0, sigma=0.5, size=15)
        
        results = self.calculator.comprehensive_assessment(
            flow_range=(0.5, 15.0),
            season='annual',
            annual_min_flows=annual_min_flows
        )
        
        # 应该包含7Q10结果
        assert 'q7_10' in results
        assert results['q7_10'] > 0
        
        # 推荐值列表应该包含4个方法
        assert len(results['all_recommendations']) == 4
    
    def test_generate_report(self):
        """测试报告生成"""
        results = self.calculator.comprehensive_assessment(
            flow_range=(0.5, 15.0),
            season='annual'
        )
        
        report = self.calculator.generate_report(results)
        
        # 报告应该是字符串
        assert isinstance(report, str)
        
        # 报告应该包含关键信息
        assert "生态流量计算综合评估报告" in report
        assert self.river.name in report
        assert "Tennant法" in report
        assert "湿周法" in report
        assert "R2-Cross法" in report
        assert "综合推荐结果" in report
        
        # 报告应该包含数值
        assert f"{self.river.Q_maf:.2f}" in report


class TestMethodConsistency:
    """测试方法之间的一致性"""
    
    def setup_method(self):
        """设置测试用例"""
        self.river = River(name="Consistency Test River", mean_annual_flow=20.0)
        reach = RiverReach(2000, 25, 0.0008, 0.03, 2.0)
        self.river.add_reach(reach)
        self.calculator = EcologicalFlowCalculator(self.river)
    
    def test_methods_give_similar_results(self):
        """测试不同方法给出的结果在合理范围内"""
        results = self.calculator.comprehensive_assessment()
        
        tennant = results['tennant_recommended']
        wp = results['wp_recommended']
        r2cross = results['r2cross_recommended']
        
        # 所有方法的结果都应该在MAF的5%-50%之间
        Q_maf = self.river.Q_maf
        for Q in [tennant, wp, r2cross]:
            assert 0.05 * Q_maf < Q < 0.5 * Q_maf
        
        # 不同方法的结果不应该相差太大（最大/最小 < 5）
        recommendations = [tennant, wp, r2cross]
        ratio = max(recommendations) / min(recommendations)
        assert ratio < 5.0  # 相差不超过5倍（放宽限制，因为方法原理不同）


class TestRobustness:
    """测试鲁棒性"""
    
    def test_small_river(self):
        """测试小河流"""
        river = River(name="Small River", mean_annual_flow=1.0)
        reach = RiverReach(500, 3, 0.005, 0.04, 2.0)
        river.add_reach(reach)
        
        calculator = EcologicalFlowCalculator(river)
        results = calculator.comprehensive_assessment(flow_range=(0.05, 1.0))
        
        # 应该能够正常计算
        assert results['final_recommended'] > 0
        assert results['final_recommended'] < river.Q_maf
    
    def test_large_river(self):
        """测试大河流"""
        river = River(name="Large River", mean_annual_flow=1000.0)
        reach = RiverReach(10000, 200, 0.0002, 0.025, 3.0)
        river.add_reach(reach)
        
        calculator = EcologicalFlowCalculator(river)
        results = calculator.comprehensive_assessment(flow_range=(50, 1000))
        
        # 应该能够正常计算
        assert results['final_recommended'] > 0
        assert results['final_recommended'] < river.Q_maf


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
