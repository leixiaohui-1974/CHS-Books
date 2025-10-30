#!/usr/bin/env python3
"""
案例14扩展实验：MPC参数影响
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

print("=" * 80)
print("案例14扩展实验：预测步长影响")
print("=" * 80)

A_tank, R, K = 2.5, 1.8, 1.2
a, b = -1/(A_tank * R), K/A_tank
dt = 0.5

N_values = [5, 10, 20]
results = {}

for N in N_values:
    print(f"\n测试 N={N}")
    t = np.arange(0, 30, dt)
    y = np.zeros(len(t))
    y[0] = 0.5
    r = 2.0
    
    for k in range(len(t)-1):
        def cost(u_seq):
            y_p = y[k]
            J = 0
            for i in range(N):
                u_v = np.clip(u_seq[i], 0, 1)
                y_p = y_p + (a*y_p + b*u_v) * dt
                J += (y_p - r)**2 + 0.1*u_v**2
            return J
        
        res = minimize(cost, np.ones(N)*0.5, 
                      method='L-BFGS-B', bounds=[(0,1)]*N)
        y[k+1] = y[k] + (a*y[k] + b*res.x[0]) * dt
    
    results[N] = y
    print(f"  最终值: {y[-1]:.3f}")

# 可视化
plt.figure(figsize=(10, 6))
for N in N_values:
    plt.plot(np.arange(0, 30, dt), results[N], 
             linewidth=2, label=f'N={N}')

plt.axhline(2.0, color='r', linestyle='--', label='Reference')
plt.xlabel('Time (min)')
plt.ylabel('Water Level (m)')
plt.title('Effect of Prediction Horizon N')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('exp_mpc_horizon.png', dpi=150)
print("\n图表已保存：exp_mpc_horizon.png")
print("\n结论：N越大，预测越准确，但计算量增加")
print("=" * 80)

plt.show()
