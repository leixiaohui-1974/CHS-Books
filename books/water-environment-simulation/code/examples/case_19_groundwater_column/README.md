# 案例19：一维地下水污染柱实验

## 案例背景
实验室土柱实验，研究污染物在多孔介质中的运移。

## 核心理论

**控制方程**：
```
R * ∂C/∂t + v * ∂C/∂x = D * ∂²C/∂x²
```

**阻滞因子**：
```
R = 1 + ρb*Kd/θ
```

## 计算任务
1. 建立1D对流-弥散-吸附模型
2. 模拟穿透曲线
3. 分析阻滞效应
4. 预测污染羽到达时间

## 使用说明
```python
from models.groundwater_transport import GroundwaterColumn1D

model = GroundwaterColumn1D(L=1.0, nx=100, theta=0.3, Kd=0.5)
t = np.linspace(0, 10, 200)
t_out, x_out, C_history = model.solve(t, v=0.1, D=0.01, C_in=100)
```

**版本**: v1.0
