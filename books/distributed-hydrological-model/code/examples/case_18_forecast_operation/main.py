"""
案例18：实时洪水预报调度系统
===========================

演示基于洪水预报的水库实时优化调度，
整合水文预报与水库调度，实现预见期优化。

核心内容：
1. 降雨-径流预报
2. 预见期洪水预报
3. 预报驱动的水库调度
4. 实时更新与滚动优化
5. 调度效果对比评估

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel
from core.reservoir.operation_rules import (
    ReservoirRules, FloodControlRule, ConservationRule
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ForecastSystem:
    """洪水预报系统"""
    
    def __init__(self, hydro_params: dict, lead_time: int = 3):
        """
        初始化预报系统
        
        Parameters
        ----------
        hydro_params : dict
            水文模型参数
        lead_time : int
            预见期（天）
        """
        self.model = XinAnJiangModel(hydro_params)
        self.lead_time = lead_time
    
    def forecast(self, 
                 rainfall_forecast: np.ndarray,
                 evaporation: np.ndarray) -> np.ndarray:
        """
        洪水预报
        
        Parameters
        ----------
        rainfall_forecast : ndarray
            降雨预报序列
        evaporation : ndarray
            蒸发序列
            
        Returns
        -------
        runoff_forecast : ndarray
            径流预报
        """
        # 运行水文模型
        results = self.model.run(rainfall_forecast, evaporation)
        runoff = results['R']
        
        # 处理NaN
        runoff = np.nan_to_num(runoff, nan=0.0)
        runoff = np.maximum(runoff, 0.0)
        
        # 转换为流量 (m³/s)
        # 假设流域面积100km²，时间步长1天
        area = 100.0  # km²
        dt = 86400.0  # s
        
        discharge = runoff * 1e-3 * area * 1e6 / dt
        
        return discharge


class ForecastBasedOperation:
    """基于预报的水库调度"""
    
    def __init__(self, 
                 reservoir: ReservoirRules,
                 forecast_system: ForecastSystem):
        """
        初始化
        
        Parameters
        ----------
        reservoir : ReservoirRules
            水库调度规则
        forecast_system : ForecastSystem
            预报系统
        """
        self.reservoir = reservoir
        self.forecast_system = forecast_system
    
    def operate_with_forecast(self,
                             initial_level: float,
                             observed_inflow: np.ndarray,
                             rainfall_forecast: np.ndarray,
                             evaporation: np.ndarray) -> dict:
        """
        基于预报的实时调度
        
        Parameters
        ----------
        initial_level : float
            初始水位
        observed_inflow : ndarray
            实测入库流量
        rainfall_forecast : ndarray
            降雨预报（滚动预报）
        evaporation : ndarray
            蒸发
            
        Returns
        -------
        results : dict
            调度结果
        """
        n_days = len(observed_inflow)
        lead_time = self.forecast_system.lead_time
        
        # 结果数组
        levels = np.zeros(n_days)
        storages = np.zeros(n_days)
        outflows = np.zeros(n_days)
        forecast_inflow_series = np.zeros((n_days, lead_time))
        
        # 初始状态
        levels[0] = initial_level
        storages[0] = self.reservoir.level_storage_curve(initial_level)
        
        # 逐日调度
        for day in range(n_days - 1):
            # 当前状态
            current_level = levels[day]
            current_storage = storages[day]
            current_inflow = observed_inflow[day]
            
            # 洪水预报
            forecast_start = day
            forecast_end = min(day + lead_time, n_days)
            forecast_length = forecast_end - forecast_start
            
            if forecast_length > 0:
                rainfall_fc = rainfall_forecast[forecast_start:forecast_end]
                evap_fc = evaporation[forecast_start:forecast_end]
                
                # 预报入库流量
                inflow_forecast = self.forecast_system.forecast(
                    rainfall_fc, evap_fc
                )
                forecast_inflow_series[day, :forecast_length] = inflow_forecast
                
                # 预见期最大入库流量
                max_forecast_inflow = np.max(inflow_forecast)
            else:
                max_forecast_inflow = current_inflow
            
            # 基于预报的调度决策
            state = {
                'level': current_level,
                'storage': current_storage,
                'zone': self.reservoir.get_zone(current_level)
            }
            
            # 预见性调度：如果预报有大洪水，提前预泄
            if max_forecast_inflow > current_inflow * 1.5:
                # 加大泄流，腾出库容
                outflow = min(current_inflow * 1.2, 
                            self.reservoir.characteristics['max_outflow'])
            else:
                # 常规调度
                outflow = self.reservoir._select_and_apply_rule(
                    state, current_inflow, day
                )
            
            # 限制出流
            outflow = np.clip(outflow, 0, 
                            self.reservoir.characteristics['max_outflow'])
            outflows[day] = outflow
            
            # 水量平衡
            delta_storage = (current_inflow - outflow) * 86400.0 / 1e4
            new_storage = current_storage + delta_storage
            
            # 限制库容
            new_storage = np.clip(
                new_storage,
                self.reservoir.characteristics['dead_storage'],
                self.reservoir.characteristics['total_storage']
            )
            storages[day + 1] = new_storage
            
            # 反算水位
            levels[day + 1] = self.reservoir._storage_to_level(new_storage)
        
        # 最后一天
        outflows[-1] = outflows[-2]
        
        return {
            'level': levels,
            'storage': storages,
            'outflow': outflows,
            'forecast_inflow': forecast_inflow_series,
            'observed_inflow': observed_inflow
        }


def run_forecast_operation():
    """运行实时预报调度"""
    print("\n" + "="*70)
    print("案例18：实时洪水预报调度系统")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 设置水文模型
    print("1. 设置水文预报模型...")
    hydro_params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    
    forecast_system = ForecastSystem(hydro_params, lead_time=3)
    print(f"   预见期: {forecast_system.lead_time} 天\n")
    
    # 2. 设置水库
    print("2. 设置水库特征...")
    reservoir = ReservoirRules()
    reservoir.set_characteristics(
        dead_level=95.0,
        normal_level=108.0,
        flood_limit_level=113.0,
        design_flood_level=118.0,
        max_level=122.0,
        dead_storage=500.0,
        total_storage=8000.0,
        max_outflow=600.0
    )
    
    # 添加规则
    reservoir.add_rule(FloodControlRule(113.0, 118.0, 600.0))
    reservoir.add_rule(ConservationRule(108.0, 95.0, 20.0, 80.0))
    print("   水库调度规则已设置\n")
    
    # 3. 生成降雨和入流
    print("3. 生成降雨和入流过程...")
    n_days = 60
    
    # 降雨过程
    rainfall = np.ones(n_days) * 5.0
    rainfall[20:26] = [10, 25, 40, 35, 20, 10]  # 第一场暴雨
    rainfall[40:46] = [15, 35, 50, 45, 25, 15]  # 第二场暴雨
    
    # 蒸发
    evaporation = np.ones(n_days) * 3.0
    
    # 实测入库流量（基于降雨生成）
    observed_inflow = np.ones(n_days) * 50.0
    observed_inflow[21:28] = [80, 150, 250, 200, 120, 80, 60]
    observed_inflow[41:48] = [100, 200, 350, 300, 180, 100, 70]
    
    print(f"   时间步数: {n_days} 天")
    print(f"   最大入流: {np.max(observed_inflow):.0f} m³/s\n")
    
    # 4. 情景对比：有预报 vs 无预报
    print("4. 运行对比调度...\n")
    
    # 情景1：基于预报的调度
    print("   情景1: 基于预报的调度...")
    forecast_op = ForecastBasedOperation(reservoir, forecast_system)
    results_forecast = forecast_op.operate_with_forecast(
        initial_level=108.0,
        observed_inflow=observed_inflow,
        rainfall_forecast=rainfall,
        evaporation=evaporation
    )
    
    # 情景2：常规调度（无预报）
    print("   情景2: 常规调度（无预报）...")
    results_normal = reservoir.operate(
        initial_level=108.0,
        inflow_series=observed_inflow,
        dt=86400.0
    )
    
    print("\n5. 调度完成\n")
    
    # 5. 对比分析
    print("="*70)
    print("预报调度效果对比")
    print("="*70)
    
    print(f"\n【情景1：基于预报的调度】")
    print(f"  最高水位: {np.max(results_forecast['level']):.2f} m")
    print(f"  最大出流: {np.max(results_forecast['outflow']):.1f} m³/s")
    print(f"  超防洪限制: {'是' if np.any(results_forecast['level'] > 113.0) else '否'}")
    
    print(f"\n【情景2：常规调度（无预报）】")
    print(f"  最高水位: {np.max(results_normal['level']):.2f} m")
    print(f"  最大出流: {np.max(results_normal['outflow']):.1f} m³/s")
    print(f"  超防洪限制: {'是' if np.any(results_normal['level'] > 113.0) else '否'}")
    
    # 计算改善效果
    level_reduction = np.max(results_normal['level']) - np.max(results_forecast['level'])
    print(f"\n【预报调度改善效果】")
    print(f"  最高水位降低: {level_reduction:.2f} m")
    print(f"  防洪效益: {level_reduction / np.max(results_normal['level']) * 100:.1f}%")
    
    # 6. 可视化
    print(f"\n6. 生成可视化...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    time = np.arange(n_days)
    
    # 图1：入库流量与预报
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time, observed_inflow, 'b-', linewidth=2, label='实测入流')
    
    # 绘制预报（选几个关键时刻）
    key_days = [18, 19, 20, 38, 39, 40]
    for day in key_days:
        if day < n_days - 3:
            forecast = results_forecast['forecast_inflow'][day, :]
            forecast_time = np.arange(day, min(day + len(forecast), n_days))
            ax1.plot(forecast_time, forecast[:len(forecast_time)], 
                    '--', alpha=0.5, linewidth=1.5)
    
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('流量 (m³/s)', fontsize=10)
    ax1.set_title('【预报系统】入库流量与预报', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2：水位对比
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(time, results_forecast['level'], 'b-', 
            linewidth=2, label='基于预报')
    ax2.plot(time, results_normal['level'], 'r--', 
            linewidth=2, label='常规调度')
    ax2.axhline(y=113.0, color='orange', linestyle=':', 
               linewidth=1.5, label='防洪限制水位')
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('水位 (m)', fontsize=10)
    ax2.set_title('水位过程对比', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3：出流对比
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(time, results_forecast['outflow'], 'b-', 
            linewidth=2, label='基于预报')
    ax3.plot(time, results_normal['outflow'], 'r--', 
            linewidth=2, label='常规调度')
    
    ax3.set_xlabel('时间 (天)', fontsize=11)
    ax3.set_ylabel('出流 (m³/s)', fontsize=10)
    ax3.set_title('出流过程对比', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 图4：库容对比
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(time, results_forecast['storage'], 'b-', 
            linewidth=2, label='基于预报')
    ax4.plot(time, results_normal['storage'], 'r--', 
            linewidth=2, label='常规调度')
    
    ax4.set_xlabel('时间 (天)', fontsize=11)
    ax4.set_ylabel('库容 (万m³)', fontsize=10)
    ax4.set_title('库容过程对比', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 图5：关键指标对比
    ax5 = fig.add_subplot(gs[2, 1])
    
    metrics = ['最高水位\n(m)', '最大出流\n(m³/s)', '平均库容\n(万m³)']
    forecast_values = [
        np.max(results_forecast['level']),
        np.max(results_forecast['outflow']),
        np.mean(results_forecast['storage'])
    ]
    normal_values = [
        np.max(results_normal['level']),
        np.max(results_normal['outflow']),
        np.mean(results_normal['storage'])
    ]
    
    x_pos = np.arange(len(metrics))
    width = 0.35
    
    # 归一化到0-1显示
    max_vals = [120, 400, 6000]
    forecast_norm = [v/m for v, m in zip(forecast_values, max_vals)]
    normal_norm = [v/m for v, m in zip(normal_values, max_vals)]
    
    ax5.bar(x_pos - width/2, forecast_norm, width, 
           label='基于预报', color='blue', alpha=0.7)
    ax5.bar(x_pos + width/2, normal_norm, width, 
           label='常规调度', color='red', alpha=0.7)
    
    ax5.set_ylabel('归一化值', fontsize=10)
    ax5.set_title('关键指标对比', fontsize=12, fontweight='bold')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(metrics)
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 添加实际值标签
    for i, (f_val, n_val) in enumerate(zip(forecast_values, normal_values)):
        ax5.text(i - width/2, forecast_norm[i] + 0.02, f'{f_val:.1f}',
                ha='center', fontsize=8)
        ax5.text(i + width/2, normal_norm[i] + 0.02, f'{n_val:.1f}',
                ha='center', fontsize=8)
    
    plt.savefig(f'{output_dir}/forecast_operation.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/forecast_operation.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_forecast_operation()
