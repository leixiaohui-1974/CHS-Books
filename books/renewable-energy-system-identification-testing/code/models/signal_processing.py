"""
信号处理模块

包含:
1. FFT频谱分析
2. 滤波器设计
3. 小波变换
4. 特征提取
5. THD计算

作者: CHS Books
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, Tuple


class FFTAnalyzer:
    """
    FFT频谱分析器
    
    用于谐波分析、故障诊断
    """
    
    def __init__(self, fs: float, name: str = "FFT"):
        """
        初始化FFT分析器
        
        Args:
            fs: 采样频率 (Hz)
        """
        self.name = name
        self.fs = fs
    
    def analyze(self, signal_data: np.ndarray) -> Dict:
        """
        频谱分析
        
        Args:
            signal_data: 时域信号
            
        Returns:
            频谱分析结果
        """
        n = len(signal_data)
        
        # FFT
        yf = fft(signal_data)
        xf = fftfreq(n, 1 / self.fs)[:n//2]
        
        # 幅值谱
        magnitude = 2.0/n * np.abs(yf[:n//2])
        
        # 相位谱
        phase = np.angle(yf[:n//2])
        
        return {
            'frequencies': xf,
            'magnitude': magnitude,
            'phase': phase,
        }
    
    def compute_thd(
        self,
        signal_data: np.ndarray,
        fundamental_freq: float
    ) -> float:
        """
        计算总谐波畸变率 (THD)
        
        Args:
            signal_data: 信号数据
            fundamental_freq: 基波频率
            
        Returns:
            THD (%)
        """
        result = self.analyze(signal_data)
        freqs = result['frequencies']
        magnitude = result['magnitude']
        
        # 找到基波和谐波
        fundamental_idx = np.argmin(np.abs(freqs - fundamental_freq))
        fundamental_mag = magnitude[fundamental_idx]
        
        # 谐波（2-40次）
        harmonic_power = 0
        for n in range(2, 41):
            harmonic_freq = n * fundamental_freq
            harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
            if harmonic_idx < len(magnitude):
                harmonic_power += magnitude[harmonic_idx]**2
        
        # THD
        thd = np.sqrt(harmonic_power) / fundamental_mag * 100
        
        return thd


class FilterDesign:
    """
    数字滤波器设计
    """
    
    @staticmethod
    def lowpass(cutoff: float, fs: float, order: int = 5) -> Tuple:
        """
        低通滤波器
        
        Args:
            cutoff: 截止频率 (Hz)
            fs: 采样频率 (Hz)
            order: 阶数
            
        Returns:
            滤波器系数 (b, a)
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    @staticmethod
    def highpass(cutoff: float, fs: float, order: int = 5) -> Tuple:
        """高通滤波器"""
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        return b, a
    
    @staticmethod
    def bandpass(
        low: float,
        high: float,
        fs: float,
        order: int = 5
    ) -> Tuple:
        """带通滤波器"""
        nyq = 0.5 * fs
        low_normal = low / nyq
        high_normal = high / nyq
        b, a = signal.butter(order, [low_normal, high_normal], btype='band')
        return b, a
    
    @staticmethod
    def apply_filter(
        data: np.ndarray,
        b: np.ndarray,
        a: np.ndarray
    ) -> np.ndarray:
        """应用滤波器"""
        return signal.filtfilt(b, a, data)


class FeatureExtraction:
    """
    时域/频域特征提取
    
    用于故障诊断
    """
    
    @staticmethod
    def time_domain_features(signal_data: np.ndarray) -> Dict:
        """
        时域特征
        
        Args:
            signal_data: 信号数据
            
        Returns:
            特征字典
        """
        features = {
            'mean': np.mean(signal_data),
            'std': np.std(signal_data),
            'rms': np.sqrt(np.mean(signal_data**2)),
            'peak': np.max(np.abs(signal_data)),
            'peak_to_peak': np.ptp(signal_data),
            'crest_factor': np.max(np.abs(signal_data)) / np.sqrt(np.mean(signal_data**2)),
            'kurtosis': np.mean((signal_data - np.mean(signal_data))**4) / np.std(signal_data)**4,
            'skewness': np.mean((signal_data - np.mean(signal_data))**3) / np.std(signal_data)**3,
        }
        return features
    
    @staticmethod
    def frequency_domain_features(
        signal_data: np.ndarray,
        fs: float
    ) -> Dict:
        """
        频域特征
        
        Args:
            signal_data: 信号数据
            fs: 采样频率
            
        Returns:
            特征字典
        """
        # FFT
        n = len(signal_data)
        yf = fft(signal_data)
        xf = fftfreq(n, 1/fs)[:n//2]
        magnitude = 2.0/n * np.abs(yf[:n//2])
        
        # 功率谱密度
        psd = magnitude**2
        
        features = {
            'spectral_centroid': np.sum(xf * psd) / np.sum(psd),
            'spectral_spread': np.sqrt(np.sum(((xf - features.get('spectral_centroid', 0))**2) * psd) / np.sum(psd)),
            'spectral_energy': np.sum(psd),
            'dominant_frequency': xf[np.argmax(psd)],
        }
        
        return features


class VibrationAnalyzer:
    """
    振动信号分析器
    
    用于旋转机械故障诊断
    """
    
    def __init__(self, fs: float, name: str = "VibrationAnalyzer"):
        """
        初始化振动分析器
        
        Args:
            fs: 采样频率
        """
        self.name = name
        self.fs = fs
        self.fft_analyzer = FFTAnalyzer(fs)
    
    def bearing_fault_detection(
        self,
        vibration_signal: np.ndarray,
        shaft_speed: float,  # Hz
        bearing_params: Dict
    ) -> Dict:
        """
        轴承故障检测
        
        Args:
            vibration_signal: 振动信号
            shaft_speed: 轴转速 (Hz)
            bearing_params: 轴承参数
                {'BPFO': 外圈故障频率系数,
                 'BPFI': 内圈故障频率系数,
                 'BSF': 滚动体故障频率系数}
                 
        Returns:
            故障诊断结果
        """
        # 特征频率
        BPFO = bearing_params.get('BPFO', 3.5) * shaft_speed
        BPFI = bearing_params.get('BPFI', 4.5) * shaft_speed
        BSF = bearing_params.get('BSF', 2.0) * shaft_speed
        
        # 频谱分析
        spectrum = self.fft_analyzer.analyze(vibration_signal)
        freqs = spectrum['frequencies']
        magnitude = spectrum['magnitude']
        
        # 检查特征频率附近的幅值
        def get_magnitude_at_freq(target_freq, bandwidth=1.0):
            idx = np.argmin(np.abs(freqs - target_freq))
            return magnitude[idx]
        
        outer_race_mag = get_magnitude_at_freq(BPFO)
        inner_race_mag = get_magnitude_at_freq(BPFI)
        ball_mag = get_magnitude_at_freq(BSF)
        
        # 阈值判断
        threshold = np.mean(magnitude) + 3 * np.std(magnitude)
        
        faults = []
        if outer_race_mag > threshold:
            faults.append('外圈故障')
        if inner_race_mag > threshold:
            faults.append('内圈故障')
        if ball_mag > threshold:
            faults.append('滚动体故障')
        
        return {
            'faults': faults if faults else ['正常'],
            'BPFO_magnitude': outer_race_mag,
            'BPFI_magnitude': inner_race_mag,
            'BSF_magnitude': ball_mag,
            'threshold': threshold,
        }


class PowerQualityAnalyzer:
    """
    电能质量分析器
    """
    
    def __init__(self, fs: float, name: str = "PowerQuality"):
        """
        初始化电能质量分析器
        
        Args:
            fs: 采样频率
        """
        self.name = name
        self.fs = fs
        self.fft_analyzer = FFTAnalyzer(fs)
    
    def analyze_voltage_sag(
        self,
        voltage_signal: np.ndarray,
        nominal_voltage: float
    ) -> Dict:
        """
        电压暂降分析
        
        Args:
            voltage_signal: 电压信号
            nominal_voltage: 额定电压
            
        Returns:
            分析结果
        """
        # RMS计算（滑动窗口）
        window_size = int(self.fs / 50)  # 1个周期
        rms_values = []
        
        for i in range(0, len(voltage_signal) - window_size, window_size//2):
            window = voltage_signal[i:i+window_size]
            rms = np.sqrt(np.mean(window**2))
            rms_values.append(rms)
        
        rms_values = np.array(rms_values)
        
        # 暂降检测（低于0.9pu）
        sag_threshold = 0.9 * nominal_voltage
        sag_indices = np.where(rms_values < sag_threshold)[0]
        
        if len(sag_indices) > 0:
            sag_depth = (nominal_voltage - np.min(rms_values)) / nominal_voltage
            sag_duration = len(sag_indices) * (window_size / 2) / self.fs
        else:
            sag_depth = 0
            sag_duration = 0
        
        return {
            'sag_detected': len(sag_indices) > 0,
            'sag_depth': sag_depth,
            'sag_duration': sag_duration,
            'rms_min': np.min(rms_values),
        }
    
    def flicker_analysis(
        self,
        voltage_signal: np.ndarray,
        nominal_voltage: float
    ) -> float:
        """
        闪变分析（简化）
        
        Args:
            voltage_signal: 电压信号
            nominal_voltage: 额定电压
            
        Returns:
            短时闪变值 Pst
        """
        # 简化计算：基于电压波动
        voltage_fluctuation = np.diff(voltage_signal) / nominal_voltage
        pst = np.sqrt(np.mean(voltage_fluctuation**2)) * 100
        
        return pst
