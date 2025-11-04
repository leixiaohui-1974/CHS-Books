#!/usr/bin/env python3
"""
系统诊断工具
自动诊断系统问题并提供解决方案
"""

import os
import sys
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
import json


class DiagnosticTool:
    """诊断工具"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
    
    def add_issue(self, title: str, description: str, solution: str):
        """添加问题"""
        self.issues.append({
            'title': title,
            'description': description,
            'solution': solution
        })
    
    def add_warning(self, title: str, description: str):
        """添加警告"""
        self.warnings.append({
            'title': title,
            'description': description
        })
    
    def add_info(self, title: str, value: str):
        """添加信息"""
        self.info.append({
            'title': title,
            'value': value
        })
    
    def check_python_version(self):
        """检查Python版本"""
        print("🔍 检查Python版本...", end=" ")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        self.add_info("Python版本", version_str)
        
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            self.add_issue(
                "Python版本过低",
                f"当前版本: {version_str}, 推荐版本: 3.11+",
                "升级Python: sudo apt install python3.11"
            )
            print("⚠️")
        else:
            print("✓")
    
    def check_disk_space(self):
        """检查磁盘空间"""
        print("🔍 检查磁盘空间...", end=" ")
        
        disk = psutil.disk_usage('/')
        percent = disk.percent
        free_gb = disk.free / (1024**3)
        
        self.add_info("磁盘使用", f"{percent:.1f}% ({free_gb:.1f}GB 可用)")
        
        if percent > 90:
            self.add_issue(
                "磁盘空间不足",
                f"磁盘使用率: {percent:.1f}%",
                "清理磁盘空间: sudo apt clean && docker system prune"
            )
            print("⚠️")
        elif percent > 80:
            self.add_warning(
                "磁盘空间偏低",
                f"磁盘使用率: {percent:.1f}%"
            )
            print("⚠️")
        else:
            print("✓")
    
    def check_memory(self):
        """检查内存"""
        print("🔍 检查内存...", end=" ")
        
        memory = psutil.virtual_memory()
        percent = memory.percent
        available_gb = memory.available / (1024**3)
        
        self.add_info("内存使用", f"{percent:.1f}% ({available_gb:.1f}GB 可用)")
        
        if percent > 90:
            self.add_issue(
                "内存不足",
                f"内存使用率: {percent:.1f}%",
                "增加内存或优化程序"
            )
            print("⚠️")
        elif percent > 80:
            self.add_warning(
                "内存使用偏高",
                f"内存使用率: {percent:.1f}%"
            )
            print("⚠️")
        else:
            print("✓")
    
    def check_docker(self):
        """检查Docker"""
        print("🔍 检查Docker...", end=" ")
        
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.add_info("Docker", version)
                print("✓")
            else:
                self.add_issue(
                    "Docker不可用",
                    "Docker命令执行失败",
                    "安装Docker: https://docs.docker.com/get-docker/"
                )
                print("✗")
        
        except FileNotFoundError:
            self.add_issue(
                "Docker未安装",
                "系统中未找到Docker",
                "安装Docker: https://docs.docker.com/get-docker/"
            )
            print("✗")
        
        except Exception as e:
            self.add_warning("Docker检查失败", str(e))
            print("⚠️")
    
    def check_dependencies(self):
        """检查Python依赖"""
        print("🔍 检查Python依赖...", end=" ")
        
        required_packages = [
            'fastapi',
            'sqlalchemy',
            'redis',
            'pymongo',
            'openai',
            'docker',
            'pytest'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.add_issue(
                "缺少依赖包",
                f"缺少: {', '.join(missing)}",
                "安装依赖: pip install -r requirements.txt"
            )
            print("⚠️")
        else:
            self.add_info("Python依赖", "所有核心包已安装")
            print("✓")
    
    def check_files(self):
        """检查关键文件"""
        print("🔍 检查关键文件...", end=" ")
        
        backend_dir = Path(__file__).parent
        platform_dir = backend_dir.parent
        
        required_files = [
            backend_dir / "requirements.txt",
            platform_dir / "docker-compose.v2.yml",
            platform_dir / "README_V2.md",
        ]
        
        missing = []
        for file in required_files:
            if not file.exists():
                missing.append(file.name)
        
        if missing:
            self.add_warning(
                "缺少文件",
                f"缺少: {', '.join(missing)}"
            )
            print("⚠️")
        else:
            self.add_info("关键文件", "完整")
            print("✓")
    
    def check_ports(self):
        """检查端口占用"""
        print("🔍 检查端口占用...", end=" ")
        
        critical_ports = [8000, 5432, 6379, 27017]
        occupied = []
        
        for port in critical_ports:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    occupied.append(port)
                    break
        
        if occupied:
            self.add_info("已占用端口", ', '.join(map(str, occupied)))
            print("ℹ️")
        else:
            self.add_info("端口状态", "所有关键端口可用")
            print("✓")
    
    def check_env_file(self):
        """检查环境配置"""
        print("🔍 检查环境配置...", end=" ")
        
        env_file = Path(__file__).parent / ".env"
        
        if not env_file.exists():
            self.add_warning(
                "缺少配置文件",
                "未找到.env文件，使用配置向导创建: python3 setup_wizard.py"
            )
            print("⚠️")
        else:
            self.add_info("环境配置", "已配置")
            print("✓")
    
    def generate_report(self):
        """生成诊断报告"""
        print("\n" + "=" * 70)
        print(" 系统诊断报告")
        print("=" * 70)
        print()
        
        # 系统信息
        if self.info:
            print("📋 系统信息:")
            print("-" * 70)
            for item in self.info:
                print(f"  {item['title']}: {item['value']}")
            print()
        
        # 问题
        if self.issues:
            print("❌ 发现的问题:")
            print("-" * 70)
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue['title']}")
                print(f"     问题: {issue['description']}")
                print(f"     解决: {issue['solution']}")
                print()
        
        # 警告
        if self.warnings:
            print("⚠️  警告:")
            print("-" * 70)
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning['title']}")
                print(f"     {warning['description']}")
            print()
        
        # 总结
        print("=" * 70)
        if not self.issues and not self.warnings:
            print("✅ 系统状态良好，未发现问题")
        else:
            issue_count = len(self.issues)
            warning_count = len(self.warnings)
            print(f"发现 {issue_count} 个问题, {warning_count} 个警告")
            
            if self.issues:
                print("\n建议按优先级解决问题:")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue['solution']}")
        
        print("=" * 70)
    
    def export_json(self, output_file: str):
        """导出JSON报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'info': self.info,
            'issues': self.issues,
            'warnings': self.warnings,
            'summary': {
                'issue_count': len(self.issues),
                'warning_count': len(self.warnings)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 报告已导出: {output_file}")
    
    def run_diagnostics(self):
        """运行所有诊断"""
        print("=" * 70)
        print(" 智能知识平台 - 系统诊断工具")
        print("=" * 70)
        print()
        
        # 运行各项检查
        self.check_python_version()
        self.check_disk_space()
        self.check_memory()
        self.check_docker()
        self.check_dependencies()
        self.check_files()
        self.check_ports()
        self.check_env_file()
        
        # 生成报告
        self.generate_report()
        
        # 导出JSON
        output_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.export_json(output_file)


def main():
    """主函数"""
    tool = DiagnosticTool()
    tool.run_diagnostics()


if __name__ == "__main__":
    main()
