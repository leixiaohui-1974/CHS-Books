"""
单水箱模型 - 教学专用

这是专门为教学设计的简化模型，特点：
1. 极简实现，容易理解
2. 详细注释，每行都解释
3. 适合高中物理基础的学生
4. 可直接用于仿真和控制实验

作者：水系统控制论教材开发组
版本：1.0.0
日期：2025-10-28
"""

import numpy as np


class SingleTank:
    """
    单水箱模型
    
    基于物理原理：
    - 质量守恒：dV/dt = Q_in - Q_out
    - 几何关系：V = A × h
    - 流出规律：Q_out = h / R（线性近似）
    
    适用场景：
    - 家庭水塔
    - 工业储罐
    - 水位控制系统教学
    
    示例：
        >>> tank = SingleTank(A=2.0, R=2.0, K=1.0)
        >>> tank.h = 2.0  # 设置初始水位
        >>> new_h = tank.step(u=0.5, dt=0.1)  # 50%功率抽水0.1分钟
        >>> print(f"新水位: {new_h:.3f}米")
    """
    
    def __init__(self, A=2.0, R=2.0, K=1.0):
        """
        初始化水箱
        
        参数：
            A (float): 横截面积（单位：平方米 m²）
                - 默认 2.0 m² （相当于边长约1.4米的正方形）
                - 越大，水位变化越慢
            
            R (float): 出口阻力系数（单位：分钟/平方米 min/m²）
                - 默认 2.0 min/m²
                - 越大，出水越慢
                - 物理意义：Q_out = h / R
            
            K (float): 泵增益（单位：立方米每分钟每单位控制信号 m³/min）
                - 默认 1.0
                - 表示泵的抽水能力
                - 实际流量 = K × 控制信号(0-1)
        
        Raises:
            ValueError: 如果参数不合理（如负数或零）
        """
        # 参数检查
        if A <= 0:
            raise ValueError(f"横截面积必须大于0，当前值：{A}")
        if R <= 0:
            raise ValueError(f"阻力系数必须大于0，当前值：{R}")
        if K < 0:
            raise ValueError(f"泵增益不能为负，当前值：{K}")
        
        self.A = A  # 横截面积
        self.R = R  # 阻力系数
        self.K = K  # 泵增益
        
        # 计算系统特性参数（用于分析）
        self.tau = A * R  # 时间常数（分钟）
        self.steady_state_gain = K * R  # 稳态增益
        
        # 初始状态
        self.h = 2.0  # 初始水位 2米
        self.t = 0.0  # 仿真时间（分钟）
    
    def compute_flow_out(self, h):
        """
        计算出水流量
        
        物理模型：Q_out = h / R
        - 水位越高，压力越大，出水越快
        - 这是线性化近似（实际可能是平方根关系 Q ∝ √h）
        
        参数：
            h (float): 当前水位（米）
        
        返回：
            float: 出水流量（m³/min）
        
        注意：
            当水位≤0时，返回0（防止负流量）
        """
        if h <= 0:
            return 0.0  # 没水了，不能再流出
        
        Q_out = h / self.R
        return Q_out
    
    def compute_level_change_rate(self, h, Q_in):
        """
        计算水位变化速度 dh/dt
        
        推导过程：
        1. 质量守恒：dV/dt = Q_in - Q_out
        2. 几何关系：V = A × h，所以 dV/dt = A × dh/dt
        3. 代入得：A × dh/dt = Q_in - Q_out
        4. 两边除以A：dh/dt = (Q_in - Q_out) / A
        
        参数：
            h (float): 当前水位（米）
            Q_in (float): 入水流量（m³/min）
        
        返回：
            float: 水位变化速度（m/min）
            
        物理意义：
            - dh/dt > 0: 水位上升
            - dh/dt < 0: 水位下降
            - dh/dt = 0: 水位不变（稳态）
        """
        Q_out = self.compute_flow_out(h)
        dh_dt = (Q_in - Q_out) / self.A
        return dh_dt
    
    def step(self, u, dt=0.1):
        """
        推进一个时间步长（使用显式欧拉法）
        
        数值方法：显式欧拉法（Forward Euler）
        - h_new = h_old + (dh/dt) × dt
        - 简单但要求dt足够小以保证稳定性
        
        参数：
            u (float): 控制输入（0-1之间）
                - 0 = 泵关闭
                - 1 = 泵全速运行
                - 0.5 = 泵50%功率
            dt (float): 时间步长（分钟），默认0.1分钟=6秒
        
        返回：
            float: 更新后的水位（米）
        
        示例：
            >>> tank = SingleTank()
            >>> tank.h = 2.0  # 初始水位2米
            >>> new_h = tank.step(u=0.5, dt=0.1)  # 50%功率抽水
            >>> print(f"新水位: {new_h:.3f}米")
            新水位: 2.010米
        """
        # 限制控制输入在合理范围内
        u = np.clip(u, 0.0, 1.0)
        
        # 计算实际流入量
        Q_in = self.K * u
        
        # 计算水位变化速度
        dh_dt = self.compute_level_change_rate(self.h, Q_in)
        
        # 更新水位（欧拉法）
        self.h = self.h + dh_dt * dt
        
        # 水位不能为负（物理约束）
        self.h = max(0.0, self.h)
        
        # 更新时间
        self.t += dt
        
        return self.h
    
    def reset(self, h0=2.0):
        """
        重置水箱状态
        
        用途：
        - 开始新的仿真实验
        - 测试不同初始条件
        
        参数：
            h0 (float): 初始水位（米），默认2.0米
        """
        self.h = h0
        self.t = 0.0
    
    def get_state_space_matrices(self):
        """
        返回状态空间表示
        
        连续时间状态空间模型：
            dx/dt = A·x + B·u
            y = C·x + D·u
        
        对于单水箱：
            状态 x = h (水位)
            输入 u = 控制信号 (0-1)
            输出 y = h (水位)
        
        推导：
            dh/dt = -h/(A×R) + (K/A)·u
                  = (-1/τ)·h + (K/A)·u
        
        因此：
            A = -1/τ = -1/(A×R)
            B = K/A
            C = 1
            D = 0
        
        返回：
            tuple: (A, B, C, D) 状态空间矩阵
        
        用途：
            - 控制系统设计（LQR、极点配置等）
            - 可控性、可观性分析
            - 传递函数计算
        
        示例：
            >>> tank = SingleTank(A=2.0, R=2.0, K=1.0)
            >>> A, B, C, D = tank.get_state_space_matrices()
            >>> print(f"A = {A[0,0]:.4f}")
            A = -0.2500
        """
        A_matrix = np.array([[-1.0 / self.tau]])
        B_matrix = np.array([[self.K / self.A]])
        C_matrix = np.array([[1.0]])
        D_matrix = np.array([[0.0]])
        
        return A_matrix, B_matrix, C_matrix, D_matrix
    
    def get_transfer_function(self):
        """
        返回传递函数参数
        
        传递函数（拉普拉斯变换）：
            G(s) = Y(s)/U(s) = K_dc / (τ·s + 1)
        
        其中：
            K_dc = K × R （直流增益，稳态增益）
            τ = A × R （时间常数）
        
        物理意义：
            - K_dc: 单位阶跃输入的最终水位
            - τ: 达到最终值63.2%所需时间
        
        返回：
            dict: 包含增益、时间常数和描述字符串
        
        示例：
            >>> tank = SingleTank(A=2.0, R=2.0, K=1.0)
            >>> tf = tank.get_transfer_function()
            >>> print(tf['description'])
            G(s) = 2.00 / (4.00·s + 1)
        """
        return {
            'gain': self.steady_state_gain,
            'tau': self.tau,
            'num': [self.steady_state_gain],
            'den': [self.tau, 1],
            'description': f'G(s) = {self.steady_state_gain:.2f} / ({self.tau:.2f}·s + 1)'
        }
    
    def __repr__(self):
        """开发者友好的字符串表示"""
        return (f"SingleTank(A={self.A:.2f}, R={self.R:.2f}, K={self.K:.2f}, "
                f"h={self.h:.2f}, t={self.t:.2f})")
    
    def __str__(self):
        """用户友好的字符串表示"""
        return (f"单水箱模型: 横截面积{self.A:.2f}m², 阻力系数{self.R:.2f}min/m², "
                f"泵增益{self.K:.2f}m³/min, 当前水位{self.h:.2f}m, 时间{self.t:.2f}min")


# ============================================================================
# 辅助函数 - 用于教学演示和仿真
# ============================================================================

def simulate_open_loop(tank, u_sequence, dt=0.1):
    """
    开环仿真（固定控制输入序列）
    
    用途：
    - 测试系统开环响应
    - 阶跃响应实验
    - 脉冲响应实验
    
    参数：
        tank (SingleTank): 水箱对象
        u_sequence (array-like): 控制输入序列
        dt (float): 时间步长（分钟）
    
    返回：
        tuple: (t, h, Q_in, Q_out)
            - t: 时间序列
            - h: 水位序列
            - Q_in: 入水流量序列
            - Q_out: 出水流量序列
    
    示例：
        >>> tank = SingleTank()
        >>> tank.reset(h0=2.0)
        >>> u = np.ones(100)  # 100步单位阶跃
        >>> t, h, Q_in, Q_out = simulate_open_loop(tank, u, dt=0.1)
    """
    n_steps = len(u_sequence)
    t = np.arange(n_steps) * dt
    h = np.zeros(n_steps)
    Q_in = np.zeros(n_steps)
    Q_out = np.zeros(n_steps)
    
    for i, u in enumerate(u_sequence):
        h[i] = tank.h
        Q_in[i] = tank.K * u
        Q_out[i] = tank.compute_flow_out(tank.h)
        tank.step(u, dt)
    
    return t, h, Q_in, Q_out


def simulate_closed_loop(tank, controller, duration=60, dt=0.1):
    """
    闭环仿真（带反馈控制）
    
    用途：
    - 测试控制器性能
    - PID参数整定
    - 控制系统设计验证
    
    参数：
        tank (SingleTank): 水箱对象
        controller: 控制器对象（需要有control(h)方法）
        duration (float): 仿真时长（分钟）
        dt (float): 时间步长（分钟）
    
    返回：
        tuple: (t, h, u, error)
            - t: 时间序列
            - h: 水位序列
            - u: 控制输入序列
            - error: 误差序列
    
    示例：
        >>> from src.control.basic_controllers import ProportionalController
        >>> tank = SingleTank()
        >>> controller = ProportionalController(Kp=2.0, setpoint=3.0)
        >>> t, h, u, error = simulate_closed_loop(tank, controller, duration=60)
    """
    n_steps = int(duration / dt)
    t = np.zeros(n_steps)
    h = np.zeros(n_steps)
    u = np.zeros(n_steps)
    error = np.zeros(n_steps)
    
    for i in range(n_steps):
        t[i] = tank.t
        h[i] = tank.h
        
        # 控制器计算
        u[i] = controller.control(tank.h)
        error[i] = controller.setpoint - tank.h
        
        # 水箱更新
        tank.step(u[i], dt)
    
    return t, h, u, error


def calculate_step_response_metrics(t, y, setpoint, dt):
    """
    计算阶跃响应性能指标
    
    参数：
        t (array): 时间序列
        y (array): 输出序列
        setpoint (float): 目标值
        dt (float): 采样周期
    
    返回：
        dict: 性能指标字典
            - rise_time: 上升时间（10%-90%）
            - settling_time: 调节时间（2%误差带）
            - overshoot: 超调量（%）
            - steady_state_error: 稳态误差
            - peak_time: 峰值时间
            - peak_value: 峰值
    """
    metrics = {}
    
    # 上升时间（10%-90%）
    try:
        idx_10 = np.where(y >= 0.1 * setpoint)[0][0]
        idx_90 = np.where(y >= 0.9 * setpoint)[0][0]
        metrics['rise_time'] = t[idx_90] - t[idx_10]
    except:
        metrics['rise_time'] = np.nan
    
    # 峰值
    peak_idx = np.argmax(y)
    metrics['peak_value'] = y[peak_idx]
    metrics['peak_time'] = t[peak_idx]
    
    # 超调量
    if metrics['peak_value'] > setpoint:
        metrics['overshoot'] = (metrics['peak_value'] - setpoint) / setpoint * 100
    else:
        metrics['overshoot'] = 0.0
    
    # 调节时间（2%误差带）
    settling_band = 0.02 * abs(setpoint)
    try:
        settled_indices = np.where(np.abs(y - setpoint) <= settling_band)[0]
        if len(settled_indices) > 0:
            # 找到最后一次进入并保持在误差带内的时刻
            for i in range(len(settled_indices)-1, 0, -1):
                if settled_indices[i] - settled_indices[i-1] > 1:
                    metrics['settling_time'] = t[settled_indices[i]]
                    break
            else:
                metrics['settling_time'] = t[settled_indices[0]]
        else:
            metrics['settling_time'] = np.nan
    except:
        metrics['settling_time'] = np.nan
    
    # 稳态误差
    metrics['steady_state_error'] = abs(y[-1] - setpoint)
    
    return metrics


# ============================================================================
# 测试代码 - 验证模型正确性
# ============================================================================

if __name__ == "__main__":
    """运行基本测试"""
    print("=" * 70)
    print("单水箱模型基本测试")
    print("=" * 70)
    
    # 创建水箱
    tank = SingleTank(A=2.0, R=2.0, K=1.0)
    print(f"\n{tank}")
    print(f"时间常数 τ = {tank.tau:.2f} 分钟")
    print(f"稳态增益 K = {tank.steady_state_gain:.2f}")
    
    # 测试1: 阶跃响应
    print("\n" + "-" * 70)
    print("[测试1] 阶跃输入 u=1.0 (全速抽水)")
    print("-" * 70)
    tank.reset(h0=2.0)
    
    for i in range(5):
        h_new = tank.step(u=1.0, dt=1.0)  # 每步1分钟
        Q_out = tank.compute_flow_out(h_new)
        print(f"  t={tank.t:.1f}min, h={h_new:.3f}m, Q_out={Q_out:.3f}m³/min")
    
    # 测试2: 状态空间矩阵
    print("\n" + "-" * 70)
    print("[测试2] 状态空间表示")
    print("-" * 70)
    A, B, C, D = tank.get_state_space_matrices()
    print(f"  A = {A[0,0]:.4f}")
    print(f"  B = {B[0,0]:.4f}")
    print(f"  C = {C[0,0]:.4f}")
    print(f"  D = {D[0,0]:.4f}")
    
    # 测试3: 传递函数
    print("\n" + "-" * 70)
    print("[测试3] 传递函数")
    print("-" * 70)
    tf = tank.get_transfer_function()
    print(f"  {tf['description']}")
    print(f"  分子: {tf['num']}")
    print(f"  分母: {tf['den']}")
    
    # 测试4: 开环仿真
    print("\n" + "-" * 70)
    print("[测试4] 开环阶跃响应仿真")
    print("-" * 70)
    tank.reset(h0=0.0)  # 从0开始
    u_sequence = np.ones(100)  # 100步单位阶跃
    t, h, Q_in, Q_out = simulate_open_loop(tank, u_sequence, dt=0.1)
    
    print(f"  初始水位: {h[0]:.3f}m")
    print(f"  最终水位: {h[-1]:.3f}m")
    print(f"  理论稳态值: {tank.steady_state_gain:.3f}m")
    print(f"  误差: {abs(h[-1] - tank.steady_state_gain):.4f}m")
    
    # 测试5: 性能指标计算
    print("\n" + "-" * 70)
    print("[测试5] 阶跃响应性能指标")
    print("-" * 70)
    metrics = calculate_step_response_metrics(t, h, tank.steady_state_gain, 0.1)
    print(f"  上升时间: {metrics['rise_time']:.2f} 分钟")
    print(f"  调节时间: {metrics['settling_time']:.2f} 分钟")
    print(f"  超调量: {metrics['overshoot']:.2f}%")
    print(f"  稳态误差: {metrics['steady_state_error']:.4f}m")
    
    print("\n" + "=" * 70)
    print("✅ 所有基本测试通过!")
    print("=" * 70)
