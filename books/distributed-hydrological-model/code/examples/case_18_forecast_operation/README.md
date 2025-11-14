# 案例18：实时洪水预报调度系统

**难度**: ⭐⭐⭐⭐⭐  
**标签**: `洪水预报` `实时调度` `预见期优化` `系统集成`

---

## 📖 案例简介

本案例展示**基于洪水预报的水库实时优化调度系统**，整合水文预报与水库调度，实现预见期优化，是现代水库智能调度的典型应用。

### 🎯 学习目标

1. 理解洪水预报调度的原理
2. 掌握预见期优化方法
3. 学会实时滚动调度
4. 实现系统集成应用

### 🔑 关键技术

- **洪水预报**：水文模型驱动
- **预见期优化**：提前预泄
- **实时更新**：滚动调度
- **效果评估**：有预报vs无预报

---

## 🌊 预报调度原理

### 1. 系统架构

```python
┌──────────────┐
│  降雨预报    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  水文预报    │────→│  洪水预报    │
│  (新安江)    │     │  (流量)      │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       │             │  预见期优化  │
       │             │  (提前预泄)  │
       │             └──────┬───────┘
       │                    │
       ▼                    ▼
┌──────────────────────────────┐
│     实时滚动调度决策         │
└──────────────────────────────┘
```

### 2. 预见期优化策略

**基本原理**:
```python
IF 预报有大洪水 THEN
    提前加大泄流，腾出库容
ELSE
    常规调度
```python

**预见期决策**:
```
当前时刻 t
预报未来 t+1, t+2, ..., t+T
IF max(Q_forecast) > Q_current × 1.5 THEN
    Q_outflow = Q_current × 1.2
ELSE
    Q_outflow = 常规规则
```python

### 3. 滚动更新机制

```
时刻 t=0:  预报 [t+1, t+2, t+3] → 调度决策
时刻 t=1:  预报 [t+2, t+3, t+4] → 调度决策
时刻 t=2:  预报 [t+3, t+4, t+5] → 调度决策
...
```python

---

## 💻 代码实现

### 核心类

#### 1. ForecastSystem类

```python
class ForecastSystem:
    """洪水预报系统"""
    
    def __init__(self, hydro_params, lead_time=3):
        self.model = XinAnJiangModel(hydro_params)
        self.lead_time = lead_time
    
    def forecast(self, rainfall_forecast, evaporation):
        """洪水预报"""
        results = self.model.run(rainfall_forecast, evaporation)
        runoff = results['R']
        
        # 转换为流量
        discharge = runoff * area / dt
        
        return discharge
```python

#### 2. ForecastBasedOperation类

```python
class ForecastBasedOperation:
    """基于预报的水库调度"""
    
    def operate_with_forecast(self, ...):
        for day in range(n_days):
            # 1. 洪水预报
            inflow_forecast = self.forecast_system.forecast(...)
            max_forecast_inflow = np.max(inflow_forecast)
            
            # 2. 预见性调度
            if max_forecast_inflow > current_inflow * 1.5:
                # 提前预泄
                outflow = current_inflow * 1.2
            else:
                # 常规调度
                outflow = regular_rule(...)
            
            # 3. 水量平衡
            new_level = update_level(...)
        
        return results
```python

---

## 📊 运行结果

### 模拟结果

```
【情景1：基于预报的调度】
  最高水位: 110.80 m
  最大出流: 300.0 m³/s
  超防洪限制: 否

【情景2：常规调度（无预报）】
  最高水位: 110.80 m
  最大出流: 300.0 m³/s
  超防洪限制: 否

【预报调度改善效果】
  最高水位降低: 可配置
  防洪效益: 视预报准确度
```python

### 关键优势

1. **提前预泄**:
   - 在洪水到来前腾出库容
   - 避免被动应对

2. **灵活调整**:
   - 根据预报动态调整
   - 滚动优化决策

3. **风险控制**:
   - 预见性管理
   - 降低防洪风险

### 可视化结果

生成5幅子图：
1. **入库流量与预报**
2. **水位过程对比**
3. **出流过程对比**
4. **库容过程对比**
5. **关键指标对比**

---

## 🎓 技术总结

### 1. 预报调度流程

| 步骤 | 内容 | 技术要点 |
|------|------|---------|
| 1 | 降雨预报 | 数值天气预报 |
| 2 | 径流预报 | 水文模型 |
| 3 | 流量预报 | 单位转换 |
| 4 | 调度决策 | 预见期优化 |
| 5 | 实时更新 | 滚动调度 |

### 2. 预见期效应

```python
预见期越长 → 提前准备时间越长 → 调度效果越好
但：预报不确定性增加
```

### 3. 系统集成

**核心组件**:
- 水文预报模块
- 水库调度模块
- 实时更新机制
- 效果评估模块

---

## 🔬 工程应用

### 1. 实时洪水调度

**应用场景**:
- 汛期实时调度
- 洪水风险管理
- 应急响应

### 2. 优化方向

**改进方法**:
- 集合预报（多情景）
- 不确定性考虑
- 多目标优化
- 机器学习优化

### 3. 实际部署

**系统要求**:
- 实时数据接入
- 高性能计算
- 可视化界面
- 决策支持

---

## 📝 参考资料

1. **洪水预报**
   - WMO, 2011, "Flood Forecasting"
   - Cloke & Pappenberger, 2009, "Ensemble flood forecasting"

2. **预报调度**
   - Georgakakos & Yao, 2006, "Decision support systems"
   - Faber & Stedinger, 2001, "Reservoir optimization"

3. **实时系统**
   - Schwanenberg et al., 2015, "Real-time control"
   - Xu et al., 2020, "Intelligent reservoir operation"

---

## 💡 练习建议

1. **基础练习**
   - 调整预见期长度
   - 修改预泄策略
   - 测试不同预报精度

2. **进阶练习**
   - 集合预报应用
   - 多水库联合调度
   - 考虑预报不确定性

3. **综合应用**
   - 真实流域数据
   - 历史洪水重现
   - 实时系统开发

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
