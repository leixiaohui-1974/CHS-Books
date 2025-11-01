# 《水力学考研核心100题》快速开始指南

## 🎯 项目简介

本项目是一套完整的水力学考研复习资料，包含：
- **100道核心题目**：涵盖静水压强、水动力学、管道流动、明渠流动、水工建筑物、非恒定流
- **39个Python代码文件**：每个知识点都有完整的可执行代码
- **78张可视化图片**：直观展示计算过程和结果
- **350,000+字详实内容**：理论+例题+拓展

---

## 📁 目录结构

```
hydraulics-core-100/
├── chapters/              # 教材内容（6章100题）
│   ├── 第一章_静水压强.md
│   ├── 第二章_水动力学基础.md
│   ├── 第三章_管道流动.md
│   ├── 第四章_明渠流动.md
│   ├── 第五章_水工建筑物.md
│   └── 第六章_非恒定流基础.md
│
├── code/examples/         # Python示例代码（39个文件）
│   ├── ch01_hydrostatics/          # 第一章（5个文件）
│   ├── ch02_hydrodynamics/         # 第二章（6个文件）
│   ├── ch03_pipe_flow/             # 第三章（6个文件）
│   ├── ch04_open_channel/          # 第四章（11个文件）
│   ├── ch05_hydraulic_structures/  # 第五章（7个文件）
│   └── ch06_unsteady_flow/         # 第六章（4个文件）
│
├── README.md              # 项目说明
├── QUICK_START.md         # 本文件
└── PROJECT_100_COMPLETE.md # 完成报告
```

---

## 🚀 快速开始

### 1. 环境准备

**Python环境**：
```bash
# 确认Python版本（需要3.6+）
python3 --version

# 安装依赖包
pip3 install numpy matplotlib scipy
```

### 2. 运行示例

**运行单个代码文件**：
```bash
# 进入代码目录
cd code/examples

# 运行任意Python文件
python3 ch01_hydrostatics/pressure_center_calculation.py
python3 ch04_open_channel/uniform_flow_rectangular.py
python3 ch05_hydraulic_structures/weir_sharp_crested.py
```

**批量运行**：
```bash
# 运行某一章的所有代码
cd code/examples/ch04_open_channel
for file in *.py; do python3 "$file"; done
```

### 3. 查看结果

代码运行后会：
- 在终端输出计算结果
- 在当前目录生成PNG图片文件

**查看生成的图片**：
```bash
ls -lh *.png
```

---

## 📖 学习路径

### 路径1：按章节学习（推荐）
1. 阅读章节Markdown文件（`chapters/第X章_XXX.md`）
2. 理解核心公式和概念
3. 运行对应的Python代码
4. 查看可视化图片
5. 完成章节习题

### 路径2：按知识点学习
- **静水压强**：`ch01_hydrostatics/`（5个文件）
- **伯努利方程**：`ch02_hydrodynamics/bernoulli_*.py`
- **管道计算**：`ch03_pipe_flow/`（6个文件）
- **明渠均匀流**：`ch04_open_channel/uniform_flow_*.py`
- **明渠临界水深**：`ch04_open_channel/critical_depth_*.py`
- **水面曲线**：`ch04_open_channel/gvf_profile_*.py`
- **水工建筑物**：`ch05_hydraulic_structures/`（7个文件）

### 路径3：考前冲刺
1. 查阅各章的"核心公式速查"
2. 运行高频考点代码（标注⭐⭐⭐）
3. 重点复习综合题

---

## 💡 代码示例

### 示例1：矩形明渠均匀流计算
```python
# 文件：ch04_open_channel/uniform_flow_rectangular.py
python3 uniform_flow_rectangular.py

# 输出：
# - 正常水深计算结果
# - Q-h关系曲线
# - 流速分布图
# - 参数对比表
```

### 示例2：薄壁堰流量计算
```python
# 文件：ch05_hydraulic_structures/weir_sharp_crested.py
python3 weir_sharp_crested.py

# 输出：
# - 矩形堰、三角堰流量
# - Q-H关系曲线
# - 流量系数敏感性分析
# - 堰型选择指南
```

### 示例3：水锤分析
```python
# 文件：ch06_unsteady_flow/water_hammer_analysis.py
python3 water_hammer_analysis.py

# 输出：
# - 水锤波速
# - 压力升高值
# - 波传播过程
# - 防护措施建议
```

---

## 🎓 各章节重点

| 章节 | 核心内容 | 代码文件数 | 考试权重 |
|------|---------|-----------|---------|
| 第一章 | 静水压强、压力中心 | 5 | ⭐⭐ |
| 第二章 | 伯努利、连续性、动量方程 | 6 | ⭐⭐⭐ |
| 第三章 | 管道损失、管网计算 | 6 | ⭐⭐⭐ |
| 第四章 | 明渠均匀流、临界水深、水面曲线 | 11 | ⭐⭐⭐ |
| 第五章 | 堰流、闸孔、消能工 | 7 | ⭐⭐ |
| 第六章 | Saint-Venant、水锤 | 4 | ⭐ |

---

## 🔧 故障排除

### 问题1：中文显示为方块
**原因**：matplotlib缺少中文字体  
**解决**：代码已内置字体配置，应能正常显示

### 问题2：模块未找到
```bash
# 报错：ModuleNotFoundError: No module named 'numpy'
# 解决：
pip3 install numpy matplotlib scipy
```

### 问题3：图片不显示
**原因**：使用Agg后端，图片保存到文件  
**解决**：运行后查看当前目录的PNG文件

---

## 📞 技术支持

- **Bug报告**：请在GitHub提Issue
- **使用问题**：查看各章节README.md
- **学习交流**：欢迎提交PR改进代码

---

## 🎯 学习建议

### 时间安排（4周冲刺）
- **Week 1**：第一章+第二章（基础巩固）
- **Week 2**：第三章+第四章上半（管道+均匀流）
- **Week 3**：第四章下半+第五章（GVF+水工）
- **Week 4**：第六章+总复习（非恒定流+串讲）

### 每天学习流程
1. 阅读理论（30分钟）
2. 运行代码（30分钟）
3. 手工推导（30分钟）
4. 做习题（30分钟）

### 考前一周
- 每天复习一章的"核心公式速查"
- 重做错题集
- 模拟考试（历年真题）

---

## 🏆 项目特色

✅ **系统完整**：100题覆盖全部考点  
✅ **代码可执行**：39个文件全部测试通过  
✅ **可视化精美**：78张高质量图片  
✅ **注释详细**：中英文双语，易于理解  
✅ **工程实用**：结合实际案例  

---

## 📚 相关资源

- **教材推荐**：
  - 《水力学》（吴持恭主编）
  - 《水力学》（闻德荪主编）
  - 《水力学与桥涵水文》（交通版）

- **在线资源**：
  - 中国大学MOOC：水力学课程
  - B站：相关视频讲解

---

**祝您考研成功！💪**

---

*《水力学考研核心100题》*  
*完成日期：2025-10-31*  
*版本：v1.0*
