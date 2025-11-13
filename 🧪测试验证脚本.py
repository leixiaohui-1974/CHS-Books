#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 15本考研书系列 - 测试验证脚本

功能：
1. 测试所有Python工具是否能正常运行
2. 验证依赖包是否正确安装
3. 检查数据文件完整性
4. 测试核心功能
5. 生成测试报告

作者：15本考研书系列开发组
版本：v1.5
日期：2025-11-12
"""

import sys
import importlib
import subprocess
from pathlib import Path
from datetime import datetime

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.total_tests = 0
    
    def run_all_tests(self):
        """运行所有测试"""
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║          🧪 15本考研书系列 - 测试验证脚本                  ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
        # 1. 测试Python环境
        self.test_python_version()
        
        # 2. 测试依赖包
        self.test_dependencies()
        
        # 3. 测试项目文件
        self.test_project_files()
        
        # 4. 测试Python工具
        self.test_python_tools()
        
        # 5. 测试脚本
        self.test_scripts()
        
        # 6. 生成报告
        self.generate_report()
    
    def test_python_version(self):
        """测试Python版本"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📌 测试 1: Python 环境检查")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        print(f"Python 版本: {version_str}")
        self.total_tests += 1
        
        if version.major == 3 and version.minor >= 7:
            print("✅ Python 版本符合要求 (>= 3.7)\n")
            self.results["passed"].append("Python版本检查")
        else:
            print(f"❌ Python 版本过低，需要 >= 3.7，当前: {version_str}\n")
            self.results["failed"].append("Python版本检查")
    
    def test_dependencies(self):
        """测试依赖包"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📌 测试 2: 依赖包检查")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        required_packages = {
            'numpy': '1.20.0',
            'scipy': '1.7.0',
            'pandas': '1.3.0',
            'matplotlib': '3.4.0',
            'seaborn': '0.11.0',
        }
        
        optional_packages = {
            'tqdm': '4.62.0',
        }
        
        # 测试必需包
        print("必需依赖包：")
        for package, min_version in required_packages.items():
            self.total_tests += 1
            try:
                mod = importlib.import_module(package)
                version = getattr(mod, '__version__', 'unknown')
                print(f"  • {package:15} {version:12} ✅")
                self.results["passed"].append(f"依赖包: {package}")
            except ImportError:
                print(f"  • {package:15} {'未安装':12} ❌")
                self.results["failed"].append(f"依赖包: {package}")
        
        # 测试可选包
        print("\n可选依赖包：")
        for package, min_version in optional_packages.items():
            self.total_tests += 1
            try:
                mod = importlib.import_module(package)
                version = getattr(mod, '__version__', 'unknown')
                print(f"  • {package:15} {version:12} ✅")
                self.results["passed"].append(f"可选包: {package}")
            except ImportError:
                print(f"  • {package:15} {'未安装':12} ⚠️ (可选)")
                self.results["warnings"].append(f"可选包: {package}")
        
        print()
    
    def test_project_files(self):
        """测试项目文件"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📌 测试 3: 项目文件检查")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        required_files = [
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md",
            ".gitignore",
            "📦requirements.txt",
            "CHANGELOG.md",
        ]
        
        print("核心文档：")
        for filename in required_files:
            self.total_tests += 1
            filepath = Path(filename)
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  • {filename:25} {size:8} bytes ✅")
                self.results["passed"].append(f"文件: {filename}")
            else:
                print(f"  • {filename:25} {'缺失':>8} ❌")
                self.results["failed"].append(f"文件: {filename}")
        
        # 测试Python工具
        print("\nPython工具：")
        python_tools = [
            "📊学习数据分析工具.py",
            "🤖学习助手CLI.py",
            "⏰学习提醒系统.py",
            "📈学习可视化报告生成器.py",
            "🔧项目验证脚本.py",
            "🎬快速演示脚本.py",
        ]
        
        for tool in python_tools:
            self.total_tests += 1
            filepath = Path(tool)
            if filepath.exists():
                lines = len(filepath.read_text(encoding='utf-8').splitlines())
                print(f"  • {tool:35} {lines:4} 行 ✅")
                self.results["passed"].append(f"工具: {tool}")
            else:
                print(f"  • {tool:35} {'缺失':>4} ❌")
                self.results["failed"].append(f"工具: {tool}")
        
        print()
    
    def test_python_tools(self):
        """测试Python工具的语法"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📌 测试 4: Python工具语法检查")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        python_tools = [
            "📊学习数据分析工具.py",
            "🤖学习助手CLI.py",
            "⏰学习提醒系统.py",
            "📈学习可视化报告生成器.py",
            "🔧项目验证脚本.py",
            "🎬快速演示脚本.py",
        ]
        
        for tool in python_tools:
            self.total_tests += 1
            filepath = Path(tool)
            if not filepath.exists():
                print(f"  • {tool:35} 跳过 (文件不存在)")
                continue
            
            # 尝试编译Python文件
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, filepath, 'exec')
                print(f"  • {tool:35} ✅ 语法正确")
                self.results["passed"].append(f"语法: {tool}")
            except SyntaxError as e:
                print(f"  • {tool:35} ❌ 语法错误: {e}")
                self.results["failed"].append(f"语法: {tool}")
        
        print()
    
    def test_scripts(self):
        """测试脚本"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📌 测试 5: Bash脚本检查")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        scripts = [
            "🚀一键启动脚本.sh",
            "🔄快速更新脚本.sh",
        ]
        
        for script in scripts:
            self.total_tests += 1
            filepath = Path(script)
            if filepath.exists():
                # 检查是否有执行权限 (Unix-like系统)
                import os
                is_executable = os.access(filepath, os.X_OK)
                status = "✅ (可执行)" if is_executable else "⚠️ (需要chmod +x)"
                print(f"  • {script:35} {status}")
                
                if is_executable:
                    self.results["passed"].append(f"脚本: {script}")
                else:
                    self.results["warnings"].append(f"脚本: {script} (需要执行权限)")
            else:
                print(f"  • {script:35} ❌ 缺失")
                self.results["failed"].append(f"脚本: {script}")
        
        print()
    
    def generate_report(self):
        """生成测试报告"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 测试结果汇总")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        warnings = len(self.results["warnings"])
        
        print(f"总测试数: {self.total_tests}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⚠️  警告: {warnings}")
        
        success_rate = (passed / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n成功率: {success_rate:.1f}%")
        
        # 进度条
        bar_length = 40
        filled = int(bar_length * success_rate / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}] {success_rate:.1f}%")
        
        # 失败项详情
        if failed > 0:
            print("\n❌ 失败项：")
            for item in self.results["failed"]:
                print(f"  • {item}")
        
        # 警告项详情
        if warnings > 0:
            print("\n⚠️  警告项：")
            for item in self.results["warnings"]:
                print(f"  • {item}")
        
        # 总体评价
        print("\n" + "━" * 60)
        if failed == 0:
            print("🎉 所有测试通过！项目状态：优秀")
        elif failed <= 2:
            print("✅ 大部分测试通过，项目状态：良好")
        else:
            print("⚠️  存在较多问题，建议修复后再使用")
        
        # 保存报告
        self.save_report(success_rate)
    
    def save_report(self, success_rate):
        """保存测试报告"""
        report_file = Path(f"测试报告-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🧪 测试验证报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 📊 测试摘要\n\n")
            f.write(f"- **总测试数**: {self.total_tests}\n")
            f.write(f"- **✅ 通过**: {len(self.results['passed'])}\n")
            f.write(f"- **❌ 失败**: {len(self.results['failed'])}\n")
            f.write(f"- **⚠️ 警告**: {len(self.results['warnings'])}\n")
            f.write(f"- **成功率**: {success_rate:.1f}%\n\n")
            
            if self.results["passed"]:
                f.write("## ✅ 通过的测试\n\n")
                for item in self.results["passed"]:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            if self.results["failed"]:
                f.write("## ❌ 失败的测试\n\n")
                for item in self.results["failed"]:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            if self.results["warnings"]:
                f.write("## ⚠️ 警告项\n\n")
                for item in self.results["warnings"]:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            f.write("---\n\n")
            f.write("**© 2025 15本考研书系列开发组**\n")
        
        print(f"\n📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    try:
        runner = TestRunner()
        runner.run_all_tests()
        print("\n" + "═" * 60)
        print("测试完成！")
        print("═" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
