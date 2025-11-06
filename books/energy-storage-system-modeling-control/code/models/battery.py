"""
电池建模模块

包含:
1. 锂离子电池模型 (Thevenin等效电路)
2. 电池SOC/SOH估算
3. 电池热模型
4. 铅酸电池模型
5. 液流电池模型
6. 超级电容模型

作者: CHS Books
"""

import numpy as np
from typing import Dict, Tuple
from scipy.interpolate import interp1d
from scipy.integrate import odeint


class LithiumBatteryThevenin:
    """
    锂离子电池Thevenin等效电路模型
    
    模型结构:
        OCV(SOC) -- R0 -- [R1-C1] -- Terminal
        
    参数:
        - OCV: 开路电压 (与SOC相关)
        - R0: 欧姆内阻
        - R1, C1: 一阶RC网络 (极化阻抗)
    """
    
    def __init__(
        self,
        capacity: float = 50.0,  # Ah
        R0: float = 0.01,  # Ohm
        R1: float = 0.015,  # Ohm
        C1: float = 2000.0,  # F
        soc_ocv_curve: Dict = None,
        name: str = "LiIonBattery"
    ):
        """
        初始化锂电池模型
        
        Args:
            capacity: 额定容量 (Ah)
            R0: 欧姆内阻
            R1, C1: RC极化网络参数
            soc_ocv_curve: SOC-OCV曲线数据
        """
        self.name = name
        self.capacity = capacity  # Ah
        self.R0 = R0
        self.R1 = R1
        self.C1 = C1
        
        # SOC-OCV曲线（典型的锂电池）
        if soc_ocv_curve is None:
            self.soc_points = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
            self.ocv_points = np.array([2.8, 3.2, 3.4, 3.5, 3.6, 3.65, 3.7, 3.75, 3.85, 4.0, 4.2])
        else:
            self.soc_points = np.array(soc_ocv_curve['soc'])
            self.ocv_points = np.array(soc_ocv_curve['ocv'])
        
        # 插值函数
        self.ocv_func = interp1d(self.soc_points, self.ocv_points, 
                                kind='cubic', fill_value='extrapolate')
        
        # 状态变量
        self.soc = 0.8  # 初始SOC
        self.V1 = 0.0   # RC网络电压
        
    def get_ocv(self, soc: float) -> float:
        """获取开路电压"""
        return float(self.ocv_func(np.clip(soc, 0, 1)))
    
    def get_terminal_voltage(self, I: float) -> float:
        """
        计算端电压
        
        Args:
            I: 电流 (A), 充电为正，放电为负
            
        Returns:
            端电压 (V)
        """
        ocv = self.get_ocv(self.soc)
        V_terminal = ocv - I * self.R0 - self.V1
        return V_terminal
    
    def update_states(self, I: float, dt: float):
        """
        更新状态变量
        
        Args:
            I: 电流 (A)
            dt: 时间步长 (s)
        """
        # 更新SOC (安时积分法)
        self.soc += -I * dt / (self.capacity * 3600)
        self.soc = np.clip(self.soc, 0, 1)
        
        # 更新RC网络电压 (一阶动态)
        tau = self.R1 * self.C1
        dV1_dt = (I * self.R1 - self.V1) / tau
        self.V1 += dV1_dt * dt
    
    def simulate_discharge(
        self,
        I_discharge: float,
        duration: float,
        dt: float = 1.0
    ) -> Dict:
        """
        仿真恒流放电过程
        
        Args:
            I_discharge: 放电电流 (A, 正值)
            duration: 放电时间 (s)
            dt: 时间步长 (s)
            
        Returns:
            仿真结果
        """
        n_steps = int(duration / dt)
        t = np.zeros(n_steps)
        soc = np.zeros(n_steps)
        V_terminal = np.zeros(n_steps)
        V_ocv = np.zeros(n_steps)
        V_rc = np.zeros(n_steps)
        power = np.zeros(n_steps)
        
        for i in range(n_steps):
            t[i] = i * dt
            soc[i] = self.soc
            V_ocv[i] = self.get_ocv(self.soc)
            V_terminal[i] = self.get_terminal_voltage(-I_discharge)
            V_rc[i] = self.V1
            power[i] = V_terminal[i] * I_discharge
            
            self.update_states(-I_discharge, dt)
            
            # 截止电压检查
            if V_terminal[i] < 2.5:
                t = t[:i+1]
                soc = soc[:i+1]
                V_terminal = V_terminal[:i+1]
                V_ocv = V_ocv[:i+1]
                V_rc = V_rc[:i+1]
                power = power[:i+1]
                break
        
        return {
            't': t,
            'soc': soc,
            'V_terminal': V_terminal,
            'V_ocv': V_ocv,
            'V_rc': V_rc,
            'power': power,
            'energy': np.trapz(power, t) / 3600,  # Wh
        }


class BatterySOCEstimator:
    """
    电池SOC估算器
    
    方法1: 安时积分法 (Coulomb Counting)
    方法2: 扩展卡尔曼滤波 (EKF)
    """
    
    def __init__(
        self,
        capacity: float = 50.0,
        initial_soc: float = 0.8,
        method: str = 'coulomb_counting'
    ):
        """
        初始化SOC估算器
        
        Args:
            capacity: 电池容量 (Ah)
            initial_soc: 初始SOC
            method: 'coulomb_counting' 或 'ekf'
        """
        self.capacity = capacity
        self.soc = initial_soc
        self.method = method
        
        # EKF参数
        if method == 'ekf':
            self.P = 0.01  # 状态估计误差协方差
            self.Q = 1e-6  # 过程噪声协方差
            self.R = 0.01  # 测量噪声协方差
    
    def coulomb_counting(self, I: float, dt: float) -> float:
        """
        安时积分法估算SOC
        
        Args:
            I: 电流 (A), 充电为正
            dt: 时间步长 (s)
            
        Returns:
            SOC
        """
        self.soc += -I * dt / (self.capacity * 3600)
        self.soc = np.clip(self.soc, 0, 1)
        return self.soc
    
    def ekf_update(
        self,
        I: float,
        V_measured: float,
        battery_model: LithiumBatteryThevenin,
        dt: float
    ) -> float:
        """
        扩展卡尔曼滤波更新SOC
        
        Args:
            I: 电流 (A)
            V_measured: 测量端电压 (V)
            battery_model: 电池模型
            dt: 时间步长 (s)
            
        Returns:
            估算的SOC
        """
        # 预测步骤
        soc_pred = self.soc - I * dt / (self.capacity * 3600)
        soc_pred = np.clip(soc_pred, 0, 1)
        
        # 预测协方差
        P_pred = self.P + self.Q
        
        # 计算预测电压
        V_pred = battery_model.get_ocv(soc_pred) - I * battery_model.R0 - battery_model.V1
        
        # 计算雅可比矩阵 (数值微分)
        delta = 0.001
        V_plus = battery_model.get_ocv(soc_pred + delta) - I * battery_model.R0 - battery_model.V1
        V_minus = battery_model.get_ocv(soc_pred - delta) - I * battery_model.R0 - battery_model.V1
        H = (V_plus - V_minus) / (2 * delta)  # dV/dSOC
        
        # 卡尔曼增益
        K = P_pred * H / (H * P_pred * H + self.R)
        
        # 更新步骤
        innovation = V_measured - V_pred
        self.soc = soc_pred + K * innovation
        self.soc = np.clip(self.soc, 0, 1)
        
        # 更新协方差
        self.P = (1 - K * H) * P_pred
        
        return self.soc


class BatterySOHEstimator:
    """
    电池健康状态(SOH)估算器
    
    SOH = 当前容量 / 初始容量 × 100%
    """
    
    def __init__(
        self,
        initial_capacity: float = 50.0,
        cycle_count: int = 0
    ):
        """
        初始化SOH估算器
        
        Args:
            initial_capacity: 初始容量 (Ah)
            cycle_count: 循环次数
        """
        self.initial_capacity = initial_capacity
        self.current_capacity = initial_capacity
        self.cycle_count = cycle_count
    
    def estimate_soh_linear(self, cycles: int) -> float:
        """
        线性衰减模型估算SOH
        
        典型锂电池: 500次循环衰减至80%
        
        Args:
            cycles: 累计循环次数
            
        Returns:
            SOH (0-1)
        """
        degradation_rate = 0.2 / 500  # 每次循环衰减0.04%
        soh = 1.0 - degradation_rate * cycles
        soh = max(0.5, soh)  # 最低50%
        self.current_capacity = soh * self.initial_capacity
        return soh
    
    def estimate_soh_nonlinear(self, cycles: int) -> float:
        """
        非线性衰减模型
        
        采用指数衰减 + 线性衰减组合
        
        Args:
            cycles: 累计循环次数
            
        Returns:
            SOH (0-1)
        """
        # 指数衰减部分 (前期快速衰减)
        exp_part = 0.05 * (1 - np.exp(-cycles / 100))
        
        # 线性衰减部分 (后期稳定衰减)
        lin_part = 0.15 * cycles / 500
        
        soh = 1.0 - exp_part - lin_part
        soh = max(0.5, soh)
        self.current_capacity = soh * self.initial_capacity
        return soh


class BatteryThermalModel:
    """
    电池热模型 (集总参数模型)
    
    简化为单一温度节点
    """
    
    def __init__(
        self,
        mass: float = 1.0,  # kg
        specific_heat: float = 1000.0,  # J/(kg·K)
        h_conv: float = 10.0,  # W/(m²·K), 对流换热系数
        A_surface: float = 0.1,  # m², 表面积
        T_ambient: float = 25.0,  # °C
        T_init: float = 25.0,  # °C
        name: str = "BatteryThermal"
    ):
        """
        初始化热模型
        
        Args:
            mass: 电池质量
            specific_heat: 比热容
            h_conv: 对流换热系数
            A_surface: 表面积
            T_ambient: 环境温度
            T_init: 初始温度
        """
        self.name = name
        self.mass = mass
        self.cp = specific_heat
        self.h_conv = h_conv
        self.A_surface = A_surface
        self.T_ambient = T_ambient
        self.T = T_init
    
    def compute_heat_generation(self, I: float, V_terminal: float, V_ocv: float) -> float:
        """
        计算产热功率
        
        Q_gen = I² * R_total = I * (V_ocv - V_terminal)
        
        Args:
            I: 电流 (A)
            V_terminal: 端电压 (V)
            V_ocv: 开路电压 (V)
            
        Returns:
            产热功率 (W)
        """
        Q_gen = abs(I * (V_ocv - V_terminal))
        return Q_gen
    
    def update_temperature(self, Q_gen: float, dt: float):
        """
        更新电池温度
        
        能量平衡: m*cp*dT/dt = Q_gen - Q_loss
        Q_loss = h*A*(T - T_ambient)
        
        Args:
            Q_gen: 产热功率 (W)
            dt: 时间步长 (s)
        """
        Q_loss = self.h_conv * self.A_surface * (self.T - self.T_ambient)
        dT_dt = (Q_gen - Q_loss) / (self.mass * self.cp)
        self.T += dT_dt * dt
    
    def simulate_thermal_response(
        self,
        Q_gen_profile: np.ndarray,
        t: np.ndarray
    ) -> np.ndarray:
        """
        仿真热响应
        
        Args:
            Q_gen_profile: 产热功率时间序列 (W)
            t: 时间序列 (s)
            
        Returns:
            温度时间序列 (°C)
        """
        T_history = np.zeros_like(t)
        T_history[0] = self.T
        
        for i in range(1, len(t)):
            dt = t[i] - t[i-1]
            self.update_temperature(Q_gen_profile[i-1], dt)
            T_history[i] = self.T
        
        return T_history


class BatteryPackBalancing:
    """
    电池组均衡控制
    
    串联电池组的主动/被动均衡
    """
    
    def __init__(
        self,
        n_cells: int = 10,
        balancing_type: str = 'passive',
        I_balance: float = 0.1,  # A, 均衡电流
        name: str = "PackBalancing"
    ):
        """
        初始化均衡控制器
        
        Args:
            n_cells: 串联单体数量
            balancing_type: 'passive'被动 或 'active'主动
            I_balance: 均衡电流
        """
        self.name = name
        self.n_cells = n_cells
        self.balancing_type = balancing_type
        self.I_balance = I_balance
        
        # 单体SOC（初始化为不均衡状态）
        self.cell_soc = np.linspace(0.7, 0.9, n_cells)
    
    def passive_balancing(self, dt: float) -> np.ndarray:
        """
        被动均衡（耗散式）
        
        对高SOC单体放电至平均值
        
        Args:
            dt: 时间步长 (s)
            
        Returns:
            均衡后的SOC
        """
        soc_mean = np.mean(self.cell_soc)
        
        for i in range(self.n_cells):
            if self.cell_soc[i] > soc_mean + 0.02:  # 阈值2%
                # 放电
                delta_soc = self.I_balance * dt / (50.0 * 3600)  # 假设50Ah容量
                self.cell_soc[i] -= delta_soc
        
        return self.cell_soc
    
    def active_balancing(self, dt: float) -> np.ndarray:
        """
        主动均衡（能量转移）
        
        从高SOC单体转移能量至低SOC单体
        
        Args:
            dt: 时间步长 (s)
            
        Returns:
            均衡后的SOC
        """
        soc_mean = np.mean(self.cell_soc)
        
        for i in range(self.n_cells):
            if abs(self.cell_soc[i] - soc_mean) > 0.02:
                # 均衡至平均值
                delta_soc = 0.5 * self.I_balance * dt / (50.0 * 3600)
                if self.cell_soc[i] > soc_mean:
                    self.cell_soc[i] -= delta_soc
                else:
                    self.cell_soc[i] += delta_soc
        
        return self.cell_soc


class LeadAcidBattery:
    """
    铅酸电池模型 (Shepherd模型)
    
    适用于传统铅酸电池
    """
    
    def __init__(
        self,
        capacity: float = 100.0,  # Ah
        V_nominal: float = 12.0,  # V
        R_internal: float = 0.02,  # Ohm
        name: str = "LeadAcid"
    ):
        """
        初始化铅酸电池模型
        
        Args:
            capacity: 额定容量 (Ah)
            V_nominal: 额定电压 (V)
            R_internal: 内阻 (Ohm)
        """
        self.name = name
        self.capacity = capacity
        self.V_nominal = V_nominal
        self.R_internal = R_internal
        
        # 状态
        self.soc = 0.8
    
    def get_voltage(self, I: float) -> float:
        """
        计算端电压（Shepherd模型简化）
        
        V = V0 - K*Q/(Q-it) - R*I + A*exp(-B*it)
        简化为: V = V_nominal * (0.85 + 0.15*SOC) - R*I
        
        Args:
            I: 电流 (A), 放电为负
            
        Returns:
            端电压 (V)
        """
        V_ocv = self.V_nominal * (0.85 + 0.15 * self.soc)
        V_terminal = V_ocv - I * self.R_internal
        return V_terminal
    
    def update_soc(self, I: float, dt: float):
        """更新SOC"""
        self.soc += -I * dt / (self.capacity * 3600)
        self.soc = np.clip(self.soc, 0, 1)


class VanadiumRedoxFlowBattery:
    """
    全钒液流电池模型
    
    功率与容量解耦
    """
    
    def __init__(
        self,
        power_rating: float = 100e3,  # W
        energy_capacity: float = 400e3,  # Wh
        efficiency: float = 0.75,
        name: str = "VRFB"
    ):
        """
        初始化液流电池模型
        
        Args:
            power_rating: 额定功率 (W)
            energy_capacity: 储能容量 (Wh)
            efficiency: 充放电效率
        """
        self.name = name
        self.P_rated = power_rating
        self.E_capacity = energy_capacity
        self.efficiency = efficiency
        
        # 状态
        self.soc = 0.5
    
    def charge(self, P_charge: float, dt: float):
        """
        充电
        
        Args:
            P_charge: 充电功率 (W)
            dt: 时间步长 (s)
        """
        P_charge = min(P_charge, self.P_rated)
        delta_E = P_charge * self.efficiency * dt / 3600  # Wh
        self.soc += delta_E / self.E_capacity
        self.soc = min(self.soc, 1.0)
    
    def discharge(self, P_discharge: float, dt: float) -> float:
        """
        放电
        
        Args:
            P_discharge: 放电功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            实际输出功率 (W)
        """
        P_discharge = min(P_discharge, self.P_rated)
        P_output = P_discharge * self.efficiency
        delta_E = P_discharge * dt / 3600  # Wh
        
        if self.soc * self.E_capacity >= delta_E:
            self.soc -= delta_E / self.E_capacity
            return P_output
        else:
            # SOC不足
            available_E = self.soc * self.E_capacity
            self.soc = 0
            return available_E * 3600 / dt * self.efficiency


class Supercapacitor:
    """
    超级电容模型
    
    简化为理想电容 + 等效串联电阻(ESR)
    """
    
    def __init__(
        self,
        capacitance: float = 3000.0,  # F
        esr: float = 0.001,  # Ohm
        V_rated: float = 2.7,  # V
        V_min: float = 1.35,  # V
        name: str = "Supercap"
    ):
        """
        初始化超级电容模型
        
        Args:
            capacitance: 电容值 (F)
            esr: 等效串联电阻 (Ohm)
            V_rated: 额定电压 (V)
            V_min: 最小工作电压 (V)
        """
        self.name = name
        self.C = capacitance
        self.ESR = esr
        self.V_rated = V_rated
        self.V_min = V_min
        
        # 状态
        self.V_cap = V_rated  # 电容电压
    
    def get_terminal_voltage(self, I: float) -> float:
        """计算端电压"""
        return self.V_cap - I * self.ESR
    
    def update_voltage(self, I: float, dt: float):
        """
        更新电容电压
        
        I = C * dV/dt
        
        Args:
            I: 电流 (A), 充电为正
            dt: 时间步长 (s)
        """
        self.V_cap += I * dt / self.C
        self.V_cap = np.clip(self.V_cap, self.V_min, self.V_rated)
    
    def get_stored_energy(self) -> float:
        """
        计算存储能量
        
        E = 0.5 * C * V²
        
        Returns:
            能量 (J)
        """
        return 0.5 * self.C * self.V_cap**2
    
    def get_soc(self) -> float:
        """
        计算SOC (基于能量)
        
        Returns:
            SOC (0-1)
        """
        E_current = self.get_stored_energy()
        E_rated = 0.5 * self.C * self.V_rated**2
        return E_current / E_rated
