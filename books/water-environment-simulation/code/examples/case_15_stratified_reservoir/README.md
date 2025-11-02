# 案例15：水库温度分层与水质模拟

## 案例背景

深水水库（80m）夏季温度分层明显，底层DO下降导致水质问题。

## 核心理论

**1D垂向扩散方程**：
```
∂T/∂t = ∂/∂z(Kz * ∂T/∂z)
∂DO/∂t = ∂/∂z(Kz * ∂DO/∂z) + 光合作用 - 呼吸 - SOD
```

**关键参数**：
- Kz：垂向扩散系数（强分层<1e-5 m²/d，弱分层>1e-3 m²/d）
- SOD：沉积物耗氧速率（0.1-2 g/m²/d）

## 计算任务

1. 建立1D垂向温度模型
2. 模拟分层演变
3. 耦合DO模型
4. 分析底层缺氧
5. 评估改善措施

## 使用说明

```python
from models.stratified_reservoir import StratifiedReservoir1D

# 初始化
model = StratifiedReservoir1D(H=80, nz=41)

# 设置扩散系数（强分层）
model.set_vertical_diffusivity(Kz=1e-5)

# 求解温度场
t = np.linspace(0, 90, 100)
t_out, T_field = model.solve_temperature_1d(t, T_surface=25)

# 求解DO场
t_out, DO_field = model.solve_do_1d(t)

# 评估缺氧风险
anoxic_depth, fraction = model.assess_anoxia_risk(DO_threshold=2.0)
```

## 工程意义

- 水库水质管理
- 取水口选址
- 曝气方案设计
- 底层缺氧防控

---

**版本**: v1.0  
**完成时间**: 2025-11-02
