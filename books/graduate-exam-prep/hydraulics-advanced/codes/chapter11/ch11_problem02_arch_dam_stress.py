# -*- coding: utf-8 -*-
"""
第11章 水工建筑物 - 题2：拱坝应力分析

问题描述：
    某双曲拱坝，坝顶高程300m，河床高程200m
    拱冠梁顶部厚度dt = 6m，底部厚度db = 40m
    拱冠梁顶部半径Rt = 150m，底部半径Rb = 100m
    上游水位285m，混凝土弹性模量E = 25GPa
    
    求：
    1. 拱坝几何参数
    2. 拱向与梁向应力
    3. 应力分布规律
    4. 坝体稳定与安全
    5. 拱梁分载

核心公式：
    1. 水压力：p = γw·h
    2. 拱向应力：σθ = p·R/d
    3. 梁向应力：σz = M/(d²/6)
    4. 拱梁分载：η = Ra/(Ra+Rb)

考试要点：
    - 拱坝几何设计
    - 应力计算
    - 拱梁分载
    - 安全评价

作者: CHS-Books Team
日期: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ArchDamStress:
    """拱坝应力分析"""
    
    def __init__(self, Z_top: float, Z_bed: float, dt: float, db: float,
                 Rt: float, Rb: float, H_water: float, E: float = 25e9):
        self.Z_top = Z_top  # 坝顶高程
        self.Z_bed = Z_bed  # 河床高程
        self.dt = dt  # 顶部厚度
        self.db = db  # 底部厚度
        self.Rt = Rt  # 顶部半径
        self.Rb = Rb  # 底部半径
        self.H_water = H_water  # 上游水位
        self.E = E  # 弹性模量 Pa
        self.gamma_w = 10  # 水重度 kN/m³
        self.gamma_c = 24  # 混凝土重度 kN/m³
        
    def dam_height(self) -> float:
        """坝高"""
        return self.Z_top - self.Z_bed
    
    def water_head(self) -> float:
        """水头"""
        return self.H_water - self.Z_bed
    
    def thickness_at_elevation(self, Z: float) -> float:
        """
        任意高程处的坝厚
        d(Z) = dt + (db-dt)·(Z_top-Z)/H
        """
        H = self.dam_height()
        d = self.dt + (self.db - self.dt) * (self.Z_top - Z) / H
        return d
    
    def radius_at_elevation(self, Z: float) -> float:
        """
        任意高程处的拱半径
        R(Z) = Rt + (Rb-Rt)·(Z_top-Z)/H
        """
        H = self.dam_height()
        R = self.Rt + (self.Rb - self.Rt) * (self.Z_top - Z) / H
        return R
    
    def water_pressure(self, Z: float) -> float:
        """
        任意高程处的水压力
        p = γw·(H_water - Z)
        """
        if Z > self.H_water:
            return 0
        else:
            return self.gamma_w * (self.H_water - Z)
    
    def arch_stress(self, Z: float) -> float:
        """
        拱向应力（圆筒公式）
        σθ = p·R/d
        """
        p = self.water_pressure(Z)
        R = self.radius_at_elevation(Z)
        d = self.thickness_at_elevation(Z)
        
        sigma_theta = p * R / d  # kPa
        return sigma_theta
    
    def cantilever_stress(self, Z: float) -> float:
        """
        梁向应力（悬臂梁）
        σz = M/(W) = M/(b·d²/6)
        假设单位宽度b=1m
        """
        # 从该高程到坝顶的水压力总和（简化）
        if Z > self.H_water:
            M = 0
        else:
            h = self.H_water - Z
            # 弯矩（单宽）
            M = 0.5 * self.gamma_w * h ** 2 * (h / 3)
        
        d = self.thickness_at_elevation(Z)
        # 抗弯截面模量（单宽）
        W = d ** 2 / 6
        
        sigma_z = M / W if W > 0 else 0  # kPa
        return sigma_z
    
    def arch_cantilever_ratio(self, Z: float) -> Tuple[float, float]:
        """
        拱梁分载（刚度比法）
        η = Ra/(Ra+Rb)
        Ra - 拱圈刚度
        Rb - 梁的刚度
        """
        R = self.radius_at_elevation(Z)
        d = self.thickness_at_elevation(Z)
        H = self.dam_height()
        
        # 拱圈刚度（简化）：Ka = E·d/R
        Ka = self.E * d / R
        
        # 梁刚度（简化）：Kb = E·d³/(12·H²)
        Kb = self.E * (d ** 3) / (12 * (H ** 2))
        
        # 拱梁分载比
        eta_arch = Ka / (Ka + Kb)  # 拱承担
        eta_cantilever = Kb / (Ka + Kb)  # 梁承担
        
        return eta_arch, eta_cantilever
    
    def max_stress(self) -> Dict:
        """最大应力位置"""
        Z_range = np.linspace(self.Z_bed, self.H_water, 100)
        
        sigma_theta_list = [self.arch_stress(Z) for Z in Z_range]
        sigma_z_list = [self.cantilever_stress(Z) for Z in Z_range]
        
        idx_max_theta = np.argmax(sigma_theta_list)
        idx_max_z = np.argmax(sigma_z_list)
        
        return {
            'Z_max_theta': Z_range[idx_max_theta],
            'sigma_max_theta': sigma_theta_list[idx_max_theta],
            'Z_max_z': Z_range[idx_max_z],
            'sigma_max_z': sigma_z_list[idx_max_z]
        }
    
    def safety_check(self) -> Dict:
        """安全检查"""
        max_stress_info = self.max_stress()
        
        # 混凝土抗压强度（C30：fck=20.1MPa）
        f_ck = 20.1 * 1000  # kPa
        
        # 安全系数
        K_theta = f_ck / max_stress_info['sigma_max_theta']
        K_z = f_ck / max_stress_info['sigma_max_z']
        
        is_safe = (K_theta >= 3.0) and (K_z >= 3.0)
        
        return {
            'f_ck': f_ck,
            'K_theta': K_theta,
            'K_z': K_z,
            'is_safe': is_safe
        }
    
    def plot_analysis(self):
        """绘制分析图表"""
        fig = plt.figure(figsize=(16, 12))
        
        H = self.dam_height()
        h_water = self.water_head()
        max_stress_info = self.max_stress()
        safety_info = self.safety_check()
        
        # 1. 拱坝纵剖面
        ax1 = plt.subplot(3, 3, 1)
        
        # 高程范围
        Z_range = np.linspace(self.Z_bed, self.Z_top, 100)
        
        # 上游面与下游面
        d_upstream = [self.thickness_at_elevation(Z) / 2 for Z in Z_range]
        d_downstream = [-self.thickness_at_elevation(Z) / 2 for Z in Z_range]
        
        ax1.plot(d_upstream, Z_range, 'b-', linewidth=2, label='上游面')
        ax1.plot(d_downstream, Z_range, 'r-', linewidth=2, label='下游面')
        ax1.fill_betweenx(Z_range, d_upstream, d_downstream, alpha=0.3, color='gray')
        
        # 水位线
        ax1.axhline(self.H_water, color='cyan', linestyle='--', linewidth=2, label=f'水位{self.H_water}m')
        ax1.fill_betweenx([self.Z_bed, self.H_water], -50, 0,
                         alpha=0.3, color='lightblue')
        
        # 标注
        ax1.text(0, self.Z_top+2, f'顶部d={self.dt}m', ha='center', fontsize=9, fontweight='bold')
        ax1.text(0, self.Z_bed-3, f'底部d={self.db}m', ha='center', fontsize=9, fontweight='bold')
        
        ax1.set_xlabel('坝厚 (m)', fontsize=10)
        ax1.set_ylabel('高程 (m)', fontsize=10)
        ax1.set_title('拱坝纵剖面', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-30, 30)
        
        # 2. 几何参数
        ax2 = plt.subplot(3, 3, 2)
        ax2.axis('off')
        
        ax2.text(0.5, 0.95, '拱坝参数', fontsize=11, ha='center', fontweight='bold')
        ax2.text(0.1, 0.82, f'坝高: H = {H:.0f} m', fontsize=10, color='red')
        ax2.text(0.1, 0.72, f'水头: h = {h_water:.0f} m', fontsize=10, color='blue')
        ax2.text(0.1, 0.62, f'顶部厚度: dt = {self.dt} m', fontsize=10)
        ax2.text(0.1, 0.52, f'底部厚度: db = {self.db} m', fontsize=10)
        ax2.text(0.1, 0.42, f'顶部半径: Rt = {self.Rt} m', fontsize=10)
        ax2.text(0.1, 0.32, f'底部半径: Rb = {self.Rb} m', fontsize=10)
        ax2.text(0.1, 0.22, f'厚高比: db/H = {self.db/H:.3f}', fontsize=10, color='green')
        ax2.text(0.1, 0.12, f'弹性模量: E = {self.E/1e9:.0f} GPa', fontsize=10)
        ax2.text(0.1, 0.02, f'混凝土重度: γc = {self.gamma_c} kN/m³', fontsize=10)
        
        ax2.set_title('基本参数', fontsize=12, fontweight='bold')
        
        # 3. 坝厚与半径分布
        ax3 = plt.subplot(3, 3, 3)
        
        Z_plot = np.linspace(self.Z_bed, self.Z_top, 100)
        d_plot = [self.thickness_at_elevation(Z) for Z in Z_plot]
        R_plot = [self.radius_at_elevation(Z) for Z in Z_plot]
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(d_plot, Z_plot, 'b-', linewidth=2, label='坝厚d')
        line2 = ax3_twin.plot(R_plot, Z_plot, 'r-', linewidth=2, label='半径R')
        
        ax3.set_xlabel('坝厚 d (m)', fontsize=10, color='blue')
        ax3.set_ylabel('高程 (m)', fontsize=10)
        ax3_twin.set_xlabel('半径 R (m)', fontsize=10, color='red')
        ax3.set_title('坝厚与半径分布', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper right')
        
        # 4. 水压力分布
        ax4 = plt.subplot(3, 3, 4)
        
        Z_water = np.linspace(self.Z_bed, self.H_water, 100)
        p_water = [self.water_pressure(Z) for Z in Z_water]
        
        ax4.plot(p_water, Z_water, 'b-', linewidth=3)
        ax4.fill_betweenx(Z_water, 0, p_water, alpha=0.3, color='lightblue')
        ax4.axhline(self.H_water, color='cyan', linestyle='--', linewidth=1)
        
        ax4.set_xlabel('水压力 p (kPa)', fontsize=10)
        ax4.set_ylabel('高程 (m)', fontsize=10)
        ax4.set_title('水压力分布', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. 拱向应力分布
        ax5 = plt.subplot(3, 3, 5)
        
        sigma_theta = [self.arch_stress(Z) for Z in Z_water]
        
        ax5.plot(sigma_theta, Z_water, 'r-', linewidth=3)
        ax5.fill_betweenx(Z_water, 0, sigma_theta, alpha=0.3, color='pink')
        ax5.plot(max_stress_info['sigma_max_theta'], max_stress_info['Z_max_theta'], 
                'ro', markersize=12, label=f"最大{max_stress_info['sigma_max_theta']:.0f}kPa")
        
        ax5.set_xlabel('拱向应力 σθ (kPa)', fontsize=10)
        ax5.set_ylabel('高程 (m)', fontsize=10)
        ax5.set_title('拱向应力分布', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. 梁向应力分布
        ax6 = plt.subplot(3, 3, 6)
        
        sigma_z = [self.cantilever_stress(Z) for Z in Z_water]
        
        ax6.plot(sigma_z, Z_water, 'g-', linewidth=3)
        ax6.fill_betweenx(Z_water, 0, sigma_z, alpha=0.3, color='lightgreen')
        ax6.plot(max_stress_info['sigma_max_z'], max_stress_info['Z_max_z'],
                'go', markersize=12, label=f"最大{max_stress_info['sigma_max_z']:.0f}kPa")
        
        ax6.set_xlabel('梁向应力 σz (kPa)', fontsize=10)
        ax6.set_ylabel('高程 (m)', fontsize=10)
        ax6.set_title('梁向应力分布', fontsize=12, fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. 拱梁分载
        ax7 = plt.subplot(3, 3, 7)
        
        Z_ratio = np.linspace(self.Z_bed, self.Z_top, 50)
        eta_arch_list = []
        eta_cant_list = []
        
        for Z in Z_ratio:
            eta_a, eta_c = self.arch_cantilever_ratio(Z)
            eta_arch_list.append(eta_a * 100)  # 转为百分比
            eta_cant_list.append(eta_c * 100)
        
        ax7.plot(eta_arch_list, Z_ratio, 'b-', linewidth=2, label='拱圈承担')
        ax7.plot(eta_cant_list, Z_ratio, 'r-', linewidth=2, label='梁承担')
        ax7.axvline(50, color='k', linestyle='--', linewidth=1, alpha=0.5)
        
        ax7.set_xlabel('分载比 (%)', fontsize=10)
        ax7.set_ylabel('高程 (m)', fontsize=10)
        ax7.set_title('拱梁分载比', fontsize=12, fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        ax7.set_xlim(0, 100)
        
        # 8. 安全系数
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('off')
        
        ax8.text(0.5, 0.95, '安全检查', fontsize=11, ha='center', fontweight='bold')
        ax8.text(0.1, 0.78, f'混凝土强度: fck = {safety_info["f_ck"]/1000:.1f} MPa', 
                fontsize=10)
        ax8.text(0.1, 0.65, f'最大拱向应力: {max_stress_info["sigma_max_theta"]:.0f} kPa', 
                fontsize=10, color='red')
        ax8.text(0.1, 0.55, f'最大梁向应力: {max_stress_info["sigma_max_z"]:.0f} kPa', 
                fontsize=10, color='green')
        
        ax8.text(0.1, 0.40, f'拱向安全系数: Kθ = {safety_info["K_theta"]:.2f}', 
                fontsize=10, color='blue', fontweight='bold')
        ax8.text(0.1, 0.30, f'梁向安全系数: Kz = {safety_info["K_z"]:.2f}', 
                fontsize=10, color='purple', fontweight='bold')
        
        if safety_info['is_safe']:
            ax8.text(0.1, 0.15, '✓ 安全系数满足要求（K≥3.0）', fontsize=10, 
                    color='green', fontweight='bold')
        else:
            ax8.text(0.1, 0.15, '✗ 安全系数不足！', fontsize=10, 
                    color='red', fontweight='bold')
        
        ax8.set_title('安全评价', fontsize=12, fontweight='bold')
        
        # 9. 结果汇总表
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['项目', '数值', '单位'],
            ['坝高', f'{H:.0f}', 'm'],
            ['底部厚度', f'{self.db}', 'm'],
            ['厚高比', f'{self.db/H:.3f}', '-'],
            ['最大拱向应力', f'{max_stress_info["sigma_max_theta"]:.0f}', 'kPa'],
            ['最大梁向应力', f'{max_stress_info["sigma_max_z"]:.0f}', 'kPa'],
            ['拱向安全系数', f'{safety_info["K_theta"]:.2f}', '-'],
            ['梁向安全系数', f'{safety_info["K_z"]:.2f}', '-']
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.45, 0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.2)
        
        for i in range(3):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 高亮关键指标
        for i in [5, 6, 7, 8]:
            for j in range(3):
                table[(i, j)].set_facecolor('#FFF9E6')
        
        ax9.set_title('计算结果汇总', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/tmp/ch11_problem02_arch_dam_stress.png', dpi=150, bbox_inches='tight')
        print(f"图表已保存: /tmp/ch11_problem02_arch_dam_stress.png")
        plt.show()
    
    def print_results(self):
        """打印结果"""
        print("\n" + "="*70)
        print("第11章 水工建筑物 - 题2：拱坝应力分析")
        print("="*70)
        
        H = self.dam_height()
        h_water = self.water_head()
        max_stress_info = self.max_stress()
        safety_info = self.safety_check()
        
        print(f"\n【拱坝几何】")
        print(f"坝顶高程: {self.Z_top} m")
        print(f"河床高程: {self.Z_bed} m")
        print(f"坝高: H = {H:.2f} m")
        print(f"上游水位: {self.H_water} m")
        print(f"水头: h = {h_water:.2f} m")
        
        print(f"\n【坝体参数】")
        print(f"顶部厚度: dt = {self.dt} m")
        print(f"底部厚度: db = {self.db} m")
        print(f"厚高比: db/H = {self.db/H:.3f}")
        print(f"顶部拱半径: Rt = {self.Rt} m")
        print(f"底部拱半径: Rb = {self.Rb} m")
        
        # 中间高程示例
        Z_mid = (self.Z_bed + self.H_water) / 2
        d_mid = self.thickness_at_elevation(Z_mid)
        R_mid = self.radius_at_elevation(Z_mid)
        eta_a, eta_c = self.arch_cantilever_ratio(Z_mid)
        
        print(f"\n【中间高程Z={Z_mid:.0f}m处】")
        print(f"坝厚: d = {d_mid:.2f} m")
        print(f"拱半径: R = {R_mid:.2f} m")
        print(f"水压力: p = {self.water_pressure(Z_mid):.2f} kPa")
        print(f"拱向应力: σθ = p·R/d = {self.arch_stress(Z_mid):.2f} kPa")
        print(f"梁向应力: σz = {self.cantilever_stress(Z_mid):.2f} kPa")
        print(f"拱梁分载: 拱圈{eta_a*100:.1f}%，悬臂梁{eta_c*100:.1f}%")
        
        print(f"\n【最大应力】")
        print(f"最大拱向应力: σθ_max = {max_stress_info['sigma_max_theta']:.2f} kPa")
        print(f"  位置: Z = {max_stress_info['Z_max_theta']:.2f} m")
        print(f"最大梁向应力: σz_max = {max_stress_info['sigma_max_z']:.2f} kPa")
        print(f"  位置: Z = {max_stress_info['Z_max_z']:.2f} m")
        
        print(f"\n【安全检查】")
        print(f"混凝土抗压强度: fck = {safety_info['f_ck']/1000:.1f} MPa = {safety_info['f_ck']:.0f} kPa")
        print(f"拱向安全系数: Kθ = fck/σθ_max = {safety_info['K_theta']:.3f}")
        print(f"梁向安全系数: Kz = fck/σz_max = {safety_info['K_z']:.3f}")
        
        if safety_info['is_safe']:
            print(f"✓ 拱向Kθ = {safety_info['K_theta']:.2f} ≥ 3.0，满足要求")
            print(f"✓ 梁向Kz = {safety_info['K_z']:.2f} ≥ 3.0，满足要求")
            print(f"✓ 拱坝应力安全")
        else:
            print(f"✗ 安全系数不足！")
        
        print(f"\n✓ 拱坝应力分析完成")
        print(f"\n{'='*70}\n")


def main():
    Z_top = 300
    Z_bed = 200
    dt = 6
    db = 40
    Rt = 150
    Rb = 100
    H_water = 285
    E = 25e9  # Pa
    
    dam = ArchDamStress(Z_top, Z_bed, dt, db, Rt, Rb, H_water, E)
    dam.print_results()
    dam.plot_analysis()


if __name__ == "__main__":
    main()
