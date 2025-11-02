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
