"""
案例20扩展实验：工程实现的深入研究

本程序进行更深入的实验：
1. 传感器标定实验
2. 滤波器对比（移动平均、指数平滑、卡尔曼滤波）
3. 抗饱和策略深入对比
4. 多故障场景的综合测试
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# 配置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("案例20扩展实验：工程实现深入研究")
print("=" * 80)

# ============================================================================
# 实验1：传感器标定实验
# ============================================================================

print("\n" + "=" * 80)
print("实验1：传感器标定实验")
print("=" * 80)

print("\n[测试：通过已知物理量标定传感器]")

# 模拟原始传感器数据（ADC值）和对应的真实物理量
known_physical = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
raw_readings = np.array([12, 124, 235, 351, 462, 575, 688, 799, 910])

# 线性拟合求标定参数
coeffs = np.polyfit(raw_readings, known_physical, 1)
k_calib, b_calib = coeffs[0], coeffs[1]

print(f"\n标定结果：")
print(f"  斜率 k = {k_calib:.6f}")
print(f"  截距 b = {b_calib:.6f}")
print(f"  标定公式：y_physical = {k_calib:.6f} * ADC + {b_calib:.6f}")

# 验证标定精度
fitted_physical = k_calib * raw_readings + b_calib
residuals = known_physical - fitted_physical
rmse = np.sqrt(np.mean(residuals**2))
print(f"\n标定精度：RMSE = {rmse:.6f} m")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：标定曲线
axes[0].scatter(raw_readings, known_physical, s=100, c='blue', label='标定点', zorder=3)
raw_line = np.linspace(0, 1000, 100)
physical_line = k_calib * raw_line + b_calib
axes[0].plot(raw_line, physical_line, 'r--', linewidth=2, label=f'拟合线: y={k_calib:.4f}x+{b_calib:.3f}')
axes[0].set_xlabel('原始读数 (ADC)', fontsize=12)
axes[0].set_ylabel('物理量 (m)', fontsize=12)
axes[0].set_title('实验1：传感器标定曲线', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 右图：残差
axes[1].bar(range(len(residuals)), residuals, color='green', alpha=0.7)
axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
axes[1].set_xlabel('标定点序号', fontsize=12)
axes[1].set_ylabel('残差 (m)', fontsize=12)
axes[1].set_title('标定残差分析', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('exp1_sensor_calibration.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：exp1_sensor_calibration.png")

# ============================================================================
# 实验2：滤波器对比
# ============================================================================

print("\n" + "=" * 80)
print("实验2：滤波器对比")
print("=" * 80)

class MovingAverageFilter:
    """移动平均滤波器"""
    def __init__(self, window_size=5):
        self.buffer = deque(maxlen=window_size)
    def update(self, value):
        self.buffer.append(value)
        return np.mean(self.buffer)
    def reset(self):
        self.buffer.clear()

class ExponentialFilter:
    """指数平滑滤波器"""
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.value = None
    def update(self, measurement):
        if self.value is None:
            self.value = measurement
        else:
            self.value = self.alpha * measurement + (1 - self.alpha) * self.value
        return self.value
    def reset(self):
        self.value = None

class SimpleKalmanFilter:
    """简化的卡尔曼滤波器（一维）"""
    def __init__(self, process_variance=1e-3, measurement_variance=0.1**2):
        self.Q = process_variance  # 过程噪声方差
        self.R = measurement_variance  # 测量噪声方差
        self.x = 0.0  # 估计值
        self.P = 1.0  # 估计误差协方差

    def update(self, measurement):
        # 预测步骤
        x_pred = self.x
        P_pred = self.P + self.Q

        # 更新步骤
        K = P_pred / (P_pred + self.R)  # 卡尔曼增益
        self.x = x_pred + K * (measurement - x_pred)
        self.P = (1 - K) * P_pred

        return self.x

    def reset(self):
        self.x = 0.0
        self.P = 1.0

# 生成测试信号：真实值 + 噪声
N = 200
t = np.linspace(0, 20, N)
true_signal = 2.0 + 0.5 * np.sin(2 * np.pi * 0.2 * t)  # 缓慢变化的信号
noise = np.random.normal(0, 0.2, N)
noisy_signal = true_signal + noise

# 应用不同滤波器
filters = {
    '移动平均(5)': MovingAverageFilter(window_size=5),
    '指数平滑(α=0.3)': ExponentialFilter(alpha=0.3),
    '卡尔曼滤波': SimpleKalmanFilter(process_variance=1e-3, measurement_variance=0.04)
}

filtered_results = {}
for name, filt in filters.items():
    filtered = np.zeros(N)
    for i in range(N):
        filtered[i] = filt.update(noisy_signal[i])
    filtered_results[name] = filtered

# 计算性能指标
print("\n[滤波器性能对比]")
print("-" * 70)
print(f"{'滤波器':<20} {'RMSE':<15} {'延迟(样本)':<15}")
print("-" * 70)

for name, filtered in filtered_results.items():
    rmse = np.sqrt(np.mean((filtered - true_signal)**2))

    # 估算延迟：找到上升沿响应的50%点
    idx_start = 50  # 信号开始上升的点
    idx_half = np.where(filtered[idx_start:] >= (true_signal[idx_start] + true_signal[idx_start+20])/2)[0]
    if len(idx_half) > 0:
        delay = idx_half[0]
    else:
        delay = 0

    print(f"{name:<20} {rmse:<15.4f} {delay:<15}")

# 可视化
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 上图：滤波效果
axes[0].plot(t, true_signal, 'k-', linewidth=2, label='真实信号', zorder=3)
axes[0].plot(t, noisy_signal, 'gray', linewidth=0.5, alpha=0.5, label='噪声信号')
colors = ['blue', 'red', 'green']
for (name, filtered), color in zip(filtered_results.items(), colors):
    axes[0].plot(t, filtered, linewidth=2, label=name, color=color)
axes[0].set_ylabel('信号值', fontsize=12)
axes[0].set_title('实验2：滤波器效果对比', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# 下图：误差分析
for (name, filtered), color in zip(filtered_results.items(), colors):
    error = filtered - true_signal
    axes[1].plot(t, error, linewidth=1.5, label=name, color=color)
axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
axes[1].set_xlabel('时间 (s)', fontsize=12)
axes[1].set_ylabel('滤波误差', fontsize=12)
axes[1].set_title('滤波误差对比', fontsize=12, fontweight='bold')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exp2_filter_comparison.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：exp2_filter_comparison.png")

print("\n结论：")
print("  - 移动平均：简单有效，但有延迟")
print("  - 指数平滑：延迟小，但对突变响应慢")
print("  - 卡尔曼滤波：综合性能最优，跟踪能力强")

# ============================================================================
# 实验3：抗饱和策略深入对比
# ============================================================================

print("\n" + "=" * 80)
print("实验3：抗饱和策略深入对比")
print("=" * 80)

class PIDWithAntiWindup:
    """带不同抗饱和策略的PID"""
    def __init__(self, Kp, Ki, Kd, dt, u_limits, strategy='none'):
        self.Kp, self.Ki, self.Kd, self.dt = Kp, Ki, Kd, dt
        self.u_min, self.u_max = u_limits
        self.strategy = strategy
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, error):
        p_term = self.Kp * error
        d_term = self.Kd * (error - self.prev_error) / self.dt

        if self.strategy == 'none':
            # 无抗饱和
            self.integral += error * self.dt
            i_term = self.Ki * self.integral
            u = p_term + i_term + d_term
            u = np.clip(u, self.u_min, self.u_max)

        elif self.strategy == 'conditional':
            # 条件积分：饱和时停止积分
            u_unsat = p_term + self.Ki * self.integral + d_term
            if not (u_unsat > self.u_max or u_unsat < self.u_min):
                self.integral += error * self.dt
            i_term = self.Ki * self.integral
            u = p_term + i_term + d_term
            u = np.clip(u, self.u_min, self.u_max)

        elif self.strategy == 'back_calculation':
            # 反算法
            self.integral += error * self.dt
            i_term = self.Ki * self.integral
            u_unsat = p_term + i_term + d_term
            u = np.clip(u_unsat, self.u_min, self.u_max)
            # 反算调整积分项
            if u != u_unsat:
                self.integral = (u - p_term - d_term) / self.Ki

        elif self.strategy == 'clamping':
            # 积分限幅
            self.integral += error * self.dt
            integral_limit = 5.0
            self.integral = np.clip(self.integral, -integral_limit, integral_limit)
            i_term = self.Ki * self.integral
            u = p_term + i_term + d_term
            u = np.clip(u, self.u_min, self.u_max)

        self.prev_error = error
        return u

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

# 简单系统
class SimpleSystem:
    def __init__(self, A=3.0, R=2.0, dt=0.1):
        self.A, self.R, self.dt = A, R, dt
        self.h = 0.0
    def step(self, u):
        dhdt = (u - self.h / self.R) / self.A
        self.h += dhdt * self.dt
        self.h = np.clip(self.h, 0, 4.0)
        return self.h

# 测试场景：大设定值 + 阶跃变化
T = 60
dt = 0.1
N = int(T / dt)
t = np.linspace(0, T, N)
setpoint = np.ones(N) * 3.5
setpoint[300:] = 1.5  # 阶跃变化

strategies = ['none', 'conditional', 'back_calculation', 'clamping']
strategy_names = {
    'none': '无抗饱和',
    'conditional': '条件积分',
    'back_calculation': '反算法',
    'clamping': '积分限幅'
}

results_antiwindup = {}

for strategy in strategies:
    system = SimpleSystem()
    pid = PIDWithAntiWindup(Kp=8, Ki=2, Kd=4, dt=dt, u_limits=(0, 10), strategy=strategy)

    y = np.zeros(N)
    u = np.zeros(N)

    for i in range(N):
        y[i] = system.h
        error = setpoint[i] - y[i]
        u[i] = pid.compute(error)
        if i < N - 1:
            system.step(u[i])

    results_antiwindup[strategy_names[strategy]] = {'y': y, 'u': u}

# 可视化
fig, axes = plt.subplots(3, 1, figsize=(14, 11))

colors = ['gray', 'blue', 'red', 'green']

# 液位
axes[0].plot(t, setpoint, 'k--', linewidth=2, label='设定值')
axes[0].axvline(30, color='orange', linestyle=':', linewidth=2, label='设定值变化')
for (name, result), color in zip(results_antiwindup.items(), colors):
    axes[0].plot(t, result['y'], label=name, linewidth=1.5, color=color, alpha=0.8)
axes[0].set_ylabel('液位 h (m)', fontsize=12)
axes[0].set_title('实验3：抗饱和策略对比', fontsize=14, fontweight='bold')
axes[0].legend(loc='right')
axes[0].grid(True, alpha=0.3)

# 控制量
axes[1].axhline(10, color='red', linestyle=':', linewidth=1, label='饱和上限')
axes[1].axvline(30, color='orange', linestyle=':', linewidth=2)
for (name, result), color in zip(results_antiwindup.items(), colors):
    axes[1].plot(t, result['u'], label=name, linewidth=1.5, color=color, alpha=0.8)
axes[1].set_ylabel('控制量 u (m³/min)', fontsize=12)
axes[1].set_title('控制量对比', fontsize=12, fontweight='bold')
axes[1].legend(loc='right')
axes[1].grid(True, alpha=0.3)

# 放大设定值变化后的响应
t_zoom = t[300:400]
axes[2].axhline(1.5, color='k', linestyle='--', linewidth=2, label='新设定值')
for (name, result), color in zip(results_antiwindup.items(), colors):
    axes[2].plot(t_zoom, result['y'][300:400], label=name, linewidth=2, color=color, alpha=0.8)
axes[2].set_xlabel('时间 (s)', fontsize=12)
axes[2].set_ylabel('液位 h (m)', fontsize=12)
axes[2].set_title('设定值变化后的响应（放大）', fontsize=12, fontweight='bold')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exp3_antiwindup_strategies.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：exp3_antiwindup_strategies.png")

# 计算性能指标
print("\n[抗饱和策略性能]")
print("-" * 70)
print(f"{'策略':<15} {'第一段超调(%)':<18} {'第二段调节时间(s)':<20}")
print("-" * 70)

for name, result in results_antiwindup.items():
    # 第一段超调
    overshoot1 = (np.max(result['y'][:300]) - setpoint[0]) / setpoint[0] * 100

    # 第二段调节时间
    tolerance = 0.02 * setpoint[300]
    settled = np.where(np.abs(result['y'][300:] - setpoint[300]) < tolerance)[0]
    if len(settled) > 0:
        settling_time2 = settled[0] * dt
    else:
        settling_time2 = (N - 300) * dt

    print(f"{name:<15} {overshoot1:<18.2f} {settling_time2:<20.2f}")

print("\n结论：")
print("  - 无抗饱和：超调大，恢复慢")
print("  - 条件积分：改善明显，简单有效")
print("  - 反算法：性能最优，工程常用")
print("  - 积分限幅：折中方案，易于实现")

# ============================================================================
# 实验4：多故障场景综合测试
# ============================================================================

print("\n" + "=" * 80)
print("实验4：多故障场景综合测试")
print("=" * 80)

print("\n[测试：传感器故障、执行器饱和、通信延迟]")

class RobustControlSystem:
    """鲁棒控制系统 - 带故障处理"""
    def __init__(self):
        self.system = SimpleSystem()
        self.pid = PIDWithAntiWindup(Kp=8, Ki=2, Kd=4, dt=0.1, u_limits=(0, 10), strategy='back_calculation')
        self.filter = SimpleKalmanFilter()
        self.h_estimate = 0.0
        self.fault_count = 0

    def run(self, setpoint, duration, faults=None):
        dt = 0.1
        N = int(duration / dt)
        t = np.linspace(0, duration, N)

        y_raw = np.zeros(N)
        y_filtered = np.zeros(N)
        u = np.zeros(N)
        fault_flags = np.zeros(N)

        for i in range(N):
            current_time = i * dt

            # 读取传感器（可能有故障）
            y_true = self.system.h
            y_measured = y_true

            # 故障注入
            if faults:
                # 传感器噪声
                if 'sensor_noise' in faults and faults['sensor_noise']['start'] <= current_time < faults['sensor_noise']['end']:
                    y_measured += np.random.normal(0, faults['sensor_noise']['level'])
                    fault_flags[i] = 1

                # 传感器偏置
                if 'sensor_bias' in faults and faults['sensor_bias']['start'] <= current_time < faults['sensor_bias']['end']:
                    y_measured += faults['sensor_bias']['bias']
                    fault_flags[i] = 2

                # 执行器饱和（故意的控制量限制）
                if 'actuator_limit' in faults and faults['actuator_limit']['start'] <= current_time < faults['actuator_limit']['end']:
                    self.pid.u_max = faults['actuator_limit']['limit']
                    fault_flags[i] = 3
                else:
                    self.pid.u_max = 10.0

            # 滤波
            y_filt = self.filter.update(y_measured)

            # 计算控制量
            error = setpoint - y_filt
            u_command = self.pid.compute(error)

            # 更新系统
            self.system.step(u_command)

            # 记录
            y_raw[i] = y_measured
            y_filtered[i] = y_filt
            u[i] = u_command

        return t, y_raw, y_filtered, u, fault_flags

# 运行测试
system = RobustControlSystem()
faults = {
    'sensor_noise': {'start': 10, 'end': 15, 'level': 0.3},
    'sensor_bias': {'start': 25, 'end': 30, 'bias': 0.5},
    'actuator_limit': {'start': 40, 'end': 45, 'limit': 5.0}
}

t, y_raw, y_filtered, u, fault_flags = system.run(setpoint=2.0, duration=60, faults=faults)

# 可视化
fig, axes = plt.subplots(3, 1, figsize=(14, 11))

# 液位
axes[0].axhline(2.0, color='k', linestyle='--', linewidth=2, label='设定值')
axes[0].plot(t, y_raw, 'gray', linewidth=0.5, alpha=0.5, label='原始测量')
axes[0].plot(t, y_filtered, 'b-', linewidth=2, label='滤波后')

# 标注故障区间
axes[0].axvspan(10, 15, alpha=0.2, color='red', label='传感器噪声')
axes[0].axvspan(25, 30, alpha=0.2, color='orange', label='传感器偏置')
axes[0].axvspan(40, 45, alpha=0.2, color='purple', label='执行器限制')

axes[0].set_ylabel('液位 h (m)', fontsize=12)
axes[0].set_title('实验4：多故障场景综合测试', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper right', fontsize=9)
axes[0].grid(True, alpha=0.3)

# 控制量
axes[1].plot(t, u, 'g-', linewidth=2)
axes[1].axhline(10, color='r', linestyle=':', label='正常上限')
axes[1].axhline(5, color='purple', linestyle=':', label='故障上限')
axes[1].axvspan(40, 45, alpha=0.2, color='purple')
axes[1].set_ylabel('控制量 u (m³/min)', fontsize=12)
axes[1].set_title('控制量响应', fontsize=12, fontweight='bold')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# 故障标志
axes[2].plot(t, fault_flags, 'r-', linewidth=2, drawstyle='steps-post')
axes[2].set_xlabel('时间 (s)', fontsize=12)
axes[2].set_ylabel('故障类型', fontsize=12)
axes[2].set_yticks([0, 1, 2, 3])
axes[2].set_yticklabels(['正常', '传感器噪声', '传感器偏置', '执行器限制'])
axes[2].set_title('故障检测标志', fontsize=12, fontweight='bold')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exp4_fault_scenarios.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：exp4_fault_scenarios.png")

print("\n结论：")
print("  - 卡尔曼滤波有效抑制传感器噪声")
print("  - 传感器偏置需要故障检测和隔离")
print("  - 抗饱和策略确保执行器受限时性能")
print("  - 需要多层次的故障处理机制")

print("\n" + "=" * 80)
print("所有扩展实验完成！")
print("=" * 80)

print("\n关键收获：")
print("1. 传感器标定是保证测量精度的基础")
print("2. 卡尔曼滤波综合性能最优，值得学习")
print("3. 抗饱和必不可少，反算法工程常用")
print("4. 实际系统需要考虑多种故障模式")
print("5. 鲁棒设计：预防为主，检测为辅，恢复为要")
