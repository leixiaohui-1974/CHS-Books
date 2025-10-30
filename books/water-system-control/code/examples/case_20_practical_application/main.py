"""
案例20：实际应用 - 控制器的工程实现

本程序演示控制器的工程实现，包括模块化架构、状态机、故障处理等
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from enum import Enum
from collections import deque
import logging

# 配置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

print("=" * 80)
print("案例20：实际应用 - 控制器的工程实现")
print("=" * 80)

# ============================================================================
# Part 1: 基础组件 - 传感器、执行器、滤波器
# ============================================================================

print("\n" + "=" * 80)
print("Part 1: 基础组件 - 传感器、执行器、滤波器")
print("=" * 80)

class FaultType(Enum):
    """故障类型枚举"""
    NONE = 0
    OUT_OF_RANGE = 1
    RATE_LIMIT = 2
    STUCK = 3
    NOISE = 4

class State(Enum):
    """控制器状态枚举"""
    IDLE = 0
    INIT = 1
    READY = 2
    RUN = 3
    ERROR = 4
    STOP = 5

class MovingAverageFilter:
    """移动平均滤波器"""
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self.logger = logging.getLogger('Filter')

    def update(self, value):
        self.buffer.append(value)
        filtered = np.mean(self.buffer)
        return filtered

    def reset(self):
        self.buffer.clear()

class Sensor:
    """传感器类 - 包含标定、滤波、故障检测"""
    def __init__(self, name, calibration=(1.0, 0.0), range_limit=(0.0, 4.0), filter_window=5):
        self.name = name
        self.k, self.b = calibration  # 标定参数
        self.y_min, self.y_max = range_limit
        self.filter = MovingAverageFilter(filter_window)
        self.history = deque(maxlen=20)
        self.fault = FaultType.NONE
        self.logger = logging.getLogger(f'Sensor.{name}')

    def read(self, raw_value, noise_level=0.0):
        """读取传感器值"""
        # 添加噪声模拟真实传感器
        noisy_value = raw_value + np.random.normal(0, noise_level)

        # 标定
        calibrated = self.k * noisy_value + self.b

        # 滤波
        filtered = self.filter.update(calibrated)

        # 故障检测
        self.fault = self.check_fault(filtered)
        if self.fault != FaultType.NONE:
            self.logger.warning(f"故障检测: {self.fault.name}, 值={filtered:.3f}")

        # 记录历史
        self.history.append(filtered)

        return filtered

    def check_fault(self, value):
        """故障检测"""
        # 1. 范围检查
        if value < self.y_min or value > self.y_max:
            return FaultType.OUT_OF_RANGE

        # 2. 固定值检查（传感器卡死）
        if len(self.history) >= 10:
            std = np.std(list(self.history)[-10:])
            if std < 0.001:
                return FaultType.STUCK

        # 3. 变化率检查
        if len(self.history) >= 2:
            dy = abs(value - self.history[-1])
            if dy > 0.5:  # 液位不可能突变
                return FaultType.RATE_LIMIT

        return FaultType.NONE

    def reset(self):
        """重置传感器"""
        self.filter.reset()
        self.history.clear()
        self.fault = FaultType.NONE

class Actuator:
    """执行器类 - 包含限幅、死区、延迟模拟"""
    def __init__(self, name, limits=(0.0, 10.0), dead_zone=0.1):
        self.name = name
        self.u_min, self.u_max = limits
        self.dead_zone = dead_zone
        self.current_value = 0.0
        self.saturation_flag = False
        self.logger = logging.getLogger(f'Actuator.{name}')

    def set(self, command):
        """设置执行器输出"""
        # 死区处理
        if abs(command) < self.dead_zone:
            actual = 0.0
        else:
            actual = command

        # 限幅
        self.saturation_flag = False
        if actual > self.u_max:
            actual = self.u_max
            self.saturation_flag = True
            self.logger.warning(f"饱和: 命令={command:.3f} > 上限={self.u_max}")
        elif actual < self.u_min:
            actual = self.u_min
            self.saturation_flag = True
            self.logger.warning(f"饱和: 命令={command:.3f} < 下限={self.u_min}")

        self.current_value = actual
        return actual

    def is_saturated(self):
        """检查是否饱和"""
        return self.saturation_flag

# 演示传感器和执行器
print("\n[演示1：传感器标定和滤波]")
sensor = Sensor("LevelSensor", calibration=(1.0, 0.0), range_limit=(0.0, 4.0))
raw_values = [1.0, 1.05, 0.95, 1.1, 0.9, 1.0]
print(f"{'原始值':<10} {'标定值':<10} {'滤波值':<10}")
print("-" * 30)
for raw in raw_values:
    filtered = sensor.read(raw, noise_level=0.05)
    print(f"{raw:<10.3f} {raw:<10.3f} {filtered:<10.3f}")

print("\n[演示2：执行器限幅和死区]")
actuator = Actuator("Pump", limits=(0.0, 10.0), dead_zone=0.1)
commands = [-1.0, 0.05, 2.0, 8.0, 12.0]
print(f"{'命令值':<10} {'实际输出':<10} {'是否饱和':<10}")
print("-" * 30)
for cmd in commands:
    actual = actuator.set(cmd)
    saturated = "是" if actuator.is_saturated() else "否"
    print(f"{cmd:<10.2f} {actual:<10.2f} {saturated:<10}")

# ============================================================================
# Part 2: 控制器类 - 带抗饱和的PID
# ============================================================================

print("\n" + "=" * 80)
print("Part 2: 控制器类 - 带抗饱和的PID")
print("=" * 80)

class PIDController:
    """PID控制器 - 带抗饱和功能"""
    def __init__(self, Kp=8.0, Ki=2.0, Kd=4.0, dt=0.1, u_limits=(0.0, 10.0)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.u_min, self.u_max = u_limits

        self.integral = 0.0
        self.prev_error = 0.0
        self.logger = logging.getLogger('PID')

    def compute(self, error, anti_windup=True):
        """计算控制量"""
        # 比例项
        p_term = self.Kp * error

        # 积分项
        self.integral += error * self.dt
        i_term = self.Ki * self.integral

        # 微分项
        derivative = (error - self.prev_error) / self.dt
        d_term = self.Kd * derivative

        # 理想控制量
        u_ideal = p_term + i_term + d_term

        # 抗饱和处理
        if u_ideal > self.u_max:
            u_actual = self.u_max
            if anti_windup:
                # 反算法：调整积分项
                self.integral = (self.u_max - p_term - d_term) / self.Ki
        elif u_ideal < self.u_min:
            u_actual = self.u_min
            if anti_windup:
                self.integral = (self.u_min - p_term - d_term) / self.Ki
        else:
            u_actual = u_ideal

        self.prev_error = error
        return u_actual

    def reset(self):
        """重置控制器"""
        self.integral = 0.0
        self.prev_error = 0.0

# 演示抗饱和效果
print("\n[演示：有/无抗饱和对比]")

class SimpleSystem:
    """简单水箱系统"""
    def __init__(self, A=3.0, R=2.0, dt=0.1):
        self.A = A
        self.R = R
        self.dt = dt
        self.h = 0.0

    def step(self, u):
        dhdt = (u - self.h / self.R) / self.A
        self.h += dhdt * self.dt
        self.h = np.clip(self.h, 0, 4.0)
        return self.h

# 测试：大设定值，观察超调
T_test = 30
dt = 0.1
N_test = int(T_test / dt)
t_test = np.linspace(0, T_test, N_test)
target = 3.5  # 接近上限

results_windup = {}
for anti_windup_enabled in [False, True]:
    system = SimpleSystem()
    controller = PIDController(Kp=8, Ki=2, Kd=4, dt=dt, u_limits=(0, 10))

    y = np.zeros(N_test)
    u = np.zeros(N_test)

    for i in range(N_test):
        y[i] = system.h
        error = target - y[i]
        u[i] = controller.compute(error, anti_windup=anti_windup_enabled)
        if i < N_test - 1:
            system.step(u[i])

    label = "抗饱和" if anti_windup_enabled else "无抗饱和"
    results_windup[label] = {'y': y, 'u': u}

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 液位
axes[0].axhline(target, color='black', linestyle='--', linewidth=2, label='设定值')
for label, result in results_windup.items():
    axes[0].plot(t_test, result['y'], label=label, linewidth=2)
axes[0].set_ylabel('液位 h (m)')
axes[0].set_title('抗饱和效果对比', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 控制量
for label, result in results_windup.items():
    axes[1].plot(t_test, result['u'], label=label, linewidth=2)
axes[1].axhline(10, color='red', linestyle=':', linewidth=1, label='饱和上限')
axes[1].set_xlabel('时间 (s)')
axes[1].set_ylabel('控制量 u (m³/min)')
axes[1].set_title('控制量对比', fontsize=12, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('anti_windup_comparison.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：anti_windup_comparison.png")

# 计算超调量
for label, result in results_windup.items():
    overshoot = (np.max(result['y']) - target) / target * 100
    print(f"{label}: 超调量 = {overshoot:.2f}%")

# ============================================================================
# Part 3: 状态机实现
# ============================================================================

print("\n" + "=" * 80)
print("Part 3: 状态机实现")
print("=" * 80)

class ControllerStateMachine:
    """控制器状态机"""
    def __init__(self):
        self.state = State.IDLE
        self.logger = logging.getLogger('StateMachine')

    def transition(self, event):
        """状态转移"""
        old_state = self.state

        if self.state == State.IDLE:
            if event == 'start':
                self.state = State.INIT
        elif self.state == State.INIT:
            if event == 'init_success':
                self.state = State.READY
            elif event == 'init_fail':
                self.state = State.ERROR
        elif self.state == State.READY:
            if event == 'run':
                self.state = State.RUN
        elif self.state == State.RUN:
            if event == 'fault':
                self.state = State.ERROR
            elif event == 'stop':
                self.state = State.STOP
        elif self.state == State.ERROR:
            if event == 'recover':
                self.state = State.READY
            elif event == 'critical':
                self.state = State.STOP
        elif self.state == State.STOP:
            if event == 'restart':
                self.state = State.IDLE

        if old_state != self.state:
            self.logger.info(f"状态转移: {old_state.name} -> {self.state.name}")

    def get_state(self):
        return self.state

# 演示状态机
print("\n[演示：状态机转移]")
sm = ControllerStateMachine()

events = ['start', 'init_success', 'run', 'fault', 'recover', 'run', 'stop', 'restart']
for event in events:
    sm.transition(event)
    time.sleep(0.1)

# ============================================================================
# Part 4: 完整的控制系统 - 集成所有组件
# ============================================================================

print("\n" + "=" * 80)
print("Part 4: 完整的控制系统 - 集成所有组件")
print("=" * 80)

class WaterTankControlSystem:
    """完整的水箱控制系统"""
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('ControlSystem')

        # 创建组件
        self.sensor = Sensor(
            "LevelSensor",
            calibration=config['sensor']['calibration'],
            range_limit=config['sensor']['range_limit'],
            filter_window=config['sensor']['filter_window']
        )

        self.actuator = Actuator(
            "Pump",
            limits=config['actuator']['limits'],
            dead_zone=config['actuator']['dead_zone']
        )

        self.controller = PIDController(
            Kp=config['controller']['Kp'],
            Ki=config['controller']['Ki'],
            Kd=config['controller']['Kd'],
            dt=config['controller']['dt'],
            u_limits=config['actuator']['limits']
        )

        self.state_machine = ControllerStateMachine()

        # 系统模型（真实硬件中这是物理系统）
        self.system = SimpleSystem(
            A=config['system']['A'],
            R=config['system']['R'],
            dt=config['controller']['dt']
        )

        # 数据记录
        self.data_log = {
            't': [],
            'h': [],
            'sp': [],
            'u': [],
            'state': []
        }

    def initialize(self):
        """初始化系统"""
        self.logger.info("开始初始化...")
        self.state_machine.transition('start')

        # 自检
        try:
            # 传感器自检
            test_value = self.sensor.read(0.0)
            self.logger.info(f"传感器自检: {test_value:.3f} m")

            # 执行器自检
            self.actuator.set(0.0)
            self.logger.info("执行器自检通过")

            self.state_machine.transition('init_success')
            self.logger.info("初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            self.state_machine.transition('init_fail')
            return False

    def run(self, setpoint, duration, fault_scenarios=None):
        """运行控制系统"""
        if self.state_machine.get_state() != State.READY:
            self.logger.error("系统未就绪，无法运行")
            return

        self.state_machine.transition('run')
        self.logger.info(f"开始运行，设定值={setpoint} m，时长={duration} s")

        dt = self.config['controller']['dt']
        N = int(duration / dt)

        for i in range(N):
            current_time = i * dt

            # 读取传感器
            noise_level = 0.02  # 正常噪声
            if fault_scenarios and 'sensor_noise' in fault_scenarios:
                if fault_scenarios['sensor_noise']['start'] <= current_time < fault_scenarios['sensor_noise']['end']:
                    noise_level = fault_scenarios['sensor_noise']['level']
                    self.logger.warning(f"传感器噪声增大: {noise_level}")

            h = self.sensor.read(self.system.h, noise_level=noise_level)

            # 故障检测
            if self.sensor.fault != FaultType.NONE:
                self.state_machine.transition('fault')
                self.logger.error(f"检测到传感器故障: {self.sensor.fault.name}")
                # 简化处理：使用上一次的值
                if len(self.data_log['h']) > 0:
                    h = self.data_log['h'][-1]

            # 计算控制量
            error = setpoint - h
            u_command = self.controller.compute(error, anti_windup=True)

            # 设置执行器
            u_actual = self.actuator.set(u_command)

            # 执行器饱和检测
            if self.actuator.is_saturated():
                self.logger.debug(f"执行器饱和: 命令={u_command:.2f}, 实际={u_actual:.2f}")

            # 更新系统
            self.system.step(u_actual)

            # 记录数据
            self.data_log['t'].append(current_time)
            self.data_log['h'].append(h)
            self.data_log['sp'].append(setpoint)
            self.data_log['u'].append(u_actual)
            self.data_log['state'].append(self.state_machine.get_state().name)

            # 模拟实时控制（可选）
            # time.sleep(dt)

        self.state_machine.transition('stop')
        self.logger.info("运行结束")

    def plot_results(self):
        """绘制结果"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        t = np.array(self.data_log['t'])
        h = np.array(self.data_log['h'])
        sp = np.array(self.data_log['sp'])
        u = np.array(self.data_log['u'])

        # 液位
        axes[0].plot(t, sp, 'k--', linewidth=2, label='设定值')
        axes[0].plot(t, h, 'b-', linewidth=1.5, label='实际值')
        axes[0].set_ylabel('液位 h (m)')
        axes[0].set_title('完整控制系统运行结果', fontsize=14, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 控制量
        axes[1].plot(t, u, 'g-', linewidth=1.5)
        axes[1].axhline(self.config['actuator']['limits'][1], color='r', linestyle=':', label='上限')
        axes[1].axhline(self.config['actuator']['limits'][0], color='r', linestyle=':', label='下限')
        axes[1].set_ylabel('控制量 u (m³/min)')
        axes[1].set_title('控制量', fontsize=12, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # 误差
        error = sp - h
        axes[2].plot(t, error, 'r-', linewidth=1.5)
        axes[2].axhline(0, color='k', linestyle='--', linewidth=1)
        axes[2].set_xlabel('时间 (s)')
        axes[2].set_ylabel('误差 e (m)')
        axes[2].set_title('跟踪误差', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('complete_control_system.png', dpi=150, bbox_inches='tight')
        print("\n图表已保存：complete_control_system.png")

# 配置参数
config = {
    'system': {
        'A': 3.0,
        'R': 2.0
    },
    'sensor': {
        'calibration': (1.0, 0.0),
        'range_limit': (0.0, 4.0),
        'filter_window': 5
    },
    'actuator': {
        'limits': (0.0, 10.0),
        'dead_zone': 0.1
    },
    'controller': {
        'Kp': 8.0,
        'Ki': 2.0,
        'Kd': 4.0,
        'dt': 0.1
    }
}

# 创建并运行系统
print("\n[场景1：正常运行]")
control_system = WaterTankControlSystem(config)
control_system.initialize()
control_system.run(setpoint=2.0, duration=30)
control_system.plot_results()

# ============================================================================
# Part 5: 故障场景测试
# ============================================================================

print("\n" + "=" * 80)
print("Part 5: 故障场景测试")
print("=" * 80)

print("\n[场景2：传感器噪声故障]")
control_system2 = WaterTankControlSystem(config)
control_system2.initialize()

fault_scenarios = {
    'sensor_noise': {
        'start': 15.0,
        'end': 20.0,
        'level': 0.2  # 噪声显著增大
    }
}

control_system2.run(setpoint=2.0, duration=30, fault_scenarios=fault_scenarios)

# 绘制对比
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 正常 vs 故障
t1 = np.array(control_system.data_log['t'])
h1 = np.array(control_system.data_log['h'])
t2 = np.array(control_system2.data_log['t'])
h2 = np.array(control_system2.data_log['h'])

axes[0].plot(t1, h1, 'b-', linewidth=1.5, label='正常运行', alpha=0.7)
axes[0].plot(t2, h2, 'r-', linewidth=1.5, label='传感器噪声故障', alpha=0.7)
axes[0].axhline(2.0, color='k', linestyle='--', linewidth=2, label='设定值')
axes[0].axvspan(15, 20, alpha=0.2, color='red', label='故障区间')
axes[0].set_ylabel('液位 h (m)')
axes[0].set_title('故障场景测试：传感器噪声', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 噪声放大
axes[1].plot(t2, h2, 'r-', linewidth=1, alpha=0.7)
axes[1].axvspan(15, 20, alpha=0.2, color='red', label='故障区间')
axes[1].set_xlabel('时间 (s)')
axes[1].set_ylabel('液位 h (m)')
axes[1].set_title('传感器噪声细节', fontsize=12, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim([1.8, 2.2])

plt.tight_layout()
plt.savefig('fault_scenario_sensor_noise.png', dpi=150, bbox_inches='tight')
print("\n图表已保存：fault_scenario_sensor_noise.png")

print("\n" + "=" * 80)
print("完整控制系统演示完成！")
print("=" * 80)

print("\n主要功能：")
print("1. 传感器：标定、滤波、故障检测")
print("2. 执行器：限幅、死区、饱和检测")
print("3. 控制器：PID + 抗饱和")
print("4. 状态机：完整的状态管理")
print("5. 系统集成：模块化架构")
print("6. 故障处理：传感器噪声故障测试")
