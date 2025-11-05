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
