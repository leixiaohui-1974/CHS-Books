"""
案例24：流域数字孪生系统
========================

演示流域数字孪生系统，实现物理流域与数字流域的
实时映射、状态同步、预测预警和智能决策。

核心内容：
1. 实时数据接入
2. 模型实时运行
3. 状态更新与同化
4. 可视化监控
5. 预警决策支持

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
import os
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RealTimeDataSource:
    """实时数据源（模拟）"""
    
    def __init__(self, n_stations: int = 5):
        """
        初始化数据源
        
        Parameters
        ----------
        n_stations : int
            雨量站数量
        """
        self.n_stations = n_stations
        self.current_time = 0
        
        # 生成真实数据（模拟）
        self._generate_true_data()
    
    def _generate_true_data(self):
        """生成真实数据序列"""
        n_steps = 120
        
        # 降雨（包含洪峰）
        self.true_rainfall = np.ones((self.n_stations, n_steps)) * 3.0
        for s in range(self.n_stations):
            # 添加随机性
            self.true_rainfall[s, :] += np.random.normal(0, 1, n_steps)
            
            # 添加洪峰
            flood_start = 30 + s * 2
            for t in range(flood_start, min(flood_start + 15, n_steps)):
                self.true_rainfall[s, t] += 25 * np.exp(-((t - flood_start - 7) / 3)**2)
        
        # 确保非负
        self.true_rainfall = np.maximum(self.true_rainfall, 0)
        
        # 流量观测（稍后由模型生成）
        self.true_discharge = None
    
    def get_rainfall(self, time_step: int) -> np.ndarray:
        """获取降雨观测"""
        if time_step < len(self.true_rainfall[0]):
            # 添加观测噪声
            noise = np.random.normal(0, 0.5, self.n_stations)
            return self.true_rainfall[:, time_step] + noise
        return np.zeros(self.n_stations)
    
    def get_discharge(self, time_step: int) -> float:
        """获取流量观测"""
        if self.true_discharge is not None and time_step < len(self.true_discharge):
            # 添加观测噪声
            noise = np.random.normal(0, 0.5)
            return self.true_discharge[time_step] + noise
        return None


class DigitalTwinModel:
    """数字孪生模型"""
    
    def __init__(self, xaj_params: Dict, area: float):
        """
        初始化数字孪生模型
        
        Parameters
        ----------
        xaj_params : dict
            新安江模型参数
        area : float
            流域面积 (km²)
        """
        self.xaj_params = xaj_params
        self.area = area
        
        # 创建模型集合（用于EnKF）
        self.n_ensemble = 30
        self.models = [XinAnJiangModel(xaj_params.copy()) for _ in range(self.n_ensemble)]
        
        # 观测误差
        self.obs_error = 0.5
        
        # 状态历史
        self.discharge_history = []
        self.discharge_ensemble_history = []
        self.rainfall_history = []
        
        # 预警阈值
        self.warning_threshold = 20.0
        self.alert_threshold = 30.0
    
    def run_timestep(self, rainfall: np.ndarray, evaporation: float,
                    observation: float = None) -> Dict:
        """
        运行一个时间步
        
        Parameters
        ----------
        rainfall : np.ndarray
            降雨 (mm)
        evaporation : float
            蒸发 (mm)
        observation : float
            流量观测 (m³/s)，用于同化
            
        Returns
        -------
        result : dict
            运行结果
        """
        # 平均降雨
        avg_rainfall = np.mean(rainfall)
        self.rainfall_history.append(avg_rainfall)
        
        # 运行模型集合
        discharges = []
        for model in self.models:
            result = model.run(np.array([avg_rainfall]), np.array([evaporation]))
            Q = result['Q'][0]
            Q = np.nan_to_num(Q, nan=0.0, posinf=0.0, neginf=0.0)
            Q = max(Q, 0.0)
            discharges.append(Q)
        
        discharges = np.array(discharges)
        
        # 数据同化（如果有观测）
        if observation is not None:
            # 简化的EnKF更新
            discharges = self._enkf_update(discharges, observation)
        
        # 完成时间步
        return self._finalize_timestep(discharges)
    
    def _enkf_update(self, forecast: np.ndarray, observation: float) -> np.ndarray:
        """
        简化的EnKF更新
        
        Parameters
        ----------
        forecast : np.ndarray
            预报集合
        observation : float
            观测值
            
        Returns
        -------
        analysis : np.ndarray
            分析集合
        """
        # 计算集合平均和协方差
        mean_forecast = np.mean(forecast)
        
        # 背景误差协方差（集合方差）
        P_f = np.var(forecast)
        
        # 卡尔曼增益
        K = P_f / (P_f + self.obs_error**2)
        
        # 更新集合成员
        analysis = np.zeros_like(forecast)
        for i in range(len(forecast)):
            # 添加观测扰动
            obs_perturbed = observation + np.random.normal(0, self.obs_error)
            # 更新
            analysis[i] = forecast[i] + K * (obs_perturbed - forecast[i])
        
        return analysis
    
    def _finalize_timestep(self, discharges: np.ndarray) -> Dict:
        """完成时间步，计算统计量"""
        # 集合平均
        mean_discharge = np.mean(discharges)
        std_discharge = np.std(discharges)
        
        self.discharge_history.append(mean_discharge)
        self.discharge_ensemble_history.append(discharges.copy())
        
        # 预警判断
        warning_level = self._check_warning(mean_discharge)
        
        return {
            'discharge_mean': mean_discharge,
            'discharge_std': std_discharge,
            'discharge_ensemble': discharges,
            'warning_level': warning_level
        }
    
    def _check_warning(self, discharge: float) -> str:
        """检查预警等级"""
        if discharge >= self.alert_threshold:
            return '红色预警'
        elif discharge >= self.warning_threshold:
            return '黄色预警'
        else:
            return '正常'
    
    def forecast(self, rainfall_forecast: np.ndarray, 
                evaporation_forecast: np.ndarray, lead_time: int) -> Dict:
        """
        预报未来
        
        Parameters
        ----------
        rainfall_forecast : np.ndarray
            降雨预报 (lead_time,)
        evaporation_forecast : np.ndarray
            蒸发预报 (lead_time,)
        lead_time : int
            预见期
            
        Returns
        -------
        forecast : dict
            预报结果
        """
        # 保存当前模型状态
        saved_states = [model.state.copy() for model in self.models]
        
        # 运行预报
        forecast_discharge = np.zeros((self.n_ensemble, lead_time))
        
        for i, model in enumerate(self.models):
            for t in range(lead_time):
                result = model.run(
                    np.array([rainfall_forecast[t]]),
                    np.array([evaporation_forecast[t]])
                )
                Q = result['Q'][0]
                Q = np.nan_to_num(Q, nan=0.0, posinf=0.0, neginf=0.0)
                Q = max(Q, 0.0)
                forecast_discharge[i, t] = Q
        
        # 恢复模型状态
        for model, state in zip(self.models, saved_states):
            model.state = state.copy()
        
        # 统计
        mean_forecast = np.mean(forecast_discharge, axis=0)
        std_forecast = np.std(forecast_discharge, axis=0)
        
        # 预警判断
        max_discharge = np.max(mean_forecast)
        forecast_warning = self._check_warning(max_discharge)
        
        return {
            'discharge_mean': mean_forecast,
            'discharge_std': std_forecast,
            'discharge_ensemble': forecast_discharge,
            'warning_level': forecast_warning,
            'peak_time': np.argmax(mean_forecast),
            'peak_value': max_discharge
        }


def run_digital_twin():
    """运行数字孪生系统"""
    print("\n" + "="*70)
    print("案例24：流域数字孪生系统")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 初始化系统
    print("1. 初始化数字孪生系统...")
    
    # 数据源
    data_source = RealTimeDataSource(n_stations=5)
    
    # XAJ参数
    xaj_params = {
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
    
    # 数字孪生模型
    twin_model = DigitalTwinModel(xaj_params, area=1000.0)
    
    print(f"   雨量站数量: {data_source.n_stations}")
    print(f"   集合成员数: {twin_model.n_ensemble}")
    print(f"   黄色预警阈值: {twin_model.warning_threshold} m³/s")
    print(f"   红色预警阈值: {twin_model.alert_threshold} m³/s\n")
    
    # 2. 生成"真实"流量（作为观测）
    print("2. 生成真实观测...")
    true_model = XinAnJiangModel(xaj_params)
    true_discharges = []
    evaporation = 4.0
    
    for t in range(len(data_source.true_rainfall[0])):
        avg_rainfall = np.mean(data_source.true_rainfall[:, t])
        result = true_model.run(np.array([avg_rainfall]), np.array([evaporation]))
        Q = result['Q'][0]
        Q = np.nan_to_num(Q, nan=0.0, posinf=0.0, neginf=0.0)
        Q = max(Q, 0.0)
        true_discharges.append(Q)
    
    data_source.true_discharge = np.array(true_discharges)
    
    print(f"   模拟时长: {len(true_discharges)} 小时")
    print(f"   最大流量: {np.max(true_discharges):.1f} m³/s\n")
    
    # 3. 实时运行（前60小时，有观测同化）
    print("3. 实时运行（数据同化）...")
    n_realtime = 60
    
    for t in range(n_realtime):
        # 获取实时数据
        rainfall = data_source.get_rainfall(t)
        observation = data_source.get_discharge(t)
        
        # 运行时间步
        result = twin_model.run_timestep(rainfall, evaporation, observation)
        
        # 显示预警
        if result['warning_level'] != '正常':
            print(f"   t={t}h: {result['warning_level']}! "
                  f"流量={result['discharge_mean']:.1f}±{result['discharge_std']:.1f} m³/s")
    
    print(f"   实时运行完成\n")
    
    # 4. 预报模式（60-120小时，无观测）
    print("4. 预报模式（无同化）...")
    
    for t in range(n_realtime, len(true_discharges)):
        # 获取降雨（无流量观测）
        rainfall = data_source.get_rainfall(t)
        
        # 运行时间步（无同化）
        result = twin_model.run_timestep(rainfall, evaporation, observation=None)
    
    print(f"   预报运行完成\n")
    
    # 5. 超前预报（从t=60时刻）
    print("5. 超前预报...")
    lead_time = 24
    
    # 生成预报降雨（简化：使用真实值+扰动）
    forecast_rainfall = []
    forecast_evap = []
    for t in range(n_realtime, n_realtime + lead_time):
        if t < len(data_source.true_rainfall[0]):
            rain = np.mean(data_source.true_rainfall[:, t])
            rain += np.random.normal(0, 2.0)  # 预报误差
            forecast_rainfall.append(max(rain, 0))
        else:
            forecast_rainfall.append(3.0)
        forecast_evap.append(evaporation)
    
    forecast_rainfall = np.array(forecast_rainfall)
    forecast_evap = np.array(forecast_evap)
    
    # 执行预报
    forecast_result = twin_model.forecast(forecast_rainfall, forecast_evap, lead_time)
    
    print(f"   预见期: {lead_time} 小时")
    print(f"   预报峰值: {forecast_result['peak_value']:.1f} m³/s")
    print(f"   峰现时间: {forecast_result['peak_time']} 小时后")
    print(f"   预警等级: {forecast_result['warning_level']}\n")
    
    # 6. 结果统计
    print("="*70)
    print("数字孪生系统性能评估")
    print("="*70)
    
    # 同化阶段（0-60h）
    obs_period = true_discharges[:n_realtime]
    sim_period = np.array(twin_model.discharge_history[:n_realtime])
    
    rmse_assim = np.sqrt(np.mean((obs_period - sim_period)**2))
    nse_assim = 1 - np.sum((obs_period - sim_period)**2) / \
                    np.sum((obs_period - np.mean(obs_period))**2)
    
    print(f"\n【同化阶段 (0-{n_realtime}h)】")
    print(f"  RMSE: {rmse_assim:.2f} m³/s")
    print(f"  NSE:  {nse_assim:.4f}")
    
    # 预报阶段（60-120h）
    obs_forecast = true_discharges[n_realtime:]
    sim_forecast = np.array(twin_model.discharge_history[n_realtime:])
    
    rmse_forecast = np.sqrt(np.mean((obs_forecast - sim_forecast)**2))
    nse_forecast = 1 - np.sum((obs_forecast - sim_forecast)**2) / \
                       np.sum((obs_forecast - np.mean(obs_forecast))**2)
    
    print(f"\n【预报阶段 ({n_realtime}-120h)】")
    print(f"  RMSE: {rmse_forecast:.2f} m³/s")
    print(f"  NSE:  {nse_forecast:.4f}")
    
    # 7. 可视化
    print(f"\n6. 生成数字孪生监控面板...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, hspace=0.4, wspace=0.3)
    
    time = np.arange(len(true_discharges))
    
    # 图1: 实时流量监控（带不确定性）
    ax1 = fig.add_subplot(gs[0, :])
    
    # 真实观测
    ax1.plot(time, true_discharges, 'k-', linewidth=2, label='真实观测', alpha=0.8)
    
    # 数字孪生模拟
    sim_discharge = np.array(twin_model.discharge_history)
    ax1.plot(time[:len(sim_discharge)], sim_discharge, 'b-', linewidth=2, 
            label='数字孪生', alpha=0.8)
    
    # 不确定性区间（±2σ）
    ensemble_history = twin_model.discharge_ensemble_history
    if len(ensemble_history) > 0:
        ensemble_array = np.array(ensemble_history)
        mean = np.mean(ensemble_array, axis=1)
        std = np.std(ensemble_array, axis=1)
        ax1.fill_between(time[:len(mean)], mean - 2*std, mean + 2*std,
                        color='blue', alpha=0.2, label='95%置信区间')
    
    # 预报区间
    forecast_time = np.arange(n_realtime, n_realtime + lead_time)
    ax1.plot(forecast_time, forecast_result['discharge_mean'], 'r--',
            linewidth=2, label='超前预报', alpha=0.8)
    
    # 预警阈值
    ax1.axhline(y=twin_model.warning_threshold, color='orange', 
               linestyle='--', linewidth=1, label='黄色预警')
    ax1.axhline(y=twin_model.alert_threshold, color='red',
               linestyle='--', linewidth=1, label='红色预警')
    
    # 标记同化/预报分界
    ax1.axvline(x=n_realtime, color='gray', linestyle=':', linewidth=2,
               label='同化↔预报')
    
    ax1.set_xlabel('时间 (h)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=11)
    ax1.set_title('实时流量监控与预报', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9, ncol=3, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 图2: 降雨过程
    ax2 = fig.add_subplot(gs[1, 0])
    avg_rainfall = [np.mean(data_source.true_rainfall[:, t]) 
                   for t in range(len(data_source.true_rainfall[0]))]
    ax2.bar(time[:len(avg_rainfall)], avg_rainfall, color='blue', alpha=0.6, width=1.0)
    ax2.axvline(x=n_realtime, color='gray', linestyle=':', linewidth=2)
    ax2.set_xlabel('时间 (h)', fontsize=10)
    ax2.set_ylabel('降雨 (mm/h)', fontsize=10)
    ax2.set_title('降雨过程', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 图3: 误差演变
    ax3 = fig.add_subplot(gs[1, 1])
    errors = true_discharges[:len(sim_discharge)] - sim_discharge
    ax3.plot(time[:len(errors)], errors, 'r-', linewidth=1, alpha=0.7)
    ax3.axhline(y=0, color='k', linestyle='--', linewidth=1)
    ax3.axvline(x=n_realtime, color='gray', linestyle=':', linewidth=2)
    ax3.set_xlabel('时间 (h)', fontsize=10)
    ax3.set_ylabel('误差 (m³/s)', fontsize=10)
    ax3.set_title('模拟误差', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 图4: 集合散点（实时）
    ax4 = fig.add_subplot(gs[1, 2])
    if len(ensemble_history) > 0:
        # 选择几个时刻展示集合
        sample_times = [20, 40, 60, 80, 100]
        for st in sample_times:
            if st < len(ensemble_history):
                ensemble = ensemble_history[st]
                ax4.scatter([st]*len(ensemble), ensemble, alpha=0.5, s=20)
    
    ax4.plot(time[:len(sim_discharge)], sim_discharge, 'b-', linewidth=2, alpha=0.7)
    ax4.axvline(x=n_realtime, color='gray', linestyle=':', linewidth=2)
    ax4.set_xlabel('时间 (h)', fontsize=10)
    ax4.set_ylabel('流量 (m³/s)', fontsize=10)
    ax4.set_title('集合预报散点', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 图5: 累积误差
    ax5 = fig.add_subplot(gs[2, 0])
    cumulative_error_assim = np.cumsum(np.abs(obs_period - sim_period))
    cumulative_error_forecast = np.cumsum(np.abs(obs_forecast - sim_forecast))
    
    ax5.plot(time[:n_realtime], cumulative_error_assim, 'b-',
            linewidth=2, label='同化阶段')
    ax5.plot(time[n_realtime:n_realtime+len(cumulative_error_forecast)],
            cumulative_error_forecast + cumulative_error_assim[-1], 'r-',
            linewidth=2, label='预报阶段')
    ax5.set_xlabel('时间 (h)', fontsize=10)
    ax5.set_ylabel('累积绝对误差 (m³/s)', fontsize=10)
    ax5.set_title('累积误差', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 预报技巧
    ax6 = fig.add_subplot(gs[2, 1])
    metrics_names = ['RMSE\n(同化)', 'RMSE\n(预报)', 'NSE\n(同化)', 'NSE\n(预报)']
    metrics_values = [rmse_assim, rmse_forecast, nse_assim*10, nse_forecast*10]
    colors = ['blue', 'red', 'blue', 'red']
    
    bars = ax6.bar(metrics_names, metrics_values, color=colors, alpha=0.6,
                  edgecolor='black')
    ax6.set_ylabel('指标值', fontsize=10)
    ax6.set_title('性能指标对比', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar, val in zip(bars, metrics_values):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 图7: 预警时间轴
    ax7 = fig.add_subplot(gs[2, 2])
    
    # 计算预警状态
    warning_status = np.zeros(len(true_discharges))
    for t, Q in enumerate(true_discharges):
        if Q >= twin_model.alert_threshold:
            warning_status[t] = 2  # 红色
        elif Q >= twin_model.warning_threshold:
            warning_status[t] = 1  # 黄色
        else:
            warning_status[t] = 0  # 正常
    
    # 绘制预警状态
    colors_map = ['green', 'yellow', 'red']
    for level in [0, 1, 2]:
        mask = warning_status == level
        ax7.fill_between(time, 0, 1, where=mask, color=colors_map[level],
                        alpha=0.5, transform=ax7.get_xaxis_transform())
    
    ax7.plot(time, true_discharges / np.max(true_discharges), 'k-',
            linewidth=2, alpha=0.7, label='流量（归一化）')
    ax7.axvline(x=n_realtime, color='gray', linestyle=':', linewidth=2)
    ax7.set_xlabel('时间 (h)', fontsize=10)
    ax7.set_ylabel('归一化流量', fontsize=10)
    ax7.set_title('预警时间轴', fontsize=12, fontweight='bold')
    ax7.legend(fontsize=9)
    ax7.set_ylim([0, 1.1])
    
    plt.savefig(f'{output_dir}/digital_twin.png',
                dpi=300, bbox_inches='tight')
    print(f"   监控面板已保存: {output_dir}/digital_twin.png")
    plt.close()
    
    print(f"\n监控面板已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_digital_twin()
