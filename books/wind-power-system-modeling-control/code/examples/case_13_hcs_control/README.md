# 案例13: 爬山搜索控制 (HCS Control)

## 简介

本案例研究爬山搜索(Hill-Climb Search, HCS)控制策略，这是一种自适应的最大功率点跟踪(MPPT)方法。HCS无需风速测量和风轮特性参数，通过不断调整转矩指令并观察功率变化，自动搜索最大功率工作点。本案例演示爬山搜索原理、扰动步长和更新频率的影响以及TSR/PSF/HCS三种MPPT算法的综合对比。HCS控制具有自适应性强、鲁棒性好的优点，特别适用于风轮特性未知或变化的场景。

## 理论背景

爬山搜索算法的核心思想是"试探-决策"：周期性地对转矩指令施加小扰动ΔT，观察功率变化ΔP。如果ΔP>0(功率增加)，说明扰动方向正确，继续沿该方向调整；如果ΔP<0(功率减少)，说明方向错误，反向扰动。数学表达为：T(k+1) = T(k) + sign(ΔP/ΔT) × ΔT。算法最终会在最大功率点附近振荡。HCS的优点包括：(1)自适应，无需系统参数；(2)鲁棒，适应风轮特性变化(如叶片污染、结冰)；(3)实现简单。缺点包括：(1)响应较慢，需要数个扰动周期才能收敛；(2)稳态振荡，损失约1-3%能量；(3)扰动参数(步长ΔT、周期)需要权衡响应速度和稳态精度。

## 代码说明

### 主要类

**HCSController**: 爬山搜索控制器类
- `__init__(delta_T, update_interval)`: 初始化控制器
  - delta_T: 扰动步长 (N·m)
  - update_interval: 更新周期 (s)

- `compute_torque(power, dt)`: 计算转矩指令
  - 输入: 当前功率P、时间步dt
  - 输出: 转矩指令T_ref
  - 算法:
    ```
    if P > P_prev:
        保持扰动方向
    else:
        反转扰动方向
    T_ref += delta_T
    ```

### 演示函数

- `demo_hcs_principle()`: HCS爬山原理
  - 模拟P-ω曲线
  - 爬山过程可视化
  - 收敛轨迹

- `demo_hcs_parameters()`: HCS参数影响
  - 扰动步长影响(大步长vs小步长)
  - 更新周期影响(快速vs慢速)
  - 三种配置对比

- `demo_mppt_comparison()`: 三种MPPT算法综合对比
  - TSR控制
  - PSF控制
  - HCS控制
  - 性能雷达图

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_13_hcs_control

# 运行案例
python main.py
```

## 参数说明

### HCS参数
- **delta_T**: 扰动步长
  - 小步长(5,000 N·m): 精度高，收敛慢
  - 中等步长(10,000 N·m): 平衡
  - 大步长(20,000 N·m): 快速，振荡大

- **update_interval**: 更新周期
  - 短周期(2 s): 响应快，易受噪声干扰
  - 中等周期(5 s): 推荐
  - 长周期(10 s): 稳定，动态性差

### 推荐配置
- delta_T = 10,000 N·m
- update_interval = 5 s
- 稳态振荡 < 2%
- 响应时间 < 30 s

## 预期结果说明

运行本案例后将生成3张图表：

1. **case13_hcs_principle.png** (两图):
   - 爬山过程:
     - P-ω曲线(抛物线)
     - HCS搜索路径(红色折线)
     - 从低转速逐步爬升至峰值
     - 在峰值附近振荡

   - 转速收敛:
     - 转速逐步接近最优值
     - 稳态振荡幅值与步长相关

2. **case13_hcs_parameters.png** (四图):
   - 转速响应对比:
     - 快速(大步长): 超调大，振荡
     - 中等: 平衡
     - 慢速(小步长): 平滑，响应慢

   - 功率响应对比:
     - 快速配置先到达额定
     - 但稳态波动大

   - 风速输入:
     - 阶跃10→12 m/s

   - 参数影响总结:
     - 文字说明三种配置的优缺点

3. **case13_mppt_comparison.png** (四图):
   - 转速对比:
     - TSR: 最平滑
     - PSF: 较平滑
     - HCS: 明显振荡

   - 功率对比:
     - 三者功率相近
     - HCS波动最大

   - Cp对比:
     - TSR平均Cp最高(0.47-0.48)
     - PSF次之(0.46-0.47)
     - HCS略低(0.45-0.47)

   - 性能雷达图(五维评价):
     - 平均Cp: TSR > PSF > HCS
     - 稳定性: TSR > PSF > HCS
     - 响应速度: TSR > PSF > HCS
     - 实现难度: HCS > PSF > TSR
     - 鲁棒性: HCS > PSF > TSR

### 控制台输出
- HCS爬山步骤详情
- 不同参数配置的性能
- 三种MPPT算法的平均Cp和标准差

## 工程应用

HCS控制的应用场景：

### 适用场景
1. **老旧机组改造**:
   - 风轮特性数据缺失
   - 无法准确标定Kopt
2. **叶片污染/结冰**:
   - Cp曲线变化
   - HCS自动适应
3. **低成本方案**:
   - 无需风速计
   - 无需风轮数据
4. **多机型混合风电场**:
   - 统一控制策略

### 参数调优指南

| 场景 | delta_T | update_interval | 说明 |
|-----|---------|-----------------|------|
| 快速响应 | 20,000 | 2-3 s | 风速变化快 |
| 平衡配置 | 10,000 | 5 s | 推荐 |
| 稳态优先 | 5,000 | 8-10 s | 风速稳定 |

### 性能优化技巧
1. **步长自适应**:
   - 收敛过程: 大步长
   - 接近峰值: 减小步长
2. **功率滤波**:
   - 低通滤波避免噪声干扰
3. **边界限制**:
   - 转矩上下限保护
4. **混合策略**:
   - 启动阶段: PSF快速接近
   - 稳态阶段: HCS精细调整

## 三种MPPT算法综合对比

### TSR控制
- **优点**: 精度最高，响应最快
- **缺点**: 依赖风速测量
- **应用**: 陆上风电，风速测量可靠

### PSF控制
- **优点**: 无需风速，实现简单
- **缺点**: 需要Kopt参数
- **应用**: 海上风电，标准化机型

### HCS控制
- **优点**: 自适应，最鲁棒
- **缺点**: 响应慢，稳态振荡
- **应用**: 老旧机组，特殊环境

## 参考文献

1. Datta, R., & Ranganathan, V. T. (2003). A method of tracking the peak power points for a variable speed wind energy conversion system. *IEEE Transactions on Energy Conversion*, 18(1), 163-168.
2. Kazmi, S. M. R., et al. (2011). A novel algorithm for fast and efficient speed-sensorless maximum power point tracking in wind energy conversion systems. *IEEE Transactions on Industrial Electronics*, 58(1), 29-36.
3. Abdullah, M. A., et al. (2012). A review of maximum power point tracking algorithms for wind energy systems. *Renewable and Sustainable Energy Reviews*, 16(5), 3220-3227.
