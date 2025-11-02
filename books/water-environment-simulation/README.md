# 水环境模拟教材
## 基于案例驱动的水环境数值模拟课程

**适用对象**: 环境工程、水利工程、市政工程专业本科生及研究生  
**教学方法**: 案例驱动学习（Case-Based Learning）  
**完成度**: 开发中（3/30个案例已完成）  
**版本**: v0.1-dev（开发版本）

---

## 🚀 快速开始

### 安装依赖

```bash
cd /workspace/books/water-environment-simulation
pip install -r requirements.txt
```

### 运行第一个案例

```bash
# 案例1：污染物在静水中的扩散
python code/examples/case_01_diffusion/main.py
```

---

## 📚 已完成案例

### 第一部分：水质模拟基础

#### ✅ 案例1：污染物在静水中的扩散（4学时）
- **难度**: ⭐☆☆☆☆
- **核心理论**: Fick扩散定律
- **数值方法**: 显式/隐式有限差分法
- **代码位置**: `code/examples/case_01_diffusion/`

#### ✅ 案例2：示踪剂在渠道中的对流-扩散（6学时）
- **难度**: ⭐⭐☆☆☆
- **核心理论**: 对流-扩散方程
- **数值方法**: 迎风格式、中心差分、QUICK格式
- **代码位置**: `code/examples/case_02_advection_diffusion/`

#### ✅ 案例3：河流中的降解反应（6学时）
- **难度**: ⭐⭐☆☆☆
- **核心理论**: 一阶反应动力学、参数率定
- **数值方法**: 反应-迁移耦合求解
- **代码位置**: `code/examples/case_03_reaction/`

---

## 📊 项目结构

```
water-environment-simulation/
├── README.md                    # 本文件
├── requirements.txt             # 依赖包
├── code/
│   ├── models/                  # 核心模型
│   │   ├── diffusion.py         # 扩散模型
│   │   ├── advection_diffusion.py  # 对流-扩散模型
│   │   └── reaction.py          # 反应动力学
│   ├── solvers/                 # 数值求解器
│   │   ├── fdm_solvers.py       # 有限差分求解器
│   │   └── schemes.py           # 数值格式
│   ├── utils/                   # 工具函数
│   │   ├── numerical.py         # 数值方法工具
│   │   ├── plotting.py          # 绘图工具
│   │   └── validation.py        # 验证工具
│   └── examples/                # 案例代码
│       ├── case_01_diffusion/
│       ├── case_02_advection_diffusion/
│       └── case_03_reaction/
├── docs/                        # 文档
├── tests/                       # 测试代码
└── data/                        # 数据文件
```

---

## 🔬 核心功能

### 已实现模型
- ✅ 1D/2D Fick扩散模型
- ✅ 1D对流-扩散模型
- ✅ 反应动力学（零阶、一阶、二阶）

### 已实现求解器
- ✅ 显式有限差分（FTCS）
- ✅ 隐式有限差分（BTCS）
- ✅ Crank-Nicolson格式
- ✅ 迎风格式
- ✅ 中心差分格式
- ✅ QUICK格式

### 已实现工具
- ✅ 数值稳定性分析
- ✅ 解析解验证
- ✅ 可视化工具
- ✅ 参数敏感性分析

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_diffusion.py -v
pytest tests/test_advection_diffusion.py -v
pytest tests/test_reaction.py -v
```

---

## 📖 学习路径

### 零基础学习者
1. 学习案例1（扩散）- 理解基本概念
2. 学习案例2（对流-扩散）- 理解数值格式
3. 学习案例3（反应）- 理解耦合求解

### 有基础学习者
1. 直接运行代码，观察结果
2. 修改参数，探索影响
3. 阅读源代码，理解实现

---

## 🔧 技术栈

- **Python**: 3.8+
- **NumPy**: 数值计算
- **SciPy**: 科学计算
- **Matplotlib**: 绘图
- **pytest**: 测试框架

---

## 📅 开发进度

- [x] 项目框架搭建
- [x] 案例1：扩散模型
- [x] 案例2：对流-扩散模型
- [x] 案例3：反应动力学
- [ ] 案例4：S-P溶解氧模型
- [ ] 案例5：营养盐循环
- [ ] 案例6：自净能力评估
- [ ] 案例7-30：待开发

---

**最后更新**: 2025-11-02  
**开发状态**: Phase 1 进行中  
**测试状态**: 基础功能测试通过
