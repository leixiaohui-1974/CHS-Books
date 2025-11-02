# 案例18：三维湖泊富营养化模拟

## 案例背景
大型浅水湖泊，风生流作用显著，藻类空间分布不均，需3D模拟。

## 核心理论
- 3D水动力-水质-生态耦合
- 风驱动湖流
- 藻类输运与聚集

## 计算任务
1. 建立简化3D模型
2. 模拟风驱动输运
3. 评估水华面积

## 使用说明
```python
from models.lake_3d_eutrophication import Lake3DEutrophication

model = Lake3DEutrophication(Lx=10000, Ly=8000, H=3, nx=50, ny=40, nz=3)
Chl_field = model.simulate_wind_driven_transport(wind_speed=5, wind_dir=90, dt=100, n_steps=100)
```

**版本**: v1.0
