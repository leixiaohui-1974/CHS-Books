# --- CHS AUTOMATED ENVIRONMENT FIX ---
import sys, os
# Super safe I/O override for Windows legacy scripts
class SafeWriter:
    def __init__(self, target):
        self.target = target
    def write(self, s):
        try:
            self.target.write(s)
        except UnicodeEncodeError:
            self.target.write(s.encode('utf-8', 'backslashreplace').decode('gbk', 'ignore'))
    def flush(self):
        if hasattr(self.target, 'flush'): self.target.flush()
    def __getattr__(self, name):
        return getattr(self.target, name)

if not getattr(sys.stdout, '_chs_safe', False):
    sys.stdout = SafeWriter(sys.stdout)
    sys.stdout._chs_safe = True
if not getattr(sys.stderr, '_chs_safe', False):
    sys.stderr = SafeWriter(sys.stderr)
    sys.stderr._chs_safe = True

_current_dir = os.path.dirname(os.path.abspath(__file__))
for i in range(4):
    _test_path = os.path.abspath(os.path.join(_current_dir, *(['..'] * i)))
    if os.path.exists(os.path.join(_test_path, 'core')) or os.path.exists(os.path.join(_test_path, 'gwflow')) or os.path.exists(os.path.join(_test_path, 'models')) or os.path.exists(os.path.join(_test_path, 'code', 'core')):
        if _test_path not in sys.path:
            sys.path.insert(0, _test_path)
        code_dir = os.path.join(_test_path, 'code')
        if os.path.exists(code_dir) and code_dir not in sys.path:
            sys.path.insert(0, code_dir)
        break
# -------------------------------------
"""
案例19：一维地下水污染柱实验
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.groundwater_transport import (GroundwaterColumn1D, 
                                          calculate_retardation_factor,
                                          calculate_breakthrough_time)

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例19：一维地下水污染柱实验")
    print("=" * 70)
    
    # 参数
    L = 1.0  # 土柱长度 (m)
    theta = 0.3  # 孔隙度
    rho_b = 1.5  # 干容重 (g/cm³)
    v = 0.1  # 渗流速度 (m/d)
    D = 0.01  # 弥散系数 (m²/d)
    C_in = 100  # 入口浓度 (mg/L)
    
    # 对比不同Kd
    Kd_values = [0, 0.5, 1.0]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    for Kd in Kd_values:
        print(f"\n{'='*70}")
        print(f"情景：Kd = {Kd} cm³/g")
        print('='*70)
        
        # 初始化模型
        model = GroundwaterColumn1D(L=L, nx=100, theta=theta, rho_b=rho_b, Kd=Kd)
        
        # 计算穿透时间
        t_bt = calculate_breakthrough_time(L, v, model.R)
        
        # 模拟
        t = np.linspace(0, 15, 300)
        t_out, x_out, C_history = model.solve(t, v, D, C_in)
        
        # 穿透曲线（出口）
        ax1.plot(t_out, C_history[:, -1], linewidth=2, label=f'Kd={Kd}')
        
        # 浓度分布（最终时刻）
        ax2.plot(x_out, C_history[-1, :], linewidth=2, label=f'Kd={Kd}')
        
        # 时空图
        if Kd == 0.5:
            im = ax3.contourf(x_out, t_out, C_history, levels=20, cmap='RdYlBu_r')
            plt.colorbar(im, ax=ax3, label='C (mg/L)')
    
    ax1.set_xlabel('Time (d)', fontsize=12)
    ax1.set_ylabel('C (mg/L)', fontsize=12)
    ax1.set_title('Breakthrough Curves', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Distance (m)', fontsize=12)
    ax2.set_ylabel('C (mg/L)', fontsize=12)
    ax2.set_title('Concentration Profiles (t=15d)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax3.set_xlabel('Distance (m)', fontsize=12)
    ax3.set_ylabel('Time (d)', fontsize=12)
    ax3.set_title('Spatiotemporal Distribution (Kd=0.5)', fontsize=14, fontweight='bold')
    
    # 阻滞因子对比
    R_values = [calculate_retardation_factor(theta, rho_b, Kd) for Kd in Kd_values]
    ax4.bar([f'Kd={Kd}' for Kd in Kd_values], R_values, color=['blue', 'orange', 'green'])
    ax4.set_ylabel('Retardation Factor', fontsize=12)
    ax4.set_title('Effect of Sorption', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('groundwater_column.png', dpi=150, bbox_inches='tight')
    print("\n  ✓ 已保存: groundwater_column.png")
    
    print("\n" + "=" * 70)
    print("案例19完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()