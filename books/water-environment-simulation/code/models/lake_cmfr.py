"""
湖泊完全混合反应器（CMFR）模型
Lake Complete Mixed Flow Reactor Model

用于模拟小型湖泊水质，假设湖泊内部完全混合（0D箱式模型）
"""

import numpy as np
from scipy.integrate import odeint


class LakeCMFR:
    """
    湖泊完全混合反应器模型
    
    基本假设：
    - 湖泊内部完全混合（0D）
    - 浓度均匀分布
    - 无空间变化
    
    控制方程：
    V * dC/dt = Q_in * C_in - Q_out * C - k*V*C + S
    
    参数：
    - V: 湖泊体积 (m³)
    - Q_in: 入流流量 (m³/d)
    - Q_out: 出流流量 (m³/d)
    - k: 一阶反应速率 (1/d)
    - C_in: 入流浓度 (mg/L)
    - S: 内源产生/去除速率 (mg/d)
    """
    
    def __init__(self, A, H, Q_in, Q_out=None, k=0, C_in=0, C0=0):
        """
        初始化湖泊CMFR模型
        
        参数：
        - A: 湖泊面积 (m²)
        - H: 平均水深 (m)
        - Q_in: 入流流量 (m³/d)
        - Q_out: 出流流量 (m³/d)，默认等于Q_in
        - k: 一阶反应速率常数 (1/d)
        - C_in: 入流浓度 (mg/L)
        - C0: 初始浓度 (mg/L)
        """
        self.A = A  # 面积
        self.H = H  # 水深
        self.V = A * H  # 体积
        self.Q_in = Q_in
        self.Q_out = Q_out if Q_out is not None else Q_in
        self.k = k
        self.C_in = C_in
        self.C = C0  # 当前浓度
        self.S = 0  # 内源
        
        # 计算水力停留时间
        self.HRT = self.V / self.Q_out if self.Q_out > 0 else np.inf
        
        print(f"湖泊完全混合模型初始化:")
        print(f"  面积: {self.A/1e6:.2f} km²")
        print(f"  水深: {self.H} m")
        print(f"  体积: {self.V/1e6:.2f} × 10⁶ m³")
        print(f"  入流流量: {self.Q_in:.1f} m³/d")
        print(f"  出流流量: {self.Q_out:.1f} m³/d")
        print(f"  水力停留时间: {self.HRT:.1f} d")
        print(f"  反应速率: {self.k:.4f} 1/d")
    
    def calculate_hydraulic_residence_time(self):
        """
        计算水力停留时间（HRT）
        
        HRT = V / Q_out
        
        返回：
        - HRT: 水力停留时间 (d)
        """
        if self.Q_out > 0:
            HRT = self.V / self.Q_out
        else:
            HRT = np.inf
        
        print(f"\n水力停留时间计算:")
        print(f"  体积: {self.V/1e6:.2f} × 10⁶ m³")
        print(f"  出流: {self.Q_out:.1f} m³/d")
        print(f"  HRT: {HRT:.1f} d ({HRT/30:.2f} month)")
        
        return HRT
    
    def calculate_flushing_rate(self):
        """
        计算换水率（冲刷率）
        
        r = Q_out / V = 1 / HRT
        
        返回：
        - r: 换水率 (1/d)
        """
        r = self.Q_out / self.V if self.V > 0 else 0
        
        print(f"\n换水率计算:")
        print(f"  换水率: {r:.6f} 1/d")
        print(f"  换水周期: {1/r:.1f} d" if r > 0 else "  换水周期: ∞")
        
        return r
    
    def set_internal_source(self, S):
        """
        设置内源（产生或去除）
        
        参数：
        - S: 内源速率 (mg/d)
             > 0: 内源产生（如底泥释放）
             < 0: 内源去除（如沉降、曝气）
        """
        self.S = S
        print(f"\n内源设置: {S:.2f} mg/d")
        if S > 0:
            print(f"  内源产生（底泥释放等）")
        elif S < 0:
            print(f"  内源去除（沉降、曝气等）")
        else:
            print(f"  无内源")
    
    def dC_dt(self, C, t, Q_in, C_in, Q_out, k, V, S):
        """
        浓度变化率（ODE右侧）
        
        dC/dt = (Q_in*C_in - Q_out*C - k*V*C + S) / V
        """
        return (Q_in * C_in - Q_out * C - k * V * C + S) / V
    
    def solve_transient(self, t_span, C_in_func=None, Q_in_func=None):
        """
        求解瞬态响应
        
        参数：
        - t_span: 时间数组 (d)
        - C_in_func: 入流浓度函数 C_in(t)，默认为常数
        - Q_in_func: 入流流量函数 Q_in(t)，默认为常数
        
        返回：
        - t: 时间数组
        - C: 浓度数组
        """
        if C_in_func is None:
            C_in_func = lambda t: self.C_in
        if Q_in_func is None:
            Q_in_func = lambda t: self.Q_in
        
        # 定义变系数ODE
        def dC_dt_variable(C, t):
            Q_in_t = Q_in_func(t)
            C_in_t = C_in_func(t)
            return (Q_in_t * C_in_t - self.Q_out * C - self.k * self.V * C + self.S) / self.V
        
        # 求解
        C = odeint(dC_dt_variable, self.C, t_span)
        
        print(f"\n瞬态求解完成:")
        print(f"  时间范围: {t_span[0]:.1f} - {t_span[-1]:.1f} d")
        print(f"  初始浓度: {self.C:.2f} mg/L")
        print(f"  最终浓度: {C[-1][0]:.2f} mg/L")
        
        return t_span, C.flatten()
    
    def calculate_steady_state(self):
        """
        计算稳态浓度
        
        稳态：dC/dt = 0
        C_ss = (Q_in*C_in + S) / (Q_out + k*V)
        
        返回：
        - C_ss: 稳态浓度 (mg/L)
        """
        denominator = self.Q_out + self.k * self.V
        if denominator > 0:
            C_ss = (self.Q_in * self.C_in + self.S) / denominator
        else:
            C_ss = np.inf
        
        print(f"\n稳态浓度计算:")
        print(f"  入流负荷: {self.Q_in * self.C_in:.2f} mg/d")
        print(f"  内源: {self.S:.2f} mg/d")
        print(f"  总负荷: {self.Q_in * self.C_in + self.S:.2f} mg/d")
        print(f"  出流去除: {self.Q_out:.2f} m³/d")
        print(f"  反应去除: {self.k * self.V:.2f} m³/d")
        print(f"  稳态浓度: {C_ss:.2f} mg/L")
        
        return C_ss
    
    def calculate_response_time(self):
        """
        计算响应时间（达到稳态的时间）
        
        响应时间常数：τ = V / (Q_out + k*V)
        达到95%稳态需要：t_95 = 3*τ
        
        返回：
        - tau: 响应时间常数 (d)
        - t_95: 达到95%稳态的时间 (d)
        """
        denominator = self.Q_out + self.k * self.V
        if denominator > 0:
            tau = self.V / denominator
            t_95 = 3 * tau
        else:
            tau = np.inf
            t_95 = np.inf
        
        print(f"\n响应时间计算:")
        print(f"  响应时间常数: {tau:.1f} d")
        print(f"  95%稳态时间: {t_95:.1f} d")
        
        return tau, t_95
    
    def evaluate_water_exchange(self, Q_new):
        """
        评估换水措施效果
        
        参数：
        - Q_new: 新的出流流量 (m³/d)
        
        返回：
        - C_ss_old: 原稳态浓度
        - C_ss_new: 新稳态浓度
        - improvement: 改善百分比
        """
        # 原稳态浓度
        C_ss_old = self.calculate_steady_state()
        
        # 保存原参数
        Q_out_old = self.Q_out
        
        # 新参数
        self.Q_out = Q_new
        C_ss_new = self.calculate_steady_state()
        
        # 改善效果
        improvement = (C_ss_old - C_ss_new) / C_ss_old * 100 if C_ss_old > 0 else 0
        
        print(f"\n换水措施评估:")
        print(f"  原出流: {Q_out_old:.1f} m³/d")
        print(f"  新出流: {Q_new:.1f} m³/d")
        print(f"  原稳态浓度: {C_ss_old:.2f} mg/L")
        print(f"  新稳态浓度: {C_ss_new:.2f} mg/L")
        print(f"  改善: {improvement:.1f}%")
        
        # 恢复原参数
        self.Q_out = Q_out_old
        
        return C_ss_old, C_ss_new, improvement
    
    def evaluate_aeration(self, k_aeration):
        """
        评估曝气措施效果（增加反应速率）
        
        参数：
        - k_aeration: 曝气增加的反应速率 (1/d)
        
        返回：
        - C_ss_old: 原稳态浓度
        - C_ss_new: 新稳态浓度
        - improvement: 改善百分比
        """
        # 原稳态浓度
        C_ss_old = self.calculate_steady_state()
        
        # 保存原参数
        k_old = self.k
        
        # 新参数
        self.k = k_old + k_aeration
        C_ss_new = self.calculate_steady_state()
        
        # 改善效果
        improvement = (C_ss_old - C_ss_new) / C_ss_old * 100 if C_ss_old > 0 else 0
        
        print(f"\n曝气措施评估:")
        print(f"  原反应速率: {k_old:.4f} 1/d")
        print(f"  曝气增加: {k_aeration:.4f} 1/d")
        print(f"  新反应速率: {self.k:.4f} 1/d")
        print(f"  原稳态浓度: {C_ss_old:.2f} mg/L")
        print(f"  新稳态浓度: {C_ss_new:.2f} mg/L")
        print(f"  改善: {improvement:.1f}%")
        
        # 恢复原参数
        self.k = k_old
        
        return C_ss_old, C_ss_new, improvement


def calculate_critical_load(V, Q_out, k, C_standard):
    """
    计算临界负荷
    
    临界负荷是使稳态浓度达到标准的最大允许负荷
    
    L_crit = C_standard * (Q_out + k*V)
    
    参数：
    - V: 湖泊体积 (m³)
    - Q_out: 出流流量 (m³/d)
    - k: 反应速率 (1/d)
    - C_standard: 水质标准 (mg/L)
    
    返回：
    - L_crit: 临界负荷 (mg/d)
    """
    L_crit = C_standard * (Q_out + k * V)
    
    print(f"\n临界负荷计算:")
    print(f"  水质标准: {C_standard:.2f} mg/L")
    print(f"  出流去除能力: {Q_out:.2f} m³/d")
    print(f"  反应去除能力: {k * V:.2f} m³/d")
    print(f"  总去除能力: {Q_out + k * V:.2f} m³/d")
    print(f"  临界负荷: {L_crit:.2f} mg/d")
    
    return L_crit


def calculate_flushing_efficiency(Q_out, V, k=0):
    """
    计算冲刷效率（去除效率）
    
    E = 1 - 1/(1 + (Q_out + k*V)/Q_in)
    
    对于Q_in = Q_out:
    E = (Q_out + k*V) / (2*Q_out + k*V)
    
    参数：
    - Q_out: 出流流量 (m³/d)
    - V: 体积 (m³)
    - k: 反应速率 (1/d)
    
    返回：
    - E: 去除效率
    """
    if Q_out > 0:
        # 假设Q_in = Q_out
        E = (Q_out + k * V) / (2 * Q_out + k * V)
    else:
        E = 0
    
    print(f"\n冲刷效率计算:")
    print(f"  出流: {Q_out:.1f} m³/d")
    print(f"  反应去除: {k * V:.1f} m³/d")
    print(f"  去除效率: {E*100:.1f}%")
    
    return E
