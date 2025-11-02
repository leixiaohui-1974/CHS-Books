"""
生态流量计算模型
===============

实现多种生态流量计算方法
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from .channel import River, RiverReach


class EcologicalFlowCalculator:
    """
    生态流量计算器
    
    实现多种生态流量计算方法：
    1. Tennant法（蒙大拿法）
    2. 湿周法
    3. R2-Cross法
    4. 7Q10法（枯水期低流量）
    
    Parameters
    ----------
    river : River
        河流对象
    """
    
    def __init__(self, river: River):
        self.river = river
        
    def tennant_method(self, season: str = 'annual') -> Dict[str, float]:
        """
        Tennant法（蒙大拿法）
        
        基于多年平均流量的百分比确定生态流量
        
        Parameters
        ----------
        season : str
            季节类型，可选 'annual', 'spawning', 'winter'
            
        Returns
        -------
        dict
            不同生态保护等级对应的流量
            
        Notes
        -----
        Tennant (1976) 推荐值：
        - 优秀: 60-100% MAF
        - 良好: 40-60% MAF  
        - 一般: 30-40% MAF
        - 最小: 10-30% MAF
        - 枯水期最小: 10% MAF
        """
        Q_maf = self.river.Q_maf
        
        # 季节调整系数
        season_factors = {
            'annual': 1.0,
            'spawning': 1.2,  # 产卵期需要更多流量
            'winter': 0.8     # 冬季可适当减少
        }
        
        factor = season_factors.get(season, 1.0)
        
        return {
            'excellent_lower': 0.60 * Q_maf * factor,
            'excellent_upper': 1.00 * Q_maf * factor,
            'good_lower': 0.40 * Q_maf * factor,
            'good_upper': 0.60 * Q_maf * factor,
            'fair_lower': 0.30 * Q_maf * factor,
            'fair_upper': 0.40 * Q_maf * factor,
            'poor_lower': 0.10 * Q_maf * factor,
            'poor_upper': 0.30 * Q_maf * factor,
            'minimum': 0.10 * Q_maf * factor,
            'recommended': 0.30 * Q_maf * factor  # 一般推荐值
        }
    
    def wetted_perimeter_method(self, 
                                 flow_range: Tuple[float, float] = None,
                                 n_points: int = 50) -> Dict[str, any]:
        """
        湿周法
        
        基于湿周-流量关系曲线，找到湿周增长率突变点作为生态流量
        
        Parameters
        ----------
        flow_range : tuple, optional
            流量范围 (Q_min, Q_max)，默认为 (0.05*MAF, MAF)
        n_points : int
            计算点数
            
        Returns
        -------
        dict
            包含生态流量、湿周-流量关系数据
        """
        if flow_range is None:
            Q_min = 0.05 * self.river.Q_maf
            Q_max = self.river.Q_maf
        else:
            Q_min, Q_max = flow_range
        
        # 计算流量-湿周关系
        flows = np.linspace(Q_min, Q_max, n_points)
        wetted_perimeters = []
        
        for Q in flows:
            wp = self.river.average_wetted_perimeter(Q)
            wetted_perimeters.append(wp)
        
        wetted_perimeters = np.array(wetted_perimeters)
        
        # 计算湿周变化率 dP/dQ
        dP_dQ = np.gradient(wetted_perimeters, flows)
        
        # 计算二阶导数（曲率）
        d2P_dQ2 = np.gradient(dP_dQ, flows)
        
        # 找到曲率最大点（拐点）
        inflection_idx = np.argmax(np.abs(d2P_dQ2[5:-5])) + 5  # 排除边界点
        
        Q_eco = flows[inflection_idx]
        WP_eco = wetted_perimeters[inflection_idx]
        
        # 计算湿周比例
        WP_max = wetted_perimeters[-1]
        wp_ratio = WP_eco / WP_max
        
        return {
            'ecological_flow': Q_eco,
            'wetted_perimeter': WP_eco,
            'wp_ratio': wp_ratio,
            'flow_data': flows,
            'wp_data': wetted_perimeters,
            'dP_dQ': dP_dQ,
            'd2P_dQ2': d2P_dQ2,
            'inflection_index': inflection_idx
        }
    
    def r2cross_method(self,
                      flow_range: Tuple[float, float] = None,
                      n_points: int = 50) -> Dict[str, any]:
        """
        R2-Cross法
        
        基于水深-流量关系，通常选择平均水深达到某一阈值的流量
        
        Parameters
        ----------
        flow_range : tuple, optional
            流量范围
        n_points : int
            计算点数
            
        Returns
        -------
        dict
            包含生态流量和水深-流量关系
            
        Notes
        -----
        R2-Cross法通常选择：
        - 水深为最大水深的20-30%时的流量
        """
        if flow_range is None:
            Q_min = 0.05 * self.river.Q_maf
            Q_max = self.river.Q_maf
        else:
            Q_min, Q_max = flow_range
        
        flows = np.linspace(Q_min, Q_max, n_points)
        depths = []
        
        # 使用第一个河段作为代表断面
        if not self.river.reaches:
            raise ValueError("河流中没有河段数据")
        
        reach = self.river.reaches[0]
        
        for Q in flows:
            h = reach.solve_depth(Q)
            depths.append(h)
        
        depths = np.array(depths)
        
        # 找到最大水深的25%对应的流量（经验值）
        h_max = depths[-1]
        target_depth = 0.25 * h_max
        
        # 找到最接近目标水深的流量
        idx = np.argmin(np.abs(depths - target_depth))
        Q_eco = flows[idx]
        h_eco = depths[idx]
        
        return {
            'ecological_flow': Q_eco,
            'depth': h_eco,
            'depth_ratio': h_eco / h_max,
            'flow_data': flows,
            'depth_data': depths,
            'target_depth': target_depth,
            'max_depth': h_max
        }
    
    def q7_10_method(self, annual_min_flows: List[float]) -> float:
        """
        7Q10法
        
        10年重现期的连续7天最低流量
        
        Parameters
        ----------
        annual_min_flows : list
            多年逐年最小7日平均流量数据
            
        Returns
        -------
        float
            7Q10流量值
            
        Notes
        -----
        使用对数正态分布拟合，计算10%保证率的流量
        """
        if len(annual_min_flows) < 10:
            raise ValueError("至少需要10年的流量数据")
        
        # 对数正态分布拟合
        log_flows = np.log(annual_min_flows)
        mean_log = np.mean(log_flows)
        std_log = np.std(log_flows, ddof=1)
        
        # 10%保证率对应的标准正态分位数
        z_10 = -1.282  # 对应10%累积概率
        
        # 计算7Q10
        log_q7_10 = mean_log + z_10 * std_log
        q7_10 = np.exp(log_q7_10)
        
        return q7_10
    
    def comprehensive_assessment(self,
                                flow_range: Tuple[float, float] = None,
                                season: str = 'annual',
                                annual_min_flows: Optional[List[float]] = None) -> Dict[str, any]:
        """
        综合评估生态流量
        
        综合多种方法的结果，给出推荐值
        
        Parameters
        ----------
        flow_range : tuple, optional
            流量范围
        season : str
            季节
        annual_min_flows : list, optional
            年最小流量序列
            
        Returns
        -------
        dict
            各方法结果和综合推荐值
        """
        results = {}
        
        # 1. Tennant法
        tennant = self.tennant_method(season)
        results['tennant'] = tennant
        results['tennant_recommended'] = tennant['recommended']
        
        # 2. 湿周法
        wp_method = self.wetted_perimeter_method(flow_range)
        results['wetted_perimeter'] = wp_method
        results['wp_recommended'] = wp_method['ecological_flow']
        
        # 3. R2-Cross法
        r2cross = self.r2cross_method(flow_range)
        results['r2cross'] = r2cross
        results['r2cross_recommended'] = r2cross['ecological_flow']
        
        # 4. 7Q10法（如果有数据）
        if annual_min_flows is not None and len(annual_min_flows) > 0:
            q7_10 = self.q7_10_method(annual_min_flows)
            results['q7_10'] = q7_10
        
        # 综合推荐值（取中位数）
        recommendations = [
            results['tennant_recommended'],
            results['wp_recommended'],
            results['r2cross_recommended']
        ]
        
        if annual_min_flows is not None and len(annual_min_flows) > 0:
            recommendations.append(results['q7_10'])
        
        results['all_recommendations'] = recommendations
        results['final_recommended'] = np.median(recommendations)
        results['recommendation_range'] = (np.min(recommendations), np.max(recommendations))
        
        # 计算占多年平均流量的比例
        results['percentage_of_maf'] = results['final_recommended'] / self.river.Q_maf * 100
        
        return results
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """
        生成生态流量评估报告
        
        Parameters
        ----------
        results : dict
            综合评估结果
            
        Returns
        -------
        str
            格式化的报告文本
        """
        report = []
        report.append("="*80)
        report.append("生态流量计算综合评估报告")
        report.append("="*80)
        report.append(f"\n河流名称: {self.river.name}")
        report.append(f"多年平均流量: {self.river.Q_maf:.2f} m³/s")
        report.append("\n" + "-"*80)
        report.append("各方法计算结果:")
        report.append("-"*80)
        
        # Tennant法
        report.append(f"\n1. Tennant法（蒙大拿法）")
        report.append(f"   推荐值: {results['tennant_recommended']:.3f} m³/s")
        report.append(f"   占MAF比例: {results['tennant_recommended']/self.river.Q_maf*100:.1f}%")
        
        # 湿周法
        report.append(f"\n2. 湿周法")
        report.append(f"   推荐值: {results['wp_recommended']:.3f} m³/s")
        report.append(f"   对应湿周: {results['wetted_perimeter']['wetted_perimeter']:.2f} m")
        report.append(f"   湿周比例: {results['wetted_perimeter']['wp_ratio']*100:.1f}%")
        
        # R2-Cross法
        report.append(f"\n3. R2-Cross法")
        report.append(f"   推荐值: {results['r2cross_recommended']:.3f} m³/s")
        report.append(f"   对应水深: {results['r2cross']['depth']:.2f} m")
        report.append(f"   水深比例: {results['r2cross']['depth_ratio']*100:.1f}%")
        
        # 7Q10法
        if 'q7_10' in results:
            report.append(f"\n4. 7Q10法")
            report.append(f"   推荐值: {results['q7_10']:.3f} m³/s")
        
        # 综合推荐
        report.append("\n" + "="*80)
        report.append("综合推荐结果:")
        report.append("="*80)
        report.append(f"\n推荐生态流量: {results['final_recommended']:.3f} m³/s")
        report.append(f"占多年平均流量: {results['percentage_of_maf']:.1f}%")
        report.append(f"推荐范围: {results['recommendation_range'][0]:.3f} ~ "
                     f"{results['recommendation_range'][1]:.3f} m³/s")
        
        # 生态保护建议
        pct = results['percentage_of_maf']
        if pct >= 40:
            level = "优秀"
            suggestion = "能够保障河流生态系统良好功能"
        elif pct >= 30:
            level = "良好"
            suggestion = "能够满足主要水生生物的基本需求"
        elif pct >= 20:
            level = "一般"
            suggestion = "能够维持水生生态系统基本功能，但生境质量受限"
        else:
            level = "较差"
            suggestion = "仅能满足最低生存需求，建议提高生态流量"
        
        report.append(f"\n生态保护等级: {level}")
        report.append(f"评价: {suggestion}")
        report.append("\n" + "="*80)
        
        return "\n".join(report)
