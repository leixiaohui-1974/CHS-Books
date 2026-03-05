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
"""案例26：河流生态系统模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.river_ecosystem import RiverEcosystemModel, calculate_biodiversity_index
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例26：河流生态系统模拟")
    print("="*70)
    
    model = RiverEcosystemModel()
    t = np.linspace(0, 100, 500)
    t_out, result = model.solve(t)
    
    # 生物多样性
    H = calculate_biodiversity_index(result[-1, :])
    
    # 绘图
    plt.figure(figsize=(10, 6))
    plt.plot(t_out, result[:, 0], 'g-', linewidth=2, label='Algae')
    plt.plot(t_out, result[:, 1], 'b-', linewidth=2, label='Zooplankton')
    plt.plot(t_out, result[:, 2], 'r-', linewidth=2, label='Fish')
    plt.xlabel('Time (d)')
    plt.ylabel('Biomass (mg/L)')
    plt.title('River Ecosystem Dynamics')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('river_ecosystem.png', dpi=150)
    print("  ✓ 已保存: river_ecosystem.png")
    print("\n"+"="*70)
    print("案例26完成！")
    print("="*70)

if __name__ == '__main__':
    main()