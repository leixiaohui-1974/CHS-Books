"""
发电机建模模块

包含:
1. DFIG - 双馈感应发电机
2. PMSG - 永磁同步发电机
3. 传动系统模型
4. 并网动态模型

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple


class DFIGModel:
    """
    双馈感应发电机（Doubly-Fed Induction Generator）模型
    
    基于dq同步旋转坐标系的三阶模型
    """
    
    def __init__(
        self,
        P_rated: float = 2e6,      # 额定功率 (W)
        V_rated: float = 690,       # 额定电压 (V, line-to-line)
        f_rated: float = 50,        # 额定频率 (Hz)
        poles: int = 4,             # 极对数
        Rs: float = 0.01,           # 定子电阻 (pu)
        Rr: float = 0.01,           # 转子电阻 (pu)
        Lm: float = 3.0,            # 励磁电感 (pu)
        Lls: float = 0.1,           # 定子漏感 (pu)
        Llr: float = 0.1,           # 转子漏感 (pu)
        name: str = "DFIG"
    ):
        """
        初始化DFIG模型
        
        Args:
            P_rated: 额定功率 (W)
            V_rated: 额定电压 (V, line-to-line)
            f_rated: 额定频率 (Hz)
            poles: 极对数
            Rs, Rr: 定子/转子电阻 (pu)
            Lm: 励磁电感 (pu)
            Lls, Llr: 定子/转子漏感 (pu)
        """
        self.name = name
        self.P_rated = P_rated
        self.V_rated = V_rated
        self.f_rated = f_rated
        self.poles = poles
        
        # 电阻 (pu)
        self.Rs = Rs
        self.Rr = Rr
        
        # 电感 (pu)
        self.Lm = Lm
        self.Lls = Lls
        self.Llr = Llr
        self.Ls = Lm + Lls  # 定子自感
        self.Lr = Lm + Llr  # 转子自感
        
        # 同步速度
        self.omega_s = 2 * np.pi * f_rated  # rad/s (电角速度)
        self.n_sync = 60 * f_rated / (poles / 2)  # RPM
        
        # 基准值
        self.V_base = V_rated / np.sqrt(3)  # 相电压
        self.I_base = P_rated / (np.sqrt(3) * V_rated)
        self.Z_base = self.V_base / self.I_base
        self.L_base = self.Z_base / self.omega_s
        
    def compute_slip(self, omega_r: float) -> float:
        """
        计算转差率
        
        Args:
            omega_r: 转子机械角速度 (rad/s)
            
        Returns:
            转差率 s
        """
        omega_e = omega_r * self.poles / 2  # 电角速度
        s = (self.omega_s - omega_e) / self.omega_s
        return s
    
    def steady_state(
        self, 
        s: float, 
        Vs_dq: Tuple[float, float] = None
    ) -> Dict:
        """
        稳态分析
        
        Args:
            s: 转差率
            Vs_dq: 定子电压dq分量 (Vsd, Vsq), 默认为额定电压
            
        Returns:
            稳态结果字典
        """
        if Vs_dq is None:
            Vs_dq = (0, self.V_base)  # 定子电压矢量定向到q轴
        
        Vsd, Vsq = Vs_dq
        
        # 转子角频率（电角速度）
        omega_r = (1 - s) * self.omega_s
        omega_slip = s * self.omega_s
        
        # 稳态时 d/dt = 0，简化方程
        # 假设转子电压为0（短路转子）
        Vrd, Vrq = 0, 0
        
        # 求解磁链（简化）
        # 完整求解需要联立方程，这里用近似
        # psi_sd = Ls * Isd + Lm * Ird
        # psi_sq = Ls * Isq + Lm * Irq
        # 转子短路: Vrq = 0 = Rr*Irq + s*omega_s*(psi_rd)
        
        # 简化计算：假设矢量控制下Isd=0
        Isd = 0
        
        # Vsq ≈ omega_s * psi_sd
        psi_sd = Vsq / self.omega_s
        Isq = (psi_sd / self.Ls) if self.Ls > 0 else 0
        
        # 转子电流（近似）
        Ird = 0
        Irq = -self.Lm / self.Lr * Isq
        
        # 功率
        Ps = 1.5 * (Vsd * Isd + Vsq * Isq)
        Te = 1.5 * self.poles / 2 * self.Lm * (Isq * Ird - Isd * Irq)
        
        return {
            's': s,
            'omega_r': omega_r,
            'Isd': Isd,
            'Isq': Isq,
            'Ird': Ird,
            'Irq': Irq,
            'psi_sd': psi_sd,
            'psi_sq': Vsq / self.omega_s,
            'Te': Te,
            'Ps': Ps,
            'Qs': 0,  # 简化
        }
    
    def dynamic_equations(
        self,
        t: float,
        state: np.ndarray,
        Vr_dq: Tuple[float, float],
        Vs_dq: Tuple[float, float],
        Tm: float
    ) -> np.ndarray:
        """
        动态方程 (三阶简化模型)
        
        状态变量: [psi_rd, psi_rq, omega_r]
        
        Args:
            t: 时间
            state: 状态向量 [psi_rd, psi_rq, omega_r]
            Vr_dq: 转子电压 (Vrd, Vrq)
            Vs_dq: 定子电压 (Vsd, Vsq)
            Tm: 机械转矩
            
        Returns:
            状态导数
        """
        psi_rd, psi_rq, omega_r = state
        Vrd, Vrq = Vr_dq
        Vsd, Vsq = Vs_dq
        
        # 电角速度
        omega_e = omega_r * self.poles / 2
        omega_slip = self.omega_s - omega_e
        
        # 转子电流
        Ird = (psi_rd - self.Lm / self.Ls * (Vsd / self.omega_s)) / self.Llr
        Irq = (psi_rq - self.Lm / self.Ls * (Vsq / self.omega_s)) / self.Llr
        
        # 定子电流
        Isd = (Vsd / self.omega_s - psi_rd) / self.Lls
        Isq = (Vsq / self.omega_s - psi_rq) / self.Lls
        
        # 磁链方程
        dpsi_rd = Vrd - self.Rr * Ird + omega_slip * psi_rq
        dpsi_rq = Vrq - self.Rr * Irq - omega_slip * psi_rd
        
        # 电磁转矩
        Te = 1.5 * self.poles / 2 * self.Lm * (Isq * Ird - Isd * Irq)
        
        # 运动方程（简化，忽略惯性）
        # J * domega_r = Tm - Te
        J = 100  # kg*m^2 (示例值)
        domega_r = (Tm - Te) / J
        
        return np.array([dpsi_rd, dpsi_rq, domega_r])
    
    def simulate_step(
        self,
        state: np.ndarray,
        Vr_dq: Tuple[float, float],
        Vs_dq: Tuple[float, float],
        Tm: float,
        dt: float
    ) -> Tuple[np.ndarray, Dict]:
        """
        单步仿真（Euler法）
        
        Args:
            state: 当前状态 [psi_rd, psi_rq, omega_r]
            Vr_dq: 转子电压
            Vs_dq: 定子电压
            Tm: 机械转矩
            dt: 时间步长
            
        Returns:
            (新状态, 输出字典)
        """
        # 计算导数
        dstate = self.dynamic_equations(0, state, Vr_dq, Vs_dq, Tm)
        
        # Euler积分
        new_state = state + dstate * dt
        
        # 计算输出
        psi_rd, psi_rq, omega_r = new_state
        omega_e = omega_r * self.poles / 2
        omega_slip = self.omega_s - omega_e
        s = omega_slip / self.omega_s
        
        Vsd, Vsq = Vs_dq
        Ird = (psi_rd - self.Lm / self.Ls * (Vsd / self.omega_s)) / self.Llr
        Irq = (psi_rq - self.Lm / self.Ls * (Vsq / self.omega_s)) / self.Llr
        Isd = (Vsd / self.omega_s - psi_rd) / self.Lls
        Isq = (Vsq / self.omega_s - psi_rq) / self.Lls
        
        Te = 1.5 * self.poles / 2 * self.Lm * (Isq * Ird - Isd * Irq)
        Ps = 1.5 * (Vsd * Isd + Vsq * Isq)
        Qs = 1.5 * (Vsq * Isd - Vsd * Isq)
        
        output = {
            't': 0,
            's': s,
            'omega_r': omega_r,
            'omega_rpm': omega_r * 60 / (2*np.pi),
            'psi_rd': psi_rd,
            'psi_rq': psi_rq,
            'Isd': Isd,
            'Isq': Isq,
            'Ird': Ird,
            'Irq': Irq,
            'Te': Te,
            'Ps': Ps,
            'Qs': Qs,
        }
        
        return new_state, output


class PMSGModel:
    """
    永磁同步发电机（Permanent Magnet Synchronous Generator）模型
    
    基于dq旋转坐标系
    """
    
    def __init__(
        self,
        P_rated: float = 2e6,
        V_rated: float = 690,
        f_rated: float = 50,
        poles: int = 60,           # 直驱式，极对数多
        Rs: float = 0.01,
        Ld: float = 0.8,           # d轴电感 (pu)
        Lq: float = 0.8,           # q轴电感 (pu)
        psi_f: float = 1.0,        # 永磁体磁链 (pu)
        name: str = "PMSG"
    ):
        """
        初始化PMSG模型
        """
        self.name = name
        self.P_rated = P_rated
        self.V_rated = V_rated
        self.f_rated = f_rated
        self.poles = poles
        
        self.Rs = Rs
        self.Ld = Ld
        self.Lq = Lq
        self.psi_f = psi_f
        
        self.omega_base = 2 * np.pi * f_rated
        
    def electromagnetic_torque(self, Id: float, Iq: float) -> float:
        """
        计算电磁转矩
        
        Te = 1.5 * p * [psi_f * Iq + (Ld - Lq) * Id * Iq]
        
        对于表贴式PMSG, Ld ≈ Lq，简化为: Te = 1.5 * p * psi_f * Iq
        """
        Te = 1.5 * self.poles / 2 * (
            self.psi_f * Iq + (self.Ld - self.Lq) * Id * Iq
        )
        return Te
    
    def voltage_equations(
        self,
        Id: float,
        Iq: float,
        omega_e: float
    ) -> Tuple[float, float]:
        """
        电压方程（稳态）
        
        Vd = Rs * Id - omega_e * Lq * Iq
        Vq = Rs * Iq + omega_e * (Ld * Id + psi_f)
        """
        Vd = self.Rs * Id - omega_e * self.Lq * Iq
        Vq = self.Rs * Iq + omega_e * (self.Ld * Id + self.psi_f)
        return Vd, Vq
    
    def steady_state(self, omega_r: float, Iq: float, Id: float = 0) -> Dict:
        """
        稳态运行点计算
        
        Args:
            omega_r: 转子机械角速度 (rad/s)
            Iq: q轴电流 (A)
            Id: d轴电流 (A, 通常为0)
            
        Returns:
            稳态结果
        """
        omega_e = omega_r * self.poles / 2
        
        Te = self.electromagnetic_torque(Id, Iq)
        Vd, Vq = self.voltage_equations(Id, Iq, omega_e)
        
        Ps = 1.5 * (Vd * Id + Vq * Iq)
        Qs = 1.5 * (Vq * Id - Vd * Iq)
        
        return {
            'omega_r': omega_r,
            'omega_rpm': omega_r * 60 / (2*np.pi),
            'omega_e': omega_e,
            'Id': Id,
            'Iq': Iq,
            'Vd': Vd,
            'Vq': Vq,
            'Te': Te,
            'Ps': Ps,
            'Qs': Qs,
        }


class DrivetrainModel:
    """
    传动系统两质量模型
    
    风轮 - 柔性轴 - 发电机
    """
    
    def __init__(
        self,
        Jt: float = 1e7,           # 风轮转动惯量 (kg*m^2)
        Jg: float = 1e5,           # 发电机转动惯量 (kg*m^2)
        Ks: float = 1e8,           # 轴刚度 (N*m/rad)
        Cs: float = 1e6,           # 轴阻尼 (N*m*s/rad)
        N: float = 100,            # 齿轮箱变比
        name: str = "Drivetrain"
    ):
        """
        初始化传动系统模型
        
        Args:
            Jt: 风轮转动惯量
            Jg: 发电机转动惯量
            Ks: 轴刚度
            Cs: 轴阻尼
            N: 齿轮箱变比（风轮侧/发电机侧）
        """
        self.name = name
        self.Jt = Jt
        self.Jg = Jg
        self.Ks = Ks
        self.Cs = Cs
        self.N = N
    
    def dynamics(
        self,
        t: float,
        state: np.ndarray,
        Tt: float,
        Tg: float
    ) -> np.ndarray:
        """
        两质量模型动态方程
        
        状态: [theta_t, omega_t, theta_g, omega_g]
        
        Args:
            t: 时间
            state: 状态向量
            Tt: 风轮转矩
            Tg: 发电机转矩
            
        Returns:
            状态导数
        """
        theta_t, omega_t, theta_g, omega_g = state
        
        # 轴扭转角（转换到同一侧）
        theta_twist = theta_t - self.N * theta_g
        omega_twist = omega_t - self.N * omega_g
        
        # 轴转矩
        Ts = self.Ks * theta_twist + self.Cs * omega_twist
        
        # 风轮侧
        dtheta_t = omega_t
        domega_t = (Tt - Ts) / self.Jt
        
        # 发电机侧
        dtheta_g = omega_g
        domega_g = (self.N * Ts - Tg) / self.Jg
        
        return np.array([dtheta_t, domega_t, dtheta_g, domega_g])
    
    def simulate(
        self,
        t_span: Tuple[float, float],
        state0: np.ndarray,
        Tt_func,
        Tg_func,
        dt: float = 0.01
    ) -> Dict:
        """
        时域仿真
        
        Args:
            t_span: 时间范围 (t0, tf)
            state0: 初始状态
            Tt_func: 风轮转矩函数 Tt(t)
            Tg_func: 发电机转矩函数 Tg(t)
            dt: 时间步长
            
        Returns:
            仿真结果
        """
        t0, tf = t_span
        N = int((tf - t0) / dt)
        
        t_array = np.linspace(t0, tf, N)
        state_array = np.zeros((N, 4))
        state_array[0] = state0
        
        state = state0.copy()
        
        for i in range(1, N):
            t = t_array[i]
            Tt = Tt_func(t)
            Tg = Tg_func(t)
            
            dstate = self.dynamics(t, state, Tt, Tg)
            state = state + dstate * dt
            state_array[i] = state
        
        return {
            't': t_array,
            'theta_t': state_array[:, 0],
            'omega_t': state_array[:, 1],
            'theta_g': state_array[:, 2],
            'omega_g': state_array[:, 3],
        }


def abc_to_dq(I_abc: np.ndarray, theta: float) -> Tuple[float, float]:
    """
    ABC坐标系到dq坐标系变换（Clarke-Park变换）
    
    Args:
        I_abc: ABC三相电流 [Ia, Ib, Ic]
        theta: 转子位置角 (rad)
        
    Returns:
        (Id, Iq)
    """
    Ia, Ib, Ic = I_abc
    
    # Clarke变换 (ABC -> αβ)
    I_alpha = Ia
    I_beta = (Ia + 2*Ib) / np.sqrt(3)
    
    # Park变换 (αβ -> dq)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    
    Id = I_alpha * cos_theta + I_beta * sin_theta
    Iq = -I_alpha * sin_theta + I_beta * cos_theta
    
    return Id, Iq


def dq_to_abc(Id: float, Iq: float, theta: float) -> np.ndarray:
    """
    dq坐标系到ABC坐标系反变换
    
    Args:
        Id, Iq: dq电流
        theta: 转子位置角
        
    Returns:
        [Ia, Ib, Ic]
    """
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    
    # Park反变换 (dq -> αβ)
    I_alpha = Id * cos_theta - Iq * sin_theta
    I_beta = Id * sin_theta + Iq * cos_theta
    
    # Clarke反变换 (αβ -> ABC)
    Ia = I_alpha
    Ib = (-I_alpha + np.sqrt(3) * I_beta) / 2
    Ic = (-I_alpha - np.sqrt(3) * I_beta) / 2
    
    return np.array([Ia, Ib, Ic])
