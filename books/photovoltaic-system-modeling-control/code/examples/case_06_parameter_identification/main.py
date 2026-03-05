# --- CHS AUTOMATED ENVIRONMENT FIX ---
import sys, os
# Super safe I/O override for Windows legacy scripts
class SafeWriter:
    def __init__(self, target):
        self.target = target
    def write(self, s):
        try:
            self.target.write(s)
        except UnicodeEncodeError:
            self.target.write(s.encode('utf-8', 'backslashreplace').decode('gbk', 'ignore'))
    def flush(self):
        if hasattr(self.target, 'flush'): self.target.flush()
    def __getattr__(self, name):
        return getattr(self.target, name)

if not getattr(sys.stdout, '_chs_safe', False):
    sys.stdout = SafeWriter(sys.stdout)
    sys.stdout._chs_safe = True
if not getattr(sys.stderr, '_chs_safe', False):
    sys.stderr = SafeWriter(sys.stderr)
    sys.stderr._chs_safe = True

_current_dir = os.path.dirname(os.path.abspath(__file__))
for i in range(4):
    _test_path = os.path.abspath(os.path.join(_current_dir, *(['..'] * i)))
    if os.path.exists(os.path.join(_test_path, 'core')) or os.path.exists(os.path.join(_test_path, 'gwflow')) or os.path.exists(os.path.join(_test_path, 'models')) or os.path.exists(os.path.join(_test_path, 'code', 'core')):
        if _test_path not in sys.path:
            sys.path.insert(0, _test_path)
        code_dir = os.path.join(_test_path, 'code')
        if os.path.exists(code_dir) and code_dir not in sys.path:
            sys.path.insert(0, code_dir)
        break
# -------------------------------------
"""
案例6: 参数辨识方法
Case 6: Parameter Identification Methods

工程背景:
--------
光伏系统建模需要准确的参数:
- 新组件参数验证
- 现场测试辨识  
- 老化参数跟踪
- 模型精度提升

学习目标:
--------
1. 掌握参数辨识原理
2. 学习多种辨识方法
3. 理解参数物理意义
4. 评估辨识精度
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

from code.models.pv_cell import SingleDiodeModel
from code.models.pv_module import PVModule
from code.models.pv_identification import ParameterExtractor, ParameterComparator


def main():
    """主函数: 参数辨识方法演示"""
    print("=" * 80)
    print("案例6: 参数辨识方法")
    print("Case 6: Parameter Identification Methods")
    print("=" * 80)
    
    # 1. 生成"测试"数据(模拟真实测量)
    print("\n步骤1: 生成测试数据")
    print("-" * 80)
    
    # 创建真实模型
    true_params = {
        'Isc': 8.0,
        'Voc': 0.6,
        'Imp': 7.5,
        'Vmp': 0.48,
        'T': 298.15,
        'G': 1000.0
    }
    
    cell_true = SingleDiodeModel(**true_params)
    V_measured, I_measured = cell_true.get_iv_curve(100)
    
    # 添加测量噪声
    noise_level = 0.02  # 2%
    I_measured = I_measured + np.random.normal(0, noise_level, len(I_measured))
    
    print(f"生成测试数据: {len(V_measured)} 个点")
    print(f"噪声水平: {noise_level*100:.1f}%")
    
    # 提取关键点
    Isc_m = I_measured[0]
    Voc_m = V_measured[np.argmin(np.abs(I_measured))]
    P_m = V_measured * I_measured
    idx_mpp = np.argmax(P_m)
    Vmp_m = V_measured[idx_mpp]
    Imp_m = I_measured[idx_mpp]
    
    print(f"\n关键点:")
    print(f"  Isc = {Isc_m:.3f} A")
    print(f"  Voc = {Voc_m:.3f} V")
    print(f"  Vmp = {Vmp_m:.3f} V")
    print(f"  Imp = {Imp_m:.3f} A")
    print(f"  Pmp = {Vmp_m*Imp_m:.3f} W")
    
    # 2. 方法1: 关键点法
    print("\n步骤2: 方法1 - 关键点法")
    print("-" * 80)
    
    extractor = ParameterExtractor()
    params_kp = extractor.extract_from_key_points(
        Isc_m, Voc_m, Imp_m, Vmp_m, T=298.15, Ns=1
    )
    
    print(f"提取参数:")
    print(f"  Iph = {params_kp['Iph']:.6f} A")
    print(f"  I0  = {params_kp['I0']:.3e} A")
    print(f"  Rs  = {params_kp['Rs']:.6f} Ω")
    print(f"  Rsh = {params_kp['Rsh']:.3f} Ω")
    print(f"  n   = {params_kp['n']:.3f}")
    
    # 3. 方法2-4: 优化方法
    print("\n步骤3: 方法2-4 - 优化方法")
    print("-" * 80)
    
    comparator = ParameterComparator()
    all_results = comparator.compare_methods(V_measured, I_measured, T=298.15, Ns=1)
    
    print("\n各方法对比:")
    print(f"{'方法':<20} {'RMSE':<12} {'R²':<12} {'成功':<8}")
    print("-" * 60)
    
    for method_name, result in all_results.items():
        if result and 'rmse' in result:
            print(f"{method_name:<20} {result['rmse']:<12.6f} {result['r2']:<12.6f} "
                  f"{'✓' if result.get('success', True) else '✗':<8}")
        else:
            print(f"{method_name:<20} {'N/A':<12} {'N/A':<12} {'✗':<8}")
    
    # 选择最佳方法
    best_method = 'least_squares'
    params_best = all_results[best_method]
    
    print(f"\n最佳方法: {best_method}")
    print(f"提取参数:")
    print(f"  Iph = {params_best['Iph']:.6f} A")
    print(f"  I0  = {params_best['I0']:.3e} A")
    print(f"  Rs  = {params_best['Rs']:.6f} Ω")
    print(f"  Rsh = {params_best['Rsh']:.3f} Ω")
    print(f"  n   = {params_best['n']:.3f}")
    
    # 4. 精度评估
    print("\n步骤4: 精度评估")
    print("-" * 80)
    
    accuracy = comparator.evaluate_accuracy(
        params_best, V_measured, I_measured, T=298.15, Ns=1
    )
    
    print(f"误差指标:")
    print(f"  MAE  = {accuracy['mae']:.6f} A")
    print(f"  RMSE = {accuracy['rmse']:.6f} A")
    print(f"  MAPE = {accuracy['mape']:.3f} %")
    print(f"  R²   = {accuracy['r2']:.6f}")
    
    # 5. 可视化
    print("\n步骤5: 结果可视化")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 图1: 测量数据vs拟合曲线(I-V)
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(V_measured, I_measured, 'bo', markersize=4, alpha=0.5, label='测量数据')
    ax1.plot(V_measured, params_best['I_fitted'], 'r-', linewidth=2, label='拟合曲线')
    ax1.set_xlabel('电压 (V)', fontsize=11)
    ax1.set_ylabel('电流 (A)', fontsize=11)
    ax1.set_title(f'I-V曲线拟合 (R²={accuracy["r2"]:.4f})', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2: P-V曲线对比
    ax2 = plt.subplot(2, 3, 2)
    P_measured = V_measured * I_measured
    P_fitted = V_measured * params_best['I_fitted']
    ax2.plot(V_measured, P_measured, 'bo', markersize=4, alpha=0.5, label='测量数据')
    ax2.plot(V_measured, P_fitted, 'r-', linewidth=2, label='拟合曲线')
    ax2.set_xlabel('电压 (V)', fontsize=11)
    ax2.set_ylabel('功率 (W)', fontsize=11)
    ax2.set_title('P-V曲线拟合', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: 残差分析
    ax3 = plt.subplot(2, 3, 3)
    residuals = I_measured - params_best['I_fitted']
    ax3.plot(V_measured, residuals, 'go', markersize=4, alpha=0.6)
    ax3.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax3.set_xlabel('电压 (V)', fontsize=11)
    ax3.set_ylabel('残差 (A)', fontsize=11)
    ax3.set_title(f'残差分布 (RMSE={accuracy["rmse"]:.4f}A)', fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 参数对比(不同方法)
    ax4 = plt.subplot(2, 3, 4)
    methods = ['key_points', 'least_squares', 'minimize']
    param_names = ['Rs', 'Rsh', 'n']
    
    x = np.arange(len(param_names))
    width = 0.25
    
    for i, method in enumerate(methods):
        if all_results[method]:
            values = [
                all_results[method]['Rs'] * 1000,  # 转为mΩ
                all_results[method]['Rsh'] / 100,  # 缩放
                all_results[method]['n']
            ]
            ax4.bar(x + i*width, values, width, label=method, alpha=0.7)
    
    ax4.set_ylabel('参数值', fontsize=11)
    ax4.set_title('不同方法参数对比', fontsize=12)
    ax4.set_xticks(x + width)
    ax4.set_xticklabels(['Rs(mΩ)', 'Rsh(/100Ω)', 'n'])
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 图5: 精度对比
    ax5 = plt.subplot(2, 3, 5)
    methods_valid = [m for m in methods if all_results[m] and 'rmse' in all_results[m]]
    rmse_values = [all_results[m]['rmse'] * 1000 for m in methods_valid]  # 转为mA
    
    bars = ax5.bar(range(len(methods_valid)), rmse_values, 
                   color=['steelblue', 'seagreen', 'coral'][:len(methods_valid)],
                   alpha=0.7)
    ax5.set_ylabel('RMSE (mA)', fontsize=11)
    ax5.set_title('拟合精度对比', fontsize=12)
    ax5.set_xticks(range(len(methods_valid)))
    ax5.set_xticklabels(methods_valid, rotation=20, fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, rmse_values):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 图6: 误差分布直方图
    ax6 = plt.subplot(2, 3, 6)
    ax6.hist(residuals * 1000, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax6.axvline(x=0, color='r', linestyle='--', linewidth=2)
    ax6.set_xlabel('残差 (mA)', fontsize=11)
    ax6.set_ylabel('频数', fontsize=11)
    ax6.set_title(f'残差分布直方图', fontsize=12)
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('光伏参数辨识方法对比', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # 保存
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'parameter_identification.png'),
                dpi=300, bbox_inches='tight')
    print(f"图表已保存")
    
    # 6. 总结
    print("\n步骤6: 总结")
    print("=" * 80)
    
    print("\n方法对比:")
    print("  关键点法:   简单快速, 精度较低")
    print("  最小二乘法: 精度高, 收敛快 (推荐)")
    print("  优化法:     精度高, 计算稍慢")
    print("  曲线拟合:   精度高, 需要好的初值")
    
    print(f"\n最佳精度: RMSE = {accuracy['rmse']*1000:.2f} mA, R² = {accuracy['r2']:.6f}")
    print("提取参数可用于精确建模!")
    
    print("\n" + "=" * 80)
    print("案例6主程序完成！")
    print("🎉 阶段一全部6个案例开发完成！")
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()