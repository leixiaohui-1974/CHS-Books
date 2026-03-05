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
"""案例28：湿地生态系统净化功能模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.wetland_model import WetlandModel, assess_seasonal_variation
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例28：湿地生态系统净化功能模拟")
    print("="*70)
    
    model = WetlandModel(area=1000, depth=0.5, porosity=0.4)
    
    # 不同HRT下的去除效率
    HRTs = np.linspace(1, 10, 10)
    efficiencies = []
    for HRT in HRTs:
        C_out, eff = model.calculate_removal(C_in=50, HRT=HRT, k_removal=0.3)
        efficiencies.append(eff)
    
    # 设计优化
    required_HRT, required_area = model.optimize_design(target_efficiency=80, C_in=50, k_removal=0.3)
    
    # 季节变化
    summer_k, winter_k = assess_seasonal_variation(25, 5)
    
    # 绘图
    plt.figure(figsize=(8, 6))
    plt.plot(HRTs, efficiencies, 'cs-', linewidth=2, markersize=8)
    plt.axhline(y=80, color='r', linestyle='--', label='Target (80%)')
    plt.xlabel('HRT (d)')
    plt.ylabel('Removal Efficiency (%)')
    plt.title('Wetland Treatment Performance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('wetland.png', dpi=150)
    print("  ✓ 已保存: wetland.png")
    print("\n"+"="*70)
    print("案例28完成！")
    print("="*70)

if __name__ == '__main__':
    main()