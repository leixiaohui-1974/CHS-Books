# 案例20：二维含水层污染羽迁移

## 案例背景
化工厂渗漏，污染物进入地下水，形成污染羽。

## 核心理论

**控制方程**：
```
∂C/∂t + v·∇C = ∇·(D∇C) - λC
```

## 计算任务
1. 建立2D溶质运移模型
2. 模拟污染羽扩展
3. 预测水井污染风险
4. 评估阻截方案

## 使用说明
```python
from models.aquifer_2d import Aquifer2D

model = Aquifer2D(Lx=500, Ly=300, nx=100, ny=60)
t = np.linspace(0, 365, 200)
t_out, C_history = model.solve_transport(t, vx=0.5, vy=0, Dx=5, Dy=2, source_x=50, source_y=150)
```

**版本**: v1.0
