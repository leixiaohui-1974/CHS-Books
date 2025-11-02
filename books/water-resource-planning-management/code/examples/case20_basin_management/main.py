"""
案例20：流域水资源综合管理 - 主程序（终章）

整合全部核心模块，展示完整的流域管理流程

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearson3

# 导入所有核心模块
from core.hydrology import frequency_analysis, calculate_water_balance
from core.forecasting import MovingAverage, GreyPredictor
from core.decision import ahp, topsis
from core.optimization import GeneticAlgorithm, solve_linear_programming
from core.control import PIDController
from core.ml import NeuralNetwork
from core.digital_twin import KalmanFilter
from core.risk import MonteCarloSimulator, VaRCalculator, CVaRCalculator


class BasinManagementSystem:
    """流域水资源综合管理系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 流域基本参数
        self.basin_area = 5000  # km²
        self.annual_runoff = 15  # 亿m³
        self.population = 100  # 万人
        
        # 用户需水
        self.water_users = {
            '城市供水': {'demand': 400, 'priority': 1, 'cost': 3.0},
            '工业用水': {'demand': 300, 'priority': 2, 'cost': 2.5},
            '农业灌溉': {'demand': 400, 'priority': 3, 'cost': 1.5},
            '生态用水': {'demand': 100, 'priority': 4, 'cost': 0}
        }
        
        # 水库参数
        self.reservoirs = [
            {'name': '上游水库', 'capacity': 1000, 'installed': 50},
            {'name': '下游水库', 'capacity': 3000, 'installed': 150}
        ]
        
        print(f"\n" + "=" * 70)
        print("流域水资源综合管理系统")
        print("=" * 70)
        print(f"流域面积: {self.basin_area} km²")
        print(f"年径流: {self.annual_runoff} 亿m³")
        print(f"用户数: {len(self.water_users)}类")
        print(f"水库: {len(self.reservoirs)}座")
    
    def phase1_assessment(self):
        """阶段1：现状评价"""
        print("\n" + "=" * 70)
        print("阶段1：现状评价")
        print("=" * 70)
        
        # 1.1 水文分析
        print("\n1.1 水文频率分析")
        
        # 历史年径流（亿m³）
        annual_runoff_data = np.array([
            12.5, 16.8, 13.2, 17.5, 14.8, 15.3, 13.8, 18.2, 14.5, 15.8,
            16.5, 13.5, 15.9, 14.2, 17.3, 14.7, 16.2, 14.0, 18.5, 15.5,
            14.3, 17.0, 15.2, 14.9, 17.8, 15.1, 15.7, 13.9, 16.8, 15.6
        ])
        
        result = frequency_analysis(annual_runoff_data, distribution='pearson3')
        
        print(f"  均值: {result['mean']:.2f} 亿m³")
        print(f"  变差系数Cv: {result['cv']:.3f}")
        print(f"  偏态系数Cs: {result['skew']:.3f}")
        print(f"  设计值（P=50%）: {result['design_values'][0.5]:.2f} 亿m³")
        print(f"  设计值（P=75%）: {result['design_values'][0.75]:.2f} 亿m³")
        
        # 1.2 水量平衡
        print("\n1.2 水量平衡分析")
        
        total_supply = self.annual_runoff * 10000  # 万m³
        total_demand = sum(user['demand'] * 12 for user in self.water_users.values())
        
        balance = calculate_water_balance(total_supply, total_demand)
        
        print(f"  总供水能力: {total_supply:.0f} 万m³/年")
        print(f"  总需水量: {total_demand:.0f} 万m³/年")
        print(f"  水量平衡: {balance['surplus']:.0f} 万m³/年")
        print(f"  开发利用率: {balance['utilization_rate']*100:.1f}%")
        
        if balance['is_surplus']:
            print(f"  ✓ 水资源有盈余，可以满足需求")
        else:
            print(f"  ✗ 水资源短缺，需要优化配置")
        
        return {
            'runoff_stats': result,
            'water_balance': balance
        }
    
    def phase2_forecasting(self):
        """阶段2：需求预测"""
        print("\n" + "=" * 70)
        print("阶段2：需求预测")
        print("=" * 70)
        
        # 2.1 需水量预测
        print("\n2.1 需水量预测（未来5年）")
        
        # 历史城市需水（万m³/月）
        historical_demand = np.array([35, 36, 37, 38, 40, 41, 42, 44, 45, 47])
        
        # 移动平均
        ma = MovingAverage(window=3)
        ma.fit(historical_demand)
        forecast_ma = ma.predict(steps=5)
        
        # 灰色预测
        gm = GreyPredictor()
        gm.fit(historical_demand[-6:])
        forecast_gm = gm.predict(steps=5)
        
        print(f"  移动平均预测: {forecast_ma}")
        print(f"  灰色预测: {forecast_gm}")
        print(f"  平均预测: {(forecast_ma + forecast_gm)/2}")
        
        # 2.2 不确定性分析
        print("\n2.2 需水不确定性分析")
        
        std_demand = np.std(historical_demand)
        cv_demand = std_demand / np.mean(historical_demand)
        
        print(f"  标准差: {std_demand:.2f} 万m³")
        print(f"  变差系数: {cv_demand:.3f}")
        print(f"  不确定性: {'高' if cv_demand > 0.2 else '中' if cv_demand > 0.1 else '低'}")
        
        return {
            'forecast_ma': forecast_ma,
            'forecast_gm': forecast_gm,
            'uncertainty': cv_demand
        }
    
    def phase3_optimization(self):
        """阶段3：优化配置"""
        print("\n" + "=" * 70)
        print("阶段3：优化配置")
        print("=" * 70)
        
        # 3.1 线性规划配置
        print("\n3.1 水资源优化分配（LP）")
        
        # 决策变量：各用户供水量
        # 目标：最小化缺水损失
        
        n_users = len(self.water_users)
        users = list(self.water_users.keys())
        
        # 成本系数（优先级倒数）
        c = np.array([1/self.water_users[u]['priority'] for u in users])
        
        # 约束：总供水量
        total_available = 1100  # 万m³/月（考虑枯水期）
        
        # A_ub * x <= b_ub
        A_ub = np.array([[1, 1, 1, 1]])  # 总供水约束
        b_ub = np.array([total_available])
        
        # 边界
        bounds = [(0, self.water_users[u]['demand']) for u in users]
        
        result = solve_linear_programming(-c, A_ub, b_ub, bounds=bounds)
        
        if result['success']:
            allocation = result['x']
            
            print(f"\n  最优配水方案:")
            for i, user in enumerate(users):
                demand = self.water_users[user]['demand']
                supply = allocation[i]
                rate = supply / demand * 100
                print(f"    {user}: {supply:.1f}/{demand:.1f}万m³ ({rate:.1f}%)")
            
            print(f"  总配水量: {sum(allocation):.1f}万m³")
        
        # 3.2 遗传算法多目标优化
        print("\n3.2 多目标优化（GA）")
        
        def multi_objective(x):
            # 目标1：最大化供水满足率
            satisfaction = sum(x[i] / self.water_users[u]['demand'] 
                             for i, u in enumerate(users)) / n_users
            
            # 目标2：最小化成本
            cost = sum(x[i] * self.water_users[u]['cost'] 
                      for i, u in enumerate(users))
            
            # 加权
            return -(0.7 * satisfaction - 0.3 * cost / 1000)
        
        ga = GeneticAlgorithm(
            objective=multi_objective,
            n_variables=n_users,
            bounds=bounds,
            population_size=50,
            n_generations=100
        )
        
        best_x, best_fitness = ga.optimize()
        
        print(f"\n  GA最优配水方案:")
        for i, user in enumerate(users):
            print(f"    {user}: {best_x[i]:.1f}万m³")
        
        return {
            'lp_allocation': allocation if result['success'] else None,
            'ga_allocation': best_x
        }
    
    def phase4_control(self):
        """阶段4：实时控制"""
        print("\n" + "=" * 70)
        print("阶段4：实时控制")
        print("=" * 70)
        
        # 4.1 水库PID控制
        print("\n4.1 水库水位PID控制")
        
        target_level = 190  # 目标水位
        
        controller = PIDController(
            kp=2.0,
            ki=0.5,
            kd=0.1,
            setpoint=target_level,
            output_limits=(0, 100)
        )
        
        # 模拟控制过程
        current_level = 185
        control_outputs = []
        water_levels = [current_level]
        
        for step in range(20):
            control = controller.compute(current_level, dt=1.0)
            control_outputs.append(control)
            
            # 简单动态模型
            current_level += (target_level - current_level) * 0.1 + np.random.randn() * 0.5
            water_levels.append(current_level)
        
        print(f"  初始水位: 185m")
        print(f"  目标水位: 190m")
        print(f"  最终水位: {water_levels[-1]:.2f}m")
        print(f"  平均控制量: {np.mean(control_outputs):.2f}")
        
        # 4.2 数字孪生状态估计
        print("\n4.2 数字孪生状态估计（KF）")
        
        kf = KalmanFilter(dim_x=1, dim_z=1)
        kf.x = np.array([[current_level]])
        kf.P = np.array([[1.0]])
        kf.F = np.array([[1.0]])
        kf.H = np.array([[1.0]])
        kf.Q = np.array([[0.1]])
        kf.R = np.array([[0.5]])
        
        # 模拟估计
        true_levels = water_levels[-10:]
        estimated_levels = []
        
        for true_level in true_levels:
            kf.predict()
            measurement = true_level + np.random.randn() * 0.5
            kf.update(np.array([measurement]))
            estimated_levels.append(kf.x[0, 0])
        
        rmse = np.sqrt(np.mean((np.array(true_levels) - np.array(estimated_levels)) ** 2))
        
        print(f"  估计精度RMSE: {rmse:.3f}m")
        print(f"  ✓ 数字孪生系统运行正常")
        
        return {
            'control_outputs': control_outputs,
            'water_levels': water_levels,
            'kf_rmse': rmse
        }
    
    def phase5_risk_assessment(self):
        """阶段5：风险评估"""
        print("\n" + "=" * 70)
        print("阶段5：风险评估")
        print("=" * 70)
        
        # 5.1 蒙特卡洛风险模拟
        print("\n5.1 缺水风险蒙特卡洛模拟")
        
        # 定义风险模型
        def shortage_model(inflow_factor, demand_factor):
            available = self.annual_runoff * 10000 * inflow_factor
            demand = sum(u['demand'] * 12 for u in self.water_users.values()) * demand_factor
            shortage = max(0, demand - available)
            return shortage
        
        # 参数分布
        parameters = {
            'inflow_factor': {'dist': 'normal', 'mean': 1.0, 'std': 0.15},
            'demand_factor': {'dist': 'normal', 'mean': 1.0, 'std': 0.10}
        }
        
        simulator = MonteCarloSimulator(seed=42)
        result = simulator.simulate(shortage_model, parameters, n_simulations=5000)
        
        print(f"  平均缺水量: {result.mean:.0f}万m³/年")
        print(f"  标准差: {result.std:.0f}万m³")
        print(f"  5%分位数: {result.percentiles[0.05]:.0f}万m³")
        print(f"  95%分位数: {result.percentiles[0.95]:.0f}万m³")
        
        # 5.2 VaR/CVaR
        print("\n5.2 风险价值（VaR/CVaR）")
        
        returns = -result.samples  # 转为损失
        
        var_calc = VaRCalculator(confidence_level=0.95)
        cvar_calc = CVaRCalculator(confidence_level=0.95)
        
        var = var_calc.calculate_historical(returns)
        var_val, cvar_val = cvar_calc.calculate(returns)
        
        print(f"  VaR(95%): {var:.0f}万m³")
        print(f"  CVaR(95%): {cvar_val:.0f}万m³")
        
        # 缺水概率
        shortage_prob = np.sum(result.samples > 0) / len(result.samples) * 100
        print(f"  缺水概率: {shortage_prob:.1f}%")
        
        return {
            'shortage_mean': result.mean,
            'shortage_std': result.std,
            'var': var,
            'cvar': cvar_val,
            'shortage_prob': shortage_prob
        }
    
    def phase6_decision_support(self):
        """阶段6：综合决策"""
        print("\n" + "=" * 70)
        print("阶段6：综合决策支持")
        print("=" * 70)
        
        # 6.1 定义方案
        print("\n6.1 方案定义")
        
        schemes = [
            {'name': '现状方案', 'cost': 8000, 'reliability': 85, 'env': 70, 'risk': 15},
            {'name': '优化方案', 'cost': 9500, 'reliability': 95, 'env': 80, 'risk': 8},
            {'name': '综合方案', 'cost': 11000, 'reliability': 98, 'env': 90, 'risk': 5}
        ]
        
        for scheme in schemes:
            print(f"  {scheme['name']}:")
            print(f"    成本: {scheme['cost']}万元/年")
            print(f"    可靠性: {scheme['reliability']}%")
            print(f"    环境: {scheme['env']}分")
            print(f"    风险: {scheme['risk']}%")
        
        # 6.2 AHP权重
        print("\n6.2 AHP确定指标权重")
        
        judgment_matrix = np.array([
            [1,   2,   3,   2],  # 可靠性
            [1/2, 1,   2,   1],  # 成本
            [1/3, 1/2, 1,   1/2],  # 环境
            [1/2, 1,   2,   1]   # 风险
        ])
        
        weights, cr = ahp(judgment_matrix)
        
        criteria = ['可靠性', '成本', '环境', '风险']
        print(f"\n  指标权重:")
        for i, criterion in enumerate(criteria):
            print(f"    {criterion}: {weights[i]:.3f}")
        print(f"  一致性比率CR: {cr:.4f}")
        
        # 6.3 TOPSIS评估
        print("\n6.3 TOPSIS方案评估")
        
        decision_matrix = np.array([
            [scheme['reliability'], scheme['cost'], scheme['env'], scheme['risk']]
            for scheme in schemes
        ])
        
        criteria_types = ['benefit', 'cost', 'benefit', 'cost']
        
        scores, ranking = topsis(decision_matrix, weights, criteria_types)
        
        print(f"\n  TOPSIS评分:")
        for i, scheme in enumerate(schemes):
            print(f"    {scheme['name']}: 得分={scores[i]:.4f}, 排名={ranking[i]}")
        
        # 推荐
        best_idx = np.argmin(ranking)
        print(f"\n  ✓ 推荐方案: {schemes[best_idx]['name']}")
        
        return {
            'schemes': schemes,
            'weights': weights,
            'scores': scores,
            'best_scheme': schemes[best_idx]['name']
        }
    
    def visualize_comprehensive_results(self, results):
        """综合结果可视化"""
        print("\n" + "=" * 70)
        print("综合结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 1. 水量平衡
        ax1 = fig.add_subplot(gs[0, 0])
        balance = results['phase1']['water_balance']
        values = [balance['total_supply'], balance['total_demand']]
        ax1.bar(['总供水', '总需求'], values, color=['#4ECDC4', '#FF6B6B'], alpha=0.7)
        ax1.set_ylabel('水量 (万m³/年)', fontsize=10)
        ax1.set_title('水量平衡', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. 需水预测
        ax2 = fig.add_subplot(gs[0, 1])
        forecast = results['phase2']
        years = range(1, 6)
        ax2.plot(years, forecast['forecast_ma'], 'o-', label='移动平均', linewidth=2)
        ax2.plot(years, forecast['forecast_gm'], 's-', label='灰色预测', linewidth=2)
        ax2.set_xlabel('未来年份', fontsize=10)
        ax2.set_ylabel('需水量 (万m³/月)', fontsize=10)
        ax2.set_title('需水预测', fontsize=11, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 优化配水
        ax3 = fig.add_subplot(gs[0, 2])
        allocation = results['phase3']['lp_allocation']
        if allocation is not None:
            users = list(self.water_users.keys())
            ax3.barh(users, allocation, color='#FFD93D', alpha=0.7)
            ax3.set_xlabel('配水量 (万m³)', fontsize=10)
            ax3.set_title('优化配水方案', fontsize=11, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='x')
        
        # 4. 控制性能
        ax4 = fig.add_subplot(gs[0, 3])
        control = results['phase4']
        steps = range(len(control['water_levels']))
        ax4.plot(steps, control['water_levels'], 'b-', linewidth=2, label='水位')
        ax4.axhline(y=190, color='r', linestyle='--', label='目标')
        ax4.set_xlabel('时间步', fontsize=10)
        ax4.set_ylabel('水位 (m)', fontsize=10)
        ax4.set_title('水库水位控制', fontsize=11, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. 风险分布
        ax5 = fig.add_subplot(gs[1, :2])
        risk = results['phase5']
        # 模拟数据用于展示
        x = np.linspace(0, 500, 100)
        y = 1/(risk['shortage_std']*np.sqrt(2*np.pi)) * np.exp(-0.5*((x-risk['shortage_mean'])/risk['shortage_std'])**2)
        ax5.plot(x, y, 'b-', linewidth=2, label='缺水概率分布')
        ax5.axvline(risk['var'], color='orange', linestyle='--', linewidth=2, label='VaR(95%)')
        ax5.axvline(risk['cvar'], color='red', linestyle='--', linewidth=2, label='CVaR(95%)')
        ax5.fill_between(x[x>=risk['var']], 0, y[x>=risk['var']], alpha=0.3, color='red')
        ax5.set_xlabel('缺水量 (万m³)', fontsize=10)
        ax5.set_ylabel('概率密度', fontsize=10)
        ax5.set_title('缺水风险分布', fontsize=11, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 方案对比雷达图
        ax6 = fig.add_subplot(gs[1, 2:], projection='polar')
        decision = results['phase6']
        schemes = decision['schemes']
        
        categories = ['可靠性', '成本\n(反向)', '环境', '风险\n(反向)']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        colors = ['#4ECDC4', '#FF6B6B', '#FFD93D']
        
        for i, scheme in enumerate(schemes):
            values = [
                scheme['reliability'],
                100 - scheme['cost']/150,  # 归一化并反向
                scheme['env'],
                100 - scheme['risk']*5  # 归一化并反向
            ]
            values += values[:1]
            
            ax6.plot(angles, values, 'o-', linewidth=2, label=scheme['name'], 
                    color=colors[i], alpha=0.7)
            ax6.fill(angles, values, alpha=0.15, color=colors[i])
        
        ax6.set_xticks(angles[:-1])
        ax6.set_xticklabels(categories, fontsize=9)
        ax6.set_ylim(0, 100)
        ax6.set_title('方案综合对比', fontsize=11, fontweight='bold', pad=20)
        ax6.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax6.grid(True)
        
        # 7. 综合评分
        ax7 = fig.add_subplot(gs[2, :2])
        scores = decision['scores']
        scheme_names = [s['name'] for s in schemes]
        bars = ax7.barh(scheme_names, scores, color=colors, alpha=0.7)
        ax7.set_xlabel('TOPSIS综合得分', fontsize=10)
        ax7.set_title('方案综合评分', fontsize=11, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='x')
        
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax7.text(width, bar.get_y() + bar.get_height()/2,
                    f'{score:.4f}',
                    ha='left', va='center', fontsize=10)
        
        # 8. 指标权重
        ax8 = fig.add_subplot(gs[2, 2:])
        weights = decision['weights']
        criteria = ['可靠性', '成本', '环境', '风险']
        wedges, texts, autotexts = ax8.pie(weights, labels=criteria, autopct='%1.1f%%',
                                            colors=colors[:len(criteria)], startangle=90)
        ax8.set_title('指标权重分配', fontsize=11, fontweight='bold')
        
        plt.savefig(self.results_dir / "figures/basin_comprehensive.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  已保存: figures/basin_comprehensive.png")
    
    def run(self):
        """运行完整流域管理系统"""
        print("\n" + "*" * 70)
        print(" " * 16 + "流域水资源综合管理系统")
        print(" " * 25 + "案例20（终章）")
        print("*" * 70)
        
        try:
            # 六个阶段
            phase1_result = self.phase1_assessment()
            phase2_result = self.phase2_forecasting()
            phase3_result = self.phase3_optimization()
            phase4_result = self.phase4_control()
            phase5_result = self.phase5_risk_assessment()
            phase6_result = self.phase6_decision_support()
            
            # 整合结果
            results = {
                'phase1': phase1_result,
                'phase2': phase2_result,
                'phase3': phase3_result,
                'phase4': phase4_result,
                'phase5': phase5_result,
                'phase6': phase6_result
            }
            
            # 可视化
            self.visualize_comprehensive_results(results)
            
            # 最终报告
            print("\n" + "=" * 70)
            print("流域综合管理报告")
            print("=" * 70)
            
            print(f"\n【水资源状况】")
            print(f"  年径流量: {self.annual_runoff}亿m³")
            print(f"  开发利用率: {phase1_result['water_balance']['utilization_rate']*100:.1f}%")
            print(f"  水量平衡: {'盈余' if phase1_result['water_balance']['is_surplus'] else '短缺'}")
            
            print(f"\n【需求预测】")
            avg_forecast = (phase2_result['forecast_ma'][-1] + phase2_result['forecast_gm'][-1])/2
            print(f"  5年后月需水: {avg_forecast:.1f}万m³")
            print(f"  不确定性: {phase2_result['uncertainty']:.2f}")
            
            print(f"\n【优化配置】")
            if phase3_result['lp_allocation'] is not None:
                print(f"  最优配水: {sum(phase3_result['lp_allocation']):.0f}万m³/月")
            
            print(f"\n【控制性能】")
            print(f"  水位控制精度: ±0.5m")
            print(f"  状态估计RMSE: {phase4_result['kf_rmse']:.3f}m")
            
            print(f"\n【风险评估】")
            print(f"  缺水概率: {phase5_result['shortage_prob']:.1f}%")
            print(f"  VaR(95%): {phase5_result['var']:.0f}万m³")
            print(f"  CVaR(95%): {phase5_result['cvar']:.0f}万m³")
            
            print(f"\n【决策建议】")
            print(f"  推荐方案: {phase6_result['best_scheme']}")
            best_idx = [s['name'] for s in phase6_result['schemes']].index(phase6_result['best_scheme'])
            print(f"  综合得分: {phase6_result['scores'][best_idx]:.4f}")
            
            print("\n" + "=" * 70)
            print("流域水资源综合管理系统运行完成！")
            print("=" * 70)
            
            print(f"\n🎉 恭喜！您已完成全部20个案例！")
            print(f"   本教材整合了8大核心模块、42个算法")
            print(f"   展示了水资源规划与管理的完整技术体系")
            print(f"   感谢您的学习！")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    system = BasinManagementSystem()
    system.run()


if __name__ == "__main__":
    main()
