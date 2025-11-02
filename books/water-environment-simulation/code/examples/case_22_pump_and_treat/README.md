# 案例22：抽出-处理修复方案优化

## 案例背景
污染场地修复，通过抽水井抽出污染地下水处理。

## 核心理论
- 抽出-处理技术
- 修复优化
- 费用-效益分析

## 计算任务
1. 模拟抽水修复效果
2. 优化抽水井位置
3. 预测修复时间

## 使用说明
```python
from models.pump_and_treat import PumpAndTreat

model = PumpAndTreat(Lx=200, Ly=200, nx=50, ny=50)
t = np.linspace(0, 365, 200)
t_out, C_history, mass_removed = model.simulate_remediation(t, pump_x=100, pump_y=100, Q_pump=50)
```

**版本**: v1.0
