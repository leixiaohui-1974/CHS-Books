"""
Green-Ampt超渗产流模型
====================

Green-Ampt模型是经典的物理性产流模型，基于达西定律描述降雨入渗过程。

理论基础
--------
1. 入渗率计算：
   f(t) = K × [1 + (ψ × Δθ) / F(t)]
   
   其中：
   - f(t): 入渗率 (mm/h)
   - K: 饱和导水率 (mm/h)
   - ψ: 湿润锋吸力 (mm)
   - Δθ: 初始含水率差 (θs - θi)
   - F(t): 累积入渗量 (mm)

2. 累积入渗量：
   F(t) = K×t + ψ×Δθ×ln[1 + F(t)/(ψ×Δθ)]

3. 产流判断：
   - 若 i(t) < f(t)，全部入渗，无地表径流
   - 若 i(t) ≥ f(t)，超渗产流，R = i - f

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Tuple, Optional
import warnings


class GreenAmptModel:
    """
    Green-Ampt超渗产流模型
    
    Parameters
    ----------
    params : dict
        模型参数，包括：
        - K : float, 饱和导水率 (mm/h)
        - psi : float, 湿润锋吸力 (mm)
        - theta_s : float, 饱和含水率 (-)
        - theta_i : float, 初始含水率 (-)
        - dt : float, 时间步长 (h)
    
    Attributes
    ----------
    K : float
        饱和导水率
    psi : float
        湿润锋吸力
    delta_theta : float
        含水率差 (theta_s - theta_i)
    F : float
        累积入渗量 (mm)
    ponding : bool
        是否开始积水
    t_ponding : float
        积水时间 (h)
    
    Examples
    --------
    >>> params = {
    ...     'K': 10.0,      # mm/h
    ...     'psi': 100.0,   # mm
    ...     'theta_s': 0.45,
    ...     'theta_i': 0.20,
    ...     'dt': 0.1       # h
    ... }
    >>> model = GreenAmptModel(params)
    >>> rainfall = np.array([20, 25, 30, 15, 10, 5])  # mm/h
    >>> results = model.run(rainfall)
    """
    
    def __init__(self, params: Dict[str, float]):
        """初始化Green-Ampt模型"""
        # 验证必需参数
        required_params = ['K', 'psi', 'theta_s', 'theta_i', 'dt']
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        # 设置参数
        self.K = params['K']              # 饱和导水率 (mm/h)
        self.psi = params['psi']          # 湿润锋吸力 (mm)
        self.theta_s = params['theta_s']  # 饱和含水率
        self.theta_i = params['theta_i']  # 初始含水率
        self.dt = params['dt']            # 时间步长 (h)
        
        # 计算含水率差
        self.delta_theta = self.theta_s - self.theta_i
        
        if self.delta_theta <= 0:
            raise ValueError("初始含水率必须小于饱和含水率")
        
        # 状态变量
        self.F = 0.0           # 累积入渗量 (mm)
        self.ponding = False   # 是否开始积水
        self.t_ponding = 0.0   # 积水时间 (h)
        
        # 物理约束检查
        if self.K <= 0:
            raise ValueError("饱和导水率必须为正")
        if self.psi < 0:
            raise ValueError("湿润锋吸力不能为负")
        if not (0 < self.theta_i < self.theta_s <= 1):
            raise ValueError("含水率必须满足: 0 < θi < θs ≤ 1")
    
    def infiltration_capacity(self, F: float) -> float:
        """
        计算当前入渗能力
        
        Parameters
        ----------
        F : float
            累积入渗量 (mm)
        
        Returns
        -------
        f : float
            入渗率 (mm/h)
        """
        if F <= 0:
            # 初始入渗率（无穷大，用一个大值代替）
            return 1e6
        
        # Green-Ampt公式
        f = self.K * (1 + (self.psi * self.delta_theta) / F)
        
        return f
    
    def solve_cumulative_infiltration(self, rainfall: float, F_prev: float) -> float:
        """
        求解累积入渗量
        
        使用迭代法求解隐式方程：
        F(t) = K×Δt + F(t-1) + ψ×Δθ×ln[(F + ψ×Δθ)/(F_prev + ψ×Δθ)]
        
        Parameters
        ----------
        rainfall : float
            降雨强度 (mm/h)
        F_prev : float
            上一时刻累积入渗量 (mm)
        
        Returns
        -------
        F : float
            当前累积入渗量 (mm)
        """
        # 最大可能入渗量（全部降雨入渗）
        max_infiltration = rainfall * self.dt
        
        if not self.ponding:
            # 尚未积水，检查是否开始积水
            # 积水条件：降雨强度 > 入渗能力
            f = self.infiltration_capacity(F_prev)
            
            if rainfall > f:
                # 开始积水
                self.ponding = True
                # 计算积水时刻的累积入渗量
                # Fp = (K × ψ × Δθ) / (i - K)
                if rainfall > self.K:
                    Fp = (self.K * self.psi * self.delta_theta) / (rainfall - self.K)
                else:
                    Fp = F_prev + max_infiltration
                
                # 如果Fp小于已有入渗量，使用已有值
                if Fp < F_prev:
                    Fp = F_prev
                
                return Fp
            else:
                # 未积水，全部入渗
                return F_prev + max_infiltration
        
        # 已积水，使用迭代法求解
        # 初始猜测
        F = F_prev + self.K * self.dt
        
        # 牛顿迭代法
        max_iter = 20
        tol = 1e-6
        
        for _ in range(max_iter):
            # 目标函数: f(F) = F - K×Δt - F_prev - ψ×Δθ×ln[(F + ψ×Δθ)/(F_prev + ψ×Δθ)]
            psi_theta = self.psi * self.delta_theta
            
            if F + psi_theta <= 0 or F_prev + psi_theta <= 0:
                break
            
            f_val = F - self.K * self.dt - F_prev - \
                    psi_theta * np.log((F + psi_theta) / (F_prev + psi_theta))
            
            # 导数: f'(F) = 1 - ψ×Δθ/(F + ψ×Δθ)
            df_val = 1 - psi_theta / (F + psi_theta)
            
            if abs(df_val) < 1e-10:
                break
            
            # 更新
            F_new = F - f_val / df_val
            
            # 确保非负
            F_new = max(F_new, F_prev)
            
            # 检查收敛
            if abs(F_new - F) < tol:
                F = F_new
                break
            
            F = F_new
        
        # 不能超过最大降雨量
        F = min(F, F_prev + max_infiltration)
        
        return F
    
    def run(self, rainfall: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行Green-Ampt模型
        
        Parameters
        ----------
        rainfall : ndarray
            降雨强度序列 (mm/h)
        
        Returns
        -------
        results : dict
            包含以下键值：
            - infiltration : ndarray, 入渗量 (mm)
            - runoff : ndarray, 地表径流 (mm)
            - F : ndarray, 累积入渗量 (mm)
            - f : ndarray, 入渗率 (mm/h)
        """
        n = len(rainfall)
        
        # 初始化结果数组
        infiltration = np.zeros(n)  # 时段入渗量 (mm)
        runoff = np.zeros(n)        # 时段径流量 (mm)
        F_series = np.zeros(n)      # 累积入渗量 (mm)
        f_series = np.zeros(n)      # 入渗率 (mm/h)
        
        # 重置状态
        self.reset()
        
        # 逐时段计算
        for t in range(n):
            i = rainfall[t]  # 当前降雨强度 (mm/h)
            
            if i <= 0:
                # 无降雨
                infiltration[t] = 0
                runoff[t] = 0
                F_series[t] = self.F
                f_series[t] = self.infiltration_capacity(self.F)
                continue
            
            # 求解累积入渗量
            F_new = self.solve_cumulative_infiltration(i, self.F)
            
            # 时段入渗量
            inf = F_new - self.F
            
            # 时段降雨量
            P = i * self.dt
            
            # 时段径流量
            R = max(0, P - inf)
            
            # 保存结果
            infiltration[t] = inf
            runoff[t] = R
            F_series[t] = F_new
            f_series[t] = self.infiltration_capacity(F_new)
            
            # 更新状态
            self.F = F_new
        
        return {
            'infiltration': infiltration,
            'runoff': runoff,
            'F': F_series,
            'f': f_series
        }
    
    def reset(self):
        """重置模型状态"""
        self.F = 0.0
        self.ponding = False
        self.t_ponding = 0.0
    
    def get_state(self) -> Dict[str, float]:
        """获取当前模型状态"""
        return {
            'F': self.F,
            'ponding': self.ponding,
            't_ponding': self.t_ponding
        }
    
    def set_state(self, state: Dict[str, float]):
        """设置模型状态"""
        if 'F' in state:
            self.F = state['F']
        if 'ponding' in state:
            self.ponding = state['ponding']
        if 't_ponding' in state:
            self.t_ponding = state['t_ponding']


def create_default_green_ampt_params(soil_type: str = 'loam') -> Dict[str, float]:
    """
    创建默认的Green-Ampt参数
    
    Parameters
    ----------
    soil_type : str
        土壤类型，可选：
        - 'sand' : 砂土
        - 'loamy_sand' : 壤砂土
        - 'sandy_loam' : 砂壤土
        - 'loam' : 壤土
        - 'silt_loam' : 粉砂壤土
        - 'sandy_clay_loam' : 砂黏壤土
        - 'clay_loam' : 黏壤土
        - 'silty_clay_loam' : 粉砂黏壤土
        - 'clay' : 黏土
    
    Returns
    -------
    params : dict
        默认参数
    
    References
    ----------
    Rawls, W.J., et al. (1983). Green-Ampt Infiltration Parameters from Soils Data.
    Journal of Hydraulic Engineering, 109(1), 62-70.
    """
    # 典型土壤参数（来自Rawls et al., 1983）
    soil_params = {
        'sand': {
            'K': 117.8,      # mm/h
            'psi': 49.5,     # mm
            'theta_s': 0.437,
            'theta_i': 0.15
        },
        'loamy_sand': {
            'K': 29.9,
            'psi': 61.3,
            'theta_s': 0.437,
            'theta_i': 0.15
        },
        'sandy_loam': {
            'K': 10.9,
            'psi': 110.1,
            'theta_s': 0.453,
            'theta_i': 0.15
        },
        'loam': {
            'K': 3.4,
            'psi': 88.9,
            'theta_s': 0.463,
            'theta_i': 0.20
        },
        'silt_loam': {
            'K': 6.5,
            'psi': 166.8,
            'theta_s': 0.501,
            'theta_i': 0.25
        },
        'sandy_clay_loam': {
            'K': 1.5,
            'psi': 218.5,
            'theta_s': 0.398,
            'theta_i': 0.20
        },
        'clay_loam': {
            'K': 1.0,
            'psi': 208.8,
            'theta_s': 0.464,
            'theta_i': 0.25
        },
        'silty_clay_loam': {
            'K': 1.0,
            'psi': 273.0,
            'theta_s': 0.471,
            'theta_i': 0.25
        },
        'clay': {
            'K': 0.3,
            'psi': 316.3,
            'theta_s': 0.475,
            'theta_i': 0.30
        }
    }
    
    if soil_type not in soil_params:
        raise ValueError(f"未知的土壤类型: {soil_type}. "
                        f"可选: {list(soil_params.keys())}")
    
    params = soil_params[soil_type].copy()
    params['dt'] = 0.1  # 默认时间步长 0.1h = 6分钟
    
    return params


if __name__ == '__main__':
    # 简单测试
    print("Green-Ampt模型测试")
    print("=" * 50)
    
    # 创建模型（壤土）
    params = create_default_green_ampt_params('loam')
    print(f"土壤类型: 壤土")
    print(f"参数: K={params['K']:.1f} mm/h, psi={params['psi']:.1f} mm")
    print()
    
    model = GreenAmptModel(params)
    
    # 模拟暴雨
    rainfall = np.array([10, 20, 30, 40, 30, 20, 10, 5, 0, 0])  # mm/h
    print(f"降雨: {rainfall}")
    print()
    
    # 运行模型
    results = model.run(rainfall)
    
    print("结果:")
    print(f"累积入渗: {results['F'][-1]:.2f} mm")
    print(f"累积径流: {np.sum(results['runoff']):.2f} mm")
    print(f"径流系数: {np.sum(results['runoff']) / np.sum(rainfall * params['dt']):.2%}")
