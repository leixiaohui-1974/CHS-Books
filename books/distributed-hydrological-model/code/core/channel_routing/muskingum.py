"""
Muskingum河道洪水演进模型
=======================

Muskingum方法是河道洪水演进的经典方法，基于水量平衡和蓄泄关系。

理论基础
--------
1. 水量平衡方程：
   dS/dt = I(t) - Q(t)
   
2. 蓄泄关系（楔形+棱柱蓄水）：
   S = K[X×I + (1-X)×Q]
   
3. 差分求解：
   Q(t+Δt) = C0×I(t+Δt) + C1×I(t) + C2×Q(t)
   
   其中：
   C0 = (-KX + 0.5Δt) / (K - KX + 0.5Δt)
   C1 = (KX + 0.5Δt) / (K - KX + 0.5Δt)
   C2 = (K - KX - 0.5Δt) / (K - KX + 0.5Δt)

参数说明：
---------
K : 传播时间常数 (h)，表示洪波从河段上游传到下游的时间
X : 蓄量比重系数 (0-0.5)，表示楔形蓄水所占的比重
    - X=0: 水库型（纯棱柱蓄水）
    - X=0.5: 纯楔形蓄水
    - X=0.2-0.3: 典型河道

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Optional
import warnings


class MuskingumChannel:
    """
    Muskingum河道洪水演进模型
    
    Parameters
    ----------
    params : dict
        模型参数：
        - K : float, 传播时间 (h)
        - X : float, 蓄量比重系数 (0-0.5)
        - dt : float, 时间步长 (h)
    
    Examples
    --------
    >>> params = {
    ...     'K': 6.0,    # 6小时
    ...     'X': 0.25,   # 典型河道
    ...     'dt': 1.0    # 1小时
    ... }
    >>> model = MuskingumChannel(params)
    >>> inflow = np.array([100, 200, 300, 250, 150, 80])  # m³/s
    >>> results = model.run(inflow)
    """
    
    def __init__(self, params: Dict[str, float]):
        """初始化Muskingum模型"""
        # 验证参数
        required = ['K', 'X', 'dt']
        for param in required:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        self.K = params['K']    # 传播时间 (h)
        self.X = params['X']    # 蓄量比重系数
        self.dt = params['dt']  # 时间步长 (h)
        
        # 参数检查
        if self.K <= 0:
            raise ValueError("K必须为正")
        if not (0 <= self.X <= 0.5):
            raise ValueError("X必须在0到0.5之间")
        if self.dt <= 0:
            raise ValueError("dt必须为正")
        
        # 检查稳定性条件
        self._check_stability()
        
        # 计算演算系数
        self._compute_coefficients()
        
        # 状态变量
        self.Q = 0.0  # 当前出流 (m³/s)
        self.I_prev = 0.0  # 上一时刻入流
    
    def _check_stability(self):
        """检查数值稳定性"""
        # Muskingum方法的稳定性条件
        # 2*K*X <= dt <= 2*K*(1-X)
        
        lower_bound = 2 * self.K * self.X
        upper_bound = 2 * self.K * (1 - self.X)
        
        if self.dt < lower_bound or self.dt > upper_bound:
            warnings.warn(
                f"时间步长dt={self.dt}h可能导致数值不稳定。\n"
                f"建议范围: {lower_bound:.2f}h <= dt <= {upper_bound:.2f}h",
                UserWarning
            )
    
    def _compute_coefficients(self):
        """计算演算系数"""
        denominator = self.K - self.K * self.X + 0.5 * self.dt
        
        self.C0 = (-self.K * self.X + 0.5 * self.dt) / denominator
        self.C1 = (self.K * self.X + 0.5 * self.dt) / denominator
        self.C2 = (self.K - self.K * self.X - 0.5 * self.dt) / denominator
        
        # 验证系数和为1
        coef_sum = self.C0 + self.C1 + self.C2
        if abs(coef_sum - 1.0) > 1e-6:
            raise ValueError(f"演算系数和不等于1: {coef_sum}")
    
    def run(self, inflow: np.ndarray, 
            initial_outflow: float = 0.0) -> Dict[str, np.ndarray]:
        """
        运行Muskingum模型
        
        Parameters
        ----------
        inflow : ndarray
            入流过程 (m³/s)
        initial_outflow : float
            初始出流 (m³/s)
        
        Returns
        -------
        results : dict
            包含：
            - outflow : ndarray, 出流过程 (m³/s)
            - storage : ndarray, 蓄量过程 (m³)
            - attenuation : float, 削峰率
            - lag : int, 滞时（时段数）
        """
        n = len(inflow)
        
        # 初始化结果
        outflow = np.zeros(n)
        storage = np.zeros(n)
        
        # 初始条件
        self.Q = initial_outflow
        self.I_prev = inflow[0] if n > 0 else 0.0
        
        # 时间步进
        for t in range(n):
            I = inflow[t]
            
            # Muskingum方程
            Q_new = self.C0 * I + self.C1 * self.I_prev + self.C2 * self.Q
            
            # 确保非负
            Q_new = max(Q_new, 0)
            
            # 计算蓄量
            S = self.K * (self.X * I + (1 - self.X) * Q_new) * 3600  # m³
            
            # 保存结果
            outflow[t] = Q_new
            storage[t] = S
            
            # 更新状态
            self.I_prev = I
            self.Q = Q_new
        
        # 计算削峰率和滞时
        peak_inflow = np.max(inflow)
        peak_outflow = np.max(outflow)
        attenuation = (peak_inflow - peak_outflow) / peak_inflow if peak_inflow > 0 else 0
        
        peak_in_time = np.argmax(inflow)
        peak_out_time = np.argmax(outflow)
        lag = peak_out_time - peak_in_time
        
        return {
            'outflow': outflow,
            'storage': storage,
            'attenuation': attenuation,
            'lag': lag,
            'C0': self.C0,
            'C1': self.C1,
            'C2': self.C2
        }
    
    def reset(self):
        """重置模型状态"""
        self.Q = 0.0
        self.I_prev = 0.0
    
    def get_state(self) -> Dict[str, float]:
        """获取当前状态"""
        return {
            'Q': self.Q,
            'I_prev': self.I_prev
        }
    
    def set_state(self, state: Dict[str, float]):
        """设置模型状态"""
        if 'Q' in state:
            self.Q = state['Q']
        if 'I_prev' in state:
            self.I_prev = state['I_prev']


def estimate_muskingum_parameters(inflow: np.ndarray, outflow: np.ndarray,
                                  dt: float) -> Dict[str, float]:
    """
    根据实测入流和出流估算Muskingum参数
    
    使用最小二乘法估算K和X
    
    Parameters
    ----------
    inflow : ndarray
        实测入流过程 (m³/s)
    outflow : ndarray
        实测出流过程 (m³/s)
    dt : float
        时间步长 (h)
    
    Returns
    -------
    params : dict
        包含K和X的估算值
    
    Notes
    -----
    这是简化的参数估计方法，实际应用中可能需要更复杂的优化算法。
    """
    # 简化方法：根据峰值和滞时估算
    peak_in = np.max(inflow)
    peak_out = np.max(outflow)
    
    time_peak_in = np.argmax(inflow) * dt
    time_peak_out = np.argmax(outflow) * dt
    
    # 估算K（约等于滞时）
    K = time_peak_out - time_peak_in
    K = max(K, dt)  # 至少一个时段
    
    # 估算X（根据削峰率）
    attenuation = (peak_in - peak_out) / peak_in
    # 经验公式：attenuation ≈ X / (1 + X)
    X = attenuation / (1 - attenuation) if attenuation < 0.5 else 0.3
    X = np.clip(X, 0, 0.5)
    
    return {
        'K': K,
        'X': X,
        'dt': dt
    }


if __name__ == '__main__':
    # 简单测试
    print("Muskingum模型测试")
    print("=" * 50)
    
    params = {
        'K': 6.0,    # 6小时
        'X': 0.25,   # 典型河道
        'dt': 1.0    # 1小时
    }
    
    print(f"参数:")
    print(f"  K = {params['K']} h")
    print(f"  X = {params['X']}")
    print(f"  dt = {params['dt']} h")
    print()
    
    model = MuskingumChannel(params)
    
    print(f"演算系数:")
    print(f"  C0 = {model.C0:.4f}")
    print(f"  C1 = {model.C1:.4f}")
    print(f"  C2 = {model.C2:.4f}")
    print(f"  Sum = {model.C0 + model.C1 + model.C2:.4f}")
    print()
    
    # 模拟洪水过程（三角形）
    time = np.arange(20)
    inflow = np.zeros(20)
    inflow[2:7] = [50, 100, 200, 150, 80]
    
    print("入流过程:")
    print(f"  峰值: {np.max(inflow):.0f} m³/s")
    print(f"  峰现时刻: {np.argmax(inflow)} h")
    print()
    
    results = model.run(inflow)
    
    print("出流过程:")
    print(f"  峰值: {np.max(results['outflow']):.2f} m³/s")
    print(f"  峰现时刻: {np.argmax(results['outflow'])} h")
    print(f"  削峰率: {results['attenuation']:.2%}")
    print(f"  滞时: {results['lag']} h")
