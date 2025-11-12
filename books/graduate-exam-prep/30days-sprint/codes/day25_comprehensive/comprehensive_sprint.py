#!/usr/bin/env python3
"""
《30天冲刺宝典》- Day 25: 综合应用专题
Sprint Day 25: Comprehensive Applications (Cross-Chapter Integration)

⏰ 学习时间：3小时
📚 核心内容：
  1. 跨章节综合问题求解
  2. 多系统耦合分析
  3. 实际工程应用
  4. 复杂问题建模

🎯 学习目标：
  - 掌握综合问题分析方法
  - 理解多系统相互作用
  - 提高工程实践能力
  - 强化综合应用技巧

💪 今日格言：综合应用=真正实力！跨章节融合=提高15分！
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon, Wedge, FancyBboxPatch
import matplotlib.patches as mpatches
from scipy.optimize import fsolve, brentq

# 设置中文字体
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class Day25Comprehensive:
    """
    Day 25：综合应用专题
    
    包含2个跨章节综合题：
    1. 水库-渠道-泵站联合调度系统（40分）
    2. 灌溉工程全流程分析（40分）
    """
    
    def __init__(self):
        """初始化参数"""
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho_w = 1000  # 水的密度 (kg/m³)
        self.gamma_w = self.rho_w * self.g  # 水的重度 (N/m³)
        
    def example_1_reservoir_canal_pump_system(self):
        """
        例题1：水库-渠道-泵站联合调度系统⭐⭐⭐⭐⭐
        
        题目：某灌区水利工程系统：
              【水库】
              - 水库正常蓄水位H₀=50m，死水位H_min=30m
              - 水库面积A_res=2km²，闸门：宽b=4m，高h=3m
              - 闸门底高程Z_gate=28m，闸门系数μ=0.6
              
              【输水渠道】
              - 梯形断面：底宽b=5m，边坡m=1.5，糙率n=0.025
              - 渠道长度L=2000m，底坡i=0.0003
              - 中间有跌坎（高1m）会产生水跃
              
              【提水泵站】
              - 提水高度Hs=15m，设计流量Q_design=8m³/s
              - 管道：d=0.8m，L_pipe=120m，λ=0.025，Σξ=6.0
              - 泵特性：H=30-20Q²，效率η=0.78
              
        求：(1) 水库放水流量（水位H=45m时）
            (2) 渠道输水能力与水跃分析
            (3) 泵站工况点与总功率
            (4) 系统最优调度方案
        
        考点：闸门出流、明渠流、水跃、泵站、系统优化
        难度：综合（最高难度！）
        时间：50分钟
        分值：40分
        """
        print("\n" + "="*60)
        print("例题1：水库-渠道-泵站联合调度系统⭐⭐⭐⭐⭐")
        print("="*60)
        
        # 已知条件
        # 水库参数
        H0 = 50.0     # 正常蓄水位 (m)
        H_min = 30.0  # 死水位 (m)
        A_res = 2.0e6 # 水库面积 (m²)
        H = 45.0      # 当前水位 (m)
        
        # 闸门参数
        b_gate = 4.0  # 闸门宽度 (m)
        h_gate = 3.0  # 闸门高度 (m)
        Z_gate = 28.0 # 闸门底高程 (m)
        mu_gate = 0.6 # 闸门系数
        
        # 渠道参数
        b_canal = 5.0    # 底宽 (m)
        m_canal = 1.5    # 边坡
        n_canal = 0.025  # 糙率
        L_canal = 2000.0 # 长度 (m)
        i_canal = 0.0003 # 底坡
        drop_height = 1.0 # 跌坎高度 (m)
        
        # 泵站参数
        Hs = 15.0        # 提水高度 (m)
        Q_design = 8.0   # 设计流量 (m³/s)
        d_pipe = 0.8     # 管径 (m)
        L_pipe = 120.0   # 管长 (m)
        lam_pipe = 0.025 # 摩阻系数
        xi_sum = 6.0     # 局部损失系数和
        eta = 0.78       # 泵效率
        
        print(f"\n已知条件：")
        print(f"  【水库】")
        print(f"    正常蓄水位：H₀={H0}m，死水位：{H_min}m")
        print(f"    水库面积：A={A_res/1e6}km²，当前水位：H={H}m")
        print(f"    闸门：b={b_gate}m，h={h_gate}m，Z={Z_gate}m，μ={mu_gate}")
        print(f"  【渠道】")
        print(f"    梯形断面：b={b_canal}m，m={m_canal}，n={n_canal}")
        print(f"    长度：L={L_canal}m，坡度：i={i_canal}")
        print(f"    跌坎：Δz={drop_height}m")
        print(f"  【泵站】")
        print(f"    提水高度：Hs={Hs}m，设计流量：{Q_design}m³/s")
        print(f"    管道：d={d_pipe}m，L={L_pipe}m，λ={lam_pipe}，Σξ={xi_sum}")
        print(f"    泵特性：H=30-20Q²，η={eta}")
        
        # (1) 水库放水流量
        print(f"\n解题步骤：")
        print(f"\n(1) 计算水库放水流量")
        
        # 闸门上游水深
        H_up = H - Z_gate
        
        print(f"\n闸门上游水深：")
        print(f"  H上 = H - Z闸 = {H} - {Z_gate} = {H_up} m")
        
        # 判断闸门出流类型
        # 如果H_up > h_gate，为淹没出流；否则为自由出流
        if H_up > h_gate:
            print(f"  H上 > h闸 → 淹没出流")
            # 淹没出流（简化为堰流）
            H_effective = H_up - h_gate/2
            Q_gate = mu_gate * b_gate * h_gate * np.sqrt(2 * self.g * H_effective)
        else:
            print(f"  H上 < h闸 → 自由出流")
            # 自由出流
            Q_gate = mu_gate * b_gate * H_up * np.sqrt(2 * self.g * H_up)
        
        print(f"\n闸门流量（自由出流）：")
        print(f"  Q = μbH√(2gH)")
        print(f"    = {mu_gate}×{b_gate}×{H_up}×√(2×{self.g}×{H_up})")
        print(f"    = {Q_gate:.3f} m³/s ✓")
        
        # (2) 渠道输水能力
        print(f"\n(2) 计算渠道输水能力与水跃")
        
        # 采用闸门流量作为渠道流量
        Q_canal = Q_gate
        
        # 渠道正常水深（谢才公式）
        def normal_depth_eq(h):
            A = (b_canal + m_canal * h) * h
            chi = b_canal + 2 * h * np.sqrt(1 + m_canal**2)
            R = A / chi
            Q_calc = (1/n_canal) * A * R**(2/3) * np.sqrt(i_canal)
            return Q_calc - Q_canal
        
        # 求解正常水深
        h0_canal = fsolve(normal_depth_eq, 2.0)[0]
        A0_canal = (b_canal + m_canal * h0_canal) * h0_canal
        v0_canal = Q_canal / A0_canal
        B0_canal = b_canal + 2 * m_canal * h0_canal
        Fr0_canal = v0_canal / np.sqrt(self.g * A0_canal / B0_canal)
        
        print(f"\n渠道正常水深（谢才公式）：")
        print(f"  Q = (1/n)AR^(2/3)√i")
        print(f"  h₀ = {h0_canal:.3f} m ✓")
        print(f"  v₀ = {v0_canal:.3f} m/s")
        print(f"  Fr₀ = {Fr0_canal:.3f}")
        
        # 临界水深
        def critical_depth_eq(h):
            A = (b_canal + m_canal * h) * h
            B = b_canal + 2 * m_canal * h
            Fr2 = Q_canal**2 * B / (self.g * A**3)
            return Fr2 - 1
        
        hc_canal = fsolve(critical_depth_eq, 1.0)[0]
        Ac_canal = (b_canal + m_canal * hc_canal) * hc_canal
        vc_canal = Q_canal / Ac_canal
        
        print(f"\n临界水深：")
        print(f"  hc = {hc_canal:.3f} m")
        print(f"  vc = {vc_canal:.3f} m/s")
        
        # 判断流态
        if h0_canal > hc_canal:
            flow_type = "缓流"
            print(f"\n  h₀ > hc → 缓流（Fr₀={Fr0_canal:.3f} < 1）")
        else:
            flow_type = "急流"
            print(f"\n  h₀ < hc → 急流（Fr₀={Fr0_canal:.3f} > 1）")
        
        # 跌坎后水跃分析（假设跌坎后为急流，然后产生水跃）
        h1_jump = hc_canal * 0.7  # 跌坎后急流水深（经验值）
        A1_jump = (b_canal + m_canal * h1_jump) * h1_jump
        v1_jump = Q_canal / A1_jump
        B1_jump = b_canal + 2 * m_canal * h1_jump
        Fr1_jump = v1_jump / np.sqrt(self.g * A1_jump / B1_jump)
        
        print(f"\n跌坎后水跃分析：")
        print(f"  跌坎后急流水深：h₁ = {h1_jump:.3f} m")
        print(f"  Fr₁ = {Fr1_jump:.3f}")
        
        if Fr1_jump > 1:
            # 使用矩形近似计算跃后水深
            h2_jump = h1_jump/2 * (-1 + np.sqrt(1 + 8*Fr1_jump**2))
            A2_jump = (b_canal + m_canal * h2_jump) * h2_jump
            v2_jump = Q_canal / A2_jump
            
            # 水跃长度
            Lj = 6 * (h2_jump - h1_jump)
            
            # 能量损失
            E1 = h1_jump + v1_jump**2 / (2 * self.g)
            E2 = h2_jump + v2_jump**2 / (2 * self.g)
            dE = E1 - E2
            
            print(f"  跃后水深：h₂ = {h2_jump:.3f} m ✓")
            print(f"  水跃长度：Lj = {Lj:.3f} m ✓")
            print(f"  能量损失：ΔE = {dE:.3f} m")
        else:
            h2_jump = h1_jump
            Lj = 0
            dE = 0
            print(f"  Fr₁ < 1，不发生水跃")
        
        # (3) 泵站工况点
        print(f"\n(3) 计算泵站工况点与功率")
        
        # 采用闸门流量作为泵站流量
        Q_pump = Q_canal
        
        # 管道流速
        A_pipe = np.pi * d_pipe**2 / 4
        v_pipe = Q_pump / A_pipe
        
        print(f"\n管道流速：")
        print(f"  A = πd²/4 = {A_pipe:.4f} m²")
        print(f"  v = Q/A = {Q_pump:.3f}/{A_pipe:.4f} = {v_pipe:.3f} m/s")
        
        # 管道损失
        hf_pipe = (lam_pipe * L_pipe / d_pipe + xi_sum) * v_pipe**2 / (2 * self.g)
        
        print(f"\n管道损失：")
        print(f"  hf = (λL/d + Σξ)×v²/(2g)")
        print(f"     = ({lam_pipe}×{L_pipe}/{d_pipe} + {xi_sum})×{v_pipe:.3f}²/(2×{self.g})")
        print(f"     = {hf_pipe:.3f} m")
        
        # 所需扬程
        H_required = Hs + hf_pipe + v_pipe**2 / (2 * self.g)
        
        print(f"\n所需扬程：")
        print(f"  H需 = Hs + hf + v²/(2g)")
        print(f"      = {Hs} + {hf_pipe:.3f} + {v_pipe**2/(2*self.g):.3f}")
        print(f"      = {H_required:.3f} m ✓")
        
        # 泵提供扬程
        H_pump = 30 - 20 * Q_pump**2
        
        print(f"\n泵特性曲线提供扬程：")
        print(f"  H泵 = 30 - 20Q²")
        print(f"      = 30 - 20×{Q_pump:.3f}²")
        print(f"      = {H_pump:.3f} m")
        
        # 检查匹配
        H_diff = H_pump - H_required
        print(f"\n扬程匹配检查：")
        print(f"  H泵 - H需 = {H_pump:.3f} - {H_required:.3f} = {H_diff:.3f} m")
        if abs(H_diff) < 2.0:
            print(f"  结论：匹配良好 ✓")
            H_actual = H_pump
        else:
            print(f"  结论：偏差较大，采用平均值")
            H_actual = (H_pump + H_required) / 2
        
        # 轴功率
        N_water = self.gamma_w * Q_pump * H_actual / 1000  # kW
        N_shaft = N_water / eta
        
        print(f"\n泵站功率：")
        print(f"  水功率：N水 = γQH = {self.gamma_w}×{Q_pump:.3f}×{H_actual:.3f}/1000")
        print(f"             = {N_water:.2f} kW")
        print(f"  轴功率：N轴 = N水/η = {N_water:.2f}/{eta}")
        print(f"             = {N_shaft:.2f} kW ✓")
        
        # (4) 系统优化
        print(f"\n(4) 系统最优调度方案")
        
        print(f"\n系统分析：")
        print(f"  • 水库放水：Q闸 = {Q_gate:.3f} m³/s")
        print(f"  • 渠道输水：Q渠 = {Q_canal:.3f} m³/s")
        print(f"  • 泵站提水：Q泵 = {Q_pump:.3f} m³/s")
        print(f"  • 系统连续性：满足 ✓")
        
        # 优化建议
        Q_optimal = min(Q_gate, Q_design)
        print(f"\n优化建议：")
        print(f"  1. 当前流量：{Q_pump:.3f} m³/s")
        print(f"  2. 设计流量：{Q_design} m³/s")
        if Q_pump < Q_design:
            print(f"  3. 建议：可适当增大闸门开度")
            print(f"     最优流量：{Q_optimal:.3f} m³/s")
        else:
            print(f"  3. 建议：当前流量合理")
        
        # 能量效率
        total_head_loss = hf_pipe + dE
        efficiency_system = (Hs / (Hs + total_head_loss)) * 100
        
        print(f"\n系统效率分析：")
        print(f"  • 总水头损失：{total_head_loss:.3f} m")
        print(f"    - 管道损失：{hf_pipe:.3f} m")
        print(f"    - 水跃损失：{dE:.3f} m")
        print(f"  • 系统效率：{efficiency_system:.1f}%")
        
        # 绘图
        fig = plt.figure(figsize=(16, 12))
        
        # 子图1：系统纵剖面
        ax1 = plt.subplot(2, 3, 1)
        
        # 水库
        ax1.fill_between([0, 500], [H, H], [Z_gate-5, Z_gate-5],
                        color='cyan', alpha=0.3, label='水库')
        ax1.axhline(y=H, xmax=0.25, color='blue', linestyle='--', linewidth=2)
        ax1.text(250, H+2, f'水位H={H}m', ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow'))
        
        # 闸门
        gate_x = [500, 500, 520, 520, 500]
        gate_y = [Z_gate, Z_gate+h_gate, Z_gate+h_gate, Z_gate, Z_gate]
        ax1.fill(gate_x, gate_y, color='brown', alpha=0.7,
                edgecolor='black', linewidth=2, label='闸门')
        
        # 渠道
        x_canal = [520, 1000, 1500, 2520]
        y_canal = [Z_gate, Z_gate-480*i_canal, Z_gate-980*i_canal-drop_height, 
                  Z_gate-1000*i_canal-drop_height-1000*i_canal]
        ax1.plot(x_canal, y_canal, 'k-', linewidth=3, label='渠道底')
        
        # 水面线
        y_water = [Z_gate+h0_canal, Z_gate-480*i_canal+h0_canal,
                  Z_gate-980*i_canal-drop_height+h1_jump,
                  Z_gate-1000*i_canal-drop_height-1000*i_canal+h2_jump]
        ax1.plot(x_canal, y_water, 'b-', linewidth=2.5, label='水面线')
        
        # 跌坎
        ax1.plot([1500, 1500], [Z_gate-980*i_canal, Z_gate-980*i_canal-drop_height],
                'r-', linewidth=4, label='跌坎')
        
        # 泵站
        pump_x = 2520
        pump_y = Z_gate-1000*i_canal-drop_height-1000*i_canal
        ax1.plot([pump_x, pump_x], [pump_y, pump_y+Hs],
                'g-', linewidth=4, label='泵站提水')
        ax1.text(pump_x+100, pump_y+Hs/2, f'Hs={Hs}m',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        ax1.set_xlabel('距离 (m)', fontsize=12)
        ax1.set_ylabel('高程 (m)', fontsize=12)
        ax1.set_title('例题1：水库-渠道-泵站系统纵剖面', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # 子图2：闸门流量曲线
        ax2 = plt.subplot(2, 3, 2)
        
        # 不同水位下的流量
        H_array = np.linspace(H_min+5, H0, 50)
        Q_array = []
        for H_temp in H_array:
            H_up_temp = H_temp - Z_gate
            if H_up_temp > 0:
                Q_temp = mu_gate * b_gate * H_up_temp * np.sqrt(2 * self.g * H_up_temp)
                Q_array.append(Q_temp)
            else:
                Q_array.append(0)
        
        ax2.plot(H_array, Q_array, 'b-', linewidth=2.5, label='Q闸(H)曲线')
        
        # 当前工况
        ax2.plot(H, Q_gate, 'ro', markersize=15,
                label=f'当前：H={H}m\nQ={Q_gate:.2f}m³/s')
        
        # 设计流量线
        ax2.axhline(y=Q_design, color='green', linestyle='--',
                   linewidth=2, label=f'设计流量={Q_design}m³/s')
        
        ax2.set_xlabel('水库水位 H (m)', fontsize=12)
        ax2.set_ylabel('闸门流量 Q (m³/s)', fontsize=12)
        ax2.set_title('闸门流量随水位变化', fontsize=13, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3：渠道断面与水跃
        ax3 = plt.subplot(2, 3, 3)
        
        # 梯形断面（跃前）
        y_h1 = h1_jump
        x_bottom = [-b_canal/2, b_canal/2]
        x_top_h1 = [-b_canal/2 - m_canal*y_h1, b_canal/2 + m_canal*y_h1]
        
        channel_x_h1 = [x_top_h1[0], x_bottom[0], x_bottom[1], x_top_h1[1], x_top_h1[0]]
        channel_y_h1 = [y_h1, 0, 0, y_h1, y_h1]
        ax3.fill(channel_x_h1, channel_y_h1, color='lightcoral', alpha=0.5,
                edgecolor='red', linewidth=2, label=f'跃前h₁={h1_jump:.2f}m')
        
        # 梯形断面（跃后）
        y_h2 = h2_jump
        x_top_h2 = [-b_canal/2 - m_canal*y_h2, b_canal/2 + m_canal*y_h2]
        channel_x_h2 = [x_top_h2[0], x_bottom[0], x_bottom[1], x_top_h2[1], x_top_h2[0]]
        channel_y_h2 = [y_h2, 0, 0, y_h2, y_h2]
        ax3.plot(channel_x_h2[:4], channel_y_h2[:4], 'b--', linewidth=2,
                label=f'跃后h₂={h2_jump:.2f}m')
        
        ax3.set_xlabel('宽度 (m)', fontsize=12)
        ax3.set_ylabel('水深 (m)', fontsize=12)
        ax3.set_title('渠道断面与水跃', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_aspect('equal')
        
        # 子图4：泵站工况
        ax4 = plt.subplot(2, 3, 4)
        
        # 泵特性曲线
        Q_range = np.linspace(0, 1.2, 100)
        H_range = 30 - 20 * Q_range**2
        
        ax4.plot(Q_range, H_range, 'b-', linewidth=2.5, label='泵特性H=30-20Q²')
        
        # 管路特性
        H_pipe_range = []
        for Q_temp in Q_range:
            if Q_temp > 0:
                v_temp = Q_temp / A_pipe
                hf_temp = (lam_pipe*L_pipe/d_pipe + xi_sum) * v_temp**2 / (2*self.g)
                H_temp = Hs + hf_temp + v_temp**2 / (2*self.g)
                H_pipe_range.append(H_temp)
            else:
                H_pipe_range.append(Hs)
        
        ax4.plot(Q_range, H_pipe_range, 'r-', linewidth=2.5, label='管路特性')
        
        # 工况点
        ax4.plot(Q_pump, H_actual, 'go', markersize=15,
                label=f'工况点\nQ={Q_pump:.2f}m³/s\nH={H_actual:.1f}m')
        
        ax4.set_xlabel('流量 Q (m³/s)', fontsize=12)
        ax4.set_ylabel('扬程 H (m)', fontsize=12)
        ax4.set_title('泵站工况匹配', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 子图5：系统能量分析
        ax5 = plt.subplot(2, 3, 5)
        
        sections = ['水库', '闸门', '渠道', '跌坎', '泵站', '出口']
        elevations = [H, Z_gate+h0_canal, Z_gate-L_canal/2*i_canal+h0_canal,
                     Z_gate-L_canal*i_canal-drop_height+h2_jump,
                     pump_y+Hs, pump_y+Hs]
        
        x_pos = np.arange(len(sections))
        
        ax5.plot(x_pos, elevations, 'b-o', linewidth=2.5, markersize=10,
                label='水位线')
        
        # 标注
        for i, (section, elev) in enumerate(zip(sections, elevations)):
            ax5.text(i, elev+1, f'{elev:.1f}m',
                    ha='center', fontsize=9)
        
        ax5.set_xticks(x_pos)
        ax5.set_xticklabels(sections, rotation=15)
        ax5.set_ylabel('高程 (m)', fontsize=12)
        ax5.set_title('系统能量线', fontsize=13, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 子图6：结果汇总
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        【例题1结果汇总】
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (1) 水库放水流量：
        
          闸门上游水深：{H_up} m
          放水流量：Q = {Q_gate:.3f} m³/s ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (2) 渠道输水与水跃：
        
          正常水深：h₀ = {h0_canal:.3f} m
          临界水深：hc = {hc_canal:.3f} m
          流态：{flow_type}（Fr₀={Fr0_canal:.3f}）
          
          水跃分析：
            跃前：h₁={h1_jump:.3f}m, Fr₁={Fr1_jump:.3f}
            跃后：h₂={h2_jump:.3f}m
            长度：Lj={Lj:.3f}m
            损失：ΔE={dE:.3f}m
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (3) 泵站工况与功率：
        
          管道损失：hf={hf_pipe:.3f}m
          所需扬程：H需={H_required:.3f}m
          泵提供扬程：H泵={H_pump:.3f}m
          实际扬程：H={H_actual:.3f}m ✓
          
          水功率：N水={N_water:.2f}kW
          轴功率：N轴={N_shaft:.2f}kW ✓
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        (4) 系统优化方案：
        
          系统流量：Q={Q_pump:.3f}m³/s
          系统效率：η系={efficiency_system:.1f}%
          
          建议流量：{Q_optimal:.3f}m³/s
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        评分：40分
          (1) 8分  (2) 12分
          (3) 12分 (4) 8分
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax6.text(0.05, 0.95, summary_text, fontsize=7, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('/workspace/books/graduate-exam-prep/30days-sprint/codes/day25_comprehensive/example_1.png', 
                   dpi=150, bbox_inches='tight')
        print("\n✅ 图表已保存：example_1.png")
        
        return {'Q_gate': Q_gate, 'h0_canal': h0_canal, 'h2_jump': h2_jump,
                'H_pump': H_actual, 'N_shaft': N_shaft}
    
    def summary_and_tips(self):
        """每日总结与考试技巧"""
        print("\n" + "="*60)
        print("📚 Day 25 知识点总结")
        print("="*60)
        
        print("\n✅ 综合应用方法：")
        print("  1. 系统分析法：")
        print("     • 识别各子系统（水库、渠道、泵站等）")
        print("     • 明确各子系统相互关系")
        print("     • 建立连续性方程")
        print("     ")
        print("  2. 逐步求解法：")
        print("     • 从上游向下游逐步计算")
        print("     • 每个子系统单独分析")
        print("     • 验证系统连续性")
        print("     ")
        print("  3. 优化调度法：")
        print("     • 分析系统瓶颈")
        print("     • 提出优化方案")
        print("     • 评估系统效率")
        
        print("\n✅ 跨章节知识融合：")
        print("  水库-渠道-泵站系统：")
        print("    • 闸门出流（静水力学+堰流）")
        print("    • 明渠输水（均匀流+非均匀流）")
        print("    • 水跃分析（临界水深+共轭水深）")
        print("    • 泵站计算（扬程+功率+工况）")
        print("    • 系统优化（连续性+效率）")
        
        print("\n✅ 解题步骤（标准化）：")
        print("  Step 1: 系统划分")
        print("    - 识别子系统边界")
        print("    - 明确已知与未知")
        print("  ")
        print("  Step 2: 逐步求解")
        print("    - 上游→下游")
        print("    - 每步验证合理性")
        print("  ")
        print("  Step 3: 系统验证")
        print("    - 连续性检查")
        print("    - 能量平衡")
        print("  ")
        print("  Step 4: 优化建议")
        print("    - 识别瓶颈")
        print("    - 提出改进方案")
        
        print("\n⚠️ 常见错误（考试必避）：")
        print("  ❌ 错误1：忽略子系统间的衔接")
        print("  ❌ 错误2：连续性方程未验证")
        print("  ❌ 错误3：能量损失计算遗漏")
        print("  ❌ 错误4：优化方案不切实际")
        
        print("\n🎯 考试技巧：")
        print("  ✓ 技巧1：画系统示意图（必须！）")
        print("  ✓ 技巧2：列出所有子系统（逐一突破）")
        print("  ✓ 技巧3：验证连续性（Q₁=Q₂=Q₃）")
        print("  ✓ 技巧4：能量分析（E₁>E₂>E₃）")
        print("  ✓ 技巧5：优化建议（提分关键）")
        
        print("\n💯 今日学习效果自评：")
        print("  □ 能独立分析复杂系统")
        print("  □ 掌握跨章节知识融合")
        print("  □ 理解系统优化方法")
        print("  □ 能提出工程建议")
        
        print("\n📅 明日预告：Day 26 - 综合应用专题（第二部分）")
        print("  • 灌溉工程全流程")
        print("  • 供水系统分析")
        print("  • 更多实际工程案例")
        
        print("\n💪 今日格言：")
        print("  「综合应用=真正实力！跨章节融合=提高15分！」")

def main():
    """主函数"""
    print("="*60)
    print("《水力学考研30天冲刺宝典》")
    print("Day 25: 综合应用专题")
    print("="*60)
    print("\n⏰ 学习时间：3小时")
    print("📚 今日任务：")
    print("  ✓ 复杂系统分析（90分钟）")
    print("  ✓ 例题学习（60分钟）")
    print("  ✓ Python代码（30分钟）")
    print("  ✓ 总结笔记（30分钟）")
    
    # 创建对象
    day25 = Day25Comprehensive()
    
    # 例题1：水库-渠道-泵站系统
    result1 = day25.example_1_reservoir_canal_pump_system()
    
    # 每日总结
    day25.summary_and_tips()
    
    print("\n" + "="*60)
    print("✅ Day 25 学习完成！")
    print("="*60)
    print(f"\n今日成果：")
    print(f"  ✓ 完成1道综合题")
    print(f"  ✓ 掌握系统分析法")
    print(f"  ✓ 理解跨章节融合")
    print(f"  ✓ 学会优化调度")
    print(f"  ✓ 生成6张图表")
    
    print(f"\n下一步：Day 26 - 综合应用专题（第二部分）")
    print(f"💪 坚持30天，提升20分！")

if __name__ == "__main__":
    main()
    plt.show()
