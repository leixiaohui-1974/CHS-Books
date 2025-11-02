# 案例16：水库异重流模拟

## 案例背景
汛期高浓度泥沙水流进入水库，形成异重流潜入底层，影响取水口水质。

## 核心理论
- 密度差驱动流动：Δρ = ρ₀·β·C
- 约化重力：g' = g·Δρ/ρ₀  
- 密度Froude数：Fr = u/√(g'·h)
- 异重流速度：u ≈ √(g'·h)

## 计算任务
1. 潜入点判断
2. 异重流运动模拟
3. 浓度分布分析
4. 取水口风险评估

## 使用说明
```python
from models.density_current import DensityCurrent2D

model = DensityCurrent2D(L=1000, H=50, nx=100, nz=25)
x_plunge = model.calculate_plunge_point(C_inflow=10, Q_inflow=50, H_reservoir=50)
C_field = model.simulate_underflow(C_source=10, x_source=5, dt=10, n_steps=500)
```

## 工程意义
- 水库调度优化
- 取水口选址  
- 分层取水设计

**版本**: v1.0
