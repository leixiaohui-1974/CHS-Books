"""
DC/DC变换器模型
包含Boost、Buck、Buck-Boost等拓扑

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
from typing import Dict, Tuple


class DCDCConverter:
    """
    DC/DC变换器基类
    
    状态空间平均模型:
        dx/dt = A·x + B·u
        y = C·x + D·u
    """
    
    def __init__(self, L: float, C: float, R: float, name: str = "DCDC"):
        """
        初始化DC/DC变换器
        
        Args:
            L: 电感 (H)
            C: 电容 (F)
            R: 负载电阻 (Ω)
            name: 变换器名称
        """
        self.name = name
        self.L = L
        self.C = C
        self.R = R
        
        # 状态变量
        self.i_L = 0.0  # 电感电流 (A)
        self.v_C = 0.0  # 电容电压 (V)
        
        # 输入
        self.v_in = 0.0  # 输入电压 (V)
        self.d = 0.0     # 占空比 (0-1)
    
    def reset(self):
        """重置状态"""
        self.i_L = 0.0
        self.v_C = 0.0
    
    def update(self, v_in: float, d: float, dt: float) -> Tuple[float, float]:
        """
        更新变换器状态
        
        Args:
            v_in: 输入电压 (V)
            d: 占空比 (0-1)
            dt: 时间步长 (s)
            
        Returns:
            (i_L, v_C): 电感电流和电容电压
        """
        raise NotImplementedError("子类需实现update方法")
    
    def get_status(self) -> Dict:
        """获取变换器状态"""
        return {
            'name': self.name,
            'i_L': self.i_L,
            'v_C': self.v_C,
            'v_in': self.v_in,
            'd': self.d,
            'P_out': self.v_C**2 / self.R if self.R > 0 else 0
        }


class BoostConverter(DCDCConverter):
    """
    Boost升压变换器
    
    电路拓扑:
        Vin --L-- Diode --+-- Cout -- Rload
                    |     |
                   SW     ⏚
                   
    状态空间模型:
        d i_L/dt = (1/L) × [Vin - (1-d)×v_C]
        d v_C/dt = (1/C) × [(1-d)×i_L - v_C/R]
        
    理想稳态:
        V_out = V_in / (1 - D)
        
    升压比 > 1
    """
    
    def __init__(self, L: float, C: float, R: float, r_L: float = 0.0, name: str = "Boost"):
        """
        初始化Boost变换器
        
        Args:
            L: 电感 (H)
            C: 电容 (F)
            R: 负载电阻 (Ω)
            r_L: 电感等效串联电阻 (Ω)
            name: 变换器名称
        """
        super().__init__(L, C, R, name)
        self.r_L = r_L
    
    def update(self, v_in: float, d: float, dt: float) -> Tuple[float, float]:
        """
        更新Boost变换器状态
        
        Args:
            v_in: 输入电压 (V)
            d: 占空比 (0-1)
            dt: 时间步长 (s)
            
        Returns:
            (i_L, v_C): 电感电流和电容电压
        """
        self.v_in = v_in
        self.d = np.clip(d, 0, 0.95)  # 限制最大占空比
        
        # 状态空间方程
        # di_L/dt = (1/L) × [v_in - r_L×i_L - (1-d)×v_C]
        di_L_dt = (v_in - self.r_L * self.i_L - (1 - self.d) * self.v_C) / self.L
        
        # dv_C/dt = (1/C) × [(1-d)×i_L - v_C/R]
        dv_C_dt = ((1 - self.d) * self.i_L - self.v_C / self.R) / self.C
        
        # 欧拉积分
        self.i_L += di_L_dt * dt
        self.v_C += dv_C_dt * dt
        
        # 限制状态
        self.i_L = max(0, self.i_L)
        self.v_C = max(0, self.v_C)
        
        return self.i_L, self.v_C


class BuckConverter(DCDCConverter):
    """
    Buck降压变换器
    
    电路拓扑:
        Vin --SW--+-- L --+-- Cout -- Rload
                  |       |
                Diode     ⏚
                  
    状态空间模型:
        d i_L/dt = (1/L) × [d×Vin - v_C]
        d v_C/dt = (1/C) × [i_L - v_C/R]
        
    理想稳态:
        V_out = D × V_in
        
    降压比 < 1
    """
    
    def __init__(self, L: float, C: float, R: float, r_L: float = 0.0, name: str = "Buck"):
        """
        初始化Buck变换器
        
        Args:
            L: 电感 (H)
            C: 电容 (F)
            R: 负载电阻 (Ω)
            r_L: 电感等效串联电阻 (Ω)
            name: 变换器名称
        """
        super().__init__(L, C, R, name)
        self.r_L = r_L
    
    def update(self, v_in: float, d: float, dt: float) -> Tuple[float, float]:
        """
        更新Buck变换器状态
        
        Args:
            v_in: 输入电压 (V)
            d: 占空比 (0-1)
            dt: 时间步长 (s)
            
        Returns:
            (i_L, v_C): 电感电流和电容电压
        """
        self.v_in = v_in
        self.d = np.clip(d, 0, 0.95)
        
        # 状态空间方程
        # di_L/dt = (1/L) × [d×v_in - r_L×i_L - v_C]
        di_L_dt = (self.d * v_in - self.r_L * self.i_L - self.v_C) / self.L
        
        # dv_C/dt = (1/C) × [i_L - v_C/R]
        dv_C_dt = (self.i_L - self.v_C / self.R) / self.C
        
        # 欧拉积分
        self.i_L += di_L_dt * dt
        self.v_C += dv_C_dt * dt
        
        # 限制状态
        self.i_L = max(0, self.i_L)
        self.v_C = max(0, self.v_C)
        
        return self.i_L, self.v_C


class BuckBoostConverter(DCDCConverter):
    """
    Buck-Boost升降压变换器
    
    电路拓扑:
        Vin --SW--+
                  |
                  L
                  |
             Diode--+-- Cout -- Rload
                    |
                    ⏚
                    
    状态空间模型:
        d i_L/dt = (1/L) × [d×Vin - (1-d)×v_C]
        d v_C/dt = (1/C) × [-(1-d)×i_L - v_C/R]
        
    理想稳态:
        V_out = -D/(1-D) × V_in
        
    输出电压极性反转
    升降压比可 > 1 或 < 1
    """
    
    def __init__(self, L: float, C: float, R: float, r_L: float = 0.0, name: str = "Buck-Boost"):
        """
        初始化Buck-Boost变换器
        
        Args:
            L: 电感 (H)
            C: 电容 (F)
            R: 负载电阻 (Ω)
            r_L: 电感等效串联电阻 (Ω)
            name: 变换器名称
        """
        super().__init__(L, C, R, name)
        self.r_L = r_L
    
    def update(self, v_in: float, d: float, dt: float) -> Tuple[float, float]:
        """
        更新Buck-Boost变换器状态
        
        Args:
            v_in: 输入电压 (V)
            d: 占空比 (0-1)
            dt: 时间步长 (s)
            
        Returns:
            (i_L, v_C): 电感电流和电容电压 (注意v_C为负值)
        """
        self.v_in = v_in
        self.d = np.clip(d, 0.05, 0.95)  # 避免极端占空比
        
        # 状态空间方程
        # di_L/dt = (1/L) × [d×v_in - r_L×i_L - (1-d)×|v_C|]
        # 注意: v_C为负值，但这里用绝对值简化
        di_L_dt = (self.d * v_in - self.r_L * self.i_L - (1 - self.d) * abs(self.v_C)) / self.L
        
        # dv_C/dt = (1/C) × [-(1-d)×i_L - v_C/R]
        dv_C_dt = (-(1 - self.d) * self.i_L - self.v_C / self.R) / self.C
        
        # 欧拉积分
        self.i_L += di_L_dt * dt
        self.v_C += dv_C_dt * dt
        
        # 限制状态
        self.i_L = max(0, self.i_L)
        # Buck-Boost输出为负电压
        self.v_C = min(0, self.v_C)
        
        return self.i_L, self.v_C


# ==================== 直流母线电压控制器 ====================

class DCBusVoltageController:
    """
    直流母线电压控制器
    
    控制目标: 稳定直流母线电压
    控制策略: PI控制 + 前馈补偿
    
    结构:
        V_ref → PI控制器 → d (占空比)
          ↑                ↓
        V_meas ← DC/DC变换器
    """
    
    def __init__(self, Kp: float, Ki: float, v_ref: float = 400.0, 
                 d_limit: tuple = (0.05, 0.95), name: str = "DCBusController"):
        """
        初始化直流母线电压控制器
        
        Args:
            Kp: 比例增益
            Ki: 积分增益
            v_ref: 参考电压 (V)
            d_limit: 占空比限幅 (min, max)
            name: 控制器名称
        """
        self.name = name
        self.Kp = Kp
        self.Ki = Ki
        self.v_ref = v_ref
        self.d_min, self.d_max = d_limit
        
        # 状态
        self.integral = 0.0
        self.error = 0.0
        self.d = 0.5  # 初始占空比
    
    def update(self, v_measured: float, dt: float, 
               feedforward: float = 0.0, enable_ff: bool = True) -> float:
        """
        更新控制器
        
        Args:
            v_measured: 测量电压 (V)
            dt: 时间步长 (s)
            feedforward: 前馈补偿项
            enable_ff: 是否启用前馈
            
        Returns:
            d: 占空比 (0-1)
        """
        # 误差
        self.error = self.v_ref - v_measured
        
        # PI控制
        p_term = self.Kp * self.error
        self.integral += self.error * dt
        i_term = self.Ki * self.integral
        
        # 控制输出
        self.d = p_term + i_term
        
        # 前馈补偿
        if enable_ff:
            self.d += feedforward
        
        # 限幅
        self.d = np.clip(self.d, self.d_min, self.d_max)
        
        # 抗饱和
        if self.d >= self.d_max or self.d <= self.d_min:
            self.integral -= self.error * dt  # 回退
        
        return self.d
    
    def reset(self):
        """重置控制器"""
        self.integral = 0.0
        self.error = 0.0
        self.d = 0.5
    
    def set_reference(self, v_ref: float):
        """设置参考电压"""
        self.v_ref = v_ref
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        return {
            'name': self.name,
            'v_ref': self.v_ref,
            'error': self.error,
            'integral': self.integral,
            'd': self.d
        }


class FeedforwardCompensator:
    """
    前馈补偿器
    
    原理: 基于系统模型预测所需占空比
    Boost: d_ff = 1 - V_in / V_ref
    Buck: d_ff = V_ref / V_in
    """
    
    def __init__(self, converter_type: str = "boost"):
        """
        初始化前馈补偿器
        
        Args:
            converter_type: 变换器类型 ("boost", "buck", "buck-boost")
        """
        self.converter_type = converter_type.lower()
    
    def calculate(self, v_in: float, v_ref: float) -> float:
        """
        计算前馈占空比
        
        Args:
            v_in: 输入电压 (V)
            v_ref: 参考电压 (V)
            
        Returns:
            d_ff: 前馈占空比
        """
        if self.converter_type == "boost":
            # Boost: V_out = V_in / (1 - d)
            d_ff = 1 - v_in / v_ref if v_ref > v_in else 0
        
        elif self.converter_type == "buck":
            # Buck: V_out = d * V_in
            d_ff = v_ref / v_in if v_in > v_ref else 1
        
        elif self.converter_type == "buck-boost":
            # Buck-Boost: V_out = -d/(1-d) * V_in
            d_ff = v_ref / (v_in + v_ref)
        
        else:
            d_ff = 0.5
        
        return np.clip(d_ff, 0.05, 0.95)


# ==================== 功率解耦控制 ====================

class PowerDecouplingController:
    """
    功率解耦控制器
    
    问题: 单相系统功率脉动
        P(t) = P0 + P2·cos(2ωt)
        导致直流母线电压二倍频波动
    
    解决方案: 有源功率解耦
        - 检测二倍频分量
        - 补偿控制
        - 减小储能电容
    """
    
    def __init__(self, omega: float, C: float, name: str = "PowerDecoupling"):
        """
        初始化功率解耦控制器
        
        Args:
            omega: 电网角频率 (rad/s)
            C: 直流电容 (F)
            name: 控制器名称
        """
        self.name = name
        self.omega = omega
        self.C = C
        
        # 二倍频陷波滤波器
        self.v_2f = 0.0  # 二倍频分量
        self.alpha = 0.9  # 滤波系数
        
    def extract_ripple(self, v_dc: float, dt: float) -> float:
        """
        提取二倍频纹波
        
        Args:
            v_dc: 直流电压 (V)
            dt: 时间步长 (s)
            
        Returns:
            v_ripple: 纹波电压 (V)
        """
        # 简化的二倍频提取（实际应使用带通滤波器）
        # 这里用一阶滤波器近似
        self.v_2f = self.alpha * self.v_2f + (1 - self.alpha) * v_dc
        v_ripple = v_dc - self.v_2f
        
        return v_ripple
    
    def compensate(self, v_ripple: float, i_ref: float) -> float:
        """
        功率补偿
        
        Args:
            v_ripple: 纹波电压 (V)
            i_ref: 基准电流参考 (A)
            
        Returns:
            i_comp: 补偿电流参考 (A)
        """
        # 补偿电流 = Kp * v_ripple
        Kp = 0.1
        i_comp = i_ref + Kp * v_ripple
        
        return i_comp


# ==================== 下垂控制 ====================

class DroopController:
    """
    下垂控制器 (Droop Control)
    
    原理: 模拟同步发电机的频率/电压下垂特性
    
    直流微网电压下垂:
        V = V_ref - m·I
        
    其中:
        m: 下垂系数 (Ω)
        I: 输出电流 (A)
    """
    
    def __init__(self, V_ref: float, m: float, name: str = "DroopController"):
        """
        初始化下垂控制器
        
        Args:
            V_ref: 参考电压 (V)
            m: 下垂系数 (Ω)
            name: 控制器名称
        """
        self.name = name
        self.V_ref = V_ref
        self.m = m
    
    def calculate(self, I_output: float) -> float:
        """
        计算下垂电压参考
        
        Args:
            I_output: 输出电流 (A)
            
        Returns:
            V_droop: 下垂电压参考 (V)
        """
        V_droop = self.V_ref - self.m * I_output
        
        return V_droop
    
    def set_droop_coefficient(self, m: float):
        """设置下垂系数"""
        self.m = m

