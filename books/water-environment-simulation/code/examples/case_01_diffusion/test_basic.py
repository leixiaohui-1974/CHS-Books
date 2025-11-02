"""
基础功能测试（不需要外部依赖）
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_diffusion_model():
    """测试扩散模型基本功能"""
    try:
        # 尝试导入numpy
        import numpy as np
        has_numpy = True
    except ImportError:
        print("警告: NumPy未安装，跳过数值测试")
        has_numpy = False
        return False
    
    try:
        from models.diffusion import Diffusion1D
        print("✓ 成功导入Diffusion1D模型")
    except Exception as e:
        print(f"✗ 导入模型失败: {e}")
        return False
    
    try:
        # 创建模型
        model = Diffusion1D(L=10.0, T=100.0, nx=50, nt=500, D=0.01)
        print(f"✓ 成功创建模型")
        print(f"  - 网格: {model.nx} x {model.nt}")
        print(f"  - dx = {model.dx:.4f} m, dt = {model.dt:.4f} s")
        print(f"  - Fourier数: Fo = {model.Fo:.4f}")
        
        # 检查稳定性
        if model.Fo <= 0.5:
            print(f"✓ 满足显式稳定性条件 (Fo ≤ 0.5)")
        else:
            print(f"⚠ 不满足显式稳定性条件 (Fo = {model.Fo} > 0.5)")
        
    except Exception as e:
        print(f"✗ 创建模型失败: {e}")
        return False
    
    try:
        # 设置初始条件
        x0 = 5.0
        sigma = 0.5
        C0 = lambda x: np.exp(-((x - x0) / sigma)**2)
        model.set_initial_condition(C0)
        print(f"✓ 成功设置初始条件")
        
        # 设置边界条件
        model.set_boundary_conditions('dirichlet', 0.0, 0.0)
        print(f"✓ 成功设置边界条件")
        
    except Exception as e:
        print(f"✗ 设置条件失败: {e}")
        return False
    
    try:
        # 显式求解
        print(f"\n开始显式求解...")
        C_explicit = model.solve_explicit()
        print(f"✓ 显式求解完成")
        print(f"  - 结果形状: {C_explicit.shape}")
        print(f"  - 初始最大浓度: {np.max(C_explicit[0, :]):.6f}")
        print(f"  - 最终最大浓度: {np.max(C_explicit[-1, :]):.6f}")
        
        # 检查物理合理性
        if np.all(C_explicit >= -1e-10):
            print(f"✓ 浓度始终非负")
        else:
            print(f"✗ 出现负浓度")
            return False
        
        if np.all(np.isfinite(C_explicit)):
            print(f"✓ 结果数值稳定")
        else:
            print(f"✗ 出现NaN或Inf")
            return False
        
        # 检查扩散效果
        peak_initial = np.max(C_explicit[0, :])
        peak_final = np.max(C_explicit[-1, :])
        if peak_final < peak_initial:
            print(f"✓ 峰值随时间降低（扩散效果正确）")
        else:
            print(f"⚠ 峰值未降低")
        
    except Exception as e:
        print(f"✗ 显式求解失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        # 隐式求解
        print(f"\n开始隐式求解...")
        model.set_initial_condition(C0)
        model.set_boundary_conditions('dirichlet', 0.0, 0.0)
        C_implicit = model.solve_implicit()
        print(f"✓ 隐式求解完成")
        
        # 对比两种方法
        diff = np.abs(C_explicit[-1, :] - C_implicit[-1, :])
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)
        print(f"  - 显式与隐式差异:")
        print(f"    最大差异: {max_diff:.6e}")
        print(f"    平均差异: {mean_diff:.6e}")
        
        if max_diff < 0.1:
            print(f"✓ 两种方法结果一致")
        else:
            print(f"⚠ 两种方法结果差异较大")
        
    except Exception as e:
        print(f"✗ 隐式求解失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n" + "=" * 60)
    print(f"✓ 所有基本功能测试通过！")
    print(f"=" * 60)
    return True


if __name__ == '__main__':
    success = test_diffusion_model()
    sys.exit(0 if success else 1)
