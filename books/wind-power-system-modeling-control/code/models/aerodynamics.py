"""
气动学模型

本模块包含风力机气动学的核心功能:
- 叶素动量理论 (BEM - Blade Element Momentum)
- 升力和阻力系数
- 诱导因子计算
- Prandtl叶尖损失修正
- 风轮转矩和功率计算
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from scipy.optimize import fsolve


# ==================== 翼型气动特性 ====================

class AirfoilData:
    """
    翼型气动数据
    
    存储升力系数Cl和阻力系数Cd随攻角α的变化
    """
    
    def __init__(self, alpha: np.ndarray, Cl: np.ndarray, Cd: np.ndarray,
                 name: str = "Airfoil"):
        """
        初始化翼型数据
        
        Args:
            alpha: 攻角数组 (度)
            Cl: 升力系数数组
            Cd: 阻力系数数组
            name: 翼型名称
        """
        self.alpha = np.asarray(alpha)
        self.Cl = np.asarray(Cl)
        self.Cd = np.asarray(Cd)
        self.name = name
        
        # 验证数据长度
        if not (len(self.alpha) == len(self.Cl) == len(self.Cd)):
            raise ValueError("攻角、Cl和Cd数组长度必须相同")
    
    def get_Cl(self, alpha_query: float) -> float:
        """
        插值获取升力系数
        
        Args:
            alpha_query: 查询攻角 (度)
            
        Returns:
            升力系数
        """
        return np.interp(alpha_query, self.alpha, self.Cl)
    
    def get_Cd(self, alpha_query: float) -> float:
        """
        插值获取阻力系数
        
        Args:
            alpha_query: 查询攻角 (度)
            
        Returns:
            阻力系数
        """
        return np.interp(alpha_query, self.alpha, self.Cd)
    
    def get_Cl_Cd(self, alpha_query: float) -> Tuple[float, float]:
        """
        同时获取Cl和Cd
        
        Args:
            alpha_query: 查询攻角 (度)
            
        Returns:
            (Cl, Cd)
        """
        Cl = self.get_Cl(alpha_query)
        Cd = self.get_Cd(alpha_query)
        return Cl, Cd
    
    @staticmethod
    def create_flat_plate(alpha_range: np.ndarray = None) -> 'AirfoilData':
        """
        创建理想平板翼型（用于演示）
        
        Cl = 2π * sin(α)
        Cd = 0.01 + 0.02 * (Cl)²
        
        Args:
            alpha_range: 攻角范围 (度)
            
        Returns:
            翼型数据对象
        """
        if alpha_range is None:
            alpha_range = np.linspace(-10, 20, 61)
        
        alpha_rad = np.deg2rad(alpha_range)
        Cl = 2 * np.pi * np.sin(alpha_rad)
        Cd = 0.01 + 0.02 * Cl**2
        
        return AirfoilData(alpha_range, Cl, Cd, name="Flat_Plate")
    
    @staticmethod
    def create_naca0012(alpha_range: np.ndarray = None) -> 'AirfoilData':
        """
        创建简化的NACA0012翼型数据
        
        Args:
            alpha_range: 攻角范围 (度)
            
        Returns:
            翼型数据对象
        """
        if alpha_range is None:
            alpha_range = np.linspace(-10, 20, 61)
        
        # 简化模型（实际应使用CFD或风洞数据）
        alpha_rad = np.deg2rad(alpha_range)
        Cl = 6.28 * alpha_rad  # 线性段
        
        # 失速修正
        stall_angle = 12  # 度
        for i, a in enumerate(alpha_range):
            if abs(a) > stall_angle:
                Cl[i] = Cl[i] * np.cos(np.deg2rad(abs(a) - stall_angle))
        
        Cd = 0.008 + 0.01 * Cl**2
        
        return AirfoilData(alpha_range, Cl, Cd, name="NACA0012")
    
    def get_status(self) -> Dict:
        """返回翼型数据状态"""
        return {
            'name': self.name,
            'alpha_range': (self.alpha.min(), self.alpha.max()),
            'Cl_max': self.Cl.max(),
            'Cd_min': self.Cd.min()
        }


# ==================== 叶素动量理论 ====================

class BEMSolver:
    """
    叶素动量理论 (Blade Element Momentum) 求解器
    
    用于计算风轮的气动性能
    """
    
    def __init__(self, R: float, r_hub: float, B: int,
                 airfoil: AirfoilData, chord: np.ndarray, twist: np.ndarray,
                 max_iter: int = 100, tol: float = 1e-5,
                 name: str = "BEM_Solver"):
        """
        初始化BEM求解器
        
        Args:
            R: 风轮半径 (m)
            r_hub: 轮毂半径 (m)
            B: 叶片数
            airfoil: 翼型气动数据
            chord: 弦长分布 (m)，与径向位置对应
            twist: 扭角分布 (度)，与径向位置对应
            max_iter: 最大迭代次数
            tol: 收敛容差
            name: 求解器名称
        """
        self.R = R
        self.r_hub = r_hub
        self.B = B
        self.airfoil = airfoil
        self.chord = np.asarray(chord)
        self.twist = np.asarray(twist)
        self.max_iter = max_iter
        self.tol = tol
        self.name = name
        
        # 验证输入
        if R <= r_hub:
            raise ValueError("风轮半径必须大于轮毂半径")
        if B < 1:
            raise ValueError("叶片数必须至少为1")
    
    def solve_blade_element(self, r: float, chord_local: float, 
                           twist_local: float, v_wind: float, omega: float,
                           a_init: float = 0.2, a_prime_init: float = 0.01) -> Dict:
        """
        求解单个叶素的诱导因子
        
        Args:
            r: 径向位置 (m)
            chord_local: 该位置的弦长 (m)
            twist_local: 该位置的扭角 (度)
            v_wind: 来流风速 (m/s)
            omega: 风轮角速度 (rad/s)
            a_init: 轴向诱导因子初值
            a_prime_init: 切向诱导因子初值
            
        Returns:
            包含诱导因子、气动力等的字典
        """
        # 初始化
        a = a_init
        a_prime = a_prime_init
        
        # 迭代求解
        for iteration in range(self.max_iter):
            a_old = a
            a_prime_old = a_prime
            
            # 1. 计算流动角phi
            v_axial = v_wind * (1 - a)
            v_tangential = omega * r * (1 + a_prime)
            
            if v_axial <= 0:
                v_axial = 1e-6  # 防止除零
            
            phi = np.arctan2(v_axial, v_tangential)  # rad
            phi_deg = np.rad2deg(phi)
            
            # 2. 计算攻角 alpha
            alpha = phi_deg - twist_local  # 度
            
            # 3. 获取Cl和Cd
            Cl, Cd = self.airfoil.get_Cl_Cd(alpha)
            
            # 4. 计算法向力和切向力系数
            Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
            Ct = Cl * np.sin(phi) - Cd * np.cos(phi)
            
            # 5. 计算实度 (solidity)
            sigma = self.B * chord_local / (2 * np.pi * r)
            
            # 6. Prandtl叶尖损失修正
            F = self.prandtl_tip_loss_factor(r, phi)
            
            # 7. 更新轴向诱导因子a
            if a < 0.4:  # 动量理论适用
                a_new = 1 / (4 * F * np.sin(phi)**2 / (sigma * Cn) + 1)
            else:  # Glauert经验修正
                K = 4 * F * np.sin(phi)**2 / (sigma * Cn)
                a_new = 0.5 * (2 + K * (1 - 2 * 0.889) - 
                               np.sqrt((K * (1 - 2 * 0.889) + 2)**2 + 
                                      4 * (K * 0.889**2 - 1)))
            
            # 8. 更新切向诱导因子a'
            a_prime_new = 1 / (4 * F * np.sin(phi) * np.cos(phi) / 
                              (sigma * Ct) - 1)
            
            # 限制诱导因子范围
            a_new = np.clip(a_new, 0, 0.95)
            a_prime_new = np.clip(a_prime_new, -0.5, 0.5)
            
            # 9. 松弛因子（提高收敛性）
            relax = 0.5
            a = relax * a_new + (1 - relax) * a
            a_prime = relax * a_prime_new + (1 - relax) * a_prime
            
            # 10. 检查收敛
            if abs(a - a_old) < self.tol and abs(a_prime - a_prime_old) < self.tol:
                break
        
        # 计算气动力
        v_rel = np.sqrt(v_axial**2 + v_tangential**2)
        q = 0.5 * 1.225 * v_rel**2  # 动压 (ρ=1.225 kg/m³)
        
        dL = q * chord_local * Cl  # 升力 per unit span (N/m)
        dD = q * chord_local * Cd  # 阻力 per unit span (N/m)
        dFn = dL * np.cos(phi) + dD * np.sin(phi)  # 法向力 (N/m)
        dFt = dL * np.sin(phi) - dD * np.cos(phi)  # 切向力 (N/m)
        
        return {
            'r': r,
            'a': a,
            'a_prime': a_prime,
            'phi': phi_deg,
            'alpha': alpha,
            'Cl': Cl,
            'Cd': Cd,
            'Cn': Cn,
            'Ct': Ct,
            'F': F,
            'v_rel': v_rel,
            'dFn': dFn,
            'dFt': dFt,
            'converged': iteration < self.max_iter - 1
        }
    
    def prandtl_tip_loss_factor(self, r: float, phi: float) -> float:
        """
        Prandtl叶尖损失修正因子
        
        Args:
            r: 径向位置 (m)
            phi: 流动角 (rad)
            
        Returns:
            修正因子F (0-1)
        """
        if abs(np.sin(phi)) < 1e-6:
            return 1.0
        
        f = self.B / 2 * (self.R - r) / (r * abs(np.sin(phi)))
        F = 2 / np.pi * np.arccos(np.exp(-f))
        
        # 限制范围
        F = np.clip(F, 0.01, 1.0)
        
        return F
    
    def solve_rotor(self, v_wind: float, omega: float, 
                   n_elements: int = 20) -> Dict:
        """
        求解整个风轮
        
        Args:
            v_wind: 来流风速 (m/s)
            omega: 风轮角速度 (rad/s)
            n_elements: 叶素数量
            
        Returns:
            风轮气动性能结果
        """
        # 径向位置
        r_array = np.linspace(self.r_hub, self.R, n_elements)
        dr = r_array[1] - r_array[0]
        
        # 弦长和扭角分布（插值）
        r_design = np.linspace(self.r_hub, self.R, len(self.chord))
        chord_array = np.interp(r_array, r_design, self.chord)
        twist_array = np.interp(r_array, r_design, self.twist)
        
        # 初始化结果存储
        results = []
        
        # 对每个叶素求解
        for i, r in enumerate(r_array):
            result = self.solve_blade_element(
                r, chord_array[i], twist_array[i], 
                v_wind, omega
            )
            results.append(result)
        
        # 积分计算总转矩和功率
        torque_total = 0
        thrust_total = 0
        
        for i, result in enumerate(results):
            # 每个叶素的贡献
            dT = result['dFt'] * result['r'] * self.B * dr  # 转矩 (N·m)
            dThrust = result['dFn'] * self.B * dr  # 推力 (N)
            
            torque_total += dT
            thrust_total += dThrust
        
        # 功率
        power = torque_total * omega  # W
        
        # 风轮扫掠面积
        A = np.pi * (self.R**2 - self.r_hub**2)
        
        # 可用功率
        P_available = 0.5 * 1.225 * A * v_wind**3
        
        # 功率系数Cp
        Cp = power / P_available if P_available > 0 else 0
        
        # 推力系数Ct
        Ct = thrust_total / (0.5 * 1.225 * A * v_wind**2) if v_wind > 0 else 0
        
        return {
            'v_wind': v_wind,
            'omega': omega,
            'TSR': omega * self.R / v_wind if v_wind > 0 else 0,
            'torque': torque_total,
            'power': power,
            'thrust': thrust_total,
            'Cp': Cp,
            'Ct': Ct,
            'blade_elements': results,
            'r_array': r_array
        }
    
    def get_status(self) -> Dict:
        """返回求解器状态"""
        return {
            'name': self.name,
            'R': self.R,
            'r_hub': self.r_hub,
            'B': self.B,
            'airfoil': self.airfoil.name
        }


# ==================== 简化风轮模型 ====================

class SimpleRotor:
    """
    简化风轮模型
    
    使用经验公式快速计算Cp-λ曲线
    """
    
    def __init__(self, R: float, Cp_max: float = 0.48, 
                 lambda_opt: float = 8.0, name: str = "SimpleRotor"):
        """
        初始化简化风轮模型
        
        Args:
            R: 风轮半径 (m)
            Cp_max: 最大功率系数
            lambda_opt: 最优叶尖速比
            name: 模型名称
        """
        self.R = R
        self.Cp_max = Cp_max
        self.lambda_opt = lambda_opt
        self.name = name
    
    def Cp_curve(self, lambda_val: float) -> float:
        """
        功率系数曲线（经验公式）
        
        Args:
            lambda_val: 叶尖速比 λ = ωR/v
            
        Returns:
            功率系数Cp
        """
        # 简化的Cp-λ曲线（高斯型）
        Cp = self.Cp_max * np.exp(-0.5 * ((lambda_val - self.lambda_opt) / 3)**2)
        
        return Cp
    
    def calculate_power(self, v_wind: float, omega: float, 
                       rho: float = 1.225) -> Dict:
        """
        计算风轮功率
        
        Args:
            v_wind: 风速 (m/s)
            omega: 角速度 (rad/s)
            rho: 空气密度 (kg/m³)
            
        Returns:
            功率计算结果
        """
        # 叶尖速比
        lambda_val = omega * self.R / v_wind if v_wind > 0 else 0
        
        # 功率系数
        Cp = self.Cp_curve(lambda_val)
        
        # 扫掠面积
        A = np.pi * self.R**2
        
        # 可用功率
        P_available = 0.5 * rho * A * v_wind**3
        
        # 实际功率
        P = Cp * P_available
        
        # 转矩
        T = P / omega if omega > 0 else 0
        
        return {
            'v_wind': v_wind,
            'omega': omega,
            'lambda': lambda_val,
            'Cp': Cp,
            'power': P,
            'torque': T,
            'P_available': P_available
        }
    
    def get_status(self) -> Dict:
        """返回模型状态"""
        return {
            'name': self.name,
            'R': self.R,
            'Cp_max': self.Cp_max,
            'lambda_opt': self.lambda_opt
        }


# ==================== 辅助函数 ====================

def calculate_tip_speed_ratio(omega: float, R: float, v_wind: float) -> float:
    """
    计算叶尖速比
    
    λ = ωR / v
    
    Args:
        omega: 角速度 (rad/s)
        R: 风轮半径 (m)
        v_wind: 风速 (m/s)
        
    Returns:
        叶尖速比
    """
    if v_wind <= 0:
        return 0
    
    return omega * R / v_wind


def design_blade_twist(r_array: np.ndarray, R: float, 
                      lambda_design: float = 8.0) -> np.ndarray:
    """
    设计叶片扭角分布（简化方法）
    
    Args:
        r_array: 径向位置数组 (m)
        R: 风轮半径 (m)
        lambda_design: 设计叶尖速比
        
    Returns:
        扭角数组 (度)
    """
    # 局部速比
    lambda_r = lambda_design * r_array / R
    
    # 最优入流角（简化假设）
    phi_opt = np.rad2deg(2 / 3 * np.arctan(1 / lambda_r))
    
    # 扭角（假设最优攻角为6度）
    alpha_opt = 6  # 度
    twist = phi_opt - alpha_opt
    
    return twist


def design_blade_chord(r_array: np.ndarray, R: float, B: int,
                      Cl_design: float = 1.0) -> np.ndarray:
    """
    设计叶片弦长分布（简化方法）
    
    Args:
        r_array: 径向位置数组 (m)
        R: 风轮半径 (m)
        B: 叶片数
        Cl_design: 设计升力系数
        
    Returns:
        弦长数组 (m)
    """
    # 简化的线性分布
    chord = 0.1 * R * (1 - r_array / R)
    
    # 最小弦长
    chord = np.maximum(chord, 0.01 * R)
    
    return chord
