# 光伏发电系统建模与控制

**Photovoltaic System Modeling and Control**

一套完整的光伏发电系统建模、仿真与控制教材，基于Python的案例驱动学习。

---

## 📚 教材简介

本教材是**新能源系列教材**的第一本，专注于光伏发电系统的建模、仿真与控制技术。

### 核心特色

✅ **案例驱动**: 26个工程案例，从单个光伏电池到大型光伏电站  
✅ **完整流程**: 建模 → 仿真 → 控制 → 优化  
✅ **Python实现**: 完整源代码，可直接运行  
✅ **工程导向**: 贴近实际应用，提供设计指导  

### 适用对象

- 新能源科学与工程专业本科生/研究生
- 电气工程专业本科生/研究生
- 自动化专业本科生/研究生
- 光伏行业工程师和研究人员

### 先修课程

- 电路原理
- 自动控制原理
- 电力电子技术
- Python基础

---

## 📖 教材结构

### 第一部分: 光伏电池建模 (案例1-6, 6周)

- ✅ **案例1**: 光伏电池I-V特性建模 (单二极管模型)
- ⏳ 案例2: 多二极管精确模型
- ⏳ 案例3: 光伏组件建模
- ⏳ 案例4: 光伏阵列建模
- ⏳ 案例5: 环境因素影响建模
- ⏳ 案例6: 光伏老化与衰减建模

### 第二部分: MPPT控制技术 (案例7-12, 6周)

- ⏳ 案例7: 扰动观察法 (P&O)
- ⏳ 案例8: 增量电导法 (INC)
- ⏳ 案例9: 恒电压法 (CV)
- ⏳ 案例10: 模糊逻辑MPPT
- ⏳ 案例11: 神经网络MPPT
- ⏳ 案例12: 多峰MPPT算法

### 第三部分: 并网逆变器控制 (案例13-18, 6周)

- ⏳ 案例13: 单相PWM逆变器建模
- ⏳ 案例14: 三相PWM逆变器建模
- ⏳ 案例15: 电流环控制
- ⏳ 案例16: 电压环控制
- ⏳ 案例17: 并网同步技术
- ⏳ 案例18: 低电压穿越 (LVRT)

### 第四部分: 直流侧控制 (案例19-22, 4周)

- ⏳ 案例19: DC/DC变换器建模
- ⏳ 案例20: 直流母线电压控制
- ⏳ 案例21: 功率解耦控制
- ⏳ 案例22: 直流微网母线电压控制

### 第五部分: 系统级控制 (案例23-26, 4周)

- ⏳ 案例23: 有功/无功协调控制
- ⏳ 案例24: 光储联合控制
- ⏳ 案例25: 多光伏电站协调控制
- ⏳ 案例26: 虚拟同步发电机 (VSG)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行案例1

```bash
cd code/examples/case_01_pv_cell_iv_characteristics
python main.py
```

### 3. 运行实验

```bash
python experiments.py
```

### 4. 运行测试

```bash
cd ../../tests
python test_pv_cell.py
```

---

## 📊 当前进度

| 部分 | 案例数 | 完成 | 进度 |
|------|--------|------|------|
| 第一部分: 光伏电池建模 | 6 | 1 | 🟩⬜⬜⬜⬜⬜ 17% |
| 第二部分: MPPT控制 | 6 | 0 | ⬜⬜⬜⬜⬜⬜ 0% |
| 第三部分: 并网逆变器 | 6 | 0 | ⬜⬜⬜⬜⬜⬜ 0% |
| 第四部分: 直流侧控制 | 4 | 0 | ⬜⬜⬜⬜ 0% |
| 第五部分: 系统级控制 | 4 | 0 | ⬜⬜⬜⬜ 0% |
| **总计** | **26** | **1** | **🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜ 4%** |

---

## 🎓 学习成果

完成本教材后，学生能够：

### 建模能力
- ✅ 建立光伏电池/组件/阵列完整模型
- ✅ 掌握电力电子变换器建模方法
- ✅ 理解并网系统动态特性

### 控制能力
- ✅ 设计并实现MPPT算法
- ✅ 设计并网逆变器控制系统
- ✅ 掌握多层级协调控制策略

### 仿真能力
- ✅ 独立完成系统级仿真
- ✅ 分析系统动态响应
- ✅ 优化控制参数

### 工程能力
- ✅ 光伏系统方案设计
- ✅ 性能测试与评估
- ✅ 故障诊断与处理

---

## 📂 项目结构

```
photovoltaic-system-modeling-control/
├── README.md                   # 本文件
├── requirements.txt            # 依赖包
├── code/                       # 源代码
│   ├── models/                 # 核心模型
│   │   ├── pv_cell.py          # 光伏电池模型
│   │   ├── pv_module.py        # 光伏组件模型
│   │   └── pv_array.py         # 光伏阵列模型
│   ├── control/                # 控制算法
│   ├── examples/               # 案例代码
│   │   └── case_01_pv_cell_iv_characteristics/
│   │       ├── README.md       # 案例文档
│   │       ├── main.py         # 主程序
│   │       ├── experiments.py  # 实验脚本
│   │       └── outputs/        # 输出图表
│   └── utils/                  # 工具函数
├── tests/                      # 测试代码
│   └── test_pv_cell.py         # 光伏电池测试
├── docs/                       # 文档
└── data/                       # 数据文件
```

---

## 🧪 测试

运行所有测试：

```bash
cd tests
python test_pv_cell.py
```

预期输出：
```
test_initialization (__main__.TestSingleDiodeModel) ... ok
test_short_circuit_current (__main__.TestSingleDiodeModel) ... ok
test_open_circuit_voltage (__main__.TestSingleDiodeModel) ... ok
...
----------------------------------------------------------------------
Ran 20 tests in 2.345s

OK
```

---

## 📈 开发计划

### Phase 1: 光伏电池建模 (Week 1-6) 🟢 进行中
- ✅ 案例1: 光伏电池I-V特性建模 (已完成)
- ⏳ 案例2-6: 其他建模案例

### Phase 2: MPPT控制技术 (Week 7-12)
- ⏳ 案例7-12

### Phase 3: 并网逆变器控制 (Week 13-18)
- ⏳ 案例13-18

### Phase 4: 直流侧与系统级控制 (Week 19-26)
- ⏳ 案例19-26

---

## 🤝 贡献

欢迎贡献！

### 贡献方式
- 报告Bug
- 提出新功能建议
- 提交Pull Request
- 改进文档

### 开发规范
- 代码遵循PEP 8规范
- 所有函数需要docstring
- 新增代码需要单元测试
- 提交前运行测试

---

## 📞 联系我们

- **项目主页**: /workspace/books/photovoltaic-system-modeling-control
- **Issue**: 欢迎提Issue
- **Email**: chs-books@example.com

---

## 📄 许可证

MIT License

---

## 🙏 致谢

本教材参考了：
- NREL (National Renewable Energy Laboratory)
- Sandia National Laboratories
- Martin A. Green教授的开创性工作
- IEC/IEEE光伏标准

感谢开源社区的贡献！

---

**版本**: v1.0-alpha  
**最后更新**: 2025-11-04  
**状态**: 🟢 开发中  
**作者**: CHS-Books 新能源教材组
