"""
Terzaghi固结理论模块

提供：
- 土层类定义
- 一维固结方程
- 固结度计算
- 压缩量计算
"""

import numpy as np
from scipy import special
from dataclasses import dataclass
from typing import Union, Optional, Tuple


@dataclass
class SoilLayer:
    """
    土层类
    
    Attributes
    ----------
    name : str
        土层名称
    top : float
        顶面标高 [m]
    bottom : float
        底面标高 [m]
    av : float, optional
        压缩系数 [1/kPa]
    Cc : float, optional
        压缩指数 [-]
    e0 : float, optional
        初始孔隙比 [-]
    sigma_c : float, optional
        先期固结压力 [kPa]
    Cv : float, optional
        固结系数 [m²/day]
    gamma_sat : float, optional
        饱和重度 [kN/m³]
    """
    name: str
    top: float
    bottom: float
    av: Optional[float] = None
    Cc: Optional[float] = None
    e0: Optional[float] = None
    sigma_c: Optional[float] = None
    Cv: Optional[float] = None
    gamma_sat: float = 19.0
    
    def __post_init__(self):
        """计算土层厚度"""
        self.thickness = self.top - self.bottom
        self.z_mid = (self.top + self.bottom) / 2
    
    def compute_compression_linear(self, delta_sigma: float) -> float:
        """
        线性压缩模型
        
        ΔH = av * Δσ' * H
        
        Parameters
        ----------
        delta_sigma : float
            有效应力增量 [kPa]
        
        Returns
        -------
        delta_H : float
            压缩量 [m]
        """
        if self.av is None:
            raise ValueError(f"Layer {self.name}: av not specified")
        
        delta_H = self.av * delta_sigma * self.thickness
        return delta_H
    
    def compute_compression_logarithmic(
        self,
        sigma_0: float,
        sigma_f: float
    ) -> float:
        """
        对数压缩模型（e-logσ'直线）
        
        ΔH/H = Δε = Cc / (1+e0) * log10(σ'f / σ'0)
        
        Parameters
        ----------
        sigma_0 : float
            初始有效应力 [kPa]
        sigma_f : float
            最终有效应力 [kPa]
        
        Returns
        -------
        delta_H : float
            压缩量 [m]
        """
        if self.Cc is None or self.e0 is None:
            raise ValueError(f"Layer {self.name}: Cc and e0 required")
        
        strain = self.Cc / (1 + self.e0) * np.log10(sigma_f / sigma_0)
        delta_H = strain * self.thickness
        return delta_H
    
    def compute_compression_with_preconsolidation(
        self,
        sigma_0: float,
        sigma_f: float,
        Cs: Optional[float] = None
    ) -> float:
        """
        考虑先期固结的压缩
        
        分段计算：
        - σ'0 → σ'c: 再压缩（Cs）
        - σ'c → σ'f: 正常压缩（Cc）
        
        Parameters
        ----------
        sigma_0 : float
            初始有效应力 [kPa]
        sigma_f : float
            最终有效应力 [kPa]
        Cs : float, optional
            回弹指数，默认Cs = Cc/5
        
        Returns
        -------
        delta_H : float
            总压缩量 [m]
        """
        if self.Cc is None or self.e0 is None or self.sigma_c is None:
            raise ValueError(f"Layer {self.name}: Cc, e0, sigma_c required")
        
        if Cs is None:
            Cs = self.Cc / 5  # 经验关系
        
        delta_H = 0.0
        
        if sigma_f <= self.sigma_c:
            # 仅再压缩
            strain = Cs / (1 + self.e0) * np.log10(sigma_f / sigma_0)
            delta_H = strain * self.thickness
        else:
            if sigma_0 < self.sigma_c:
                # 再压缩 + 正常压缩
                strain_recomp = Cs / (1 + self.e0) * np.log10(self.sigma_c / sigma_0)
                strain_virgin = self.Cc / (1 + self.e0) * np.log10(sigma_f / self.sigma_c)
                delta_H = (strain_recomp + strain_virgin) * self.thickness
            else:
                # 仅正常压缩
                strain = self.Cc / (1 + self.e0) * np.log10(sigma_f / sigma_0)
                delta_H = strain * self.thickness
        
        return delta_H


def terzaghi_consolidation_1d(
    z: np.ndarray,
    t: float,
    H: float,
    Cv: float,
    u0: float = 100.0,
    drainage: str = 'double',
    n_terms: int = 20
) -> np.ndarray:
    """
    Terzaghi一维固结方程解析解
    
    ∂u/∂t = Cv * ∂²u/∂z²
    
    u(z,t): 超孔隙水压力
    
    Parameters
    ----------
    z : ndarray
        深度坐标 [m]
    t : float
        时间 [day]
    H : float
        排水距离 [m]（双面排水H=层厚/2，单面排水H=层厚）
    Cv : float
        固结系数 [m²/day]
    u0 : float, optional
        初始超孔压 [kPa]，默认100
    drainage : str, optional
        排水条件，'double'（双面）或'single'（单面）
    n_terms : int, optional
        级数项数，默认20
    
    Returns
    -------
    u : ndarray
        超孔压 [kPa]
    
    Notes
    -----
    解析解（级数形式）：
    u(z,t) = Σ (2u0/M) * sin(Mz/H) * exp(-M²Tv)
    M = π(2m+1)/2, m=0,1,2,...
    Tv = Cv*t/H²
    """
    Tv = Cv * t / H**2
    
    u = np.zeros_like(z)
    
    for m in range(n_terms):
        M = np.pi * (2*m + 1) / 2
        u += (2 * u0 / M) * np.sin(M * z / H) * np.exp(-M**2 * Tv)
    
    return u


def consolidation_degree(
    Tv: Union[float, np.ndarray],
    drainage: str = 'double'
) -> Union[float, np.ndarray]:
    """
    平均固结度U(Tv)
    
    U = 1 - Σ (2/M²) * exp(-M²Tv)
    
    Parameters
    ----------
    Tv : float or array
        时间因子 Tv = Cv*t/H²
    drainage : str
        排水条件
    
    Returns
    -------
    U : float or array
        平均固结度（0~1）
    
    Notes
    -----
    简化公式（Tv < 0.2）：
    U ≈ √(4Tv/π)
    
    简化公式（Tv > 0.2）：
    U ≈ 1 - 10^(-Tv/0.085)
    """
    Tv = np.asarray(Tv)
    U = np.zeros_like(Tv, dtype=float)
    
    # 精确计算（级数）
    n_terms = 20
    for m in range(n_terms):
        M = np.pi * (2*m + 1) / 2
        U += (2 / M**2) * np.exp(-M**2 * Tv)
    
    U = 1 - U
    U = np.clip(U, 0, 1)
    
    return U


def consolidation_settlement(
    t: np.ndarray,
    S_ultimate: float,
    Cv: float,
    H: float,
    drainage: str = 'double'
) -> np.ndarray:
    """
    固结沉降时间曲线
    
    S(t) = U(t) * S_ultimate
    
    Parameters
    ----------
    t : ndarray
        时间 [day]
    S_ultimate : float
        最终沉降量 [m]
    Cv : float
        固结系数 [m²/day]
    H : float
        排水距离 [m]
    drainage : str
        排水条件
    
    Returns
    -------
    S : ndarray
        沉降量 [m]
    """
    Tv = Cv * t / H**2
    U = consolidation_degree(Tv, drainage)
    S = U * S_ultimate
    
    return S


def compute_settlement_time(
    U_target: float,
    S_ultimate: float,
    Cv: float,
    H: float,
    drainage: str = 'double'
) -> float:
    """
    计算达到指定固结度所需时间
    
    Parameters
    ----------
    U_target : float
        目标固结度（0~1）
    S_ultimate : float
        最终沉降量 [m]
    Cv : float
        固结系数 [m²/day]
    H : float
        排水距离 [m]
    drainage : str
        排水条件
    
    Returns
    -------
    t : float
        所需时间 [day]
    """
    # 反查Tv
    if U_target < 0.5:
        # 简化公式
        Tv = np.pi / 4 * U_target**2
    else:
        # 近似公式
        Tv = -0.085 * np.log10(1 - U_target)
    
    t = Tv * H**2 / Cv
    
    return t


def compute_Cv_from_t50(t50: float, H: float, drainage: str = 'double') -> float:
    """
    根据t50（U=50%时间）反算Cv
    
    Cv = Tv50 * H² / t50
    
    Parameters
    ----------
    t50 : float
        U=50%时的时间 [day]
    H : float
        排水距离 [m]
    drainage : str
        排水条件
    
    Returns
    -------
    Cv : float
        固结系数 [m²/day]
    """
    Tv50 = 0.197  # U=50%时的Tv值
    Cv = Tv50 * H**2 / t50
    return Cv
