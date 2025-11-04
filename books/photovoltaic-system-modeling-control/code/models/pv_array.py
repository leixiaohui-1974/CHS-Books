"""
光伏阵列模型
PV Array Models

阵列由多个组件串并联构成
支持大规模光伏电站建模
"""

from typing import Tuple, List
import numpy as np
from .pv_module import PVModule


class PVArray:
    """
    光伏阵列模型
    
    结构: Np个并联串,每串Ns个串联组件
    
    电气特性:
    - 串联: 电压相加, 电流不变
    - 并联: 电流相加, 电压不变
    
    典型配置:
    - 小型系统: 1串 × 10-20组件 = 5-10kW
    - 中型系统: 10串 × 20组件 = 100kW
    - 大型电站: 100串 × 25组件 = 1MW+
    """
    
    def __init__(self,
                 module: PVModule,
                 Ns: int = 1,
                 Np: int = 1,
                 name: str = "PV Array"):
        """
        初始化光伏阵列
        
        Parameters:
        -----------
        module : PVModule
            组件模板
        Ns : int
            每串串联组件数
        Np : int
            并联串数
        name : str
            阵列名称
        """
        self.module = module
        self.Ns = Ns
        self.Np = Np
        self.name = name
        
        # 阵列特性
        self.Voc = Ns * module.Voc
        self.Isc = Np * module.Isc
        
        # 预估参数
        vmpp_module, impp_module, pmpp_module = module.find_mpp()
        self.Vmp_est = vmpp_module * Ns
        self.Imp_est = impp_module * Np
        self.Pmp_est = pmpp_module * Ns * Np
        
        # 阵列规模
        self.total_modules = Ns * Np
        self.total_cells = self.total_modules * module.Ns
        
    def calculate_current(self, voltage: float) -> float:
        """
        计算给定电压下的阵列电流
        
        并联特性: I_array = Np × I_string
        串联特性: V_string = Ns × V_module
        
        Parameters:
        -----------
        voltage : float
            阵列总电压(V)
            
        Returns:
        --------
        float : 阵列电流(A)
        """
        # 边界检查
        if voltage <= 0:
            return self.Isc
        if voltage >= self.Voc:
            return 0.0
        
        # 每个组件的平均电压
        v_module = voltage / self.Ns
        
        # 单个串的电流
        i_string = self.module.calculate_current(v_module)
        
        # 并联后的总电流
        i_array = self.Np * i_string
        
        return max(0.0, i_array)
    
    def calculate_power(self, voltage: float) -> float:
        """
        计算给定电压下的阵列功率
        
        Parameters:
        -----------
        voltage : float
            阵列电压(V)
            
        Returns:
        --------
        float : 阵列功率(W)
        """
        current = self.calculate_current(voltage)
        return voltage * current
    
    def get_iv_curve(self, num_points: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取阵列I-V特性曲线
        
        Parameters:
        -----------
        num_points : int
            曲线点数
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray] : 电压数组(V), 电流数组(A)
        """
        # 基于组件曲线缩放
        V_module, I_module = self.module.get_iv_curve(num_points)
        
        # 串联: 电压 × Ns
        V_array = V_module * self.Ns
        
        # 并联: 电流 × Np
        I_array = I_module * self.Np
        
        return V_array, I_array
    
    def get_pv_curve(self, num_points: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取阵列P-V特性曲线
        
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray] : 电压数组(V), 功率数组(W)
        """
        V, I = self.get_iv_curve(num_points)
        P = V * I
        return V, P
    
    def find_mpp(self) -> Tuple[float, float, float]:
        """
        寻找阵列最大功率点
        
        Returns:
        --------
        Tuple[float, float, float] : Vmpp(V), Impp(A), Pmpp(W)
        """
        V, P = self.get_pv_curve(500)
        idx = np.argmax(P)
        Vmpp = V[idx]
        Pmpp = P[idx]
        Impp = Pmpp / Vmpp if Vmpp > 0 else 0
        
        return Vmpp, Impp, Pmpp
    
    def get_parameters(self) -> dict:
        """
        获取阵列参数
        
        Returns:
        --------
        dict : 参数字典
        """
        vmpp, impp, pmpp = self.find_mpp()
        
        return {
            'name': self.name,
            'configuration': f'{self.Np}P{self.Ns}S',
            'Ns': self.Ns,
            'Np': self.Np,
            'total_modules': self.total_modules,
            'total_cells': self.total_cells,
            'Voc': self.Voc,
            'Isc': self.Isc,
            'Vmpp': vmpp,
            'Impp': impp,
            'Pmpp': pmpp,
            'Pmpp_kW': pmpp / 1000,
            'FF': pmpp / (self.Voc * self.Isc),
        }
    
    def print_parameters(self):
        """打印阵列参数"""
        params = self.get_parameters()
        
        print(f"\n{self.name} - 阵列参数")
        print("=" * 70)
        print(f"配置:")
        print(f"  阵列配置:              {params['configuration']}")
        print(f"  串联组件数 (Ns):       {params['Ns']} 个/串")
        print(f"  并联串数 (Np):         {params['Np']} 串")
        print(f"  总组件数:              {params['total_modules']} 个")
        print(f"  总电池片数:            {params['total_cells']} 片")
        
        print(f"\n电气参数:")
        print(f"  开路电压 Voc:          {params['Voc']:.2f} V")
        print(f"  短路电流 Isc:          {params['Isc']:.2f} A")
        print(f"  最大功率点电压 Vmpp:   {params['Vmpp']:.2f} V")
        print(f"  最大功率点电流 Impp:   {params['Impp']:.2f} A")
        print(f"  最大功率 Pmpp:         {params['Pmpp']:.2f} W ({params['Pmpp_kW']:.2f} kW)")
        print(f"  填充因子 FF:           {params['FF']:.4f} ({params['FF']*100:.2f}%)")
        print("=" * 70)
    
    def calculate_system_size(self, module_area: float = 1.6) -> dict:
        """
        计算系统规模参数
        
        Parameters:
        -----------
        module_area : float
            单个组件面积(m²), 典型值1.6-2.0m²
            
        Returns:
        --------
        dict : 系统规模参数
        """
        total_area = self.total_modules * module_area
        _, _, pmpp = self.find_mpp()
        
        # 计算效率
        G_stc = 1000  # W/m²
        efficiency = (pmpp / (total_area * G_stc)) * 100
        
        return {
            'module_area': module_area,
            'total_area': total_area,
            'power_kW': pmpp / 1000,
            'power_MW': pmpp / 1e6,
            'efficiency': efficiency,
            'kW_per_m2': pmpp / total_area / 1000,
        }


class CombinerBox:
    """
    汇流箱模型
    Combiner Box Model
    
    将多个光伏串并联汇流到一个输出
    """
    
    def __init__(self,
                 num_strings: int,
                 name: str = "Combiner Box"):
        """
        初始化汇流箱
        
        Parameters:
        -----------
        num_strings : int
            接入光伏串数量
        name : str
            汇流箱名称
        """
        self.num_strings = num_strings
        self.name = name
        
        # 保护元件
        self.has_fuses = True           # 熔断器
        self.has_surge_protector = True  # 防雷器
        self.has_breaker = True         # 断路器
    
    def get_specifications(self) -> dict:
        """获取汇流箱规格"""
        return {
            'name': self.name,
            'num_strings': self.num_strings,
            'fuses': self.has_fuses,
            'surge_protector': self.has_surge_protector,
            'breaker': self.has_breaker,
        }
