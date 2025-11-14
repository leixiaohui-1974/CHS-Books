# 案例4: 风轮功率特性

## 简介

本案例深入探讨风力机风轮的功率特性曲线，包括Cp-λ性能曲线优化、最优叶尖速比确定、风速-功率特性曲线绘制以及年发电量估算。通过本案例，您将学习如何评估风力机在不同风速条件下的性能表现，掌握功率曲线的绘制方法，并能够基于风资源分布预测年发电量。这些内容对于风力机选型、性能评估和经济性分析至关重要。

## 理论背景

风轮功率特性是风力机最重要的性能指标。功率系数Cp定义为风轮捕获的功率与来流风能的比值，它是叶尖速比λ的函数。对于给定的风轮设计，存在一个最优叶尖速比λ_opt使得Cp达到最大值Cp_max。风力机的功率曲线通常分为三个区域：切入风速以下(停机)、额定风速以下(变速MPPT)和额定风速以上(变桨限功率)。年发电量(AEP)的计算需要结合风速概率分布(如Weibull分布)和功率曲线进行积分。容量因子(Capacity Factor)定义为年发电量与理论最大发电量的比值，是衡量风电场经济性的关键指标，通常在25%-45%之间。

## 代码说明

### 主要类和函数

1. **BEMSolver**: 叶素动量理论求解器
   - `solve_rotor()`: 计算给定工况下的风轮性能
   - 输出Cp、Ct、功率、转矩等参数

2. **WeibullDistribution**: Weibull风速分布模型
   - `pdf()`: 概率密度函数
   - `mean_speed`: 平均风速

3. **辅助函数**:
   - `create_baseline_rotor()`: 创建基准风轮模型
   - `design_blade_twist()`: 叶片扭角设计
   - `design_blade_chord()`: 叶片弦长设计

### 演示函数

- `demo_cp_lambda_optimization()`: Cp-λ曲线优化与最优点识别
- `demo_power_curve()`: 风速-功率特性曲线绘制
- `demo_annual_energy()`: 年发电量估算分析

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_04_rotor_performance

# 运行案例
python main.py
```

## 参数说明

### 风轮参数
- **R**: 风轮半径 (40 m)
- **r_hub**: 轮毂半径 (1.5 m)
- **B**: 叶片数量 (3)
- **lambda_opt**: 最优叶尖速比 (8.0)
- **Cp_max**: 最大功率系数 (约0.48)

### 功率曲线参数
- **v_rated**: 额定风速 (12 m/s)
- **P_rated**: 额定功率 (2000 kW)
- **v_cut_in**: 切入风速 (3 m/s)
- **v_cut_out**: 切出风速 (25 m/s)

### 风资源参数 (Weibull分布)
- **k**: 形状参数 (2.0)
- **c**: 尺度参数 (8.0 m/s)

## 预期结果说明

运行本案例后将生成3张图表：

1. **case04_cp_lambda_curve.png**:
   - Cp-λ曲线: 展示功率系数随叶尖速比的变化
   - 最优工作点标注(λ_opt≈8.0, Cp_max≈0.48)
   - Betz极限参考线(0.593)
   - 功率-λ曲线: 展示功率随叶尖速比的变化关系

2. **case04_power_curve.png**:
   - 风力机功率曲线: 典型的S型曲线
     - 3-12 m/s: 变速MPPT区，功率∝v³
     - 12-25 m/s: 额定功率区，P=P_rated
   - 转速曲线: 展示转速随风速的变化
     - 额定风速以下: 转速随风速线性增加
     - 额定风速以上: 转速保持额定值

3. **case04_annual_energy.png**:
   - 风速分布直方图: 基于Weibull分布的年小时数统计
   - 发电量贡献分布: 不同风速段对年发电量的贡献
   - 典型结果: AEP约5000-6000 MWh, 容量因子30-35%

### 控制台输出
- 最优工作点参数(λ_opt, Cp_max, P_max)
- Betz效率(Cp_max/0.593)
- 不同风速下的功率和转速
- 年发电量和容量因子
- 等效满发小时数

## 工程应用

本案例的知识可用于：
- 风力机选型和匹配
- 风电场发电量预测
- 经济性分析(IRR, NPV计算)
- 功率曲线质保验收
- 性能基准测试

## 参考文献

1. IEC 61400-12-1: Wind Turbines - Part 12-1: Power Performance Measurements
2. Manwell, J. F., McGowan, J. G., & Rogers, A. L. (2010). *Wind Energy Explained*
3. Burton, T., et al. (2011). *Wind Energy Handbook*
