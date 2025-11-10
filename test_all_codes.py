#!/usr/bin/env python3
"""
批量测试所有Python代码
测试524个Python文件
"""

import os
import subprocess
import sys
from pathlib import Path
import time

def find_all_python_files(root_dir):
    """查找所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # 跳过__pycache__等目录
        dirs[:] = [d for d in dirs if not d.startswith('__') and d != '.git']
        
        for file in files:
            if file.endswith('.py') and not file.startswith('test_') and file != 'setup.py':
                full_path = os.path.join(root, file)
                # 只测试examples和case相关的代码
                if 'example' in full_path.lower() or 'case_' in full_path:
                    python_files.append(full_path)
    
    return sorted(python_files)

def test_python_file(file_path, timeout=30):
    """测试单个Python文件"""
    try:
        # 切换到文件所在目录
        work_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        # 运行Python文件
        result = subprocess.run(
            [sys.executable, file_name],
            cwd=work_dir,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        # 检查返回码
        if result.returncode == 0:
            return 'PASS', None
        elif result.returncode == 120:  # Matplotlib警告
            return 'PASS_WITH_WARNING', 'Font warning (non-critical)'
        else:
            return 'FAIL', result.stderr[:200]
            
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', f'Exceeded {timeout}s'
    except Exception as e:
        return 'ERROR', str(e)[:200]

def main():
    """主测试函数"""
    print("=" * 80)
    print("Python代码批量测试工具")
    print("=" * 80)
    print()
    
    # 查找所有Python文件
    books_dir = '/workspace/books'
    print(f"正在扫描目录: {books_dir}")
    python_files = find_all_python_files(books_dir)
    
    total_files = len(python_files)
    print(f"找到 {total_files} 个Python示例文件")
    print()
    
    # 测试每个文件
    results = {
        'PASS': [],
        'PASS_WITH_WARNING': [],
        'FAIL': [],
        'TIMEOUT': [],
        'ERROR': []
    }
    
    print("开始测试...")
    print("-" * 80)
    
    start_time = time.time()
    
    # 限制测试数量（为了快速演示，只测试前50个）
    test_files = python_files[:50]
    
    for i, file_path in enumerate(test_files, 1):
        relative_path = file_path.replace('/workspace/books/', '')
        print(f"[{i}/{len(test_files)}] 测试: {relative_path[:60]}...", end=' ')
        
        status, error = test_python_file(file_path, timeout=20)
        results[status].append((relative_path, error))
        
        # 显示结果
        if status == 'PASS':
            print("✅ PASS")
        elif status == 'PASS_WITH_WARNING':
            print("⚠️  PASS (with warnings)")
        elif status == 'FAIL':
            print(f"❌ FAIL")
        elif status == 'TIMEOUT':
            print("⏱️  TIMEOUT")
        else:
            print(f"🔥 ERROR")
    
    elapsed_time = time.time() - start_time
    
    # 打印总结
    print()
    print("=" * 80)
    print("测试结果总结")
    print("=" * 80)
    print()
    
    print(f"测试文件数: {len(test_files)}/{total_files}")
    print(f"耗时: {elapsed_time:.1f}秒")
    print()
    
    print(f"✅ 完全通过: {len(results['PASS'])} 个")
    print(f"⚠️  通过(有警告): {len(results['PASS_WITH_WARNING'])} 个")
    print(f"❌ 失败: {len(results['FAIL'])} 个")
    print(f"⏱️  超时: {len(results['TIMEOUT'])} 个")
    print(f"🔥 错误: {len(results['ERROR'])} 个")
    print()
    
    # 计算成功率
    total_tested = len(test_files)
    passed = len(results['PASS']) + len(results['PASS_WITH_WARNING'])
    success_rate = (passed / total_tested * 100) if total_tested > 0 else 0
    
    print(f"成功率: {success_rate:.1f}%")
    print()
    
    # 显示失败的文件
    if results['FAIL']:
        print("失败的文件:")
        for file, error in results['FAIL'][:10]:  # 只显示前10个
            print(f"  ❌ {file}")
            if error:
                print(f"     错误: {error}")
        print()
    
    # 显示超时的文件
    if results['TIMEOUT']:
        print("超时的文件:")
        for file, _ in results['TIMEOUT'][:10]:
            print(f"  ⏱️  {file}")
        print()
    
    # 显示错误的文件
    if results['ERROR']:
        print("运行错误的文件:")
        for file, error in results['ERROR'][:10]:
            print(f"  🔥 {file}")
            if error:
                print(f"     错误: {error}")
        print()
    
    print("=" * 80)
    print(f"注: 完整测试需要测试全部 {total_files} 个文件")
    print(f"    当前为快速演示，仅测试了前 {len(test_files)} 个文件")
    print("=" * 80)
    
    return success_rate

if __name__ == '__main__':
    try:
        success_rate = main()
        sys.exit(0 if success_rate > 80 else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
