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
"""案例24：河湖水系连通与水质改善"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.river_network import RiverNetworkModel, optimize_gate_schedule
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例24：河湖水系连通与水质改善")
    print("="*70)
    
    model = RiverNetworkModel(n_nodes=10, n_gates=5)
    
    # 闸门调度
    openings = np.linspace(0.2, 1.0, 5)
    outflows = [model.simulate_gate_operation(o, inflow=10) for o in openings]
    
    # 换水周期
    exchange_time = model.calculate_water_exchange_time(volume=50000, flow_rate=5)
    
    # 优化调度
    optimal_opening = optimize_gate_schedule(target_quality=20, current_quality=35)
    
    # 绘图
    plt.figure(figsize=(8, 6))
    plt.plot(openings*100, outflows, 'g^-', linewidth=2, markersize=8)
    plt.xlabel('Gate Opening (%)')
    plt.ylabel('Outflow (m³/s)')
    plt.title('Gate Operation Curve')
    plt.grid(True, alpha=0.3)
    plt.savefig('river_network.png', dpi=150)
    print("  ✓ 已保存: river_network.png")
    print("\n"+"="*70)
    print("案例24完成！")
    print("="*70)

if __name__ == '__main__':
    main()