#!/usr/bin/env python3
"""
参数敏感性分析工具
==================

功能: 分析PID参数、物理参数等对系统性能的影响

使用方法:
    python3 sensitivity_analyzer.py
    
输出:
    - sensitivity_analysis_report.txt (分析报告)
    - sensitivity_Kp.png (Kp敏感性曲线)
    - sensitivity_Ki.png (Ki敏感性曲线)
    - sensitivity_Kd.png (Kd敏感性曲线)
    - sensitivity_width.png (闸门宽度敏感性)
    - sensitivity_comprehensive.png (综合敏感性矩阵)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import time

print("="*80)
print("  参数敏感性分析工具 v1.0")
print("="*80)
print()

# ============================================================================
# 简化PID模型（复用pid_tuner.py中的模型）
# ============================================================================

class SimplePIDController:
    """简化的PID控制器"""
    
    def __init__(self, Kp: float, Ki: float, Kd: float):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0.0
        self.prev_error = 0.0
    
    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.prev_error = 0.0
    
    def compute(self, setpoint: float, measurement: float, dt: float) -> float:
        """计算PID输出"""
        error = setpoint - measurement
        
        # P项
        P = self.Kp * error
        
        # I项（带抗饱和）
        self.integral += error * dt
        self.integral = np.clip(self.integral, -10, 10)
        I = self.Ki * self.integral
        
        # D项
        D = self.Kd * (error - self.prev_error) / dt if dt > 0 else 0
        
        self.prev_error = error
        
        # 总输出（限幅）
        output = P + I + D
        output = np.clip(output, 0, 3.0)
        
        return output

class SimpleGateModel:
    """简化的闸门-渠道模型"""
    
    def __init__(self, width: float = 3.0, length: float = 100.0):
        self.width = width
        self.length = length
        self.water_level = 2.0
        self.pool_area = width * length
    
    def reset(self):
        """重置模型状态"""
        self.water_level = 2.0
    
    def gate_discharge(self, opening: float) -> float:
        """计算闸门流量"""
        if opening < 0.1:
            return 0.0
        
        g = 9.81
        H = self.water_level + 0.5
        mu = 0.85
        
        Q = mu * self.width * opening * np.sqrt(2 * g * H)
        return Q
    
    def update(self, opening: float, demand: float, dt: float) -> float:
        """更新水位"""
        Q_in = self.gate_discharge(opening)
        Q_out = demand
        
        dV = (Q_in - Q_out) * dt
        dh = dV / self.pool_area
        
        self.water_level += dh
        self.water_level = np.clip(self.water_level, 0.5, 4.0)
        
        return self.water_level

# ============================================================================
# 参数敏感性分析器
# ============================================================================

class SensitivityAnalyzer:
    """参数敏感性分析器"""
    
    def __init__(self):
        self.results = {}
    
    def simulate_step_response(self, Kp: float, Ki: float, Kd: float, 
                               width: float = 3.0) -> Dict:
        """仿真阶跃响应"""
        controller = SimplePIDController(Kp, Ki, Kd)
        model = SimpleGateModel(width=width)
        
        # 仿真参数
        dt = 0.1
        duration = 60.0
        steps = int(duration / dt)
        
        setpoint = 2.0
        demand = 10.0
        
        # 存储数据
        time_data = []
        level_data = []
        error_data = []
        
        # 仿真循环
        for i in range(steps):
            t = i * dt
            
            # 控制
            opening = controller.compute(setpoint, model.water_level, dt)
            
            # 更新
            level = model.update(opening, demand, dt)
            error = abs(setpoint - level)
            
            time_data.append(t)
            level_data.append(level)
            error_data.append(error)
        
        # 计算性能指标
        level_array = np.array(level_data)
        error_array = np.array(error_data)
        
        # 稳态误差（最后10秒平均）
        steady_error = np.mean(error_array[-100:]) * 100  # cm
        
        # 最大误差
        max_error = np.max(error_array) * 100  # cm
        
        # 超调量
        overshoot = (np.max(level_array) - setpoint) * 100  # cm
        
        # 稳定时间（误差<5cm的时间）
        settling_idx = np.where(error_array < 0.05)[0]
        settling_time = settling_idx[0] * dt if len(settling_idx) > 0 else duration
        
        return {
            'steady_error': steady_error,
            'max_error': max_error,
            'overshoot': overshoot,
            'settling_time': settling_time
        }
    
    def analyze_Kp_sensitivity(self, Ki: float = 0.5, Kd: float = 0.1,
                               Kp_range: Tuple[float, float] = (0.5, 5.0),
                               n_points: int = 20) -> Dict:
        """分析Kp参数敏感性"""
        print("\n【Kp参数敏感性分析】")
        print("-" * 80)
        
        Kp_values = np.linspace(Kp_range[0], Kp_range[1], n_points)
        results = {
            'Kp': [],
            'steady_error': [],
            'max_error': [],
            'overshoot': [],
            'settling_time': []
        }
        
        for i, Kp in enumerate(Kp_values, 1):
            print(f"  [{i}/{n_points}] Kp={Kp:.2f}...", end='')
            
            metrics = self.simulate_step_response(Kp, Ki, Kd)
            
            results['Kp'].append(Kp)
            results['steady_error'].append(metrics['steady_error'])
            results['max_error'].append(metrics['max_error'])
            results['overshoot'].append(metrics['overshoot'])
            results['settling_time'].append(metrics['settling_time'])
            
            print(f" 稳态误差={metrics['steady_error']:.2f}cm")
        
        return results
    
    def analyze_Ki_sensitivity(self, Kp: float = 2.5, Kd: float = 0.1,
                               Ki_range: Tuple[float, float] = (0.1, 1.5),
                               n_points: int = 20) -> Dict:
        """分析Ki参数敏感性"""
        print("\n【Ki参数敏感性分析】")
        print("-" * 80)
        
        Ki_values = np.linspace(Ki_range[0], Ki_range[1], n_points)
        results = {
            'Ki': [],
            'steady_error': [],
            'max_error': [],
            'overshoot': [],
            'settling_time': []
        }
        
        for i, Ki in enumerate(Ki_values, 1):
            print(f"  [{i}/{n_points}] Ki={Ki:.2f}...", end='')
            
            metrics = self.simulate_step_response(Kp, Ki, Kd)
            
            results['Ki'].append(Ki)
            results['steady_error'].append(metrics['steady_error'])
            results['max_error'].append(metrics['max_error'])
            results['overshoot'].append(metrics['overshoot'])
            results['settling_time'].append(metrics['settling_time'])
            
            print(f" 稳态误差={metrics['steady_error']:.2f}cm")
        
        return results
    
    def analyze_Kd_sensitivity(self, Kp: float = 2.5, Ki: float = 0.5,
                               Kd_range: Tuple[float, float] = (0.0, 0.5),
                               n_points: int = 20) -> Dict:
        """分析Kd参数敏感性"""
        print("\n【Kd参数敏感性分析】")
        print("-" * 80)
        
        Kd_values = np.linspace(Kd_range[0], Kd_range[1], n_points)
        results = {
            'Kd': [],
            'steady_error': [],
            'max_error': [],
            'overshoot': [],
            'settling_time': []
        }
        
        for i, Kd in enumerate(Kd_values, 1):
            print(f"  [{i}/{n_points}] Kd={Kd:.2f}...", end='')
            
            metrics = self.simulate_step_response(Kp, Ki, Kd)
            
            results['Kd'].append(Kd)
            results['steady_error'].append(metrics['steady_error'])
            results['max_error'].append(metrics['max_error'])
            results['overshoot'].append(metrics['overshoot'])
            results['settling_time'].append(metrics['settling_time'])
            
            print(f" 稳态误差={metrics['steady_error']:.2f}cm")
        
        return results
    
    def analyze_width_sensitivity(self, Kp: float = 2.5, Ki: float = 0.5, 
                                  Kd: float = 0.1,
                                  width_range: Tuple[float, float] = (2.0, 5.0),
                                  n_points: int = 15) -> Dict:
        """分析闸门宽度敏感性"""
        print("\n【闸门宽度敏感性分析】")
        print("-" * 80)
        
        width_values = np.linspace(width_range[0], width_range[1], n_points)
        results = {
            'width': [],
            'steady_error': [],
            'max_error': [],
            'overshoot': [],
            'settling_time': []
        }
        
        for i, width in enumerate(width_values, 1):
            print(f"  [{i}/{n_points}] 宽度={width:.2f}m...", end='')
            
            metrics = self.simulate_step_response(Kp, Ki, Kd, width=width)
            
            results['width'].append(width)
            results['steady_error'].append(metrics['steady_error'])
            results['max_error'].append(metrics['max_error'])
            results['overshoot'].append(metrics['overshoot'])
            results['settling_time'].append(metrics['settling_time'])
            
            print(f" 稳态误差={metrics['steady_error']:.2f}cm")
        
        return results
    
    def plot_sensitivity(self, results: Dict, param_name: str, 
                        output_file: str):
        """绘制敏感性曲线"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'{param_name}参数敏感性分析', fontsize=16, fontweight='bold')
        
        param_values = results[list(results.keys())[0]]
        
        # 稳态误差
        ax = axes[0, 0]
        ax.plot(param_values, results['steady_error'], 'b-o', linewidth=2, markersize=6)
        ax.set_xlabel(f'{param_name}', fontsize=12)
        ax.set_ylabel('Steady State Error (cm)', fontsize=12)
        ax.set_title('(a) Steady State Error', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 最大误差
        ax = axes[0, 1]
        ax.plot(param_values, results['max_error'], 'r-s', linewidth=2, markersize=6)
        ax.set_xlabel(f'{param_name}', fontsize=12)
        ax.set_ylabel('Max Error (cm)', fontsize=12)
        ax.set_title('(b) Max Error', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 超调量
        ax = axes[1, 0]
        ax.plot(param_values, results['overshoot'], 'g-^', linewidth=2, markersize=6)
        ax.set_xlabel(f'{param_name}', fontsize=12)
        ax.set_ylabel('Overshoot (cm)', fontsize=12)
        ax.set_title('(c) Overshoot', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # 稳定时间
        ax = axes[1, 1]
        ax.plot(param_values, results['settling_time'], 'm-d', linewidth=2, markersize=6)
        ax.set_xlabel(f'{param_name}', fontsize=12)
        ax.set_ylabel('Settling Time (s)', fontsize=12)
        ax.set_title('(d) Settling Time', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✓ 敏感性曲线已保存: {output_file}")
    
    def plot_comprehensive(self, Kp_results: Dict, Ki_results: Dict, 
                          Kd_results: Dict, width_results: Dict):
        """绘制综合敏感性对比"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Comprehensive Sensitivity Analysis', 
                    fontsize=16, fontweight='bold')
        
        # Kp敏感性
        ax = axes[0, 0]
        ax.plot(Kp_results['Kp'], Kp_results['steady_error'], 'b-o', label='Steady Error')
        ax.plot(Kp_results['Kp'], Kp_results['max_error'], 'r-s', label='Max Error')
        ax.set_xlabel('Kp', fontsize=12)
        ax.set_ylabel('Error (cm)', fontsize=12)
        ax.set_title('(a) Kp Sensitivity', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Ki敏感性
        ax = axes[0, 1]
        ax.plot(Ki_results['Ki'], Ki_results['steady_error'], 'b-o', label='Steady Error')
        ax.plot(Ki_results['Ki'], Ki_results['max_error'], 'r-s', label='Max Error')
        ax.set_xlabel('Ki', fontsize=12)
        ax.set_ylabel('Error (cm)', fontsize=12)
        ax.set_title('(b) Ki Sensitivity', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Kd敏感性
        ax = axes[1, 0]
        ax.plot(Kd_results['Kd'], Kd_results['steady_error'], 'b-o', label='Steady Error')
        ax.plot(Kd_results['Kd'], Kd_results['max_error'], 'r-s', label='Max Error')
        ax.set_xlabel('Kd', fontsize=12)
        ax.set_ylabel('Error (cm)', fontsize=12)
        ax.set_title('(c) Kd Sensitivity', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 闸门宽度敏感性
        ax = axes[1, 1]
        ax.plot(width_results['width'], width_results['steady_error'], 'b-o', label='Steady Error')
        ax.plot(width_results['width'], width_results['max_error'], 'r-s', label='Max Error')
        ax.set_xlabel('Gate Width (m)', fontsize=12)
        ax.set_ylabel('Error (cm)', fontsize=12)
        ax.set_title('(d) Width Sensitivity', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sensitivity_comprehensive.png', dpi=150, bbox_inches='tight')
        print("\n✓ 综合敏感性对比图已保存: sensitivity_comprehensive.png")
    
    def generate_report(self, Kp_results: Dict, Ki_results: Dict,
                       Kd_results: Dict, width_results: Dict,
                       output_file: str = 'sensitivity_analysis_report.txt'):
        """生成分析报告"""
        lines = []
        lines.append("="*80)
        lines.append("  参数敏感性分析报告")
        lines.append("="*80)
        lines.append("")
        
        # Kp敏感性
        lines.append("【Kp参数敏感性】")
        lines.append("-" * 80)
        Kp_min_idx = np.argmin(Kp_results['steady_error'])
        lines.append(f"分析范围: {Kp_results['Kp'][0]:.2f} ~ {Kp_results['Kp'][-1]:.2f}")
        lines.append(f"最优值: Kp = {Kp_results['Kp'][Kp_min_idx]:.2f}")
        lines.append(f"对应稳态误差: {Kp_results['steady_error'][Kp_min_idx]:.2f} cm")
        lines.append(f"误差变化范围: {min(Kp_results['steady_error']):.2f} ~ {max(Kp_results['steady_error']):.2f} cm")
        lines.append("")
        
        # Ki敏感性
        lines.append("【Ki参数敏感性】")
        lines.append("-" * 80)
        Ki_min_idx = np.argmin(Ki_results['steady_error'])
        lines.append(f"分析范围: {Ki_results['Ki'][0]:.2f} ~ {Ki_results['Ki'][-1]:.2f}")
        lines.append(f"最优值: Ki = {Ki_results['Ki'][Ki_min_idx]:.2f}")
        lines.append(f"对应稳态误差: {Ki_results['steady_error'][Ki_min_idx]:.2f} cm")
        lines.append(f"误差变化范围: {min(Ki_results['steady_error']):.2f} ~ {max(Ki_results['steady_error']):.2f} cm")
        lines.append("")
        
        # Kd敏感性
        lines.append("【Kd参数敏感性】")
        lines.append("-" * 80)
        Kd_min_idx = np.argmin(Kd_results['steady_error'])
        lines.append(f"分析范围: {Kd_results['Kd'][0]:.2f} ~ {Kd_results['Kd'][-1]:.2f}")
        lines.append(f"最优值: Kd = {Kd_results['Kd'][Kd_min_idx]:.2f}")
        lines.append(f"对应稳态误差: {Kd_results['steady_error'][Kd_min_idx]:.2f} cm")
        lines.append(f"误差变化范围: {min(Kd_results['steady_error']):.2f} ~ {max(Kd_results['steady_error']):.2f} cm")
        lines.append("")
        
        # 闸门宽度敏感性
        lines.append("【闸门宽度敏感性】")
        lines.append("-" * 80)
        width_min_idx = np.argmin(width_results['steady_error'])
        lines.append(f"分析范围: {width_results['width'][0]:.2f} ~ {width_results['width'][-1]:.2f} m")
        lines.append(f"最优值: Width = {width_results['width'][width_min_idx]:.2f} m")
        lines.append(f"对应稳态误差: {width_results['steady_error'][width_min_idx]:.2f} cm")
        lines.append(f"误差变化范围: {min(width_results['steady_error']):.2f} ~ {max(width_results['steady_error']):.2f} cm")
        lines.append("")
        
        # 敏感性排序
        lines.append("【参数敏感性排序】")
        lines.append("-" * 80)
        
        Kp_sensitivity = max(Kp_results['steady_error']) - min(Kp_results['steady_error'])
        Ki_sensitivity = max(Ki_results['steady_error']) - min(Ki_results['steady_error'])
        Kd_sensitivity = max(Kd_results['steady_error']) - min(Kd_results['steady_error'])
        width_sensitivity = max(width_results['steady_error']) - min(width_results['steady_error'])
        
        sensitivities = [
            ('Kp', Kp_sensitivity),
            ('Ki', Ki_sensitivity),
            ('Kd', Kd_sensitivity),
            ('Width', width_sensitivity)
        ]
        sensitivities.sort(key=lambda x: x[1], reverse=True)
        
        lines.append("按稳态误差变化幅度排序:")
        for i, (param, sens) in enumerate(sensitivities, 1):
            lines.append(f"  {i}. {param:8s}: {sens:.2f} cm")
        lines.append("")
        
        # 推荐参数
        lines.append("【推荐参数组合】")
        lines.append("-" * 80)
        lines.append(f"Kp = {Kp_results['Kp'][Kp_min_idx]:.2f}")
        lines.append(f"Ki = {Ki_results['Ki'][Ki_min_idx]:.2f}")
        lines.append(f"Kd = {Kd_results['Kd'][Kd_min_idx]:.2f}")
        lines.append(f"Width = {width_results['width'][width_min_idx]:.2f} m")
        lines.append("")
        
        lines.append("="*80)
        
        report_text = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n✓ 分析报告已保存: {output_file}")
        
        return report_text

# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("【参数敏感性分析】")
    print("-" * 80)
    print("分析目标: PID参数(Kp, Ki, Kd)和闸门宽度对控制性能的影响")
    print()
    
    analyzer = SensitivityAnalyzer()
    
    start_time = time.time()
    
    # 1. Kp敏感性分析
    Kp_results = analyzer.analyze_Kp_sensitivity(Ki=0.5, Kd=0.1, 
                                                  Kp_range=(0.5, 5.0), n_points=20)
    analyzer.plot_sensitivity(Kp_results, 'Kp', 'sensitivity_Kp.png')
    
    # 2. Ki敏感性分析
    Ki_results = analyzer.analyze_Ki_sensitivity(Kp=2.5, Kd=0.1,
                                                  Ki_range=(0.1, 1.5), n_points=20)
    analyzer.plot_sensitivity(Ki_results, 'Ki', 'sensitivity_Ki.png')
    
    # 3. Kd敏感性分析
    Kd_results = analyzer.analyze_Kd_sensitivity(Kp=2.5, Ki=0.5,
                                                  Kd_range=(0.0, 0.5), n_points=20)
    analyzer.plot_sensitivity(Kd_results, 'Kd', 'sensitivity_Kd.png')
    
    # 4. 闸门宽度敏感性分析
    width_results = analyzer.analyze_width_sensitivity(Kp=2.5, Ki=0.5, Kd=0.1,
                                                       width_range=(2.0, 5.0), n_points=15)
    analyzer.plot_sensitivity(width_results, 'Width', 'sensitivity_width.png')
    
    # 5. 综合对比图
    analyzer.plot_comprehensive(Kp_results, Ki_results, Kd_results, width_results)
    
    # 6. 生成分析报告
    report = analyzer.generate_report(Kp_results, Ki_results, Kd_results, width_results)
    print()
    print(report)
    
    elapsed = time.time() - start_time
    
    print()
    print("="*80)
    print("  分析完成!")
    print("="*80)
    print()
    print(f"总耗时: {elapsed:.1f}秒")
    print()
    print("生成的文件:")
    print("  1. sensitivity_Kp.png - Kp敏感性曲线")
    print("  2. sensitivity_Ki.png - Ki敏感性曲线")
    print("  3. sensitivity_Kd.png - Kd敏感性曲线")
    print("  4. sensitivity_width.png - 闸门宽度敏感性曲线")
    print("  5. sensitivity_comprehensive.png - 综合对比图")
    print("  6. sensitivity_analysis_report.txt - 分析报告")
    print()
    print("="*80)
