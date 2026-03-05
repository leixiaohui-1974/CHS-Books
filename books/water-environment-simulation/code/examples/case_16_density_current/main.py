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
案例16：水库异重流模拟
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.density_current import DensityCurrent2D, calculate_densimetric_froude, estimate_underflow_velocity

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例16：水库异重流模拟")
    print("=" * 70)
    
    # 初始化
    model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
    
    # 任务1：潜入点
    x_plunge = model.calculate_plunge_point(C_inflow=10, Q_inflow=50, H_reservoir=50)
    
    # 任务2：异重流模拟
    print("\n任务2：异重流运动模拟")
    C_field = model.simulate_underflow(C_source=10, x_source=5, dt=10, n_steps=500)
    
    # 任务3：取水口评估
    print("\n任务3：取水口风险评估")
    C_intake, risk = model.assess_intake_risk(x_intake=500, z_intake=25, C_threshold=0.5)
    
    # 绘图
    print("\n生成图表...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    X, Z = np.meshgrid(model.x, model.z)
    im = ax.contourf(X, Z, C_field, levels=20, cmap='YlOrRd')
    ax.set_xlabel('Distance (m)', fontsize=12)
    ax.set_ylabel('Depth (m)', fontsize=12)
    ax.set_title('Density Current Simulation', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    plt.colorbar(im, ax=ax, label='Sediment Concentration (kg/m³)')
    
    # 标记取水口
    ax.plot(500, 25, 'r*', markersize=20, label='Intake')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig('density_current.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: density_current.png")
    
    print("\n" + "=" * 70)
    print("案例16完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()