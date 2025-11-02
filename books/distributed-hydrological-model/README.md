# 分布式水文模型教材
## 原理、方法与Python实现

**项目定位**: CHS-Books系列第五本  
**适用对象**: 水文水资源专业本科生、研究生、工程技术人员  
**教学方法**: 案例驱动学习 + 流域实例 + Python实现  
**完成度**: 🚧 开发中 (19/25个案例，9/10个核心模块)  
**版本**: v0.18.0-alpha

---

## 📚 教材概述

本教材系统讲解**分布式水文模型**的理论、方法与工程应用，通过25个递进案例，覆盖从流域划分到实时洪水预报的完整流程。

### 为什么学习分布式水文模型？

1. **精细化模拟**：考虑空间异质性，提升模拟精度
2. **物理过程完整**：降雨-产流-汇流-演进全过程
3. **工程应用广**：洪水预报、水资源管理、气候变化评估
4. **前沿技术融合**：AI、大数据、数字孪生
5. **职业发展必备**：水文水资源领域核心技能

### 教学特色

- ✅ **案例驱动**：25个真实流域案例，从10km²到10000km²
- ✅ **Python实现**：生产级代码，可直接用于科研和工程
- ✅ **理论扎实**：系统的水文学和数值方法理论
- ✅ **复用优化**：继承CHS-Books前4本书的成熟代码
- ✅ **开源共享**：GitHub全部开源，惠及更多学习者

---

## 🎯 25个递进案例

### 第一部分：基础建模（案例1-8）⭐⭐

| 案例 | 标题 | 难度 | 状态 |
|------|------|------|------|
| 案例1 | DEM分析与河网提取 | ⭐ | ✅ |
| 案例2 | Thiessen多边形降雨插值 | ⭐ | ✅ |
| 案例3 | IDW与Kriging空间插值对比 | ⭐⭐ | ✅ |
| 案例4 | 新安江模型产流计算 | ⭐⭐ | ✅ |
| 案例5 | Green-Ampt超渗产流模型 | ⭐⭐ | ✅ |
| 案例6 | 分布式产流网格模型 | ⭐⭐⭐ | ✅ |
| 案例7 | 坡面运动波汇流 | ⭐⭐ | ✅ |
| 案例8 | 单元线法河道汇流 | ⭐⭐ | ✅ |

### 第二部分：高级模拟（案例9-16）⭐⭐⭐

| 案例 | 标题 | 难度 | 状态 |
|------|------|------|------|
| 案例9 | 参数敏感性分析 | ⭐⭐ | ✅ |
| 案例10 | Muskingum-Cunge方法 | ⭐⭐ | ✅ |
| 案例11 | SCE-UA参数率定算法 | ⭐⭐⭐ | ✅ |
| 案例12 | GLUE不确定性分析 | ⭐⭐⭐ | ✅ |
| 案例13 | EnKF数据同化 | ⭐⭐⭐ | ✅ |
| 案例14 | 完整流域分布式模型 | ⭐⭐⭐⭐ | ✅ |
| 案例15 | 水文-水动力耦合 | ⭐⭐⭐⭐ | ✅ |
| 案例16 | 人类活动影响评估 | ⭐⭐⭐⭐ | ✅ |

**第二部分完成！** 🎉

### 第三部分：耦合与应用（案例17-25）⭐⭐⭐⭐

| 案例 | 名称 | 难度 | 状态 |
|------|------|------|------|
| 案例17 | 水库优化调度 | ⭐⭐⭐⭐ | ✅ |
| 案例18 | 实时洪水预报调度 | ⭐⭐⭐⭐⭐ | ✅ |
| 案例19 | 气候变化影响评估 | ⭐⭐⭐⭐ | ✅ |

（案例20-25详见完整文档）

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆仓库
cd /workspace/books/distributed-hydrological-model

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import numpy, scipy, matplotlib; print('安装成功！')"
```

### 2. 运行第一个案例

```bash
# 案例1：DEM分析与河网提取
cd code/examples/case_01_dem_watershed
python main.py

# 查看结果
ls outputs/
```

### 3. 交互式学习

```bash
# 启动Jupyter Notebook
jupyter notebook code/examples/case_01_dem_watershed/notebook.ipynb
```

---

## 📖 核心内容

### 知识体系（13章，88学时）

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| 第1章 | 分布式水文模型概论 | 发展历史、模型分类、数据基础 |
| 第2章 | 流域空间离散化 | DEM处理、流域划分、河网提取 |
| 第3章 | 降雨空间插值 | Thiessen、IDW、Kriging方法 |
| 第4章 | 产流模拟 | 蓄满产流、超渗产流、分布式产流 |
| 第5章 | 坡面汇流 | 运动波、扩散波、动力波方法 |
| 第6章 | 河道汇流 | Muskingum、圣维南方程求解 |
| 第7章 | 蒸散发模拟 | Penman-Monteith、潜在蒸散发 |
| 第8章 | 参数率定与不确定性 | SCE-UA、GLUE、贝叶斯方法 |
| 第9章 | 在线辨识与同化 | 卡尔曼滤波、粒子滤波、EnKF |
| 第10章 | 水文水动力耦合 | SWMM、自建耦合框架 |
| 第11章 | 人类活动影响 | 水库、灌溉、城市化、气候变化 |
| 第12章 | 流域智能管理 | 洪水预报、水资源调度、决策支持 |
| 第13章 | 综合应用案例 | 大型流域建模、实时预报系统 |

### 核心模块

```python
# 流域分析
from pydromodel.basin import watershed_delineation, river_network_extraction

# 空间插值
from pydromodel.interpolation import thiessen, idw, kriging

# 产流模拟
from pydromodel.runoff_generation import XinAnJiangModel, GreenAmpt

# 河道汇流
from pydromodel.channel_routing import Muskingum, SaintVenant1D

# 参数率定
from pydromodel.calibration import SCE_UA, GLUE

# 数据同化
from pydromodel.assimilation import KalmanFilter, EnKF
```

---

## 🛠️ 技术栈

### 空间分析
- GDAL/OGR、Rasterio、Geopandas
- PySheds、WhiteboxTools

### 数值计算
- NumPy、SciPy、Numba

### 优化与辨识
- SPOTPY、PyMC3、Filterpy

### 可视化
- Matplotlib、Plotly、Folium

---

## 📊 项目进度

| 阶段 | 进度 | 状态 |
|------|------|------|
| 项目框架 | 100% | ✅ |
| 核心模块 | 30% | 🔄 |
| 案例开发 | 16% (4/25) | 🔄 |
| 测试代码 | 10% | 🔄 |
| 文档编写 | 20% | 🔄 |

**当前版本**: v0.1.0-alpha  
**预计完成**: 2026-02

---

## 🎓 学习路径

### 零基础学习者（12周）
1. 学习Python基础和NumPy（2周）
2. 按顺序学习案例1-8（6周）
3. 选择案例9-16深入学习（3周）
4. 完成一个综合项目（1周）

### 有基础学习者（6周）
1. 快速浏览案例1-4（1周）
2. 重点学习案例5-16（4周）
3. 完成综合应用案例（1周）

### 科研人员（按需）
- 直接查阅相关模块和案例
- 使用代码库进行科研开发
- 参与开源贡献

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 如何贡献
1. 报告错误或建议
2. 提供流域数据
3. 改进算法代码
4. 完善文档说明
5. 添加新案例

---

## 📄 许可证

本项目采用 MIT License

---

## 📞 联系方式

- GitHub Issues: [提交问题]
- 邮箱: chs-books@example.com
- 讨论区: [GitHub Discussions]

---

## 🌟 致谢

- CHS-Books前4本书的基础支持
- Python开源社区（NumPy、SciPy等）
- 全球水文学研究者的理论贡献

---

**最后更新**: 2025-11-02  
**开发团队**: CHS-Books项目组  
**项目状态**: 🚧 Alpha版本开发中

---

## 📚 相关教材

- [《水系统控制论》](../water-system-control/) - 控制理论基础
- [《明渠水力学》](../open-channel-hydraulics/) - 水力计算基础
- [《渠道与管道控制》](../canal-pipeline-control/) - 控制工程实践
- [《智能水网工程设计》](../intelligent-water-network-design/) - 工程设计方法

**让我们一起开启分布式水文建模的智能时代！** 💧🌊🏔️
