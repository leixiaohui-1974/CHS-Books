"""
变流器控制模块

包含:
1. DFIG转子侧控制（RSC）
2. DFIG网侧控制（GSC）
3. PMSG全功率变流器控制
4. dq解耦控制
5. 电流环控制器
6. LVRT控制
7. 有功/无功控制

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple
from .control import PIDController


class DQCurrentController:
    """
    dq电流解耦控制器
    
    基于前馈解耦的PI电流环
    """
    
    def __init__(
        self,
        Kp_d: float = 1.0,
        Ki_d: float = 10.0,
        Kp_q: float = 1.0,
        Ki_q: float = 10.0,
        L: float = 0.1,
        omega_base: float = 314.0,
        name: str = "DQ_Current"
    ):
        """
        初始化dq电流控制器
        
        Args:
            Kp_d, Ki_d: d轴PI参数
            Kp_q, Ki_q: q轴PI参数
            L: 电感 (pu)
            omega_base: 基准角频率
        """
        self.name = name
        self.L = L
        self.omega_base = omega_base
        
        # d轴PI控制器
        self.pi_d = PIDController(Kp=Kp_d, Ki=Ki_d, Kd=0, output_limits=(-1, 1))
        
        # q轴PI控制器
        self.pi_q = PIDController(Kp=Kp_q, Ki=Ki_q, Kd=0, output_limits=(-1, 1))
    
    def compute_voltage(
        self,
        Id_ref: float,
        Iq_ref: float,
        Id_meas: float,
        Iq_meas: float,
        omega_e: float,
        dt: float
    ) -> Dict:
        """
        计算dq轴电压指令
        
        包含解耦前馈补偿：
        Vd = PI_d(Id_ref - Id) - omega_e * L * Iq
        Vq = PI_q(Iq_ref - Iq) + omega_e * L * Id
        
        Args:
            Id_ref, Iq_ref: dq电流参考值
            Id_meas, Iq_meas: dq电流测量值
            omega_e: 电角频率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # PI控制
        Vd_pi = self.pi_d.compute(Id_ref, Id_meas, dt)
        Vq_pi = self.pi_q.compute(Iq_ref, Iq_meas, dt)
        
        # 解耦前馈
        Vd_ff = -omega_e * self.L * Iq_meas
        Vq_ff = omega_e * self.L * Id_meas
        
        # 总电压
        Vd = Vd_pi + Vd_ff
        Vq = Vq_pi + Vq_ff
        
        return {
            'Vd': Vd,
            'Vq': Vq,
            'Vd_pi': Vd_pi,
            'Vq_pi': Vq_pi,
            'Vd_ff': Vd_ff,
            'Vq_ff': Vq_ff,
        }


class DFIGRotorSideControl:
    """
    DFIG转子侧变流器（RSC）控制
    
    外环：有功/无功功率控制
    内环：dq电流控制
    """
    
    def __init__(
        self,
        Kp_P: float = 0.1,
        Ki_P: float = 1.0,
        Kp_Q: float = 0.1,
        Ki_Q: float = 1.0,
        Kp_i: float = 1.0,
        Ki_i: float = 10.0,
        Lr: float = 0.1,
        Lm: float = 3.0,
        name: str = "DFIG_RSC"
    ):
        """
        初始化RSC控制器
        
        Args:
            Kp_P, Ki_P: 有功功率外环PI
            Kp_Q, Ki_Q: 无功功率外环PI
            Kp_i, Ki_i: 电流内环PI
            Lr: 转子电感
            Lm: 励磁电感
        """
        self.name = name
        self.Lr = Lr
        self.Lm = Lm
        
        # 功率外环
        self.pi_P = PIDController(Kp=Kp_P, Ki=Ki_P, Kd=0)
        self.pi_Q = PIDController(Kp=Kp_Q, Ki=Ki_Q, Kd=0)
        
        # 电流内环
        self.current_ctrl = DQCurrentController(Kp_d=Kp_i, Ki_d=Ki_i, Kp_q=Kp_i, Ki_q=Ki_i, L=Lr)
    
    def compute_control(
        self,
        P_ref: float,
        Q_ref: float,
        P_meas: float,
        Q_meas: float,
        Ird: float,
        Irq: float,
        Vsd: float,
        Vsq: float,
        omega_slip: float,
        dt: float
    ) -> Dict:
        """
        RSC控制计算
        
        Args:
            P_ref, Q_ref: 功率参考值
            P_meas, Q_meas: 功率测量值
            Ird, Irq: 转子电流dq
            Vsd, Vsq: 定子电压dq
            omega_slip: 转差角频率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 功率外环 → 电流参考
        Irq_ref = self.pi_P.compute(P_ref, P_meas, dt)
        Ird_ref = self.pi_Q.compute(Q_ref, Q_meas, dt)
        
        # 电流内环 → 电压指令
        voltage = self.current_ctrl.compute_voltage(
            Ird_ref, Irq_ref, Ird, Irq, omega_slip, dt
        )
        
        return {
            'Vrd': voltage['Vd'],
            'Vrq': voltage['Vq'],
            'Ird_ref': Ird_ref,
            'Irq_ref': Irq_ref,
        }


class DFIGGridSideControl:
    """
    DFIG网侧变流器（GSC）控制
    
    外环：直流母线电压控制 + 无功功率控制
    内环：dq电流控制
    """
    
    def __init__(
        self,
        Kp_Vdc: float = 1.0,
        Ki_Vdc: float = 10.0,
        Kp_Q: float = 0.1,
        Ki_Q: float = 1.0,
        Kp_i: float = 1.0,
        Ki_i: float = 10.0,
        Lg: float = 0.1,
        name: str = "DFIG_GSC"
    ):
        """
        初始化GSC控制器
        
        Args:
            Kp_Vdc, Ki_Vdc: 直流电压外环PI
            Kp_Q, Ki_Q: 无功功率外环PI
            Kp_i, Ki_i: 电流内环PI
            Lg: 网侧电感
        """
        self.name = name
        self.Lg = Lg
        
        # 外环
        self.pi_Vdc = PIDController(Kp=Kp_Vdc, Ki=Ki_Vdc, Kd=0)
        self.pi_Q = PIDController(Kp=Kp_Q, Ki=Ki_Q, Kd=0)
        
        # 电流内环
        self.current_ctrl = DQCurrentController(Kp_d=Kp_i, Ki_d=Ki_i, Kp_q=Kp_i, Ki_q=Ki_i, L=Lg)
    
    def compute_control(
        self,
        Vdc_ref: float,
        Vdc_meas: float,
        Q_ref: float,
        Q_meas: float,
        Igd: float,
        Igq: float,
        omega_s: float,
        dt: float
    ) -> Dict:
        """
        GSC控制计算
        
        Args:
            Vdc_ref, Vdc_meas: 直流电压
            Q_ref, Q_meas: 无功功率
            Igd, Igq: 网侧电流dq
            omega_s: 同步角频率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 外环
        Igd_ref = self.pi_Vdc.compute(Vdc_ref, Vdc_meas, dt)
        Igq_ref = self.pi_Q.compute(Q_ref, Q_meas, dt)
        
        # 电流内环
        voltage = self.current_ctrl.compute_voltage(
            Igd_ref, Igq_ref, Igd, Igq, omega_s, dt
        )
        
        return {
            'Vgd': voltage['Vd'],
            'Vgq': voltage['Vq'],
            'Igd_ref': Igd_ref,
            'Igq_ref': Igq_ref,
        }


class PMSGFullConverter:
    """
    PMSG全功率变流器控制
    
    机侧：转矩/转速控制
    网侧：直流电压控制 + 功率控制
    """
    
    def __init__(
        self,
        Kp_omega: float = 100.0,
        Ki_omega: float = 1000.0,
        Kp_i_msc: float = 1.0,
        Ki_i_msc: float = 10.0,
        Kp_Vdc: float = 1.0,
        Ki_Vdc: float = 10.0,
        Kp_i_gsc: float = 1.0,
        Ki_i_gsc: float = 10.0,
        Ld: float = 0.8,
        Lq: float = 0.8,
        Lg: float = 0.1,
        name: str = "PMSG_FullConv"
    ):
        """
        初始化PMSG全功率变流器
        
        Args:
            Kp_omega, Ki_omega: 转速外环PI
            Kp_i_msc, Ki_i_msc: 机侧电流环PI
            Kp_Vdc, Ki_Vdc: 直流电压外环PI
            Kp_i_gsc, Ki_i_gsc: 网侧电流环PI
            Ld, Lq: 电机dq电感
            Lg: 网侧电感
        """
        self.name = name
        
        # 机侧控制（MSC）
        self.pi_omega = PIDController(Kp=Kp_omega, Ki=Ki_omega, Kd=0)
        self.msc_current = DQCurrentController(Kp_d=Kp_i_msc, Ki_d=Ki_i_msc, Kp_q=Kp_i_msc, Ki_q=Ki_i_msc, L=Ld)
        
        # 网侧控制（GSC）
        self.pi_Vdc = PIDController(Kp=Kp_Vdc, Ki=Ki_Vdc, Kd=0)
        self.gsc_current = DQCurrentController(Kp_d=Kp_i_gsc, Ki_d=Ki_i_gsc, Kp_q=Kp_i_gsc, Ki_q=Ki_i_gsc, L=Lg)
    
    def compute_machine_side(
        self,
        omega_ref: float,
        omega_meas: float,
        Id: float,
        Iq: float,
        omega_e: float,
        dt: float
    ) -> Dict:
        """
        机侧变流器控制
        
        Args:
            omega_ref, omega_meas: 转速参考/测量
            Id, Iq: 电机电流dq
            omega_e: 电角频率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 转速外环 → Iq参考（Id=0控制）
        Iq_ref = self.pi_omega.compute(omega_ref, omega_meas, dt)
        Id_ref = 0  # Id=0控制
        
        # 电流内环
        voltage = self.msc_current.compute_voltage(Id_ref, Iq_ref, Id, Iq, omega_e, dt)
        
        return {
            'Vd': voltage['Vd'],
            'Vq': voltage['Vq'],
            'Id_ref': Id_ref,
            'Iq_ref': Iq_ref,
        }
    
    def compute_grid_side(
        self,
        Vdc_ref: float,
        Vdc_meas: float,
        Q_ref: float,
        Q_meas: float,
        Igd: float,
        Igq: float,
        omega_s: float,
        dt: float
    ) -> Dict:
        """
        网侧变流器控制
        
        Args:
            Vdc_ref, Vdc_meas: 直流电压
            Q_ref, Q_meas: 无功功率
            Igd, Igq: 网侧电流
            omega_s: 同步角频率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 外环
        Igd_ref = self.pi_Vdc.compute(Vdc_ref, Vdc_meas, dt)
        Igq_ref = -Q_ref / (1.5 * 1.0)  # 简化Q控制
        
        # 电流内环
        voltage = self.gsc_current.compute_voltage(Igd_ref, Igq_ref, Igd, Igq, omega_s, dt)
        
        return {
            'Vgd': voltage['Vd'],
            'Vgq': voltage['Vq'],
            'Igd_ref': Igd_ref,
            'Igq_ref': Igq_ref,
        }


class LVRTController:
    """
    低电压穿越（LVRT）控制器
    
    电压跌落时的有功/无功控制策略
    """
    
    def __init__(
        self,
        V_threshold: float = 0.9,
        Q_gain: float = 2.0,
        I_max: float = 1.2,
        name: str = "LVRT"
    ):
        """
        初始化LVRT控制器
        
        Args:
            V_threshold: 电压跌落阈值（pu）
            Q_gain: 无功支撑增益
            I_max: 最大电流限制（pu）
        """
        self.name = name
        self.V_threshold = V_threshold
        self.Q_gain = Q_gain
        self.I_max = I_max
    
    def compute_current_limit(self, V_grid: float) -> Dict:
        """
        计算LVRT期间的电流限制
        
        Args:
            V_grid: 电网电压（pu）
            
        Returns:
            电流限制
        """
        if V_grid < self.V_threshold:
            # 电压跌落，限制有功增加无功
            V_dip = max(0.1, V_grid)
            
            # 有功电流限制（降低）
            Id_max = 0.5 * self.I_max
            
            # 无功电流（支撑电压）
            dV = self.V_threshold - V_grid
            Iq_ref = self.Q_gain * dV
            Iq_ref = min(Iq_ref, np.sqrt(self.I_max**2 - Id_max**2))
            
            mode = "LVRT"
        else:
            # 正常运行
            Id_max = self.I_max
            Iq_ref = 0
            mode = "Normal"
        
        return {
            'Id_max': Id_max,
            'Iq_ref': Iq_ref,
            'mode': mode,
            'V_grid': V_grid,
        }


class SSODampingController:
    """
    次同步振荡（SSO）抑制控制器
    
    基于附加阻尼控制
    """
    
    def __init__(
        self,
        K_damping: float = 0.1,
        omega_filter: float = 10.0,
        name: str = "SSO_Damping"
    ):
        """
        初始化SSO抑制控制器
        
        Args:
            K_damping: 阻尼增益
            omega_filter: 滤波器频率
        """
        self.name = name
        self.K_damping = K_damping
        self.omega_filter = omega_filter
        
        # 状态变量
        self.omega_filtered = 0
    
    def compute_damping_signal(
        self,
        omega: float,
        dt: float
    ) -> Dict:
        """
        计算附加阻尼信号
        
        Args:
            omega: 转速测量
            dt: 时间步长
            
        Returns:
            阻尼信号
        """
        # 一阶滤波器
        alpha = dt * self.omega_filter / (1 + dt * self.omega_filter)
        self.omega_filtered = alpha * omega + (1 - alpha) * self.omega_filtered
        
        # 计算转速偏差
        d_omega = omega - self.omega_filtered
        
        # 阻尼信号（附加到电流参考）
        damping_signal = -self.K_damping * d_omega
        
        return {
            'damping_signal': damping_signal,
            'd_omega': d_omega,
            'omega_filtered': self.omega_filtered,
        }


def compute_power_from_dq(Vd: float, Vq: float, Id: float, Iq: float) -> Tuple[float, float]:
    """
    从dq电压电流计算有功/无功功率
    
    P = 1.5 * (Vd * Id + Vq * Iq)
    Q = 1.5 * (Vq * Id - Vd * Iq)
    
    Args:
        Vd, Vq: dq电压
        Id, Iq: dq电流
        
    Returns:
        (P, Q)
    """
    P = 1.5 * (Vd * Id + Vq * Iq)
    Q = 1.5 * (Vq * Id - Vd * Iq)
    return P, Q


def abc_to_dq_transform(I_abc: np.ndarray, theta: float) -> Tuple[float, float]:
    """
    ABC到dq坐标变换（Park变换）
    
    Args:
        I_abc: ABC三相电流 [Ia, Ib, Ic]
        theta: 转子位置角
        
    Returns:
        (Id, Iq)
    """
    Ia, Ib, Ic = I_abc
    
    # Clarke变换
    I_alpha = Ia
    I_beta = (Ia + 2*Ib) / np.sqrt(3)
    
    # Park变换
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    
    Id = I_alpha * cos_theta + I_beta * sin_theta
    Iq = -I_alpha * sin_theta + I_beta * cos_theta
    
    return Id, Iq


def dq_to_abc_transform(Id: float, Iq: float, theta: float) -> np.ndarray:
    """
    dq到ABC坐标反变换
    
    Args:
        Id, Iq: dq电流
        theta: 转子位置角
        
    Returns:
        [Ia, Ib, Ic]
    """
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    
    # Park反变换
    I_alpha = Id * cos_theta - Iq * sin_theta
    I_beta = Id * sin_theta + Iq * cos_theta
    
    # Clarke反变换
    Ia = I_alpha
    Ib = (-I_alpha + np.sqrt(3) * I_beta) / 2
    Ic = (-I_alpha - np.sqrt(3) * I_beta) / 2
    
    return np.array([Ia, Ib, Ic])
