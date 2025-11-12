#!/usr/bin/env python3
"""
《水力学1000题详解》快速演示脚本
Quick Start Demo for Hydraulics-1000 Code Library

这个脚本演示如何使用代码库中的各个模块。
This script demonstrates how to use modules in the code library.

作者: CHS-Books开发团队
日期: 2025-11-10
"""

import sys
import os

# 确保可以导入代码库中的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("《水力学1000题详解》Python代码库 - 快速演示")
print("Hydraulics-1000 Python Code Library - Quick Start Demo")
print("="*80)
print()

# ============================================================================
# 演示1: 静水压强计算
# ============================================================================
print("【演示1：静水压强计算】")
print("-" * 60)

try:
    from problem_001_hydrostatic_pressure import HydrostaticPressure
    
    # 创建求解器
    solver1 = HydrostaticPressure()
    
    # 修改参数
    solver1.h = 15  # 水深15米
    
    # 计算
    solver1.calculate_pressure()
    
    print(f"✓ 成功运行 problem_001_hydrostatic_pressure")
    print(f"  水深: {solver1.h} m")
    print(f"  密度: {solver1.rho} kg/m³")
    print(f"  压强: {solver1.p:.2f} Pa = {solver1.p/1000:.2f} kPa")
    print()
except ImportError as e:
    print(f"✗ 无法导入 problem_001: {e}")
    print("  请确保代码文件存在")
    print()
except Exception as e:
    print(f"✗ 运行出错: {e}")
    print()

# ============================================================================
# 演示2: 管道水力计算
# ============================================================================
print("【演示2：管道水力计算】")
print("-" * 60)

try:
    from problem_351_pipe_calculation import PipeCalculation
    
    # 创建求解器
    solver2 = PipeCalculation()
    
    # 修改参数
    solver2.Q = 0.05  # 流量0.05 m³/s
    solver2.d = 0.2   # 直径0.2m
    solver2.L = 500   # 长度500m
    
    # 重新计算
    solver2.calculate_velocity()
    solver2.calculate_reynolds()
    solver2.calculate_friction_factor()
    solver2.calculate_head_loss()
    
    print(f"✓ 成功运行 problem_351_pipe_calculation")
    print(f"  流量: {solver2.Q} m³/s")
    print(f"  管径: {solver2.d} m")
    print(f"  流速: {solver2.v:.4f} m/s")
    print(f"  Reynolds数: {solver2.Re:.0f}")
    print(f"  阻力系数λ: {solver2.lambda_f:.4f}")
    print(f"  水头损失: {solver2.h_f:.4f} m")
    print()
except ImportError as e:
    print(f"✗ 无法导入 problem_351: {e}")
    print("  该代码可能不存在或命名不同")
    print()
except Exception as e:
    print(f"✗ 运行出错: {e}")
    print()

# ============================================================================
# 演示3: 明渠均匀流计算
# ============================================================================
print("【演示3：明渠均匀流计算】")
print("-" * 60)

try:
    from problem_456_manning_formula import ManningFormula
    
    # 创建求解器
    solver3 = ManningFormula()
    
    # 修改参数
    solver3.b = 8     # 底宽8m
    solver3.h = 2.5   # 水深2.5m
    solver3.i = 0.001 # 坡度0.001
    solver3.n = 0.02  # 糙率0.02
    
    # 重新计算
    solver3.calculate_flow()
    
    print(f"✓ 成功运行 problem_456_manning_formula")
    print(f"  底宽: {solver3.b} m")
    print(f"  水深: {solver3.h} m")
    print(f"  坡度: {solver3.i}")
    print(f"  糙率: {solver3.n}")
    print(f"  流量: {solver3.Q:.4f} m³/s")
    print(f"  流速: {solver3.v:.4f} m/s")
    print()
except ImportError as e:
    print(f"✗ 无法导入 problem_456: {e}")
    print("  该代码可能不存在或命名不同")
    print()
except Exception as e:
    print(f"✗ 运行出错: {e}")
    print()

# ============================================================================
# 演示4: 水泵工况分析
# ============================================================================
print("【演示4：水泵工况分析】")
print("-" * 60)

try:
    from problem_791_pump_operation import PumpOperation
    
    # 创建求解器
    solver4 = PumpOperation()
    
    print(f"✓ 成功运行 problem_791_pump_operation")
    print(f"  水泵型号: {solver4.pump.name}")
    print(f"  额定流量: {solver4.pump.Q0} m³/s")
    print(f"  额定扬程: {solver4.pump.H0} m")
    print(f"  额定效率: {solver4.pump.eta0*100:.1f}%")
    print(f"  工况流量: {solver4.Q_operating:.4f} m³/s")
    print(f"  工况扬程: {solver4.H_operating:.4f} m")
    print()
except ImportError as e:
    print(f"✗ 无法导入 problem_791: {e}")
    print()
except Exception as e:
    print(f"✗ 运行出错: {e}")
    print()

# ============================================================================
# 演示5: 综合水利工程系统
# ============================================================================
print("【演示5：综合水利工程系统】")
print("-" * 60)

try:
    from problem_904_integrated_water_project import IntegratedWaterProject
    
    # 创建求解器
    solver5 = IntegratedWaterProject()
    
    print(f"✓ 成功运行 problem_904_integrated_water_project")
    print(f"  上游水位: {solver5.H1} m")
    print(f"  厂房高程: {solver5.H2} m")
    print(f"  设计流量: {solver5.Q_design} m³/s")
    print(f"  毛水头: {solver5.H_gross} m")
    print(f"  净水头: {solver5.H_net:.2f} m")
    print(f"  装机容量: {solver5.P_generator/1000:.3f} MW")
    print(f"  总效率: {solver5.eta_total*100:.2f}%")
    print(f"  年发电量: {solver5.annual_energy:.0f} MWh")
    print()
except ImportError as e:
    print(f"✗ 无法导入 problem_904: {e}")
    print()
except Exception as e:
    print(f"✗ 运行出错: {e}")
    print()

# ============================================================================
# 总结
# ============================================================================
print("="*80)
print("【演示总结】")
print("-" * 60)
print("""
✓ 快速演示完成！

您已经看到了如何：
1. 导入代码库中的模块
2. 创建求解器对象
3. 修改计算参数
4. 执行计算
5. 查看结果

更多功能：
- 运行完整代码查看详细输出和可视化
- 查看 README.md 了解使用指南
- 查看 CODE_INDEX.md 了解所有可用代码
- 运行 run_all_tests.sh 批量测试所有代码

示例命令：
  python3 problem_904_integrated_water_project.py  # 运行完整计算
  bash run_all_tests.sh                           # 批量测试
  cat README.md                                   # 查看使用指南
""")
print("="*80)


if __name__ == "__main__":
    print("\n提示: 要运行完整的代码示例，请直接执行相应的Python文件")
    print("例如: python3 problem_904_integrated_water_project.py")
