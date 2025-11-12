#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例14：模型预测控制（MPC）- 简化版演示
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 必须在import pyplot之前设置
import matplotlib.pyplot as plt
from scipy.optimize import minimize

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

print("=" * 80)
print("案例14：模型预测控制（MPC）演示")
print("=" * 80)

# 系统参数
A_tank, R, K = 2.5, 1.8, 1.2
a = -1/(A_tank * R)
b = K/A_tank

print(f"\n[系统模型] dy/dt = {a:.4f}*y + {b:.4f}*u")

# MPC参数
N = 10  # 预测步长
dt = 0.5
lambda_u = 0.1  # 控制权重

print(f"\n[MPC参数] N={N}, λ={lambda_u}")

# 约束
y_min, y_max = 0.0, 3.0
u_min, u_max = 0.0, 1.0

print(f"\n[约束] y∈[{y_min}, {y_max}], u∈[{u_min}, {u_max}]")

# 仿真
t_sim = np.arange(0, 50, dt)
y = np.zeros(len(t_sim))
u = np.zeros(len(t_sim))
y[0] = 0.5

# 参考轨迹（阶跃变化）
r = 2.0 * np.ones(len(t_sim))
r[int(len(t_sim)*0.6):] = 1.5

for k in range(len(t_sim)-1):
    # MPC优化
    def cost(u_seq):
        y_pred = y[k]
        J = 0
        for i in range(N):
            if k+i >= len(t_sim):
                break
            u_val = np.clip(u_seq[i], u_min, u_max)
            y_pred = y_pred + (a*y_pred + b*u_val) * dt
            J += (y_pred - r[k+i])**2 + lambda_u * u_val**2
        return J
    
    u0 = np.ones(N) * 0.5
    res = minimize(cost, u0, method='L-BFGS-B', 
                   bounds=[(u_min, u_max)]*N)
    u[k] = res.x[0]
    
    # 系统更新
    y[k+1] = y[k] + (a*y[k] + b*u[k]) * dt
    
    if k % 20 == 0:
        print(f"t={t_sim[k]:.1f}: y={y[k]:.3f}, u={u[k]:.3f}, r={r[k]:.1f}")

# 可视化
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

axes[0].plot(t_sim, y, 'b-', linewidth=2, label='MPC Output')
axes[0].plot(t_sim, r, 'r--', linewidth=2, label='Reference')
axes[0].axhline(y_max, color='gray', linestyle=':', alpha=0.5)
axes[0].set_ylabel('Water Level (m)')
axes[0].set_title('MPC Control Performance')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(t_sim, u, 'g-', linewidth=2)
axes[1].axhline(u_max, color='r', linestyle=':', alpha=0.5)
axes[1].axhline(u_min, color='r', linestyle=':', alpha=0.5)
axes[1].set_xlabel('Time (min)')
axes[1].set_ylabel('Control Input')
axes[1].set_title('Control Signal')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('case14_mpc_demo.png', dpi=150)
print("\n图表已保存：case14_mpc_demo.png")

print("\n" + "=" * 80)
print("MPC演示完成！")
print("优势：自动处理约束，优化性能")
print("=" * 80)

plt.show()
