"""
测试生态水力指标模型
===================
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.models.indicators import (
    IHACalculator,
    HydraulicDiversityIndex,
    HydrologicAlterationAssessment,
    generate_iha_report
)


class TestIHACalculator:
    """测试IHACalculator类"""
    
    def setup_method(self):
        """设置测试用例"""
        # 创建10年的模拟日流量数据
        np.random.seed(42)
        n_years = 10
        n_days = n_years * 365
        
        start_date = datetime(2000, 1, 1)
        self.dates = np.array([start_date + timedelta(days=i) for i in range(n_days)])
        
        # 生成具有季节性的流量数据
        flows = []
        for i in range(n_days):
            year_progress = (i % 365) / 365.0
            # 季节性模式
            seasonal = 50 + 30 * np.sin(2 * np.pi * year_progress)
            # 随机波动
            noise = np.random.normal(0, 5)
            flows.append(max(seasonal + noise, 5))
        
        self.daily_flow = np.array(flows)
        self.calculator = IHACalculator(self.daily_flow, self.dates)
    
    def test_initialization(self):
        """测试初始化"""
        assert len(self.calculator.daily_flow) == len(self.calculator.dates)
        assert len(self.calculator.df) > 0
        assert 'flow' in self.calculator.df.columns
        assert 'date' in self.calculator.df.columns
    
    def test_invalid_data(self):
        """测试无效数据"""
        with pytest.raises(ValueError):
            # 长度不匹配
            IHACalculator(self.daily_flow[:100], self.dates)
    
    def test_calculate_group1(self):
        """测试组1：月平均流量"""
        results = self.calculator.calculate_group1()
        
        # 应该有12个月的均值和CV
        assert len(results) == 24  # 12个均值 + 12个CV
        
        # 检查每个月都有结果
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month in months:
            assert f'{month}_mean' in results
            assert f'{month}_cv' in results
            assert results[f'{month}_mean'] > 0
            assert results[f'{month}_cv'] >= 0
    
    def test_calculate_group2(self):
        """测试组2：极端流量"""
        results = self.calculator.calculate_group2()
        
        # 应该包含最小和最大流量指标
        windows = [1, 3, 7, 30, 90]
        for window in windows:
            assert f'min_{window}day' in results
            assert f'max_{window}day' in results
            assert results[f'min_{window}day'] > 0
            assert results[f'max_{window}day'] > results[f'min_{window}day']
        
        # 基流指数
        assert 'base_flow_index' in results
        assert 0 <= results['base_flow_index'] <= 1
    
    def test_calculate_group3(self):
        """测试组3：极端流量时间"""
        results = self.calculator.calculate_group3()
        
        assert 'julian_min' in results
        assert 'julian_max' in results
        
        # 儒略日应该在1-365之间
        assert 1 <= results['julian_min'] <= 365
        assert 1 <= results['julian_max'] <= 365
    
    def test_calculate_group4(self):
        """测试组4：流量脉冲"""
        results = self.calculator.calculate_group4()
        
        assert 'high_pulse_count' in results
        assert 'low_pulse_count' in results
        assert 'high_pulse_duration' in results
        assert 'low_pulse_duration' in results
        
        # 脉冲次数和持续时间应该为正
        assert results['high_pulse_count'] >= 0
        assert results['low_pulse_count'] >= 0
        assert results['high_pulse_duration'] >= 0
        assert results['low_pulse_duration'] >= 0
    
    def test_calculate_group5(self):
        """测试组5：流量变化速率"""
        results = self.calculator.calculate_group5()
        
        assert 'rise_rate' in results
        assert 'fall_rate' in results
        assert 'reversals' in results
        
        # 变化速率应该为正
        assert results['rise_rate'] >= 0
        assert results['fall_rate'] >= 0
        assert results['reversals'] >= 0
    
    def test_calculate_all_indicators(self):
        """测试计算所有指标"""
        results = self.calculator.calculate_all_indicators()
        
        # 应该有33+个指标（含月度CV）
        assert len(results) >= 33
        
        # 所有值应该是数值
        for key, value in results.items():
            assert isinstance(value, (int, float, np.number))
            assert not np.isnan(value)
    
    def test_compare_periods(self):
        """测试建坝前后对比"""
        # 分成两个时期
        mid_date = datetime(2005, 1, 1)
        pre_dates = self.dates[self.dates < mid_date]
        post_dates = self.dates[self.dates >= mid_date]
        
        results = self.calculator.compare_periods(pre_dates, post_dates)
        
        assert 'pre' in results
        assert 'post' in results
        assert 'change' in results
        
        # 检查关键指标
        for key in ['Jan_mean', 'min_7day', 'max_7day']:
            assert key in results['pre']
            assert key in results['post']
            assert key in results['change']


class TestHydraulicDiversityIndex:
    """测试HydraulicDiversityIndex类"""
    
    def test_shannon_index(self):
        """测试Shannon指数"""
        # 均匀分布的数据应该有高Shannon指数
        uniform_data = np.random.uniform(0, 100, 1000)
        H_uniform = HydraulicDiversityIndex.shannon_index(uniform_data, bins=10)
        
        # Shannon指数应该为正
        assert H_uniform > 0
        
        # 单一值的数据应该有低Shannon指数
        constant_data = np.ones(1000) * 50
        H_constant = HydraulicDiversityIndex.shannon_index(constant_data, bins=10)
        
        # 均匀分布应该比单一值有更高的Shannon指数
        assert H_uniform > H_constant
    
    def test_simpson_index(self):
        """测试Simpson指数"""
        # 均匀分布
        uniform_data = np.random.uniform(0, 100, 1000)
        D_uniform = HydraulicDiversityIndex.simpson_index(uniform_data, bins=10)
        
        # Simpson指数应该在0-1之间
        assert 0 <= D_uniform <= 1
        
        # 单一值
        constant_data = np.ones(1000) * 50
        D_constant = HydraulicDiversityIndex.simpson_index(constant_data, bins=10)
        
        # 均匀分布应该有更高的Simpson指数
        assert D_uniform > D_constant
    
    def test_pielou_evenness(self):
        """测试Pielou均匀度"""
        # 均匀分布
        uniform_data = np.random.uniform(0, 100, 1000)
        J_uniform = HydraulicDiversityIndex.pielou_evenness(uniform_data, bins=10)
        
        # 均匀度应该在0-1之间
        assert 0 <= J_uniform <= 1
        
        # 单一值的数据
        constant_data = np.ones(1000) * 50
        J_constant = HydraulicDiversityIndex.pielou_evenness(constant_data, bins=10)
        
        # 均匀分布应该有更高的均匀度
        assert J_uniform > J_constant or J_constant == 0
    
    def test_different_bin_numbers(self):
        """测试不同的分组数"""
        data = np.random.uniform(0, 100, 1000)
        
        H_10 = HydraulicDiversityIndex.shannon_index(data, bins=10)
        H_20 = HydraulicDiversityIndex.shannon_index(data, bins=20)
        
        # 两者都应该为正
        assert H_10 > 0
        assert H_20 > 0


class TestHydrologicAlterationAssessment:
    """测试HydrologicAlterationAssessment类"""
    
    def test_calculate_alteration_degree(self):
        """测试改变度计算"""
        pre = {'flow1': 100, 'flow2': 50, 'flow3': 25}
        post = {'flow1': 150, 'flow2': 40, 'flow3': 30}
        
        alteration = HydrologicAlterationAssessment.calculate_alteration_degree(pre, post)
        
        # 应该返回改变度字典
        assert len(alteration) == 3
        
        # 检查计算正确性
        assert alteration['flow1'] == pytest.approx(50.0)  # |150-100|/100 * 100
        assert alteration['flow2'] == pytest.approx(20.0)  # |40-50|/50 * 100
        assert alteration['flow3'] == pytest.approx(20.0)  # |30-25|/25 * 100
    
    def test_zero_value_handling(self):
        """测试零值处理"""
        pre = {'flow1': 0, 'flow2': 50}
        post = {'flow1': 10, 'flow2': 60}
        
        alteration = HydrologicAlterationAssessment.calculate_alteration_degree(pre, post)
        
        # 零值的改变度应该为0
        assert alteration['flow1'] == 0
        assert alteration['flow2'] == pytest.approx(20.0)
    
    def test_overall_alteration_index(self):
        """测试总体改变指数"""
        alteration = {
            'ind1': 10, 'ind2': 20, 'ind3': 30,
            'ind4': 40, 'ind5': 50
        }
        
        overall = HydrologicAlterationAssessment.overall_alteration_index(alteration)
        
        assert 'mean_alteration' in overall
        assert 'median_alteration' in overall
        assert 'max_alteration' in overall
        assert 'grade' in overall
        
        # 检查计算
        assert overall['mean_alteration'] == pytest.approx(30.0)
        assert overall['median_alteration'] == pytest.approx(30.0)
        assert overall['max_alteration'] == pytest.approx(50.0)
    
    def test_alteration_grades(self):
        """测试改变等级分类"""
        # 轻度改变
        alt_light = {'ind': 10}
        overall_light = HydrologicAlterationAssessment.overall_alteration_index(alt_light)
        assert overall_light['grade'] == "轻度改变"
        
        # 中度改变
        alt_moderate = {'ind': 30}
        overall_moderate = HydrologicAlterationAssessment.overall_alteration_index(alt_moderate)
        assert overall_moderate['grade'] == "中度改变"
        
        # 较大改变
        alt_high = {'ind': 50}
        overall_high = HydrologicAlterationAssessment.overall_alteration_index(alt_high)
        assert overall_high['grade'] == "较大改变"
        
        # 严重改变
        alt_severe = {'ind': 70}
        overall_severe = HydrologicAlterationAssessment.overall_alteration_index(alt_severe)
        assert overall_severe['grade'] == "严重改变"


class TestReportGeneration:
    """测试报告生成"""
    
    def test_generate_iha_report(self):
        """测试IHA报告生成"""
        # 模拟结果数据
        results = {
            'pre': {
                'Jan_mean': 100, 'Feb_mean': 90, 'Mar_mean': 80,
                'Apr_mean': 70, 'May_mean': 60, 'Jun_mean': 50,
                'Jul_mean': 40, 'Aug_mean': 50, 'Sep_mean': 60,
                'Oct_mean': 70, 'Nov_mean': 80, 'Dec_mean': 90,
                'min_1day': 20, 'min_7day': 25, 'min_30day': 30,
                'max_1day': 200, 'max_7day': 180, 'max_30day': 150,
                'julian_min': 180, 'julian_max': 90,
                'high_pulse_count': 10, 'low_pulse_count': 8,
                'rise_rate': 5.0, 'fall_rate': 4.5
            },
            'post': {
                'Jan_mean': 110, 'Feb_mean': 95, 'Mar_mean': 85,
                'Apr_mean': 75, 'May_mean': 65, 'Jun_mean': 55,
                'Jul_mean': 45, 'Aug_mean': 55, 'Sep_mean': 65,
                'Oct_mean': 75, 'Nov_mean': 85, 'Dec_mean': 95,
                'min_1day': 25, 'min_7day': 30, 'min_30day': 35,
                'max_1day': 180, 'max_7day': 160, 'max_30day': 140,
                'julian_min': 190, 'julian_max': 85,
                'high_pulse_count': 8, 'low_pulse_count': 6,
                'rise_rate': 4.0, 'fall_rate': 3.5
            },
            'change': {
                'Jan_mean': 10, 'Feb_mean': 5.6, 'Mar_mean': 6.3,
                'Apr_mean': 7.1, 'May_mean': 8.3, 'Jun_mean': 10.0,
                'Jul_mean': 12.5, 'Aug_mean': 10.0, 'Sep_mean': 8.3,
                'Oct_mean': 7.1, 'Nov_mean': 6.3, 'Dec_mean': 5.6,
                'min_1day': 25, 'min_7day': 20, 'min_30day': 16.7,
                'max_1day': -10, 'max_7day': -11.1, 'max_30day': -6.7,
                'julian_min': 10, 'julian_max': -5,
                'high_pulse_count': -20, 'low_pulse_count': -25,
                'rise_rate': -20, 'fall_rate': -22.2
            }
        }
        
        report = generate_iha_report(results)
        
        # 报告应该是字符串
        assert isinstance(report, str)
        
        # 报告应该包含关键信息
        assert '水文改变指标' in report
        assert '月平均流量' in report
        assert '极端流量' in report
        
        # 报告应该包含数值
        assert '100' in report or '110' in report


class TestEdgeCases:
    """测试边界情况"""
    
    def test_short_time_series(self):
        """测试短时间序列"""
        # 1年数据
        dates = np.array([datetime(2000, 1, 1) + timedelta(days=i) for i in range(365)])
        flow = np.random.uniform(20, 100, 365)
        
        calculator = IHACalculator(flow, dates)
        results = calculator.calculate_all_indicators()
        
        # 应该仍能计算指标
        assert len(results) > 0
    
    def test_constant_flow(self):
        """测试恒定流量"""
        dates = np.array([datetime(2000, 1, 1) + timedelta(days=i) for i in range(365)])
        flow = np.ones(365) * 50
        
        calculator = IHACalculator(flow, dates)
        results = calculator.calculate_all_indicators()
        
        # 恒定流量的CV应该为0或很小
        assert results['Jan_cv'] == pytest.approx(0, abs=1e-6)
        
        # Shannon指数应该很低
        H = HydraulicDiversityIndex.shannon_index(flow, bins=10)
        assert H == pytest.approx(0, abs=1e-1)
    
    def test_extreme_values(self):
        """测试极端值"""
        dates = np.array([datetime(2000, 1, 1) + timedelta(days=i) for i in range(365)])
        # 包含极端值的流量
        flow = np.concatenate([
            np.ones(180) * 10,    # 低流量
            np.ones(180) * 1000,  # 高流量
            [10, 1000, 10, 1000, 10]
        ])
        
        calculator = IHACalculator(flow, dates)
        results = calculator.calculate_all_indicators()
        
        # 应该能够处理极端值
        assert results['min_1day'] == pytest.approx(10)
        assert results['max_1day'] >= 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
