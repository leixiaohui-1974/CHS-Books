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
案例22：抽出-处理修复方案优化
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.pump_and_treat import PumpAndTreat, optimize_well_location

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例22：抽出-处理修复方案优化")
    print("=" * 70)
    
    # 初始化
    model = PumpAndTreat(Lx=200, Ly=200, nx=50, ny=50)
    
    # 初始污染分布
    for i in range(model.ny):
        for j in range(model.nx):
            x = j * model.dx
            y = i * model.dy
            r = np.sqrt((x - 80)**2 + (y - 100)**2)
            model.C[i, j] = 100 * np.exp(-r**2 / 1000)
    
    # 优化抽水井位置
    pump_x, pump_y = optimize_well_location((model.Lx, model.Ly), (80, 100))
    
    # 模拟修复
    t = np.linspace(0, 365, 200)
    t_out, C_history, mass_removed = model.simulate_remediation(t, pump_x, pump_y, Q_pump=50, D=5)
    
    # 绘图
    print("\n生成图表...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    time_indices = [0, len(C_history)//3, 2*len(C_history)//3, -1]
    time_labels = ['t=0d', 't=122d', 't=244d', 't=365d']
    
    for idx, (ti, label) in enumerate(zip(time_indices, time_labels)):
        ax = axes[idx//2, idx%2]
        
        x = np.linspace(0, model.Lx, model.nx)
        y = np.linspace(0, model.Ly, model.ny)
        
        im = ax.contourf(x, y, C_history[ti], levels=20, cmap='RdYlBu_r')
        ax.plot(pump_x, pump_y, 'k^', markersize=12, label='Pump Well')
        ax.set_xlabel('X (m)', fontsize=11)
        ax.set_ylabel('Y (m)', fontsize=11)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax, label='C (mg/L)')
    
    plt.tight_layout()
    plt.savefig('pump_and_treat.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: pump_and_treat.png")
    
    print("\n" + "=" * 70)
    print("案例22完成！Phase 5全部完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()