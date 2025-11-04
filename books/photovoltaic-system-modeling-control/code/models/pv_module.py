"""
光伏组件模型
PV Module Model

光伏组件由多片电池串联组成,并配备旁路二极管
"""

from typing import Optional, List, Tuple
import numpy as np
from .pv_cell import PVCell, SingleDiodeModel, DoubleDiodeModel


class BypassDiode:
    """
    旁路二极管模型
    Bypass Diode Model
    
    用于防止热斑效应和部分遮挡时的功率损失
    """
    
    def __init__(self, 
                 Vf: float = 0.7,      # 正向压降 (V)
                 Rs: float = 0.01,     # 串联电阻 (Ω)
                 n: float = 1.0):      # 理想因子
        """
        初始化旁路二极管
        
        Parameters:
        -----------
        Vf : float
            正向压降 (V), 典型值0.5-0.9V
        Rs : float
            串联电阻 (Ω), 典型值0.01-0.05Ω
        n : float
            理想因子, 典型值1.0-1.2
        """
        self.Vf = Vf
        self.Rs = Rs
        self.n = n
        self.k = 1.380649e-23  # 玻尔兹曼常数
        self.q = 1.602176634e-19  # 电子电荷
        self.T = 298.15  # 温度(K)
        self.Vt = self.k * self.T / self.q
        
        # 反向饱和电流(估算)
        self.I0 = 1e-6
    
    def is_conducting(self, voltage: float) -> bool:
        """
        判断二极管是否导通
        
        Parameters:
        -----------
        voltage : float
            加在二极管上的电压(V)
            
        Returns:
        --------
        bool : 是否导通
        """
        # 当电压为负且绝对值超过导通电压时导通
        return voltage < -self.Vf
    
    def calculate_current(self, voltage: float) -> float:
        """
        计算旁路二极管电流
        
        正向: I ≈ 0 (截止)
        反向导通: 根据二极管方程计算
        
        Parameters:
        -----------
        voltage : float
            二极管电压(V)
            
        Returns:
        --------
        float : 电流(A)
        """
        if voltage >= 0:
            # 正向截止
            return 0.0
        else:
            # 反向,可能导通
            # 使用简化的指数模型
            if voltage < -self.Vf:
                # 导通,近似线性
                I = -(voltage + self.Vf) / self.Rs
                return max(0, I)
            else:
                # 未完全导通
                return 0.0


class PVModule:
    """
    光伏组件模型
    PV Module Model
    
    由Ns片电池串联组成,配备Nb个旁路二极管
    每个旁路二极管保护Ns/Nb片电池
    
    典型配置:
    - 60片组件: 60片串联, 3个旁路二极管
    - 72片组件: 72片串联, 3个旁路二极管
    - 每个二极管保护20-24片电池
    """
    
    def __init__(self,
                 cell_model: PVCell,
                 Ns: int = 60,
                 Nb: int = 3,
                 bypass_diode_Vf: float = 0.7,
                 name: str = "PV Module"):
        """
        初始化光伏组件
        
        Parameters:
        -----------
        cell_model : PVCell
            单片电池模型(作为模板)
        Ns : int
            串联电池片数量
        Nb : int
            旁路二极管数量
        bypass_diode_Vf : float
            旁路二极管正向压降(V)
        name : str
            组件名称
        """
        self.name = name
        self.Ns = Ns
        self.Nb = Nb
        self.cells_per_bypass = Ns // Nb  # 每个旁路二极管保护的电池数
        
        # 复制电池模板创建所有电池
        self.cells = []
        for i in range(Ns):
            # 创建新电池实例
            if isinstance(cell_model, SingleDiodeModel):
                cell = SingleDiodeModel(
                    Isc=cell_model.Isc_stc,
                    Voc=cell_model.Voc_stc,
                    Imp=cell_model.Imp_stc,
                    Vmp=cell_model.Vmp_stc,
                    T=cell_model.T,
                    G=cell_model.G,
                    name=f"Cell-{i+1}"
                )
            elif isinstance(cell_model, DoubleDiodeModel):
                cell = DoubleDiodeModel(
                    Isc=cell_model.Isc_stc,
                    Voc=cell_model.Voc_stc,
                    Imp=cell_model.Imp_stc,
                    Vmp=cell_model.Vmp_stc,
                    T=cell_model.T,
                    G=cell_model.G,
                    n1=cell_model.n1,
                    n2=cell_model.n2,
                    name=f"Cell-{i+1}"
                )
            else:
                raise ValueError(f"Unsupported cell model type: {type(cell_model)}")
            
            self.cells.append(cell)
        
        # 创建旁路二极管
        self.bypass_diodes = []
        for i in range(Nb):
            diode = BypassDiode(Vf=bypass_diode_Vf)
            self.bypass_diodes.append(diode)
        
        # 组件特性参数
        self.Voc = cell_model.Voc * Ns  # 开路电压 ≈ Ns * Voc_cell
        self.Isc = cell_model.Isc       # 短路电流 ≈ Isc_cell
        self.Vmp = cell_model.Vmp_stc * Ns
        self.Imp = cell_model.Imp_stc
        self.Pmp = self.Vmp * self.Imp
    
    def set_cell_irradiance(self, irradiances: List[float]):
        """
        设置每片电池的辐照度(用于遮挡仿真)
        
        Parameters:
        -----------
        irradiances : List[float]
            每片电池的辐照度列表(W/m²)
        """
        if len(irradiances) != self.Ns:
            raise ValueError(f"Need {self.Ns} irradiance values, got {len(irradiances)}")
        
        for i, G in enumerate(irradiances):
            self.cells[i].update_conditions(G=G)
    
    def set_cell_temperature(self, temperatures: List[float]):
        """
        设置每片电池的温度
        
        Parameters:
        -----------
        temperatures : List[float]
            每片电池的温度列表(K)
        """
        if len(temperatures) != self.Ns:
            raise ValueError(f"Need {self.Ns} temperature values, got {len(temperatures)}")
        
        for i, T in enumerate(temperatures):
            self.cells[i].update_conditions(T=T)
    
    def set_uniform_conditions(self, T: float, G: float):
        """
        设置所有电池的统一工作条件
        
        Parameters:
        -----------
        T : float
            温度(K)
        G : float
            辐照度(W/m²)
        """
        for cell in self.cells:
            cell.update_conditions(T=T, G=G)
    
    def calculate_current(self, voltage: float) -> float:
        """
        计算给定电压下的组件电流
        
        考虑旁路二极管的影响
        串联电池的电流相同,电压相加
        
        Parameters:
        -----------
        voltage : float
            组件总电压(V)
            
        Returns:
        --------
        float : 组件电流(A)
        """
        # 使用迭代方法求解
        # 假设电流I,计算各部分电压,使其和等于总电压
        
        def voltage_residual(I):
            """计算电压差"""
            V_total = 0.0
            
            # 遍历每个旁路二极管保护的子串
            for i in range(self.Nb):
                start_idx = i * self.cells_per_bypass
                end_idx = start_idx + self.cells_per_bypass
                
                # 计算子串的总电压
                V_substring = 0.0
                for j in range(start_idx, min(end_idx, self.Ns)):
                    # 每片电池在电流I下的电压
                    # 使用反函数(从I求V)
                    V_cell = self._cell_voltage(self.cells[j], I)
                    V_substring += V_cell
                
                # 检查旁路二极管
                diode = self.bypass_diodes[i]
                if V_substring < -diode.Vf:
                    # 旁路二极管导通
                    V_bypass = -diode.Vf - I * diode.Rs
                    V_total += V_bypass
                else:
                    # 旁路二极管不导通
                    V_total += V_substring
            
            return V_total - voltage
        
        # 搜索合适的电流
        from scipy.optimize import fsolve, brentq
        
        # 初始猜测
        I_guess = self.Isc * 0.5
        
        try:
            I = fsolve(voltage_residual, I_guess, full_output=False)[0]
            return max(0, I)
        except:
            return 0.0
    
    def _cell_voltage(self, cell: PVCell, current: float) -> float:
        """
        计算给定电流下的电池电压(反函数)
        
        通过搜索找到V使得I(V) = current
        """
        # 边界情况
        if current <= 0:
            return cell.Voc
        if current >= cell.Isc:
            return 0.0
        
        # 二分搜索
        V_low = 0.0
        V_high = cell.Voc
        tolerance = 1e-4
        
        for _ in range(50):
            V_mid = (V_low + V_high) / 2
            I_mid = cell.calculate_current(V_mid)
            
            if abs(I_mid - current) < tolerance:
                return V_mid
            
            if I_mid > current:
                V_low = V_mid
            else:
                V_high = V_mid
        
        return (V_low + V_high) / 2
    
    def get_iv_curve(self, num_points: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取I-V特性曲线
        
        Parameters:
        -----------
        num_points : int
            曲线点数
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray] : 电压数组, 电流数组
        """
        # 电压范围: 0 到 Voc
        V_max = self.Voc * 1.1
        voltages = np.linspace(0, V_max, num_points)
        currents = np.array([self.calculate_current(v) for v in voltages])
        
        return voltages, currents
    
    def get_pv_curve(self, num_points: int = 300) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取P-V特性曲线
        """
        V, I = self.get_iv_curve(num_points)
        P = V * I
        return V, P
    
    def find_mpp(self) -> Tuple[float, float, float]:
        """
        寻找最大功率点
        
        Returns:
        --------
        Tuple[float, float, float] : Vmpp, Impp, Pmpp
        """
        V, P = self.get_pv_curve(500)
        idx = np.argmax(P)
        Vmpp = V[idx]
        Pmpp = P[idx]
        Impp = Pmpp / Vmpp if Vmpp > 0 else 0
        
        return Vmpp, Impp, Pmpp
    
    def get_parameters(self) -> dict:
        """获取组件参数"""
        return {
            'name': self.name,
            'Ns': self.Ns,
            'Nb': self.Nb,
            'cells_per_bypass': self.cells_per_bypass,
            'Voc': self.Voc,
            'Isc': self.Isc,
            'Vmp': self.Vmp,
            'Imp': self.Imp,
            'Pmp': self.Pmp,
        }
    
    def print_parameters(self):
        """打印组件参数"""
        params = self.get_parameters()
        print(f"\n{self.name} - 组件参数")
        print("=" * 60)
        print(f"配置:")
        print(f"  串联电池数 Ns:         {params['Ns']} 片")
        print(f"  旁路二极管数 Nb:       {params['Nb']} 个")
        print(f"  每组电池数:            {params['cells_per_bypass']} 片/组")
        print(f"\n额定参数:")
        print(f"  开路电压 Voc:          {params['Voc']:.2f} V")
        print(f"  短路电流 Isc:          {params['Isc']:.3f} A")
        print(f"  最大功率点电压 Vmp:    {params['Vmp']:.2f} V")
        print(f"  最大功率点电流 Imp:    {params['Imp']:.3f} A")
        print(f"  最大功率 Pmp:          {params['Pmp']:.2f} W")
        print("=" * 60)
