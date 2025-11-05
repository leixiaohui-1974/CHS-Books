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


# ==================== 风切变模型 ====================

class WindShear:
    """
    风切变模型
    
    描述风速随高度的变化规律，两种常用模型：
    1. 指数律 (Power Law)
    2. 对数律 (Logarithmic Law)
    """
    
    def __init__(self, model: str = "power_law", name: str = "WindShear"):
        """
        初始化风切变模型
        
        Args:
            model: 模型类型 "power_law" 或 "log_law"
            name: 模型名称
        """
        if model not in ["power_law", "log_law"]:
            raise ValueError("模型类型必须是 'power_law' 或 'log_law'")
        
        self.model = model
        self.name = name
    
    def power_law(self, v_ref: float, h_ref: float, h: np.ndarray, 
                  alpha: float = 0.14) -> np.ndarray:
        """
        指数律（幂律）风切变模型
        
        v(h) = v_ref * (h / h_ref)^α
        
        Args:
            v_ref: 参考高度的风速 (m/s)
            h_ref: 参考高度 (m)
            h: 目标高度 (m)
            alpha: 风切变指数，典型值0.1-0.4
                   - 平坦地形：0.14
                   - 粗糙地形：0.20-0.25
                   - 城市：0.30-0.40
        
        Returns:
            目标高度的风速 (m/s)
        """
        h = np.asarray(h)
        
        # 防止除零
        if h_ref <= 0:
            raise ValueError("参考高度必须大于0")
        
        # 计算风速
        v = v_ref * (h / h_ref)**alpha
        
        return v
    
    def log_law(self, v_ref: float, h_ref: float, h: np.ndarray,
                z0: float = 0.1) -> np.ndarray:
        """
        对数律风切变模型
        
        v(h) = v_ref * ln(h/z0) / ln(h_ref/z0)
        
        Args:
            v_ref: 参考高度的风速 (m/s)
            h_ref: 参考高度 (m)
            h: 目标高度 (m)
            z0: 粗糙度长度 (m)，典型值：
                - 平静水面：0.0001-0.001
                - 草地：0.01-0.04
                - 农田：0.05-0.15
                - 森林：0.5-1.0
                - 城市：1.0-3.0
        
        Returns:
            目标高度的风速 (m/s)
        """
        h = np.asarray(h)
        
        # 防止对数参数无效
        if z0 <= 0:
            raise ValueError("粗糙度长度必须大于0")
        if h_ref <= z0:
            raise ValueError("参考高度必须大于粗糙度长度")
        
        # 确保h > z0
        h = np.maximum(h, z0 + 1e-6)
        
        # 计算风速
        v = v_ref * np.log(h / z0) / np.log(h_ref / z0)
        
        return v
    
    def calculate(self, v_ref: float, h_ref: float, h: np.ndarray, 
                  **kwargs) -> np.ndarray:
        """
        根据选择的模型计算风速
        
        Args:
            v_ref: 参考高度风速 (m/s)
            h_ref: 参考高度 (m)
            h: 目标高度 (m)
            **kwargs: 模型参数
        
        Returns:
            目标高度风速 (m/s)
        """
        if self.model == "power_law":
            alpha = kwargs.get('alpha', 0.14)
            return self.power_law(v_ref, h_ref, h, alpha)
        else:  # log_law
            z0 = kwargs.get('z0', 0.1)
            return self.log_law(v_ref, h_ref, h, z0)
    
    @staticmethod
    def estimate_alpha(v1: float, h1: float, v2: float, h2: float) -> float:
        """
        从两个高度的风速估算风切变指数
        
        α = ln(v2/v1) / ln(h2/h1)
        
        Args:
            v1: 高度h1的风速 (m/s)
            h1: 高度1 (m)
            v2: 高度h2的风速 (m/s)
            h2: 高度2 (m)
        
        Returns:
            风切变指数 α
        """
        if v1 <= 0 or v2 <= 0:
            raise ValueError("风速必须大于0")
        if h1 <= 0 or h2 <= 0:
            raise ValueError("高度必须大于0")
        if h1 == h2:
            raise ValueError("两个高度不能相同")
        
        alpha = np.log(v2 / v1) / np.log(h2 / h1)
        return alpha
    
    def get_status(self) -> Dict:
        """返回模型状态"""
        return {
            'name': self.name,
            'model': self.model
        }


# ==================== 湍流强度模型 ====================

class TurbulenceIntensity:
    """
    湍流强度模型
    
    湍流强度定义为风速标准差与平均风速的比值：
    TI = σ_v / v_mean
    
    影响风力机的疲劳载荷和功率波动
    """
    
    def __init__(self, name: str = "TurbulenceIntensity"):
        """初始化湍流强度模型"""
        self.name = name
    
    def calculate(self, wind_speeds: np.ndarray) -> float:
        """
        计算湍流强度
        
        Args:
            wind_speeds: 风速时间序列 (m/s)
        
        Returns:
            湍流强度 (无量纲)
        """
        wind_speeds = np.asarray(wind_speeds)
        
        if len(wind_speeds) < 2:
            raise ValueError("数据点不足")
        
        v_mean = np.mean(wind_speeds)
        
        if v_mean <= 0:
            return 0.0
        
        sigma_v = np.std(wind_speeds)
        TI = sigma_v / v_mean
        
        return TI
    
    def iec_category(self, v_mean: float, category: str = "A") -> float:
        """
        IEC 61400-1标准湍流强度模型
        
        TI = I_ref * (0.75 * v_mean + b) / (v_mean + 5.6)
        
        Args:
            v_mean: 平均风速 (m/s)
            category: 湍流等级
                - "A": 高湍流 (I_ref=0.16)
                - "B": 中等湍流 (I_ref=0.14)
                - "C": 低湍流 (I_ref=0.12)
        
        Returns:
            湍流强度
        """
        # IEC标准参数
        I_ref_dict = {
            "A": 0.16,
            "B": 0.14,
            "C": 0.12
        }
        
        if category not in I_ref_dict:
            raise ValueError(f"湍流等级必须是A, B或C")
        
        I_ref = I_ref_dict[category]
        
        # 参数b（特征湍流参数）
        b = 5.6  # m/s
        
        # 计算湍流强度
        if v_mean <= 0:
            return I_ref
        
        TI = I_ref * (0.75 * v_mean + b) / (v_mean + b)
        
        return TI
    
    def kaimal_spectrum(self, f: np.ndarray, v_mean: float, 
                        sigma_v: float, L: float = 340.2) -> np.ndarray:
        """
        Kaimal湍流功率谱密度
        
        S(f) = 4 * σ_v² * L / v_mean / (1 + 6*f*L/v_mean)^(5/3)
        
        Args:
            f: 频率 (Hz)
            v_mean: 平均风速 (m/s)
            sigma_v: 风速标准差 (m/s)
            L: 积分尺度 (m)，典型值340.2m
        
        Returns:
            功率谱密度 (m²/s²/Hz)
        """
        f = np.asarray(f)
        
        # 防止除零
        if v_mean <= 0:
            raise ValueError("平均风速必须大于0")
        
        # 归一化频率
        f_normalized = 6 * f * L / v_mean
        
        # 计算功率谱
        S = 4 * sigma_v**2 * L / v_mean / (1 + f_normalized)**(5/3)
        
        return S
    
    def generate_turbulent_wind(self, v_mean: float, TI: float, 
                               duration: float, dt: float = 0.1) -> np.ndarray:
        """
        生成湍流风速时间序列（简化方法）
        
        Args:
            v_mean: 平均风速 (m/s)
            TI: 湍流强度
            duration: 持续时间 (s)
            dt: 时间步长 (s)
        
        Returns:
            湍流风速时间序列
        """
        # 时间序列
        n_samples = int(duration / dt)
        
        # 标准差
        sigma_v = TI * v_mean
        
        # 生成随机波动（白噪声）
        noise = np.random.normal(0, sigma_v, n_samples)
        
        # 低通滤波（简单移动平均）
        window_size = max(int(10 / dt), 3)  # 约10秒窗口
        kernel = np.ones(window_size) / window_size
        filtered_noise = np.convolve(noise, kernel, mode='same')
        
        # 叠加到平均风速
        v_turbulent = v_mean + filtered_noise
        
        # 确保非负
        v_turbulent = np.maximum(v_turbulent, 0)
        
        return v_turbulent
    
    def classify_terrain(self, TI: float, v_mean: float = 10.0) -> str:
        """
        根据湍流强度估计地形类型
        
        Args:
            TI: 湍流强度
            v_mean: 参考风速 (m/s)
        
        Returns:
            地形类型描述
        """
        # 根据IEC标准分类
        if TI < 0.12:
            return "低湍流地形（平坦海面、开阔平原）"
        elif TI < 0.14:
            return "中等湍流地形（农田、草地）"
        elif TI < 0.16:
            return "高湍流地形（丘陵、沿海）"
        else:
            return "极高湍流地形（山地、森林、城市）"
    
    def get_status(self) -> Dict:
        """返回模型状态"""
        return {
            'name': self.name
        }


# ==================== 风廓线模型 ====================

class WindProfile:
    """
    风廓线模型（整合风切变和湍流）
    
    提供完整的风速垂直分布分析
    """
    
    def __init__(self, v_ref: float, h_ref: float, 
                 shear_model: str = "power_law",
                 name: str = "WindProfile"):
        """
        初始化风廓线模型
        
        Args:
            v_ref: 参考高度风速 (m/s)
            h_ref: 参考高度 (m)
            shear_model: 风切变模型类型
            name: 模型名称
        """
        self.v_ref = v_ref
        self.h_ref = h_ref
        self.name = name
        
        # 创建风切变模型
        self.shear = WindShear(model=shear_model)
        
        # 创建湍流模型
        self.turbulence = TurbulenceIntensity()
    
    def get_profile(self, heights: np.ndarray, **kwargs) -> np.ndarray:
        """
        获取风速廓线
        
        Args:
            heights: 高度数组 (m)
            **kwargs: 风切变模型参数
        
        Returns:
            各高度的风速
        """
        return self.shear.calculate(self.v_ref, self.h_ref, heights, **kwargs)
    
    def hub_height_wind(self, h_hub: float, **kwargs) -> float:
        """
        计算轮毂高度风速
        
        Args:
            h_hub: 轮毂高度 (m)
            **kwargs: 风切变参数
        
        Returns:
            轮毂高度风速 (m/s)
        """
        return self.shear.calculate(self.v_ref, self.h_ref, 
                                   np.array([h_hub]), **kwargs)[0]
    
    def rotor_equivalent_wind(self, h_hub: float, rotor_diameter: float,
                             n_points: int = 10, **kwargs) -> float:
        """
        计算风轮等效风速（考虑风切变）
        
        对风轮扫掠面积内的风速进行加权平均
        
        Args:
            h_hub: 轮毂高度 (m)
            rotor_diameter: 风轮直径 (m)
            n_points: 采样点数量
            **kwargs: 风切变参数
        
        Returns:
            等效风速 (m/s)
        """
        # 风轮半径
        R = rotor_diameter / 2
        
        # 采样点（在风轮圆盘上）
        r_samples = np.linspace(0, R, n_points)
        
        # 对应的高度
        h_samples = h_hub + r_samples  # 简化：只考虑垂直方向
        
        # 各点风速
        v_samples = self.shear.calculate(self.v_ref, self.h_ref, 
                                        h_samples, **kwargs)
        
        # 面积加权平均（简化为线性加权）
        weights = r_samples / np.sum(r_samples) if np.sum(r_samples) > 0 else np.ones_like(r_samples) / len(r_samples)
        v_eq = np.sum(v_samples * weights)
        
        return v_eq
    
    def get_status(self) -> Dict:
        """返回模型状态"""
        return {
            'name': self.name,
            'v_ref': self.v_ref,
            'h_ref': self.h_ref,
            'shear_model': self.shear.model
        }
