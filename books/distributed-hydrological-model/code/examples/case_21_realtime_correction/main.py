"""
案例21：实时校正模型
===================

演示洪水预报的实时误差校正技术，
包括自回归校正、卡尔曼滤波校正、自适应参数更新。

核心内容：
1. 误差自回归（AR）模型
2. 卡尔曼滤波校正
from pathlib import Path
3. 自适应参数更新
4. 多方法对比
5. 预报精度评估

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from typing import Dict, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ARErrorCorrection:
    """误差自回归校正模型"""
    
    def __init__(self, order: int = 3):
        """
        初始化AR模型
        
        Parameters
        ----------
        order : int
            自回归阶数
        """
        self.order = order
        self.coefficients = None
        self.error_history = []
    
    def fit(self, errors: np.ndarray):
        """
        拟合AR模型
        
        Parameters
        ----------
        errors : np.ndarray
            历史误差序列
        """
        n = len(errors)
        if n < self.order + 1:
            # 数据不足，使用简单平均
            self.coefficients = np.ones(self.order) / self.order
            return
        
        # 构建设计矩阵
        X = np.zeros((n - self.order, self.order))
        y = errors[self.order:]
        
        for i in range(self.order):
            X[:, i] = errors[self.order - i - 1:n - i - 1]
        
        # 最小二乘拟合
        try:
            self.coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
        except:
            # 拟合失败，使用等权重
            self.coefficients = np.ones(self.order) / self.order
    
    def predict(self, recent_errors: np.ndarray) -> float:
        """
        预测下一时刻误差
        
        Parameters
        ----------
        recent_errors : np.ndarray
            最近的误差序列
            
        Returns
        -------
        predicted_error : float
            预测误差
        """
        if self.coefficients is None or len(recent_errors) < self.order:
            return 0.0
        
        # 使用最近的order个误差
        recent = recent_errors[-self.order:]
        predicted = np.sum(self.coefficients * recent[::-1])
        
        return predicted
    
    def correct(self, forecast: float, recent_errors: np.ndarray) -> float:
        """
        校正预报值
        
        Parameters
        ----------
        forecast : float
            原始预报值
        recent_errors : np.ndarray
            最近的误差序列
            
        Returns
        -------
        corrected : float
            校正后的预报值
        """
        error_pred = self.predict(recent_errors)
        corrected = forecast + error_pred
        return np.maximum(corrected, 0.0)  # 确保非负


class KalmanFilterCorrection:
    """卡尔曼滤波校正模型"""
    
    def __init__(self, process_variance: float = 0.1, 
                 measurement_variance: float = 1.0):
        """
        初始化卡尔曼滤波器
        
        Parameters
        ----------
        process_variance : float
            过程噪声方差（Q）
        measurement_variance : float
            测量噪声方差（R）
        """
        self.Q = process_variance  # 过程噪声
        self.R = measurement_variance  # 测量噪声
        
        # 状态估计（误差）
        self.x = 0.0  # 误差估计
        self.P = 1.0  # 估计误差协方差
    
    def update(self, observation: float, forecast: float):
        """
        更新卡尔曼滤波器
        
        Parameters
        ----------
        observation : float
            实测值
        forecast : float
            预报值
        """
        # 预测误差
        error = observation - forecast
        
        # 预测步
        x_pred = self.x
        P_pred = self.P + self.Q
        
        # 更新步
        K = P_pred / (P_pred + self.R)  # 卡尔曼增益
        self.x = x_pred + K * (error - x_pred)
        self.P = (1 - K) * P_pred
    
    def correct(self, forecast: float) -> float:
        """
        校正预报值
        
        Parameters
        ----------
        forecast : float
            原始预报值
            
        Returns
        -------
        corrected : float
            校正后的预报值
        """
        corrected = forecast + self.x
        return np.maximum(corrected, 0.0)


class AdaptiveParameterUpdater:
    """自适应参数更新器"""
    
    def __init__(self, learning_rate: float = 0.01):
        """
        初始化参数更新器
        
        Parameters
        ----------
        learning_rate : float
            学习率
        """
        self.learning_rate = learning_rate
        self.parameter_history = {}
    
    def update(self, param_name: str, current_value: float,
               gradient: float) -> float:
        """
        更新参数
        
        Parameters
        ----------
        param_name : str
            参数名称
        current_value : float
            当前参数值
        gradient : float
            梯度（误差对参数的导数）
            
        Returns
        -------
        updated_value : float
            更新后的参数值
        """
        # 简单的梯度下降
        new_value = current_value - self.learning_rate * gradient
        
        # 记录历史
        if param_name not in self.parameter_history:
            self.parameter_history[param_name] = []
        self.parameter_history[param_name].append(new_value)
        
        return new_value


def run_forecast_with_correction():
    """运行带校正的洪水预报"""
    print("\n" + "="*70)
    print("案例21：实时校正模型")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 准备数据
    print("1. 生成模拟数据...")
    n_days = 120
    np.random.seed(42)
    
    # 生成降雨（包含几次洪水过程）
    rainfall = np.ones(n_days) * 5.0
    rainfall += 3.0 * np.sin(2 * np.pi * np.arange(n_days) / 30)
    
    # 添加洪峰
    flood_days = [20, 50, 80]
    for day in flood_days:
        for i in range(10):
            if day + i < n_days:
                rainfall[day + i] += 40 * np.exp(-((i - 5) / 2)**2)
    
    # 蒸发
    evaporation = np.ones(n_days) * 3.0
    evaporation += 1.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    
    print(f"   时间步数: {n_days} 天")
    print(f"   最大降雨: {np.max(rainfall):.1f} mm/day\n")
    
    # 2. 生成"真实"观测值（用稍微不同的参数）
    print("2. 生成真实观测值...")
    
    # "真实"模型参数
    true_params = {
        'K': 0.8,
        'UM': 20.0,
        'LM': 80.0,
        'C': 0.18,
        'WM': 120.0,
        'B': 0.40,
        'IM': 0.02,
        'SM': 30.0,
        'EX': 1.2,
        'KG': 0.45,
        'KI': 0.35,
        'CG': 0.98,
        'CI': 0.70,
        'CS': 0.85
    }
    
    true_model = XinAnJiangModel(true_params)
    true_results = true_model.run(rainfall, evaporation)
    observed_flow = true_results['Q']
    observed_flow = np.nan_to_num(observed_flow, nan=0.0, posinf=0.0, neginf=0.0)
    observed_flow = np.maximum(observed_flow, 0.0)
    
    # 添加观测噪声
    obs_noise = np.random.normal(0, 2.0, n_days)
    observed_flow = np.maximum(observed_flow + obs_noise, 0.0)
    
    print(f"   最大流量: {np.max(observed_flow):.1f} m³/s\n")
    
    # 3. 预报模型（参数有偏差）
    print("3. 设置预报模型（参数有偏差）...")
    
    # 预报模型参数（与真实值有偏差）
    forecast_params = {
        'K': 0.8,
        'UM': 20.0,
        'LM': 80.0,
        'C': 0.15,        # 偏低
        'WM': 110.0,      # 偏低
        'B': 0.35,        # 偏低
        'IM': 0.02,
        'SM': 30.0,
        'EX': 1.2,
        'KG': 0.40,       # 偏低
        'KI': 0.35,
        'CG': 0.98,
        'CI': 0.70,
        'CS': 0.85
    }
    
    forecast_model = XinAnJiangModel(forecast_params)
    
    print("   参数偏差：")
    print(f"     WM: {forecast_params['WM']} vs {true_params['WM']} (偏低)")
    print(f"     B:  {forecast_params['B']} vs {true_params['B']} (偏低)")
    print(f"     KG: {forecast_params['KG']} vs {true_params['KG']} (偏低)")
    print(f"     C:  {forecast_params['C']} vs {true_params['C']} (偏低)\n")
    
    # 4. 运行不同的预报方案
    print("4. 运行多种预报方案...")
    
    # 4.1 无校正预报（基准）
    print("   4.1 无校正预报...")
    baseline_results = forecast_model.run(rainfall, evaporation)
    baseline_flow = baseline_results['Q']
    baseline_flow = np.nan_to_num(baseline_flow, nan=0.0, posinf=0.0, neginf=0.0)
    baseline_flow = np.maximum(baseline_flow, 0.0)
    
    # 4.2 AR校正预报
    print("   4.2 AR误差校正预报...")
    ar_corrector = ARErrorCorrection(order=3)
    ar_corrected_flow = np.zeros(n_days)
    ar_errors = []
    
    warmup_period = 10  # 前10天用于预热
    
    for t in range(n_days):
        if t < warmup_period:
            # 预热期：使用原始预报，积累误差
            ar_corrected_flow[t] = baseline_flow[t]
            error = observed_flow[t] - baseline_flow[t]
            ar_errors.append(error)
        else:
            # 正式预报期：使用AR校正
            # 每5天重新拟合一次AR模型
            if (t - warmup_period) % 5 == 0:
                ar_corrector.fit(np.array(ar_errors))
            
            # 校正预报
            ar_corrected_flow[t] = ar_corrector.correct(
                baseline_flow[t], 
                np.array(ar_errors)
            )
            
            # 更新误差历史（使用实测值）
            error = observed_flow[t] - baseline_flow[t]
            ar_errors.append(error)
    
    # 4.3 卡尔曼滤波校正
    print("   4.3 卡尔曼滤波校正预报...")
    kf_corrector = KalmanFilterCorrection(process_variance=0.5, 
                                         measurement_variance=2.0)
    kf_corrected_flow = np.zeros(n_days)
    
    for t in range(n_days):
        if t < warmup_period:
            # 预热期
            kf_corrected_flow[t] = baseline_flow[t]
            kf_corrector.update(observed_flow[t], baseline_flow[t])
        else:
            # 正式预报期
            kf_corrected_flow[t] = kf_corrector.correct(baseline_flow[t])
            kf_corrector.update(observed_flow[t], baseline_flow[t])
    
    print("   完成\n")
    
    # 5. 精度评估
    print("="*70)
    print("预报精度评估（预热期后）")
    print("="*70)
    
    eval_period = slice(warmup_period, n_days)
    obs_eval = observed_flow[eval_period]
    
    def evaluate(forecast, observed, name):
        """评估预报精度"""
        # 均方根误差
        rmse = np.sqrt(np.mean((forecast - observed)**2))
        
        # 平均绝对误差
        mae = np.mean(np.abs(forecast - observed))
        
        # 相对误差
        re = np.abs(np.sum(forecast) - np.sum(observed)) / np.sum(observed) * 100
        
        # 峰值误差
        peak_obs = np.max(observed)
        peak_for = np.max(forecast)
        peak_error = np.abs(peak_for - peak_obs) / peak_obs * 100
        
        # 相关系数
        corr = np.corrcoef(forecast, observed)[0, 1]
        
        # Nash-Sutcliffe效率系数
        nse = 1 - np.sum((observed - forecast)**2) / \
                  np.sum((observed - np.mean(observed))**2)
        
        print(f"\n【{name}】")
        print(f"  RMSE:         {rmse:.2f} m³/s")
        print(f"  MAE:          {mae:.2f} m³/s")
        print(f"  相对误差:      {re:.2f}%")
        print(f"  峰值误差:      {peak_error:.2f}%")
        print(f"  相关系数:      {corr:.4f}")
        print(f"  NSE:          {nse:.4f}")
        
        return {
            'rmse': rmse,
            'mae': mae,
            're': re,
            'peak_error': peak_error,
            'corr': corr,
            'nse': nse
        }
    
    baseline_metrics = evaluate(baseline_flow[eval_period], obs_eval, "无校正预报")
    ar_metrics = evaluate(ar_corrected_flow[eval_period], obs_eval, "AR校正预报")
    kf_metrics = evaluate(kf_corrected_flow[eval_period], obs_eval, "卡尔曼滤波校正")
    
    # 改进百分比
    print(f"\n{'='*70}")
    print("校正效果（相对基准的改进）")
    print("="*70)
    
    print(f"\n【AR校正】")
    print(f"  RMSE改进:     {(baseline_metrics['rmse'] - ar_metrics['rmse']) / baseline_metrics['rmse'] * 100:.1f}%")
    print(f"  MAE改进:      {(baseline_metrics['mae'] - ar_metrics['mae']) / baseline_metrics['mae'] * 100:.1f}%")
    print(f"  峰值误差改进:  {(baseline_metrics['peak_error'] - ar_metrics['peak_error']):.1f}%")
    print(f"  NSE改进:      {(ar_metrics['nse'] - baseline_metrics['nse']):.4f}")
    
    print(f"\n【卡尔曼滤波校正】")
    print(f"  RMSE改进:     {(baseline_metrics['rmse'] - kf_metrics['rmse']) / baseline_metrics['rmse'] * 100:.1f}%")
    print(f"  MAE改进:      {(baseline_metrics['mae'] - kf_metrics['mae']) / baseline_metrics['mae'] * 100:.1f}%")
    print(f"  峰值误差改进:  {(baseline_metrics['peak_error'] - kf_metrics['peak_error']):.1f}%")
    print(f"  NSE改进:      {(kf_metrics['nse'] - baseline_metrics['nse']):.4f}")
    
    # 6. 可视化
    print(f"\n5. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    
    time = np.arange(n_days)
    
    # 图1：全过程对比
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time, observed_flow, 'k-', linewidth=2, label='实测流量', alpha=0.8)
    ax1.plot(time, baseline_flow, 'b--', linewidth=1.5, label='无校正预报', alpha=0.7)
    ax1.plot(time, ar_corrected_flow, 'r-', linewidth=1.5, label='AR校正', alpha=0.8)
    ax1.plot(time, kf_corrected_flow, 'g-', linewidth=1.5, label='卡尔曼滤波校正', alpha=0.8)
    
    # 标记预热期
    ax1.axvspan(0, warmup_period, alpha=0.2, color='gray', label='预热期')
    
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=11)
    ax1.set_title('实时校正预报全过程对比', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 图2：预报误差演变
    ax2 = fig.add_subplot(gs[1, 0])
    baseline_error = baseline_flow - observed_flow
    ar_error = ar_corrected_flow - observed_flow
    kf_error = kf_corrected_flow - observed_flow
    
    ax2.plot(time, baseline_error, 'b-', linewidth=1, label='无校正', alpha=0.7)
    ax2.plot(time, ar_error, 'r-', linewidth=1, label='AR校正', alpha=0.7)
    ax2.plot(time, kf_error, 'g-', linewidth=1, label='卡尔曼滤波', alpha=0.7)
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=1)
    ax2.axvspan(0, warmup_period, alpha=0.2, color='gray')
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('误差 (m³/s)', fontsize=11)
    ax2.set_title('预报误差演变', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3：散点图对比（预热期后）
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.scatter(obs_eval, baseline_flow[eval_period], alpha=0.5, 
               s=30, c='blue', label='无校正')
    ax3.scatter(obs_eval, ar_corrected_flow[eval_period], alpha=0.5, 
               s=30, c='red', label='AR校正')
    ax3.scatter(obs_eval, kf_corrected_flow[eval_period], alpha=0.5, 
               s=30, c='green', label='卡尔曼滤波')
    
    max_val = np.max(obs_eval) * 1.1
    ax3.plot([0, max_val], [0, max_val], 'k--', linewidth=1, alpha=0.5)
    
    ax3.set_xlabel('实测流量 (m³/s)', fontsize=11)
    ax3.set_ylabel('预报流量 (m³/s)', fontsize=11)
    ax3.set_title('预报值 vs 实测值', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.axis('equal')
    ax3.set_xlim([0, max_val])
    ax3.set_ylim([0, max_val])
    
    # 图4：精度指标对比
    ax4 = fig.add_subplot(gs[2, 0])
    metrics_names = ['RMSE', 'MAE', '峰值误差\n(%)', 'NSE×10']
    baseline_vals = [baseline_metrics['rmse'], baseline_metrics['mae'], 
                    baseline_metrics['peak_error'], baseline_metrics['nse']*10]
    ar_vals = [ar_metrics['rmse'], ar_metrics['mae'], 
              ar_metrics['peak_error'], ar_metrics['nse']*10]
    kf_vals = [kf_metrics['rmse'], kf_metrics['mae'], 
              kf_metrics['peak_error'], kf_metrics['nse']*10]
    
    x_pos = np.arange(len(metrics_names))
    width = 0.25
    
    ax4.bar(x_pos - width, baseline_vals, width, label='无校正', 
           color='blue', alpha=0.7)
    ax4.bar(x_pos, ar_vals, width, label='AR校正', 
           color='red', alpha=0.7)
    ax4.bar(x_pos + width, kf_vals, width, label='卡尔曼滤波', 
           color='green', alpha=0.7)
    
    ax4.set_ylabel('指标值', fontsize=11)
    ax4.set_title('精度指标对比', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(metrics_names)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 图5：误差累积分布
    ax5 = fig.add_subplot(gs[2, 1])
    
    abs_errors_baseline = np.abs(baseline_error[eval_period])
    abs_errors_ar = np.abs(ar_error[eval_period])
    abs_errors_kf = np.abs(kf_error[eval_period])
    
    sorted_baseline = np.sort(abs_errors_baseline)
    sorted_ar = np.sort(abs_errors_ar)
    sorted_kf = np.sort(abs_errors_kf)
    
    percentiles = np.linspace(0, 100, len(sorted_baseline))
    
    ax5.plot(sorted_baseline, percentiles, 'b-', linewidth=2, 
            label='无校正', alpha=0.8)
    ax5.plot(sorted_ar, percentiles, 'r-', linewidth=2, 
            label='AR校正', alpha=0.8)
    ax5.plot(sorted_kf, percentiles, 'g-', linewidth=2, 
            label='卡尔曼滤波', alpha=0.8)
    
    ax5.set_xlabel('绝对误差 (m³/s)', fontsize=11)
    ax5.set_ylabel('累积百分比 (%)', fontsize=11)
    ax5.set_title('误差累积分布函数', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    plt.savefig(f'{output_dir}/realtime_correction.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/realtime_correction.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_forecast_with_correction()
