# 案例3: 叶片气动力计算

## 简介

本案例演示风力机叶片气动力学的核心理论和计算方法，包括翼型气动特性分析、叶素动量理论(BEM)求解、诱导因子计算以及风轮性能曲线(Cp-λ)的绘制。通过本案例，您将深入理解风力机气动设计的基础原理，掌握从翼型选择到风轮性能优化的完整流程。这是风力机设计与分析的核心内容，为后续的性能优化和控制策略提供理论基础。

## 理论背景

叶片气动力学是风力机设计的核心。翼型的升力系数(Cl)和阻力系数(Cd)决定了叶片截面的气动性能。叶素动量理论(Blade Element Momentum Theory, BEM)是最广泛使用的风轮气动分析方法，它将叶片沿径向划分为多个叶素，在每个叶素上结合动量理论和叶素理论进行迭代求解。通过计算轴向诱导因子(a)和切向诱导因子(a')，可以得到叶片上的力分布，进而求得风轮的总转矩、推力和功率系数Cp。功率系数Cp与叶尖速比λ的关系曲线是评价风轮性能的重要指标，Betz极限(Cp_max=16/27≈0.593)是理论上风能转换效率的上限。实际风轮由于叶尖损失、阻力等因素，Cp通常在0.45-0.50之间。

## 代码说明

### 主要类和函数

1. **AirfoilData**: 翼型气动数据类
   - `create_flat_plate()`: 创建平板翼型数据
   - `create_naca0012()`: 创建NACA0012翼型数据
   - `get_status()`: 获取翼型特性参数

2. **BEMSolver**: 叶素动量理论求解器
   - `solve_rotor()`: 求解风轮整体性能
   - 计算功率系数Cp、推力系数Ct
   - 输出叶素级的详细结果

3. **SimpleRotor**: 简化风轮模型
   - `Cp_curve()`: 功率系数曲线函数

4. **设计函数**:
   - `design_blade_chord()`: 叶片弦长分布设计
   - `design_blade_twist()`: 叶片扭角分布设计

### 演示函数

- `demo_airfoil_characteristics()`: 演示翼型Cl-α、Cd-α曲线
- `demo_blade_design()`: 演示叶片弦长和扭角分布
- `demo_bem_solver()`: 演示BEM理论求解过程
- `demo_cp_lambda_curve()`: 演示Cp-λ性能曲线

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_03_blade_aerodynamics

# 运行案例
python main.py
```

## 参数说明

### 风轮参数
- **R**: 风轮半径 (40 m)
- **r_hub**: 轮毂半径 (1.5 m)
- **B**: 叶片数量 (3)
- **lambda_opt**: 设计叶尖速比 (8.0)

### 翼型参数
- **alpha**: 攻角范围 (-10° ~ 20°)
- **Cl**: 升力系数
- **Cd**: 阻力系数

### BEM求解参数
- **n_elements**: 叶素数量 (15-20)
- **v_wind**: 来流风速 (m/s)
- **omega**: 风轮转速 (rad/s)

## 预期结果说明

运行本案例后将生成4张图表：

1. **case03_airfoil_characteristics.png**:
   - 平板翼型和NACA0012的Cl-α、Cd-α曲线对比
   - 展示不同翼型的气动特性差异

2. **case03_blade_design.png**:
   - 叶片弦长沿径向的分布
   - 叶片扭角沿径向的分布
   - 典型的扭角在叶根处较大(~12°)，叶尖处较小(~0°)

3. **case03_bem_solution.png**:
   - 轴向诱导因子a的径向分布(应接近但不超过1/3)
   - 切向诱导因子a'的分布
   - 攻角α、升力系数Cl、切向力dFt的分布
   - Prandtl叶尖损失修正因子F的分布

4. **case03_cp_lambda_curve.png**:
   - BEM理论计算的Cp-λ曲线
   - 简化模型对比
   - 最大功率系数Cp_max约为0.48
   - 最优叶尖速比λ_opt约为8.0
   - Betz极限参考线(0.593)

### 控制台输出
- 翼型特性参数(最大Cl、最小Cd等)
- 叶片几何参数
- BEM求解收敛信息
- 风轮性能指标(Cp, Ct, 功率, 转矩, 推力)
- 最优工作点参数

## 参考文献

1. Hansen, M. O. L. (2015). *Aerodynamics of Wind Turbines*. Routledge.
2. Burton, T., et al. (2011). *Wind Energy Handbook*. John Wiley & Sons.
3. Manwell, J. F., McGowan, J. G., & Rogers, A. L. (2010). *Wind Energy Explained: Theory, Design and Application*. John Wiley & Sons.
