# 案例30:人工湿地水力停留时间优化设计

## 案例简介

本案例研究人工湿地污水处理系统的水力设计优化。水力停留时间(HRT)是影响人工湿地处理效果的关键参数,直接决定污染物去除效率和占地面积。通过建立HRT优化模型,综合考虑处理目标、水力负荷、长宽比等因素,设计高效经济的人工湿地系统,为生态污水处理工程提供技术支撑。

## 理论背景

人工湿地是利用土壤-植物-微生物系统净化污水的生态技术,具有投资省、运行费用低、管理简单等优点。核心设计参数包括:

**1. 水力停留时间(HRT)**
HRT = V / Q = (L × W × h) / Q
其中V为有效容积,Q为进水流量

**2. 污染物去除**
C_out = C_in × exp(-k × HRT)
其中k为去除系数,COD约0.5-1.0/d,TN约0.2-0.4/d,TP约0.3-0.6/d

**3. 长宽比优化**
长宽比影响水流态,推流式湿地长宽比宜大于2:1,最优值通常为3-5:1,可提高有效容积比(减少短流)

**4. 水力负荷**
q = Q / A (m³/m²·d)
典型值0.05-0.15 m³/m²·d

**5. 植物配置**
不同水深区配置不同植物:挺水植物(0-0.5m)、浮叶植物(0.5-1.5m)、沉水植物(1.5-3m)

## 代码说明

### 主要类和函数

1. **ConstructedWetland类** - 人工湿地设计
   - `pollutant_removal()`: 计算污染物去除率
   - `aspect_ratio_optimization()`: 优化长宽比
   - `effective_volume_ratio()`: 计算有效容积比

2. **design_wetland_system()**: 系统设计函数

### 核心算法

```python
# 所需HRT
HRT = -ln(C_out / C_in) / k

# 湿地尺寸
Volume = HRT * Q
Area = Volume / depth
Length = sqrt(Area * ratio)
Width = Area / Length

# 有效容积比
e = 1 - 1 / (1 + 0.3 * ratio)
```

## 运行方法

```bash
cd /home/user/CHS-Books/books/ecohydraulics/code/examples/case_30_constructed_wetland
python main.py
```

## 参数说明

### 设计条件
- `inlet_flow`: 进水流量,如1000m³/d
- `inlet_concentration`: 进水浓度,COD如150mg/L
- `target_removal_rate`: 目标去除率,如80%

### 湿地参数
- `length`: 长度,优化计算得出
- `width`: 宽度,优化计算得出
- `depth`: 水深,典型值0.6-1.0m
- `porosity`: 介质孔隙率,约0.4

### 去除系数(20°C)
- COD: 0.8/d
- BOD: 1.0/d
- TN: 0.3/d
- TP: 0.5/d
- NH3-N: 0.4/d

## 预期结果说明

1. **推荐设计方案**(目标去除率80%)
   - 长度: 约45m
   - 宽度: 约15m
   - 深度: 0.6m
   - 总面积: 675m²
   - 有效容积: 270m³
   - HRT: 6.5天
   - 水力负荷: 1.48 m³/m²·d

2. **处理效果**(HRT=6.5天)
   - COD: 150→30mg/L (去除80%)
   - BOD: 80→8mg/L (去除90%)
   - TN: 30→12mg/L (去除60%)
   - TP: 3→1.2mg/L (去除60%)
   - NH3-N: 15→6mg/L (去除60%)

3. **长宽比优化**
   - 推荐长宽比: 3:1
   - 有效容积比: 0.74
   - 避免短流和死区

4. **成本估算**
   - 土建工程: 约10万元
   - 设备安装: 约6万元
   - 植物种植: 约4万元
   - 年运行维护: 1.8万元

5. **可视化图表**
   - HRT-去除率关系曲线(多污染物)
   - 长宽比-有效容积比柱状图
   - 示踪剂响应曲线对比
   - 多污染物去除效果柱状图
   - 湿地平面布置图
   - 投资与运行成本估算

## 生态意义与环境影响

### 生态意义

1. **生态净化**:利用自然净化能力,减少能源消耗和化学药剂使用
2. **生境营造**:为水鸟、两栖动物、水生昆虫提供栖息地
3. **景观价值**:植物景观改善人居环境,提供休闲空间
4. **环境教育**:展示生态技术,提高公众环保意识

### 应用场景

1. **农村生活污水**
   - 分散式小规模处理(10-1000m³/d)
   - 典型案例:江苏太湖流域农村污水治理

2. **城镇污水厂尾水提标**
   - 深度去除氮磷
   - 典型案例:北京奥林匹克森林公园人工湿地

3. **工业废水预处理**
   - 食品加工、纺织印染等行业
   - 降低后续处理负荷

4. **雨水径流净化**
   - 初期雨水COD、SS去除
   - 海绵城市LID设施

### 运行管理

1. **植物管理**
   - 春季补种,秋季收割
   - 收割植物移除营养盐

2. **水力维护**
   - 定期清理堵塞
   - 监测水位防止短流

3. **冬季运行**
   - 北方地区冬季效率下降
   - 可采用表面覆盖、增加HRT等措施

## 参考文献

1. Kadlec RH, Wallace SD. Treatment wetlands[M]. 2nd ed. Boca Raton: CRC Press, 2009.

2. Vymazal J. Horizontal sub-surface flow and hybrid constructed wetlands systems for wastewater treatment[J]. Ecological Engineering, 2005, 25(5): 478-490.

3. 吴晓磊. 人工湿地污水处理-理论与技术[M]. 北京:化学工业出版社, 2007.

4. 李旭东, 李怀正, 诸惠昌. 人工湿地水力学特性研究[J]. 环境科学, 2006, 27(1): 104-108.

5. García J, Rousseau DP, Morató J, et al. Contaminant removal processes in subsurface-flow constructed wetlands: a review[J]. Critical Reviews in Environmental Science and Technology, 2010, 40(7): 561-661.
