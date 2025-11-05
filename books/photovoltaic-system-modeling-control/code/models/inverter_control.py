"""
并网逆变器控制模块
包含PWM调制、电流控制、电压控制等核心算法

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class InverterParameters:
    """逆变器参数"""
    V_dc: float = 400.0          # 直流母线电压 (V)
    V_ac: float = 220.0          # 交流额定电压 (V RMS)
    f_ac: float = 50.0           # 交流频率 (Hz)
    f_sw: float = 10000.0        # 开关频率 (Hz)
    dead_time: float = 2e-6      # 死区时间 (s)
    
    # 滤波器参数
    L_filter: float = 5e-3       # 滤波电感 (H)
    C_filter: float = 10e-6      # 滤波电容 (F)
    R_filter: float = 0.1        # 电感等效电阻 (Ω)


class PWMModulator:
    """PWM调制器基类"""
    
    def __init__(self, params: InverterParameters):
        self.params = params
        self.t = 0.0
        self.omega = 2 * np.pi * params.f_ac
        self.T_sw = 1.0 / params.f_sw
        
        # 历史记录
        self.history = {
            'time': [],
            'modulation_wave': [],
            'carrier_wave': [],
            'switching_signal': [],
            'output_voltage': []
        }
    
    def generate_reference(self, t: float, amplitude: float = None, phase: float = 0.0) -> float:
        """
        生成参考正弦波
        
        Args:
            t: 时间 (s)
            amplitude: 幅值 (如果为None，使用额定电压)
            phase: 相位角 (rad)
            
        Returns:
            参考信号值
        """
        if amplitude is None:
            amplitude = self.params.V_ac * np.sqrt(2)  # 转换为峰值
        
        return amplitude * np.sin(self.omega * t + phase)
    
    def modulate(self, v_ref: float, t: float) -> Tuple[float, Dict]:
        """
        执行PWM调制 (抽象方法，子类实现)
        
        Args:
            v_ref: 参考电压 (V)
            t: 当前时间 (s)
            
        Returns:
            (switching_signal, info_dict)
        """
        raise NotImplementedError("子类必须实现modulate方法")
    
    def calculate_thd(self, signal: np.ndarray, fs: float, f0: float, n_harmonics: int = 50) -> Dict:
        """
        计算总谐波失真(THD)
        
        Args:
            signal: 信号数组
            fs: 采样频率 (Hz)
            f0: 基波频率 (Hz)
            n_harmonics: 计算的谐波次数
            
        Returns:
            包含THD和谐波分量的字典
        """
        # FFT分析
        N = len(signal)
        fft_result = np.fft.fft(signal) / N
        freqs = np.fft.fftfreq(N, 1/fs)
        
        # 提取正频率部分
        positive_freqs = freqs[:N//2]
        magnitude = 2 * np.abs(fft_result[:N//2])
        
        # 找基波
        f0_idx = np.argmin(np.abs(positive_freqs - f0))
        fundamental = magnitude[f0_idx]
        
        # 计算谐波
        harmonics = {}
        harmonic_sum_sq = 0.0
        
        for n in range(2, n_harmonics + 1):
            fn = n * f0
            fn_idx = np.argmin(np.abs(positive_freqs - fn))
            
            # 确保频率匹配在合理范围内
            if np.abs(positive_freqs[fn_idx] - fn) < f0 / 2:
                h_mag = magnitude[fn_idx]
                harmonics[n] = h_mag
                harmonic_sum_sq += h_mag ** 2
        
        # 计算THD
        thd = np.sqrt(harmonic_sum_sq) / fundamental * 100 if fundamental > 0 else 0.0
        
        return {
            'THD': thd,
            'fundamental': fundamental,
            'harmonics': harmonics,
            'frequencies': positive_freqs,
            'magnitude': magnitude
        }


class SPWMModulator(PWMModulator):
    """
    正弦脉宽调制(SPWM)
    
    原理:
        将正弦调制波与三角载波比较，产生PWM信号
        
    特点:
        - 实现简单
        - 谐波性能良好
        - 直流电压利用率约86.6%
    """
    
    def __init__(self, params: InverterParameters, modulation_index: float = 0.9):
        """
        初始化SPWM调制器
        
        Args:
            params: 逆变器参数
            modulation_index: 调制比 (0-1), 默认0.9
        """
        super().__init__(params)
        self.modulation_index = modulation_index
        self.name = "SPWM"
        
        # 载波频率比
        self.mf = int(params.f_sw / params.f_ac)  # 频率比
        
    def modulate(self, v_ref: float, t: float) -> Tuple[float, Dict]:
        """
        SPWM调制
        
        Args:
            v_ref: 参考电压 (V)
            t: 当前时间 (s)
            
        Returns:
            (switching_signal, info_dict)
            switching_signal: 开关信号 (1或0)
            info_dict: 包含调制波、载波等信息
        """
        # 归一化调制波 (-1 to 1)
        m_wave = (v_ref / self.params.V_dc) * self.modulation_index
        
        # 生成三角载波 (-1 to 1)
        carrier_phase = (t % self.T_sw) / self.T_sw
        if carrier_phase < 0.5:
            c_wave = -1 + 4 * carrier_phase  # 上升沿
        else:
            c_wave = 3 - 4 * carrier_phase   # 下降沿
        
        # 比较产生开关信号
        switching_signal = 1.0 if m_wave > c_wave else 0.0
        
        # 输出电压 (对于单相H桥)
        v_out = self.params.V_dc * (switching_signal - 0.5) * 2
        
        info = {
            'modulation_wave': m_wave,
            'carrier_wave': c_wave,
            'switching_signal': switching_signal,
            'output_voltage': v_out,
            'modulation_index': self.modulation_index
        }
        
        return switching_signal, info
    
    def simulate(self, duration: float, dt: float = None) -> Dict:
        """
        仿真SPWM调制过程
        
        Args:
            duration: 仿真时长 (s)
            dt: 时间步长 (s), 默认为开关周期的1/100
            
        Returns:
            包含时间历史的字典
        """
        if dt is None:
            dt = self.T_sw / 100
        
        time = np.arange(0, duration, dt)
        N = len(time)
        
        # 初始化数组
        v_ref = np.zeros(N)
        mod_wave = np.zeros(N)
        carrier = np.zeros(N)
        sw_signal = np.zeros(N)
        v_out = np.zeros(N)
        
        # 生成参考电压
        v_ref = self.generate_reference(time)
        
        # 逐点调制
        for i, t in enumerate(time):
            sw, info = self.modulate(v_ref[i], t)
            mod_wave[i] = info['modulation_wave']
            carrier[i] = info['carrier_wave']
            sw_signal[i] = info['switching_signal']
            v_out[i] = info['output_voltage']
        
        return {
            'time': time,
            'v_ref': v_ref,
            'modulation_wave': mod_wave,
            'carrier_wave': carrier,
            'switching_signal': sw_signal,
            'output_voltage': v_out,
            'modulation_index': self.modulation_index,
            'frequency_ratio': self.mf
        }


class SVPWMModulator:
    """
    空间矢量脉宽调制(SVPWM)
    
    原理:
        将三相电压矢量分解为基本矢量的线性组合
        通过选择合适的矢量和作用时间，合成期望的电压矢量
        
    特点:
        - 直流电压利用率高 (约100%)
        - 谐波性能优秀
        - 计算相对复杂
    """
    
    def __init__(self, params: InverterParameters):
        super().__init__()
        self.params = params
        self.name = "SVPWM"
        self.T_s = 1.0 / params.f_sw  # 采样周期
        
        # 六个基本电压矢量的角度 (rad)
        self.sector_angles = np.array([0, np.pi/3, 2*np.pi/3, np.pi, 
                                       4*np.pi/3, 5*np.pi/3])
        
        # 八个开关状态对应的电压矢量 (归一化)
        self.basic_vectors = self._generate_basic_vectors()
        
    def _generate_basic_vectors(self) -> np.ndarray:
        """生成八个基本电压矢量 (Clarke变换后的αβ坐标)"""
        vectors = np.zeros((8, 2))
        
        # V1-V6: 有效矢量
        for i in range(6):
            angle = i * np.pi / 3
            vectors[i+1] = [np.cos(angle), np.sin(angle)]
        
        # V0, V7: 零矢量
        vectors[0] = [0, 0]
        vectors[7] = [0, 0]
        
        return vectors * (2.0 / 3.0)  # 归一化系数
    
    def clarke_transform(self, va: float, vb: float, vc: float) -> Tuple[float, float]:
        """
        Clarke变换: abc → αβ
        
        Args:
            va, vb, vc: 三相电压
            
        Returns:
            (v_alpha, v_beta)
        """
        v_alpha = (2*va - vb - vc) / 3
        v_beta = (vb - vc) / np.sqrt(3)
        
        return v_alpha, v_beta
    
    def inverse_clarke_transform(self, v_alpha: float, v_beta: float) -> Tuple[float, float, float]:
        """
        逆Clarke变换: αβ → abc
        
        Args:
            v_alpha, v_beta: αβ坐标系电压
            
        Returns:
            (va, vb, vc)
        """
        va = v_alpha
        vb = -0.5 * v_alpha + np.sqrt(3)/2 * v_beta
        vc = -0.5 * v_alpha - np.sqrt(3)/2 * v_beta
        
        return va, vb, vc
    
    def get_sector(self, v_alpha: float, v_beta: float) -> int:
        """
        判断参考矢量所在扇区 (1-6)
        
        Args:
            v_alpha, v_beta: αβ坐标系电压
            
        Returns:
            扇区号 (1-6)
        """
        angle = np.arctan2(v_beta, v_alpha)
        if angle < 0:
            angle += 2 * np.pi
        
        sector = int(np.floor(angle / (np.pi / 3))) + 1
        if sector > 6:
            sector = 6
        if sector < 1:
            sector = 1
        
        return sector
    
    def calculate_duty_cycles(self, v_alpha: float, v_beta: float, V_dc: float) -> Tuple[int, float, float, float]:
        """
        计算矢量作用时间
        
        Args:
            v_alpha, v_beta: 参考电压矢量 (αβ坐标)
            V_dc: 直流母线电压
            
        Returns:
            (sector, T1, T2, T0)
            sector: 扇区号
            T1, T2: 两个相邻有效矢量的作用时间 (归一化)
            T0: 零矢量作用时间 (归一化)
        """
        # 判断扇区
        sector = self.get_sector(v_alpha, v_beta)
        
        # 计算参考矢量的幅值和相位
        V_ref = np.sqrt(v_alpha**2 + v_beta**2)
        theta = np.arctan2(v_beta, v_alpha)
        
        # 扇区内部角度 (相对于扇区起始角)
        theta_sector = theta - (sector - 1) * np.pi / 3
        
        # 计算调制比
        m = V_ref / (V_dc * np.sqrt(3) / 2)
        
        # 限制调制比
        if m > 1.0:
            m = 1.0
        
        # 计算矢量作用时间 (归一化到采样周期)
        T1 = m * np.sin(np.pi/3 - theta_sector)
        T2 = m * np.sin(theta_sector)
        T0 = 1 - T1 - T2
        
        # 确保时间非负
        T1 = max(0, min(1, T1))
        T2 = max(0, min(1, T2))
        T0 = max(0, 1 - T1 - T2)
        
        return sector, T1, T2, T0
    
    def generate_switching_times(self, sector: int, T1: float, T2: float, T0: float) -> Dict:
        """
        生成三相开关时间
        
        七段式SVPWM序列: V0 - V1 - V2 - V7 - V2 - V1 - V0
        
        Args:
            sector: 扇区号 (1-6)
            T1, T2: 相邻矢量作用时间 (归一化)
            T0: 零矢量作用时间 (归一化)
            
        Returns:
            三相导通时间字典
        """
        # 零矢量均分
        T0_half = T0 / 2
        
        # 七段式排列
        Ta = T0_half
        Tb = Ta + T1
        Tc = Tb + T2
        # 对称排列
        
        # 根据扇区计算三相导通时间
        switching_times = {'Ta': 0, 'Tb': 0, 'Tc': 0}
        
        if sector == 1:
            switching_times['Ta'] = Tc
            switching_times['Tb'] = Tb
            switching_times['Tc'] = Ta
        elif sector == 2:
            switching_times['Ta'] = Tb
            switching_times['Tb'] = Tc
            switching_times['Tc'] = Ta
        elif sector == 3:
            switching_times['Ta'] = Ta
            switching_times['Tb'] = Tc
            switching_times['Tc'] = Tb
        elif sector == 4:
            switching_times['Ta'] = Ta
            switching_times['Tb'] = Tb
            switching_times['Tc'] = Tc
        elif sector == 5:
            switching_times['Ta'] = Tb
            switching_times['Tb'] = Ta
            switching_times['Tc'] = Tc
        elif sector == 6:
            switching_times['Ta'] = Tc
            switching_times['Tb'] = Ta
            switching_times['Tc'] = Tb
        
        return switching_times
    
    def modulate(self, va_ref: float, vb_ref: float, vc_ref: float, V_dc: float) -> Dict:
        """
        SVPWM调制
        
        Args:
            va_ref, vb_ref, vc_ref: 三相参考电压
            V_dc: 直流母线电压
            
        Returns:
            调制信息字典
        """
        # Clarke变换
        v_alpha, v_beta = self.clarke_transform(va_ref, vb_ref, vc_ref)
        
        # 计算占空比
        sector, T1, T2, T0 = self.calculate_duty_cycles(v_alpha, v_beta, V_dc)
        
        # 生成开关时间
        switching_times = self.generate_switching_times(sector, T1, T2, T0)
        
        return {
            'v_alpha': v_alpha,
            'v_beta': v_beta,
            'sector': sector,
            'T1': T1,
            'T2': T2,
            'T0': T0,
            'switching_times': switching_times
        }
    
    def simulate(self, duration: float, amplitude: float = None, frequency: float = None) -> Dict:
        """
        仿真SVPWM三相调制过程
        
        Args:
            duration: 仿真时长 (s)
            amplitude: 电压幅值 (V), 默认使用额定值
            frequency: 频率 (Hz), 默认使用额定值
            
        Returns:
            仿真结果字典
        """
        if amplitude is None:
            amplitude = self.params.V_ac * np.sqrt(2)
        if frequency is None:
            frequency = self.params.f_ac
        
        omega = 2 * np.pi * frequency
        dt = self.T_s / 10  # 每个开关周期10个点
        time = np.arange(0, duration, dt)
        N = len(time)
        
        # 初始化数组
        va_ref = amplitude * np.sin(omega * time)
        vb_ref = amplitude * np.sin(omega * time - 2*np.pi/3)
        vc_ref = amplitude * np.sin(omega * time + 2*np.pi/3)
        
        v_alpha = np.zeros(N)
        v_beta = np.zeros(N)
        sectors = np.zeros(N, dtype=int)
        T1_arr = np.zeros(N)
        T2_arr = np.zeros(N)
        T0_arr = np.zeros(N)
        
        # 逐点调制
        for i in range(N):
            result = self.modulate(va_ref[i], vb_ref[i], vc_ref[i], self.params.V_dc)
            v_alpha[i] = result['v_alpha']
            v_beta[i] = result['v_beta']
            sectors[i] = result['sector']
            T1_arr[i] = result['T1']
            T2_arr[i] = result['T2']
            T0_arr[i] = result['T0']
        
        return {
            'time': time,
            'va_ref': va_ref,
            'vb_ref': vb_ref,
            'vc_ref': vc_ref,
            'v_alpha': v_alpha,
            'v_beta': v_beta,
            'sectors': sectors,
            'T1': T1_arr,
            'T2': T2_arr,
            'T0': T0_arr
        }


class InverterModel:
    """
    逆变器系统模型
    包含PWM调制器和输出滤波器
    """
    
    def __init__(self, params: InverterParameters, modulator: PWMModulator):
        self.params = params
        self.modulator = modulator
        
        # 滤波器状态变量
        self.i_L = 0.0  # 电感电流 (A)
        self.v_C = 0.0  # 电容电压 (V)
        
    def update_filter(self, v_in: float, i_load: float, dt: float):
        """
        更新LC滤波器状态
        
        微分方程:
            L * di_L/dt = v_in - v_C - R*i_L
            C * dv_C/dt = i_L - i_load
        
        Args:
            v_in: 输入电压 (开关输出)
            i_load: 负载电流
            dt: 时间步长
        """
        L = self.params.L_filter
        C = self.params.C_filter
        R = self.params.R_filter
        
        # 电感电流变化率
        di_L = (v_in - self.v_C - R * self.i_L) / L
        
        # 电容电压变化率
        dv_C = (self.i_L - i_load) / C
        
        # 更新状态 (欧拉法)
        self.i_L += di_L * dt
        self.v_C += dv_C * dt
        
    def simulate_with_filter(self, duration: float, load_resistance: float = 10.0) -> Dict:
        """
        仿真逆变器+滤波器系统
        
        Args:
            duration: 仿真时长 (s)
            load_resistance: 负载电阻 (Ω)
            
        Returns:
            仿真结果字典
        """
        dt = self.modulator.T_sw / 100
        time = np.arange(0, duration, dt)
        N = len(time)
        
        # 初始化数组
        v_ref = np.zeros(N)
        v_pwm = np.zeros(N)
        i_L = np.zeros(N)
        v_out = np.zeros(N)
        
        # 重置滤波器状态
        self.i_L = 0.0
        self.v_C = 0.0
        
        # 逐点仿真
        for i, t in enumerate(time):
            # 生成参考电压
            v_ref[i] = self.modulator.generate_reference(t)
            
            # PWM调制
            if hasattr(self.modulator, 'modulate'):
                _, info = self.modulator.modulate(v_ref[i], t)
                v_pwm[i] = info['output_voltage']
            
            # 计算负载电流
            i_load = self.v_C / load_resistance
            
            # 更新滤波器
            self.update_filter(v_pwm[i], i_load, dt)
            
            # 记录状态
            i_L[i] = self.i_L
            v_out[i] = self.v_C
        
        return {
            'time': time,
            'v_ref': v_ref,
            'v_pwm': v_pwm,
            'i_filter': i_L,
            'v_output': v_out,
            'load_resistance': load_resistance
        }


# ==================== 电流控制器 ====================

class CurrentController:
    """电流控制器基类"""
    
    def __init__(self, name: str = "CurrentController"):
        self.name = name
        self.i_ref = 0.0
        self.i_measured = 0.0
        self.v_output = 0.0
        
        # 历史记录
        self.history = {
            'time': [],
            'i_ref': [],
            'i_measured': [],
            'error': [],
            'v_output': []
        }
    
    def reset(self):
        """重置控制器状态"""
        self.i_ref = 0.0
        self.i_measured = 0.0
        self.v_output = 0.0
        self.history = {
            'time': [],
            'i_ref': [],
            'i_measured': [],
            'error': [],
            'v_output': []
        }
    
    def update(self, i_ref: float, i_measured: float, dt: float, **kwargs) -> float:
        """
        更新控制器 (抽象方法)
        
        Args:
            i_ref: 参考电流 (A)
            i_measured: 测量电流 (A)
            dt: 时间步长 (s)
            **kwargs: 其他参数
            
        Returns:
            控制输出电压 (V)
        """
        raise NotImplementedError("子类必须实现update方法")


class PIController(CurrentController):
    """
    PI (比例-积分) 电流控制器
    
    控制律:
        u(t) = Kp * e(t) + Ki * ∫e(t)dt
    
    其中:
        e(t) = i_ref - i_measured
    
    特点:
        - 简单实用
        - 稳态误差为0
        - 适用于直流或dq坐标系
    """
    
    def __init__(self, Kp: float, Ki: float, v_limit: float = None, name: str = "PI"):
        """
        初始化PI控制器
        
        Args:
            Kp: 比例增益
            Ki: 积分增益
            v_limit: 输出电压限幅 (V), 默认无限制
            name: 控制器名称
        """
        super().__init__(name)
        self.Kp = Kp
        self.Ki = Ki
        self.v_limit = v_limit
        
        # 积分器状态
        self.integral = 0.0
        self.integral_limit = v_limit if v_limit else 1000.0
    
    def reset(self):
        """重置控制器"""
        super().reset()
        self.integral = 0.0
    
    def update(self, i_ref: float, i_measured: float, dt: float, **kwargs) -> float:
        """
        更新PI控制器
        
        Args:
            i_ref: 参考电流 (A)
            i_measured: 测量电流 (A)
            dt: 时间步长 (s)
            
        Returns:
            控制输出电压 (V)
        """
        # 计算误差
        error = i_ref - i_measured
        
        # 比例项
        p_term = self.Kp * error
        
        # 积分项 (带抗饱和)
        self.integral += error * dt
        
        # 积分限幅 (抗积分饱和)
        if self.integral_limit:
            self.integral = np.clip(self.integral, 
                                   -self.integral_limit / self.Ki,
                                   self.integral_limit / self.Ki)
        
        i_term = self.Ki * self.integral
        
        # 控制输出
        v_output = p_term + i_term
        
        # 输出限幅
        if self.v_limit:
            v_output = np.clip(v_output, -self.v_limit, self.v_limit)
        
        # 保存状态
        self.i_ref = i_ref
        self.i_measured = i_measured
        self.v_output = v_output
        
        return v_output
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        error = self.i_ref - self.i_measured
        return {
            'name': self.name,
            'Kp': self.Kp,
            'Ki': self.Ki,
            'error': error,
            'integral': self.integral,
            'p_term': self.Kp * error,
            'i_term': self.Ki * self.integral,
            'v_output': self.v_output
        }


class PRController(CurrentController):
    """
    PR (比例-谐振) 电流控制器
    
    控制律:
        u(t) = Kp * e(t) + Kr * [s / (s² + ω₀²)] * e(t)
    
    离散化 (Tustin变换):
        H_r(z) = Kr * [(2/Ts) * (z-1) / ((2/Ts)² + ω₀²) * (z+1)]
    
    特点:
        - 对特定频率(ω₀)有无穷大增益
        - 可消除该频率的稳态误差
        - 适用于交流系统(abc坐标系)
    """
    
    def __init__(self, Kp: float, Kr: float, omega_0: float, 
                 Ts: float, v_limit: float = None, name: str = "PR"):
        """
        初始化PR控制器
        
        Args:
            Kp: 比例增益
            Kr: 谐振增益
            omega_0: 谐振角频率 (rad/s), 通常为基波频率
            Ts: 采样周期 (s)
            v_limit: 输出电压限幅 (V)
            name: 控制器名称
        """
        super().__init__(name)
        self.Kp = Kp
        self.Kr = Kr
        self.omega_0 = omega_0
        self.Ts = Ts
        self.v_limit = v_limit
        
        # 谐振环节离散化系数 (Tustin变换)
        # H_r(z) = Kr * b0 + b1*z^-1 + b2*z^-2 / (1 + a1*z^-1 + a2*z^-2)
        omega_sq = omega_0 ** 2
        Ts_sq = Ts ** 2
        
        # 分子系数
        self.b0 = Kr * 2 / Ts
        self.b1 = 0.0
        self.b2 = -Kr * 2 / Ts
        
        # 分母系数
        denom = 4 / Ts_sq + omega_sq
        self.a1 = (2 * omega_sq - 8 / Ts_sq) / denom
        self.a2 = (4 / Ts_sq - omega_sq) / denom
        
        # 状态变量 (谐振环节的过去值)
        self.e_k1 = 0.0  # e(k-1)
        self.e_k2 = 0.0  # e(k-2)
        self.u_r_k1 = 0.0  # u_r(k-1)
        self.u_r_k2 = 0.0  # u_r(k-2)
    
    def reset(self):
        """重置控制器"""
        super().reset()
        self.e_k1 = 0.0
        self.e_k2 = 0.0
        self.u_r_k1 = 0.0
        self.u_r_k2 = 0.0
    
    def update(self, i_ref: float, i_measured: float, dt: float, **kwargs) -> float:
        """
        更新PR控制器
        
        Args:
            i_ref: 参考电流 (A)
            i_measured: 测量电流 (A)
            dt: 时间步长 (s) - 未使用,使用初始化时的Ts
            
        Returns:
            控制输出电压 (V)
        """
        # 计算误差
        error = i_ref - i_measured
        
        # 比例项
        p_term = self.Kp * error
        
        # 谐振项 (IIR滤波器)
        u_r = (self.b0 * error + 
               self.b1 * self.e_k1 + 
               self.b2 * self.e_k2 - 
               self.a1 * self.u_r_k1 - 
               self.a2 * self.u_r_k2)
        
        # 控制输出
        v_output = p_term + u_r
        
        # 输出限幅
        if self.v_limit:
            v_output = np.clip(v_output, -self.v_limit, self.v_limit)
        
        # 更新状态
        self.e_k2 = self.e_k1
        self.e_k1 = error
        self.u_r_k2 = self.u_r_k1
        self.u_r_k1 = u_r
        
        # 保存
        self.i_ref = i_ref
        self.i_measured = i_measured
        self.v_output = v_output
        
        return v_output
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        error = self.i_ref - self.i_measured
        return {
            'name': self.name,
            'Kp': self.Kp,
            'Kr': self.Kr,
            'omega_0': self.omega_0,
            'error': error,
            'p_term': self.Kp * error,
            'r_term': self.u_r_k1,
            'v_output': self.v_output
        }


class DQCurrentController:
    """
    dq坐标系下的电流控制器
    
    原理:
        在同步旋转坐标系(dq)下,交流量变为直流量
        使用两个PI控制器分别控制d轴和q轴电流
        
    坐标变换:
        Park变换: abc → dq
        逆Park变换: dq → abc
        
    解耦控制:
        考虑d轴和q轴的耦合项
        v_d = v_d_PI - ω*L*i_q (前馈解耦)
        v_q = v_q_PI + ω*L*i_d (前馈解耦)
    """
    
    def __init__(self, Kp: float, Ki: float, L: float, omega: float, 
                 v_limit: float = None, name: str = "DQ_PI"):
        """
        初始化dq电流控制器
        
        Args:
            Kp: 比例增益
            Ki: 积分增益
            L: 电感值 (H)
            omega: 电网角频率 (rad/s)
            v_limit: 输出电压限幅 (V)
            name: 控制器名称
        """
        self.name = name
        self.L = L
        self.omega = omega
        self.v_limit = v_limit
        
        # 创建d轴和q轴PI控制器
        self.pi_d = PIController(Kp, Ki, v_limit, name="PI_d")
        self.pi_q = PIController(Kp, Ki, v_limit, name="PI_q")
        
        # 状态变量
        self.theta = 0.0  # Park变换角度
        
    def park_transform(self, i_a: float, i_b: float, i_c: float, theta: float) -> Tuple[float, float]:
        """
        Park变换: abc → dq
        
        Args:
            i_a, i_b, i_c: 三相电流
            theta: 变换角度 (rad)
            
        Returns:
            (i_d, i_q)
        """
        # 先进行Clarke变换
        i_alpha = (2*i_a - i_b - i_c) / 3
        i_beta = (i_b - i_c) / np.sqrt(3)
        
        # Park变换
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        i_d = i_alpha * cos_theta + i_beta * sin_theta
        i_q = -i_alpha * sin_theta + i_beta * cos_theta
        
        return i_d, i_q
    
    def inverse_park_transform(self, v_d: float, v_q: float, theta: float) -> Tuple[float, float, float]:
        """
        逆Park变换: dq → abc
        
        Args:
            v_d, v_q: dq坐标系电压
            theta: 变换角度 (rad)
            
        Returns:
            (v_a, v_b, v_c)
        """
        # 逆Park变换到αβ
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        v_alpha = v_d * cos_theta - v_q * sin_theta
        v_beta = v_d * sin_theta + v_q * cos_theta
        
        # 逆Clarke变换到abc
        v_a = v_alpha
        v_b = -0.5 * v_alpha + np.sqrt(3)/2 * v_beta
        v_c = -0.5 * v_alpha - np.sqrt(3)/2 * v_beta
        
        return v_a, v_b, v_c
    
    def update(self, i_d_ref: float, i_q_ref: float, 
               i_a: float, i_b: float, i_c: float, 
               theta: float, dt: float, enable_decoupling: bool = True) -> Tuple[float, float, float]:
        """
        更新dq电流控制器
        
        Args:
            i_d_ref, i_q_ref: dq参考电流
            i_a, i_b, i_c: 测量的三相电流
            theta: Park变换角度 (rad)
            dt: 时间步长 (s)
            enable_decoupling: 是否启用解耦控制
            
        Returns:
            (v_a, v_b, v_c) 三相输出电压
        """
        # Park变换: abc → dq
        i_d, i_q = self.park_transform(i_a, i_b, i_c, theta)
        
        # PI控制
        v_d_pi = self.pi_d.update(i_d_ref, i_d, dt)
        v_q_pi = self.pi_q.update(i_q_ref, i_q, dt)
        
        # 解耦控制 (前馈补偿)
        if enable_decoupling:
            v_d = v_d_pi - self.omega * self.L * i_q
            v_q = v_q_pi + self.omega * self.L * i_d
        else:
            v_d = v_d_pi
            v_q = v_q_pi
        
        # 输出限幅
        if self.v_limit:
            v_mag = np.sqrt(v_d**2 + v_q**2)
            if v_mag > self.v_limit:
                scale = self.v_limit / v_mag
                v_d *= scale
                v_q *= scale
        
        # 逆Park变换: dq → abc
        v_a, v_b, v_c = self.inverse_park_transform(v_d, v_q, theta)
        
        self.theta = theta
        
        return v_a, v_b, v_c
    
    def reset(self):
        """重置控制器"""
        self.pi_d.reset()
        self.pi_q.reset()
        self.theta = 0.0
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        return {
            'name': self.name,
            'theta': self.theta,
            'pi_d': self.pi_d.get_status(),
            'pi_q': self.pi_q.get_status()
        }


# ==================== 电压控制器 ====================

class VoltageController:
    """电压控制器基类"""
    
    def __init__(self, name: str = "VoltageController"):
        self.name = name
        self.v_ref = 0.0
        self.v_measured = 0.0
        self.output = 0.0
    
    def reset(self):
        """重置控制器"""
        self.v_ref = 0.0
        self.v_measured = 0.0
        self.output = 0.0
    
    def update(self, v_ref: float, v_measured: float, dt: float, **kwargs) -> float:
        """更新控制器 (抽象方法)"""
        raise NotImplementedError("子类必须实现update方法")


class DCVoltageController(VoltageController):
    """
    直流母线电压控制器
    
    用途:
        控制直流母线电压稳定
        输出为有功功率参考
        
    控制结构:
        PI控制器 + 前馈补偿
        
    输出:
        i_ref = PI(V_ref - V_dc) + I_ff
    """
    
    def __init__(self, Kp: float, Ki: float, C: float, 
                 v_nominal: float = 400.0, i_limit: float = None, name: str = "DC_Voltage"):
        """
        初始化直流电压控制器
        
        Args:
            Kp: 比例增益
            Ki: 积分增益
            C: 直流侧电容 (F)
            v_nominal: 额定直流电压 (V)
            i_limit: 输出电流限幅 (A)
            name: 控制器名称
        """
        super().__init__(name)
        self.pi = PIController(Kp, Ki, v_limit=i_limit)
        self.C = C
        self.v_nominal = v_nominal
        self.i_limit = i_limit
    
    def update(self, v_ref: float, v_measured: float, dt: float, 
               p_load: float = 0.0, enable_feedforward: bool = True) -> float:
        """
        更新直流电压控制器
        
        Args:
            v_ref: 参考电压 (V)
            v_measured: 测量电压 (V)
            dt: 时间步长 (s)
            p_load: 负载功率 (W), 用于前馈
            enable_feedforward: 是否启用前馈
            
        Returns:
            参考电流 (A)
        """
        # PI控制
        i_ref_pi = self.pi.update(v_ref, v_measured, dt)
        
        # 前馈补偿 (根据功率平衡)
        if enable_feedforward and v_measured > 0:
            i_ff = p_load / v_measured
        else:
            i_ff = 0.0
        
        # 总参考电流
        i_ref = i_ref_pi + i_ff
        
        # 限幅
        if self.i_limit:
            i_ref = np.clip(i_ref, -self.i_limit, self.i_limit)
        
        self.v_ref = v_ref
        self.v_measured = v_measured
        self.output = i_ref
        
        return i_ref
    
    def reset(self):
        """重置控制器"""
        super().reset()
        self.pi.reset()
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        return {
            'name': self.name,
            'v_ref': self.v_ref,
            'v_measured': self.v_measured,
            'error': self.v_ref - self.v_measured,
            'output': self.output,
            'pi_status': self.pi.get_status()
        }


class ACVoltageController(VoltageController):
    """
    交流电压控制器 (单相)
    
    用途:
        独立运行模式下控制交流输出电压
        
    控制结构:
        双环控制: 电压外环(PI) + 电流内环(PI/PR)
        
    特点:
        - 电压环带宽较低 (几百Hz)
        - 电流环带宽较高 (几kHz)
        - 解耦控制提升性能
    """
    
    def __init__(self, Kp_v: float, Ki_v: float, 
                 Kp_i: float, Ki_i: float,
                 L: float, C: float, omega: float = None,
                 v_limit: float = None, i_limit: float = None,
                 name: str = "AC_Voltage"):
        """
        初始化交流电压控制器
        
        Args:
            Kp_v, Ki_v: 电压环PI参数
            Kp_i, Ki_i: 电流环PI参数
            L: 滤波电感 (H)
            C: 滤波电容 (F)
            omega: 基波角频率 (rad/s), 用于前馈
            v_limit: 电压环输出限幅 (A)
            i_limit: 电流环输出限幅 (V)
            name: 控制器名称
        """
        super().__init__(name)
        self.pi_voltage = PIController(Kp_v, Ki_v, v_limit=v_limit)
        self.pi_current = PIController(Kp_i, Ki_i, v_limit=i_limit)
        self.L = L
        self.C = C
        self.omega = omega if omega else 2 * np.pi * 50.0
        
        # 状态变量
        self.i_ref = 0.0
        self.i_measured = 0.0
    
    def update(self, v_ref: float, v_measured: float, i_measured: float,
               dt: float, i_load: float = 0.0, enable_decoupling: bool = True) -> float:
        """
        更新交流电压控制器
        
        Args:
            v_ref: 参考电压 (V)
            v_measured: 测量电压 (V)
            i_measured: 测量电流 (A)
            dt: 时间步长 (s)
            i_load: 负载电流 (A), 用于前馈
            enable_decoupling: 是否启用解耦控制
            
        Returns:
            控制输出电压 (V)
        """
        # 电压外环: 输出电流参考
        i_ref = self.pi_voltage.update(v_ref, v_measured, dt)
        
        # 负载电流前馈
        if enable_decoupling:
            i_ref += i_load
        
        # 电流内环: 输出电压参考
        v_out = self.pi_current.update(i_ref, i_measured, dt)
        
        # 电容电压前馈 (提高动态)
        if enable_decoupling:
            v_out += v_measured
        
        # 保存状态
        self.v_ref = v_ref
        self.v_measured = v_measured
        self.i_ref = i_ref
        self.i_measured = i_measured
        self.output = v_out
        
        return v_out
    
    def reset(self):
        """重置控制器"""
        super().reset()
        self.pi_voltage.reset()
        self.pi_current.reset()
        self.i_ref = 0.0
        self.i_measured = 0.0
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        return {
            'name': self.name,
            'v_ref': self.v_ref,
            'v_measured': self.v_measured,
            'i_ref': self.i_ref,
            'i_measured': self.i_measured,
            'v_error': self.v_ref - self.v_measured,
            'i_error': self.i_ref - self.i_measured,
            'output': self.output,
            'voltage_loop': self.pi_voltage.get_status(),
            'current_loop': self.pi_current.get_status()
        }


class DualLoopVoltageController:
    """
    双环电压控制器 (三相dq坐标系)
    
    结构:
        - 外环: 直流电压控制 → d轴电流参考
        - 内环: dq电流控制 → dq电压参考
        
    应用:
        三相并网/独立系统的电压控制
        
    特点:
        - 电压环调节直流母线
        - 电流环快速跟踪
        - dq解耦提升性能
    """
    
    def __init__(self, Kp_v: float, Ki_v: float, C_dc: float,
                 Kp_i: float, Ki_i: float, L: float, omega: float,
                 v_dc_nominal: float = 400.0, 
                 i_limit: float = None, v_limit: float = None,
                 name: str = "DualLoop"):
        """
        初始化双环控制器
        
        Args:
            Kp_v, Ki_v: 电压环PI参数
            C_dc: 直流侧电容 (F)
            Kp_i, Ki_i: 电流环PI参数
            L: 滤波电感 (H)
            omega: 电网角频率 (rad/s)
            v_dc_nominal: 额定直流电压 (V)
            i_limit: 电流环限幅 (A)
            v_limit: 电流控制器输出限幅 (V)
            name: 控制器名称
        """
        self.name = name
        
        # 电压外环 (直流)
        self.voltage_ctrl = DCVoltageController(Kp_v, Ki_v, C_dc, 
                                                 v_dc_nominal, i_limit)
        
        # 电流内环 (dq)
        self.current_ctrl = DQCurrentController(Kp_i, Ki_i, L, omega, v_limit)
        
        self.v_dc_nominal = v_dc_nominal
    
    def update(self, v_dc_ref: float, v_dc_measured: float,
               i_a: float, i_b: float, i_c: float,
               theta: float, dt: float,
               p_load: float = 0.0, i_q_ref: float = 0.0,
               enable_feedforward: bool = True,
               enable_decoupling: bool = True) -> Tuple[float, float, float]:
        """
        更新双环控制器
        
        Args:
            v_dc_ref: 直流电压参考 (V)
            v_dc_measured: 测量直流电压 (V)
            i_a, i_b, i_c: 三相电流 (A)
            theta: Park变换角度 (rad)
            dt: 时间步长 (s)
            p_load: 负载功率 (W), 用于前馈
            i_q_ref: q轴电流参考 (A), 通常为0
            enable_feedforward: 启用电压环前馈
            enable_decoupling: 启用电流环解耦
            
        Returns:
            (v_a, v_b, v_c) 三相输出电压
        """
        # 电压外环: V_dc → i_d_ref
        i_d_ref = self.voltage_ctrl.update(
            v_dc_ref, v_dc_measured, dt, p_load, enable_feedforward
        )
        
        # 电流内环: (i_d_ref, i_q_ref) + (i_a, i_b, i_c) → (v_a, v_b, v_c)
        v_a, v_b, v_c = self.current_ctrl.update(
            i_d_ref, i_q_ref, i_a, i_b, i_c, theta, dt, enable_decoupling
        )
        
        return v_a, v_b, v_c
    
    def reset(self):
        """重置控制器"""
        self.voltage_ctrl.reset()
        self.current_ctrl.reset()
    
    def get_status(self) -> Dict:
        """获取控制器状态"""
        return {
            'name': self.name,
            'voltage_loop': self.voltage_ctrl.get_status(),
            'current_loop': self.current_ctrl.get_status()
        }


# ==================== 锁相环(PLL) ====================

class PLL:
    """锁相环基类"""
    
    def __init__(self, name: str = "PLL"):
        self.name = name
        self.theta = 0.0  # 相位角
        self.omega = 2 * np.pi * 50.0  # 角频率
        self.frequency = 50.0  # 频率
    
    def reset(self):
        """重置PLL"""
        self.theta = 0.0
        self.omega = 2 * np.pi * 50.0
        self.frequency = 50.0
    
    def update(self, *args, **kwargs) -> Tuple[float, float, float]:
        """更新PLL (抽象方法)
        
        Returns:
            (theta, omega, frequency)
        """
        raise NotImplementedError("子类必须实现update方法")


class SRFPLL(PLL):
    """
    同步参考坐标系锁相环 (Synchronous Reference Frame PLL)
    
    原理:
        将三相电压变换到dq坐标系，在同步坐标系下：
        - q轴分量反映相位误差
        - 通过PI控制器调节频率
        - 积分得到相位角
        
    优点:
        - 结构简单
        - 响应快速
        - 易于实现
        
    适用:
        三相平衡系统
    """
    
    def __init__(self, Kp: float = 50.0, Ki: float = 1000.0, 
                 omega_nominal: float = None, name: str = "SRF-PLL"):
        """
        初始化SRF-PLL
        
        Args:
            Kp: PI控制器比例增益
            Ki: PI控制器积分增益
            omega_nominal: 额定角频率 (rad/s)
            name: PLL名称
        """
        super().__init__(name)
        
        if omega_nominal is None:
            omega_nominal = 2 * np.pi * 50.0
        
        self.omega_nominal = omega_nominal
        self.frequency_nominal = omega_nominal / (2 * np.pi)
        
        # PI控制器
        self.Kp = Kp
        self.Ki = Ki
        self.integral = 0.0
        
        # 初始化
        self.omega = omega_nominal
        self.frequency = self.frequency_nominal
        self.theta = 0.0
        
        # 状态记录
        self.v_d = 0.0
        self.v_q = 0.0
    
    def clarke_transform(self, va: float, vb: float, vc: float) -> Tuple[float, float]:
        """Clarke变换: abc → αβ"""
        v_alpha = va
        v_beta = (va + 2 * vb) / np.sqrt(3)
        return v_alpha, v_beta
    
    def park_transform(self, v_alpha: float, v_beta: float, theta: float) -> Tuple[float, float]:
        """Park变换: αβ → dq"""
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        v_d = v_alpha * cos_theta + v_beta * sin_theta
        v_q = -v_alpha * sin_theta + v_beta * cos_theta
        
        return v_d, v_q
    
    def update(self, va: float, vb: float, vc: float, dt: float) -> Tuple[float, float, float]:
        """
        更新SRF-PLL
        
        Args:
            va, vb, vc: 三相电压 (V)
            dt: 时间步长 (s)
            
        Returns:
            (theta, omega, frequency): 相位角(rad), 角频率(rad/s), 频率(Hz)
        """
        # Clarke变换
        v_alpha, v_beta = self.clarke_transform(va, vb, vc)
        
        # Park变换
        v_d, v_q = self.park_transform(v_alpha, v_beta, self.theta)
        
        # 保存状态
        self.v_d = v_d
        self.v_q = v_q
        
        # PI控制器 (v_q为误差信号)
        error = v_q
        self.integral += error * dt
        
        # 频率调节
        omega_adj = self.Kp * error + self.Ki * self.integral
        self.omega = self.omega_nominal + omega_adj
        
        # 频率限幅 (±5Hz)
        omega_min = 2 * np.pi * (self.frequency_nominal - 5)
        omega_max = 2 * np.pi * (self.frequency_nominal + 5)
        self.omega = np.clip(self.omega, omega_min, omega_max)
        
        # 相位积分
        self.theta += self.omega * dt
        
        # 相位归一化到 [0, 2π)
        self.theta = np.mod(self.theta, 2 * np.pi)
        
        # 计算频率
        self.frequency = self.omega / (2 * np.pi)
        
        return self.theta, self.omega, self.frequency
    
    def reset(self):
        """重置PLL"""
        super().reset()
        self.omega = self.omega_nominal
        self.frequency = self.frequency_nominal
        self.theta = 0.0
        self.integral = 0.0
        self.v_d = 0.0
        self.v_q = 0.0
    
    def get_status(self) -> Dict:
        """获取PLL状态"""
        return {
            'name': self.name,
            'theta': self.theta,
            'theta_deg': np.degrees(self.theta),
            'omega': self.omega,
            'frequency': self.frequency,
            'v_d': self.v_d,
            'v_q': self.v_q,
            'error': self.v_q,
            'integral': self.integral
        }


class SinglePhasePLL(PLL):
    """
    单相锁相环
    
    原理:
        通过构造正交信号，将单相系统映射到两相系统
        使用类似SRF-PLL的方法进行锁相
        
    方法:
        - 延迟法: 使用T/4延迟构造正交信号
        - 滤波法: 使用带通滤波器提取正交分量
        
    本实现: 使用简化的90度相移法
    """
    
    def __init__(self, Kp: float = 50.0, Ki: float = 1000.0,
                 omega_nominal: float = None, name: str = "Single-Phase-PLL"):
        """
        初始化单相PLL
        
        Args:
            Kp: PI控制器比例增益
            Ki: PI控制器积分增益
            omega_nominal: 额定角频率 (rad/s)
            name: PLL名称
        """
        super().__init__(name)
        
        if omega_nominal is None:
            omega_nominal = 2 * np.pi * 50.0
        
        self.omega_nominal = omega_nominal
        self.frequency_nominal = omega_nominal / (2 * np.pi)
        
        # PI控制器
        self.Kp = Kp
        self.Ki = Ki
        self.integral = 0.0
        
        # 初始化
        self.omega = omega_nominal
        self.frequency = self.frequency_nominal
        self.theta = 0.0
        
        # 正交信号生成 (简化: 使用相位偏移)
        self.v_alpha_history = []
        self.history_size = 10
    
    def generate_orthogonal(self, v: float) -> Tuple[float, float]:
        """
        生成正交信号 (α, β)
        
        简化方法: 使用当前估计相位生成正交信号
        """
        # v_alpha = v (直接使用输入)
        # v_beta = v在90度相移后的估计 (使用PLL输出)
        
        v_alpha = v
        v_beta = v * np.sin(self.theta + np.pi / 2) / np.sin(self.theta) if np.abs(np.sin(self.theta)) > 0.01 else 0.0
        
        return v_alpha, v_beta
    
    def update(self, v: float, dt: float) -> Tuple[float, float, float]:
        """
        更新单相PLL
        
        Args:
            v: 单相电压 (V)
            dt: 时间步长 (s)
            
        Returns:
            (theta, omega, frequency): 相位角(rad), 角频率(rad/s), 频率(Hz)
        """
        # 生成正交信号
        v_alpha, v_beta = self.generate_orthogonal(v)
        
        # Park变换
        cos_theta = np.cos(self.theta)
        sin_theta = np.sin(self.theta)
        
        v_d = v_alpha * cos_theta + v_beta * sin_theta
        v_q = -v_alpha * sin_theta + v_beta * cos_theta
        
        # PI控制器 (v_q为误差信号)
        error = v_q
        self.integral += error * dt
        
        # 频率调节
        omega_adj = self.Kp * error + self.Ki * self.integral
        self.omega = self.omega_nominal + omega_adj
        
        # 频率限幅
        omega_min = 2 * np.pi * (self.frequency_nominal - 5)
        omega_max = 2 * np.pi * (self.frequency_nominal + 5)
        self.omega = np.clip(self.omega, omega_min, omega_max)
        
        # 相位积分
        self.theta += self.omega * dt
        
        # 相位归一化
        self.theta = np.mod(self.theta, 2 * np.pi)
        
        # 计算频率
        self.frequency = self.omega / (2 * np.pi)
        
        return self.theta, self.omega, self.frequency
    
    def reset(self):
        """重置PLL"""
        super().reset()
        self.omega = self.omega_nominal
        self.frequency = self.frequency_nominal
        self.theta = 0.0
        self.integral = 0.0
        self.v_alpha_history = []
    
    def get_status(self) -> Dict:
        """获取PLL状态"""
        return {
            'name': self.name,
            'theta': self.theta,
            'theta_deg': np.degrees(self.theta),
            'omega': self.omega,
            'frequency': self.frequency,
            'integral': self.integral
        }
