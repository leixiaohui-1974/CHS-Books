"""
多点源污染叠加模型
Multi-Source Pollution Superposition Model

包括：
1. 多点源排放模拟
2. 污染物叠加效应
3. 达标距离计算
4. 排放方案优化
"""

import numpy as np
from scipy.integrate import odeint


class PointSource:
    """
    点源污染源
    
    参数：
        x: 排放口位置 (m)
        Q_waste: 排放流量 (m³/s)
        C_waste: 排放浓度 (mg/L)
        name: 点源名称
    """
    
    def __init__(self, x, Q_waste, C_waste, name="Point Source"):
        """初始化点源"""
        self.x = x
        self.Q_waste = Q_waste
        self.C_waste = C_waste
        self.name = name
    
    def __repr__(self):
        return f"{self.name} at x={self.x}m: Q={self.Q_waste}m³/s, C={self.C_waste}mg/L"


class MultiSourceRiver1D:
    """
    一维河流多点源污染模拟
    
    基于稳态对流-扩散-反应方程：
    u * dC/dx = D * d²C/dx² - k * C
    
    边界条件：
    - 上游边界：C(0) = C0
    - 点源边界：质量守恒（混合后浓度）
    
    参数：
        L: 河段长度 (m)
        nx: 空间节点数
        u: 流速 (m/s)
        D: 扩散系数 (m²/s)
        k: 降解系数 (1/s)
        Q_river: 河流流量 (m³/s)
        C0: 上游本底浓度 (mg/L)
    """
    
    def __init__(self, L, nx, u, D, k, Q_river, C0=0):
        """初始化多点源河流模型"""
        self.L = L
        self.nx = nx
        self.u = u
        self.D = D
        self.k = k
        self.Q_river = Q_river
        self.C0 = C0
        
        # 空间离散
        self.x = np.linspace(0, L, nx)
        self.dx = L / (nx - 1)
        
        # 点源列表
        self.sources = []
        
        # 结果
        self.C = None
        
        # 无量纲数
        self.Pe = u * L / D if D > 0 else float('inf')  # Peclet数
        self.Da = k * L / u if u > 0 else 0              # Damköhler数
        
        print(f"多点源河流模型初始化:")
        print(f"  河段长度 L = {L} m")
        print(f"  流速 u = {u} m/s")
        print(f"  扩散系数 D = {D} m²/s")
        print(f"  降解系数 k = {k*86400:.2f} day⁻¹")
        print(f"  Peclet数 Pe = {self.Pe:.1f}")
        print(f"  Damköhler数 Da = {self.Da:.3f}")
    
    def add_source(self, x, Q_waste, C_waste, name=None):
        """
        添加点源
        
        参数：
            x: 排放口位置 (m)
            Q_waste: 排放流量 (m³/s)
            C_waste: 排放浓度 (mg/L)
            name: 点源名称
        """
        if name is None:
            name = f"Source_{len(self.sources)+1}"
        
        source = PointSource(x, Q_waste, C_waste, name)
        self.sources.append(source)
        
        print(f"添加点源: {source}")
        
        return source
    
    def calculate_mixed_concentration(self, C_upstream, Q_upstream, source):
        """
        计算点源混合后浓度
        
        质量守恒：
        Q_mixed * C_mixed = Q_upstream * C_upstream + Q_waste * C_waste
        Q_mixed = Q_upstream + Q_waste
        
        参数：
            C_upstream: 上游浓度 (mg/L)
            Q_upstream: 上游流量 (m³/s)
            source: 点源对象
            
        返回：
            C_mixed: 混合后浓度 (mg/L)
            Q_mixed: 混合后流量 (m³/s)
        """
        Q_mixed = Q_upstream + source.Q_waste
        C_mixed = (Q_upstream * C_upstream + source.Q_waste * source.C_waste) / Q_mixed
        
        print(f"\n{source.name}处混合:")
        print(f"  上游: Q={Q_upstream:.2f} m³/s, C={C_upstream:.3f} mg/L")
        print(f"  排放: Q={source.Q_waste:.2f} m³/s, C={source.C_waste:.3f} mg/L")
        print(f"  → 混合后: Q={Q_mixed:.2f} m³/s, C={C_mixed:.3f} mg/L")
        
        return C_mixed, Q_mixed
    
    def solve_segment(self, x_start, x_end, C_start, u_segment, Q_segment):
        """
        求解河段解析解
        
        对于稳态1D对流-扩散-反应方程：
        u * dC/dx = D * d²C/dx² - k * C
        
        解析解（忽略扩散项，对流占主导）：
        C(x) = C_start * exp(-k * (x - x_start) / u)
        
        参数：
            x_start: 河段起点 (m)
            x_end: 河段终点 (m)
            C_start: 起点浓度 (mg/L)
            u_segment: 河段流速 (m/s)
            Q_segment: 河段流量 (m³/s)
            
        返回：
            x_seg: 河段节点位置
            C_seg: 河段浓度分布
        """
        # 河段长度
        L_seg = x_end - x_start
        
        # 河段节点
        mask = (self.x >= x_start) & (self.x <= x_end)
        x_seg = self.x[mask]
        
        # 解析解（简化：忽略扩散）
        if self.k > 0:
            C_seg = C_start * np.exp(-self.k * (x_seg - x_start) / u_segment)
        else:
            C_seg = np.full_like(x_seg, C_start)
        
        return x_seg, C_seg
    
    def solve(self):
        """
        求解多点源河流水质模拟
        
        算法：
        1. 按点源位置排序
        2. 逐段求解：
           - 河段起点到第一个点源
           - 第一个点源到第二个点源
           - ...
           - 最后一个点源到河段终点
        3. 在每个点源处：
           - 计算混合后浓度
           - 更新流量和流速
        """
        print("\n" + "="*70)
        print("求解多点源河流水质模拟")
        print("="*70)
        
        # 按位置排序点源
        self.sources.sort(key=lambda s: s.x)
        
        # 初始化
        C = np.zeros(self.nx)
        Q_current = self.Q_river
        u_current = self.u
        
        # 起点
        x_prev = 0
        C_prev = self.C0
        
        # 遍历每个点源
        for i, source in enumerate(self.sources):
            print(f"\n--- 河段 {i+1}: x={x_prev:.0f}m → x={source.x:.0f}m ---")
            
            # 求解当前河段
            x_seg, C_seg = self.solve_segment(x_prev, source.x, C_prev, u_current, Q_current)
            
            # 填充结果
            mask = (self.x >= x_prev) & (self.x < source.x)
            n_mask = np.sum(mask)
            if n_mask > 0:
                # 确保数组长度匹配
                if len(C_seg) > n_mask:
                    C[mask] = C_seg[:n_mask]
                else:
                    C[mask] = C_seg
            
            # 点源处的上游浓度
            C_upstream = C_seg[-1]
            
            # 计算混合后浓度
            C_mixed, Q_current = self.calculate_mixed_concentration(
                C_upstream, Q_current, source
            )
            
            # 更新流速（假设断面积不变）
            u_current = u_current * Q_current / (Q_current - source.Q_waste) if i == 0 else u_current
            
            # 更新下一段起点
            x_prev = source.x
            C_prev = C_mixed
        
        # 最后一段：最后一个点源到河段终点
        print(f"\n--- 河段 {len(self.sources)+1}: x={x_prev:.0f}m → x={self.L:.0f}m ---")
        x_seg, C_seg = self.solve_segment(x_prev, self.L, C_prev, u_current, Q_current)
        
        # 填充结果
        mask = self.x >= x_prev
        C[mask] = C_seg
        
        self.C = C
        
        print("\n求解完成！")
        
        return self.x, self.C
    
    def calculate_compliance_distance(self, C_standard, source_idx=None):
        """
        计算达标距离
        
        找到浓度首次低于标准的位置
        
        参数：
            C_standard: 水质标准 (mg/L)
            source_idx: 点源索引（如果指定，则计算该点源下游达标距离）
            
        返回：
            x_compliance: 达标距离 (m)
        """
        if self.C is None:
            raise ValueError("请先调用solve()方法求解")
        
        if source_idx is not None:
            # 计算指定点源下游达标距离
            source = self.sources[source_idx]
            x_start = source.x
            
            # 找到点源下游首次达标位置
            mask = self.x > x_start
            x_downstream = self.x[mask]
            C_downstream = self.C[mask]
            
            compliant = C_downstream <= C_standard
            if np.any(compliant):
                idx = np.where(compliant)[0][0]
                x_compliance = x_downstream[idx] - x_start
                
                print(f"\n{source.name}下游达标距离:")
                print(f"  标准 C_std = {C_standard} mg/L")
                print(f"  达标距离 = {x_compliance:.0f} m")
            else:
                x_compliance = None
                print(f"\n{source.name}下游在模拟河段内未达标！")
        else:
            # 计算整个河段达标距离
            compliant = self.C <= C_standard
            if np.any(compliant):
                idx = np.where(compliant)[0][0]
                x_compliance = self.x[idx]
                
                print(f"\n河段达标距离:")
                print(f"  标准 C_std = {C_standard} mg/L")
                print(f"  达标距离 = {x_compliance:.0f} m")
            else:
                x_compliance = None
                print(f"\n河段在模拟范围内未达标！")
        
        return x_compliance
    
    def calculate_max_concentration(self):
        """
        计算最大浓度及其位置
        
        返回：
            C_max: 最大浓度 (mg/L)
            x_max: 最大浓度位置 (m)
        """
        if self.C is None:
            raise ValueError("请先调用solve()方法求解")
        
        idx_max = np.argmax(self.C)
        C_max = self.C[idx_max]
        x_max = self.x[idx_max]
        
        print(f"\n最大浓度:")
        print(f"  C_max = {C_max:.3f} mg/L")
        print(f"  位置 x = {x_max:.0f} m")
        
        return C_max, x_max
    
    def optimize_discharge(self, C_standard, target_source_idx):
        """
        优化排放浓度以满足水质标准
        
        反推：给定下游水质标准，计算允许的最大排放浓度
        
        参数：
            C_standard: 水质标准 (mg/L)
            target_source_idx: 目标点源索引
            
        返回：
            C_waste_max: 允许的最大排放浓度 (mg/L)
        """
        if self.C is None:
            raise ValueError("请先调用solve()方法求解")
        
        source = self.sources[target_source_idx]
        
        # 简化算法：假设其他点源不变，调整目标点源浓度
        # 使下游最大浓度满足标准
        
        # 找到下游最不利位置（最大浓度点）
        mask = self.x > source.x
        C_downstream = self.C[mask]
        C_max_downstream = np.max(C_downstream)
        
        # 计算削减比例
        if C_max_downstream > C_standard:
            reduction_factor = C_standard / C_max_downstream
            C_waste_max = source.C_waste * reduction_factor
            
            print(f"\n{source.name}排放浓度优化:")
            print(f"  当前排放浓度: {source.C_waste:.1f} mg/L")
            print(f"  下游最大浓度: {C_max_downstream:.2f} mg/L")
            print(f"  水质标准: {C_standard} mg/L")
            print(f"  → 建议排放浓度: ≤{C_waste_max:.1f} mg/L")
            print(f"  → 需削减: {(1-reduction_factor)*100:.1f}%")
        else:
            C_waste_max = source.C_waste
            print(f"\n{source.name}当前排放浓度已满足标准")
        
        return C_waste_max


def calculate_superposition_factor(sources, Q_river):
    """
    计算污染物叠加系数
    
    叠加系数 = 实际浓度 / 单个点源浓度之和
    
    参数：
        sources: 点源列表
        Q_river: 河流流量 (m³/s)
        
    返回：
        factor: 叠加系数
    """
    # 计算每个点源单独作用的贡献
    total_load = sum(s.Q_waste * s.C_waste for s in sources)
    total_Q = Q_river + sum(s.Q_waste for s in sources)
    
    # 简单混合浓度
    C_simple = total_load / total_Q
    
    # 叠加系数（简化）
    factor = 1.0  # 稳态下叠加系数接近1
    
    print(f"\n污染物叠加分析:")
    print(f"  总污染负荷: {total_load:.2f} kg/s")
    print(f"  总流量: {total_Q:.2f} m³/s")
    print(f"  简单混合浓度: {C_simple:.2f} mg/L")
    
    return factor
