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


class IncrementalConductance(MPPTAlgorithm):
    """
    增量电导法
    Incremental Conductance Algorithm
    
    原理:
    ----
    基于 dP/dV = 0 在MPP点
    
    因为 P = V×I, 所以:
    dP/dV = I + V×(dI/dV) = 0
    
    即: dI/dV = -I/V (MPP条件)
    
    判断逻辑:
    - dI/dV > -I/V → 左侧,增加V
    - dI/dV < -I/V → 右侧,减少V
    - dI/dV = -I/V → MPP,保持V
    
    优点: 精度高、无稳态振荡、快速响应
    缺点: 计算复杂、对噪声敏感
    """
    
    def __init__(self,
                 step_size: float = 1.0,
                 initial_voltage: float = None,
                 threshold: float = 0.01,
                 name: str = "INC"):
        """
        初始化INC算法
        
        Parameters:
        -----------
        step_size : float
            步长(V)
        initial_voltage : float
            初始电压(V)
        threshold : float
            判断阈值(A/V)
        name : str
            算法名称
        """
        super().__init__(name)
        self.step_size = step_size
        self.initial_voltage = initial_voltage
        self.threshold = threshold
        
        # 内部状态
        self.v_ref = initial_voltage
        self.v_prev = 0.0
        self.i_prev = 0.0
        
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        INC算法更新
        
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
        # 第一次调用,初始化
        if self.v_ref is None:
            self.v_ref = voltage
            self.v_prev = voltage
            self.i_prev = current
            return self.v_ref
        
        # 计算增量
        dV = voltage - self.v_prev
        dI = current - self.i_prev
        
        # INC核心逻辑
        if abs(dV) < 1e-6:
            # 电压无变化
            if abs(dI) < self.threshold:
                # 电流也无变化 → MPP
                pass  # 保持当前电压
            elif dI > 0:
                # 电流增加 → 增加电压
                self.v_ref = voltage + self.step_size
            else:
                # 电流减少 → 减少电压
                self.v_ref = voltage - self.step_size
        else:
            # 电压有变化,计算增量电导
            dIdV = dI / dV  # dI/dV
            conductance = -current / voltage  # -I/V
            
            if abs(dIdV - conductance) < self.threshold:
                # dI/dV ≈ -I/V → MPP
                pass  # 保持当前电压
            elif dIdV > conductance:
                # dI/dV > -I/V → 左侧
                self.v_ref = voltage + self.step_size
            else:
                # dI/dV < -I/V → 右侧
                self.v_ref = voltage - self.step_size
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': voltage * current,
            'v_ref': self.v_ref,
            'dV': dV,
            'dI': dI
        })
        
        # 更新上一次值
        self.v_prev = voltage
        self.i_prev = current
        
        return self.v_ref
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.v_ref = self.initial_voltage
        self.v_prev = 0.0
        self.i_prev = 0.0


class ModifiedINC(IncrementalConductance):
    """
    改进型增量电导法
    Modified Incremental Conductance
    
    改进:
    ----
    - 变步长策略
    - 死区设置
    - 滤波处理
    """
    
    def __init__(self,
                 step_size_min: float = 0.1,
                 step_size_max: float = 5.0,
                 initial_voltage: float = None,
                 threshold: float = 0.01,
                 deadband: float = 0.005,
                 name: str = "Modified INC"):
        """
        初始化改进型INC
        
        Parameters:
        -----------
        step_size_min : float
            最小步长(V)
        step_size_max : float
            最大步长(V)
        initial_voltage : float
            初始电压(V)
        threshold : float
            判断阈值
        deadband : float
            死区范围
        name : str
            算法名称
        """
        super().__init__(
            step_size=(step_size_min + step_size_max) / 2,
            initial_voltage=initial_voltage,
            threshold=threshold,
            name=name
        )
        self.step_size_min = step_size_min
        self.step_size_max = step_size_max
        self.deadband = deadband
        
        # 滤波参数
        self.alpha = 0.8
        self.v_filtered = 0.0
        self.i_filtered = 0.0
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        改进型INC更新
        
        添加滤波、变步长、死区
        """
        # 第一次调用
        if self.v_ref is None:
            self.v_ref = voltage
            self.v_prev = voltage
            self.i_prev = current
            self.v_filtered = voltage
            self.i_filtered = current
            return self.v_ref
        
        # 滤波
        self.v_filtered = self.alpha * self.v_filtered + (1 - self.alpha) * voltage
        self.i_filtered = self.alpha * self.i_filtered + (1 - self.alpha) * current
        
        # 计算增量
        dV = self.v_filtered - self.v_prev
        dI = self.i_filtered - self.i_prev
        
        # 死区判断
        if abs(dV) < self.deadband and abs(dI) < self.deadband:
            # 在死区内,保持不变
            self.history.append({
                'v': voltage,
                'i': current,
                'p': voltage * current,
                'v_ref': self.v_ref,
                'dV': dV,
                'dI': dI
            })
            return self.v_ref
        
        # INC逻辑(使用滤波后的值)
        if abs(dV) > 1e-6:
            dIdV = dI / dV
            conductance = -self.i_filtered / self.v_filtered
            
            error = abs(dIdV - conductance)
            
            # 变步长: 误差大时步长大
            error_norm = min(error / 1.0, 1.0)
            self.step_size = self.step_size_min + \
                           (self.step_size_max - self.step_size_min) * error_norm
            
            if abs(error) < self.threshold:
                pass  # MPP
            elif dIdV > conductance:
                self.v_ref = voltage + self.step_size
            else:
                self.v_ref = voltage - self.step_size
        
        # 记录
        self.history.append({
            'v': voltage,
            'i': current,
            'p': voltage * current,
            'v_ref': self.v_ref,
            'dV': dV,
            'dI': dI,
            'step_size': self.step_size
        })
        
        # 更新
        self.v_prev = self.v_filtered
        self.i_prev = self.i_filtered
        
        return self.v_ref


class ConstantVoltage(MPPTAlgorithm):
    """
    恒电压法
    Constant Voltage Algorithm
    
    原理:
    ----
    基于经验法则: MPP电压通常在 0.76-0.8 × Voc
    
    步骤:
    1. 测量或估算Voc
    2. 设置Vref = k × Voc (k=0.76-0.8)
    3. 控制工作在Vref
    
    优点: 极简单、快速、成本低
    缺点: 精度低、不能跟踪变化
    """
    
    def __init__(self,
                 voltage_ratio: float = 0.76,
                 voc: float = None,
                 update_voc: bool = False,
                 voc_update_interval: int = 100,
                 name: str = "CV"):
        """
        初始化CV算法
        
        Parameters:
        -----------
        voltage_ratio : float
            MPP电压比例(0.76-0.8)
        voc : float
            开路电压(V), None则需要测量
        update_voc : bool
            是否定期更新Voc
        voc_update_interval : int
            Voc更新间隔(步数)
        name : str
            算法名称
        """
        super().__init__(name)
        self.voltage_ratio = voltage_ratio
        self.voc = voc
        self.update_voc = update_voc
        self.voc_update_interval = voc_update_interval
        
        # 内部状态
        self.v_ref = None
        self.step_count = 0
        self.voc_measured = False
        
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        CV算法更新
        
        Parameters:
        -----------
        voltage : float
            当前电压(V)
        current : float
            当前电流(A)
            
        Returns:
        --------
        float : 参考电压(V)
        """
        self.step_count += 1
        
        # 第一次调用或需要测量Voc
        if self.v_ref is None or (not self.voc_measured and self.voc is None):
            # 如果没有Voc,使用当前电压估算
            if self.voc is None:
                # 简化: 假设当前在50%左右,则Voc约为2倍
                self.voc = voltage / 0.5
                self.voc_measured = True
            
            self.v_ref = self.voltage_ratio * self.voc
        
        # 定期更新Voc(如果启用)
        if self.update_voc and self.step_count % self.voc_update_interval == 0:
            # 简化更新: 根据当前功率估算
            # 实际应用中需要短暂断开负载测量真实Voc
            if current < 0.1:  # 接近开路
                self.voc = voltage
            else:
                # 根据当前工作点估算Voc
                # Voc ≈ V + I×Rs (简化)
                self.voc = voltage * 1.3  # 粗略估算
            
            self.v_ref = self.voltage_ratio * self.voc
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': voltage * current,
            'v_ref': self.v_ref,
            'voc': self.voc
        })
        
        return self.v_ref
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.v_ref = None
        self.step_count = 0
        self.voc_measured = False
    
    def set_voc(self, voc: float):
        """
        设置Voc值
        
        Parameters:
        -----------
        voc : float
            开路电压(V)
        """
        self.voc = voc
        self.v_ref = self.voltage_ratio * voc
        self.voc_measured = True


class ImprovedCV(ConstantVoltage):
    """
    改进型恒电压法
    Improved Constant Voltage
    
    改进:
    ----
    - 根据温度/辐照度调整k值
    - 周期性Voc测量
    - 与P&O结合
    """
    
    def __init__(self,
                 voltage_ratio: float = 0.76,
                 voc: float = None,
                 temp_coef: float = -0.003,
                 name: str = "Improved CV"):
        """
        初始化改进型CV
        
        Parameters:
        -----------
        voltage_ratio : float
            基准电压比例
        voc : float
            开路电压
        temp_coef : float
            温度系数(/°C)
        name : str
            算法名称
        """
        super().__init__(
            voltage_ratio=voltage_ratio,
            voc=voc,
            update_voc=True,
            voc_update_interval=50,
            name=name
        )
        self.temp_coef = temp_coef
        self.base_temp = 25.0  # 基准温度
    
    def update(self, voltage: float, current: float, 
              temperature: float = 25.0, **kwargs) -> float:
        """
        改进型CV更新
        
        添加温度补偿
        
        Parameters:
        -----------
        voltage : float
            当前电压
        current : float
            当前电流
        temperature : float
            温度(°C)
        """
        # 调用父类更新
        v_ref_base = super().update(voltage, current, **kwargs)
        
        # 温度补偿
        delta_t = temperature - self.base_temp
        v_ref_compensated = v_ref_base * (1 + self.temp_coef * delta_t)
        
        # 更新参考电压
        self.v_ref = v_ref_compensated
        
        # 更新历史记录
        if self.history:
            self.history[-1]['v_ref'] = v_ref_compensated
            self.history[-1]['temperature'] = temperature
        
        return v_ref_compensated


class FuzzyLogicMPPT(MPPTAlgorithm):
    """
    模糊逻辑MPPT
    Fuzzy Logic MPPT
    
    原理:
    ----
    使用模糊推理系统(FIS)根据dP和dV决定电压调整
    
    输入:
    - E = dP/dI (功率变化率)
    - CE = d(E)/dt (功率变化率的变化)
    
    输出:
    - ΔV (电压调整量)
    
    优点: 鲁棒性强、响应快、不需要精确模型
    缺点: 规则设计复杂、计算量较大
    """
    
    def __init__(self,
                 step_size_max: float = 5.0,
                 initial_voltage: float = None,
                 name: str = "Fuzzy"):
        """
        初始化模糊逻辑MPPT
        
        Parameters:
        -----------
        step_size_max : float
            最大步长(V)
        initial_voltage : float
            初始电压(V)
        name : str
            算法名称
        """
        super().__init__(name)
        self.step_size_max = step_size_max
        self.initial_voltage = initial_voltage
        
        # 内部状态
        self.v_ref = initial_voltage
        self.p_prev = 0.0
        self.e_prev = 0.0  # E的前值
        
        # 定义模糊集合
        self._define_fuzzy_sets()
        
        # 定义规则库
        self._define_rules()
    
    def _define_fuzzy_sets(self):
        """定义模糊集合的隶属度函数"""
        # 输入变量E (功率变化率)的模糊集: NB, NS, ZE, PS, PB
        # 输入变量CE (E的变化率)的模糊集: NB, NS, ZE, PS, PB
        # 输出变量ΔV的模糊集: NB, NS, ZE, PS, PB
        
        # 使用三角形/梯形隶属度函数
        # 参数: [left, peak_left, peak_right, right]
        self.mf_e = {
            'NB': [-1.0, -1.0, -0.5, 0.0],   # Negative Big
            'NS': [-0.5, -0.25, 0.0, 0.25],  # Negative Small
            'ZE': [-0.25, 0.0, 0.0, 0.25],   # Zero
            'PS': [-0.25, 0.0, 0.25, 0.5],   # Positive Small
            'PB': [0.0, 0.5, 1.0, 1.0]       # Positive Big
        }
        
        self.mf_ce = {
            'NB': [-1.0, -1.0, -0.5, 0.0],
            'NS': [-0.5, -0.25, 0.0, 0.25],
            'ZE': [-0.25, 0.0, 0.0, 0.25],
            'PS': [-0.25, 0.0, 0.25, 0.5],
            'PB': [0.0, 0.5, 1.0, 1.0]
        }
        
        self.mf_dv = {
            'NB': [-1.0, -1.0, -0.5, 0.0],
            'NS': [-0.5, -0.25, 0.0, 0.25],
            'ZE': [-0.25, 0.0, 0.0, 0.25],
            'PS': [-0.25, 0.0, 0.25, 0.5],
            'PB': [0.0, 0.5, 1.0, 1.0]
        }
    
    def _define_rules(self):
        """定义模糊规则库"""
        # 规则格式: (E, CE) -> ΔV
        # 25条规则 (5x5)
        self.rules = {
            ('NB', 'NB'): 'PB',  # E负大, CE负大 -> 大幅增加电压
            ('NB', 'NS'): 'PB',
            ('NB', 'ZE'): 'PS',
            ('NB', 'PS'): 'PS',
            ('NB', 'PB'): 'ZE',
            
            ('NS', 'NB'): 'PB',
            ('NS', 'NS'): 'PS',
            ('NS', 'ZE'): 'PS',
            ('NS', 'PS'): 'ZE',
            ('NS', 'PB'): 'ZE',
            
            ('ZE', 'NB'): 'PS',
            ('ZE', 'NS'): 'PS',
            ('ZE', 'ZE'): 'ZE',  # E和CE都为零 -> 不调整
            ('ZE', 'PS'): 'NS',
            ('ZE', 'PB'): 'NS',
            
            ('PS', 'NB'): 'ZE',
            ('PS', 'NS'): 'ZE',
            ('PS', 'ZE'): 'NS',
            ('PS', 'PS'): 'NS',
            ('PS', 'PB'): 'NB',
            
            ('PB', 'NB'): 'ZE',
            ('PB', 'NS'): 'NS',
            ('PB', 'ZE'): 'NS',
            ('PB', 'PS'): 'NB',
            ('PB', 'PB'): 'NB',
        }
    
    def _membership(self, x: float, mf_params: list) -> float:
        """
        计算隶属度(梯形隶属函数)
        
        Parameters:
        -----------
        x : float
            输入值
        mf_params : list
            [left, peak_left, peak_right, right]
        
        Returns:
        --------
        float : 隶属度 [0, 1]
        """
        a, b, c, d = mf_params
        
        if x <= a or x >= d:
            return 0.0
        elif b <= x <= c:
            return 1.0
        elif a < x < b:
            return (x - a) / (b - a)
        else:  # c < x < d
            return (d - x) / (d - c)
    
    def _fuzzify(self, e: float, ce: float) -> dict:
        """
        模糊化输入
        
        Parameters:
        -----------
        e : float
            归一化的E
        ce : float
            归一化的CE
        
        Returns:
        --------
        dict : 各模糊集的隶属度
        """
        # E的模糊化
        e_fuzzy = {}
        for label, params in self.mf_e.items():
            e_fuzzy[label] = self._membership(e, params)
        
        # CE的模糊化
        ce_fuzzy = {}
        for label, params in self.mf_ce.items():
            ce_fuzzy[label] = self._membership(ce, params)
        
        return {'E': e_fuzzy, 'CE': ce_fuzzy}
    
    def _inference(self, fuzzy_inputs: dict) -> dict:
        """
        模糊推理
        
        Parameters:
        -----------
        fuzzy_inputs : dict
            模糊化的输入
        
        Returns:
        --------
        dict : 各输出模糊集的激活度
        """
        e_fuzzy = fuzzy_inputs['E']
        ce_fuzzy = fuzzy_inputs['CE']
        
        # 输出模糊集的累积激活度
        output_activation = {'NB': 0.0, 'NS': 0.0, 'ZE': 0.0, 'PS': 0.0, 'PB': 0.0}
        
        # 遍历所有规则
        for (e_label, ce_label), dv_label in self.rules.items():
            # 计算规则激活度 (AND操作用最小值)
            activation = min(e_fuzzy[e_label], ce_fuzzy[ce_label])
            
            # 累积到输出模糊集
            output_activation[dv_label] = max(output_activation[dv_label], activation)
        
        return output_activation
    
    def _defuzzify(self, output_activation: dict) -> float:
        """
        去模糊化(重心法)
        
        Parameters:
        -----------
        output_activation : dict
            输出模糊集的激活度
        
        Returns:
        --------
        float : 清晰输出值 [-1, 1]
        """
        # 计算每个模糊集的中心
        centers = {
            'NB': -0.75,
            'NS': -0.125,
            'ZE': 0.0,
            'PS': 0.125,
            'PB': 0.75
        }
        
        numerator = 0.0
        denominator = 0.0
        
        for label, activation in output_activation.items():
            numerator += activation * centers[label]
            denominator += activation
        
        if denominator < 1e-10:
            return 0.0
        
        return numerator / denominator
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        模糊逻辑MPPT更新
        
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
            self.p_prev = power
            self.e_prev = 0.0
            return self.v_ref
        
        # 计算E (功率变化率)
        dp = power - self.p_prev
        e = dp  # 简化: 直接用dp作为E
        
        # 计算CE (E的变化率)
        ce = e - self.e_prev
        
        # 归一化 E 和 CE 到 [-1, 1]
        e_norm = np.tanh(e / 10.0)  # 使用tanh归一化
        ce_norm = np.tanh(ce / 5.0)
        
        # 模糊推理
        fuzzy_inputs = self._fuzzify(e_norm, ce_norm)
        output_activation = self._inference(fuzzy_inputs)
        dv_norm = self._defuzzify(output_activation)
        
        # 反归一化到实际电压调整量
        dv = dv_norm * self.step_size_max
        
        # 更新参考电压
        self.v_ref = voltage + dv
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': power,
            'v_ref': self.v_ref,
            'e': e,
            'ce': ce,
            'dv': dv
        })
        
        # 更新状态
        self.p_prev = power
        self.e_prev = e
        
        return self.v_ref
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.v_ref = self.initial_voltage
        self.p_prev = 0.0
        self.e_prev = 0.0


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
