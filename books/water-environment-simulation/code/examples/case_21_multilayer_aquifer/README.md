# 案例21：多层含水层垂向迁移

## 案例背景
垃圾填埋场渗滤液污染潜水和承压含水层。

## 核心理论
- 多层含水层系统
- 垂向扩散
- 隔水层保护

## 计算任务
1. 建立多层模型
2. 模拟垂向迁移
3. 评估隔水层保护效果

## 使用说明
```python
from models.multilayer_aquifer import MultilayerAquifer

model = MultilayerAquifer(layers=20, dz=2)
t = np.linspace(0, 365, 200)
t_out, z_out, C_history = model.solve(t, Kz=0.1, theta=0.3)
```

**版本**: v1.0
