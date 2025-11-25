"""
案例19：地下水数字孪生架构

展示如何构建地下水系统的数字孪生，实现实时状态估计、数据同化和预测。

主要内容:
1. 卡尔曼滤波原理验证（1D简单系统）
2. 地下水模型数据同化
3. 标准KF vs 集合EnKF对比
4. 多井观测系统
5. 不确定性量化
6. 实时预测演示

理论基础:
- 卡尔曼滤波
- 集合卡尔曼滤波（EnKF）
- 数据同化
- 数字孪生概念
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from gwflow.digital_twin import (
    KalmanFilter,
    EnsembleKalmanFilter,
    ObservationSystem,
    GroundwaterDigitalTwin,
    compute_rmse
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment1_kalman_1d():
    """
    实验1：卡尔曼滤波原理验证（1D简单系统）
    
    使用简单的1D动态系统验证卡尔曼滤波的预测-更新过程。
    """
    print("\n" + "="*70)
    print("实验1：卡尔曼滤波原理验证（1D简单系统）")
    print("="*70)
    
    # 1D系统：x(k+1) = 0.95 * x(k) + w(k)
    # 观测：z(k) = x(k) + v(k)
    
    # 参数
    n_steps = 50
    F = np.array([[0.95]])  # 状态转移
    H = np.array([[1.0]])    # 观测矩阵
    Q = np.array([[0.01]])   # 过程噪声
    R = np.array([[0.1]])    # 观测噪声
    
    # 初始化
    x_true = np.array([10.0])
    x_est = np.array([8.0])  # 初始估计有偏差
    P = np.array([[1.0]])
    
    # 创建卡尔曼滤波器
    kf = KalmanFilter(F, H, Q, R)
    
    # 记录
    true_states = []
    observations = []
    estimates = []
    predictions = []
    uncertainties = []
    kalman_gains = []
    
    # 模拟
    for step in range(n_steps):
        # 真实系统演化
        x_true = F @ x_true + np.random.normal(0, np.sqrt(Q[0, 0]), size=(1,))
        
        # 生成观测
        z = H @ x_true + np.random.normal(0, np.sqrt(R[0, 0]), size=(1,))
        
        # 卡尔曼滤波
        result = kf.filter_step(x_est, P, z)
        
        # 记录
        true_states.append(x_true[0])
        observations.append(z[0])
        predictions.append(result.x_pred[0])
        estimates.append(result.x_update[0])
        uncertainties.append(np.sqrt(result.P_update[0, 0]))
        kalman_gains.append(result.K[0, 0])
        
        # 更新
        x_est = result.x_update
        P = result.P_update
    
    # 转换为数组
    true_states = np.array(true_states)
    observations = np.array(observations)
    predictions = np.array(predictions)
    estimates = np.array(estimates)
    uncertainties = np.array(uncertainties)
    kalman_gains = np.array(kalman_gains)
    
    # 计算误差
    rmse_obs = compute_rmse(observations, true_states)
    rmse_est = compute_rmse(estimates, true_states)
    
    print(f"\n观测RMSE: {rmse_obs:.4f}")
    print(f"估计RMSE: {rmse_est:.4f}")
    print(f"改善率: {(1 - rmse_est/rmse_obs)*100:.1f}%")
    print(f"最终卡尔曼增益: {kalman_gains[-1]:.4f}")
    print(f"最终不确定性: {uncertainties[-1]:.4f}")
    
    return {
        'true_states': true_states,
        'observations': observations,
        'predictions': predictions,
        'estimates': estimates,
        'uncertainties': uncertainties,
        'kalman_gains': kalman_gains,
        'rmse_obs': rmse_obs,
        'rmse_est': rmse_est
    }


def simple_gw_model(h: np.ndarray, dt: float) -> np.ndarray:
    """
    简化的地下水模型（用于演示）
    
    假设：
    - 稳态流动近似
    - 简单的扩散过程
    
    Parameters
    ----------
    h : np.ndarray
        当前水头 (ny × nx)
    dt : float
        时间步长（此模型不使用，假设稳态）
    
    Returns
    -------
    h_next : np.ndarray
        下一时刻水头
    """
    # 简单的扩散平滑（模拟流动）
    from scipy.ndimage import gaussian_filter
    h_next = gaussian_filter(h, sigma=1.0, mode='nearest')
    return h_next


def experiment2_groundwater_assimilation():
    """
    实验2：地下水模型数据同化
    
    使用简化的地下水模型进行数据同化演示。
    """
    print("\n" + "="*70)
    print("实验2：地下水模型数据同化")
    print("="*70)
    
    # 网格参数
    nx, ny = 30, 30
    dx, dy = 100.0, 100.0
    
    # 创建观测系统（5口井）
    obs_sys = ObservationSystem(nx, ny, dx, dy)
    obs_sys.add_well(500, 500, noise_std=0.05, name="MW-1")
    obs_sys.add_well(2500, 500, noise_std=0.05, name="MW-2")
    obs_sys.add_well(1500, 1500, noise_std=0.08, name="MW-3")
    obs_sys.add_well(500, 2500, noise_std=0.05, name="MW-4")
    obs_sys.add_well(2500, 2500, noise_std=0.05, name="MW-5")
    
    print(f"\n观测系统设置:")
    print(f"  网格: {nx} × {ny}")
    print(f"  监测井: {obs_sys.n_wells} 口")
    
    # 生成"真实"地下水场
    x = np.linspace(0, (nx-1)*dx, nx)
    y = np.linspace(0, (ny-1)*dy, ny)
    X, Y = np.meshgrid(x, y)
    
    # 真实场：抛物线形水头分布
    h_true_initial = 100.0 - 0.000005 * ((X - 1500)**2 + (Y - 1500)**2)
    
    # 模拟真实系统演化（添加小扰动）
    n_steps = 20
    dt = 1.0
    true_evolution = [h_true_initial.copy()]
    for step in range(n_steps - 1):
        h_current = true_evolution[-1]
        # 添加随机扰动模拟动态变化
        perturbation = np.random.normal(0, 0.02, h_current.shape)
        h_next = simple_gw_model(h_current + perturbation, dt)
        true_evolution.append(h_next)
    
    # 初始化数字孪生（标准KF）
    initial_guess = h_true_initial + np.random.normal(0, 2.0, h_true_initial.shape)
    
    dt_kf = GroundwaterDigitalTwin(
        model=simple_gw_model,
        observation_system=obs_sys,
        use_enkf=False,
        process_noise_std=0.05,
        name="KF_DigitalTwin"
    )
    dt_kf.initialize(initial_guess, initial_std=1.0)
    
    # 运行数据同化
    print(f"\n运行数据同化 ({n_steps} 步)...")
    results_kf = []
    for step in range(n_steps):
        h_true = true_evolution[step]
        obs = obs_sys.generate_observations(h_true, add_noise=True)
        info = dt_kf.assimilate_and_update(obs, dt, h_true)
        results_kf.append(info)
        
        if step % 5 == 0:
            print(f"  步骤 {step}: RMSE = {info['rmse']:.4f} m")
    
    # 提取结果
    times = np.array([r['time'] for r in results_kf])
    rmses = np.array([r['rmse'] for r in results_kf])
    
    print(f"\n数据同化完成:")
    print(f"  初始RMSE: {rmses[0]:.4f} m")
    print(f"  最终RMSE: {rmses[-1]:.4f} m")
    print(f"  改善率: {(1 - rmses[-1]/rmses[0])*100:.1f}%")
    
    return {
        'digital_twin': dt_kf,
        'true_evolution': true_evolution,
        'results': results_kf,
        'times': times,
        'rmses': rmses,
        'obs_system': obs_sys
    }


def experiment3_kf_vs_enkf():
    """
    实验3：标准KF vs 集合EnKF对比
    
    比较标准卡尔曼滤波和集合卡尔曼滤波的性能。
    """
    print("\n" + "="*70)
    print("实验3：标准KF vs 集合EnKF对比")
    print("="*70)
    
    # 网格参数
    nx, ny = 20, 20
    dx, dy = 100.0, 100.0
    
    # 创建观测系统
    obs_sys = ObservationSystem(nx, ny, dx, dy)
    obs_sys.add_well(500, 500, noise_std=0.08, name="MW-1")
    obs_sys.add_well(1500, 500, noise_std=0.08, name="MW-2")
    obs_sys.add_well(1000, 1000, noise_std=0.08, name="MW-3")
    obs_sys.add_well(500, 1500, noise_std=0.08, name="MW-4")
    obs_sys.add_well(1500, 1500, noise_std=0.08, name="MW-5")
    
    # 生成真实演化
    x = np.linspace(0, (nx-1)*dx, nx)
    y = np.linspace(0, (ny-1)*dy, ny)
    X, Y = np.meshgrid(x, y)
    h_true_initial = 50.0 - 0.00001 * ((X - 1000)**2 + (Y - 1000)**2)
    
    n_steps = 15
    dt = 1.0
    true_evolution = [h_true_initial.copy()]
    for step in range(n_steps - 1):
        h_current = true_evolution[-1]
        perturbation = np.random.normal(0, 0.05, h_current.shape)
        h_next = simple_gw_model(h_current + perturbation, dt)
        true_evolution.append(h_next)
    
    # 初始猜测
    initial_guess = h_true_initial + np.random.normal(0, 3.0, h_true_initial.shape)
    
    # 创建两个数字孪生
    dt_kf = GroundwaterDigitalTwin(
        model=simple_gw_model,
        observation_system=obs_sys,
        use_enkf=False,
        process_noise_std=0.1,
        name="StandardKF"
    )
    dt_kf.initialize(initial_guess.copy(), initial_std=2.0)
    
    dt_enkf = GroundwaterDigitalTwin(
        model=simple_gw_model,
        observation_system=obs_sys,
        use_enkf=True,
        n_ensemble=30,
        process_noise_std=0.1,
        name="EnKF"
    )
    dt_enkf.initialize(initial_guess.copy(), initial_std=2.0)
    
    print(f"\n对比两种方法 ({n_steps} 步)...")
    
    # 运行两种方法
    results_kf = []
    results_enkf = []
    
    for step in range(n_steps):
        h_true = true_evolution[step]
        obs = obs_sys.generate_observations(h_true, add_noise=True)
        
        info_kf = dt_kf.assimilate_and_update(obs, dt, h_true)
        info_enkf = dt_enkf.assimilate_and_update(obs, dt, h_true)
        
        results_kf.append(info_kf)
        results_enkf.append(info_enkf)
        
        if step % 5 == 0:
            print(f"  步骤 {step}: KF RMSE = {info_kf['rmse']:.4f} m, "
                  f"EnKF RMSE = {info_enkf['rmse']:.4f} m")
    
    rmses_kf = np.array([r['rmse'] for r in results_kf])
    rmses_enkf = np.array([r['rmse'] for r in results_enkf])
    
    print(f"\n对比结果:")
    print(f"  标准KF最终RMSE: {rmses_kf[-1]:.4f} m")
    print(f"  EnKF最终RMSE: {rmses_enkf[-1]:.4f} m")
    print(f"  EnKF改善: {(1 - rmses_enkf[-1]/rmses_kf[-1])*100:.1f}%")
    
    return {
        'dt_kf': dt_kf,
        'dt_enkf': dt_enkf,
        'true_evolution': true_evolution,
        'results_kf': results_kf,
        'results_enkf': results_enkf,
        'rmses_kf': rmses_kf,
        'rmses_enkf': rmses_enkf,
        'obs_system': obs_sys
    }


def experiment4_forecast():
    """
    实验4：实时预测演示
    
    展示数字孪生的预测能力。
    """
    print("\n" + "="*70)
    print("实验4：实时预测演示")
    print("="*70)
    
    # 使用实验2的结果
    exp2_results = experiment2_groundwater_assimilation()
    dt = exp2_results['digital_twin']
    
    # 进行未来预测
    n_forecast = 10
    dt_forecast = 1.0
    
    print(f"\n进行未来 {n_forecast} 步预测...")
    forecasts = dt.forecast(n_forecast, dt_forecast)
    
    print(f"预测完成")
    print(f"  预测步数: {n_forecast}")
    print(f"  预测时长: {n_forecast * dt_forecast:.1f}")
    
    # 不确定性区间
    lower, upper = dt.get_uncertainty_bounds(n_std=2.0)
    
    print(f"\n当前状态不确定性:")
    print(f"  平均不确定性: {np.mean(upper - lower):.4f} m")
    print(f"  最大不确定性: {np.max(upper - lower):.4f} m")
    
    return {
        'digital_twin': dt,
        'forecasts': forecasts,
        'lower_bound': lower,
        'upper_bound': upper,
        'n_forecast': n_forecast
    }


def plot_results(exp1, exp2, exp3, exp4):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(4, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # ==================== 第一行：实验1 ====================
    # 子图1：1D卡尔曼滤波演示
    ax1 = fig.add_subplot(gs[0, 0])
    steps = np.arange(len(exp1['true_states']))
    ax1.plot(steps, exp1['true_states'], 'k-', linewidth=2, label='真实状态')
    ax1.plot(steps, exp1['observations'], 'r.', markersize=8, alpha=0.6, label='观测')
    ax1.plot(steps, exp1['estimates'], 'b-', linewidth=2, label='KF估计')
    ax1.fill_between(steps, 
                     exp1['estimates'] - 2*exp1['uncertainties'],
                     exp1['estimates'] + 2*exp1['uncertainties'],
                     alpha=0.2, color='blue', label='95%置信区间')
    ax1.set_xlabel('时间步')
    ax1.set_ylabel('状态值')
    ax1.set_title('(a) 1D卡尔曼滤波演示')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：卡尔曼增益演化
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(steps, exp1['kalman_gains'], 'g-', linewidth=2)
    ax2.set_xlabel('时间步')
    ax2.set_ylabel('卡尔曼增益')
    ax2.set_title('(b) 卡尔曼增益演化')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    # 子图3：RMSE对比
    ax3 = fig.add_subplot(gs[0, 2])
    categories = ['观测', 'KF估计']
    rmses = [exp1['rmse_obs'], exp1['rmse_est']]
    colors = ['red', 'blue']
    bars = ax3.bar(categories, rmses, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('RMSE')
    ax3.set_title('(c) RMSE对比（1D系统）')
    ax3.grid(True, axis='y', alpha=0.3)
    for bar, rmse in zip(bars, rmses):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{rmse:.4f}', ha='center', va='bottom', fontsize=10)
    
    # ==================== 第二行：实验2 ====================
    # 子图4：初始状态
    ax4 = fig.add_subplot(gs[1, 0])
    h_true_initial = exp2['true_evolution'][0]
    im4 = ax4.contourf(h_true_initial, levels=15, cmap='viridis')
    obs_indices = exp2['obs_system'].get_well_indices()
    for idx, (i, j) in enumerate(obs_indices):
        ax4.plot(j, i, 'ro', markersize=10, markeredgecolor='white', markeredgewidth=2)
    ax4.set_xlabel('x节点')
    ax4.set_ylabel('y节点')
    ax4.set_title('(d) 真实初始水头场 + 监测井')
    plt.colorbar(im4, ax=ax4, label='水头 (m)')
    ax4.set_aspect('equal')
    
    # 子图5：最终估计状态
    ax5 = fig.add_subplot(gs[1, 1])
    h_final_est = exp2['digital_twin'].get_state_2d()
    im5 = ax5.contourf(h_final_est, levels=15, cmap='viridis')
    for idx, (i, j) in enumerate(obs_indices):
        ax5.plot(j, i, 'ro', markersize=10, markeredgecolor='white', markeredgewidth=2)
    ax5.set_xlabel('x节点')
    ax5.set_ylabel('y节点')
    ax5.set_title('(e) KF最终估计水头场')
    plt.colorbar(im5, ax=ax5, label='水头 (m)')
    ax5.set_aspect('equal')
    
    # 子图6：RMSE时间演化
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(exp2['times'], exp2['rmses'], 'b-', linewidth=2, marker='o', markersize=5)
    ax6.set_xlabel('时间')
    ax6.set_ylabel('RMSE (m)')
    ax6.set_title('(f) RMSE时间演化（地下水场）')
    ax6.grid(True, alpha=0.3)
    ax6.axhline(y=exp2['rmses'][0], color='r', linestyle='--', alpha=0.5, label='初始')
    ax6.axhline(y=exp2['rmses'][-1], color='g', linestyle='--', alpha=0.5, label='最终')
    ax6.legend(fontsize=9)
    
    # ==================== 第三行：实验3 ====================
    # 子图7：KF vs EnKF RMSE对比
    ax7 = fig.add_subplot(gs[2, 0])
    steps3 = np.arange(len(exp3['rmses_kf']))
    ax7.plot(steps3, exp3['rmses_kf'], 'b-', linewidth=2, marker='o', 
            markersize=5, label='标准KF')
    ax7.plot(steps3, exp3['rmses_enkf'], 'r-', linewidth=2, marker='s', 
            markersize=5, label='EnKF')
    ax7.set_xlabel('时间步')
    ax7.set_ylabel('RMSE (m)')
    ax7.set_title('(g) KF vs EnKF性能对比')
    ax7.legend(fontsize=10)
    ax7.grid(True, alpha=0.3)
    
    # 子图8：KF最终估计
    ax8 = fig.add_subplot(gs[2, 1])
    h_kf_final = exp3['dt_kf'].get_state_2d()
    im8 = ax8.contourf(h_kf_final, levels=15, cmap='viridis')
    ax8.set_xlabel('x节点')
    ax8.set_ylabel('y节点')
    ax8.set_title(f'(h) 标准KF (RMSE={exp3["rmses_kf"][-1]:.3f}m)')
    plt.colorbar(im8, ax=ax8, label='水头 (m)')
    ax8.set_aspect('equal')
    
    # 子图9：EnKF最终估计
    ax9 = fig.add_subplot(gs[2, 2])
    h_enkf_final = exp3['dt_enkf'].get_state_2d()
    im9 = ax9.contourf(h_enkf_final, levels=15, cmap='viridis')
    ax9.set_xlabel('x节点')
    ax9.set_ylabel('y节点')
    ax9.set_title(f'(i) EnKF (RMSE={exp3["rmses_enkf"][-1]:.3f}m)')
    plt.colorbar(im9, ax=ax9, label='水头 (m)')
    ax9.set_aspect('equal')
    
    # ==================== 第四行：实验4 ====================
    # 子图10：当前状态 + 不确定性
    ax10 = fig.add_subplot(gs[3, 0])
    current_state = exp4['digital_twin'].get_state_2d()
    im10 = ax10.contourf(current_state, levels=15, cmap='viridis')
    ax10.set_xlabel('x节点')
    ax10.set_ylabel('y节点')
    ax10.set_title('(j) 当前状态估计')
    plt.colorbar(im10, ax=ax10, label='水头 (m)')
    ax10.set_aspect('equal')
    
    # 子图11：不确定性场
    ax11 = fig.add_subplot(gs[3, 1])
    uncertainty_2d = (exp4['upper_bound'] - exp4['lower_bound']).reshape(current_state.shape)
    im11 = ax11.contourf(uncertainty_2d, levels=15, cmap='Reds')
    ax11.set_xlabel('x节点')
    ax11.set_ylabel('y节点')
    ax11.set_title('(k) 不确定性场 (95%区间宽度)')
    plt.colorbar(im11, ax=ax11, label='不确定性 (m)')
    ax11.set_aspect('equal')
    
    # 子图12：预测轨迹（某一点）
    ax12 = fig.add_subplot(gs[3, 2])
    # 选择中心点
    ny, nx = current_state.shape
    center_idx = (ny // 2) * nx + (nx // 2)
    current_value = exp4['digital_twin'].current_state[center_idx]
    forecast_values = exp4['forecasts'][:, center_idx]
    
    forecast_steps = np.arange(exp4['n_forecast'])
    ax12.plot([-1], [current_value], 'bo', markersize=10, label='当前状态')
    ax12.plot(forecast_steps, forecast_values, 'r-', linewidth=2, 
             marker='s', markersize=6, label='预测轨迹')
    ax12.axhline(y=current_value, color='b', linestyle='--', alpha=0.3)
    ax12.set_xlabel('预测步数')
    ax12.set_ylabel('水头 (m)')
    ax12.set_title('(l) 中心点预测轨迹')
    ax12.legend(fontsize=9)
    ax12.grid(True, alpha=0.3)
    ax12.set_xlim(-2, exp4['n_forecast'])
    
    plt.suptitle('案例19：地下水数字孪生架构全面演示', 
                fontsize=16, fontweight='bold', y=0.995)
    
    return fig


def main():
    """主函数"""
    print("\n" + "="*70)
    print("案例19：地下水数字孪生架构")
    print("="*70)
    print("\n本案例演示:")
    print("  1. 卡尔曼滤波原理（1D系统）")
    print("  2. 地下水模型数据同化")
    print("  3. 标准KF vs 集合EnKF对比")
    print("  4. 实时预测能力")
    
    # 运行实验
    print("\n" + "="*70)
    print("开始运行实验...")
    print("="*70)
    
    exp1 = experiment1_kalman_1d()
    exp2 = experiment2_groundwater_assimilation()
    exp3 = experiment3_kf_vs_enkf()
    exp4 = experiment4_forecast()
    
    # 绘图
    print("\n" + "="*70)
    print("生成可视化结果...")
    print("="*70)
    
    fig = plot_results(exp1, exp2, exp3, exp4)
    
    # 保存
    output_dir = Path(__file__).parent
    output_path = output_dir / 'case_19_results.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n结果已保存至: {output_path}")
    
    # 打印数字孪生摘要
    print(exp4['digital_twin'].summary())
    
    # 总结
    print("\n" + "="*70)
    print("案例19完成总结")
    print("="*70)
    print("\n核心成果:")
    print(f"  ✓ 卡尔曼滤波误差减少: {(1-exp1['rmse_est']/exp1['rmse_obs'])*100:.1f}%")
    print(f"  ✓ 地下水场同化RMSE: {exp2['rmses'][-1]:.4f} m")
    print(f"  ✓ EnKF相对KF改善: {(1-exp3['rmses_enkf'][-1]/exp3['rmses_kf'][-1])*100:.1f}%")
    print(f"  ✓ 成功预测未来 {exp4['n_forecast']} 步")
    
    print("\n数字孪生核心能力:")
    print("  ✓ 实时状态估计")
    print("  ✓ 数据同化")
    print("  ✓ 不确定性量化")
    print("  ✓ 未来预测")
    
    print("\n应用场景:")
    print("  • 地下水实时监测")
    print("  • 水位预警")
    print("  • 开采方案优化")
    print("  • 智能调度决策")
    
    plt.show()


if __name__ == "__main__":
    main()
