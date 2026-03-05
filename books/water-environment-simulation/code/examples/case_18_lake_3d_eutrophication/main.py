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
案例18：三维湖泊富营养化模拟
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.lake_3d_eutrophication import Lake3DEutrophication, calculate_bloom_area

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例18：三维湖泊富营养化模拟")
    print("=" * 70)
    
    # 初始化
    model = Lake3DEutrophication(Lx=10000, Ly=8000, H=3, nx=50, ny=40, nz=3)
    
    # 初始藻类分布（点源释放）
    model.Chl[0, 20, 25] = 50  # 表层中心高浓度
    
    # 模拟风驱动输运
    print("\n模拟风驱动输运...")
    Chl_field = model.simulate_wind_driven_transport(wind_speed=5, wind_dir=90, dt=100, n_steps=200)
    
    # 水华面积
    area_fraction = calculate_bloom_area(Chl_field, threshold=30)
    
    # 绘图
    print("\n生成图表...")
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 表层分布
    im = ax.contourf(model.x/1000, model.y/1000, Chl_field[0, :, :], levels=20, cmap='YlGn')
    ax.set_xlabel('X (km)', fontsize=12)
    ax.set_ylabel('Y (km)', fontsize=12)
    ax.set_title('Surface Chlorophyll-a Distribution', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Chl-a (μg/L)')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('lake_3d_chl.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: lake_3d_chl.png")
    
    print("\n" + "=" * 70)
    print("案例18完成！Phase 4全部完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()