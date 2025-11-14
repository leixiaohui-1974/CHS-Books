# 案例16：河床砾石补充与稳定性分析

## 案例简介

本案例研究河床砾石补充工程的设计与稳定性评估。砾石补充是河流生态修复的重要措施,用于恢复受损的产卵场底质、改善鱼类栖息地条件。通过合理的粒径配比设计和稳定性分析,确保补充的砾石能在不同水流条件下保持稳定,满足生态功能需求。该案例对于河流栖息地修复工程具有重要实践价值。

## 理论背景

河床砾石在河流生态系统中具有多重功能:为底栖生物提供栖息空间、为鱼类提供产卵基质、调节水流结构增加栖息地多样性。水电开发、采砂等人类活动导致许多河流砾石流失,需要通过人工补充恢复底质条件。

砾石稳定性分析基于希尔兹(Shields)准则,通过计算希尔兹数判断颗粒的起动条件:

**希尔兹数**: θ = τ / [(ρ_s - ρ) g d]

其中τ为床面剪切应力,ρ_s为砾石密度,ρ为水密度,d为粒径。临界希尔兹数θ_c约为0.045-0.05。安全系数定义为θ_c/θ,需大于1.5以确保稳定。

粒径配比设计需考虑:d10、d30、d50、d60、d90等特征粒径,通常采用对数正态分布,确保级配良好。

## 代码说明

### 主要类和函数

1. **GravelSupplementDesign类** - 砾石补充设计
   - `gravel_size_distribution()`: 设计砾石粒径分布
   - `stability_assessment()`: 评估砾石稳定性
   - `calculate_shields_number()`: 计算希尔兹数

### 核心算法

```python
# 粒径分布(对数正态)
d10 = target_d50 * 0.4
d30 = target_d50 * 0.7
d60 = target_d50 * 1.3
d90 = target_d50 * 2.0

# 希尔兹稳定性分析
τ = ρ * g * h * S  # 床面剪切应力
θ = τ / [(ρ_s - ρ) * g * d50]
safety_factor = θ_c / θ
```

## 运行方法

```bash
cd /home/user/CHS-Books/books/ecohydraulics/code/examples/case_16_gravel_supplement
python main.py
```

## 参数说明

### 设计参数
- `target_d50`: 目标中值粒径,典型值20-50mm
- `water_depth`: 设计水深,影响剪切应力
- `slope`: 河床坡度,天然河流0.001-0.005
- `velocity`: 设计流速,影响稳定性判断

### 物理参数
- 砾石密度: 2650 kg/m³(一般岩石)
- 水密度: 1000 kg/m³
- 重力加速度: 9.81 m/s²

## 预期结果说明

1. **粒径配比**
   - d10: 约10mm
   - d50: 25mm(设计值)
   - d90: 约50mm

2. **稳定性评估**(水深2m,坡度0.001)
   - 流速0.5m/s: 安全稳定,安全系数>2.0
   - 流速0.8m/s: 稳定,安全系数1.5-2.0
   - 流速1.0m/s: 基本稳定,安全系数~1.2
   - 流速1.5m/s: 可能起动,安全系数<1.0

3. **可视化图表**
   - 粒径配比柱状图
   - 安全系数随流速变化曲线

## 生态意义与环境影响

### 生态意义

1. **栖息地修复**:恢复鱼类产卵场底质条件,提高繁殖成功率
2. **生物多样性**:砾石间隙为底栖无脊椎动物提供庇护所
3. **水力多样性**:增加河床粗糙度,形成多样的流速分布

### 环境影响与应用

1. **鲑鱼产卵场修复**:北美地区广泛应用于鲑鱼栖息地恢复
2. **长江鱼类保护**:用于四大家鱼、中华鲟等产卵场修复
3. **工程考虑**
   - 砾石来源:尽量就地取材,避免长距离运输
   - 补充时机:选择枯水期施工,减少对水生生物干扰
   - 长期监测:跟踪砾石冲刷、淤积情况,必要时进行补充

### 实际案例

- 长江上游珍稀鱼类产卵场砾石床修复工程
- 美国哥伦比亚河鲑鱼栖息地修复项目
- 欧洲莱茵河砾石补充与河道再自然化工程

## 参考文献

1. Kondolf GM, Wolman MG. The sizes of salmonid spawning gravels[J]. Water Resources Research, 1993, 29(7): 2275-2285.

2. Buffington JM, Montgomery DR. A systematic analysis of eight decades of incipient motion studies, with special reference to gravel-bedded rivers[J]. Water Resources Research, 1997, 33(8): 1993-2029.

3. 谢小军, 王珂, 石小涛等. 长江上游珍稀鱼类产卵场砾石床修复技术[J]. 长江流域资源与环境, 2015, 24(10): 1725-1730.

4. 李锦, 陈永柏, 张辉等. 三峡水库运行后长江四大家鱼产卵场底质变化[J]. 长江科学院院报, 2014, 31(6): 7-11.

5. Bunte K, Abt SR. Sampling surface and subsurface particle-size distributions in wadable gravel-and cobble-bed streams for analyses in sediment transport, hydraulics, and streambed monitoring[M]. US Department of Agriculture, Forest Service, Rocky Mountain Research Station, 2001.
