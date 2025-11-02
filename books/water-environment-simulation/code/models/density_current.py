"""
水库异重流模拟（简化2D模型）
Simplified 2D Density Current Model for Reservoir

模拟高浓度泥沙水流潜入水库底层的过程
"""

import numpy as np


class DensityCurrent2D:
    """
    简化的异重流模型
    
    基于密度差驱动的重力流
    """
    
    def __init__(self, L, H, nx, nz, rho_ambient=1000, sediment_conc=0):
        """
        初始化异重流模型
        
        参数：
        - L: 水库长度 (m)
        - H: 水深 (m)
        - nx: 水平节点数
        - nz: 垂向节点数
        - rho_ambient: 环境水体密度 (kg/m³)
        - sediment_conc: 泥沙浓度场初始值 (kg/m³)
        """
        self.L = L
        self.H = H
        self.nx = nx
        self.nz = nz
        self.dx = L / (nx - 1)
        self.dz = H / (nz - 1)
        
        self.x = np.linspace(0, L, nx)
        self.z = np.linspace(0, H, nz)
        
        self.rho_ambient = rho_ambient
        self.C = np.zeros((nz, nx))  # 泥沙浓度场
        
        print(f"异重流模型初始化:")
        print(f"  水库长度: {L} m")
        print(f"  水深: {H} m")
        print(f"  网格: {nx} × {nz}")
        print(f"  环境密度: {rho_ambient} kg/m³")
    
    def calculate_density(self, C):
        """
        根据泥沙浓度计算密度
        
        ρ = ρ₀(1 + β*C)
        β ≈ 0.0006 m³/kg (泥沙)
        
        参数：
        - C: 泥沙浓度 (kg/m³)
        
        返回：
        - rho: 密度 (kg/m³)
        """
        beta = 0.0006  # 泥沙密度效应系数
        return self.rho_ambient * (1 + beta * C)
    
    def calculate_plunge_point(self, C_inflow, Q_inflow, H_reservoir):
        """
        计算潜入点位置
        
        基于Froude数判断
        
        参数：
        - C_inflow: 入流泥沙浓度 (kg/m³)
        - Q_inflow: 入流流量 (m³/s)
        - H_reservoir: 水库水深 (m)
        
        返回：
        - x_plunge: 潜入点距离 (m)
        """
        g = 9.81
        rho_inflow = self.calculate_density(C_inflow)
        delta_rho = rho_inflow - self.rho_ambient
        
        # 约化重力
        g_prime = g * delta_rho / self.rho_ambient
        
        # 简化估算：基于经验公式
        # x_plunge ≈ (Q/B)/(√(g'*h))
        B = 100  # 假设河道宽度
        h = Q_inflow / (B * 1.0)  # 入流水深估算
        u = Q_inflow / (B * h)
        
        Fr = u / np.sqrt(g_prime * h) if g_prime > 0 else 999
        
        # 临界Froude数附近潜入
        if Fr > 1:
            x_plunge = h / np.tan(0.1)  # 急流，较远处潜入
        else:
            x_plunge = 0  # 立即潜入
        
        print(f"\n潜入点计算:")
        print(f"  入流密度: {rho_inflow:.1f} kg/m³")
        print(f"  密度差: {delta_rho:.2f} kg/m³")
        print(f"  约化重力: {g_prime:.4f} m/s²")
        print(f"  Froude数: {Fr:.2f}")
        print(f"  潜入点距离: {x_plunge:.1f} m")
        
        return x_plunge
    
    def simulate_underflow(self, C_source, x_source, dt, n_steps):
        """
        模拟异重流运动（简化）
        
        参数：
        - C_source: 源浓度 (kg/m³)
        - x_source: 源位置索引
        - dt: 时间步长 (s)
        - n_steps: 步数
        
        返回：
        - C: 最终浓度场
        """
        g = 9.81
        
        for step in range(n_steps):
            C_new = self.C.copy()
            
            # 底层异重流前进（简化）
            for i in range(1, self.nx-1):
                # 底层几个节点
                for j in range(self.nz-5, self.nz):
                    if self.C[j, i] > 0.1:
                        # 密度流速度
                        delta_rho = self.calculate_density(self.C[j, i]) - self.rho_ambient
                        g_prime = g * delta_rho / self.rho_ambient
                        
                        if g_prime > 0:
                            u_density = np.sqrt(g_prime * self.dz)  # 简化速度
                            
                            # 对流
                            if u_density * dt / self.dx < 1:  # CFL条件
                                C_new[j, i+1] += 0.5 * self.C[j, i] * u_density * dt / self.dx
                                C_new[j, i] *= 0.8  # 部分留下
            
            # 源注入
            C_new[self.nz-2, x_source] += C_source * 0.1
            
            # 扩散（简化）
            for i in range(1, self.nx-1):
                for j in range(1, self.nz-1):
                    if C_new[j, i] > 0:
                        Kz = 0.01  # 垂向扩散
                        d2C = (C_new[j+1, i] - 2*C_new[j, i] + C_new[j-1, i]) / self.dz**2
                        C_new[j, i] += Kz * d2C * dt
            
            self.C = np.maximum(C_new, 0)  # 非负
        
        print(f"\n异重流模拟完成:")
        print(f"  时间步: {n_steps}")
        print(f"  最大浓度: {np.max(self.C):.2f} kg/m³")
        print(f"  底层平均浓度: {np.mean(self.C[-5:, :]):.2f} kg/m³")
        
        return self.C
    
    def assess_intake_risk(self, x_intake, z_intake, C_threshold):
        """
        评估取水口风险
        
        参数：
        - x_intake: 取水口x位置 (m)
        - z_intake: 取水口z位置 (m)  
        - C_threshold: 浓度阈值 (kg/m³)
        
        返回：
        - C_intake: 取水口浓度
        - risk: 是否超标
        """
        ix = int(x_intake / self.dx)
        iz = int(z_intake / self.dz)
        
        C_intake = self.C[iz, ix]
        risk = C_intake > C_threshold
        
        print(f"\n取水口风险评估:")
        print(f"  位置: x={x_intake}m, z={z_intake}m")
        print(f"  浓度: {C_intake:.3f} kg/m³")
        print(f"  阈值: {C_threshold:.3f} kg/m³")
        print(f"  {'⚠️  超标' if risk else '✓ 安全'}")
        
        return C_intake, risk


def calculate_densimetric_froude(u, h, delta_rho, rho_ambient):
    """
    计算密度Froude数
    
    Fr = u / √(g'*h)
    g' = g*Δρ/ρ₀
    
    参数：
    - u: 流速 (m/s)
    - h: 水深 (m)
    - delta_rho: 密度差 (kg/m³)
    - rho_ambient: 环境密度 (kg/m³)
    
    返回：
    - Fr: Froude数
    """
    g = 9.81
    g_prime = g * delta_rho / rho_ambient
    Fr = u / np.sqrt(g_prime * h) if g_prime > 0 else 999
    
    print(f"\n密度Froude数:")
    print(f"  流速: {u:.2f} m/s")
    print(f"  水深: {h:.2f} m")
    print(f"  约化重力: {g_prime:.4f} m/s²")
    print(f"  Fr: {Fr:.2f}")
    
    return Fr


def estimate_underflow_velocity(delta_rho, rho_ambient, h):
    """
    估算异重流前进速度
    
    u ≈ √(g'*h)
    
    参数：
    - delta_rho: 密度差
    - rho_ambient: 环境密度
    - h: 异重流厚度
    
    返回：
    - u: 速度 (m/s)
    """
    g = 9.81
    g_prime = g * delta_rho / rho_ambient
    u = np.sqrt(g_prime * h)
    
    print(f"\n异重流速度估算:")
    print(f"  密度差: {delta_rho:.2f} kg/m³")
    print(f"  约化重力: {g_prime:.4f} m/s²")
    print(f"  厚度: {h:.1f} m")
    print(f"  速度: {u:.3f} m/s ({u*3600:.1f} m/h)")
    
    return u
