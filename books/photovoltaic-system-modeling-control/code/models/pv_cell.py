"""
光伏电池模型
PV Cell Models

实现单二极管模型和双二极管模型
"""

import numpy as np
from scipy.optimize import fsolve
from typing import Tuple, Optional


class PVCell:
    """
    光伏电池基类
    Base class for photovoltaic cell models
    """
    
    def __init__(self, name: str = "PV Cell"):
        self.name = name
        
    def calculate_current(self, voltage: float) -> float:
        """
        计算给定电压下的电流
        
        Parameters:
        -----------
        voltage : float
            电压 (V)
            
        Returns:
        --------
        float
            电流 (A)
        """
        raise NotImplementedError
        
    def calculate_power(self, voltage: float) -> float:
        """
        计算给定电压下的功率
        
        Parameters:
        -----------
        voltage : float
            电压 (V)
            
        Returns:
        --------
        float
            功率 (W)
        """
        current = self.calculate_current(voltage)
        return voltage * current
        
    def get_iv_curve(self, voltage_points: int = 200) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取I-V特性曲线
        
        Parameters:
        -----------
        voltage_points : int
            电压采样点数
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray]
            电压数组和电流数组
        """
        v_array = np.linspace(0, self.Voc, voltage_points)
        i_array = np.array([self.calculate_current(v) for v in v_array])
        return v_array, i_array
        
    def get_pv_curve(self, voltage_points: int = 200) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取P-V特性曲线
        
        Parameters:
        -----------
        voltage_points : int
            电压采样点数
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray]
            电压数组和功率数组
        """
        v_array, i_array = self.get_iv_curve(voltage_points)
        p_array = v_array * i_array
        return v_array, p_array
        
    def find_mpp(self) -> Tuple[float, float, float]:
        """
        寻找最大功率点 (MPP)
        
        Returns:
        --------
        Tuple[float, float, float]
            Vmpp (V), Impp (A), Pmpp (W)
        """
        v_array, p_array = self.get_pv_curve(500)
        max_idx = np.argmax(p_array)
        vmpp = v_array[max_idx]
        pmpp = p_array[max_idx]
        impp = self.calculate_current(vmpp)
        return vmpp, impp, pmpp


class SingleDiodeModel(PVCell):
    """
    单二极管等效电路模型
    Single Diode Equivalent Circuit Model
    
    模型方程:
    I = Iph - I0 * [exp((V + I*Rs)/(n*Vt)) - 1] - (V + I*Rs)/Rsh
    
    其中:
    - Iph: 光生电流 (A)
    - I0: 二极管反向饱和电流 (A)
    - Rs: 串联电阻 (Ω)
    - Rsh: 并联电阻 (Ω)
    - n: 理想因子
    - Vt: 热电压 = kT/q (V)
    """
    
    # 物理常数
    k = 1.380649e-23  # 玻尔兹曼常数 (J/K)
    q = 1.602176634e-19  # 电子电荷 (C)
    
    def __init__(self,
                 Isc: float = 8.0,  # 短路电流 (A)
                 Voc: float = 0.6,  # 开路电压 (V)
                 Imp: float = 7.5,  # 最大功率点电流 (A)
                 Vmp: float = 0.48,  # 最大功率点电压 (V)
                 T: float = 298.15,  # 温度 (K), 默认25°C
                 G: float = 1000.0,  # 辐照度 (W/m²)
                 n: float = 1.2,  # 理想因子
                 Rs: Optional[float] = None,  # 串联电阻 (Ω)
                 Rsh: Optional[float] = None,  # 并联电阻 (Ω)
                 name: str = "Single Diode Model"):
        """
        初始化单二极管模型
        
        Parameters:
        -----------
        Isc : float
            标准测试条件下短路电流 (A)
        Voc : float
            标准测试条件下开路电压 (V)
        Imp : float
            标准测试条件下最大功率点电流 (A)
        Vmp : float
            标准测试条件下最大功率点电压 (V)
        T : float
            电池温度 (K)
        G : float
            辐照度 (W/m²)
        n : float
            二极管理想因子
        Rs : float, optional
            串联电阻 (Ω), 若不提供则自动计算
        Rsh : float, optional
            并联电阻 (Ω), 若不提供则自动计算
        """
        super().__init__(name)
        
        # 标准测试条件 (STC: G=1000W/m², T=25°C)
        self.Isc_stc = Isc
        self.Voc_stc = Voc
        self.Imp_stc = Imp
        self.Vmp_stc = Vmp
        self.Pmp_stc = Imp * Vmp
        
        # 当前工作条件
        self.T = T  # 温度 (K)
        self.G = G  # 辐照度 (W/m²)
        self.n = n  # 理想因子
        
        # 热电压
        self.Vt = self.k * self.T / self.q
        
        # 计算模型参数
        if Rs is None or Rsh is None:
            self.Rs, self.Rsh = self._estimate_resistances()
        else:
            self.Rs = Rs
            self.Rsh = Rsh
            
        # 计算光生电流和反向饱和电流
        self.Iph = self._calculate_photocurrent()
        self.I0 = self._calculate_saturation_current()
        
        # 更新当前工作条件下的特性参数
        self.Isc = self.calculate_current(0.0)  # 短路电流
        self.Voc = self._calculate_open_circuit_voltage()  # 开路电压
        
    def _estimate_resistances(self) -> Tuple[float, float]:
        """
        估算串联电阻和并联电阻
        使用简化的经验公式
        
        Returns:
        --------
        Tuple[float, float]
            Rs (Ω), Rsh (Ω)
        """
        # 串联电阻估算
        # Rs ≈ (Voc - Vmp) / Imp - (Vmp/Imp) * ln((Isc-Imp)/I0)
        # 简化估算
        Rs = 0.005  # 典型值 5mΩ
        
        # 并联电阻估算
        # Rsh应该很大, 典型值 1000Ω
        Rsh = 1000.0
        
        return Rs, Rsh
        
    def _calculate_photocurrent(self) -> float:
        """
        计算光生电流
        
        Iph与辐照度成正比:
        Iph = Isc_stc * (G / 1000)
        
        温度影响(简化):
        Iph = Iph0 * [1 + α(T - T_stc)]
        其中α ≈ 0.0005/K (温度系数)
        """
        G_stc = 1000.0  # W/m²
        T_stc = 298.15  # K (25°C)
        alpha = 0.0005  # 温度系数 (1/K)
        
        Iph = self.Isc_stc * (self.G / G_stc) * (1 + alpha * (self.T - T_stc))
        return Iph
        
    def _calculate_saturation_current(self) -> float:
        """
        计算二极管反向饱和电流
        
        I0与温度强相关: I0(T) = I0(T_ref) * (T/T_ref)^3 * exp(Eg/nVt * (1 - T_ref/T))
        简化为: I0 ≈ I0_ref * (T/T_ref)^3 * exp(α(T-T_ref))
        
        在STC条件下:
        I0_stc ≈ (Iph_stc - Voc_stc/Rsh) / [exp(Voc_stc/(n*Vt_stc)) - 1]
        
        当前条件:
        I0 = I0_stc * (T/T_stc)^3
        """
        T_stc = 298.15
        Vt_stc = self.k * T_stc / self.q
        
        # 计算STC下的I0
        Iph_stc = self.Isc_stc
        I0_stc = (Iph_stc - self.Voc_stc / self.Rsh) / (np.exp(self.Voc_stc / (self.n * Vt_stc)) - 1)
        
        # 温度修正
        I0 = I0_stc * np.power(self.T / T_stc, 3)
        
        return I0
        
    def _calculate_open_circuit_voltage(self) -> float:
        """
        计算开路电压
        在开路条件下求解 I = 0
        考虑当前温度和辐照度的影响
        """
        def equation(V):
            return self.Iph - self.I0 * (np.exp(V / (self.n * self.Vt)) - 1) - V / self.Rsh
        
        # 使用Voc_stc作为初始猜测,但考虑温度和辐照度的影响
        # Voc ≈ Voc_stc + n*Vt*ln(G/G_stc) + β(T-T_stc)
        G_stc = 1000.0
        T_stc = 298.15
        beta = -0.0023  # 温度系数 (V/K)
        
        V_initial = self.Voc_stc + self.n * self.Vt * np.log(self.G / G_stc) + beta * (self.T - T_stc)
        V_initial = max(0.1, V_initial)  # 确保初值合理
        
        try:
            Voc = fsolve(equation, V_initial)[0]
            return max(0, Voc)
        except:
            return self.Voc_stc
        
    def calculate_current(self, voltage: float) -> float:
        """
        计算给定电压下的电流
        
        求解隐式方程:
        I = Iph - I0 * [exp((V + I*Rs)/(n*Vt)) - 1] - (V + I*Rs)/Rsh
        
        Parameters:
        -----------
        voltage : float
            电压 (V)
            
        Returns:
        --------
        float
            电流 (A)
        """
        def equation(I):
            return (self.Iph 
                    - self.I0 * (np.exp((voltage + I * self.Rs) / (self.n * self.Vt)) - 1)
                    - (voltage + I * self.Rs) / self.Rsh
                    - I)
        
        # 初始猜测: 忽略Rs和Rsh的简化解
        I_guess = self.Iph - self.I0 * (np.exp(voltage / (self.n * self.Vt)) - 1)
        I_guess = max(0, I_guess)  # 电流不能为负
        
        try:
            I = fsolve(equation, I_guess)[0]
            return max(0, I)  # 确保电流非负
        except:
            return 0.0
            
    def update_conditions(self, T: Optional[float] = None, G: Optional[float] = None):
        """
        更新工作条件 (温度和/或辐照度)
        
        Parameters:
        -----------
        T : float, optional
            新的温度 (K)
        G : float, optional
            新的辐照度 (W/m²)
        """
        if T is not None:
            self.T = T
            self.Vt = self.k * self.T / self.q
            
        if G is not None:
            self.G = G
            
        # 重新计算光生电流和反向饱和电流
        self.Iph = self._calculate_photocurrent()
        self.I0 = self._calculate_saturation_current()
        
        # 更新特性参数
        self.Isc = self.calculate_current(0.0)
        self.Voc = self._calculate_open_circuit_voltage()
        
    def get_parameters(self) -> dict:
        """
        获取模型参数
        
        Returns:
        --------
        dict
            包含所有模型参数的字典
        """
        return {
            'name': self.name,
            'T': self.T,
            'G': self.G,
            'n': self.n,
            'Rs': self.Rs,
            'Rsh': self.Rsh,
            'Iph': self.Iph,
            'I0': self.I0,
            'Vt': self.Vt,
            'Isc': self.Isc,
            'Voc': self.Voc,
            'Isc_stc': self.Isc_stc,
            'Voc_stc': self.Voc_stc,
            'Imp_stc': self.Imp_stc,
            'Vmp_stc': self.Vmp_stc,
            'Pmp_stc': self.Pmp_stc,
        }
        
    def print_parameters(self):
        """
        打印模型参数
        """
        params = self.get_parameters()
        print(f"\n{self.name} - 模型参数")
        print("=" * 60)
        print(f"标准测试条件 (STC: G=1000W/m², T=25°C):")
        print(f"  短路电流 Isc_stc:    {params['Isc_stc']:.3f} A")
        print(f"  开路电压 Voc_stc:    {params['Voc_stc']:.3f} V")
        print(f"  最大功率点电流 Imp: {params['Imp_stc']:.3f} A")
        print(f"  最大功率点电压 Vmp: {params['Vmp_stc']:.3f} V")
        print(f"  最大功率 Pmp:       {params['Pmp_stc']:.3f} W")
        print(f"\n当前工作条件:")
        print(f"  温度 T:             {params['T']:.2f} K ({params['T']-273.15:.1f}°C)")
        print(f"  辐照度 G:           {params['G']:.1f} W/m²")
        print(f"\n模型参数:")
        print(f"  理想因子 n:         {params['n']:.3f}")
        print(f"  串联电阻 Rs:        {params['Rs']:.6f} Ω")
        print(f"  并联电阻 Rsh:       {params['Rsh']:.3f} Ω")
        print(f"  光生电流 Iph:       {params['Iph']:.3f} A")
        print(f"  反向饱和电流 I0:    {params['I0']:.3e} A")
        print(f"  热电压 Vt:          {params['Vt']:.6f} V")
        print(f"\n当前特性:")
        print(f"  短路电流 Isc:       {params['Isc']:.3f} A")
        print(f"  开路电压 Voc:       {params['Voc']:.3f} V")
        print("=" * 60)


class DoubleDiodeModel(PVCell):
    """
    双二极管等效电路模型
    Double Diode Equivalent Circuit Model
    
    更精确的模型,考虑扩散电流和复合电流
    
    模型方程:
    I = Iph - I01*[exp((V+I*Rs)/(n1*Vt)) - 1] - I02*[exp((V+I*Rs)/(n2*Vt)) - 1] - (V+I*Rs)/Rsh
    
    其中:
    - Iph: 光生电流
    - I01: 扩散电流饱和值
    - I02: 复合电流饱和值
    - n1: 扩散理想因子 (≈1.0)
    - n2: 复合理想因子 (≈2.0)
    - Rs: 串联电阻
    - Rsh: 并联电阻
    """
    
    # 物理常数
    k = 1.380649e-23  # 玻尔兹曼常数 (J/K)
    q = 1.602176634e-19  # 电子电荷 (C)
    
    def __init__(self,
                 Isc: float = 8.0,
                 Voc: float = 0.6,
                 Imp: float = 7.5,
                 Vmp: float = 0.48,
                 T: float = 298.15,
                 G: float = 1000.0,
                 n1: float = 1.0,  # 扩散理想因子
                 n2: float = 2.0,  # 复合理想因子
                 Rs: Optional[float] = None,
                 Rsh: Optional[float] = None,
                 name: str = "Double Diode Model"):
        """
        初始化双二极管模型
        
        Parameters:
        -----------
        Isc, Voc, Imp, Vmp : float
            标准测试条件下的特性参数
        T : float
            电池温度 (K)
        G : float
            辐照度 (W/m²)
        n1 : float
            扩散理想因子 (通常≈1.0)
        n2 : float
            复合理想因子 (通常≈2.0)
        Rs, Rsh : float, optional
            串联和并联电阻
        """
        super().__init__(name)
        
        # STC参数
        self.Isc_stc = Isc
        self.Voc_stc = Voc
        self.Imp_stc = Imp
        self.Vmp_stc = Vmp
        self.Pmp_stc = Imp * Vmp
        
        # 工作条件
        self.T = T
        self.G = G
        self.n1 = n1  # 扩散理想因子
        self.n2 = n2  # 复合理想因子
        
        # 热电压
        self.Vt = self.k * self.T / self.q
        
        # 电阻
        if Rs is None or Rsh is None:
            self.Rs, self.Rsh = self._estimate_resistances()
        else:
            self.Rs = Rs
            self.Rsh = Rsh
            
        # 计算电流参数
        self.Iph = self._calculate_photocurrent()
        self.I01, self.I02 = self._calculate_saturation_currents()
        
        # 更新特性参数
        self.Isc = self.calculate_current(0.0)
        self.Voc = self._calculate_open_circuit_voltage()
        
    def _estimate_resistances(self) -> Tuple[float, float]:
        """估算电阻"""
        Rs = 0.004  # 双二极管模型Rs稍小
        Rsh = 1500.0  # Rsh稍大
        return Rs, Rsh
        
    def _calculate_photocurrent(self) -> float:
        """计算光生电流"""
        G_stc = 1000.0
        T_stc = 298.15
        alpha = 0.0005
        
        Iph = self.Isc_stc * (self.G / G_stc) * (1 + alpha * (self.T - T_stc))
        return Iph
        
    def _calculate_saturation_currents(self) -> Tuple[float, float]:
        """
        计算两个二极管的反向饱和电流
        
        使用经验关系:
        I01 ≈ 0.9 * I0_total
        I02 ≈ 0.1 * I0_total
        
        I0(T) = I0(T_ref) * (T/T_ref)^3 * exp(Eg/k * (1/T_ref - 1/T))
        """
        T_stc = 298.15
        Vt_stc = self.k * T_stc / self.q
        
        # 在STC下计算I0
        Iph_stc = self.Isc_stc
        # 从Voc_stc反推I0_stc
        I0_stc = (Iph_stc - self.Voc_stc / self.Rsh) / (np.exp(self.Voc_stc / (self.n1 * Vt_stc)) - 1)
        
        # 温度修正 - 使用更强的温度依赖
        # 硅电池的能隙 Eg ≈ 1.12 eV
        Eg = 1.12  # eV
        # I0随温度强烈增加
        temp_ratio = np.power(self.T / T_stc, 3)
        exp_factor = np.exp(Eg * self.q / self.k * (1.0 / T_stc - 1.0 / self.T))
        I0_total = I0_stc * temp_ratio * exp_factor
        
        # 分配给两个二极管
        I01 = 0.9 * I0_total  # 扩散电流占主导
        I02 = 0.1 * I0_total  # 复合电流较小
        
        return I01, I02
        
    def _calculate_open_circuit_voltage(self) -> float:
        """计算开路电压"""
        def equation(V):
            term1 = self.I01 * (np.exp(V / (self.n1 * self.Vt)) - 1)
            term2 = self.I02 * (np.exp(V / (self.n2 * self.Vt)) - 1)
            term3 = V / self.Rsh
            return self.Iph - term1 - term2 - term3
        
        # 初值估算 - 考虑温度和辐照度影响
        G_stc = 1000.0
        T_stc = 298.15
        beta = -0.0023  # 温度系数 (V/K)
        
        # 基于当前条件估算初始值
        # Voc主要受温度影响(负温度系数)和辐照度影响(对数关系)
        irr_factor = self.n1 * self.Vt * np.log(max(self.G, 10) / G_stc)
        temp_factor = beta * (self.T - T_stc)
        V_initial = self.Voc_stc + irr_factor + temp_factor
        V_initial = max(0.1, min(V_initial, self.Voc_stc * 1.2))
        
        try:
            Voc = fsolve(equation, V_initial, full_output=False)[0]
            return max(0, Voc)
        except:
            return max(0.1, self.Voc_stc + temp_factor)
            
    def calculate_current(self, voltage: float) -> float:
        """
        计算给定电压下的电流
        
        求解隐式方程:
        I = Iph - I01*[exp((V+I*Rs)/(n1*Vt)) - 1] - I02*[exp((V+I*Rs)/(n2*Vt)) - 1] - (V+I*Rs)/Rsh
        """
        def equation(I):
            Vd = voltage + I * self.Rs  # 二极管电压
            term1 = self.I01 * (np.exp(Vd / (self.n1 * self.Vt)) - 1)
            term2 = self.I02 * (np.exp(Vd / (self.n2 * self.Vt)) - 1)
            term3 = Vd / self.Rsh
            return self.Iph - term1 - term2 - term3 - I
        
        # 初始猜测
        I_guess = self.Iph * 0.9
        I_guess = max(0, I_guess)
        
        try:
            I = fsolve(equation, I_guess)[0]
            return max(0, I)
        except:
            return 0.0
            
    def update_conditions(self, T: Optional[float] = None, G: Optional[float] = None):
        """更新工作条件"""
        if T is not None:
            self.T = T
            self.Vt = self.k * self.T / self.q
            
        if G is not None:
            self.G = G
            
        # 重新计算参数
        self.Iph = self._calculate_photocurrent()
        self.I01, self.I02 = self._calculate_saturation_currents()
        self.Isc = self.calculate_current(0.0)
        self.Voc = self._calculate_open_circuit_voltage()
        
    def get_parameters(self) -> dict:
        """获取模型参数"""
        return {
            'name': self.name,
            'T': self.T,
            'G': self.G,
            'n1': self.n1,
            'n2': self.n2,
            'Rs': self.Rs,
            'Rsh': self.Rsh,
            'Iph': self.Iph,
            'I01': self.I01,
            'I02': self.I02,
            'Vt': self.Vt,
            'Isc': self.Isc,
            'Voc': self.Voc,
            'Isc_stc': self.Isc_stc,
            'Voc_stc': self.Voc_stc,
            'Imp_stc': self.Imp_stc,
            'Vmp_stc': self.Vmp_stc,
            'Pmp_stc': self.Pmp_stc,
        }
        
    def print_parameters(self):
        """打印模型参数"""
        params = self.get_parameters()
        print(f"\n{self.name} - 模型参数")
        print("=" * 60)
        print(f"标准测试条件 (STC):")
        print(f"  短路电流 Isc_stc:    {params['Isc_stc']:.3f} A")
        print(f"  开路电压 Voc_stc:    {params['Voc_stc']:.3f} V")
        print(f"  最大功率 Pmp:       {params['Pmp_stc']:.3f} W")
        print(f"\n当前工作条件:")
        print(f"  温度 T:             {params['T']:.2f} K ({params['T']-273.15:.1f}°C)")
        print(f"  辐照度 G:           {params['G']:.1f} W/m²")
        print(f"\n模型参数:")
        print(f"  扩散理想因子 n1:    {params['n1']:.3f}")
        print(f"  复合理想因子 n2:    {params['n2']:.3f}")
        print(f"  串联电阻 Rs:        {params['Rs']:.6f} Ω")
        print(f"  并联电阻 Rsh:       {params['Rsh']:.3f} Ω")
        print(f"  光生电流 Iph:       {params['Iph']:.3f} A")
        print(f"  扩散饱和电流 I01:   {params['I01']:.3e} A")
        print(f"  复合饱和电流 I02:   {params['I02']:.3e} A")
        print(f"  热电压 Vt:          {params['Vt']:.6f} V")
        print(f"\n当前特性:")
        print(f"  短路电流 Isc:       {params['Isc']:.3f} A")
        print(f"  开路电压 Voc:       {params['Voc']:.3f} V")
        print("=" * 60)


if __name__ == "__main__":
    # 简单测试
    print("光伏电池模型测试")
    print("=" * 60)
    
    # 测试单二极管模型
    print("\n1. 单二极管模型:")
    pv1 = SingleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    pv1.print_parameters()
    vmpp1, impp1, pmpp1 = pv1.find_mpp()
    print(f"\nMPP: Vmpp={vmpp1:.3f}V, Impp={impp1:.3f}A, Pmpp={pmpp1:.3f}W")
    
    # 测试双二极管模型
    print("\n\n2. 双二极管模型:")
    pv2 = DoubleDiodeModel(
        Isc=8.0, Voc=0.6, Imp=7.5, Vmp=0.48,
        T=298.15, G=1000.0
    )
    pv2.print_parameters()
    vmpp2, impp2, pmpp2 = pv2.find_mpp()
    print(f"\nMPP: Vmpp={vmpp2:.3f}V, Impp={impp2:.3f}A, Pmpp={pmpp2:.3f}W")
