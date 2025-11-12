"""
《水力学考研1000题详解》配套代码
题目902：泵站供水系统综合设计（跨章节综合题）

问题描述：
某城市供水泵站系统，设计参数如下：
  水源水库: 最低水位H₁ = 5 m
  用户高程: 最高点H₂ = 85 m
  设计流量: Q_design = 0.15 m³/s
  输水管道: 总长L = 2000 m，直径d = 0.3 m，λ = 0.02
  局部损失: 进口ζ₁=0.5，弯头ζ₂=0.3×4，阀门ζ₃=5.0，出口ζ₄=1.0
  泵站选型: 需确定水泵型号和台数
  管网压力: 用户点要求p_min = 0.2 MPa

要求：
(1) 计算管路所需扬程H_pipe
(2) 选择合适的水泵（给出3个型号供选择）
(3) 计算水泵工况点（流量、扬程、效率、功率）
(4) 分析单泵与双泵并联运行
(5) 优化调节方案（节流vs变速）
(6) 计算全年运行成本

涉及知识点：
1. 管流计算（Bernoulli + 沿程局部损失）
2. 水泵特性曲线（H-Q, η-Q, P-Q）
3. 工况点分析（H_pump = H_pipe）
4. 并联运行（增流分析）
5. 调节方式比较（节流、变速、切削）
6. 经济分析（运行成本）

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PumpStationSystem:
    """泵站供水系统综合设计类"""
    
    def __init__(self):
        """初始化"""
        self.g = 9.8          # 重力加速度 (m/s²)
        
        # 水位高程
        self.H1 = 5           # 水源最低水位 (m)
        self.H2 = 85          # 用户最高点 (m)
        
        # 设计流量
        self.Q_design = 0.15  # m³/s
        
        # 输水管道
        self.L = 2000         # 管道长度 (m)
        self.d = 0.3          # 管道直径 (m)
        self.lambda_pipe = 0.02  # 沿程阻力系数
        
        # 局部损失系数
        self.zeta_inlet = 0.5       # 进口
        self.zeta_bend = 0.3 * 4    # 弯头（4个）
        self.zeta_valve = 5.0       # 阀门
        self.zeta_outlet = 1.0      # 出口
        
        # 用户压力要求
        self.p_min = 0.2e6    # Pa = 0.2 MPa
        
        # 电价
        self.electricity_price = 0.6  # 元/kWh
        
        # 计算
        self.calculate_pipe_head()
        self.select_pumps()
        self.analyze_operation()
        self.analyze_parallel_operation()
        self.compare_regulation_methods()
        self.calculate_annual_cost()
    
    def calculate_pipe_head(self):
        """计算管路所需扬程"""
        print(f"\n{'='*80}")
        print("【管路扬程计算】")
        print(f"{'='*80}")
        
        # 1. 静扬程
        self.H_static = self.H2 - self.H1 + self.p_min / (self.g * 1000)
        
        print(f"\n1. 静扬程:")
        print(f"   H_st = ΔZ + p_min/(ρg)")
        print(f"   ΔZ = H₂ - H₁ = {self.H2} - {self.H1} = {self.H2 - self.H1} m")
        print(f"   p_min/(ρg) = {self.p_min}/(1000×{self.g})")
        print(f"   p_min/(ρg) = {self.p_min/(self.g*1000):.4f} m")
        print(f"   H_st = {self.H_static:.4f} m")
        
        # 2. 流速
        A = np.pi * (self.d / 2)**2
        self.v = self.Q_design / A
        
        print(f"\n2. 管道流速:")
        print(f"   A = πd²/4 = π×{self.d}²/4 = {A:.6f} m²")
        print(f"   v = Q/A = {self.Q_design}/{A:.6f}")
        print(f"   v = {self.v:.4f} m/s")
        
        # 3. 沿程损失
        self.h_f = self.lambda_pipe * self.L / self.d * self.v**2 / (2 * self.g)
        
        print(f"\n3. 沿程损失:")
        print(f"   h_f = λ(L/d)(v²/2g)")
        print(f"   h_f = {self.lambda_pipe}×({self.L}/{self.d})×({self.v:.4f}²/(2×{self.g}))")
        print(f"   h_f = {self.h_f:.4f} m")
        
        # 4. 局部损失
        zeta_total = (self.zeta_inlet + self.zeta_bend + 
                     self.zeta_valve + self.zeta_outlet)
        self.h_j = zeta_total * self.v**2 / (2 * self.g)
        
        print(f"\n4. 局部损失:")
        print(f"   Σζ = ζ_进口 + ζ_弯头 + ζ_阀门 + ζ_出口")
        print(f"   Σζ = {self.zeta_inlet} + {self.zeta_bend} + {self.zeta_valve} + {self.zeta_outlet}")
        print(f"   Σζ = {zeta_total}")
        print(f"   h_j = Σζ(v²/2g) = {zeta_total}×{self.v**2/(2*self.g):.6f}")
        print(f"   h_j = {self.h_j:.4f} m")
        
        # 5. 总扬程
        self.H_pipe = self.H_static + self.h_f + self.h_j
        
        print(f"\n5. 管路总扬程:")
        print(f"   H_pipe = H_st + h_f + h_j")
        print(f"   H_pipe = {self.H_static:.4f} + {self.h_f:.4f} + {self.h_j:.4f}")
        print(f"   H_pipe = {self.H_pipe:.4f} m")
        
        # 6. 管路特性曲线系数
        self.S = (self.h_f + self.h_j) / self.Q_design**2
        
        print(f"\n6. 管路特性系数:")
        print(f"   H_pipe = H_st + SQ²")
        print(f"   S = (h_f + h_j)/Q² = {self.h_f + self.h_j:.4f}/{self.Q_design}²")
        print(f"   S = {self.S:.2f}")
    
    def select_pumps(self):
        """选择水泵型号"""
        print(f"\n{'='*80}")
        print("【水泵选型】")
        print(f"{'='*80}")
        
        print(f"\n设计工况点:")
        print(f"  流量: Q = {self.Q_design} m³/s = {self.Q_design*3600:.0f} m³/h")
        print(f"  扬程: H = {self.H_pipe:.2f} m")
        
        # 3个候选泵型号（虚拟数据，实际应查泵样本）
        # 调整扬程以满足132.81m的管路需求
        self.pumps = {
            'A型': {
                'name': 'A型泵',
                'Q0': 0.15,      # 额定流量 m³/s
                'H0': 150,       # 额定扬程 m (提高)
                'eta0': 0.75,    # 额定效率
                'n0': 1450,      # 额定转速 rpm
                'P0': 35,        # 额定功率 kW
                # 特性曲线系数 H = H0 - a·Q²
                'a': 500,        # H = 150 - 500Q²
                # 效率曲线系数 η = b·Q - c·Q²
                'b': 6.0,
                'c': 16.0
            },
            'B型': {
                'name': 'B型泵',
                'Q0': 0.18,
                'H0': 145,
                'eta0': 0.78,
                'n0': 1450,
                'P0': 38,
                'a': 400,        # H = 145 - 400Q²
                'b': 5.5,
                'c': 12.0
            },
            'C型': {
                'name': 'C型泵',
                'Q0': 0.12,
                'H0': 155,
                'eta0': 0.72,
                'n0': 1450,
                'P0': 32,
                'a': 600,       # H = 155 - 600Q²
                'b': 6.5,
                'c': 20.0
            }
        }
        
        print(f"\n候选泵型号:")
        for pump_type, params in self.pumps.items():
            print(f"\n  {params['name']}:")
            print(f"    额定流量: {params['Q0']} m³/s = {params['Q0']*3600:.0f} m³/h")
            print(f"    额定扬程: {params['H0']} m")
            print(f"    额定效率: {params['eta0']*100:.1f}%")
            print(f"    额定功率: {params['P0']} kW")
            print(f"    转速: {params['n0']} rpm")
        
        # 选择最优泵
        print(f"\n选型分析:")
        best_pump = None
        best_score = -1
        
        for pump_type, params in self.pumps.items():
            # 计算工况点
            H_pump_at_Q = params['H0'] - params['a'] * self.Q_design**2
            eta_at_Q = params['b'] * self.Q_design - params['c'] * self.Q_design**2
            eta_at_Q = np.clip(eta_at_Q, 0, 1)
            
            # 评分：扬程匹配度 + 效率
            H_match = 1 - abs(H_pump_at_Q - self.H_pipe) / self.H_pipe
            score = H_match * 0.6 + eta_at_Q * 0.4
            
            print(f"  {params['name']}:")
            print(f"    Q={self.Q_design}时扬程: {H_pump_at_Q:.2f} m (需要{self.H_pipe:.2f}m)")
            print(f"    Q={self.Q_design}时效率: {eta_at_Q*100:.1f}%")
            print(f"    综合评分: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_pump = pump_type
        
        self.selected_pump = best_pump
        self.pump_params = self.pumps[best_pump]
        
        print(f"\n✓ 选择: {self.pump_params['name']} (评分{best_score:.3f})")
    
    def pump_head(self, Q):
        """水泵扬程特性"""
        return self.pump_params['H0'] - self.pump_params['a'] * Q**2
    
    def pump_efficiency(self, Q):
        """水泵效率特性"""
        eta = self.pump_params['b'] * Q - self.pump_params['c'] * Q**2
        return np.clip(eta, 0, 1)
    
    def pump_power(self, Q, H):
        """水泵功率"""
        eta = self.pump_efficiency(Q)
        if eta < 0.01:
            eta = 0.01
        return 1000 * self.g * Q * H / (1000 * eta)  # kW
    
    def pipe_head_curve(self, Q):
        """管路特性曲线"""
        return self.H_static + self.S * Q**2
    
    def analyze_operation(self):
        """分析单泵运行工况"""
        print(f"\n{'='*80}")
        print("【单泵运行工况分析】")
        print(f"{'='*80}")
        
        # 求解工况点: H_pump = H_pipe
        def equation(Q):
            return self.pump_head(Q) - self.pipe_head_curve(Q)
        
        self.Q_operating = brentq(equation, 0.01, 0.3)
        self.H_operating = self.pump_head(self.Q_operating)
        self.eta_operating = self.pump_efficiency(self.Q_operating)
        self.P_operating = self.pump_power(self.Q_operating, self.H_operating)
        
        print(f"\n工况点参数:")
        print(f"  流量: Q = {self.Q_operating:.6f} m³/s = {self.Q_operating*3600:.2f} m³/h")
        print(f"  扬程: H = {self.H_operating:.4f} m")
        print(f"  效率: η = {self.eta_operating*100:.2f}%")
        print(f"  功率: P = {self.P_operating:.2f} kW")
        
        # 与设计流量比较
        Q_ratio = self.Q_operating / self.Q_design
        print(f"\n与设计流量比较:")
        print(f"  Q_实际/Q_设计 = {self.Q_operating:.6f}/{self.Q_design}")
        print(f"  比值 = {Q_ratio:.4f}")
        
        if abs(Q_ratio - 1) < 0.05:
            print(f"  ✓ 接近设计流量，选型合理")
        elif Q_ratio > 1.1:
            print(f"  ⚠ 流量偏大，可能需要节流")
        else:
            print(f"  ⚠ 流量偏小，可能需要调整")
    
    def analyze_parallel_operation(self):
        """分析双泵并联运行"""
        print(f"\n{'='*80}")
        print("【双泵并联运行分析】")
        print(f"{'='*80}")
        
        # 并联泵特性: H相同，Q叠加
        def parallel_head(Q_total):
            Q_single = Q_total / 2
            return self.pump_head(Q_single)
        
        # 求解并联工况点
        def equation_parallel(Q_total):
            return parallel_head(Q_total) - self.pipe_head_curve(Q_total)
        
        self.Q_parallel = brentq(equation_parallel, 0.01, 0.5)
        self.H_parallel = parallel_head(self.Q_parallel)
        
        Q_single_parallel = self.Q_parallel / 2
        self.eta_parallel = self.pump_efficiency(Q_single_parallel)
        self.P_parallel = 2 * self.pump_power(Q_single_parallel, self.H_parallel)
        
        print(f"\n并联工况点:")
        print(f"  总流量: Q = {self.Q_parallel:.6f} m³/s = {self.Q_parallel*3600:.2f} m³/h")
        print(f"  扬程: H = {self.H_parallel:.4f} m")
        print(f"  单泵流量: Q_单 = {Q_single_parallel:.6f} m³/s")
        print(f"  单泵效率: η = {self.eta_parallel*100:.2f}%")
        print(f"  总功率: P_总 = {self.P_parallel:.2f} kW (2×{self.P_parallel/2:.2f})")
        
        # 增流效果
        self.K_Q = self.Q_parallel / self.Q_operating
        
        print(f"\n增流效果:")
        print(f"  增流系数: K_Q = Q_并联/Q_单泵")
        print(f"  K_Q = {self.Q_parallel:.6f}/{self.Q_operating:.6f}")
        print(f"  K_Q = {self.K_Q:.4f}")
        print(f"  流量增加: {(self.K_Q - 1)*100:.1f}%")
        
        if self.K_Q >= 1.7:
            print(f"  ✓ 增流效果好")
        elif self.K_Q >= 1.5:
            print(f"  ✓ 增流效果较好")
        else:
            print(f"  ⚠ 增流效果一般（受管路特性影响）")
    
    def compare_regulation_methods(self):
        """比较调节方式"""
        print(f"\n{'='*80}")
        print("【调节方式比较】")
        print(f"{'='*80}")
        
        # 目标：从当前工况点调节到设计流量
        Q_target = self.Q_design
        
        print(f"\n调节目标: Q = {Q_target} m³/s")
        print(f"当前流量: Q = {self.Q_operating:.6f} m³/s")
        
        if abs(self.Q_operating - Q_target) / Q_target < 0.05:
            print(f"✓ 当前流量已接近设计值，无需调节")
            return
        
        # 1. 节流调节
        H_target = self.pipe_head_curve(Q_target)
        H_pump_at_target = self.pump_head(Q_target)
        H_valve = H_pump_at_target - H_target
        
        print(f"\n1. 节流调节:")
        print(f"   阀门损失: H_阀 = H_泵(Q_目标) - H_管(Q_目标)")
        print(f"   H_阀 = {H_pump_at_target:.4f} - {H_target:.4f}")
        print(f"   H_阀 = {H_valve:.4f} m")
        
        eta_throttle = self.pump_efficiency(Q_target)
        P_throttle = self.pump_power(Q_target, H_pump_at_target)
        
        print(f"   功率: P = {P_throttle:.2f} kW")
        print(f"   效率: η = {eta_throttle*100:.2f}%")
        print(f"   能量损失: {H_valve} m水头被阀门消耗")
        
        # 2. 变速调节
        # 相似律: n'/n = Q'/Q, H'/H = (n'/n)²
        n_ratio = Q_target / self.Q_operating
        n_new = self.pump_params['n0'] * n_ratio
        H_speed = self.H_operating * n_ratio**2
        
        print(f"\n2. 变速调节:")
        print(f"   转速比: n'/n = Q'/Q = {Q_target}/{self.Q_operating:.6f}")
        print(f"   n'/n = {n_ratio:.4f}")
        print(f"   新转速: n' = {self.pump_params['n0']}×{n_ratio:.4f} = {n_new:.0f} rpm")
        print(f"   扬程: H' = H×(n'/n)² = {self.H_operating:.4f}×{n_ratio**2:.4f}")
        print(f"   H' = {H_speed:.4f} m")
        
        P_speed = self.P_operating * n_ratio**3
        print(f"   功率: P' = P×(n'/n)³ = {self.P_operating:.2f}×{n_ratio**3:.4f}")
        print(f"   P' = {P_speed:.2f} kW")
        print(f"   效率基本不变: η ≈ {self.eta_operating*100:.2f}%")
        
        # 3. 对比
        print(f"\n3. 调节方式对比:")
        print(f"   节流调节: P = {P_throttle:.2f} kW, η = {eta_throttle*100:.1f}%")
        print(f"   变速调节: P = {P_speed:.2f} kW, η = {self.eta_operating*100:.1f}%")
        print(f"   节能: ΔP = {P_throttle - P_speed:.2f} kW ({(P_throttle-P_speed)/P_throttle*100:.1f}%)")
        
        if P_speed < P_throttle:
            print(f"   ✓ 变速调节更节能")
        
        self.P_throttle = P_throttle
        self.P_speed = P_speed
    
    def calculate_annual_cost(self):
        """计算全年运行成本"""
        print(f"\n{'='*80}")
        print("【全年运行成本分析】")
        print(f"{'='*80}")
        
        # 假设全年运行时间
        hours_per_year = 6000  # 小时
        
        print(f"\n假设条件:")
        print(f"  全年运行时间: {hours_per_year} h")
        print(f"  电价: {self.electricity_price} 元/kWh")
        
        # 单泵运行成本
        cost_single = self.P_operating * hours_per_year * self.electricity_price
        
        print(f"\n1. 单泵运行:")
        print(f"   功率: P = {self.P_operating:.2f} kW")
        print(f"   年耗电: W = {self.P_operating:.2f}×{hours_per_year} = {self.P_operating*hours_per_year:.0f} kWh")
        print(f"   年成本: {cost_single:.2f} 元")
        
        # 并联运行成本
        cost_parallel = self.P_parallel * hours_per_year * self.electricity_price
        
        print(f"\n2. 双泵并联:")
        print(f"   功率: P = {self.P_parallel:.2f} kW")
        print(f"   年耗电: W = {self.P_parallel:.2f}×{hours_per_year} = {self.P_parallel*hours_per_year:.0f} kWh")
        print(f"   年成本: {cost_parallel:.2f} 元")
        
        # 单位流量成本
        unit_cost_single = cost_single / (self.Q_operating * hours_per_year * 3600)
        unit_cost_parallel = cost_parallel / (self.Q_parallel * hours_per_year * 3600)
        
        print(f"\n3. 单位流量成本:")
        print(f"   单泵: {unit_cost_single:.6f} 元/m³")
        print(f"   并联: {unit_cost_parallel:.6f} 元/m³")
        
        if unit_cost_single < unit_cost_parallel:
            print(f"   ✓ 单泵运行更经济")
        else:
            print(f"   ✓ 并联运行更经济")
        
        self.annual_cost_single = cost_single
        self.annual_cost_parallel = cost_parallel
    
    def optimization_recommendations(self):
        """优化建议"""
        print(f"\n{'='*80}")
        print("【优化建议】")
        print(f"{'='*80}")
        
        suggestions = []
        
        # 1. 流量匹配
        Q_ratio = self.Q_operating / self.Q_design
        if abs(Q_ratio - 1) > 0.1:
            suggestions.append(f"• 实际流量偏差{abs(Q_ratio-1)*100:.1f}%，建议调节")
        
        # 2. 效率
        if self.eta_operating < 0.7:
            suggestions.append(f"• 运行效率{self.eta_operating*100:.1f}%偏低，建议优化")
        
        # 3. 并联
        if self.K_Q < 1.5:
            suggestions.append("• 并联增流效果不佳，考虑改变管路或泵型")
        
        # 4. 调节
        if hasattr(self, 'P_throttle') and hasattr(self, 'P_speed'):
            if self.P_throttle > self.P_speed * 1.1:
                savings = (self.P_throttle - self.P_speed) * 6000 * self.electricity_price
                suggestions.append(f"• 采用变速调节可年节约{savings:.0f}元")
        
        # 5. 维护
        suggestions.append("• 定期检查水泵性能，保持高效运行")
        suggestions.append("• 监测管道糙率变化，及时清洗")
        
        print(f"\n优化建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        return suggestions
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*80)
        print("题目902：泵站供水系统综合设计（跨章节综合题）")
        print("="*80)
        
        print("\n【系统参数】")
        print(f"  水位高差: ΔZ = {self.H2 - self.H1} m")
        print(f"  设计流量: Q = {self.Q_design} m³/s = {self.Q_design*3600:.0f} m³/h")
        print(f"  管道: L={self.L}m, d={self.d}m, λ={self.lambda_pipe}")
        print(f"  压力要求: p_min = {self.p_min/1e6} MPa")
        
        print("\n【涉及知识点】")
        print("1. 管路计算（沿程+局部损失）")
        print("2. 水泵选型（性能参数匹配）")
        print("3. 工况点分析（H_pump = H_pipe）")
        print("4. 并联运行（增流系数）")
        print("5. 调节方式（节流vs变速）")
        print("6. 经济分析（年运行成本）")
        
        print("\n【计算过程】")
        # 计算过程已在各方法中输出
        
        # 优化建议
        self.optimization_recommendations()
        
        print("\n【最终答案】")
        print("="*80)
        print(f"(1) 管路所需扬程: H_pipe = {self.H_pipe:.2f} m")
        print(f"(2) 选择泵型: {self.pump_params['name']} (H₀={self.pump_params['H0']}m, Q₀={self.pump_params['Q0']*3600:.0f}m³/h)")
        print(f"(3) 单泵工况点: Q={self.Q_operating:.4f}m³/s, H={self.H_operating:.2f}m, η={self.eta_operating*100:.1f}%, P={self.P_operating:.2f}kW")
        print(f"(4) 并联运行: Q_总={self.Q_parallel:.4f}m³/s, 增流系数K_Q={self.K_Q:.2f}")
        print(f"(5) 调节优化: 变速调节比节流节能{(self.P_throttle-self.P_speed)/self.P_throttle*100:.1f}%" if hasattr(self, 'P_throttle') else "(5) 调节：当前无需调节")
        print(f"(6) 年运行成本: 单泵{self.annual_cost_single:.0f}元, 并联{self.annual_cost_parallel:.0f}元")
        print("="*80)
    
    def visualize(self):
        """可视化"""
        fig = plt.figure(figsize=(16, 12))
        
        # 子图1：特性曲线与工况点
        ax1 = plt.subplot(2, 3, 1)
        self._plot_characteristics(ax1)
        
        # 子图2：并联特性对比
        ax2 = plt.subplot(2, 3, 2)
        self._plot_parallel_comparison(ax2)
        
        # 子图3：调节方式对比
        ax3 = plt.subplot(2, 3, 3)
        self._plot_regulation_comparison(ax3)
        
        # 子图4：效率与功率
        ax4 = plt.subplot(2, 3, 4)
        self._plot_efficiency_power(ax4)
        
        # 子图5：年运行成本
        ax5 = plt.subplot(2, 3, 5)
        self._plot_annual_cost(ax5)
        
        # 子图6：系统示意图
        ax6 = plt.subplot(2, 3, 6)
        self._plot_system_schematic(ax6)
        
        plt.tight_layout()
        return fig
    
    def _plot_characteristics(self, ax):
        """绘制特性曲线"""
        Q = np.linspace(0, 0.25, 200)
        
        # 泵特性
        H_pump = np.array([self.pump_head(q) for q in Q])
        ax.plot(Q, H_pump, 'b-', linewidth=2.5, label=f'{self.pump_params["name"]}特性')
        
        # 管路特性
        H_pipe = np.array([self.pipe_head_curve(q) for q in Q])
        ax.plot(Q, H_pipe, 'r-', linewidth=2.5, label='管路特性')
        
        # 工况点
        ax.plot(self.Q_operating, self.H_operating, 'go', markersize=12,
               label=f'工况点 Q={self.Q_operating:.3f}', zorder=5)
        ax.text(self.Q_operating + 0.01, self.H_operating + 3,
               f'Q={self.Q_operating*3600:.1f}m³/h\nH={self.H_operating:.1f}m\nη={self.eta_operating*100:.1f}%',
               fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # 设计点
        ax.plot(self.Q_design, self.H_pipe, 'r^', markersize=10,
               label=f'设计点', zorder=5)
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('泵与管路特性曲线', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.25)
    
    def _plot_parallel_comparison(self, ax):
        """绘制并联对比"""
        Q = np.linspace(0, 0.4, 200)
        
        # 单泵
        H_single = np.array([self.pump_head(q) for q in Q])
        ax.plot(Q, H_single, 'b-', linewidth=2, label='单泵')
        
        # 并联
        def parallel_head(q):
            return self.pump_head(q/2)
        H_parallel = np.array([parallel_head(q) for q in Q])
        ax.plot(Q, H_parallel, 'r--', linewidth=2, label='双泵并联')
        
        # 管路
        H_pipe = np.array([self.pipe_head_curve(q) for q in Q])
        ax.plot(Q, H_pipe, 'g-', linewidth=2, label='管路')
        
        # 工况点
        ax.plot(self.Q_operating, self.H_operating, 'bo', markersize=10)
        ax.plot(self.Q_parallel, self.H_parallel, 'ro', markersize=10)
        
        # 增流区域
        ax.fill_betweenx([80, 120], self.Q_operating, self.Q_parallel,
                        alpha=0.3, color='yellow')
        ax.text((self.Q_operating + self.Q_parallel)/2, 100,
               f'增流\nK_Q={self.K_Q:.2f}',
               ha='center', fontsize=10, weight='bold')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('扬程 H (m)', fontsize=12)
        ax.set_title('单泵vs并联特性', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_regulation_comparison(self, ax):
        """绘制调节方式对比"""
        if not hasattr(self, 'P_throttle'):
            ax.text(0.5, 0.5, '无需调节', ha='center', va='center',
                   fontsize=14, transform=ax.transAxes)
            ax.axis('off')
            return
        
        methods = ['节流调节', '变速调节']
        powers = [self.P_throttle, self.P_speed]
        colors = ['lightcoral', 'lightgreen']
        
        bars = ax.bar(methods, powers, color=colors, edgecolor='black', linewidth=2)
        
        for bar, power in zip(bars, powers):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                   f'{power:.2f} kW', ha='center', fontsize=11, weight='bold')
        
        # 节能标注
        savings = self.P_throttle - self.P_speed
        ax.annotate('', xy=(1, self.P_speed), xytext=(1, self.P_throttle),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(1.1, (self.P_throttle + self.P_speed)/2,
               f'节能\n{savings:.1f}kW\n({savings/self.P_throttle*100:.1f}%)',
               fontsize=9, weight='bold', color='red')
        
        ax.set_ylabel('功率 (kW)', fontsize=12)
        ax.set_title('调节方式功率对比', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_efficiency_power(self, ax):
        """绘制效率与功率曲线"""
        Q = np.linspace(0.05, 0.25, 100)
        
        # 效率
        eta = np.array([self.pump_efficiency(q) for q in Q])
        ax.plot(Q, eta*100, 'b-', linewidth=2.5, label='效率 η')
        
        # 功率（归一化）
        P = np.array([self.pump_power(q, self.pump_head(q)) for q in Q])
        P_norm = P / np.max(P) * 100
        ax.plot(Q, P_norm, 'r--', linewidth=2.5, label='功率 P (归一化)')
        
        # 工况点
        ax.axvline(self.Q_operating, color='green', linestyle=':', linewidth=2,
                  label=f'工况点 Q={self.Q_operating:.3f}')
        
        ax.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax.set_ylabel('效率 (%) / 归一化功率', fontsize=12)
        ax.set_title('效率与功率特性', fontsize=13, weight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_annual_cost(self, ax):
        """绘制年运行成本"""
        categories = ['单泵运行', '双泵并联']
        costs = [self.annual_cost_single/10000, self.annual_cost_parallel/10000]
        
        bars = ax.bar(categories, costs, color=['skyblue', 'lightcoral'],
                     edgecolor='black', linewidth=2)
        
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                   f'{cost:.2f}万元', ha='center', fontsize=11, weight='bold')
        
        ax.set_ylabel('年运行成本 (万元)', fontsize=12)
        ax.set_title('年运行成本对比', fontsize=13, weight='bold')
        ax.grid(True, axis='y', alpha=0.3)
    
    def _plot_system_schematic(self, ax):
        """绘制系统示意图"""
        ax.axis('off')
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # 水库
        reservoir = Rectangle((0.5, 0.5), 1.5, 1, facecolor='lightblue',
                             edgecolor='black', linewidth=2)
        ax.add_patch(reservoir)
        ax.text(1.25, 0, '水源\nH₁=5m', ha='center', fontsize=9)
        
        # 泵
        pump = Circle((3.5, 1), 0.4, facecolor='yellow', edgecolor='black', linewidth=2)
        ax.add_patch(pump)
        ax.text(3.5, 1, 'P', ha='center', va='center', fontsize=14, weight='bold')
        ax.text(3.5, 0.2, f'{self.pump_params["name"]}', ha='center', fontsize=8)
        
        # 管道
        ax.plot([2, 3.1], [1, 1], 'k-', linewidth=4)
        ax.plot([3.9, 8], [1, 7], 'k-', linewidth=4)
        ax.text(5.5, 4, f'L={self.L}m\nd={self.d}m', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        # 用户
        user = Rectangle((7.5, 7), 1, 0.8, facecolor='lightgreen',
                        edgecolor='black', linewidth=2)
        ax.add_patch(user)
        ax.text(8, 7.4, '用户\nH₂=85m', ha='center', fontsize=9)
        
        # 参数标注
        ax.text(5, 9, f'Q={self.Q_operating*3600:.0f}m³/h\nH={self.H_operating:.0f}m\nP={self.P_operating:.0f}kW',
               fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))


def test_problem_902():
    """测试题目902"""
    print("\n" + "="*80)
    print("开始泵站供水系统综合设计...")
    print("="*80)
    
    # 创建系统对象
    system = PumpStationSystem()
    
    # 打印结果
    system.print_results()
    
    # 可视化
    print("\n生成可视化图表...")
    fig = system.visualize()
    plt.savefig('/workspace/books/graduate-exam-prep/hydraulics-1000/codes/problem_902_result.png',
                dpi=150, bbox_inches='tight')
    print("图片已保存: problem_902_result.png")
    
    # 验证
    assert system.H_pipe > 0, "管路扬程应大于0"
    assert system.Q_operating > 0, "工况流量应大于0"
    assert 0 < system.eta_operating < 1, "效率应在0-1之间"
    assert system.K_Q > 1, "并联增流系数应大于1"
    
    print("\n✓ 所有测试通过！")
    print("\n【核心要点】")
    print("泵站供水系统综合设计整合多个知识点！")
    print("• 管路计算: H = H_st + h_f + h_j")
    print("• 水泵选型: 性能参数匹配")
    print("• 工况点: H_pump(Q) = H_pipe(Q)")
    print("• 并联运行: 增流系数K_Q")
    print("• 调节优化: 变速>节流")
    print("• 经济分析: 全寿命成本")


if __name__ == "__main__":
    test_problem_902()
