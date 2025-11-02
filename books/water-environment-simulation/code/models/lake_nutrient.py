"""
湖泊营养盐输入响应模型（Vollenweider模型）
Lake Nutrient Input-Response Model (Vollenweider Model)

用于评估营养盐输入对湖泊水质的影响，预测削减方案效果
"""

import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve


class VollenweiderModel:
    """
    Vollenweider湖泊磷平衡模型
    
    控制方程：
    dP/dt = L/V - P*Q/V - σ*P*A/V
    
    或写成：
    dP/dt = L/V - P*(Q/V + σ*A/V)
    dP/dt = L/V - P*(ρ + σ/H)
    
    其中：
    - P: 湖泊磷浓度 (mg/m³ or μg/L)
    - L: 外源磷负荷 (g/year or mg/d)
    - V: 湖泊体积 (m³)
    - Q: 出流流量 (m³/year or m³/d)
    - σ: 沉降速率 (m/year or m/d)
    - A: 湖泊面积 (m²)
    - H: 平均水深 (m)
    - ρ = Q/V = 1/τ: 冲刷率 (1/year or 1/d)
    - τ = V/Q: 水力停留时间 (year or d)
    """
    
    def __init__(self, A, H, Q, L, sigma, P0=0):
        """
        初始化Vollenweider模型
        
        参数：
        - A: 湖泊面积 (m²)
        - H: 平均水深 (m)
        - Q: 出流流量 (m³/d)
        - L: 外源磷负荷 (mg/d)
        - sigma: 沉降速率 (m/d)
        - P0: 初始磷浓度 (μg/L = mg/m³)
        """
        self.A = A
        self.H = H
        self.V = A * H
        self.Q = Q
        self.L = L
        self.sigma = sigma
        self.P = P0
        
        # 计算参数
        self.tau = self.V / self.Q if self.Q > 0 else np.inf  # 停留时间
        self.rho = self.Q / self.V if self.V > 0 else 0  # 冲刷率
        
        print(f"Vollenweider模型初始化:")
        print(f"  面积: {self.A/1e6:.2f} km²")
        print(f"  水深: {self.H} m")
        print(f"  体积: {self.V/1e6:.2f} × 10⁶ m³")
        print(f"  出流: {self.Q:.1f} m³/d")
        print(f"  磷负荷: {self.L/1e6:.2f} kg/d")
        print(f"  沉降速率: {self.sigma:.4f} m/d")
        print(f"  停留时间: {self.tau:.1f} d ({self.tau/365:.2f} year)")
    
    def dP_dt(self, P, t):
        """
        磷浓度变化率
        
        dP/dt = L/V - P*Q/V - σ*P*A/V
              = L/V - P*(ρ + σ/H)
        """
        return self.L / self.V - P * (self.rho + self.sigma * self.A / self.V)
    
    def solve_transient(self, t_span):
        """
        求解瞬态响应
        
        参数：
        - t_span: 时间数组 (d)
        
        返回：
        - t: 时间数组
        - P: 磷浓度数组 (μg/L)
        """
        P = odeint(self.dP_dt, self.P, t_span)
        
        print(f"\n瞬态求解完成:")
        print(f"  时间范围: {t_span[0]:.1f} - {t_span[-1]:.1f} d")
        print(f"  初始浓度: {self.P:.2f} μg/L")
        print(f"  最终浓度: {P[-1][0]:.2f} μg/L")
        
        return t_span, P.flatten()
    
    def calculate_steady_state(self):
        """
        计算稳态磷浓度
        
        稳态：dP/dt = 0
        P_ss = L / (Q + σ*A)
             = L / V / (ρ + σ/H)
             = (L/V) / (1/τ + σ/H)
        
        返回：
        - P_ss: 稳态磷浓度 (μg/L)
        """
        denominator = self.Q + self.sigma * self.A
        if denominator > 0:
            P_ss = self.L / denominator
        else:
            P_ss = np.inf
        
        print(f"\n稳态磷浓度计算:")
        print(f"  磷负荷: {self.L/1e6:.2f} kg/d")
        print(f"  水力去除: {self.Q:.1f} m³/d")
        print(f"  沉降去除: {self.sigma * self.A:.1f} m³/d")
        print(f"  总去除: {denominator:.1f} m³/d")
        print(f"  稳态浓度: {P_ss:.2f} μg/L")
        
        return P_ss
    
    def calculate_retention_coefficient(self):
        """
        计算磷滞留系数（Retention Coefficient）
        
        R = 1 - P_ss*Q/L
          = σ*A / (Q + σ*A)
          = σ*τ/H / (1 + σ*τ/H)
        
        物理意义：
        - R = 0: 无滞留，完全随水流出
        - R = 1: 完全滞留，全部沉降
        - 典型值：0.1-0.9
        
        返回：
        - R: 滞留系数
        """
        P_ss = self.calculate_steady_state()
        R = 1 - P_ss * self.Q / self.L if self.L > 0 else 0
        
        # 或者直接计算
        R_direct = self.sigma * self.A / (self.Q + self.sigma * self.A)
        
        print(f"\n磷滞留系数计算:")
        print(f"  方法1（质量平衡）: {R:.3f}")
        print(f"  方法2（直接计算）: {R_direct:.3f}")
        print(f"  滞留百分比: {R*100:.1f}%")
        
        return R
    
    def calculate_critical_load(self, P_standard):
        """
        计算临界磷负荷
        
        临界负荷是使稳态浓度达到标准的最大允许负荷
        
        L_crit = P_standard * (Q + σ*A)
        
        参数：
        - P_standard: 磷浓度标准 (μg/L)
        
        返回：
        - L_crit: 临界负荷 (mg/d)
        """
        L_crit = P_standard * (self.Q + self.sigma * self.A)
        
        print(f"\n临界磷负荷计算:")
        print(f"  水质标准: {P_standard:.1f} μg/L")
        print(f"  总去除能力: {self.Q + self.sigma * self.A:.1f} m³/d")
        print(f"  临界负荷: {L_crit/1e6:.2f} kg/d")
        print(f"  当前负荷: {self.L/1e6:.2f} kg/d")
        
        if self.L > L_crit:
            reduction = (self.L - L_crit) / self.L * 100
            print(f"  ⚠️  需要削减: {(self.L - L_crit)/1e6:.2f} kg/d ({reduction:.1f}%)")
        else:
            print(f"  ✓ 负荷在允许范围内")
        
        return L_crit
    
    def evaluate_load_reduction(self, reduction_percent):
        """
        评估负荷削减效果
        
        参数：
        - reduction_percent: 削减百分比 (0-100)
        
        返回：
        - P_old: 原稳态浓度
        - P_new: 新稳态浓度
        - improvement: 改善百分比
        """
        # 原稳态浓度
        P_old = self.calculate_steady_state()
        
        # 保存原负荷
        L_old = self.L
        
        # 削减后负荷
        self.L = L_old * (1 - reduction_percent / 100)
        P_new = self.calculate_steady_state()
        
        # 改善效果
        improvement = (P_old - P_new) / P_old * 100 if P_old > 0 else 0
        
        print(f"\n负荷削减评估:")
        print(f"  削减比例: {reduction_percent:.1f}%")
        print(f"  原负荷: {L_old/1e6:.2f} kg/d")
        print(f"  新负荷: {self.L/1e6:.2f} kg/d")
        print(f"  原浓度: {P_old:.2f} μg/L")
        print(f"  新浓度: {P_new:.2f} μg/L")
        print(f"  改善: {improvement:.1f}%")
        
        # 恢复原负荷
        self.L = L_old
        
        return P_old, P_new, improvement
    
    def calibrate_settling_velocity(self, P_observed, L_known, Q_known):
        """
        率定沉降速率
        
        根据观测的稳态浓度反推沉降速率
        
        从 P = L / (Q + σ*A)
        得 σ = (L/P - Q) / A
        
        参数：
        - P_observed: 观测磷浓度 (μg/L)
        - L_known: 已知磷负荷 (mg/d)
        - Q_known: 已知出流 (m³/d)
        
        返回：
        - sigma: 沉降速率 (m/d)
        """
        if P_observed > 0:
            sigma = (L_known / P_observed - Q_known) / self.A
            sigma = max(sigma, 0)  # 确保非负
        else:
            sigma = 0
        
        print(f"\n沉降速率率定:")
        print(f"  观测浓度: {P_observed:.2f} μg/L")
        print(f"  已知负荷: {L_known/1e6:.2f} kg/d")
        print(f"  已知出流: {Q_known:.1f} m³/d")
        print(f"  率定沉降速率: {sigma:.6f} m/d ({sigma*365:.3f} m/year)")
        
        return sigma


def calculate_trophic_state(TP):
    """
    根据总磷浓度判断营养状态
    
    分类标准（Vollenweider, OECD）：
    - 贫营养 (Oligotrophic): TP < 10 μg/L
    - 中营养 (Mesotrophic): 10 ≤ TP < 30 μg/L
    - 富营养 (Eutrophic): 30 ≤ TP < 100 μg/L
    - 超富营养 (Hypertrophic): TP ≥ 100 μg/L
    
    参数：
    - TP: 总磷浓度 (μg/L)
    
    返回：
    - state: 营养状态字符串
    - index: 状态指数 (0-3)
    """
    if TP < 10:
        state = "Oligotrophic (贫营养)"
        index = 0
    elif TP < 30:
        state = "Mesotrophic (中营养)"
        index = 1
    elif TP < 100:
        state = "Eutrophic (富营养)"
        index = 2
    else:
        state = "Hypertrophic (超富营养)"
        index = 3
    
    print(f"\n营养状态评价:")
    print(f"  总磷: {TP:.2f} μg/L")
    print(f"  状态: {state}")
    
    return state, index


def calculate_vollenweider_loading(A, H, tau, P_target):
    """
    计算Vollenweider容许负荷
    
    Vollenweider提出的容许负荷经验公式：
    L_permissible = P_target * H * (1/τ + 1/τ_s)
    
    其中 τ_s 是沉降特征时间，典型值10-20年
    
    简化形式（危险负荷）：
    L_dangerous = 10 * H^0.5 * (1 + τ^0.5)  (g/m²/year)
    
    参数：
    - A: 面积 (m²)
    - H: 水深 (m)
    - tau: 停留时间 (year)
    - P_target: 目标浓度 (μg/L = mg/m³)
    
    返回：
    - L_permissible: 容许负荷 (mg/d)
    - L_dangerous: 危险负荷 (mg/d)
    """
    # 容许负荷（τ_s取10年）
    tau_s = 10  # year
    tau_year = tau / 365  # 转换为年
    L_permissible_gm2year = P_target / 1000 * H * (1/tau_year + 1/tau_s)  # g/m²/year
    L_permissible = L_permissible_gm2year * A / 365 * 1000  # mg/d
    
    # 危险负荷
    L_dangerous_gm2year = 10 * H**0.5 * (1 + tau_year**0.5)
    L_dangerous = L_dangerous_gm2year * A / 365 * 1000  # mg/d
    
    print(f"\nVollenweider容许负荷:")
    print(f"  面积: {A/1e6:.2f} km²")
    print(f"  水深: {H} m")
    print(f"  停留时间: {tau_year:.2f} year")
    print(f"  目标浓度: {P_target:.1f} μg/L")
    print(f"  容许负荷: {L_permissible/1e6:.2f} kg/d ({L_permissible_gm2year:.2f} g/m²/year)")
    print(f"  危险负荷: {L_dangerous/1e6:.2f} kg/d ({L_dangerous_gm2year:.2f} g/m²/year)")
    
    return L_permissible, L_dangerous


def calculate_phosphorus_budget(L_in, L_out, L_settling, V):
    """
    计算磷收支平衡
    
    参数：
    - L_in: 输入负荷 (mg/d)
    - L_out: 输出负荷 (mg/d)
    - L_settling: 沉降负荷 (mg/d)
    - V: 体积 (m³)
    
    返回：
    - balance: 净累积速率 (μg/L/d)
    - retention: 滞留率 (%)
    """
    balance = (L_in - L_out - L_settling) / V  # μg/L/d
    retention = (L_out + L_settling) / L_in * 100 if L_in > 0 else 0
    
    print(f"\n磷收支平衡:")
    print(f"  输入: {L_in/1e6:.2f} kg/d")
    print(f"  输出: {L_out/1e6:.2f} kg/d")
    print(f"  沉降: {L_settling/1e6:.2f} kg/d")
    print(f"  净累积: {balance:.4f} μg/L/d")
    print(f"  滞留率: {retention:.1f}%")
    
    return balance, retention


def predict_response_time(tau, sigma, H):
    """
    预测响应时间
    
    系统响应时间常数：
    τ_response = 1 / (1/τ + σ/H)
    
    达到95%新稳态：
    t_95 = 3 * τ_response
    
    参数：
    - tau: 水力停留时间 (d)
    - sigma: 沉降速率 (m/d)
    - H: 水深 (m)
    
    返回：
    - tau_response: 响应时间常数 (d)
    - t_95: 达到95%稳态时间 (d)
    """
    tau_response = 1 / (1/tau + sigma/H)
    t_95 = 3 * tau_response
    
    print(f"\n响应时间预测:")
    print(f"  水力停留时间: {tau:.1f} d")
    print(f"  沉降时间尺度: {H/sigma:.1f} d" if sigma > 0 else "  沉降时间尺度: ∞")
    print(f"  响应时间常数: {tau_response:.1f} d")
    print(f"  95%稳态时间: {t_95:.1f} d ({t_95/365:.2f} year)")
    
    return tau_response, t_95
