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
"""案例23：流域水文-水质耦合模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.watershed_model import WatershedModel, assess_land_use_impact
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例23：流域水文-水质耦合模拟")
    print("="*70)
    
    model = WatershedModel(area=500, n_subbasins=5)
    
    # 模拟不同降雨
    rainfalls = [20, 50, 100, 150]
    runoffs = [model.simulate_runoff(r) for r in rainfalls]
    loads = [model.calculate_pollutant_load(r, EMC=50) for r in runoffs]
    
    # 土地利用影响
    impact = assess_land_use_impact(0.4, 0.3)
    
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(rainfalls, runoffs, 'bo-', linewidth=2)
    ax1.set_xlabel('Rainfall (mm)')
    ax1.set_ylabel('Runoff (mm)')
    ax1.set_title('Rainfall-Runoff')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(rainfalls, loads, 'ro-', linewidth=2)
    ax2.set_xlabel('Rainfall (mm)')
    ax2.set_ylabel('Pollutant Load (kg)')
    ax2.set_title('Pollutant Load')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('watershed.png', dpi=150)
    print("  ✓ 已保存: watershed.png")
    print("\n"+"="*70)
    print("案例23完成！")
    print("="*70)

if __name__ == '__main__':
    main()