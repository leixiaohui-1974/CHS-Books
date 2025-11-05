"""
MPPT算法模块
Maximum Power Point Tracking Algorithms

实现多种经典MPPT算法
"""

from typing import Tuple, Dict, List
import numpy as np
from abc import ABC, abstractmethod


class MPPTAlgorithm(ABC):
    """
    MPPT算法基类
    Abstract Base Class for MPPT Algorithms
    """
    
    def __init__(self, name: str = "MPPT"):
        """
        初始化MPPT算法
        
        Parameters:
        -----------
        name : str
            算法名称
        """
        self.name = name
        self.history = []  # 历史记录
        
    @abstractmethod
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        更新算法,返回新的参考电压
        
        Parameters:
        -----------
        voltage : float
            当前电压(V)
        current : float
            当前电流(A)
            
        Returns:
        --------
        float : 新的参考电压(V)
        """
        pass
    
    def reset(self):
        """重置算法"""
        self.history = []


class PerturbAndObserve(MPPTAlgorithm):
    """
    P&O扰动观察法
    Perturb and Observe Algorithm
    
    原理:
    ----
    1. 扰动电压(增加或减少ΔV)
    2. 观察功率变化
    3. 如果功率增加,继续当前方向
    4. 如果功率减少,反转方向
    
    优点: 简单、易实现、不需要PV特性
    缺点: 稳态振荡、响应慢
    """
    
    def __init__(self,
                 step_size: float = 1.0,
                 initial_voltage: float = None,
                 name: str = "P&O"):
        """
        初始化P&O算法
        
        Parameters:
        -----------
        step_size : float
            扰动步长(V)
        initial_voltage : float
            初始电压(V)
        name : str
            算法名称
        """
        super().__init__(name)
        self.step_size = step_size
        self.initial_voltage = initial_voltage
        
        # 内部状态
        self.v_ref = initial_voltage  # 参考电压
        self.p_prev = 0.0             # 上一次功率
        self.v_prev = 0.0             # 上一次电压
        self.direction = 1            # 扰动方向(+1或-1)
        
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        P&O算法更新
        
        Parameters:
        -----------
        voltage : float
            当前电压(V)
        current : float
            当前电流(A)
            
        Returns:
        --------
        float : 新的参考电压(V)
        """
        # 计算当前功率
        power = voltage * current
        
        # 第一次调用,初始化
        if self.v_ref is None:
            self.v_ref = voltage
            self.v_prev = voltage
            self.p_prev = power
            return self.v_ref
        
        # P&O核心逻辑
        dp = power - self.p_prev  # 功率变化
        dv = voltage - self.v_prev  # 电压变化
        
        if dp > 0:
            # 功率增加
            if dv > 0:
                # 电压增加,功率增加 → 继续增加电压
                self.direction = 1
            else:
                # 电压减少,功率增加 → 继续减少电压
                self.direction = -1
        else:
            # 功率减少
            if dv > 0:
                # 电压增加,功率减少 → 反转,减少电压
                self.direction = -1
            else:
                # 电压减少,功率减少 → 反转,增加电压
                self.direction = 1
        
        # 更新参考电压
        self.v_ref = voltage + self.direction * self.step_size
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': power,
            'v_ref': self.v_ref,
            'direction': self.direction
        })
        
        # 更新上一次值
        self.v_prev = voltage
        self.p_prev = power
        
        return self.v_ref
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.v_ref = self.initial_voltage
        self.p_prev = 0.0
        self.v_prev = 0.0
        self.direction = 1


class AdaptivePO(PerturbAndObserve):
    """
    自适应P&O算法
    Adaptive Perturb and Observe
    
    改进:
    ----
    - 根据功率变化调整步长
    - 接近MPP时减小步长
    - 远离MPP时增大步长
    """
    
    def __init__(self,
                 step_size_min: float = 0.1,
                 step_size_max: float = 5.0,
                 initial_voltage: float = None,
                 name: str = "Adaptive P&O"):
        """
        初始化自适应P&O
        
        Parameters:
        -----------
        step_size_min : float
            最小步长(V)
        step_size_max : float
            最大步长(V)
        initial_voltage : float
            初始电压(V)
        name : str
            算法名称
        """
        super().__init__(
            step_size=(step_size_min + step_size_max) / 2,
            initial_voltage=initial_voltage,
            name=name
        )
        self.step_size_min = step_size_min
        self.step_size_max = step_size_max
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        自适应P&O更新
        
        根据|dP/dV|调整步长:
        - |dP/dV|大 → 远离MPP → 增大步长
        - |dP/dV|小 → 接近MPP → 减小步长
        """
        power = voltage * current
        
        # 第一次调用
        if self.v_ref is None:
            self.v_ref = voltage
            self.v_prev = voltage
            self.p_prev = power
            return self.v_ref
        
        # 计算功率变化率
        dp = power - self.p_prev
        dv = voltage - self.v_prev
        
        if abs(dv) > 1e-6:
            dpdv = abs(dp / dv)  # |dP/dV|
            
            # 归一化到[0,1]
            dpdv_norm = min(dpdv / 10.0, 1.0)  # 假设最大dP/dV=10
            
            # 自适应步长: 远离MPP时大,接近时小
            self.step_size = self.step_size_min + \
                           (self.step_size_max - self.step_size_min) * dpdv_norm
        
        # 调用父类P&O逻辑
        return super().update(voltage, current, **kwargs)


class MPPTController:
    """
    MPPT控制器
    MPPT Controller
    
    整合MPPT算法与PV系统
    """
    
    def __init__(self,
                 algorithm: MPPTAlgorithm,
                 v_min: float = 0.0,
                 v_max: float = 100.0):
        """
        初始化MPPT控制器
        
        Parameters:
        -----------
        algorithm : MPPTAlgorithm
            MPPT算法
        v_min, v_max : float
            电压限制(V)
        """
        self.algorithm = algorithm
        self.v_min = v_min
        self.v_max = v_max
        
        # 性能统计
        self.tracking_history = []
        
    def step(self, pv_voltage: float, pv_current: float) -> float:
        """
        执行一步MPPT
        
        Parameters:
        -----------
        pv_voltage : float
            PV电压(V)
        pv_current : float
            PV电流(A)
            
        Returns:
        --------
        float : 参考电压(V)
        """
        # 调用算法
        v_ref = self.algorithm.update(pv_voltage, pv_current)
        
        # 限幅
        v_ref = np.clip(v_ref, self.v_min, self.v_max)
        
        # 记录
        power = pv_voltage * pv_current
        self.tracking_history.append({
            'v': pv_voltage,
            'i': pv_current,
            'p': power,
            'v_ref': v_ref
        })
        
        return v_ref
    
    def evaluate_performance(self, p_mpp: float) -> Dict:
        """
        评估MPPT性能
        
        Parameters:
        -----------
        p_mpp : float
            真实最大功率(W)
            
        Returns:
        --------
        Dict : 性能指标
        """
        if not self.tracking_history:
            return {}
        
        powers = np.array([h['p'] for h in self.tracking_history])
        
        # 平均功率
        p_avg = np.mean(powers)
        
        # 跟踪效率
        efficiency = (p_avg / p_mpp * 100) if p_mpp > 0 else 0
        
        # 稳态振荡(最后10%数据的标准差)
        n_steady = max(1, len(powers) // 10)
        p_steady = powers[-n_steady:]
        oscillation = np.std(p_steady)
        
        # 响应时间(达到95% Pmpp的时间)
        threshold = 0.95 * p_mpp
        settling_idx = np.where(powers >= threshold)[0]
        settling_time = settling_idx[0] if len(settling_idx) > 0 else len(powers)
        
        return {
            'p_avg': p_avg,
            'p_max': np.max(powers),
            'p_min': np.min(powers),
            'efficiency': efficiency,
            'oscillation': oscillation,
            'settling_time': settling_time,
            'num_steps': len(powers)
        }
    
    def reset(self):
        """重置控制器"""
        self.algorithm.reset()
        self.tracking_history = []
