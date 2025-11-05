# 快速开始指南

本指南帮助你快速上手《光伏发电系统建模与控制》教材。

---

## 1️⃣ 环境准备

### 安装Python

```bash
# 检查Python版本（需要3.7+）
python --version

# 如果没有，请从python.org下载安装
```

### 安装依赖包

```bash
pip install numpy matplotlib
```

---

## 2️⃣ 5分钟快速体验

### 运行第一个案例

```bash
# 克隆或下载项目
cd /workspace/books/photovoltaic-system-modeling-control

# 运行案例13: PWM调制
cd code/examples/case_13_pwm_modulation
python main.py
```

**预期结果**: 
- 输出SPWM和SVPWM的波形图
- 显示THD性能对比
- 保存图片到当前目录

---

## 3️⃣ 推荐学习顺序

### 初学者路径 (10周)

**第1-2周**: 光伏建模基础
```bash
# 案例1: 单二极管模型
cd code/examples/case_01_single_diode
python main.py

# 案例3: 温度影响
cd ../case_03_temperature_effect
python main.py
```

**第3-4周**: MPPT算法
```bash
# 案例7: 扰动观察法
cd ../case_07_perturb_observe
python main.py

# 案例10: 模糊逻辑
cd ../case_10_fuzzy_mppt
python main.py
```

**第5-8周**: 并网控制
```bash
# 案例13-18: 按顺序学习
cd ../case_13_pwm_modulation && python main.py
cd ../case_14_current_control && python main.py
cd ../case_15_voltage_control && python main.py
# ... 依此类推
```

**第9-10周**: 系统集成
```bash
# 案例19-22: 直流侧控制
# 案例23-26: 高级应用
```

---

## 4️⃣ 常用命令

### 运行测试

```bash
# 测试逆变器控制模块
cd /workspace
python tests/test_inverter_control.py

# 测试DC/DC变换器
python tests/test_dcdc_converter.py
```

### 查看案例文档

```bash
# 每个案例都有README.md
cd code/examples/case_13_pwm_modulation
cat README.md  # 或用文本编辑器打开
```

---

## 5️⃣ 代码结构说明

### 核心模块位置

```python
# 导入光伏模型
import sys
sys.path.insert(0, 'code')
from models.pv_cell import PhotovoltaicCell

# 导入MPPT算法
from models.mppt import PerturbObserve, IncrementalConductance

# 导入逆变器控制
from models.inverter_control import SPWMModulator, PIController

# 导入DC/DC变换器
from models.dcdc_converter import BoostConverter
```

### 创建自己的实验

```python
import numpy as np
import matplotlib.pyplot as plt
from models.inverter_control import SPWMModulator

# 创建SPWM调制器
spwm = SPWMModulator(V_dc=400.0, f_carrier=10000, f_modulation=50)

# 仿真
dt = 1e-6
time = np.arange(0, 0.02, dt)
v_out = []

for t in time:
    v_a, v_b, v_c = spwm.generate(t)
    v_out.append(v_a)

# 绘图
plt.plot(time*1000, v_out)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.show()
```

---

## 6️⃣ 常见问题

### Q1: 运行报错 "No module named 'models'"

**解决**: 确保在正确的目录运行，或添加路径：
```python
import sys
sys.path.insert(0, '/path/to/code')
```

### Q2: 图片不显示

**解决**: 
```python
# 在代码最后添加
plt.show()

# 或保存图片
plt.savefig('output.png')
```

### Q3: 测试失败

**解决**: 
1. 检查Python版本 (需要3.7+)
2. 检查numpy/matplotlib版本
3. 查看具体错误信息

---

## 7️⃣ 学习资源

### 案例文档

每个案例的README包含：
- 📖 理论讲解
- 💻 代码说明
- 🧪 实验步骤
- 📊 预期结果
- 🎓 作业练习

### 进度跟踪

查看 `PROGRESS.md` 了解：
- 各阶段完成情况
- 案例详细信息
- 开发统计

### 技术参考

查看各模块源代码：
- 详细的文档字符串
- 完整的参数说明
- 使用示例

---

## 8️⃣ 下一步

### 基础扎实后

- 修改参数，观察影响
- 尝试不同工况
- 对比算法性能

### 进阶学习

- 阅读扩展资料
- 研究源代码实现
- 完成作业练习

### 实践应用

- 设计完整系统
- 参数优化
- 性能评估

---

## 9️⃣ 获取帮助

### 文档

1. README.md - 项目概述
2. PROGRESS.md - 开发进度
3. 各案例/README.md - 详细文档

### 代码

1. 查看源代码注释
2. 运行测试用例
3. 参考示例程序

### 社区

1. 提交Issue
2. 参与讨论
3. 贡献代码

---

## 🎯 学习目标检查清单

### 阶段一 (基础建模)
- [ ] 理解光伏电池I-V特性
- [ ] 掌握单/双二极管模型
- [ ] 了解环境因素影响
- [ ] 能够建立阵列模型

### 阶段二 (MPPT控制)
- [ ] 理解MPPT原理
- [ ] 实现P&O和INC算法
- [ ] 掌握智能MPPT方法
- [ ] 能够应对多峰问题

### 阶段三 (并网控制)
- [ ] 掌握PWM调制技术
- [ ] 实现电流电压控制
- [ ] 理解PLL同步原理
- [ ] 满足并网标准要求

### 阶段四 (直流侧)
- [ ] 掌握DC/DC拓扑
- [ ] 实现电压控制
- [ ] 理解功率解耦
- [ ] 了解微网控制

### 阶段五 (系统集成)
- [ ] 实现协调控制
- [ ] 掌握保护技术
- [ ] 理解故障穿越
- [ ] 能够多机并联

---

## 💡 小贴士

1. **循序渐进**: 按顺序学习，不要跳跃
2. **动手实践**: 运行每个案例，修改参数
3. **理解原理**: 不只是运行代码，要理解为什么
4. **记录笔记**: 记录问题和解决方案
5. **对比分析**: 对比不同算法的优缺点

---

## 🚀 准备好了吗？

现在开始你的光伏系统学习之旅！

```bash
# 从案例1开始
cd code/examples/case_01_single_diode
python main.py

# 祝学习愉快！
```

---

**更新**: 2025-11-04  
**版本**: v1.0

🎉 **Happy Learning!** 🎉
