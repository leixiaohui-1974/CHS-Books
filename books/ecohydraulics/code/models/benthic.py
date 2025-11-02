"""底栖生物栖息地模型"""
import numpy as np
from typing import Dict
from .channel import RiverReach

class BenthicHabitatModel:
    """底栖生物栖息地评价模型"""
    
    @staticmethod
    def bed_shear_stress(reach: RiverReach, h: float) -> float:
        """计算床面剪切应力 τ = ρ * g * R * S"""
        rho = 1000
        g = 9.81
        R = reach.hydraulic_radius(h)
        tau = rho * g * R * reach.S0
        return tau
    
    @staticmethod
    def shields_number(tau: float, d50: float, rho_s: float = 2650) -> float:
        """Shields数 θ = τ / ((ρ_s - ρ) * g * d50)"""
        rho = 1000
        g = 9.81
        theta = tau / ((rho_s - rho) * g * d50)
        return theta
    
    @staticmethod
    def substrate_stability(theta: float) -> Dict:
        """评估底质稳定性"""
        theta_c = 0.05  # 临界Shields数
        if theta < theta_c * 0.5:
            status = "稳定"
        elif theta < theta_c:
            status = "基本稳定"
        elif theta < theta_c * 1.5:
            status = "临界"
        else:
            status = "不稳定"
        return {'theta': theta, 'theta_critical': theta_c, 'status': status}
