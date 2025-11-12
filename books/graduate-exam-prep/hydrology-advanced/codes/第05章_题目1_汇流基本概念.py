"""
第5章 流域汇流
题目1：汇流基本概念

知识点：
- 汇流过程
- 汇流时间估算
- 洪峰模数
- 影响因素分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
F = 80  # km²
L = 15  # km
J = 0.005
i_runoff = 10  # mm/h
rain_duration = 3  # h
Qp = 45  # m³/s
peak_time = rain_duration + 1.5  # h

# 计算
qp = Qp / F  # m³/s/km²
tau_observed = peak_time  # h

# 基尔皮齐公式估算汇流时间
tau_kirpich = 0.278 * L / ((J * i_runoff)**0.333)

print("="*70)
print("题目1：汇流基本概念")
print("="*70)
print(f"\n流域参数：")
print(f"  流域面积 F = {F} km²")
print(f"  主河道长度 L = {L} km")
print(f"  河道坡降 J = {J}")
print(f"  产流强度 i = {i_runoff} mm/h")
print(f"\n观测数据：")
print(f"  降雨历时 = {rain_duration} h")
print(f"  洪峰流量 Qp = {Qp} m³/s")
print(f"  洪峰出现时间 = 降雨结束后{peak_time - rain_duration} h")
print(f"\n计算结果：")
print(f"  洪峰模数 qp = Qp/F = {qp:.4f} m³/(s·km²) = {qp*1000:.1f} L/(s·km²)")
print(f"  汇流时间（观测） τ ≈ {tau_observed:.1f} h")
print(f"  汇流时间（基尔皮齐） τ = {tau_kirpich:.1f} h")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：汇流过程示意图
ax1 = fig.add_subplot(gs[0, :2])
time = np.linspace(0, 10, 100)
# 模拟降雨过程
rainfall = np.zeros_like(time)
rainfall[(time >= 0) & (time <= 3)] = i_runoff
# 模拟径流过程（简化的三角形）
runoff = np.zeros_like(time)
peak_idx = np.argmin(np.abs(time - peak_time))
runoff[:peak_idx] = np.linspace(0, Qp, peak_idx)
runoff[peak_idx:] = Qp * np.exp(-0.5*(time[peak_idx:] - peak_time))

ax1.fill_between(time, 0, rainfall, alpha=0.3, color='blue', label='降雨过程')
ax1.plot(time, runoff, 'r-', linewidth=2, label='出口断面流量过程')
ax1.plot(peak_time, Qp, 'ro', markersize=12, label=f'洪峰 Qp={Qp} m³/s')
ax1.axvline(3, color='gray', linestyle='--', alpha=0.7, label='降雨结束')
ax1.axhline(0, color='black', linewidth=1)
ax1.set_xlabel('时间 (h)', fontsize=11)
ax1.set_ylabel('流量 (m³/s) / 雨强 (mm/h)', fontsize=11)
ax1.set_title('题目1-1：降雨-径流过程', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 10)

# 标注汇流时间
ax1.annotate('', xy=(peak_time, Qp/2), xytext=(0, Qp/2),
             arrowprops=dict(arrowstyle='<->', color='green', lw=2))
ax1.text(peak_time/2, Qp/2 + 2, f'汇流时间 τ ≈ {tau_observed:.1f} h',
         fontsize=10, ha='center', color='green', fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

# 子图2：流域汇流示意图
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')

# 绘制流域
basin = Polygon([(1, 2), (9, 2), (9, 8), (5, 9), (1, 8)],
                facecolor='lightgreen', edgecolor='darkgreen', linewidth=2, alpha=0.4)
ax2.add_patch(basin)

# 河道
ax2.plot([1, 5, 9], [2, 5, 8], 'b-', linewidth=3, label='河道')

# 出口
ax2.plot(9, 8, 'ro', markersize=15, label='出口断面')
ax2.text(9.3, 8, '出口', fontsize=9, va='center')

# 最远点
ax2.plot(1, 2, 'g^', markersize=12, label='最远点')
ax2.text(1, 1.5, '最远点', fontsize=9, ha='center')

# 汇流路径
ax2.annotate('', xy=(9, 8), xytext=(1, 2),
             arrowprops=dict(arrowstyle='->', color='red', lw=2, linestyle='--'))
ax2.text(5, 4, f'L={L}km', fontsize=10, rotation=45, color='red', fontweight='bold')

# 坡面汇流示意
for x, y in [(2, 6), (4, 7), (6, 6), (7, 4)]:
    ax2.annotate('', xy=(x+0.5, y-0.5), xytext=(x, y),
                 arrowprops=dict(arrowstyle='->', color='blue', lw=1, alpha=0.6))

ax2.set_title('题目1-2：流域汇流示意', fontsize=11, fontweight='bold')
ax2.legend(fontsize=9, loc='lower left')

# 子图3：洪峰模数计算
ax3 = fig.add_subplot(gs[1, 0])
ax3.axis('off')
calc_text = f"""
洪峰模数计算：

1. 定义
   qp = Qp / F
   
2. 物理意义
   单位面积的洪峰流量
   
3. 计算
   Qp = {Qp} m³/s
   F = {F} km²
   
   qp = {Qp}/{F}
      = {qp:.4f} m³/(s·km²)
      = {qp*1000:.1f} L/(s·km²)
      
4. 典型值参考
   • 山区小流域: 1-5
   • 平原流域: 0.1-0.5
   • 城市流域: 0.5-2
   (单位: m³/(s·km²))
"""
ax3.text(0.05, 0.95, calc_text, transform=ax3.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

# 子图4：汇流时间估算
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')
time_calc = f"""
汇流时间估算：

方法1: 观测法
  • 降雨历时: {rain_duration} h
  • 洪峰出现: 降雨结束后{peak_time-rain_duration} h
  • τ ≈ {tau_observed:.1f} h
  
方法2: 基尔皮齐公式
  τ = 0.278·L/(J·i)^0.333
  
  参数:
    L = {L} km
    J = {J}
    i = {i_runoff} mm/h
  
  计算:
    τ = 0.278×{L}/{(J*i_runoff)**0.333:.3f}
      = {tau_kirpich:.1f} h
      
注: 两种方法差异较大
    • 观测法受实际条件影响
    • 公式法为理论估算
"""
ax4.text(0.05, 0.95, time_calc, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7))

# 子图5：影响因素树状图
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 10)
ax5.axis('off')

# 标题
ax5.text(5, 9, '影响汇流的因素', ha='center', fontsize=11,
         fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightblue'))

# 四大类因素
factors = [
    ('地形', 2.5, ['面积', '形状', '坡度', '河网']),
    ('河道', 7.5, ['长度', '坡降', '糙率'])
]

for cat_name, x_pos, items in factors:
    # 类别框
    cat_box = FancyBboxPatch((x_pos-1, 7), 2, 0.8,
                              boxstyle="round,pad=0.05",
                              facecolor='lightgreen', edgecolor='green', linewidth=2)
    ax5.add_patch(cat_box)
    ax5.text(x_pos, 7.4, cat_name, ha='center', va='center',
             fontsize=10, fontweight='bold')
    
    # 连线到标题
    ax5.plot([x_pos, 5], [7, 8.5], 'k-', linewidth=1.5, alpha=0.5)
    
    # 因素列表
    y_start = 5.5
    for i, item in enumerate(items):
        y = y_start - i*1
        ax5.text(x_pos, y, f'• {item}', ha='center', fontsize=9)
        ax5.plot([x_pos, x_pos], [y+0.3, 7], 'k-', linewidth=0.5, alpha=0.3)

# 下垫面和降雨因素
ax5.text(2.5, 3, '下垫面', ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat'))
ax5.text(2.5, 2.3, '植被·土壤', ha='center', fontsize=8)

ax5.text(7.5, 3, '降雨', ha='center', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat'))
ax5.text(7.5, 2.3, '强度·分布', ha='center', fontsize=8)

ax5.set_title('题目1-3：影响因素分类', fontsize=11, fontweight='bold', pad=15)

# 子图6：不同流域形状对汇流的影响
ax6 = fig.add_subplot(gs[2, :])
# 三种流域形状的洪水过程线
time_range = np.linspace(0, 10, 100)

# 扇形流域（汇流时间接近）→洪峰尖瘦
Q_fan = np.zeros_like(time_range)
peak_fan = 4
Q_fan = 50 * np.exp(-2*(time_range - peak_fan)**2)

# 长条形流域（汇流时间差异大）→洪峰平缓
Q_long = np.zeros_like(time_range)
peak_long = 5
Q_long = 35 * np.exp(-0.5*(time_range - peak_long)**2)

# 一般形状
Q_normal = np.zeros_like(time_range)
peak_normal = 4.5
Q_normal = 42 * np.exp(-1*(time_range - peak_normal)**2)

ax6.plot(time_range, Q_fan, 'r-', linewidth=2, label='扇形流域（汇流集中→洪峰尖瘦）')
ax6.plot(time_range, Q_long, 'b-', linewidth=2, label='长条形流域（汇流分散→洪峰平缓）')
ax6.plot(time_range, Q_normal, 'g--', linewidth=2, label='一般形状流域')

# 标注洪峰
ax6.plot(peak_fan, 50, 'ro', markersize=10)
ax6.plot(peak_long, 35, 'bo', markersize=10)
ax6.plot(peak_normal, 42, 'go', markersize=10)

ax6.set_xlabel('时间 (h)', fontsize=11)
ax6.set_ylabel('流量 (m³/s)', fontsize=11)
ax6.set_title('题目1-4：流域形状对洪水过程线的影响', fontsize=12, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 10)
ax6.set_ylim(0, 60)

plt.savefig('题目1_汇流基本概念.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_汇流基本概念.png")
plt.show()
