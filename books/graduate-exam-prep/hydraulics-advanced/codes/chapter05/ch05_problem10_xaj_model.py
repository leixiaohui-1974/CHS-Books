# -*- coding: utf-8 -*-
"""
第05章 水文学基础 - 题10：流域产汇流模型（新安江模型）

问题描述：
    新安江模型，流域面积F = 500 km²，蓄水容量曲线指数b = 0.3，
    流域平均蓄水容量WM = 120 mm，上层蓄水容量WUM = 30 mm。
    降雨P = 80 mm，初始土壤含水量W₀ = 60 mm。
    
    求：
    1. 蓄水容量分布曲线
    2. 径流深R（蓄满产流）
    3. 地面径流与地下径流划分
    4. 模型物理意义
    5. 参数b的影响
    6. 模型局限性

核心公式：
    1. 蓄水容量曲线: f = 1 - (1 - Wm/WM)^(b+1)
    2. 产流面积比: f = 1 - [1 - (PE/WMM)]^(1/(b+1))
    3. 径流深: R = P - WM + W₀ + WM·(1-f₀) - WM·(1-f)
    4. 简化产流: R = P - (WM - W₀)  (当P+W₀ > WM时全流域产流)

考试要点：
    - 新安江模型是我国广泛应用的流域水文模型
    - 蓄满产流：只有当土壤蓄满后才产流
    - 参数b控制蓄水容量的不均匀性
    - WM是全流域平均蓄水容量
    - 适用于湿润地区

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from typing import Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class XinAnjiangModel:
    """新安江模型（蓄满产流）"""
    
    def __init__(self, F: float, WM: float, WUM: float, WLM: float, 
                 b: float, W0: float, P: float):
        """
        初始化新安江模型
        
        参数:
            F: 流域面积 [km²]
            WM: 流域平均蓄水容量 [mm]
            WUM: 上层蓄水容量 [mm]
            WLM: 下层蓄水容量 [mm]
            b: 蓄水容量曲线指数 [无量纲]
            W0: 初始土壤含水量 [mm]
            P: 降雨量 [mm]
        """
        self.F = F
        self.WM = WM
        self.WUM = WUM
        self.WLM = WLM
        self.b = b
        self.W0 = W0
        self.P = P
        
        # 计算WMM（流域最大点蓄水容量，与WM的关系）
        self.WMM = WM / (1 - 1/(b+1))  # WMM = WM·(b+1)/b 的简化
        
    def storage_capacity_curve(self, f: np.ndarray) -> np.ndarray:
        """
        蓄水容量分布曲线
        
        参数:
            f: 蓄水容量小于某值的面积比 [0-1]
        
        返回:
            Wm: 对应的蓄水容量 [mm]
        
        公式:
            Wm = WM · [1 - (1-f)^(1/(b+1))]
        """
        Wm = self.WM * (1 - (1 - f) ** (1 / (self.b + 1)))
        return Wm
    
    def storage_curve_inverse(self, Wm: float) -> float:
        """
        蓄水容量曲线的反函数（给定Wm求f）
        
        参数:
            Wm: 蓄水容量 [mm]
        
        返回:
            f: 面积比
        
        公式:
            f = 1 - (1 - Wm/WM)^(b+1)
        """
        if Wm >= self.WM:
            return 1.0
        f = 1 - (1 - Wm / self.WM) ** (self.b + 1)
        return f
    
    def runoff_generation(self) -> Tuple[float, float, float, float]:
        """
        计算径流深（蓄满产流机制）
        
        返回:
            R: 总径流深 [mm]
            f0: 初始产流面积比
            f1: 降雨后产流面积比
            A: 产流面积 [km²]
        
        公式:
            当 P + W₀ ≤ WM: 部分面积产流
            当 P + W₀ > WM: 全流域产流，R = P - (WM - W₀)
        """
        # 初始产流面积比
        f0 = self.storage_curve_inverse(self.W0)
        
        # 判断是否全流域产流
        if self.P + self.W0 > self.WM:
            # 全流域产流
            R = self.P - (self.WM - self.W0)
            f1 = 1.0
            A = self.F
        else:
            # 部分面积产流
            # PE = P + W₀ - WM·(1-f₀)
            PE = self.P + self.W0 - self.WM * (1 - f0)
            
            if PE > 0:
                # 有效降雨，计算产流
                # 通过迭代求f1
                WMM = self.WM / (1 - 1/(self.b + 1))
                
                if PE < WMM * (1 - f0):
                    # 部分产流
                    f1 = 1 - (1 - PE / WMM) ** (1 / (self.b + 1))
                    R = self.P - self.WM * ((1 - f1) - (1 - f0))
                else:
                    # 全流域产流
                    R = self.P - (self.WM - self.W0)
                    f1 = 1.0
            else:
                # 无产流
                R = 0
                f1 = 0
            
            A = f1 * self.F
        
        return R, f0, f1, A
    
    def runoff_separation(self, R: float, ratio_surface: float = 0.7) -> Tuple[float, float]:
        """
        径流成分划分（地面径流与地下径流）
        
        参数:
            R: 总径流深 [mm]
            ratio_surface: 地面径流比例（简化假设）
        
        返回:
            RS: 地面径流深 [mm]
            RG: 地下径流深 [mm]
        """
        RS = R * ratio_surface
        RG = R * (1 - ratio_surface)
        return RS, RG
    
    def runoff_volume(self, R: float) -> float:
        """
        计算径流总量
        
        参数:
            R: 径流深 [mm]
        
        返回:
            W: 径流量 [m³]
        """
        W = R * self.F * 1000  # mm·km² → m³
        return W
    
    def parameter_b_analysis(self, b_range: tuple = (0.1, 0.5), 
                            n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        参数b的影响分析
        
        参数:
            b_range: b参数范围
            n_points: 计算点数
        
        返回:
            bs: b参数数组
            Rs: 对应的径流深数组
        """
        bs = np.linspace(b_range[0], b_range[1], n_points)
        Rs = []
        
        for b in bs:
            # 临时修改b参数
            b_old = self.b
            self.b = b
            R, _, _, _ = self.runoff_generation()
            Rs.append(R)
            self.b = b_old
        
        return bs, np.array(Rs)
    
    def initial_moisture_analysis(self, W0_range: tuple = (0, 120), 
                                 n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        初始土壤含水量的影响分析
        
        参数:
            W0_range: 初始含水量范围 [mm]
            n_points: 计算点数
        
        返回:
            W0s: 初始含水量数组
            Rs: 对应的径流深数组
        """
        W0s = np.linspace(W0_range[0], W0_range[1], n_points)
        Rs = []
        
        for W0 in W0s:
            W0_old = self.W0
            self.W0 = W0
            R, _, _, _ = self.runoff_generation()
            Rs.append(R)
            self.W0 = W0_old
        
        return W0s, np.array(Rs)
    
    def rainfall_analysis(self, P_range: tuple = (0, 150), 
                         n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        降雨量的影响分析
        
        参数:
            P_range: 降雨量范围 [mm]
            n_points: 计算点数
        
        返回:
            Ps: 降雨量数组
            Rs: 对应的径流深数组
        """
        Ps = np.linspace(P_range[0], P_range[1], n_points)
        Rs = []
        
        for P in Ps:
            P_old = self.P
            self.P = P
            R, _, _, _ = self.runoff_generation()
            Rs.append(R)
            self.P = P_old
        
        return Ps, np.array(Rs)
    
    def plot_analysis(self):
        """绘制完整分析图表（9个子图）"""
        fig = plt.figure(figsize=(16, 12))
        
        # 计算基本结果
        R, f0, f1, A = self.runoff_generation()
        RS, RG = self.runoff_separation(R)
        W = self.runoff_volume(R)
        
        # 1. 蓄水容量分布曲线
        ax1 = plt.subplot(3, 3, 1)
        f_range = np.linspace(0, 1, 100)
        Wm_range = self.storage_capacity_curve(f_range)
        
        ax1.plot(f_range, Wm_range, 'b-', linewidth=2, label='蓄水容量曲线')
        ax1.axhline(self.WM, color='r', linestyle='--', linewidth=2, 
                   label=f'平均: WM={self.WM} mm')
        ax1.axhline(self.W0, color='g', linestyle='--', linewidth=2,
                   label=f'初始: W₀={self.W0} mm')
        ax1.fill_between(f_range, 0, Wm_range, alpha=0.2, color='blue')
        
        ax1.set_xlabel('面积比 f', fontsize=11)
        ax1.set_ylabel('蓄水容量 Wm (mm)', fontsize=11)
        ax1.set_title(f'蓄水容量分布曲线 (b={self.b})', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. 参数b对曲线形状的影响
        ax2 = plt.subplot(3, 3, 2)
        b_values = [0.1, 0.3, 0.5, 0.7]
        colors = plt.cm.viridis(np.linspace(0, 1, len(b_values)))
        
        for b_val, color in zip(b_values, colors):
            Wm_b = self.WM * (1 - (1 - f_range) ** (1 / (b_val + 1)))
            ax2.plot(f_range, Wm_b, linewidth=2, color=color, label=f'b={b_val}')
        
        ax2.plot(f0, self.W0, 'ro', markersize=10, label=f'初始状态: f₀={f0:.2f}')
        ax2.set_xlabel('面积比 f', fontsize=11)
        ax2.set_ylabel('蓄水容量 Wm (mm)', fontsize=11)
        ax2.set_title('参数b对曲线形状的影响', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. 产流面积示意图
        ax3 = plt.subplot(3, 3, 3)
        
        # 绘制流域示意图
        circle = plt.Circle((0.5, 0.5), 0.4, color='lightblue', ec='black', linewidth=2)
        ax3.add_patch(circle)
        
        # 产流区域
        if f1 > 0:
            theta = np.linspace(0, 2*np.pi*f1, 100)
            x_prod = 0.5 + 0.4 * np.cos(theta)
            y_prod = 0.5 + 0.4 * np.sin(theta)
            ax3.fill(np.concatenate([[0.5], x_prod]), 
                    np.concatenate([[0.5], y_prod]), 
                    color='red', alpha=0.5, label='产流区')
        
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.set_aspect('equal')
        ax3.axis('off')
        ax3.set_title('产流面积示意图', fontsize=12, fontweight='bold')
        
        # 添加标注
        info_text = f'初始: f₀ = {f0:.2f}\n降雨后: f₁ = {f1:.2f}\n产流面积: {A:.1f} km²'
        ax3.text(0.5, 0.05, info_text, ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        ax3.legend(loc='upper right')
        
        # 4. 水量平衡计算
        ax4 = plt.subplot(3, 3, 4)
        
        # 水量平衡
        components = ['降雨P', '初始W₀', '蓄满WM', '径流R', '损失\n(WM-W₀-R)']
        values = [self.P, self.W0, self.WM, R, self.WM - self.W0 - R]
        colors_comp = ['skyblue', 'lightgreen', 'orange', 'red', 'gray']
        
        x_pos = np.arange(len(components))
        bars = ax4.bar(x_pos, values, color=colors_comp, alpha=0.7, edgecolor='black')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(components, fontsize=9)
        ax4.set_ylabel('水量 (mm)', fontsize=11)
        ax4.set_title('水量平衡分析', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标注
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2, height,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 5. 径流成分划分
        ax5 = plt.subplot(3, 3, 5)
        
        # 饼图
        sizes = [RS, RG]
        labels = [f'地面径流\nRS={RS:.1f} mm', f'地下径流\nRG={RG:.1f} mm']
        colors_pie = ['lightcoral', 'lightskyblue']
        explode = (0.05, 0)
        
        ax5.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax5.set_title(f'径流成分划分\n(总径流R={R:.1f} mm)', fontsize=12, fontweight='bold')
        
        # 6. 参数b的影响分析
        ax6 = plt.subplot(3, 3, 6)
        bs, Rs_b = self.parameter_b_analysis()
        
        ax6.plot(bs, Rs_b, 'b-', linewidth=2)
        ax6.plot(self.b, R, 'ro', markersize=10, label=f'当前: b={self.b}')
        ax6.set_xlabel('参数 b', fontsize=11)
        ax6.set_ylabel('径流深 R (mm)', fontsize=11)
        ax6.set_title('参数b对产流的影响', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        ax6.legend()
        
        # 添加说明
        ax6.text(0.5, 0.95, 'b↑: 流域不均匀性↑\n产流能力↓',
                transform=ax6.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                verticalalignment='top', horizontalalignment='center')
        
        # 7. 初始土壤含水量的影响
        ax7 = plt.subplot(3, 3, 7)
        W0s, Rs_W0 = self.initial_moisture_analysis()
        
        ax7.plot(W0s, Rs_W0, 'g-', linewidth=2)
        ax7.plot(self.W0, R, 'ro', markersize=10, label=f'当前: W₀={self.W0} mm')
        ax7.axvline(self.WM - self.P, color='orange', linestyle='--', linewidth=2,
                   label=f'临界: WM-P={self.WM-self.P:.1f} mm')
        ax7.set_xlabel('初始含水量 W₀ (mm)', fontsize=11)
        ax7.set_ylabel('径流深 R (mm)', fontsize=11)
        ax6.set_title('初始含水量对产流的影响', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3)
        ax7.legend()
        
        # 8. 降雨量的影响
        ax8 = plt.subplot(3, 3, 8)
        Ps, Rs_P = self.rainfall_analysis()
        
        ax8.plot(Ps, Rs_P, 'b-', linewidth=2)
        ax8.plot(self.P, R, 'ro', markersize=10, label=f'当前: P={self.P} mm')
        ax8.axvline(self.WM - self.W0, color='orange', linestyle='--', linewidth=2,
                   label=f'临界: WM-W₀={self.WM-self.W0:.1f} mm')
        ax8.plot(Ps, Ps, 'k--', alpha=0.3, label='P=R线')
        ax8.set_xlabel('降雨量 P (mm)', fontsize=11)
        ax8.set_ylabel('径流深 R (mm)', fontsize=11)
        ax8.set_title('降雨量对产流的影响', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3)
        ax8.legend()
        
        # 添加说明
        ax8.text(0.5, 0.3, 'P+W₀ > WM:\n全流域产流',
                transform=ax8.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                verticalalignment='top', horizontalalignment='center')
        
        # 9. 结果汇总
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        summary = [
            '═══ 新安江模型计算结果 ═══',
            '',
            '【模型参数】',
            f'流域面积: F = {self.F} km²',
            f'蓄水容量: WM = {self.WM} mm',
            f'上层蓄水: WUM = {self.WUM} mm',
            f'下层蓄水: WLM = {self.WLM} mm',
            f'曲线指数: b = {self.b}',
            '',
            '【输入条件】',
            f'降雨量: P = {self.P} mm',
            f'初始含水: W₀ = {self.W0} mm',
            '',
            '【产流结果】',
            f'初始产流面积比: f₀ = {f0:.3f}',
            f'降雨后产流面积比: f₁ = {f1:.3f}',
            f'产流面积: A = {A:.1f} km²',
            f'总径流深: R = {R:.2f} mm',
            f'  地面径流: RS = {RS:.2f} mm',
            f'  地下径流: RG = {RG:.2f} mm',
            f'径流总量: W = {W:.2e} m³',
            '',
            '【物理意义】',
            f'蓄满产流机制：土壤蓄满后才产流',
            f'产流面积随降雨增大而扩大',
            f'适用于湿润地区',
        ]
        
        y_pos = 0.98
        for line in summary:
            if '═══' in line:
                ax9.text(0.5, y_pos, line, fontsize=11, fontweight='bold',
                        horizontalalignment='center', verticalalignment='top',
                        color='darkblue')
            elif '【' in line:
                ax9.text(0.05, y_pos, line, fontsize=10, fontweight='bold',
                        verticalalignment='top', color='darkred')
            elif line == '':
                y_pos -= 0.01
                continue
            else:
                ax9.text(0.1, y_pos, line, fontsize=9, verticalalignment='top',
                        family='monospace')
            y_pos -= 0.037
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch05_problem10_xaj_model.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch05_problem10_xaj_model.png")
        plt.show()
    
    def print_results(self):
        """打印计算结果"""
        print("\n" + "="*70)
        print("第05章 水文学基础 - 题10：流域产汇流模型（新安江模型）")
        print("="*70)
        
        # 基本参数
        print(f"\n【模型参数】")
        print(f"流域面积: F = {self.F} km²")
        print(f"流域平均蓄水容量: WM = {self.WM} mm")
        print(f"上层蓄水容量: WUM = {self.WUM} mm")
        print(f"下层蓄水容量: WLM = {self.WLM} mm")
        print(f"蓄水容量曲线指数: b = {self.b}")
        
        print(f"\n【输入条件】")
        print(f"降雨量: P = {self.P} mm")
        print(f"初始土壤含水量: W₀ = {self.W0} mm")
        
        # (1) 蓄水容量分布
        print(f"\n【问题1】蓄水容量分布曲线")
        print(f"蓄水容量曲线方程:")
        print(f"Wm(f) = WM · [1 - (1-f)^(1/(b+1))]")
        print(f"Wm(f) = {self.WM} · [1 - (1-f)^(1/{self.b+1:.1f})]")
        print(f"\n特征点:")
        f_points = [0, 0.25, 0.5, 0.75, 1.0]
        for f in f_points:
            Wm = self.storage_capacity_curve(np.array([f]))[0]
            print(f"  f = {f:.2f}: Wm = {Wm:.1f} mm")
        
        # (2) 径流深计算
        print(f"\n【问题2】径流深计算（蓄满产流）")
        R, f0, f1, A = self.runoff_generation()
        
        print(f"\n初始状态:")
        print(f"初始含水量 W₀ = {self.W0} mm")
        print(f"初始产流面积比 f₀ = 1 - (1 - W₀/WM)^(b+1)")
        print(f"f₀ = 1 - (1 - {self.W0}/{self.WM})^{self.b+1:.1f} = {f0:.3f}")
        
        print(f"\n产流计算:")
        if self.P + self.W0 > self.WM:
            print(f"P + W₀ = {self.P} + {self.W0} = {self.P+self.W0} mm > WM = {self.WM} mm")
            print(f"满足全流域产流条件！")
            print(f"\n全流域产流公式:")
            print(f"R = P - (WM - W₀)")
            print(f"R = {self.P} - ({self.WM} - {self.W0})")
            print(f"R = {self.P} - {self.WM - self.W0} = {R:.2f} mm")
        else:
            print(f"P + W₀ = {self.P} + {self.W0} = {self.P+self.W0} mm < WM = {self.WM} mm")
            print(f"部分面积产流")
        
        print(f"\n✓ 总径流深: R = {R:.2f} mm")
        print(f"✓ 降雨后产流面积比: f₁ = {f1:.3f}")
        print(f"✓ 产流面积: A = {A:.1f} km² ({A/self.F*100:.1f}%)")
        
        # (3) 径流成分划分
        print(f"\n【问题3】地面径流与地下径流划分")
        RS, RG = self.runoff_separation(R)
        
        print(f"\n简化划分（假设地面径流占70%）:")
        print(f"地面径流: RS = {RS:.2f} mm ({RS/R*100:.0f}%)")
        print(f"地下径流: RG = {RG:.2f} mm ({RG/R*100:.0f}%)")
        
        W = self.runoff_volume(R)
        WS = self.runoff_volume(RS)
        WG = self.runoff_volume(RG)
        print(f"\n径流总量:")
        print(f"总量: W = R · F = {R} mm × {self.F} km² = {W:.2e} m³")
        print(f"地面: WS = {WS:.2e} m³")
        print(f"地下: WG = {WG:.2e} m³")
        
        # (4) 物理意义
        print(f"\n【问题4】模型物理意义")
        print(f"\n新安江模型核心思想:")
        print(f"1. 蓄满产流：只有当土壤蓄满水后，降雨才能产生径流")
        print(f"2. 蓄水容量不均匀分布：流域内各点蓄水容量不同")
        print(f"3. 参数b控制不均匀性：b越大，分布越不均匀")
        print(f"4. 产流面积随降雨增大而扩大")
        print(f"5. 适用于湿润地区（如长江流域、珠江流域）")
        
        print(f"\n本例物理过程:")
        print(f"  初始：流域已有{f0*100:.1f}%面积达到蓄满状态")
        print(f"  降雨：P = {self.P} mm")
        print(f"  结果：{'全流域' if f1 >= 0.99 else f'{f1*100:.1f}%面积'}产流")
        print(f"  径流：R = {R:.1f} mm")
        
        # (5) 参数b的影响
        print(f"\n【问题5】参数b的影响")
        print(f"\n参数b的作用:")
        print(f"- b越小：蓄水容量分布越均匀，产流能力越强")
        print(f"- b越大：蓄水容量分布越不均匀，产流能力越弱")
        print(f"- b=0：所有点蓄水容量相同（均匀分布）")
        
        bs_test = [0.1, 0.2, 0.3, 0.4, 0.5]
        print(f"\n不同b值下的径流深（其他条件不变）:")
        for b_test in bs_test:
            b_old = self.b
            self.b = b_test
            R_test, _, _, _ = self.runoff_generation()
            self.b = b_old
            print(f"  b = {b_test}: R = {R_test:.2f} mm")
        
        # (6) 模型局限性
        print(f"\n【问题6】模型局限性")
        print(f"\n新安江模型的局限性:")
        print(f"1. 仅适用于湿润地区，不适用于干旱/半干旱地区")
        print(f"2. 参数较多（本例简化，实际模型有10+个参数）")
        print(f"3. 参数物理意义较强，但难以直接测量")
        print(f"4. 需要率定，依赖实测资料")
        print(f"5. 对小流域或城市流域适用性较差")
        print(f"6. 蓄满产流机制假设可能不适用于所有流域")
        
        print(f"\n改进方向:")
        print(f"- 引入超渗产流机制（双源模型）")
        print(f"- 考虑植被截留、蒸散发")
        print(f"- 耦合分布式模型")
        print(f"- 引入遥感、GIS技术")
        
        # 考试要点
        print(f"\n【考试要点】")
        print(f"1. 新安江模型是蓄满产流机制（必须理解！）")
        print(f"2. 蓄水容量曲线: Wm = WM·[1-(1-f)^(1/(b+1))]")
        print(f"3. 全流域产流条件: P + W₀ > WM")
        print(f"4. 全流域产流公式: R = P - (WM - W₀)")
        print(f"5. 参数b越大，流域不均匀性越大，产流能力越弱")
        print(f"6. 适用于湿润地区（年降雨 > 800 mm）")
        
        print(f"\n{'='*70}\n")


def main():
    """主函数"""
    
    print("流域产汇流模型（新安江模型）")
    print("-" * 70)
    
    # 模型参数
    F = 500.0  # 流域面积 [km²]
    WM = 120.0  # 流域平均蓄水容量 [mm]
    WUM = 30.0  # 上层蓄水容量 [mm]
    WLM = 90.0  # 下层蓄水容量 [mm] (WM - WUM)
    b = 0.3  # 蓄水容量曲线指数
    
    # 输入条件
    W0 = 60.0  # 初始土壤含水量 [mm]
    P = 80.0  # 降雨量 [mm]
    
    # 创建模型实例
    xaj = XinAnjiangModel(F, WM, WUM, WLM, b, W0, P)
    
    # 打印结果
    xaj.print_results()
    
    # 绘制分析图
    xaj.plot_analysis()


if __name__ == "__main__":
    main()
