"""
新安江模型 (Xin'anjiang Model)
============================

中国最广泛应用的流域水文模型
由河海大学赵人俊院士于1973年提出

模型特点:
- 蓄满产流机制
- 三层蒸散发
- 三水源划分（地表径流、壤中流、地下径流）
- 自由水蓄水库

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Tuple, Optional


class XinAnJiangModel:
    """
    新安江模型
    
    Parameters
    ----------
    params : dict
        模型参数字典，包含:
        
        蒸散发参数:
        - K : float, 蒸发折算系数 (0.7-1.2)
        - UM : float, 上层蓄水容量 (10-20 mm)
        - LM : float, 下层蓄水容量 (60-90 mm)
        - C : float, 深层蒸散发系数 (0.1-0.3)
        
        产流参数:
        - WM : float, 流域平均蓄水容量 (100-200 mm)
        - B : float, 蓄水容量曲线指数 (0.1-0.4)
        - IM : float, 不透水面积占比 (0.0-0.05)
        
        水源划分参数:
        - SM : float, 自由水蓄水库容量 (10-50 mm)
        - EX : float, 自由水蓄水库出流指数 (1.0-1.5)
        - KG : float, 地下水出流系数 (0.3-0.7)
        - KI : float, 壤中流出流系数 (0.3-0.7)
        
        消退系数:
        - CG : float, 地下水消退系数 (0.9-0.999)
        - CI : float, 壤中流消退系数 (0.5-0.9)
        - CS : float, 地表径流消退系数 (0.1-0.5)
        
        初始状态 (optional):
        - W0 : float, 初始土壤含水量 (mm), 默认 WM * 0.6
        - S0 : float, 初始自由水储量 (mm), 默认 SM * 0.5
    
    Attributes
    ----------
    params : dict
        模型参数
    state : dict
        当前状态变量
        
    Examples
    --------
    >>> # 创建新安江模型
    >>> params = {
    ...     'K': 1.0, 'UM': 15, 'LM': 75, 'C': 0.15,
    ...     'WM': 150, 'B': 0.3, 'IM': 0.01,
    ...     'SM': 30, 'EX': 1.2, 'KG': 0.5, 'KI': 0.5,
    ...     'CG': 0.98, 'CI': 0.7, 'CS': 0.3
    ... }
    >>> model = XinAnJiangModel(params)
    >>> 
    >>> # 运行模拟
    >>> P = np.array([10, 20, 5, 0, 0])  # 降雨 (mm)
    >>> EM = np.array([5, 5, 5, 5, 5])   # 蒸发 (mm)
    >>> results = model.run(P, EM)
    >>> print(f"总径流: {results['R'].sum():.2f} mm")
    """
    
    def __init__(self, params: Dict[str, float]):
        """初始化新安江模型"""
        self.params = params
        
        # 验证参数
        required_params = ['K', 'UM', 'LM', 'C', 'WM', 'B', 'IM', 
                          'SM', 'EX', 'KG', 'KI', 'CG', 'CI', 'CS']
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        # 初始化状态变量
        self.state = {
            'WU': 0.0,  # 上层土壤含水量
            'WL': 0.0,  # 下层土壤含水量
            'WD': 0.0,  # 深层土壤含水量
            'W': params.get('W0', params['WM'] * 0.6),  # 总土壤含水量
            'S': params.get('S0', params['SM'] * 0.5),  # 自由水储量
            'FR': 0.0,  # 自由水蓄水库蓄水比
            'QG': 0.0,  # 地下水出流
            'QI': 0.0,  # 壤中流出流
        }
        
        # 分解初始W到三层
        self._distribute_initial_W()
    
    def _distribute_initial_W(self):
        """将初始W分配到三层"""
        W = self.state['W']
        UM = self.params['UM']
        LM = self.params['LM']
        WM = self.params['WM']
        DM = WM - UM - LM  # 深层容量
        
        if W <= UM:
            self.state['WU'] = W
            self.state['WL'] = 0
            self.state['WD'] = 0
        elif W <= UM + LM:
            self.state['WU'] = UM
            self.state['WL'] = W - UM
            self.state['WD'] = 0
        else:
            self.state['WU'] = UM
            self.state['WL'] = LM
            self.state['WD'] = W - UM - LM
    
    def run(self, P: np.ndarray, EM: np.ndarray, 
            dt: float = 1.0) -> Dict[str, np.ndarray]:
        """
        运行新安江模型
        
        Parameters
        ----------
        P : ndarray
            降雨序列 (mm)
        EM : ndarray
            蒸发能力序列 (mm)
        dt : float
            时间步长 (day), 默认1天
            
        Returns
        -------
        results : dict
            模拟结果字典，包含:
            - 'Q' : 总流量 (mm)
            - 'R' : 总径流深 (mm)
            - 'RS' : 地表径流 (mm)
            - 'RI' : 壤中流 (mm)
            - 'RG' : 地下径流 (mm)
            - 'E' : 实际蒸散发 (mm)
            - 'W' : 土壤含水量 (mm)
            - 'S' : 自由水储量 (mm)
        """
        P = np.asarray(P)
        EM = np.asarray(EM)
        n_steps = len(P)
        
        # 初始化输出数组
        Q = np.zeros(n_steps)   # 总流量
        R = np.zeros(n_steps)   # 总径流
        RS = np.zeros(n_steps)  # 地表径流
        RI = np.zeros(n_steps)  # 壤中流
        RG = np.zeros(n_steps)  # 地下径流
        E = np.zeros(n_steps)   # 实际蒸散发
        W_series = np.zeros(n_steps)  # 土壤含水量
        S_series = np.zeros(n_steps)  # 自由水储量
        
        # 时间循环
        for t in range(n_steps):
            # 1. 蒸散发计算
            EU, EL, ED = self._evapotranspiration(P[t], EM[t])
            E[t] = EU + EL + ED
            
            # 2. 产流计算
            PE = P[t] - E[t]  # 净雨
            if PE > 0:
                R_temp = self._runoff_generation(PE)
                R[t] = R_temp
            else:
                R[t] = 0
            
            # 3. 水源划分
            RS[t], RI[t], RG[t] = self._water_source_partition(R[t])
            
            # 4. 总流量（简化：直接相加，实际需汇流计算）
            Q[t] = RS[t] + RI[t] + RG[t]
            
            # 5. 记录状态
            W_series[t] = self.state['W']
            S_series[t] = self.state['S']
        
        results = {
            'Q': Q,
            'R': R,
            'RS': RS,
            'RI': RI,
            'RG': RG,
            'E': E,
            'W': W_series,
            'S': S_series,
        }
        
        return results
    
    def _evapotranspiration(self, P: float, EM: float) -> Tuple[float, float, float]:
        """
        三层蒸散发计算
        
        Parameters
        ----------
        P : float
            当前时段降雨 (mm)
        EM : float
            当前时段蒸发能力 (mm)
            
        Returns
        -------
        EU : float
            上层蒸发 (mm)
        EL : float
            下层蒸发 (mm)
        ED : float
            深层蒸发 (mm)
        """
        K = self.params['K']
        UM = self.params['UM']
        LM = self.params['LM']
        WM = self.params['WM']
        C = self.params['C']
        
        WU = self.state['WU']
        WL = self.state['WL']
        WD = self.state['WD']
        
        EP = K * EM  # 折算后的蒸发能力
        
        # 上层蒸发
        if WU + P >= EP:
            EU = EP
            WU = WU + P - EU
        else:
            EU = WU + P
            WU = 0
            
            # 下层蒸发
            if WL >= C * LM:
                EL = (EP - EU) * WL / LM
            else:
                EL = (EP - EU) * WL / (C * LM)
            
            WL = max(0, WL - EL)
            
            # 深层蒸发
            if WD >= C * (WM - UM - LM):
                ED = (EP - EU - EL) * WD / (WM - UM - LM)
            else:
                ED = (EP - EU - EL) * WD / (C * (WM - UM - LM))
            
            WD = max(0, WD - ED)
        
        # 上层超出部分下渗
        if WU > UM:
            WL = WL + (WU - UM)
            WU = UM
        
        # 下层超出部分下渗
        if WL > LM:
            WD = WD + (WL - LM)
            WL = LM
        
        # 更新状态
        self.state['WU'] = WU
        self.state['WL'] = WL
        self.state['WD'] = WD
        self.state['W'] = WU + WL + WD
        
        return EU, EL if 'EL' in locals() else 0, ED if 'ED' in locals() else 0
    
    def _runoff_generation(self, PE: float) -> float:
        """
        产流计算（蓄满产流）
        
        Parameters
        ----------
        PE : float
            净雨 (mm)
            
        Returns
        -------
        R : float
            径流深 (mm)
        """
        WM = self.params['WM']
        B = self.params['B']
        IM = self.params['IM']
        W = self.state['W']
        
        # 不透水面积产流
        R_IM = PE * IM
        
        # 透水面积产流
        PE_permeable = PE * (1 - IM)
        
        if PE_permeable <= 0:
            R_permeable = 0
        else:
            # 计算蓄水容量（防止W超过WM导致NaN）
            W_ratio = min(W / WM, 1.0)  # 确保不超过1
            A = WM * (1 - (1 - W_ratio) ** (1 / (1 + B)))  # 已蓄满面积对应的蓄水容量

            if PE_permeable + A >= WM:
                # 全部产流
                R_permeable = PE_permeable - (WM - W)
            else:
                # 部分产流
                # 新的蓄满面积对应的蓄水容量
                A_new = PE_permeable + A
                # 产流面积（防止A_new超过WM导致NaN）
                A_new_ratio = min(A_new / WM, 1.0)
                FR = 1 - (1 - A_new_ratio) ** (1 + B)
                R_permeable = PE_permeable * FR
        
        # 总产流
        R = R_IM + R_permeable
        
        # 更新土壤含水量
        self.state['W'] = min(WM, W + PE_permeable - R_permeable)
        
        return R
    
    def _water_source_partition(self, R: float) -> Tuple[float, float, float]:
        """
        水源划分（自由水蓄水库）
        
        Parameters
        ----------
        R : float
            总径流深 (mm)
            
        Returns
        -------
        RS : float
            地表径流 (mm)
        RI : float
            壤中流 (mm)
        RG : float
            地下径流 (mm)
        """
        SM = self.params['SM']
        EX = self.params['EX']
        KG = self.params['KG']
        KI = self.params['KI']
        CG = self.params['CG']
        CI = self.params['CI']
        
        S = self.state['S']
        QG = self.state['QG']
        QI = self.state['QI']
        
        # 自由水蓄水库入流
        S = S + R
        
        # 计算蓄水比
        FR = S / SM
        FR = min(1.0, FR)  # 限制在0-1之间
        
        # 水源划分
        if FR <= 0:
            RS = 0
            RI = 0
            RG = 0
        else:
            # 地表径流
            if FR > KG + KI:
                RS = S * (FR - KG - KI) ** EX
            else:
                RS = 0
            
            # 壤中流
            RI = S * KI * FR ** EX
            
            # 地下径流
            RG = S * KG * FR ** EX
        
        # 更新自由水储量
        S = S - RS - RI - RG
        S = max(0, S)
        
        # 考虑消退系数（前一时段的出流）
        QG_new = QG * CG + RG
        QI_new = QI * CI + RI
        
        # 更新状态
        self.state['S'] = S
        self.state['FR'] = FR
        self.state['QG'] = QG_new
        self.state['QI'] = QI_new
        
        return RS, QI_new - QI, QG_new - QG  # 返回增量
    
    def reset(self):
        """重置模型状态"""
        self.state = {
            'WU': 0.0,
            'WL': 0.0,
            'WD': 0.0,
            'W': self.params.get('W0', self.params['WM'] * 0.6),
            'S': self.params.get('S0', self.params['SM'] * 0.5),
            'FR': 0.0,
            'QG': 0.0,
            'QI': 0.0,
        }
        self._distribute_initial_W()
    
    def get_state(self) -> Dict[str, float]:
        """获取当前状态"""
        return self.state.copy()
    
    def set_state(self, state: Dict[str, float]):
        """设置模型状态"""
        self.state = state.copy()


def create_default_xaj_params(basin_type='humid'):
    """
    创建默认的新安江模型参数
    
    Parameters
    ----------
    basin_type : str
        流域类型: 'humid'(湿润), 'semi-humid'(半湿润), 'semi-arid'(半干旱)
        
    Returns
    -------
    params : dict
        默认参数字典
    """
    if basin_type == 'humid':
        # 湿润地区参数
        params = {
            'K': 1.0,
            'UM': 15.0,
            'LM': 75.0,
            'C': 0.15,
            'WM': 150.0,
            'B': 0.3,
            'IM': 0.01,
            'SM': 30.0,
            'EX': 1.2,
            'KG': 0.5,
            'KI': 0.5,
            'CG': 0.98,
            'CI': 0.7,
            'CS': 0.3,
        }
    elif basin_type == 'semi-humid':
        # 半湿润地区参数
        params = {
            'K': 0.9,
            'UM': 20.0,
            'LM': 80.0,
            'C': 0.18,
            'WM': 180.0,
            'B': 0.35,
            'IM': 0.02,
            'SM': 35.0,
            'EX': 1.3,
            'KG': 0.4,
            'KI': 0.4,
            'CG': 0.95,
            'CI': 0.65,
            'CS': 0.25,
        }
    else:  # semi-arid
        # 半干旱地区参数
        params = {
            'K': 0.8,
            'UM': 25.0,
            'LM': 85.0,
            'C': 0.20,
            'WM': 200.0,
            'B': 0.4,
            'IM': 0.03,
            'SM': 40.0,
            'EX': 1.4,
            'KG': 0.3,
            'KI': 0.3,
            'CG': 0.92,
            'CI': 0.60,
            'CS': 0.20,
        }
    
    return params
