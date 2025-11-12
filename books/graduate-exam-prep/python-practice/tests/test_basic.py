#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试脚本
测试Python环境和依赖库是否正确安装
"""

import sys

def test_python_version():
    """测试Python版本"""
    print("="*60)
    print("测试Python版本")
    print("="*60)
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本符合要求 (3.8+)")
        return True
    else:
        print("❌ Python版本过低，建议升级到3.8+")
        return False


def test_imports():
    """测试核心库导入"""
    print("\n" + "="*60)
    print("测试核心库导入")
    print("="*60)
    
    libraries = [
        ('numpy', 'NumPy'),
        ('matplotlib', 'Matplotlib'),
        ('pandas', 'Pandas'),
        ('scipy', 'SciPy'),
        ('sympy', 'SymPy')
    ]
    
    results = []
    for module_name, display_name in libraries:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {display_name:12} {version:12} 导入成功")
            results.append(True)
        except ImportError:
            print(f"❌ {display_name:12} {'':12} 未安装")
            results.append(False)
    
    return all(results)


def test_basic_calculation():
    """测试基础计算"""
    print("\n" + "="*60)
    print("测试基础计算")
    print("="*60)
    
    try:
        import numpy as np
        
        # 创建数组
        arr = np.array([1, 2, 3, 4, 5])
        
        # 计算统计量
        mean = np.mean(arr)
        std = np.std(arr)
        
        print(f"数组: {arr}")
        print(f"均值: {mean:.2f}")
        print(f"标准差: {std:.2f}")
        print("✅ 基础计算测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 基础计算测试失败: {e}")
        return False


def test_plotting():
    """测试绘图功能"""
    print("\n" + "="*60)
    print("测试绘图功能")
    print("="*60)
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # 非交互式后端
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 创建简单图表
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        plt.figure(figsize=(8, 6))
        plt.plot(x, y)
        plt.title('Test Plot')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.savefig('/tmp/test_plot.png')
        plt.close()
        
        print("✅ 绘图功能测试通过")
        print("   测试图表已保存到 /tmp/test_plot.png")
        return True
        
    except Exception as e:
        print(f"❌ 绘图功能测试失败: {e}")
        return False


def test_data_processing():
    """测试数据处理"""
    print("\n" + "="*60)
    print("测试数据处理")
    print("="*60)
    
    try:
        import pandas as pd
        
        # 创建DataFrame
        data = {
            '日期': ['2024-01-01', '2024-01-02', '2024-01-03'],
            '水位(m)': [125.5, 126.2, 127.1],
            '流量(m³/s)': [3800, 4100, 4500]
        }
        df = pd.DataFrame(data)
        
        # 统计分析
        mean_level = df['水位(m)'].mean()
        max_flow = df['流量(m³/s)'].max()
        
        print(f"数据行数: {len(df)}")
        print(f"平均水位: {mean_level:.2f} m")
        print(f"最大流量: {max_flow:.0f} m³/s")
        print("✅ 数据处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据处理测试失败: {e}")
        return False


def main():
    """主函数"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "Python环境测试" + " "*18 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # 运行所有测试
    tests = [
        ("Python版本", test_python_version),
        ("核心库导入", test_imports),
        ("基础计算", test_basic_calculation),
        ("绘图功能", test_plotting),
        ("数据处理", test_data_processing)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n测试 '{name}' 出错: {e}")
            results[name] = False
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12} {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！环境配置正确！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查环境配置")
        print("\n安装建议:")
        print("  pip install numpy matplotlib pandas scipy sympy jupyter")
        return 1


if __name__ == "__main__":
    sys.exit(main())
