"""
安装测试

检查必要的依赖包是否已安装
"""

import sys


def test_python_version():
    """测试Python版本"""
    assert sys.version_info >= (3, 9), "需要Python 3.9或更高版本"
    print(f"✓ Python版本: {sys.version}")


def test_import_numpy():
    """测试numpy"""
    try:
        import numpy as np
        print(f"✓ NumPy版本: {np.__version__}")
        return True
    except ImportError:
        print("✗ NumPy未安装")
        return False


def test_import_pandas():
    """测试pandas"""
    try:
        import pandas as pd
        print(f"✓ Pandas版本: {pd.__version__}")
        return True
    except ImportError:
        print("✗ Pandas未安装")
        return False


def test_import_matplotlib():
    """测试matplotlib"""
    try:
        import matplotlib
        print(f"✓ Matplotlib版本: {matplotlib.__version__}")
        return True
    except ImportError:
        print("✗ Matplotlib未安装")
        return False


def test_import_scipy():
    """测试scipy"""
    try:
        import scipy
        print(f"✓ SciPy版本: {scipy.__version__}")
        return True
    except ImportError:
        print("✗ SciPy未安装")
        return False


def test_import_pyyaml():
    """测试pyyaml"""
    try:
        import yaml
        print(f"✓ PyYAML已安装")
        return True
    except ImportError:
        print("✗ PyYAML未安装")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("检查开发环境")
    print("=" * 60)
    
    test_python_version()
    
    print("\n检查必要的依赖包:")
    print("-" * 60)
    
    results = []
    results.append(("NumPy", test_import_numpy()))
    results.append(("Pandas", test_import_pandas()))
    results.append(("Matplotlib", test_import_matplotlib()))
    results.append(("SciPy", test_import_scipy()))
    results.append(("PyYAML", test_import_pyyaml()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n通过: {success_count}/{total_count}")
    
    if success_count < total_count:
        print("\n缺少的依赖包可以通过以下命令安装:")
        print("pip install -r requirements.txt")
        print("\n或安装核心包:")
        print("pip install numpy pandas matplotlib scipy pyyaml")
        return False
    else:
        print("\n✓ 所有必要的依赖包已安装!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
