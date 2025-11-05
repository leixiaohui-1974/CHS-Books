"""
风资源模型

本模块包含风资源评估的核心功能:
- Weibull分布建模
- 风功率密度计算
- 风切变模型
- 湍流强度计算
"""

import numpy as np
from typing import Tuple, Dict, List
from scipy import stats
from scipy.special import gamma


# ==================== Weibull分布模型 ====================

class WeibullDistribution:
    """
    Weibull分布模型
    
    用于描述风速概率分布:
    f(v) = (k/c) * (v/c)^(k-1) * exp(-(v/c)^k)
    
    参数:
        k: 形状参数 (shape parameter), 典型值1.5-3.0
        c: 尺度参数 (scale parameter), 接近平均风速
    """
    
    def __init__(self, k: float, c: float, name: str = "Weibull"):
        """
        初始化Weibull分布
        
        Args:
            k: 形状参数
            c: 尺度参数 (m/s)
            name: 模型名称
        """
        if k <= 0:
            raise ValueError("形状参数k必须大于0")
        if c <= 0:
            raise ValueError("尺度参数c必须大于0")
            
        self.k = k
        self.c = c
        self.name = name
        
        # 计算统计量
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """计算分布的统计量"""
        # 平均风速
        self.mean_speed = self.c * gamma(1 + 1/self.k)
        
        # 风速方差
        self.variance = self.c**2 * (gamma(1 + 2/self.k) - gamma(1 + 1/self.k)**2)
        
        # 标准差
        self.std_dev = np.sqrt(self.variance)
        
        # 最可能风速 (概率密度最大处)
        if self.k > 1:
            self.mode_speed = self.c * ((self.k - 1) / self.k)**(1/self.k)
        else:
            self.mode_speed = 0.0
    
    def pdf(self, v: np.ndarray) -> np.ndarray:
        """
        概率密度函数
        
        Args:
            v: 风速 (m/s)
            
        Returns:
            概率密度
        """
        v = np.asarray(v)
        pdf = np.zeros_like(v, dtype=float)
        mask = v >= 0
        
        pdf[mask] = (self.k / self.c) * (v[mask] / self.c)**(self.k - 1) * \
                    np.exp(-(v[mask] / self.c)**self.k)
        
        return pdf
    
    def cdf(self, v: np.ndarray) -> np.ndarray:
        """
        累积分布函数
        
        Args:
            v: 风速 (m/s)
            
        Returns:
            累积概率
        """
        v = np.asarray(v)
        cdf = np.zeros_like(v, dtype=float)
        mask = v >= 0
        
        cdf[mask] = 1 - np.exp(-(v[mask] / self.c)**self.k)
        
        return cdf
    
    def sample(self, size: int = 1) -> np.ndarray:
        """
        生成随机风速样本
        
        Args:
            size: 样本数量
            
        Returns:
            风速样本
        """
        u = np.random.uniform(0, 1, size)
        v = self.c * (-np.log(1 - u))**(1 / self.k)
        return v
    
    @staticmethod
    def fit_from_data(wind_speeds: np.ndarray) -> 'WeibullDistribution':
        """
        从实测风速数据拟合Weibull参数
        
        Args:
            wind_speeds: 风速数据数组 (m/s)
            
        Returns:
            拟合的Weibull分布对象
        """
        # 移除非正值
        valid_data = wind_speeds[wind_speeds > 0]
        
        if len(valid_data) < 2:
            raise ValueError("有效数据点不足")
        
        # 使用scipy的Weibull拟合
        shape, loc, scale = stats.weibull_min.fit(valid_data, floc=0)
        
        return WeibullDistribution(k=shape, c=scale, name="Fitted_Weibull")
    
    def get_status(self) -> Dict:
        """返回分布状态信息"""
        return {
            'name': self.name,
            'shape_k': self.k,
            'scale_c': self.c,
            'mean_speed': self.mean_speed,
            'std_dev': self.std_dev,
            'mode_speed': self.mode_speed
        }


# ==================== 风功率密度 ====================

class WindPowerDensity:
    """
    风功率密度计算
    
    风功率密度 (W/m²):
    P/A = 0.5 * ρ * v³
    
    其中:
        ρ: 空气密度 (kg/m³)
        v: 风速 (m/s)
    """
    
    def __init__(self, rho: float = 1.225, name: str = "WindPowerDensity"):
        """
        初始化风功率密度计算器
        
        Args:
            rho: 空气密度 (kg/m³), 标准大气压下海平面为1.225
            name: 计算器名称
        """
        if rho <= 0:
            raise ValueError("空气密度必须大于0")
            
        self.rho = rho
        self.name = name
    
    def calculate(self, v: np.ndarray) -> np.ndarray:
        """
        计算风功率密度
        
        Args:
            v: 风速 (m/s)
            
        Returns:
            功率密度 (W/m²)
        """
        v = np.asarray(v)
        return 0.5 * self.rho * v**3
    
    def average_from_weibull(self, weibull: WeibullDistribution) -> float:
        """
        从Weibull分布计算平均风功率密度
        
        P_avg = 0.5 * ρ * c³ * Γ(1 + 3/k)
        
        Args:
            weibull: Weibull分布对象
            
        Returns:
            平均功率密度 (W/m²)
        """
        return 0.5 * self.rho * weibull.c**3 * gamma(1 + 3/weibull.k)
    
    def energy_pattern_factor(self, weibull: WeibullDistribution) -> float:
        """
        能量模式因子 (Energy Pattern Factor, EPF)
        
        EPF = P_avg / (0.5 * ρ * v_mean³)
        
        Args:
            weibull: Weibull分布对象
            
        Returns:
            EPF值
        """
        p_avg = self.average_from_weibull(weibull)
        p_mean = 0.5 * self.rho * weibull.mean_speed**3
        
        return p_avg / p_mean if p_mean > 0 else 0.0
    
    @staticmethod
    def air_density(T: float, P: float, elevation: float = 0) -> float:
        """
        计算不同条件下的空气密度
        
        ρ = P / (R * T)
        
        Args:
            T: 温度 (°C)
            P: 气压 (Pa), 若为None则根据海拔估算
            elevation: 海拔高度 (m)
            
        Returns:
            空气密度 (kg/m³)
        """
        # 温度转换为开尔文
        T_K = T + 273.15
        
        # 如果没有给定气压，根据海拔估算
        if P is None:
            # 标准大气压
            P0 = 101325  # Pa
            # 气压随海拔的变化 (简化模型)
            P = P0 * (1 - 0.0065 * elevation / 288.15)**5.255
        
        # 空气气体常数
        R = 287.05  # J/(kg·K)
        
        # 计算密度
        rho = P / (R * T_K)
        
        return rho
    
    def get_status(self) -> Dict:
        """返回计算器状态"""
        return {
            'name': self.name,
            'air_density': self.rho
        }


# ==================== 风速统计分析 ====================

class WindStatistics:
    """
    风速数据统计分析
    
    提供风速数据的统计分析功能:
    - 基本统计量
    - 分布拟合
    - 功率密度计算
    """
    
    def __init__(self, wind_speeds: np.ndarray, rho: float = 1.225, 
                 name: str = "WindStats"):
        """
        初始化风速统计分析
        
        Args:
            wind_speeds: 风速数据 (m/s)
            rho: 空气密度 (kg/m³)
            name: 分析名称
        """
        self.wind_speeds = np.asarray(wind_speeds)
        self.rho = rho
        self.name = name
        
        # 移除无效数据
        self.valid_data = self.wind_speeds[self.wind_speeds >= 0]
        
        if len(self.valid_data) == 0:
            raise ValueError("没有有效的风速数据")
        
        # 计算基本统计量
        self._calculate_basic_stats()
        
        # 拟合Weibull分布
        self.weibull = None
        if len(self.valid_data) >= 2:
            try:
                self.weibull = WeibullDistribution.fit_from_data(self.valid_data)
            except:
                pass
        
        # 风功率密度计算器
        self.power_density = WindPowerDensity(rho=rho)
    
    def _calculate_basic_stats(self):
        """计算基本统计量"""
        self.mean = np.mean(self.valid_data)
        self.median = np.median(self.valid_data)
        self.std = np.std(self.valid_data)
        self.min = np.min(self.valid_data)
        self.max = np.max(self.valid_data)
        
        # 百分位数
        self.percentile_25 = np.percentile(self.valid_data, 25)
        self.percentile_75 = np.percentile(self.valid_data, 75)
        self.percentile_95 = np.percentile(self.valid_data, 95)
    
    def histogram(self, bins: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算风速直方图
        
        Args:
            bins: 分组数量
            
        Returns:
            (bin_centers, frequencies)
        """
        counts, bin_edges = np.histogram(self.valid_data, bins=bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        return bin_centers, counts
    
    def average_power_density(self) -> float:
        """
        计算实测数据的平均风功率密度
        
        Returns:
            平均功率密度 (W/m²)
        """
        power_densities = self.power_density.calculate(self.valid_data)
        return np.mean(power_densities)
    
    def weibull_power_density(self) -> float:
        """
        从Weibull分布计算平均功率密度
        
        Returns:
            平均功率密度 (W/m²), 如果未拟合则返回None
        """
        if self.weibull is None:
            return None
        
        return self.power_density.average_from_weibull(self.weibull)
    
    def get_report(self) -> Dict:
        """
        生成统计报告
        
        Returns:
            统计报告字典
        """
        report = {
            'name': self.name,
            'data_points': len(self.valid_data),
            'basic_stats': {
                'mean': self.mean,
                'median': self.median,
                'std': self.std,
                'min': self.min,
                'max': self.max,
                'percentile_25': self.percentile_25,
                'percentile_75': self.percentile_75,
                'percentile_95': self.percentile_95
            },
            'power_density': {
                'measured_avg': self.average_power_density(),
                'weibull_avg': self.weibull_power_density()
            }
        }
        
        if self.weibull is not None:
            report['weibull_params'] = self.weibull.get_status()
        
        return report


# ==================== 辅助函数 ====================

def generate_synthetic_wind_data(hours: int = 8760, mean_speed: float = 7.0,
                                 k: float = 2.0, dt: float = 1.0) -> np.ndarray:
    """
    生成合成风速数据（用于测试和演示）
    
    Args:
        hours: 小时数（默认一年）
        mean_speed: 目标平均风速 (m/s)
        k: Weibull形状参数
        dt: 时间步长 (小时)
        
    Returns:
        风速时间序列
    """
    # 从mean_speed反推scale参数c
    c = mean_speed / gamma(1 + 1/k)
    
    # 创建Weibull分布
    weibull = WeibullDistribution(k=k, c=c)
    
    # 生成样本数量
    n_samples = int(hours / dt)
    
    # 生成风速样本
    wind_speeds = weibull.sample(n_samples)
    
    return wind_speeds
