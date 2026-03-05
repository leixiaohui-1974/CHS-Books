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
"""案例25：跨流域调水水质风险评估"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.water_transfer import WaterTransferModel, assess_mixing_quality
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例25：跨流域调水水质风险评估")
    print("="*70)
    
    model = WaterTransferModel(channel_length=100, flow_rate=50)
    
    # 藻类生长风险
    light_intensities = [100, 150, 200, 250]
    final_Chls = []
    for light in light_intensities:
        final_Chl, risk = model.simulate_algae_growth_risk(initial_Chl=5, light_intensity=light)
        final_Chls.append(final_Chl)
    
    # 水源混合
    mixed_quality = assess_mixing_quality(source1_quality=15, source2_quality=30, ratio=0.6)
    
    # 绘图
    plt.figure(figsize=(8, 6))
    plt.plot(light_intensities, final_Chls, 'mo-', linewidth=2, markersize=8)
    plt.axhline(y=30, color='r', linestyle='--', label='Bloom Threshold')
    plt.xlabel('Light Intensity (W/m²)')
    plt.ylabel('Final Chl-a (μg/L)')
    plt.title('Algae Growth Risk')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('water_transfer.png', dpi=150)
    print("  ✓ 已保存: water_transfer.png")
    print("\n"+"="*70)
    print("案例25完成！")
    print("="*70)

if __name__ == '__main__':
    main()