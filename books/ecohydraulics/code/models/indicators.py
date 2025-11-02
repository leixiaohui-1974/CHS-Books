"""
生态水力指标模型
===============

实现水文改变指标（IHA）和水力多样性指数计算
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from scipy import stats


class IHACalculator:
    """
    水文改变指标（IHA）计算器
    
    实现The Nature Conservancy开发的IHA方法，包含33个水文变化指标
    
    Parameters
    ----------
    daily_flow : array-like
        日流量序列 (m³/s)
    dates : array-like
        日期序列 (datetime objects)
    """
    
    def __init__(self, daily_flow: np.ndarray, dates: np.ndarray):
        self.daily_flow = np.array(daily_flow)
        self.dates = pd.to_datetime(dates)
        
        # 验证数据
        if len(self.daily_flow) != len(self.dates):
            raise ValueError("流量和日期数组长度不匹配")
        
        # 创建DataFrame便于处理
        self.df = pd.DataFrame({
            'date': self.dates,
            'flow': self.daily_flow
        })
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        self.df['doy'] = self.df['date'].dt.dayofyear  # day of year
    
    def calculate_group1(self) -> Dict[str, float]:
        """
        组1：每月平均流量（12个指标）
        
        Returns
        -------
        dict
            12个月的平均流量及其变异系数
        """
        results = {}
        
        for month in range(1, 13):
            month_data = self.df[self.df['month'] == month]['flow']
            
            # 计算各年同月的平均值
            monthly_means = self.df[self.df['month'] == month].groupby('year')['flow'].mean()
            
            mean_val = monthly_means.mean()
            std_val = monthly_means.std()
            # 避免除零和NaN
            cv = std_val / mean_val if (mean_val > 0 and std_val > 0 and not np.isnan(std_val)) else 0
            
            month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
            
            results[f'{month_name}_mean'] = mean_val
            results[f'{month_name}_cv'] = cv
        
        return results
    
    def calculate_group2(self) -> Dict[str, float]:
        """
        组2：极端流量的量级和持续时间（12个指标）
        
        包括：
        - 年最小1日、3日、7日、30日、90日平均流量
        - 年最大1日、3日、7日、30日、90日平均流量
        - 基流指数
        - 洪峰流量持续时间
        
        Returns
        -------
        dict
            极端流量指标
        """
        results = {}
        
        # 滑动窗口平均
        windows = [1, 3, 7, 30, 90]
        
        yearly_mins = []
        yearly_maxs = []
        
        for year in self.df['year'].unique():
            year_data = self.df[self.df['year'] == year]['flow'].values
            
            year_min_vals = []
            year_max_vals = []
            
            for window in windows:
                if len(year_data) >= window:
                    # 滑动窗口平均
                    moving_avg = pd.Series(year_data).rolling(window=window).mean()
                    year_min_vals.append(moving_avg.min())
                    year_max_vals.append(moving_avg.max())
                else:
                    year_min_vals.append(np.nan)
                    year_max_vals.append(np.nan)
            
            yearly_mins.append(year_min_vals)
            yearly_maxs.append(year_max_vals)
        
        # 计算多年平均
        yearly_mins = np.array(yearly_mins)
        yearly_maxs = np.array(yearly_maxs)
        
        for i, window in enumerate(windows):
            results[f'min_{window}day'] = np.nanmean(yearly_mins[:, i])
            results[f'max_{window}day'] = np.nanmean(yearly_maxs[:, i])
        
        # 基流指数（7日最小流量/年平均流量）
        annual_mean = self.df.groupby('year')['flow'].mean().mean()
        results['base_flow_index'] = results['min_7day'] / annual_mean if annual_mean > 0 else 0
        
        # 零流量天数（如果有）
        results['zero_flow_days'] = (self.daily_flow == 0).sum() / len(self.df['year'].unique())
        
        return results
    
    def calculate_group3(self) -> Dict[str, float]:
        """
        组3：极端流量的发生时间（2个指标）
        
        - 年最小流量发生的儒略日
        - 年最大流量发生的儒略日
        
        Returns
        -------
        dict
            极端流量时间指标
        """
        results = {}
        
        min_days = []
        max_days = []
        
        for year in self.df['year'].unique():
            year_data = self.df[self.df['year'] == year]
            
            min_idx = year_data['flow'].idxmin()
            max_idx = year_data['flow'].idxmax()
            
            min_days.append(year_data.loc[min_idx, 'doy'])
            max_days.append(year_data.loc[max_idx, 'doy'])
        
        results['julian_min'] = np.mean(min_days)
        results['julian_max'] = np.mean(max_days)
        
        return results
    
    def calculate_group4(self) -> Dict[str, float]:
        """
        组4：流量变化的频率和持续时间（4个指标）
        
        - 高脉冲次数（高于75分位数）
        - 低脉冲次数（低于25分位数）
        - 高脉冲持续时间
        - 低脉冲持续时间
        
        Returns
        -------
        dict
            流量脉冲指标
        """
        results = {}
        
        # 计算阈值
        q75 = np.percentile(self.daily_flow, 75)
        q25 = np.percentile(self.daily_flow, 25)
        
        # 识别高脉冲和低脉冲
        high_pulse = self.daily_flow > q75
        low_pulse = self.daily_flow < q25
        
        # 计算脉冲次数和持续时间
        high_pulse_count, high_pulse_duration = self._count_pulses(high_pulse)
        low_pulse_count, low_pulse_duration = self._count_pulses(low_pulse)
        
        n_years = len(self.df['year'].unique())
        
        results['high_pulse_count'] = high_pulse_count / n_years
        results['low_pulse_count'] = low_pulse_count / n_years
        results['high_pulse_duration'] = high_pulse_duration
        results['low_pulse_duration'] = low_pulse_duration
        
        return results
    
    def calculate_group5(self) -> Dict[str, float]:
        """
        组5：流量变化的速率（3个指标）
        
        - 平均涨水速率
        - 平均落水速率
        - 流量反转次数
        
        Returns
        -------
        dict
            流量变化速率指标
        """
        results = {}
        
        # 计算日流量变化
        flow_change = np.diff(self.daily_flow)
        
        # 涨水和落水
        rising = flow_change[flow_change > 0]
        falling = flow_change[flow_change < 0]
        
        results['rise_rate'] = np.mean(rising) if len(rising) > 0 else 0
        results['fall_rate'] = abs(np.mean(falling)) if len(falling) > 0 else 0
        
        # 流量反转次数（流量变化方向改变的次数）
        reversals = np.sum(np.diff(np.sign(flow_change)) != 0)
        results['reversals'] = reversals / len(self.df['year'].unique())
        
        return results
    
    def _count_pulses(self, pulse_mask: np.ndarray) -> Tuple[int, float]:
        """
        计算脉冲次数和平均持续时间
        
        Parameters
        ----------
        pulse_mask : array
            脉冲标识（True/False数组）
            
        Returns
        -------
        count : int
            脉冲次数
        duration : float
            平均持续时间（天）
        """
        # 查找连续True的区段
        pulse_diff = np.diff(np.concatenate(([False], pulse_mask, [False])).astype(int))
        starts = np.where(pulse_diff == 1)[0]
        ends = np.where(pulse_diff == -1)[0]
        
        count = len(starts)
        
        if count > 0:
            durations = ends - starts
            duration = np.mean(durations)
        else:
            duration = 0
        
        return count, duration
    
    def calculate_all_indicators(self) -> Dict[str, float]:
        """
        计算所有33个IHA指标
        
        Returns
        -------
        dict
            所有IHA指标
        """
        results = {}
        
        results.update(self.calculate_group1())
        results.update(self.calculate_group2())
        results.update(self.calculate_group3())
        results.update(self.calculate_group4())
        results.update(self.calculate_group5())
        
        return results
    
    def compare_periods(self, pre_dates: np.ndarray, post_dates: np.ndarray) -> Dict[str, Dict]:
        """
        比较建坝前后的IHA指标变化
        
        Parameters
        ----------
        pre_dates : array
            建坝前的日期范围
        post_dates : array
            建坝后的日期范围
            
        Returns
        -------
        dict
            包含pre（建坝前）、post（建坝后）、change（变化）的指标
        """
        # 建坝前数据
        pre_mask = (self.dates >= pre_dates[0]) & (self.dates <= pre_dates[-1])
        pre_calculator = IHACalculator(
            self.daily_flow[pre_mask],
            self.dates[pre_mask]
        )
        pre_indicators = pre_calculator.calculate_all_indicators()
        
        # 建坝后数据
        post_mask = (self.dates >= post_dates[0]) & (self.dates <= post_dates[-1])
        post_calculator = IHACalculator(
            self.daily_flow[post_mask],
            self.dates[post_mask]
        )
        post_indicators = post_calculator.calculate_all_indicators()
        
        # 计算变化
        change = {}
        for key in pre_indicators.keys():
            if pre_indicators[key] != 0:
                change[key] = (post_indicators[key] - pre_indicators[key]) / pre_indicators[key] * 100
            else:
                change[key] = 0
        
        return {
            'pre': pre_indicators,
            'post': post_indicators,
            'change': change
        }


class HydraulicDiversityIndex:
    """
    水力多样性指数计算
    
    用于评估河流生境的多样性
    """
    
    @staticmethod
    def shannon_index(values: np.ndarray, bins: int = 10) -> float:
        """
        Shannon多样性指数
        
        H' = -Σ(p_i * ln(p_i))
        
        Parameters
        ----------
        values : array
            水力参数值（如水深、流速等）
        bins : int
            分组数
            
        Returns
        -------
        float
            Shannon指数
        """
        # 将数据分组
        hist, _ = np.histogram(values, bins=bins)
        
        # 计算比例
        proportions = hist / np.sum(hist)
        
        # 移除零值
        proportions = proportions[proportions > 0]
        
        # 计算Shannon指数
        H = -np.sum(proportions * np.log(proportions))
        
        return H
    
    @staticmethod
    def simpson_index(values: np.ndarray, bins: int = 10) -> float:
        """
        Simpson多样性指数
        
        D = 1 - Σ(p_i²)
        
        Parameters
        ----------
        values : array
            水力参数值
        bins : int
            分组数
            
        Returns
        -------
        float
            Simpson指数
        """
        # 将数据分组
        hist, _ = np.histogram(values, bins=bins)
        
        # 计算比例
        proportions = hist / np.sum(hist)
        
        # 计算Simpson指数
        D = 1 - np.sum(proportions ** 2)
        
        return D
    
    @staticmethod
    def pielou_evenness(values: np.ndarray, bins: int = 10) -> float:
        """
        Pielou均匀度指数
        
        J' = H' / ln(S)
        
        Parameters
        ----------
        values : array
            水力参数值
        bins : int
            分组数
            
        Returns
        -------
        float
            Pielou均匀度指数
        """
        H = HydraulicDiversityIndex.shannon_index(values, bins)
        
        # 计算实际的类别数
        hist, _ = np.histogram(values, bins=bins)
        S = np.sum(hist > 0)
        
        if S <= 1:
            return 0
        
        J = H / np.log(S)
        
        return J


class HydrologicAlterationAssessment:
    """
    水文改变度评估
    
    评估水坝等工程对河流水文情势的改变程度
    """
    
    @staticmethod
    def calculate_alteration_degree(pre_indicators: Dict[str, float],
                                    post_indicators: Dict[str, float]) -> Dict[str, float]:
        """
        计算水文改变度
        
        改变度 = |post - pre| / pre * 100%
        
        Parameters
        ----------
        pre_indicators : dict
            建坝前指标
        post_indicators : dict
            建坝后指标
            
        Returns
        -------
        dict
            各指标的改变度（%）
        """
        alteration = {}
        
        for key in pre_indicators.keys():
            pre_val = pre_indicators[key]
            post_val = post_indicators[key]
            
            if pre_val != 0:
                alteration[key] = abs(post_val - pre_val) / abs(pre_val) * 100
            else:
                alteration[key] = 0
        
        return alteration
    
    @staticmethod
    def overall_alteration_index(alteration: Dict[str, float]) -> Dict[str, float]:
        """
        计算总体改变指数
        
        Parameters
        ----------
        alteration : dict
            各指标的改变度
            
        Returns
        -------
        dict
            总体改变指数和评级
        """
        values = list(alteration.values())
        
        # 计算统计量
        mean_alteration = np.mean(values)
        median_alteration = np.median(values)
        max_alteration = np.max(values)
        
        # 改变程度分级
        if mean_alteration < 20:
            grade = "轻度改变"
        elif mean_alteration < 40:
            grade = "中度改变"
        elif mean_alteration < 60:
            grade = "较大改变"
        else:
            grade = "严重改变"
        
        return {
            'mean_alteration': mean_alteration,
            'median_alteration': median_alteration,
            'max_alteration': max_alteration,
            'grade': grade
        }


def generate_iha_report(results: Dict) -> str:
    """
    生成IHA分析报告
    
    Parameters
    ----------
    results : dict
        IHA计算结果
        
    Returns
    -------
    str
        格式化的报告文本
    """
    report = []
    report.append("=" * 80)
    report.append("水文改变指标（IHA）分析报告")
    report.append("=" * 80)
    
    if 'pre' in results and 'post' in results:
        # 建坝前后对比报告
        report.append("\n【建坝前后对比分析】\n")
        
        pre = results['pre']
        post = results['post']
        change = results['change']
        
        # 组1：月平均流量
        report.append("1. 月平均流量变化：")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month in months:
            key = f'{month}_mean'
            if key in pre:
                report.append(f"  {month}: {pre[key]:.2f} → {post[key]:.2f} "
                            f"(变化 {change[key]:+.1f}%)")
        
        # 组2：极端流量
        report.append("\n2. 极端流量指标：")
        for window in [1, 7, 30]:
            min_key = f'min_{window}day'
            max_key = f'max_{window}day'
            report.append(f"  {window}日最小流量: {pre[min_key]:.2f} → {post[min_key]:.2f} "
                        f"(变化 {change[min_key]:+.1f}%)")
            report.append(f"  {window}日最大流量: {pre[max_key]:.2f} → {post[max_key]:.2f} "
                        f"(变化 {change[max_key]:+.1f}%)")
        
        # 组3：时间
        report.append("\n3. 极端流量发生时间：")
        report.append(f"  最小流量日: {pre['julian_min']:.0f} → {post['julian_min']:.0f} "
                     f"(偏移 {post['julian_min'] - pre['julian_min']:.0f}天)")
        report.append(f"  最大流量日: {pre['julian_max']:.0f} → {post['julian_max']:.0f} "
                     f"(偏移 {post['julian_max'] - pre['julian_max']:.0f}天)")
        
        # 组4：脉冲
        report.append("\n4. 流量脉冲特征：")
        report.append(f"  高脉冲次数: {pre['high_pulse_count']:.1f} → {post['high_pulse_count']:.1f} "
                     f"(变化 {change['high_pulse_count']:+.1f}%)")
        report.append(f"  低脉冲次数: {pre['low_pulse_count']:.1f} → {post['low_pulse_count']:.1f} "
                     f"(变化 {change['low_pulse_count']:+.1f}%)")
        
        # 组5：变化速率
        report.append("\n5. 流量变化速率：")
        report.append(f"  涨水速率: {pre['rise_rate']:.3f} → {post['rise_rate']:.3f} "
                     f"(变化 {change['rise_rate']:+.1f}%)")
        report.append(f"  落水速率: {pre['fall_rate']:.3f} → {post['fall_rate']:.3f} "
                     f"(变化 {change['fall_rate']:+.1f}%)")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)
