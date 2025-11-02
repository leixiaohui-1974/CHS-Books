# 案例17：湖泊藻类生长动力学模拟

## 案例背景
浅水湖泊夏季蓝藻暴发，需模拟藻类生长动力学，评估营养盐削减效果。

## 核心理论

**藻类生长方程**：
```
dChl/dt = (μ - r - m) * Chl
μ = μ_max * f_N * f_P * f_I * f_T
```

**限制因子**：
- Monod方程（营养盐）
- Steele方程（光照）
- 温度影响

## 计算任务
1. 建立藻类-营养盐-DO耦合模型
2. 模拟季节演替
3. 分析限制因子
4. 评估削减效果

## 使用说明
```python
from models.algae_dynamics import AlgaeGrowthModel

model = AlgaeGrowthModel(Chl0=5, N0=500, P0=50)
t = np.linspace(0, 180, 1000)
t_out, result = model.solve(t, I=200, T=25)
```

**版本**: v1.0
