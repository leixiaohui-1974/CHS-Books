"""
系统级控制模块
包含MPPT协调、孤岛检测、故障穿越、多机并联等

Author: CHS-BOOKS Project
Date: 2025-11-04
"""

import numpy as np
from typing import Dict, Tuple


# ==================== MPPT与并网协调控制 ====================

class MPPTGridCoordinator:
    """
    MPPT与并网协调控制器
    
    功能: 协调MPPT和并网逆变器
    - 正常: MPPT最大功率跟踪
    - 限功率: 降低MPPT输出
    - 离网: 切换到电压控制
    """
    
    def __init__(self, P_rated: float = 5000.0, name: str = "MPPTGridCoord"):
        """
        初始化协调控制器
        
        Args:
            P_rated: 额定功率 (W)
            name: 控制器名称
        """
        self.name = name
        self.P_rated = P_rated
        self.mode = "MPPT"  # MPPT, Limit, Voltage
        
    def coordinate(self, P_mppt: float, P_grid_limit: float) -> Tuple[float, str]:
        """
        协调控制
        
        Args:
            P_mppt: MPPT输出功率 (W)
            P_grid_limit: 电网限制功率 (W)
            
        Returns:
            (P_ref, mode): 功率参考和控制模式
        """
        if P_grid_limit >= self.P_rated:
            # 正常MPPT模式
            self.mode = "MPPT"
            P_ref = P_mppt
        elif P_grid_limit > 0:
            # 限功率模式
            self.mode = "Limit"
            P_ref = min(P_mppt, P_grid_limit)
        else:
            # 离网模式
            self.mode = "Voltage"
            P_ref = 0
        
        return P_ref, self.mode


# ==================== 孤岛检测 ====================

class IslandingDetector:
    """
    孤岛检测器
    
    方法: 主动频率偏移法 (AFD)
    原理: 注入扰动，检测频率变化
    """
    
    def __init__(self, f_nominal: float = 50.0, df_threshold: float = 0.5, name: str = "IslandDetector"):
        """
        初始化孤岛检测器
        
        Args:
            f_nominal: 额定频率 (Hz)
            df_threshold: 频率偏差阈值 (Hz)
            name: 检测器名称
        """
        self.name = name
        self.f_nominal = f_nominal
        self.df_threshold = df_threshold
        self.islanded = False
        
    def detect(self, f_measured: float, V_measured: float) -> bool:
        """
        检测孤岛
        
        Args:
            f_measured: 测量频率 (Hz)
            V_measured: 测量电压 (V)
            
        Returns:
            is_islanded: 是否孤岛
        """
        # 频率判据
        df = abs(f_measured - self.f_nominal)
        
        if df > self.df_threshold:
            self.islanded = True
        else:
            self.islanded = False
        
        return self.islanded
    
    def inject_disturbance(self, P_ref: float, t: float) -> float:
        """
        注入扰动
        
        Args:
            P_ref: 功率参考 (W)
            t: 当前时间 (s)
            
        Returns:
            P_disturbed: 扰动后功率 (W)
        """
        # 周期性功率扰动
        disturbance = 0.05 * P_ref * np.sin(2 * np.pi * 2 * t)  # 2Hz扰动
        P_disturbed = P_ref + disturbance
        
        return P_disturbed


# ==================== 低电压穿越 ====================

class LVRTController:
    """
    低电压穿越控制器 (Low Voltage Ride Through)
    
    策略:
    - 电压跌落: 降低有功，增加无功
    - 电压恢复: 逐步恢复有功
    """
    
    def __init__(self, V_nominal: float = 220.0, name: str = "LVRTController"):
        """
        初始化LVRT控制器
        
        Args:
            V_nominal: 额定电压 (V)
            name: 控制器名称
        """
        self.name = name
        self.V_nominal = V_nominal
        self.in_lvrt = False
        
    def calculate(self, V_grid: float, P_rated: float, Q_rated: float) -> Tuple[float, float]:
        """
        计算LVRT期间的功率指令
        
        Args:
            V_grid: 电网电压 (V)
            P_rated: 额定有功功率 (W)
            Q_rated: 额定无功功率 (Var)
            
        Returns:
            (P_ref, Q_ref): 功率参考
        """
        V_pu = V_grid / self.V_nominal
        
        if V_pu < 0.9:
            # 进入LVRT
            self.in_lvrt = True
            
            # 有功降低
            if V_pu < 0.2:
                P_ref = 0
            else:
                P_ref = P_rated * V_pu
            
            # 无功增加（电压支撑）
            Q_ref = Q_rated * (1 - V_pu)
            
        else:
            # 正常运行
            self.in_lvrt = False
            P_ref = P_rated
            Q_ref = 0
        
        return P_ref, Q_ref


# ==================== 多机并联控制 ====================

class ParallelController:
    """
    多机并联控制器
    
    策略: 主从控制
    - 主机: 电压源，稳定母线电压
    - 从机: 电流源，功率均分
    """
    
    def __init__(self, is_master: bool = False, n_units: int = 1, name: str = "ParallelCtrl"):
        """
        初始化并联控制器
        
        Args:
            is_master: 是否为主机
            n_units: 并联单元数
            name: 控制器名称
        """
        self.name = name
        self.is_master = is_master
        self.n_units = n_units
        
    def calculate_reference(self, P_total: float, unit_id: int) -> float:
        """
        计算功率参考
        
        Args:
            P_total: 总功率需求 (W)
            unit_id: 单元编号
            
        Returns:
            P_ref: 该单元功率参考 (W)
        """
        if self.is_master:
            # 主机承担更多功率
            P_ref = P_total * 0.5
        else:
            # 从机均分剩余功率
            P_ref = P_total * 0.5 / (self.n_units - 1) if self.n_units > 1 else 0
        
        return P_ref
    
    def synchronize(self, phase_master: float, phase_self: float) -> float:
        """
        相位同步
        
        Args:
            phase_master: 主机相位 (rad)
            phase_self: 自身相位 (rad)
            
        Returns:
            phase_correction: 相位修正 (rad)
        """
        # 简单的PI同步
        error = phase_master - phase_self
        correction = 0.1 * error  # 比例系数
        
        return correction
