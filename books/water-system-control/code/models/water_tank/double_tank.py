"""
双水箱串联模型 - 教学专用

这是专门为教学设计的二阶系统模型，特点：
1. 两个水箱串联，上水箱流入下水箱
2. 展示二阶系统的典型特性（可能有超调）
3. 适合学习PID控制、状态空间设计
4. 详细注释，每个步骤都解释

应用场景：
- 工业冷却塔（多级串联）
- 污水处理（多级沉淀池）
- 化工生产（串联反应器）

作者：水系统控制论教材开发组
版本：1.0.0
日期：2025-10-28
"""

import numpy as np
from scipy import signal


class DoubleTank:
    """
    双水箱串联模型（二阶系统）
    
    系统结构：
        泵 → 上水箱 → 下水箱 → 流出
        
    物理方程：
        上水箱：dh1/dt = (Q_in - Q_12) / A1
        下水箱：dh2/dt = (Q_12 - Q_out) / A2
        
    其中：
        Q_in = K * u （泵入流量）
        Q_12 = h1 / R1 （上箱流向下箱）
        Q_out = h2 / R2 （下箱流出）
    
    系统特性：
        - 二阶系统
        - 可能有超调
        - 响应比单水箱慢
        - 适合PID控制学习
    
    示例：
        >>> tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
        >>> tank.reset(h1_0=1.0, h2_0=1.0)
        >>> h1, h2 = tank.step(u=0.5, dt=0.1)
    """
    
    def __init__(self, A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0):
        """
        初始化双水箱系统
        
        参数：
            A1 (float): 上水箱横截面积（m²）
            A2 (float): 下水箱横截面积（m²）
            R1 (float): 上水箱出口阻力（min/m²）
            R2 (float): 下水箱出口阻力（min/m²）
            K (float): 泵增益（m³/min）
        
        Raises:
            ValueError: 如果参数不合理
        """
        # 参数检查
        if A1 <= 0 or A2 <= 0:
            raise ValueError(f"横截面积必须大于0，A1={A1}, A2={A2}")
        if R1 <= 0 or R2 <= 0:
            raise ValueError(f"阻力系数必须大于0，R1={R1}, R2={R2}")
        if K < 0:
            raise ValueError(f"泵增益不能为负，K={K}")
        
        self.A1 = A1
        self.A2 = A2
        self.R1 = R1
        self.R2 = R2
        self.K = K
        
        # 计算系统特性参数
        self.tau1 = A1 * R1  # 上水箱时间常数
        self.tau2 = A2 * R2  # 下水箱时间常数
        self.steady_state_gain = K * R1 * R2 / (R1 + R2)  # 稳态增益（近似）
        
        # 计算二阶系统参数（传递函数标准形式）
        # G(s) = K_dc / (tau1*tau2*s^2 + (tau1+tau2)*s + 1)
        self.T = np.sqrt(self.tau1 * self.tau2)  # 自然周期
        self.zeta = (self.tau1 + self.tau2) / (2 * np.sqrt(self.tau1 * self.tau2))  # 阻尼比
        self.omega_n = 1 / np.sqrt(self.tau1 * self.tau2)  # 自然频率
        
        # 初始状态
        self.h1 = 1.0  # 上水箱初始水位
        self.h2 = 1.0  # 下水箱初始水位
        self.t = 0.0   # 仿真时间
    
    def compute_flows(self, h1, h2, u):
        """
        计算各处流量
        
        参数：
            h1 (float): 上水箱水位（m）
            h2 (float): 下水箱水位（m）
            u (float): 控制输入（0-1）
        
        返回：
            tuple: (Q_in, Q_12, Q_out)
                - Q_in: 泵入流量（m³/min）
                - Q_12: 上箱流向下箱（m³/min）
                - Q_out: 下箱流出（m³/min）
        """
        # 泵入流量
        Q_in = self.K * np.clip(u, 0, 1)
        
        # 上水箱流向下水箱
        Q_12 = max(0, h1 / self.R1)
        
        # 下水箱流出
        Q_out = max(0, h2 / self.R2)
        
        return Q_in, Q_12, Q_out
    
    def compute_derivatives(self, h1, h2, u):
        """
        计算水位变化率
        
        微分方程：
            dh1/dt = (Q_in - Q_12) / A1
            dh2/dt = (Q_12 - Q_out) / A2
        
        参数：
            h1 (float): 上水箱水位
            h2 (float): 下水箱水位
            u (float): 控制输入
        
        返回：
            tuple: (dh1_dt, dh2_dt)
        """
        Q_in, Q_12, Q_out = self.compute_flows(h1, h2, u)
        
        dh1_dt = (Q_in - Q_12) / self.A1
        dh2_dt = (Q_12 - Q_out) / self.A2
        
        return dh1_dt, dh2_dt
    
    def step(self, u, dt=0.1):
        """
        推进一个时间步长（欧拉法）
        
        参数：
            u (float): 控制输入（0-1）
            dt (float): 时间步长（分钟）
        
        返回：
            tuple: (h1, h2) 更新后的水位
        """
        # 计算导数
        dh1_dt, dh2_dt = self.compute_derivatives(self.h1, self.h2, u)
        
        # 更新状态（欧拉法）
        self.h1 = max(0, self.h1 + dh1_dt * dt)
        self.h2 = max(0, self.h2 + dh2_dt * dt)
        
        # 更新时间
        self.t += dt
        
        return self.h1, self.h2
    
    def reset(self, h1_0=1.0, h2_0=1.0):
        """
        重置系统状态
        
        参数：
            h1_0 (float): 上水箱初始水位
            h2_0 (float): 下水箱初始水位
        """
        self.h1 = h1_0
        self.h2 = h2_0
        self.t = 0.0
    
    def get_state_space_matrices(self):
        """
        返回状态空间表示
        
        状态方程：
            dx/dt = A*x + B*u
            y = C*x + D*u
        
        状态向量：x = [h1, h2]^T
        输出：y = h2 (通常控制下水箱水位)
        
        推导：
            dh1/dt = -(1/tau1)*h1 + (K/A1)*u
            dh2/dt = (1/(A2*R1))*h1 - (1/tau2)*h2
        
        矩阵形式：
            A = [[-1/tau1,        0    ],
                 [1/(A2*R1), -1/tau2   ]]
            
            B = [[K/A1],
                 [  0  ]]
            
            C = [0, 1]  (测量下水箱)
            
            D = [0]
        
        返回：
            tuple: (A, B, C, D) 状态空间矩阵
        """
        A = np.array([
            [-1/self.tau1,        0           ],
            [1/(self.A2*self.R1), -1/self.tau2]
        ])
        
        B = np.array([
            [self.K / self.A1],
            [0]
        ])
        
        C = np.array([[0, 1]])  # 测量下水箱水位
        
        D = np.array([[0]])
        
        return A, B, C, D
    
    def get_transfer_function(self):
        """
        返回传递函数（从u到h2）
        
        标准二阶系统形式：
            G(s) = K / (τ1*τ2*s² + (τ1+τ2)*s + 1)
        
        也可以写成：
            G(s) = K*ωn² / (s² + 2*ζ*ωn*s + ωn²)
        
        其中：
            ωn = 1/√(τ1*τ2)  (自然频率)
            ζ = (τ1+τ2)/(2*√(τ1*τ2))  (阻尼比)
        
        返回：
            dict: 传递函数参数
        """
        # 从状态空间计算传递函数
        A, B, C, D = self.get_state_space_matrices()
        sys = signal.StateSpace(A, B, C, D)
        tf_sys = signal.ss2tf(sys.A, sys.B, sys.C, sys.D)
        
        # 提取分子和分母
        num = tf_sys[0].flatten()
        den = tf_sys[1].flatten()
        
        return {
            'num': num.tolist(),
            'den': den.tolist(),
            'omega_n': self.omega_n,
            'zeta': self.zeta,
            'tau1': self.tau1,
            'tau2': self.tau2,
            'K': self.K * self.R2,  # 近似稳态增益
            'description': f'二阶系统: ωn={self.omega_n:.3f}, ζ={self.zeta:.3f}'
        }
    
    def get_poles(self):
        """
        计算系统极点
        
        极点决定系统响应特性：
        - 实部：衰减速度
        - 虚部：振荡频率
        
        返回：
            np.ndarray: 系统极点
        """
        A, B, C, D = self.get_state_space_matrices()
        poles = np.linalg.eigvals(A)
        return poles
    
    def __repr__(self):
        """开发者友好的字符串"""
        return (f"DoubleTank(A1={self.A1}, A2={self.A2}, R1={self.R1}, R2={self.R2}, "
                f"K={self.K}, h1={self.h1:.2f}, h2={self.h2:.2f})")
    
    def __str__(self):
        """用户友好的字符串"""
        return (f"双水箱串联模型:\n"
                f"  上水箱: A1={self.A1}m², R1={self.R1}min/m², τ1={self.tau1:.2f}min, h1={self.h1:.2f}m\n"
                f"  下水箱: A2={self.A2}m², R2={self.R2}min/m², τ2={self.tau2:.2f}min, h2={self.h2:.2f}m\n"
                f"  系统特性: ωn={self.omega_n:.3f}rad/min, ζ={self.zeta:.3f}, K={self.K:.2f}m³/min")


# ============================================================================
# 辅助函数
# ============================================================================

def simulate_double_tank(tank, u_sequence, dt=0.1, measure='h2'):
    """
    双水箱开环仿真
    
    参数：
        tank (DoubleTank): 双水箱对象
        u_sequence (array): 控制输入序列
        dt (float): 时间步长
        measure (str): 测量量 ('h1', 'h2', 或 'both')
    
    返回：
        tuple: (t, h1, h2, Q_in, Q_12, Q_out)
    """
    n_steps = len(u_sequence)
    t = np.zeros(n_steps)
    h1 = np.zeros(n_steps)
    h2 = np.zeros(n_steps)
    Q_in = np.zeros(n_steps)
    Q_12 = np.zeros(n_steps)
    Q_out = np.zeros(n_steps)
    
    for i, u in enumerate(u_sequence):
        t[i] = tank.t
        h1[i] = tank.h1
        h2[i] = tank.h2
        
        Q_in[i], Q_12[i], Q_out[i] = tank.compute_flows(tank.h1, tank.h2, u)
        tank.step(u, dt)
    
    return t, h1, h2, Q_in, Q_12, Q_out


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    """运行基本测试"""
    print("=" * 70)
    print("双水箱串联模型基本测试")
    print("=" * 70)
    
    # 创建双水箱
    tank = DoubleTank(A1=1.0, A2=2.0, R1=1.0, R2=2.0, K=1.0)
    print(f"\n{tank}")
    
    # 测试1：系统特性
    print("\n" + "-" * 70)
    print("[测试1] 系统特性分析")
    print("-" * 70)
    poles = tank.get_poles()
    print(f"  自然频率 ωn = {tank.omega_n:.4f} rad/min")
    print(f"  阻尼比 ζ = {tank.zeta:.4f}")
    print(f"  系统极点: {poles}")
    if tank.zeta < 1:
        print(f"  → 欠阻尼系统，会有超调")
    elif tank.zeta == 1:
        print(f"  → 临界阻尼系统")
    else:
        print(f"  → 过阻尼系统，无超调")
    
    # 测试2：阶跃响应
    print("\n" + "-" * 70)
    print("[测试2] 阶跃响应仿真")
    print("-" * 70)
    tank.reset(h1_0=0, h2_0=0)
    u_sequence = np.ones(200)
    t, h1, h2, Q_in, Q_12, Q_out = simulate_double_tank(tank, u_sequence, dt=0.1)
    
    print(f"  初始状态: h1={h1[0]:.2f}m, h2={h2[0]:.2f}m")
    print(f"  最终状态: h1={h1[-1]:.2f}m, h2={h2[-1]:.2f}m")
    
    # 检测超调
    h2_max = np.max(h2)
    h2_final = h2[-1]
    if h2_max > h2_final * 1.01:
        overshoot = (h2_max - h2_final) / h2_final * 100
        print(f"  下水箱超调量: {overshoot:.1f}%")
    else:
        print(f"  下水箱无明显超调")
    
    # 测试3：状态空间
    print("\n" + "-" * 70)
    print("[测试3] 状态空间表示")
    print("-" * 70)
    A, B, C, D = tank.get_state_space_matrices()
    print(f"  A矩阵:")
    print(f"    {A}")
    print(f"  B矩阵:")
    print(f"    {B.T}")
    print(f"  C矩阵: {C}")
    print(f"  D矩阵: {D}")
    
    # 测试4：传递函数
    print("\n" + "-" * 70)
    print("[测试4] 传递函数")
    print("-" * 70)
    tf = tank.get_transfer_function()
    print(f"  {tf['description']}")
    print(f"  分子: {[f'{x:.4f}' for x in tf['num']]}")
    print(f"  分母: {[f'{x:.4f}' for x in tf['den']]}")
    
    print("\n" + "=" * 70)
    print("✅ 所有基本测试通过!")
    print("=" * 70)
