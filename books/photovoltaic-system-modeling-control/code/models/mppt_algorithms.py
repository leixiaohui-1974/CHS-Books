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


class ParticleSwarmMPPT(MPPTAlgorithm):
    """
    粒子群优化MPPT
    Particle Swarm Optimization MPPT
    
    原理:
    ----
    模拟鸟群觅食行为,通过粒子协作搜索全局最优解
    
    粒子: 代表可能的工作电压
    适应度: 当前电压下的输出功率
    
    更新方程:
    v_i(k+1) = w*v_i(k) + c1*r1*(pbest_i - x_i(k)) + c2*r2*(gbest - x_i(k))
    x_i(k+1) = x_i(k) + v_i(k+1)
    
    优点: 全局搜索能力强、适合多峰、收敛快
    缺点: 计算量较大、参数敏感
    """
    
    def __init__(self,
                 n_particles: int = 10,
                 v_min: float = 0.0,
                 v_max: float = 40.0,
                 w: float = 0.7,
                 c1: float = 1.5,
                 c2: float = 1.5,
                 max_iterations: int = 20,
                 tolerance: float = 0.1,
                 name: str = "PSO"):
        """
        初始化PSO MPPT
        
        Parameters:
        -----------
        n_particles : int
            粒子数量
        v_min : float
            电压搜索下限(V)
        v_max : float
            电压搜索上限(V)
        w : float
            惯性权重
        c1 : float
            个体学习因子
        c2 : float
            社会学习因子
        max_iterations : int
            最大迭代次数
        tolerance : float
            收敛容差(W)
        name : str
            算法名称
        """
        super().__init__(name)
        self.n_particles = n_particles
        self.v_min = v_min
        self.v_max = v_max
        self.w = w  # 惯性权重
        self.c1 = c1  # 个体学习因子
        self.c2 = c2  # 社会学习因子
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # 粒子状态
        self.positions = None  # 粒子位置(电压)
        self.velocities = None  # 粒子速度
        self.pbest_positions = None  # 个体最优位置
        self.pbest_fitness = None  # 个体最优适应度
        self.gbest_position = None  # 全局最优位置
        self.gbest_fitness = -np.inf  # 全局最优适应度
        
        # 控制变量
        self.v_ref = (v_min + v_max) / 2.0  # 参考电压
        self.iteration = 0
        self.converged = False
        self.pv_module = None  # PV组件引用(用于适应度计算)
        
        # 初始化粒子群
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """初始化粒子群"""
        # 随机初始化位置
        self.positions = np.random.uniform(
            self.v_min, self.v_max, self.n_particles
        )
        
        # 初始化速度(10%的搜索空间)
        v_range = (self.v_max - self.v_min) * 0.1
        self.velocities = np.random.uniform(
            -v_range, v_range, self.n_particles
        )
        
        # 初始化个体最优
        self.pbest_positions = self.positions.copy()
        self.pbest_fitness = np.full(self.n_particles, -np.inf)
        
        # 初始化全局最优
        self.gbest_position = self.positions[0]
        self.gbest_fitness = -np.inf
        
        self.iteration = 0
        self.converged = False
    
    def set_pv_module(self, pv_module):
        """
        设置PV组件引用
        
        Parameters:
        -----------
        pv_module : PVModule
            光伏组件对象
        """
        self.pv_module = pv_module
    
    def _evaluate_fitness(self, voltage: float, current: float = None) -> float:
        """
        评估适应度(功率)
        
        Parameters:
        -----------
        voltage : float
            电压(V)
        current : float, optional
            电流(A), 如果提供则直接使用
            
        Returns:
        --------
        float : 适应度值(功率W)
        """
        if current is not None:
            # 使用实测电流
            return voltage * current
        elif self.pv_module is not None:
            # 使用模型计算
            i = self.pv_module.calculate_current(voltage)
            return voltage * i
        else:
            # 无法计算,返回0
            return 0.0
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        更新PSO算法
        
        Parameters:
        -----------
        voltage : float
            当前电压(V) - 仅用于记录
        current : float
            当前电流(A) - 用于适应度计算
            
        Returns:
        --------
        float : 新的参考电压(V)
        """
        # 如果已收敛,直接返回全局最优
        if self.converged:
            return self.gbest_position
        
        # 评估所有粒子的适应度
        for i in range(self.n_particles):
            v = self.positions[i]
            # 使用模型计算每个粒子位置的适应度（不使用current）
            fitness = self._evaluate_fitness(v)
            
            # 更新个体最优
            if fitness > self.pbest_fitness[i]:
                self.pbest_fitness[i] = fitness
                self.pbest_positions[i] = v
            
            # 更新全局最优
            if fitness > self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = v
        
        # 更新粒子速度和位置
        for i in range(self.n_particles):
            # 随机因子
            r1 = np.random.random()
            r2 = np.random.random()
            
            # 速度更新
            cognitive = self.c1 * r1 * (self.pbest_positions[i] - self.positions[i])
            social = self.c2 * r2 * (self.gbest_position - self.positions[i])
            self.velocities[i] = self.w * self.velocities[i] + cognitive + social
            
            # 速度限制(防止过大)
            v_max_speed = (self.v_max - self.v_min) * 0.2
            self.velocities[i] = np.clip(self.velocities[i], -v_max_speed, v_max_speed)
            
            # 位置更新
            self.positions[i] = self.positions[i] + self.velocities[i]
            
            # 边界处理
            if self.positions[i] < self.v_min:
                self.positions[i] = self.v_min
                self.velocities[i] = 0  # 碰壁后速度归零
            elif self.positions[i] > self.v_max:
                self.positions[i] = self.v_max
                self.velocities[i] = 0
        
        # 更新迭代计数
        self.iteration += 1
        
        # 检查收敛
        if self.iteration >= self.max_iterations:
            self.converged = True
        else:
            # 检查功率变化
            fitness_std = np.std(self.pbest_fitness)
            if fitness_std < self.tolerance:
                self.converged = True
        
        # 更新参考电压为全局最优
        self.v_ref = self.gbest_position
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': voltage * current,
            'v_ref': self.v_ref,
            'iteration': self.iteration,
            'gbest_fitness': self.gbest_fitness,
            'converged': self.converged
        })
        
        return self.v_ref
    
    def get_swarm_state(self) -> dict:
        """
        获取粒子群当前状态
        
        Returns:
        --------
        dict : 粒子群状态信息
        """
        return {
            'positions': self.positions.copy(),
            'velocities': self.velocities.copy(),
            'pbest_positions': self.pbest_positions.copy(),
            'pbest_fitness': self.pbest_fitness.copy(),
            'gbest_position': self.gbest_position,
            'gbest_fitness': self.gbest_fitness,
            'iteration': self.iteration,
            'converged': self.converged
        }
    
    def reset(self):
        """重置算法"""
        super().reset()
        self._initialize_swarm()
        self.v_ref = (self.v_min + self.v_max) / 2.0
        self.gbest_fitness = -np.inf


class MultiPeakDetector:
    """
    多峰检测器
    Multi-Peak Detector
    
    用于检测P-V曲线上的多个功率峰值
    """
    
    def __init__(self, pv_module, n_scan_points: int = 50):
        """
        初始化多峰检测器
        
        Parameters:
        -----------
        pv_module : PVModule
            光伏组件对象
        n_scan_points : int
            扫描点数
        """
        self.pv_module = pv_module
        self.n_scan_points = n_scan_points
    
    def scan_pv_curve(self) -> tuple:
        """
        扫描P-V曲线
        
        Returns:
        --------
        tuple : (voltages, powers)
        """
        v_min = 0.0
        v_max = self.pv_module.Voc
        
        voltages = np.linspace(v_min, v_max, self.n_scan_points)
        powers = []
        
        for v in voltages:
            i = self.pv_module.calculate_current(v)
            powers.append(v * i)
        
        return voltages, np.array(powers)
    
    def detect_peaks(self, voltages: np.ndarray, powers: np.ndarray,
                    min_prominence: float = 1.0) -> list:
        """
        检测功率峰值
        
        Parameters:
        -----------
        voltages : np.ndarray
            电压数组
        powers : np.ndarray
            功率数组
        min_prominence : float
            最小峰值突出度(W)
            
        Returns:
        --------
        list : 峰值信息列表 [{'voltage': v, 'power': p, 'prominence': prom}, ...]
        """
        peaks = []
        n = len(powers)
        
        # 简单的峰值检测：比左右邻居都大
        for i in range(1, n - 1):
            if powers[i] > powers[i-1] and powers[i] > powers[i+1]:
                # 计算突出度（与左右最低点的差值）
                left_min = np.min(powers[max(0, i-5):i])
                right_min = np.min(powers[i+1:min(n, i+6)])
                prominence = powers[i] - max(left_min, right_min)
                
                if prominence >= min_prominence:
                    peaks.append({
                        'voltage': voltages[i],
                        'power': powers[i],
                        'prominence': prominence,
                        'index': i
                    })
        
        # 按功率降序排序
        peaks.sort(key=lambda x: x['power'], reverse=True)
        
        return peaks
    
    def find_global_mpp(self) -> dict:
        """
        找到全局MPP
        
        Returns:
        --------
        dict : {'voltage': v, 'power': p}
        """
        voltages, powers = self.scan_pv_curve()
        
        if len(powers) == 0:
            return {'voltage': 0, 'power': 0}
        
        max_idx = np.argmax(powers)
        
        return {
            'voltage': voltages[max_idx],
            'power': powers[max_idx]
        }


class GlobalScanMPPT(MPPTAlgorithm):
    """
    全局扫描MPPT
    Global Scan MPPT
    
    原理:
    ----
    定期进行全局扫描，找到全局最大功率点
    
    策略:
    1. 粗扫描: 快速扫描整个电压范围
    2. 峰值检测: 识别所有功率峰值
    3. 精细跟踪: 在全局MPP附近用传统算法跟踪
    4. 定期重扫: 应对环境变化
    
    优点: 能可靠找到全局MPP
    缺点: 扫描期间功率损失
    """
    
    def __init__(self,
                 pv_module,
                 scan_interval: int = 100,
                 n_scan_points: int = 30,
                 local_algorithm=None,
                 name: str = "GlobalScan"):
        """
        初始化全局扫描MPPT
        
        Parameters:
        -----------
        pv_module : PVModule
            光伏组件对象
        scan_interval : int
            扫描间隔(步数)
        n_scan_points : int
            扫描点数
        local_algorithm : MPPTAlgorithm
            局部跟踪算法（默认P&O）
        name : str
            算法名称
        """
        super().__init__(name)
        self.pv_module = pv_module
        self.scan_interval = scan_interval
        self.n_scan_points = n_scan_points
        
        # 多峰检测器
        self.detector = MultiPeakDetector(pv_module, n_scan_points)
        
        # 局部跟踪算法
        if local_algorithm is None:
            from code.models.mppt_algorithms import PerturbAndObserve
            self.local_algorithm = PerturbAndObserve(step_size=1.0)
        else:
            self.local_algorithm = local_algorithm
        
        # 控制变量
        self.v_ref = (pv_module.Voc / 2.0) if pv_module else 20.0
        self.step_count = 0
        self.is_scanning = False
        self.scan_complete = False
        self.global_mpp = None
    
    def _perform_scan(self):
        """执行全局扫描"""
        self.global_mpp = self.detector.find_global_mpp()
        self.v_ref = self.global_mpp['voltage']
        self.scan_complete = True
        self.is_scanning = False
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        更新算法
        
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
        self.step_count += 1
        
        # 检查是否需要扫描
        if self.step_count % self.scan_interval == 0:
            self.is_scanning = True
            self._perform_scan()
        
        # 扫描后或正常跟踪
        if self.scan_complete:
            # 使用局部算法跟踪
            self.v_ref = self.local_algorithm.update(voltage, current)
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': voltage * current,
            'v_ref': self.v_ref,
            'is_scanning': self.is_scanning,
            'step': self.step_count
        })
        
        return self.v_ref
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.step_count = 0
        self.is_scanning = False
        self.scan_complete = False
        self.global_mpp = None
        self.local_algorithm.reset()


class HybridMPPT(MPPTAlgorithm):
    """
    混合MPPT算法
    Hybrid MPPT Algorithm
    
    原理:
    ----
    结合PSO全局搜索和P&O局部跟踪的优势
    
    策略:
    1. 启动阶段: PSO快速找到全局MPP区域
    2. 跟踪阶段: P&O精细跟踪
    3. 环境变化: 检测到功率大幅下降，重新启动PSO
    
    优点: 快速+精确+鲁棒
    缺点: 实现复杂
    """
    
    def __init__(self,
                 pv_module,
                 pso_params: dict = None,
                 po_params: dict = None,
                 switch_threshold: float = 0.95,
                 reactivation_threshold: float = 0.90,
                 name: str = "Hybrid"):
        """
        初始化混合MPPT
        
        Parameters:
        -----------
        pv_module : PVModule
            光伏组件对象
        pso_params : dict
            PSO参数 {'n_particles': 10, 'max_iterations': 20, ...}
        po_params : dict
            P&O参数 {'step_size': 1.0, ...}
        switch_threshold : float
            切换阈值（PSO达到多少效率切换到P&O）
        reactivation_threshold : float
            重新激活阈值（P&O效率低于多少重启PSO）
        name : str
            算法名称
        """
        super().__init__(name)
        self.pv_module = pv_module
        self.switch_threshold = switch_threshold
        self.reactivation_threshold = reactivation_threshold
        
        # 创建PSO算法
        pso_defaults = {
            'n_particles': 10,
            'v_min': 0,
            'v_max': pv_module.Voc if pv_module else 40.0,
            'w': 0.7,
            'c1': 1.5,
            'c2': 1.5,
            'max_iterations': 20
        }
        if pso_params:
            pso_defaults.update(pso_params)
        
        self.pso = ParticleSwarmMPPT(**pso_defaults)
        if pv_module:
            self.pso.set_pv_module(pv_module)
        
        # 创建P&O算法
        po_defaults = {'step_size': 1.0}
        if po_params:
            po_defaults.update(po_params)
        
        self.po = PerturbAndObserve(**po_defaults)
        
        # 控制变量
        self.mode = 'PSO'  # 'PSO' or 'PO'
        self.v_ref = pso_defaults['v_max'] / 2.0
        self.best_power = 0.0
        self.recent_powers = []
        self.switch_count = 0
    
    def update(self, voltage: float, current: float, **kwargs) -> float:
        """
        更新算法
        
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
        power = voltage * current
        
        # 更新最佳功率
        if power > self.best_power:
            self.best_power = power
        
        # 记录最近功率
        self.recent_powers.append(power)
        if len(self.recent_powers) > 20:
            self.recent_powers.pop(0)
        
        # 根据当前模式更新
        if self.mode == 'PSO':
            self.v_ref = self.pso.update(voltage, current)
            
            # 检查是否应该切换到P&O
            if self.pso.converged:
                # PSO收敛，切换到P&O
                efficiency = power / self.best_power if self.best_power > 0 else 0
                if efficiency >= self.switch_threshold or self.pso.iteration >= self.pso.max_iterations:
                    self.mode = 'PO'
                    self.po.v_ref = self.v_ref  # 从PSO结果开始
                    self.switch_count += 1
        
        elif self.mode == 'PO':
            self.v_ref = self.po.update(voltage, current)
            
            # 检查是否需要重新激活PSO
            if len(self.recent_powers) >= 10:
                avg_recent_power = np.mean(self.recent_powers[-10:])
                efficiency = avg_recent_power / self.best_power if self.best_power > 0 else 0
                
                if efficiency < self.reactivation_threshold:
                    # 功率大幅下降，可能是环境变化，重启PSO
                    self.mode = 'PSO'
                    self.pso.reset()
                    self.switch_count += 1
                    self.best_power = power  # 重置最佳功率
        
        # 记录历史
        self.history.append({
            'v': voltage,
            'i': current,
            'p': power,
            'v_ref': self.v_ref,
            'mode': self.mode,
            'best_power': self.best_power,
            'switch_count': self.switch_count
        })
        
        return self.v_ref
    
    def get_status(self) -> dict:
        """
        获取当前状态
        
        Returns:
        --------
        dict : 状态信息
        """
        return {
            'mode': self.mode,
            'v_ref': self.v_ref,
            'best_power': self.best_power,
            'switch_count': self.switch_count,
            'pso_converged': self.pso.converged if self.mode == 'PSO' else None,
            'pso_iteration': self.pso.iteration if self.mode == 'PSO' else None
        }
    
    def reset(self):
        """重置算法"""
        super().reset()
        self.mode = 'PSO'
        self.pso.reset()
        self.po.reset()
        self.best_power = 0.0
        self.recent_powers = []
        self.switch_count = 0


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
