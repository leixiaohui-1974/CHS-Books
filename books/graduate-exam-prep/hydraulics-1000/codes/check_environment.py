#!/usr/bin/env python3
"""
环境检查工具 - Environment Check Tool
检查Python环境和依赖包是否正确安装

使用方法：python3 check_environment.py
"""

import sys
import os

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def check_python_version():
    """检查Python版本"""
    print("\n【Python版本检查】")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Python版本符合要求 (>= 3.8)")
        return True
    else:
        print("✗ Python版本过低，需要 >= 3.8")
        print(f"  当前版本: {version.major}.{version.minor}")
        return False

def check_package(package_name, import_name=None):
    """检查单个包"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', '未知')
        print(f"✓ {package_name:15s} 已安装 (版本: {version})")
        return True
    except ImportError:
        print(f"✗ {package_name:15s} 未安装")
        return False

def check_packages():
    """检查所有依赖包"""
    print("\n【依赖包检查】")
    
    packages = [
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('matplotlib', 'matplotlib'),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed

def check_codes_directory():
    """检查代码目录"""
    print("\n【代码目录检查】")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"当前目录: {current_dir}")
    
    # 检查是否有代码文件
    py_files = [f for f in os.listdir(current_dir) if f.startswith('problem_') and f.endswith('.py')]
    
    if py_files:
        print(f"✓ 找到 {len(py_files)} 个代码文件")
        # 显示前5个
        print("  示例文件:")
        for f in sorted(py_files)[:5]:
            print(f"    - {f}")
        if len(py_files) > 5:
            print(f"    ... 还有 {len(py_files)-5} 个文件")
        return True
    else:
        print("✗ 未找到代码文件")
        return False

def test_import_code():
    """测试导入代码"""
    print("\n【代码导入测试】")
    
    # 尝试导入一个示例代码
    test_files = [
        'problem_904_integrated_water_project',
        'problem_791_pump_operation',
        'problem_001_hydrostatic_pressure'
    ]
    
    success = False
    for module_name in test_files:
        try:
            # 尝试导入
            module = __import__(module_name)
            print(f"✓ 成功导入 {module_name}")
            success = True
            break
        except ImportError as e:
            print(f"✗ 无法导入 {module_name}: {e}")
            continue
        except Exception as e:
            print(f"⚠ 导入 {module_name} 时出错: {e}")
            continue
    
    return success

def test_numpy_operations():
    """测试NumPy基本操作"""
    print("\n【NumPy功能测试】")
    
    try:
        import numpy as np
        
        # 创建数组
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✓ 数组创建: {arr}")
        
        # 数学运算
        result = np.sqrt(arr)
        print(f"✓ 数学运算: √arr = {result}")
        
        # 线性代数
        x = np.linspace(0, 10, 5)
        print(f"✓ linspace: {x}")
        
        return True
    except Exception as e:
        print(f"✗ NumPy测试失败: {e}")
        return False

def test_matplotlib():
    """测试Matplotlib"""
    print("\n【Matplotlib功能测试】")
    
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 检查后端
        backend = matplotlib.get_backend()
        print(f"✓ Matplotlib后端: {backend}")
        
        # 检查中文字体
        fonts = matplotlib.font_manager.findSystemFonts()
        chinese_fonts = [f for f in fonts if 'SimHei' in f or 'Arial' in f or 'Microsoft' in f]
        if chinese_fonts:
            print(f"✓ 找到 {len(chinese_fonts)} 个中文字体")
        else:
            print("⚠ 未找到推荐的中文字体，可能显示中文时出现方框")
        
        return True
    except Exception as e:
        print(f"✗ Matplotlib测试失败: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*60)
    print("【安装建议】")
    print("="*60)
    
    print("\n如果检查未通过，请执行以下命令：")
    print("\n方法1：使用pip安装")
    print("  pip install numpy scipy matplotlib")
    
    print("\n方法2：使用requirements.txt")
    print("  pip install -r requirements.txt")
    
    print("\n方法3：使用conda（推荐给初学者）")
    print("  conda install numpy scipy matplotlib")
    
    print("\n如果Python版本过低：")
    print("  - Mac: brew install python3")
    print("  - Ubuntu: sudo apt install python3")
    print("  - Windows: 从 python.org 下载安装")

def main():
    """主函数"""
    print_header("《水力学1000题详解》环境检查工具")
    print("Environment Check Tool for Hydraulics-1000")
    
    results = []
    
    # 检查Python版本
    results.append(("Python版本", check_python_version()))
    
    # 检查依赖包
    results.append(("依赖包", check_packages()))
    
    # 检查代码目录
    results.append(("代码目录", check_codes_directory()))
    
    # 测试导入
    results.append(("代码导入", test_import_code()))
    
    # 测试NumPy
    results.append(("NumPy功能", test_numpy_operations()))
    
    # 测试Matplotlib
    results.append(("Matplotlib", test_matplotlib()))
    
    # 总结
    print("\n" + "="*60)
    print("【检查结果汇总】")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 未通过"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 恭喜！所有检查都通过了！")
        print("您可以开始使用代码库了。")
        print("\n快速开始：")
        print("  python3 problem_904_integrated_water_project.py")
    else:
        print("⚠️  部分检查未通过")
        print("请参考下面的安装建议进行修复。")
        provide_solutions()
    
    print("="*60)

if __name__ == "__main__":
    main()
