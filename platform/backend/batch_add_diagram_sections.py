#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为案例12-20批量添加示意图说明部分
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 案例12-20的示意图说明模板
diagram_sections = {
    12: {
        "title": "LQR与观测器设计系统示意图",
        "image": "case12_observer_lqr_summary.png",
        "description": """**系统架构说明：**

这张综合图展示了状态观测器与LQR最优控制的完整系统架构：

**核心组件：**

1. **状态观测器（Luenberger Observer）**：
   - 观测器方程：dx̂/dt = Ax̂ + Bu + L(y - ŷ)
   - 从输出y估计状态x̂
   - L为观测器增益矩阵
   - 估计误差渐近收敛到零

2. **LQR最优控制器**：
   - 性能指标：J = ∫(x'Qx + u'Ru)dt
   - 最优控制律：u = -Kx̂（使用估计状态）
   - K通过求解Riccati方程得到
   - Q权衡状态偏差，R权衡控制能量

3. **分离原理（Separation Principle）**：
   - 观测器和控制器可独立设计
   - 观测器极点：快速收敛
   - 控制器极点：期望闭环性能
   - 联合系统保持稳定性

**系统优势：**
- 最优性能保证
- 鲁棒性好
- 适用于状态不可测系统
- 工程实用性强

**应用场景：**
适用于需要高性能控制但状态不完全可测的系统。"""
    },
    13: {
        "title": "自适应控制系统示意图",
        "image": "case13_adaptive_control_summary.png",
        "description": """**系统架构说明：**

这张图展示了自适应控制系统的基本架构和工作原理：

**核心特点：**

1. **参数自适应机制**：
   - 在线辨识系统参数
   - 根据参数变化调整控制器
   - 适应时变或不确定系统
   - 保证系统性能

2. **自适应律设计**：
   - 基于Lyapunov稳定性理论
   - 保证参数收敛
   - 保证跟踪误差收敛
   - 自适应增益设计

3. **控制系统结构**：
   - 直接自适应（调整控制参数）
   - 间接自适应（先辨识再控制）
   - MIT规则或其他自适应律

**系统优势：**
- 适应参数变化
- 无需精确模型
- 在线学习能力
- 鲁棒性强

**应用场景：**
适用于参数时变、不确定性大的系统。"""
    },
    14: {
        "title": "模型预测控制（MPC）系统示意图",
        "image": "case14_mpc_demo.png",
        "description": """**系统架构说明：**

这张图展示了模型预测控制（MPC）的基本原理和滚动优化策略：

**核心思想：**

1. **预测模型**：
   - 使用系统模型预测未来行为
   - 预测时域：Np步
   - 考虑当前状态和未来控制

2. **滚动优化**：
   - 在线求解优化问题
   - 最小化性能指标
   - 考虑约束条件
   - 只执行第一个控制量

3. **反馈校正**：
   - 测量实际输出
   - 更新预测模型
   - 滚动到下一时刻
   - 重复优化过程

**关键优势：**
- 显式处理约束
- 多变量系统友好
- 预测未来行为
- 最优性能保证

**应用场景：**
适用于有约束的多变量优化控制问题。"""
    },
    15: {
        "title": "滑模控制系统示意图",
        "image": "case15_sliding_mode_summary.png",
        "description": """**系统架构说明：**

这张图展示了滑模控制的基本原理和滑动模态设计：

**核心概念：**

1. **滑模面设计**：
   - s(x) = 0定义滑模面
   - 系统状态被"吸引"到滑模面
   - 在滑模面上滑动到原点
   - 实现期望动态

2. **趋近律设计**：
   - 控制律使系统趋近滑模面
   - 常用：等速趋近律、指数趋近律
   - 保证有限时间到达
   - 抖振抑制

3. **鲁棒性特点**：
   - 对参数变化不敏感
   - 对外部扰动鲁棒
   - 有限时间收敛
   - 快速响应

**系统优势：**
- 鲁棒性极强
- 快速响应
- 实现简单
- 适用于不确定系统

**应用场景：**
适用于强不确定性、强扰动的系统。"""
    },
    16: {
        "title": "模糊控制系统示意图",
        "image": "case16_fuzzy_control_summary.png",
        "description": """**系统架构说明：**

这张图展示了模糊控制系统的基本结构和推理过程：

**核心组件：**

1. **模糊化（Fuzzification）**：
   - 将精确输入转为模糊量
   - 定义隶属度函数
   - 语言变量（大、中、小等）

2. **模糊推理**：
   - IF-THEN规则库
   - 基于专家知识
   - 模糊逻辑运算
   - 并行推理

3. **去模糊化（Defuzzification）**：
   - 将模糊输出转为精确值
   - 常用重心法
   - 得到控制量

**系统优势：**
- 无需精确数学模型
- 融入专家经验
- 处理非线性问题
- 易于理解和调整

**应用场景：**
适用于难以建立精确模型但有经验规则的系统。"""
    },
    17: {
        "title": "神经网络控制系统示意图",
        "image": "case17_nn_basics.png",
        "description": """**系统架构说明：**

这张图展示了神经网络控制的基本架构和学习过程：

**核心方法：**

1. **神经网络控制器**：
   - 多层前馈网络
   - 反向传播训练
   - 非线性映射能力
   - 在线学习

2. **控制策略**：
   - 直接神经网络控制
   - 神经网络PID
   - 神经网络逆模型
   - 模型参考自适应

3. **训练过程**：
   - 监督学习（离线训练）
   - 强化学习（在线调整）
   - 误差反向传播
   - 权值更新

**系统优势：**
- 强大的非线性逼近能力
- 自学习能力
- 适应性强
- 并行计算

**应用场景：**
适用于复杂非线性、难以建模的系统。"""
    },
    18: {
        "title": "强化学习控制系统示意图",
        "image": "case18_rl_control_summary.png",
        "description": """**系统架构说明：**

这张图展示了强化学习控制的基本框架和学习过程：

**核心概念：**

1. **强化学习框架**：
   - Agent（智能体）：控制器
   - Environment（环境）：被控系统
   - State（状态）：系统状态
   - Action（动作）：控制输入
   - Reward（奖励）：性能评价

2. **学习过程**：
   - 观察状态
   - 选择动作
   - 获得奖励
   - 更新策略
   - 迭代优化

3. **常用算法**：
   - Q-Learning
   - Deep Q-Network (DQN)
   - Policy Gradient
   - Actor-Critic

**系统优势：**
- 无需系统模型
- 通过交互学习
- 适应复杂环境
- 长期优化

**应用场景：**
适用于复杂决策、难以设计控制律的系统。"""
    },
    19: {
        "title": "控制方法综合对比示意图",
        "image": "case19_comprehensive_comparison.png",
        "description": """**系统架构说明：**

这张综合对比图展示了各种控制方法的性能对比和适用场景：

**对比维度：**

1. **控制性能**：
   - 上升时间
   - 超调量
   - 稳态误差
   - 鲁棒性

2. **实现复杂度**：
   - 算法复杂度
   - 计算量
   - 参数数量
   - 调试难度

3. **适用场景**：
   - 系统类型
   - 不确定性
   - 实时性要求
   - 工程应用

**方法对比：**
- **经典控制**：简单、快速、适合SISO
- **现代控制**：系统化、适合MIMO
- **智能控制**：自适应、适合复杂系统

**选择建议：**
根据系统特点、性能要求、实现条件综合选择。"""
    },
    20: {
        "title": "实际应用案例示意图",
        "image": "case20_practical_application.png",
        "description": """**系统架构说明：**

这张图展示了控制理论在实际水处理系统中的综合应用：

**实际系统特点：**

1. **多目标优化**：
   - 水位稳定
   - 能耗最小
   - 水质保证
   - 成本优化

2. **多约束条件**：
   - 设备物理限制
   - 安全运行范围
   - 环保法规要求
   - 经济性考虑

3. **综合控制策略**：
   - 分层控制架构
   - 多控制器协同
   - 优化与控制结合
   - 故障检测与诊断

**工程实施要点：**
- 系统建模与验证
- 控制器参数整定
- 仿真测试
- 现场调试
- 运行维护

**应用价值：**
展示理论到实践的完整过程，体现控制理论的工程价值。"""
    }
}

def add_diagram_section(case_num, case_dir):
    """为案例添加示意图部分"""
    readme_path = case_dir / "README.md"
    
    if not readme_path.exists():
        print(f"  ✗ README不存在：{readme_path}")
        return False
    
    # 读取现有内容
    content = readme_path.read_text(encoding='utf-8')
    
    # 检查是否已有示意图部分
    if "## 系统示意图" in content:
        print(f"  ⚠ 已存在示意图部分，跳过")
        return True
    
    # 获取模板
    info = diagram_sections.get(case_num)
    if not info:
        print(f"  ✗ 没有案例{case_num}的模板")
        return False
    
    # 构建示意图部分
    diagram_section = f'''## 系统示意图

### 图1：{info["title"]}

<table>
<tr>
<td width="50%"><img src="{info["image"]}" alt="{info["title"]}" width="100%"/></td>
<td width="50%">

{info["description"]}

</td>
</tr>
</table>

'''
    
    # 在第一个##标题之前插入（通常是"场景描述"或类似）
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if i > 0 and line.startswith('## '):
            insert_pos = i
            break
    
    if insert_pos > 0:
        new_lines = lines[:insert_pos] + diagram_section.split('\n') + lines[insert_pos:]
        new_content = '\n'.join(new_lines)
        readme_path.write_text(new_content, encoding='utf-8')
        print(f"  ✓ 已添加示意图部分")
        return True
    else:
        print(f"  ✗ 无法找到插入位置")
        return False

def main():
    """主函数"""
    print("="*80)
    print("批量为案例12-20添加示意图说明")
    print("="*80)
    
    success_count = 0
    total_count = 9
    
    for case_num in range(12, 21):
        case_name = f"case_{case_num:02d}_*"
        case_dirs = list(CASES_DIR.glob(case_name))
        
        if not case_dirs:
            print(f"\n案例{case_num}：目录不存在")
            continue
        
        case_dir = case_dirs[0]
        print(f"\n案例{case_num}：{case_dir.name}")
        
        if add_diagram_section(case_num, case_dir):
            success_count += 1
    
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"成功：{success_count}/{total_count}")
    print(f"成功率：{success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    main()

