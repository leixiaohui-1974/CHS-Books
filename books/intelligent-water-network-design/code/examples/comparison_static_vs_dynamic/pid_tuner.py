#!/usr/bin/env python3
"""
PID参数优化工具
===============

功能: 自动优化L2级PID控制器参数,找到最佳Kp, Ki, Kd

使用方法:
    python3 pid_tuner.py
    
输出:
    - pid_tuning_results.txt (优化结果报告)
    - pid_tuning_comparison.png (不同参数对比图)
    - pid_optimal_performance.png (最优参数性能)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from typing import Dict, List, Tuple
import time

print("="*80)
print("  PID参数自动优化工具")
print("="*80)
print()

# ============================================================================
# 简化的PID控制器和模型
# ============================================================================

class SimplePIDController:
    """简化的PID控制器"""
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0.0
        self.prev_error = 0.0
    
    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
    
    def compute(self, setpoint, measurement, dt):
        error = setpoint - measurement
        
        # P项
        p_term = self.Kp * error
        
        # I项
        self.integral += error * dt
        # 积分限幅
        self.integral = np.clip(self.integral, -10, 10)
        i_term = self.Ki * self.integral
        
        # D项
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        d_term = self.Kd * derivative
        
        self.prev_error = error
        
        # 输出限幅
        output = p_term + i_term + d_term
        output = np.clip(output, -1.0, 1.0)
        
        return output


class SimpleGateModel:
    """简化的闸门-渠道模型"""
    def __init__(self):
        self.h_downstream = 2.0  # 下游水位(m)
        self.gate_opening = 1.8  # 闸门开度(m)
        self.flow = 10.0         # 流量(m³/s)
        
    def update(self, control_signal, demand, dt):
        """更新模型状态"""
        # 闸门开度响应(带延迟)
        target_opening = self.gate_opening + control_signal * 0.5
        target_opening = np.clip(target_opening, 0.5, 3.0)
        self.gate_opening += (target_opening - self.gate_opening) * 0.1
        
        # 流量计算(简化)
        self.flow = 10.0 * (self.gate_opening / 1.8)
        
        # 水位响应
        water_balance = self.flow - demand
        self.h_downstream += water_balance * 0.0001  # 简化的水量平衡
        
        return self.h_downstream


def evaluate_pid(Kp, Ki, Kd, scenario='step') -> Dict:
    """评估一组PID参数的性能"""
    controller = SimplePIDController(Kp, Ki, Kd)
    model = SimpleGateModel()
    
    # 仿真参数
    dt = 10.0  # 控制周期10秒
    duration = 1800  # 30分钟
    steps = int(duration / dt)
    
    # 记录数据
    time_arr = np.arange(steps) * dt / 60  # 转换为分钟
    h_target_arr = np.zeros(steps)
    h_actual_arr = np.zeros(steps)
    demand_arr = np.zeros(steps)
    
    # 生成测试场景
    target_level = 2.0  # 目标水位
    
    for i in range(steps):
        t = i * dt
        
        if scenario == 'step':
            # 阶跃响应
            demand = 12.0 if t > 300 else 10.0
        elif scenario == 'sine':
            # 正弦波扰动
            demand = 10.0 + 2.0 * np.sin(2 * np.pi * t / 600)
        else:  # 'random'
            # 随机扰动
            demand = 10.0 + np.random.uniform(-1, 1)
        
        # PID控制
        control = controller.compute(target_level, model.h_downstream, dt)
        
        # 模型更新
        h_actual = model.update(control, demand, dt)
        
        # 记录
        h_target_arr[i] = target_level
        h_actual_arr[i] = h_actual
        demand_arr[i] = demand
    
    # 计算性能指标
    errors = (h_actual_arr - h_target_arr) * 100  # 转换为cm
    
    # 稳态误差(最后30%数据)
    steady_start = int(steps * 0.7)
    steady_error = np.mean(np.abs(errors[steady_start:]))
    
    # 最大误差
    max_error = np.max(np.abs(errors))
    
    # 超调量
    if scenario == 'step':
        overshoot = np.max(h_actual_arr[30:] - target_level) * 100
        overshoot = max(0, overshoot)
    else:
        overshoot = 0
    
    # 调节时间(误差进入±5cm的时间)
    settling_time = duration / 60  # 默认为最大值
    for i in range(steps):
        if np.all(np.abs(errors[i:]) < 5):
            settling_time = time_arr[i]
            break
    
    # 平均绝对误差
    mae = np.mean(np.abs(errors))
    
    # 综合得分(越高越好)
    score = 100 - (mae * 2 + max_error * 0.5 + settling_time * 0.5 + overshoot * 0.2)
    
    return {
        'Kp': Kp,
        'Ki': Ki,
        'Kd': Kd,
        '稳态误差(cm)': steady_error,
        '最大误差(cm)': max_error,
        '超调量(cm)': overshoot,
        '调节时间(分钟)': settling_time,
        '平均误差(cm)': mae,
        '综合得分': max(0, score),
        'time': time_arr,
        'target': h_target_arr,
        'actual': h_actual_arr,
        'demand': demand_arr
    }


# ============================================================================
# 参数优化
# ============================================================================

print("【步骤1】网格搜索优化PID参数...")
print()

# 定义搜索空间
Kp_range = [1.0, 1.5, 2.0, 2.5, 3.0]
Ki_range = [0.1, 0.3, 0.5, 0.7, 1.0]
Kd_range = [0.05, 0.1, 0.15, 0.2, 0.3]

best_results = []
all_results = []

total_combinations = len(Kp_range) * len(Ki_range) * len(Kd_range)
print(f"搜索空间: Kp×Ki×Kd = {len(Kp_range)}×{len(Ki_range)}×{len(Kd_range)} = {total_combinations}组参数")
print(f"预计耗时: ~{total_combinations*0.5:.0f}秒")
print()

start_time = time.time()
tested = 0

for Kp in Kp_range:
    for Ki in Ki_range:
        for Kd in Kd_range:
            tested += 1
            if tested % 10 == 0:
                print(f"  进度: {tested}/{total_combinations} ({tested/total_combinations*100:.0f}%)")
            
            # 评估此参数组合
            result = evaluate_pid(Kp, Ki, Kd, 'step')
            all_results.append(result)

elapsed = time.time() - start_time
print(f"\n✓ 搜索完成! 耗时{elapsed:.1f}秒")
print()

# 排序找到最优参数
all_results.sort(key=lambda x: x['综合得分'], reverse=True)
best_result = all_results[0]

print("【最优参数】")
print("-" * 80)
print(f"  Kp = {best_result['Kp']:.2f}")
print(f"  Ki = {best_result['Ki']:.2f}")
print(f"  Kd = {best_result['Kd']:.2f}")
print()
print("【性能指标】")
print(f"  稳态误差: {best_result['稳态误差(cm)']:.2f} cm")
print(f"  最大误差: {best_result['最大误差(cm)']:.2f} cm")
print(f"  超调量: {best_result['超调量(cm)']:.2f} cm")
print(f"  调节时间: {best_result['调节时间(分钟)']:.2f} 分钟")
print(f"  平均误差: {best_result['平均误差(cm)']:.2f} cm")
print(f"  综合得分: {best_result['综合得分']:.1f}")
print()

# 对比原始参数
default_result = evaluate_pid(2.0, 0.5, 0.1, 'step')
print("【与默认参数对比】")
print("-" * 80)
print(f"{'指标':<15} {'默认(2.0,0.5,0.1)':<20} {'最优参数':<20} {'改进'}")
print("-" * 80)
print(f"{'稳态误差(cm)':<15} {default_result['稳态误差(cm)']:>10.2f} {best_result['稳态误差(cm)']:>20.2f} {((default_result['稳态误差(cm)']-best_result['稳态误差(cm)'])/default_result['稳态误差(cm)']*100):>10.1f}%")
print(f"{'最大误差(cm)':<15} {default_result['最大误差(cm)']:>10.2f} {best_result['最大误差(cm)']:>20.2f} {((default_result['最大误差(cm)']-best_result['最大误差(cm)'])/default_result['最大误差(cm)']*100):>10.1f}%")
print(f"{'综合得分':<15} {default_result['综合得分']:>10.1f} {best_result['综合得分']:>20.1f} {((best_result['综合得分']-default_result['综合得分'])/default_result['综合得分']*100):>10.1f}%")
print()

# ============================================================================
# 保存优化报告
# ============================================================================

print("【步骤2】生成优化报告...")

report_lines = []
report_lines.append("="*80)
report_lines.append("  PID参数优化报告")
report_lines.append("="*80)
report_lines.append(f"\n优化时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"搜索方法: 网格搜索")
report_lines.append(f"测试场景: 阶跃响应")
report_lines.append(f"搜索空间: {total_combinations}组参数")
report_lines.append(f"耗时: {elapsed:.1f}秒\n")

report_lines.append("\n" + "="*80)
report_lines.append("  最优参数")
report_lines.append("="*80)
report_lines.append(f"\n  Kp = {best_result['Kp']:.2f}")
report_lines.append(f"  Ki = {best_result['Ki']:.2f}")
report_lines.append(f"  Kd = {best_result['Kd']:.2f}\n")

report_lines.append("\n" + "="*80)
report_lines.append("  性能指标")
report_lines.append("="*80)
report_lines.append(f"\n  稳态误差: {best_result['稳态误差(cm)']:.2f} cm")
report_lines.append(f"  最大误差: {best_result['最大误差(cm)']:.2f} cm")
report_lines.append(f"  超调量: {best_result['超调量(cm)']:.2f} cm")
report_lines.append(f"  调节时间: {best_result['调节时间(分钟)']:.2f} 分钟")
report_lines.append(f"  平均误差: {best_result['平均误差(cm)']:.2f} cm")
report_lines.append(f"  综合得分: {best_result['综合得分']:.1f}\n")

report_lines.append("\n" + "="*80)
report_lines.append("  Top 10 参数组合")
report_lines.append("="*80)
report_lines.append("\n| Rank | Kp   | Ki   | Kd   | 稳态误差 | 综合得分 |")
report_lines.append("|" + "-"*78 + "|")

for i, r in enumerate(all_results[:10], 1):
    report_lines.append(f"| {i:>4} | {r['Kp']:>4.2f} | {r['Ki']:>4.2f} | {r['Kd']:>4.2f} | {r['稳态误差(cm)']:>8.2f} | {r['综合得分']:>8.1f} |")

report_lines.append("\n" + "="*80)
report_lines.append("  使用建议")
report_lines.append("="*80)
report_lines.append("\n1. 修改dynamic_design_L2.py中的PID参数:")
report_lines.append(f"   controller = PIDController(Kp={best_result['Kp']:.2f}, Ki={best_result['Ki']:.2f}, Kd={best_result['Kd']:.2f})")
report_lines.append("\n2. 根据实际情况微调:")
report_lines.append("   - 响应偏慢: 增大Kp")
report_lines.append("   - 稳态误差大: 增大Ki")
report_lines.append("   - 振荡严重: 增大Kd")
report_lines.append("\n3. 在实际系统中测试并进一步调整")

report_lines.append("\n" + "="*80)
report_lines.append("报告完成")
report_lines.append("="*80)

with open('pid_tuning_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print("✓ pid_tuning_results.txt")

# ============================================================================
# 可视化
# ============================================================================

print()
print("【步骤3】生成对比图...")

# 图1: 不同参数对比(选择5组有代表性的)
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

selected_results = [
    all_results[0],  # 最优
    default_result,  # 默认
    all_results[len(all_results)//4],  # 中等
    all_results[len(all_results)//2],  # 中等
    all_results[-10]  # 较差
]

for i, result in enumerate(selected_results):
    if i < 6:
        ax = axes[i//3, i%3]
        
        time_data = result['time']
        target_data = result['target']
        actual_data = result['actual']
        
        ax.plot(time_data, target_data * 100, 'r--', linewidth=2, label='Target', alpha=0.7)
        ax.plot(time_data, actual_data * 100, 'b-', linewidth=1.5, label='Actual')
        
        ax.axhline(y=205, color='red', linestyle=':', alpha=0.3)
        ax.axhline(y=195, color='red', linestyle=':', alpha=0.3)
        
        ax.set_xlabel('Time (min)', fontweight='bold')
        ax.set_ylabel('Water Level (cm)', fontweight='bold')
        ax.set_title(f'({i+1}) Kp={result["Kp"]:.1f}, Ki={result["Ki"]:.1f}, Kd={result["Kd"]:.2f}\nScore={result["综合得分"]:.1f}',
                    fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

# 最后一个子图显示综合得分分布
ax = axes[1, 2]
scores = [r['综合得分'] for r in all_results[:50]]
ax.hist(scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
ax.axvline(x=best_result['综合得分'], color='red', linestyle='--', linewidth=2, label='Best')
ax.axvline(x=default_result['综合得分'], color='orange', linestyle='--', linewidth=2, label='Default')
ax.set_xlabel('Score', fontweight='bold')
ax.set_ylabel('Count', fontweight='bold')
ax.set_title('(6) Score Distribution\n(Top 50)', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

plt.suptitle('PID Parameter Tuning Comparison', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('pid_tuning_comparison.png', dpi=150, bbox_inches='tight')
print("✓ pid_tuning_comparison.png")

# 图2: 最优参数详细性能
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 子图1: 水位曲线
ax = axes[0, 0]
ax.plot(best_result['time'], best_result['target'] * 100, 'r--', linewidth=2, label='Target', alpha=0.7)
ax.plot(best_result['time'], best_result['actual'] * 100, 'b-', linewidth=2, label='Actual')
ax.fill_between(best_result['time'], 195, 205, color='green', alpha=0.1, label='±5cm band')
ax.set_xlabel('Time (min)', fontweight='bold')
ax.set_ylabel('Water Level (cm)', fontweight='bold')
ax.set_title('(a) Water Level Control', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# 子图2: 误差曲线
ax = axes[0, 1]
errors = (best_result['actual'] - best_result['target']) * 100
ax.plot(best_result['time'], errors, 'g-', linewidth=1.5)
ax.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='±5cm limit')
ax.axhline(y=-5, color='red', linestyle='--', alpha=0.5)
ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax.set_xlabel('Time (min)', fontweight='bold')
ax.set_ylabel('Error (cm)', fontweight='bold')
ax.set_title('(b) Control Error', fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# 子图3: 需水变化
ax = axes[1, 0]
ax.plot(best_result['time'], best_result['demand'], 'purple', linewidth=2)
ax.set_xlabel('Time (min)', fontweight='bold')
ax.set_ylabel('Demand (m³/s)', fontweight='bold')
ax.set_title('(c) Water Demand', fontweight='bold')
ax.grid(True, alpha=0.3)

# 子图4: 性能指标对比
ax = axes[1, 1]
metrics = ['稳态\n误差', '最大\n误差', '超调量', '调节\n时间', '平均\n误差']
default_vals = [
    default_result['稳态误差(cm)'],
    default_result['最大误差(cm)'] / 10,  # 缩放
    default_result['超调量(cm)'],
    default_result['调节时间(分钟)'],
    default_result['平均误差(cm)']
]
best_vals = [
    best_result['稳态误差(cm)'],
    best_result['最大误差(cm)'] / 10,
    best_result['超调量(cm)'],
    best_result['调节时间(分钟)'],
    best_result['平均误差(cm)']
]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax.bar(x - width/2, default_vals, width, label='Default', color='orange', alpha=0.7)
bars2 = ax.bar(x + width/2, best_vals, width, label='Optimized', color='green', alpha=0.7)

ax.set_ylabel('Value', fontweight='bold')
ax.set_title('(d) Performance Metrics Comparison', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=9)
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 添加改进百分比
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    if default_vals[i] > 0:
        improvement = (default_vals[i] - best_vals[i]) / default_vals[i] * 100
        if improvement > 0:
            ax.text(i, max(default_vals[i], best_vals[i]) + 0.5, f'{improvement:.0f}%↓',
                   ha='center', fontsize=8, color='green', fontweight='bold')

plt.suptitle(f'Optimal PID Performance (Kp={best_result["Kp"]:.2f}, Ki={best_result["Ki"]:.2f}, Kd={best_result["Kd"]:.2f})',
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('pid_optimal_performance.png', dpi=150, bbox_inches='tight')
print("✓ pid_optimal_performance.png")

print()
print("="*80)
print("  PID参数优化完成!")
print("="*80)
print()
print("生成的文件:")
print("  1. pid_tuning_results.txt - 优化结果报告")
print("  2. pid_tuning_comparison.png - 不同参数对比(6子图)")
print("  3. pid_optimal_performance.png - 最优参数性能(4子图)")
print()
print("下一步:")
print("  1. 查看报告了解最优参数")
print("  2. 在dynamic_design_L2.py中应用最优参数")
print("  3. 重新运行测试验证性能")
print()
print("="*80)
