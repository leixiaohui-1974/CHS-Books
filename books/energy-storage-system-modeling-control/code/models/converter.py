"""
储能变流器控制模块

包含:
1. 双向DC/DC变换器
2. 储能PCS控制 (PQ/VF模式)
3. 充放电策略
4. 并网/离网切换
5. 黑启动控制
6. VSG控制

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple


class BidirectionalDCDC:
    """
    双向DC/DC变换器
    
    Buck-Boost双向拓扑
    """
    
    def __init__(
        self,
        L: float = 1e-3,  # H, 电感
        C_dc: float = 2e-3,  # F, 直流侧电容
        V_dc_ref: float = 400.0,  # V, 直流电压参考
        I_max: float = 100.0,  # A, 最大电流
        fs: float = 10e3,  # Hz, 开关频率
        name: str = "BidirectionalDCDC"
    ):
        """
        初始化双向DC/DC变换器
        
        Args:
            L: 电感值
            C_dc: 直流侧电容
            V_dc_ref: 直流电压参考
            I_max: 最大电流
            fs: 开关频率
        """
        self.name = name
        self.L = L
        self.C_dc = C_dc
        self.V_dc_ref = V_dc_ref
        self.I_max = I_max
        self.fs = fs
        
        # 状态变量
        self.I_L = 0.0  # 电感电流
        self.V_dc = V_dc_ref  # 直流电压
        
        # PI控制器参数
        self.Kp_I = 0.5
        self.Ki_I = 100.0
        self.I_error_sum = 0.0
    
    def current_control(self, I_ref: float, V_battery: float, dt: float) -> float:
        """
        电流环控制
        
        Args:
            I_ref: 电流参考 (A), 充电为正
            V_battery: 电池电压 (V)
            dt: 时间步长 (s)
            
        Returns:
            占空比 (0-1)
        """
        # PI控制
        I_error = I_ref - self.I_L
        self.I_error_sum += I_error * dt
        
        # 前馈 + 反馈
        duty = (V_battery / self.V_dc) + self.Kp_I * I_error + self.Ki_I * self.I_error_sum
        duty = np.clip(duty, 0, 0.95)
        
        return duty
    
    def update_states(self, duty: float, V_battery: float, I_load: float, dt: float):
        """
        更新状态变量
        
        Args:
            duty: 占空比
            V_battery: 电池电压 (V)
            I_load: 负载电流 (A)
            dt: 时间步长 (s)
        """
        # 电感电流动态
        if duty > 0.5:  # Buck模式 (充电)
            dI_L_dt = (self.V_dc * duty - V_battery) / self.L
        else:  # Boost模式 (放电)
            dI_L_dt = (V_battery - self.V_dc * (1 - duty)) / self.L
        
        self.I_L += dI_L_dt * dt
        self.I_L = np.clip(self.I_L, -self.I_max, self.I_max)
        
        # 直流电压动态
        dV_dc_dt = (self.I_L - I_load) / self.C_dc
        self.V_dc += dV_dc_dt * dt


class StoragePCS:
    """
    储能变流器 (Power Conversion System)
    
    支持PQ模式和VF模式
    """
    
    def __init__(
        self,
        P_rated: float = 500e3,  # W
        Q_rated: float = 250e3,  # Var
        V_grid_nom: float = 380.0,  # V (线电压RMS)
        f_nom: float = 50.0,  # Hz
        name: str = "StoragePCS"
    ):
        """
        初始化储能PCS
        
        Args:
            P_rated: 额定有功功率
            Q_rated: 额定无功功率
            V_grid_nom: 电网额定电压
            f_nom: 额定频率
        """
        self.name = name
        self.P_rated = P_rated
        self.Q_rated = Q_rated
        self.V_grid_nom = V_grid_nom
        self.f_nom = f_nom
        
        # 工作模式
        self.mode = 'PQ'  # 'PQ' or 'VF'
        
        # PQ模式下的参考值
        self.P_ref = 0.0
        self.Q_ref = 0.0
        
        # VF模式下的参考值
        self.V_ref = V_grid_nom
        self.f_ref = f_nom
        
        # dq电流控制器
        self.Kp_dq = 1.0
        self.Ki_dq = 50.0
        self.Id_error_sum = 0.0
        self.Iq_error_sum = 0.0
    
    def pq_mode_control(
        self,
        V_grid_d: float,
        V_grid_q: float,
        I_d: float,
        I_q: float,
        dt: float
    ) -> Tuple[float, float]:
        """
        PQ模式控制
        
        P = 1.5 * (Vd*Id + Vq*Iq)
        Q = 1.5 * (Vq*Id - Vd*Iq)
        
        Args:
            V_grid_d, V_grid_q: 电网电压dq分量 (V)
            I_d, I_q: 输出电流dq分量 (A)
            dt: 时间步长 (s)
            
        Returns:
            Vd_ref, Vq_ref: 调制电压参考
        """
        # 功率计算
        P_actual = 1.5 * (V_grid_d * I_d + V_grid_q * I_q)
        Q_actual = 1.5 * (V_grid_q * I_d - V_grid_d * I_q)
        
        # 功率到电流的转换
        V_mag = np.sqrt(V_grid_d**2 + V_grid_q**2)
        if V_mag > 0:
            Id_ref = self.P_ref * V_grid_d / (1.5 * V_mag**2)
            Iq_ref = -self.Q_ref * V_grid_d / (1.5 * V_mag**2)
        else:
            Id_ref = 0
            Iq_ref = 0
        
        # 电流环PI控制
        Id_error = Id_ref - I_d
        Iq_error = Iq_ref - I_q
        
        self.Id_error_sum += Id_error * dt
        self.Iq_error_sum += Iq_error * dt
        
        # 解耦控制
        omega = 2 * np.pi * self.f_nom
        L_filter = 1e-3  # 滤波电感
        
        Vd_ref = V_grid_d + self.Kp_dq * Id_error + self.Ki_dq * self.Id_error_sum - omega * L_filter * I_q
        Vq_ref = V_grid_q + self.Kp_dq * Iq_error + self.Ki_dq * self.Iq_error_sum + omega * L_filter * I_d
        
        return Vd_ref, Vq_ref
    
    def vf_mode_control(
        self,
        V_d: float,
        V_q: float,
        I_d: float,
        I_q: float,
        dt: float
    ) -> Tuple[float, float]:
        """
        VF模式控制（离网）
        
        Args:
            V_d, V_q: 输出电压dq分量 (V)
            I_d, I_q: 输出电流dq分量 (A)
            dt: 时间步长 (s)
            
        Returns:
            Vd_ref, Vq_ref: 调制电压参考
        """
        # 电压环控制
        Vd_error = self.V_ref - V_d
        Vq_error = 0 - V_q  # Vq通常控制为0
        
        # 双环控制（电压外环+电流内环）
        # 简化：直接PI控制
        Kp_v = 0.1
        Ki_v = 10.0
        
        Vd_ref = self.V_ref + Kp_v * Vd_error
        Vq_ref = Kp_v * Vq_error
        
        return Vd_ref, Vq_ref


class ChargeDischargaStrategy:
    """
    充放电策略优化
    
    基于峰谷电价的优化策略
    """
    
    def __init__(
        self,
        P_rated: float = 500e3,  # W
        E_capacity: float = 1000e3,  # Wh
        price_peak: float = 1.2,  # 元/kWh
        price_valley: float = 0.3,  # 元/kWh
        price_flat: float = 0.7,  # 元/kWh
        name: str = "ChargeDischargeStrategy"
    ):
        """
        初始化充放电策略
        
        Args:
            P_rated: 额定功率
            E_capacity: 储能容量
            price_peak: 峰时电价
            price_valley: 谷时电价
            price_flat: 平时电价
        """
        self.name = name
        self.P_rated = P_rated
        self.E_capacity = E_capacity
        self.price_peak = price_peak
        self.price_valley = price_valley
        self.price_flat = price_flat
    
    def compute_power_reference(self, hour: int, soc: float) -> float:
        """
        计算功率参考
        
        策略:
        - 谷时 (23:00-7:00): 充电
        - 峰时 (10:00-15:00, 18:00-21:00): 放电
        - 平时: 待机
        
        Args:
            hour: 当前小时 (0-23)
            soc: 当前SOC (0-1)
            
        Returns:
            功率参考 (W), 充电为正
        """
        # 谷时充电
        if (hour >= 23 or hour < 7) and soc < 0.9:
            P_ref = self.P_rated  # 充电
        # 峰时放电
        elif ((10 <= hour < 15) or (18 <= hour < 21)) and soc > 0.2:
            P_ref = -self.P_rated  # 放电
        else:
            P_ref = 0  # 待机
        
        return P_ref
    
    def compute_daily_profit(
        self,
        P_profile: np.ndarray,
        price_profile: np.ndarray,
        dt: float = 3600.0
    ) -> float:
        """
        计算日收益
        
        Args:
            P_profile: 24小时功率曲线 (W)
            price_profile: 24小时电价曲线 (元/kWh)
            dt: 时间步长 (s)
            
        Returns:
            日收益 (元)
        """
        # 能量 (kWh)
        E_profile = P_profile * dt / 3600 / 1000
        
        # 收益 = 放电收入 - 充电成本
        profit = -np.sum(E_profile * price_profile)
        
        return profit


class GridFormingVSG:
    """
    构网型储能 - 虚拟同步发电机(VSG)控制
    
    模拟同步机特性，提供惯量和阻尼
    """
    
    def __init__(
        self,
        J_virtual: float = 5.0,  # kg·m², 虚拟惯量
        D_virtual: float = 10.0,  # 虚拟阻尼系数
        K_q: float = 0.001,  # 无功-电压下垂系数
        V_nom: float = 380.0,  # V
        f_nom: float = 50.0,  # Hz
        P_rated: float = 500e3,  # W
        name: str = "GridFormingVSG"
    ):
        """
        初始化VSG控制器
        
        Args:
            J_virtual: 虚拟惯量
            D_virtual: 虚拟阻尼
            K_q: 无功-电压下垂系数
            V_nom: 额定电压
            f_nom: 额定频率
            P_rated: 额定功率
        """
        self.name = name
        self.J = J_virtual
        self.D = D_virtual
        self.K_q = K_q
        self.V_nom = V_nom
        self.f_nom = f_nom
        self.omega_nom = 2 * np.pi * f_nom
        self.P_rated = P_rated
        
        # 状态变量
        self.omega = self.omega_nom  # 角频率
        self.theta = 0.0  # 相角
        self.P_mech = 0.0  # 机械功率参考
    
    def compute_frequency_response(
        self,
        P_ref: float,
        P_output: float,
        dt: float
    ) -> float:
        """
        计算频率响应
        
        摇摆方程: J*dω/dt = P_mech - P_elec - D*(ω - ω_nom)
        
        Args:
            P_ref: 功率参考 (W)
            P_output: 实际输出功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            角频率 (rad/s)
        """
        # 功率不平衡
        delta_P = P_ref - P_output
        
        # 阻尼项
        damping = self.D * (self.omega - self.omega_nom)
        
        # 摇摆方程
        d_omega_dt = (delta_P - damping) / self.J
        
        self.omega += d_omega_dt * dt
        self.omega = np.clip(self.omega, 0.95 * self.omega_nom, 1.05 * self.omega_nom)
        
        # 更新相角
        self.theta += self.omega * dt
        self.theta = np.mod(self.theta, 2 * np.pi)
        
        return self.omega
    
    def compute_voltage_response(
        self,
        Q_ref: float,
        Q_output: float
    ) -> float:
        """
        计算电压响应
        
        无功-电压下垂: V = V_nom - K_q * (Q - Q_ref)
        
        Args:
            Q_ref: 无功功率参考 (Var)
            Q_output: 实际无功功率 (Var)
            
        Returns:
            电压参考 (V)
        """
        delta_Q = Q_output - Q_ref
        V_ref = self.V_nom - self.K_q * delta_Q
        V_ref = np.clip(V_ref, 0.9 * self.V_nom, 1.1 * self.V_nom)
        
        return V_ref
    
    def get_frequency(self) -> float:
        """获取频率 (Hz)"""
        return self.omega / (2 * np.pi)


class BlackStartController:
    """
    储能黑启动控制器
    
    全黑状态下建立电压和频率
    """
    
    def __init__(
        self,
        V_target: float = 380.0,  # V
        f_target: float = 50.0,  # Hz
        ramp_rate_V: float = 50.0,  # V/s
        ramp_rate_f: float = 5.0,  # Hz/s
        name: str = "BlackStart"
    ):
        """
        初始化黑启动控制器
        
        Args:
            V_target: 目标电压
            f_target: 目标频率
            ramp_rate_V: 电压爬坡速率
            ramp_rate_f: 频率爬坡速率
        """
        self.name = name
        self.V_target = V_target
        self.f_target = f_target
        self.ramp_rate_V = ramp_rate_V
        self.ramp_rate_f = ramp_rate_f
        
        # 当前状态
        self.V_current = 0.0
        self.f_current = 0.0
        self.stage = 'idle'  # 'idle', 'voltage_buildup', 'frequency_buildup', 'ready'
    
    def start_sequence(self, dt: float) -> Dict:
        """
        执行启动序列
        
        Args:
            dt: 时间步长 (s)
            
        Returns:
            控制指令
        """
        if self.stage == 'idle':
            # 阶段1: 建立电压
            self.stage = 'voltage_buildup'
        
        if self.stage == 'voltage_buildup':
            self.V_current += self.ramp_rate_V * dt
            if self.V_current >= self.V_target:
                self.V_current = self.V_target
                self.stage = 'frequency_buildup'
        
        if self.stage == 'frequency_buildup':
            self.f_current += self.ramp_rate_f * dt
            if self.f_current >= self.f_target:
                self.f_current = self.f_target
                self.stage = 'ready'
        
        return {
            'V_ref': self.V_current,
            'f_ref': self.f_current,
            'stage': self.stage,
        }
