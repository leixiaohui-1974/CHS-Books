# 案例23：流域水文-水质耦合模拟

## 案例简介

本案例演示流域尺度的水文-水质耦合模拟方法，通过建立降雨-径流-污染负荷的关联模型，分析不同降雨强度下的流域水文响应和非点源污染物输出特征。案例采用流域水文模型（WatershedModel）模拟子流域产汇流过程，并基于事件平均浓度法（EMC）计算污染物负荷，同时评估土地利用变化对水文水质的影响，为流域综合管理和水环境保护提供科学依据。

## 理论背景

流域水文-水质耦合模拟是流域水环境管理的重要工具。降雨径流过程是流域水循环的核心环节，而非点源污染物随径流输出是流域水质恶化的主要原因。事件平均浓度法（Event Mean Concentration, EMC）假设在一次降雨事件中，污染物浓度相对稳定，污染负荷等于径流量与EMC的乘积。土地利用类型直接影响流域的产流系数和污染物输出特性：城市化地区不透水面增加导致径流系数升高，农业区化肥农药使用造成氮磷污染加重。通过水文-水质耦合模拟，可以定量评估降雨强度、土地利用、管理措施对流域水文水质的综合影响，为流域规划、污染控制和生态修复提供决策支持。

## 代码说明

### 主要类和函数

1. **WatershedModel类**
   - `__init__(area, n_subbasins)`: 初始化流域模型，设置流域面积和子流域数量
   - `simulate_runoff(rainfall)`: 模拟降雨-径流过程，计算产流量
   - `calculate_pollutant_load(runoff, EMC)`: 基于EMC法计算污染物负荷

2. **assess_land_use_impact函数**
   - 评估土地利用变化（城市化率、农业占比）对水文水质的影响
   - 参数：urbanization_rate（城市化率）、agriculture_ratio（农业占比）

3. **主程序流程**
   - 创建流域模型（面积500km²，5个子流域）
   - 模拟4种降雨情景（20、50、100、150mm）
   - 计算对应的径流和污染负荷
   - 评估土地利用影响
   - 生成可视化结果

### 核心算法

```python
# 降雨-径流关系
runoff = model.simulate_runoff(rainfall)

# 污染负荷计算
pollutant_load = runoff * EMC * area
```

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/water-environment-simulation/code/examples/case_23_watershed

# 运行模拟
python main.py
```

## 参数说明

| 参数 | 说明 | 默认值 | 单位 |
|------|------|--------|------|
| area | 流域面积 | 500 | km² |
| n_subbasins | 子流域数量 | 5 | - |
| rainfalls | 降雨情景 | [20, 50, 100, 150] | mm |
| EMC | 事件平均浓度 | 50 | mg/L |
| urbanization_rate | 城市化率 | 0.4 | - |
| agriculture_ratio | 农业占比 | 0.3 | - |

## 预期结果说明

程序运行后将生成：

1. **控制台输出**
   - 案例运行状态信息
   - 各情景的计算结果

2. **图表文件**（watershed.png）
   - 左图：降雨-径流关系曲线
   - 右图：降雨-污染负荷关系曲线

3. **结果特征**
   - 径流量随降雨强度非线性增加
   - 污染负荷与径流量呈正相关
   - 大降雨事件导致污染物集中输出

## 应用场景

1. **流域水文分析**
   - 降雨-径流关系研究
   - 洪水风险评估
   - 水资源评价

2. **非点源污染控制**
   - 污染负荷估算
   - 关键源区识别
   - 最佳管理措施（BMPs）优化

3. **土地利用规划**
   - 城市化影响评估
   - 农业面源污染控制
   - 流域综合管理

4. **水环境管理**
   - 污染物总量控制
   - 水质目标达标分析
   - 生态补偿机制设计

## 参考文献

1. Arnold, J. G., et al. (1998). Large area hydrologic modeling and assessment part I: Model development. *Journal of the American Water Resources Association*, 34(1), 73-89.

2. Novotny, V., & Olem, H. (1994). *Water quality: Prevention, identification and management of diffuse pollution*. Van Nostrand Reinhold.

3. 芮孝芳. (2004). 《水文学原理》. 北京: 中国水利水电出版社.

4. 贺缠生, 等. (2008). 流域非点源污染模型研究进展. *生态学报*, 28(5), 2362-2370.
