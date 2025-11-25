"""
案例20：智能决策支持系统

展示如何构建地下水智能管理系统，整合：
- 数值模拟
- 机器学习代理模型
- 多目标优化
- 综合决策分析

主要内容:
1. 地下水模拟数据生成（采样）
2. 神经网络代理模型训练
3. 代理模型验证
4. 单目标优化（最大化开采）
5. 多目标优化（开采vs生态vs成本）
6. 帕累托前沿分析
7. 决策推荐

应用场景:
某地区需要规划地下水开采方案，同时考虑：
- 目标1：最大化总开采量（经济）
- 目标2：最小化生态影响（水位下降）
- 目标3：最小化成本（井数和泵送成本）
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
from pathlib import Path
import time
from typing import Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from gwflow.surrogate import (
    NeuralNetworkSurrogate,
    latin_hypercube_sampling,
    plot_sampling_comparison
)
from gwflow.optimization import (
    SimpleNSGAII,
    weighted_sum_method,
    generate_pareto_front_weighted_sum,
    plot_pareto_front_2d
)
from gwflow.pumping import theis_solution, superposition_principle

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def groundwater_simulation(
    Q_wells: np.ndarray,
    well_locations: np.ndarray,
    obs_points: np.ndarray,
    T: float = 1000.0,
    S: float = 0.2,
    t: float = 365.0
) -> np.ndarray:
    """
    地下水多井系统模拟（使用Theis解）
    
    Parameters
    ----------
    Q_wells : np.ndarray
        各井抽水量 (m³/d)，形状(n_wells,)
    well_locations : np.ndarray
        井位坐标 (m)，形状(n_wells, 2)
    obs_points : np.ndarray
        观测点坐标 (m)，形状(n_obs, 2)
    T : float
        导水系数 (m²/d)
    S : float
        贮水系数
    t : float
        时间 (d)
    
    Returns
    -------
    drawdowns : np.ndarray
        各观测点的降深 (m)，形状(n_obs,)
    """
    n_obs = obs_points.shape[0]
    drawdowns = np.zeros(n_obs)
    
    for i, obs_point in enumerate(obs_points):
        # 准备井数据：(x, y, Q)
        wells_data = [
            (well_locations[j, 0], well_locations[j, 1], Q_wells[j])
            for j in range(len(Q_wells))
        ]
        # 使用叠加原理
        s = superposition_principle(
            wells_data,
            obs_point[0],
            obs_point[1],
            t,
            T,
            S,
            method='theis'
        )
        drawdowns[i] = s
    
    return drawdowns


def compute_objectives(
    Q_wells: np.ndarray,
    well_locations: np.ndarray,
    obs_points: np.ndarray,
    eco_points: np.ndarray,
    T: float,
    S: float,
    t: float,
    cost_per_well: float = 100000.0,
    cost_per_m3: float = 0.5
) -> Tuple[float, float, float]:
    """
    计算三个目标函数值
    
    Parameters
    ----------
    Q_wells : np.ndarray
        各井抽水量
    well_locations : np.ndarray
        井位
    obs_points : np.ndarray
        一般观测点
    eco_points : np.ndarray
        生态敏感点
    T, S, t : float
        水文参数
    cost_per_well : float
        单井成本
    cost_per_m3 : float
        单位水量成本
    
    Returns
    -------
    total_pumping : float
        总抽水量（目标1，最大化）
    eco_impact : float
        生态影响（生态点最大降深，目标2，最小化）
    total_cost : float
        总成本（目标3，最小化）
    """
    # 目标1：总抽水量
    total_pumping = np.sum(Q_wells)
    
    # 目标2：生态影响（生态敏感点的最大降深）
    eco_drawdowns = groundwater_simulation(
        Q_wells, well_locations, eco_points, T, S, t
    )
    eco_impact = np.max(eco_drawdowns)
    
    # 目标3：总成本 = 井成本 + 抽水成本
    n_active_wells = np.sum(Q_wells > 0)
    total_cost = n_active_wells * cost_per_well + total_pumping * cost_per_m3 * 365
    
    return total_pumping, eco_impact, total_cost


def experiment1_generate_training_data():
    """
    实验1：生成训练数据
    
    使用拉丁超立方采样生成不同抽水方案，运行数值模拟获取响应。
    """
    print("\n" + "="*70)
    print("实验1：生成训练数据（采样 + 模拟）")
    print("="*70)
    
    # 设定场景
    n_wells = 3
    well_locations = np.array([
        [1000, 1000],
        [3000, 1000],
        [2000, 3000]
    ])
    
    # 观测点（网格）
    x_obs = np.linspace(500, 3500, 10)
    y_obs = np.linspace(500, 3500, 10)
    X_obs, Y_obs = np.meshgrid(x_obs, y_obs)
    obs_points = np.column_stack([X_obs.ravel(), Y_obs.ravel()])
    
    # 生态敏感点
    eco_points = np.array([
        [500, 2000],
        [3500, 2000],
        [2000, 500]
    ])
    
    # 水文参数
    T = 1000.0  # m²/d
    S = 0.2
    t = 365.0  # 1年
    
    # 采样设置
    n_samples = 200
    Q_bounds = [(100, 2000) for _ in range(n_wells)]  # 每井100-2000 m³/d
    
    print(f"\n采样设置:")
    print(f"  井数: {n_wells}")
    print(f"  抽水量范围: 100-2000 m³/d")
    print(f"  样本数: {n_samples}")
    print(f"  观测点数: {len(obs_points)}")
    
    # 拉丁超立方采样
    print(f"\n执行拉丁超立方采样...")
    Q_samples = latin_hypercube_sampling(n_samples, n_wells, Q_bounds, seed=42)
    
    # 运行模拟
    print(f"运行数值模拟...")
    start_time = time.time()
    
    outputs = []
    for i, Q_wells in enumerate(Q_samples):
        obj1, obj2, obj3 = compute_objectives(
            Q_wells, well_locations, obs_points, eco_points, T, S, t
        )
        outputs.append([obj1, obj2, obj3])
        
        if (i + 1) % 50 == 0:
            print(f"  完成 {i+1}/{n_samples} 个样本...")
    
    elapsed_time = time.time() - start_time
    outputs = np.array(outputs)
    
    print(f"\n模拟完成！")
    print(f"  总时间: {elapsed_time:.2f} 秒")
    print(f"  平均时间: {elapsed_time/n_samples*1000:.1f} 毫秒/样本")
    
    # 输出统计
    print(f"\n输出统计:")
    for i, name in enumerate(['总抽水量 (m³/d)', '生态影响 (m)', '总成本 (元)']):
        print(f"  {name}:")
        print(f"    范围: [{outputs[:, i].min():.1f}, {outputs[:, i].max():.1f}]")
        print(f"    均值: {outputs[:, i].mean():.1f}")
    
    return {
        'Q_samples': Q_samples,
        'outputs': outputs,
        'well_locations': well_locations,
        'obs_points': obs_points,
        'eco_points': eco_points,
        'params': {'T': T, 'S': S, 't': t},
        'elapsed_time': elapsed_time
    }


def experiment2_train_surrogate(data):
    """
    实验2：训练神经网络代理模型
    
    用实验1的数据训练代理模型，实现快速预测。
    """
    print("\n" + "="*70)
    print("实验2：训练神经网络代理模型")
    print("="*70)
    
    X_train = data['Q_samples']
    y_train = data['outputs']
    
    # 划分训练/测试集
    n_train = int(0.8 * len(X_train))
    indices = np.random.permutation(len(X_train))
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]
    
    X_train_split = X_train[train_idx]
    y_train_split = y_train[train_idx]
    X_test = X_train[test_idx]
    y_test = y_train[test_idx]
    
    print(f"\n数据集划分:")
    print(f"  训练集: {len(X_train_split)} 样本")
    print(f"  测试集: {len(X_test)} 样本")
    
    # 为每个目标训练独立的代理模型
    surrogates = []
    obj_names = ['总抽水量', '生态影响', '总成本']
    
    for i, name in enumerate(obj_names):
        print(f"\n训练目标 {i+1}: {name}")
        nn = NeuralNetworkSurrogate(
            hidden_layers=(50, 30, 20),
            max_iter=500,
            random_state=42
        )
        nn.train(X_train_split, y_train_split[:, i], verbose=True)
        
        # 评估
        metrics = nn.evaluate(X_test, y_test[:, i])
        print(f"\n测试集性能:")
        print(f"  R² = {metrics['r2']:.4f}")
        print(f"  RMSE = {metrics['rmse']:.2f}")
        print(f"  MAE = {metrics['mae']:.2f}")
        
        surrogates.append(nn)
    
    # 速度对比
    print(f"\n" + "="*70)
    print("速度对比：数值模拟 vs 代理模型")
    print("="*70)
    
    # 数值模拟时间
    avg_sim_time = data['elapsed_time'] / len(data['Q_samples'])
    
    # 代理模型时间
    test_sample = X_test[0:1]
    start = time.time()
    for _ in range(100):
        for nn in surrogates:
            _ = nn.predict(test_sample)
    proxy_time = (time.time() - start) / 100
    
    print(f"  数值模拟: {avg_sim_time*1000:.1f} 毫秒/样本")
    print(f"  代理模型: {proxy_time*1000:.2f} 毫秒/样本")
    print(f"  加速比: {avg_sim_time/proxy_time:.0f}x")
    
    return {
        'surrogates': surrogates,
        'X_test': X_test,
        'y_test': y_test,
        'speedup': avg_sim_time / proxy_time
    }


def experiment3_single_objective_optimization(data, surrogate_data):
    """
    实验3：单目标优化 - 最大化总抽水量
    
    在满足生态约束的前提下，最大化总抽水量。
    """
    print("\n" + "="*70)
    print("实验3：单目标优化（最大化总抽水量）")
    print("="*70)
    
    surrogates = surrogate_data['surrogates']
    well_locations = data['well_locations']
    eco_points = data['eco_points']
    params = data['params']
    
    # 定义目标函数（使用代理模型）
    def total_pumping_objective(Q_wells):
        """目标：最大化总抽水量（转为最小化负值）"""
        pred = surrogates[0].predict(Q_wells.reshape(1, -1))
        return -pred[0]  # 最小化负值 = 最大化正值
    
    def eco_constraint(Q_wells):
        """约束：生态影响 ≤ 3.0 m"""
        pred = surrogates[1].predict(Q_wells.reshape(1, -1))
        return 3.0 - pred[0]  # ≥ 0 表示满足约束
    
    # 优化
    from scipy.optimize import minimize, NonlinearConstraint
    
    print(f"\n优化问题:")
    print(f"  最大化: 总抽水量")
    print(f"  约束: 生态影响 ≤ 3.0 m")
    print(f"  变量: 3口井的抽水量 (100-2000 m³/d)")
    
    x0 = np.array([1000, 1000, 1000])
    bounds = [(100, 2000) for _ in range(3)]
    constraint = NonlinearConstraint(eco_constraint, lb=0, ub=np.inf)
    
    result = minimize(
        total_pumping_objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraint
    )
    
    if result.success:
        opt_Q = result.x
        opt_pumping = -result.fun  # 恢复为正值
        
        # 验证（使用数值模拟）
        true_obj1, true_obj2, true_obj3 = compute_objectives(
            opt_Q, well_locations, data['obs_points'], eco_points,
            params['T'], params['S'], params['t']
        )
        
        print(f"\n优化成功！")
        print(f"  最优方案:")
        for i, Q in enumerate(opt_Q):
            print(f"    井 {i+1}: {Q:.1f} m³/d")
        print(f"\n  代理模型预测:")
        print(f"    总抽水量: {opt_pumping:.1f} m³/d")
        print(f"  数值模拟验证:")
        print(f"    总抽水量: {true_obj1:.1f} m³/d")
        print(f"    生态影响: {true_obj2:.2f} m")
        print(f"    总成本: {true_obj3/1e6:.2f} 百万元")
        print(f"\n  误差: {abs(opt_pumping - true_obj1):.1f} m³/d ({abs(opt_pumping - true_obj1)/true_obj1*100:.1f}%)")
    else:
        print(f"\n优化失败: {result.message}")
        opt_Q = None
    
    return {
        'opt_Q': opt_Q,
        'result': result
    }


def experiment4_multi_objective_optimization(data, surrogate_data):
    """
    实验4：多目标优化（NSGA-II）
    
    同时考虑三个目标：
    1. 最大化总抽水量
    2. 最小化生态影响
    3. 最小化总成本
    """
    print("\n" + "="*70)
    print("实验4：多目标优化（NSGA-II）")
    print("="*70)
    
    surrogates = surrogate_data['surrogates']
    
    # 定义目标函数（使用代理模型）
    def obj1_maximize_pumping(Q_wells):
        """最大化总抽水量（转为最小化）"""
        pred = surrogates[0].predict(Q_wells.reshape(1, -1))
        return -pred[0]  # 转为最小化问题
    
    def obj2_minimize_eco_impact(Q_wells):
        """最小化生态影响"""
        pred = surrogates[1].predict(Q_wells.reshape(1, -1))
        return pred[0]
    
    def obj3_minimize_cost(Q_wells):
        """最小化总成本"""
        pred = surrogates[2].predict(Q_wells.reshape(1, -1))
        return pred[0]
    
    # 运行NSGA-II
    print(f"\n运行NSGA-II...")
    nsga = SimpleNSGAII(
        objectives=[obj1_maximize_pumping, obj2_minimize_eco_impact, obj3_minimize_cost],
        bounds=[(100, 2000) for _ in range(3)],
        population_size=50,
        n_generations=100,
        seed=42
    )
    
    pareto_solutions, pareto_objectives = nsga.run(verbose=True)
    
    # 转换第一个目标回正值（抽水量）
    pareto_objectives[:, 0] = -pareto_objectives[:, 0]
    
    print(f"\n帕累托前沿包含 {len(pareto_solutions)} 个解")
    print(f"\n帕累托前沿目标值范围:")
    print(f"  总抽水量: [{pareto_objectives[:, 0].min():.1f}, {pareto_objectives[:, 0].max():.1f}] m³/d")
    print(f"  生态影响: [{pareto_objectives[:, 1].min():.2f}, {pareto_objectives[:, 1].max():.2f}] m")
    print(f"  总成本: [{pareto_objectives[:, 2].min()/1e6:.2f}, {pareto_objectives[:, 2].max()/1e6:.2f}] 百万元")
    
    return {
        'pareto_solutions': pareto_solutions,
        'pareto_objectives': pareto_objectives
    }


def experiment5_decision_analysis(data, surrogate_data, mo_result):
    """
    实验5：决策分析
    
    从帕累托前沿选择推荐方案。
    """
    print("\n" + "="*70)
    print("实验5：决策分析与方案推荐")
    print("="*70)
    
    pareto_solutions = mo_result['pareto_solutions']
    pareto_objectives = mo_result['pareto_objectives']
    
    # 归一化目标值
    obj_normalized = np.zeros_like(pareto_objectives)
    for i in range(3):
        min_val = pareto_objectives[:, i].min()
        max_val = pareto_objectives[:, i].max()
        if max_val > min_val:
            obj_normalized[:, i] = (pareto_objectives[:, i] - min_val) / (max_val - min_val)
        else:
            obj_normalized[:, i] = 0.5
    
    # 不同偏好下的推荐方案
    preferences = {
        '经济优先': np.array([0.7, 0.2, 0.1]),  # 重视抽水量
        '生态优先': np.array([0.1, 0.7, 0.2]),  # 重视生态
        '成本优先': np.array([0.2, 0.2, 0.6]),  # 重视成本
        '均衡方案': np.array([0.33, 0.33, 0.34])  # 均衡
    }
    
    recommendations = {}
    
    print(f"\n不同偏好下的推荐方案:")
    print("="*70)
    
    for pref_name, weights in preferences.items():
        # 计算加权得分（第一个目标最大化，需转换）
        obj_for_score = obj_normalized.copy()
        obj_for_score[:, 0] = 1 - obj_for_score[:, 0]  # 抽水量：越大越好
        
        scores = np.dot(obj_for_score, weights)
        best_idx = np.argmin(scores)
        
        best_solution = pareto_solutions[best_idx]
        best_objectives = pareto_objectives[best_idx]
        
        print(f"\n{pref_name} (权重: {weights}):")
        print(f"  推荐抽水量:")
        for i, Q in enumerate(best_solution):
            print(f"    井 {i+1}: {Q:.1f} m³/d")
        print(f"  预期结果:")
        print(f"    总抽水量: {best_objectives[0]:.1f} m³/d")
        print(f"    生态影响: {best_objectives[1]:.2f} m")
        print(f"    总成本: {best_objectives[2]/1e6:.2f} 百万元")
        
        recommendations[pref_name] = {
            'solution': best_solution,
            'objectives': best_objectives,
            'weights': weights
        }
    
    return recommendations


def plot_results(exp1, exp2, exp3, exp4, exp5):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # ==================== 第一行 ====================
    # 子图1：采样方法对比
    ax1 = fig.add_subplot(gs[0, 0])
    from gwflow.surrogate import plot_sampling_comparison
    # 简化显示：只显示前两个维度
    Q_samples_2d = exp1['Q_samples'][:, :2]
    ax1.scatter(Q_samples_2d[:, 0], Q_samples_2d[:, 1], 
               alpha=0.6, edgecolors='k', linewidths=0.5, s=30)
    ax1.set_xlabel('井1抽水量 (m³/d)')
    ax1.set_ylabel('井2抽水量 (m³/d)')
    ax1.set_title('(a) 拉丁超立方采样')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：输出分布
    ax2 = fig.add_subplot(gs[0, 1])
    outputs = exp1['outputs']
    ax2.scatter(outputs[:, 0], outputs[:, 1], 
               c=outputs[:, 2], cmap='viridis',
               alpha=0.6, edgecolors='k', linewidths=0.5, s=30)
    ax2.set_xlabel('总抽水量 (m³/d)')
    ax2.set_ylabel('生态影响 (m)')
    cbar = plt.colorbar(ax2.collections[0], ax=ax2)
    cbar.set_label('总成本 (元)', rotation=270, labelpad=20)
    ax2.set_title('(b) 目标空间分布')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：代理模型精度
    ax3 = fig.add_subplot(gs[0, 2])
    y_test = exp2['y_test']
    surrogates = exp2['surrogates']
    X_test = exp2['X_test']
    
    r2_scores = []
    for i, nn in enumerate(surrogates):
        metrics = nn.evaluate(X_test, y_test[:, i])
        r2_scores.append(metrics['r2'])
    
    categories = ['总抽水量', '生态影响', '总成本']
    colors = ['#2ecc71', '#e74c3c', '#3498db']
    bars = ax3.bar(categories, r2_scores, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('R²')
    ax3.set_title('(c) 代理模型精度')
    ax3.set_ylim([0, 1.05])
    ax3.grid(True, axis='y', alpha=0.3)
    for bar, r2 in zip(bars, r2_scores):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{r2:.4f}', ha='center', va='bottom', fontsize=10)
    
    # ==================== 第二行 ====================
    # 子图4：单目标优化结果
    ax4 = fig.add_subplot(gs[1, 0])
    if exp3['opt_Q'] is not None:
        opt_Q = exp3['opt_Q']
        wells = ['井1', '井2', '井3']
        bars = ax4.bar(wells, opt_Q, color='#3498db', alpha=0.7, edgecolor='black')
        ax4.set_ylabel('抽水量 (m³/d)')
        ax4.set_title('(d) 单目标优化最优方案')
        ax4.grid(True, axis='y', alpha=0.3)
        for bar, Q in zip(bars, opt_Q):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{Q:.0f}', ha='center', va='bottom', fontsize=10)
    
    # 子图5-6：帕累托前沿（2D投影）
    pareto_obj = exp4['pareto_objectives']
    
    ax5 = fig.add_subplot(gs[1, 1])
    scatter = ax5.scatter(pareto_obj[:, 0], pareto_obj[:, 1],
                         c=pareto_obj[:, 2], cmap='coolwarm',
                         s=60, alpha=0.7, edgecolors='k', linewidths=1)
    ax5.set_xlabel('总抽水量 (m³/d)')
    ax5.set_ylabel('生态影响 (m)')
    ax5.set_title('(e) 帕累托前沿 (抽水 vs 生态)')
    cbar = plt.colorbar(scatter, ax=ax5)
    cbar.set_label('成本 (元)', rotation=270, labelpad=20)
    ax5.grid(True, alpha=0.3)
    
    ax6 = fig.add_subplot(gs[1, 2])
    scatter = ax6.scatter(pareto_obj[:, 0], pareto_obj[:, 2]/1e6,
                         c=pareto_obj[:, 1], cmap='RdYlGn_r',
                         s=60, alpha=0.7, edgecolors='k', linewidths=1)
    ax6.set_xlabel('总抽水量 (m³/d)')
    ax6.set_ylabel('总成本 (百万元)')
    ax6.set_title('(f) 帕累托前沿 (抽水 vs 成本)')
    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('生态影响 (m)', rotation=270, labelpad=20)
    ax6.grid(True, alpha=0.3)
    
    # ==================== 第三行 ====================
    # 子图7-9：不同偏好推荐方案对比
    pref_names = ['经济优先', '生态优先', '成本优先']
    axes_bottom = [fig.add_subplot(gs[2, i]) for i in range(3)]
    
    for ax, pref_name in zip(axes_bottom, pref_names):
        rec = exp5[pref_name]
        solution = rec['solution']
        
        wells = ['井1', '井2', '井3']
        bars = ax.bar(wells, solution, alpha=0.7, edgecolor='black',
                     color=['#e74c3c', '#3498db', '#2ecc71'])
        ax.set_ylabel('抽水量 (m³/d)')
        ax.set_title(f'({chr(103 + pref_names.index(pref_name))}) {pref_name}方案')
        ax.grid(True, axis='y', alpha=0.3)
        
        for bar, Q in zip(bars, solution):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{Q:.0f}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('案例20：地下水智能决策支持系统全面演示', 
                fontsize=16, fontweight='bold', y=0.995)
    
    return fig


def main():
    """主函数"""
    print("\n" + "="*70)
    print("案例20：智能决策支持系统")
    print("="*70)
    print("\n本案例演示:")
    print("  1. 数据生成（LHS采样 + 数值模拟）")
    print("  2. 神经网络代理模型训练")
    print("  3. 单目标优化")
    print("  4. 多目标优化（NSGA-II）")
    print("  5. 决策分析与推荐")
    
    # 运行实验
    print("\n" + "="*70)
    print("开始运行实验...")
    print("="*70)
    
    exp1 = experiment1_generate_training_data()
    exp2 = experiment2_train_surrogate(exp1)
    exp3 = experiment3_single_objective_optimization(exp1, exp2)
    exp4 = experiment4_multi_objective_optimization(exp1, exp2)
    exp5 = experiment5_decision_analysis(exp1, exp2, exp4)
    
    # 绘图
    print("\n" + "="*70)
    print("生成可视化结果...")
    print("="*70)
    
    fig = plot_results(exp1, exp2, exp3, exp4, exp5)
    
    # 保存
    output_dir = Path(__file__).parent
    output_path = output_dir / 'case_20_results.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n结果已保存至: {output_path}")
    
    # 总结
    print("\n" + "="*70)
    print("案例20完成总结")
    print("="*70)
    print("\n核心成果:")
    print(f"  ✓ 生成训练数据: {len(exp1['Q_samples'])} 个样本")
    print(f"  ✓ 代理模型加速: {exp2['speedup']:.0f}x")
    print(f"  ✓ 单目标优化成功")
    print(f"  ✓ 帕累托前沿包含 {len(exp4['pareto_solutions'])} 个解")
    print(f"  ✓ 提供4种偏好推荐方案")
    
    print("\n智能决策系统能力:")
    print("  ✓ 快速模拟预测（代理模型）")
    print("  ✓ 单目标/多目标优化")
    print("  ✓ 帕累托前沿分析")
    print("  ✓ 决策支持与推荐")
    
    print("\n应用价值:")
    print("  • 缩短决策时间（数天 → 数小时）")
    print("  • 探索更多方案")
    print("  • 权衡多个目标")
    print("  • 科学决策支持")
    
    print("\n" + "="*70)
    print("🎉🎉🎉 案例20完成 - 全书20个案例全部完成！🎉🎉🎉")
    print("="*70)
    
    plt.show()


if __name__ == "__main__":
    main()
