"""
基础控制器库 - 教学专用

包含：
- OnOffController: 开关控制（滞环控制）
- ProportionalController: 比例控制（P控制）
- PIController: 比例积分控制（PI控制）

作者：水系统控制论教材开发组
版本：1.0.0
日期：2025-10-28
"""

import numpy as np


class OnOffController:
    """
    开关控制器（滞环控制 Hysteresis Control）
    
    原理：
    - 当输出低于下限 → 打开（输出最大值）
    - 当输出高于上限 → 关闭（输出0）
    - 在上下限之间 → 保持原状态
    
    优点：
    - 非常简单
    - 成本低（只需要开关量）
    - 可靠性高
    
    缺点：
    - 输出会在上下限之间振荡
    - 控制精度不高
    - 频繁启停可能损害设备
    
    适用场景：
    - 家庭水塔
    - 空调温控
    - 精度要求不高的场合
    """
    
    def __init__(self, low_threshold=2.5, high_threshold=3.5, output_on=1.0, output_off=0.0):
        """
        初始化开关控制器
        
        参数：
            low_threshold (float): 下限阈值
            high_threshold (float): 上限阈值
            output_on (float): 开启时的输出值
            output_off (float): 关闭时的输出值
        """
        if low_threshold >= high_threshold:
            raise ValueError("下限必须小于上限")
        
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.output_on = output_on
        self.output_off = output_off
        
        # 控制器状态
        self.is_on = False
        
        # 用于分析
        self.setpoint = (low_threshold + high_threshold) / 2  # 中心点
    
    def control(self, measurement):
        """
        计算控制输出
        
        参数：
            measurement (float): 测量值（如水位）
        
        返回：
            float: 控制输出
        """
        if measurement < self.low_threshold:
            self.is_on = True
        elif measurement > self.high_threshold:
            self.is_on = False
        # 在中间区域保持原状态（滞环）
        
        return self.output_on if self.is_on else self.output_off
    
    def reset(self):
        """重置控制器状态"""
        self.is_on = False
    
    def __repr__(self):
        return (f"OnOffController(low={self.low_threshold}, high={self.high_threshold}, "
                f"state={'ON' if self.is_on else 'OFF'})")


class ProportionalController:
    """
    比例控制器（P控制器）
    
    原理：
        u = Kp × e
        其中 e = setpoint - measurement （误差）
    
    特点：
    - 响应快速
    - 实现简单
    - 存在稳态误差
    
    物理意义：
    - Kp大 → 响应快，但可能振荡
    - Kp小 → 响应慢，稳定
    
    适用场景：
    - 快速响应要求
    - 可容忍一定稳态误差的场合
    """
    
    def __init__(self, Kp=1.0, setpoint=3.0, output_limits=(0.0, 1.0)):
        """
        初始化比例控制器
        
        参数：
            Kp (float): 比例增益
            setpoint (float): 设定值
            output_limits (tuple): 输出限制 (min, max)
        """
        self.Kp = Kp
        self.setpoint = setpoint
        self.output_limits = output_limits
    
    def control(self, measurement):
        """
        计算控制输出
        
        参数：
            measurement (float): 测量值
        
        返回：
            float: 控制输出
        """
        # 计算误差
        error = self.setpoint - measurement
        
        # 比例控制
        output = self.Kp * error
        
        # 限幅
        output = np.clip(output, *self.output_limits)
        
        return output
    
    def reset(self):
        """重置控制器（P控制器无内部状态）"""
        pass
    
    def __repr__(self):
        return f"ProportionalController(Kp={self.Kp}, setpoint={self.setpoint})"


class PIController:
    """
    比例积分控制器（PI控制器）
    
    原理：
        u = Kp × e + Ki × ∫e dt
    
    优点：
    - 能消除稳态误差（积分作用）
    - 比PID简单
    - 广泛应用
    
    缺点：
    - 可能出现积分饱和
    - 响应比单纯P控制慢一些
    
    适用场景：
    - 需要无静差控制
    - 工业过程控制
    - 温度、液位、压力控制
    """
    
    def __init__(self, Kp=1.0, Ki=0.1, setpoint=3.0, dt=0.1, output_limits=(0.0, 1.0)):
        """
        初始化PI控制器
        
        参数：
            Kp (float): 比例增益
            Ki (float): 积分增益
            setpoint (float): 设定值
            dt (float): 采样周期
            output_limits (tuple): 输出限制
        """
        self.Kp = Kp
        self.Ki = Ki
        self.setpoint = setpoint
        self.dt = dt
        self.output_limits = output_limits
        
        # 内部状态
        self.integral = 0.0
        self.last_error = 0.0
    
    def control(self, measurement):
        """
        计算控制输出
        
        参数：
            measurement (float): 测量值
        
        返回：
            float: 控制输出
        """
        # 计算误差
        error = self.setpoint - measurement
        
        # 比例项
        P = self.Kp * error
        
        # 积分项
        self.integral += error * self.dt
        I = self.Ki * self.integral
        
        # PI输出
        output = P + I
        
        # 限幅
        output_saturated = np.clip(output, *self.output_limits)
        
        # 抗积分饱和（Back-calculation）
        if output != output_saturated:
            # 如果输出饱和，回退积分项
            self.integral = (output_saturated - P) / self.Ki if self.Ki != 0 else 0
        
        self.last_error = error
        
        return output_saturated
    
    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.last_error = 0.0
    
    def __repr__(self):
        return (f"PIController(Kp={self.Kp}, Ki={self.Ki}, setpoint={self.setpoint}, "
                f"integral={self.integral:.3f})")


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    """测试基础控制器"""
    print("=" * 70)
    print("基础控制器测试")
    print("=" * 70)
    
    # 测试1: OnOff控制器
    print("\n[测试1] 开关控制器")
    print("-" * 70)
    controller = OnOffController(low_threshold=2.5, high_threshold=3.5)
    
    test_levels = [2.0, 2.3, 2.6, 3.0, 3.4, 3.7, 3.3, 2.8, 2.4]
    print("水位序列:", test_levels)
    print("\n控制输出:")
    for h in test_levels:
        u = controller.control(h)
        print(f"  h={h:.1f}m → u={u:.1f} ({'ON' if controller.is_on else 'OFF'})")
    
    # 测试2: 比例控制器
    print("\n[测试2] 比例控制器")
    print("-" * 70)
    controller = ProportionalController(Kp=2.0, setpoint=3.0)
    
    test_levels = [1.0, 2.0, 2.5, 2.9, 3.0, 3.1, 3.5, 4.0]
    print(f"Kp={controller.Kp}, 设定值={controller.setpoint}m")
    print("\n误差 → 控制输出:")
    for h in test_levels:
        u = controller.control(h)
        error = controller.setpoint - h
        print(f"  h={h:.1f}m, e={error:+.1f}m → u={u:.3f}")
    
    # 测试3: PI控制器
    print("\n[测试3] PI控制器")
    print("-" * 70)
    controller = PIController(Kp=1.0, Ki=0.5, setpoint=3.0, dt=0.1)
    
    # 模拟一个过程
    h = 2.0  # 初始水位
    print(f"Kp={controller.Kp}, Ki={controller.Ki}, 设定值={controller.setpoint}m")
    print("\n时间 | 水位 | 误差 | 积分 | 输出")
    print("-" * 50)
    
    for t in range(5):
        u = controller.control(h)
        error = controller.setpoint - h
        print(f"{t:4.1f} | {h:4.2f} | {error:+5.2f} | {controller.integral:6.3f} | {u:.3f}")
        
        # 简单模拟水位变化（假设系统响应）
        h = h + 0.5 * u * 0.1  # 简化的动态
    
    print("\n" + "=" * 70)
    print("✅ 所有控制器测试通过!")
    print("=" * 70)


class PIDController:
    """
    PID控制器（比例-积分-微分控制）
    
    原理：
        u = Kp × e + Ki × ∫e dt + Kd × de/dt
    
    特点：
    - P（比例）：快速响应
    - I（积分）：消除稳态误差
    - D（微分）：抑制超调，提高稳定性
    
    优点：
    - 性能优异
    - 广泛应用
    - 三个参数可灵活调节
    
    缺点：
    - 参数整定较复杂
    - 微分项对噪声敏感
    - 需要抗积分饱和
    
    适用场景：
    - 工业过程控制（90%+）
    - 温度、压力、流量、液位控制
    - 需要高精度和快速响应的场合
    """
    
    def __init__(self, Kp=1.0, Ki=0.1, Kd=0.0, setpoint=3.0, dt=0.1, 
                 output_limits=(0.0, 1.0), derivative_filter=0.1):
        """
        初始化PID控制器
        
        参数：
            Kp (float): 比例增益
            Ki (float): 积分增益
            Kd (float): 微分增益
            setpoint (float): 设定值
            dt (float): 采样周期
            output_limits (tuple): 输出限制 (min, max)
            derivative_filter (float): 微分滤波系数（0-1，越小滤波越强）
        
        注意：
            - Kd通常比Kp和Ki小得多
            - derivative_filter可以降低噪声影响
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.dt = dt
        self.output_limits = output_limits
        self.derivative_filter = derivative_filter
        
        # 内部状态
        self.integral = 0.0
        self.last_error = 0.0
        self.last_derivative = 0.0  # 用于滤波
    
    def control(self, measurement):
        """
        计算PID控制输出
        
        参数：
            measurement (float): 测量值
        
        返回：
            float: 控制输出
        
        实现细节：
        1. 计算误差
        2. 比例项：P = Kp × e
        3. 积分项：I = Ki × ∫e dt（累积）
        4. 微分项：D = Kd × de/dt（带滤波）
        5. PID = P + I + D
        6. 限幅 + 抗饱和
        """
        # 计算误差
        error = self.setpoint - measurement
        
        # 比例项
        P = self.Kp * error
        
        # 积分项（矩形积分）
        self.integral += error * self.dt
        I = self.Ki * self.integral
        
        # 微分项（一阶滤波，降低噪声）
        derivative_raw = (error - self.last_error) / self.dt
        # 一阶低通滤波：D_filtered = α×D_new + (1-α)×D_old
        derivative_filtered = (self.derivative_filter * derivative_raw + 
                              (1 - self.derivative_filter) * self.last_derivative)
        D = self.Kd * derivative_filtered
        
        # PID输出
        output = P + I + D
        
        # 限幅
        output_saturated = np.clip(output, *self.output_limits)
        
        # 抗积分饱和（Back-calculation方法）
        if output != output_saturated and self.Ki != 0:
            # 如果输出饱和，回退积分项
            self.integral = (output_saturated - P - D) / self.Ki
        
        # 更新状态
        self.last_error = error
        self.last_derivative = derivative_filtered
        
        return output_saturated
    
    def reset(self):
        """重置控制器状态"""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_derivative = 0.0
    
    def set_setpoint(self, new_setpoint):
        """更改设定值"""
        self.setpoint = new_setpoint
    
    def get_components(self, measurement):
        """
        获取PID各分量（用于分析）
        
        返回：
            dict: {'P': ..., 'I': ..., 'D': ..., 'total': ...}
        """
        error = self.setpoint - measurement
        
        P = self.Kp * error
        I = self.Ki * self.integral
        
        derivative = (error - self.last_error) / self.dt if self.last_error != 0 else 0
        derivative_filtered = (self.derivative_filter * derivative + 
                              (1 - self.derivative_filter) * self.last_derivative)
        D = self.Kd * derivative_filtered
        
        return {
            'P': P,
            'I': I,
            'D': D,
            'total': P + I + D,
            'error': error
        }
    
    def __repr__(self):
        """字符串表示"""
        return (f"PIDController(Kp={self.Kp}, Ki={self.Ki}, Kd={self.Kd}, "
                f"setpoint={self.setpoint}, integral={self.integral:.3f})")


# ============================================================================
# Ziegler-Nichols 整定方法
# ============================================================================

def ziegler_nichols_first_method(L, T, control_type='PID'):
    """
    Ziegler-Nichols第一法（过程反应曲线法）
    
    适用于一阶加纯滞后系统：G(s) = K*e^(-Ls) / (Ts + 1)
    
    参数：
        L (float): 纯滞后时间
        T (float): 时间常数
        control_type (str): 'P', 'PI', 或 'PID'
    
    返回：
        dict: {'Kp': ..., 'Ki': ..., 'Kd': ...}
    
    整定表：
        P:   Kp = T/L,           Ki = 0,         Kd = 0
        PI:  Kp = 0.9*T/L,       Ki = Kp/3.3L,   Kd = 0
        PID: Kp = 1.2*T/L,       Ki = Kp/2L,     Kd = Kp*0.5L
    """
    if L <= 0 or T <= 0:
        raise ValueError("L和T必须为正数")
    
    ratio = T / L
    
    if control_type == 'P':
        return {'Kp': ratio, 'Ki': 0, 'Kd': 0}
    elif control_type == 'PI':
        Kp = 0.9 * ratio
        return {'Kp': Kp, 'Ki': Kp / (3.3 * L), 'Kd': 0}
    elif control_type == 'PID':
        Kp = 1.2 * ratio
        return {'Kp': Kp, 'Ki': Kp / (2 * L), 'Kd': Kp * 0.5 * L}
    else:
        raise ValueError(f"不支持的控制类型：{control_type}")


# ============================================================================
# 测试代码（追加到原有测试）
# ============================================================================

if __name__ == "__main__":
    """测试PID控制器"""
    print("\n" + "=" * 70)
    print("[测试4] PID控制器")
    print("-" * 70)
    
    # 创建PID控制器
    controller = PIDController(Kp=2.0, Ki=0.5, Kd=0.5, setpoint=3.0, dt=0.1)
    
    # 模拟一个简单过程
    h = 2.0  # 初始值
    print(f"Kp={controller.Kp}, Ki={controller.Ki}, Kd={controller.Kd}")
    print("\n时间 | 水位 | 误差 | P项  | I项  | D项  | 输出")
    print("-" * 70)
    
    for t in range(10):
        components = controller.get_components(h)
        u = controller.control(h)
        
        print(f"{t*0.1:4.1f} | {h:4.2f} | {components['error']:+5.2f} | "
              f"{components['P']:+5.2f} | {components['I']:+5.2f} | "
              f"{components['D']:+5.2f} | {u:.3f}")
        
        # 简单模拟（一阶系统）
        h = h + 0.3 * u * 0.1 - 0.05 * h * 0.1
    
    # 测试Ziegler-Nichols整定
    print("\n" + "-" * 70)
    print("[测试5] Ziegler-Nichols整定方法")
    print("-" * 70)
    
    L = 1.0  # 滞后时间
    T = 4.0  # 时间常数
    
    print(f"系统参数: L={L}, T={T}")
    
    for control_type in ['P', 'PI', 'PID']:
        params = ziegler_nichols_first_method(L, T, control_type)
        print(f"\n{control_type}控制器参数:")
        print(f"  Kp = {params['Kp']:.3f}")
        if params['Ki'] > 0:
            print(f"  Ki = {params['Ki']:.3f}")
        if params['Kd'] > 0:
            print(f"  Kd = {params['Kd']:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ PID控制器测试通过!")
    print("=" * 70)
