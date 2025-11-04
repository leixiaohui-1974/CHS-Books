#!/usr/bin/env python3
"""
CI/CD集成脚本
自动化构建、测试和部署流程
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class CICDPipeline:
    """CI/CD管道"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.results = []
        self.start_time = None
    
    def log(self, message: str, level: str = "info"):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level == "success":
            print(f"{Colors.GREEN}[{timestamp}] ✓ {message}{Colors.END}")
        elif level == "error":
            print(f"{Colors.RED}[{timestamp}] ✗ {message}{Colors.END}")
        elif level == "warning":
            print(f"{Colors.YELLOW}[{timestamp}] ⚠ {message}{Colors.END}")
        elif level == "info":
            print(f"{Colors.BLUE}[{timestamp}] ℹ {message}{Colors.END}")
        else:
            print(f"[{timestamp}] {message}")
    
    def run_command(self, cmd: str, description: str, cwd: Path = None, timeout: int = 300) -> bool:
        """运行命令"""
        self.log(f"执行: {description}...", "info")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                timeout=timeout
            )
            
            success = result.returncode == 0
            
            self.results.append({
                'stage': description,
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout[:500],
                'stderr': result.stderr[:500]
            })
            
            if success:
                self.log(f"{description} 成功", "success")
            else:
                self.log(f"{description} 失败 (返回码: {result.returncode})", "error")
                if result.stderr:
                    print(f"  错误: {result.stderr[:200]}")
            
            return success
        
        except subprocess.TimeoutExpired:
            self.log(f"{description} 超时", "error")
            self.results.append({
                'stage': description,
                'success': False,
                'error': 'timeout'
            })
            return False
        
        except Exception as e:
            self.log(f"{description} 异常: {e}", "error")
            self.results.append({
                'stage': description,
                'success': False,
                'error': str(e)
            })
            return False
    
    def stage_checkout(self) -> bool:
        """阶段1: 代码检出"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 1/7: 代码检出{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 检查Git状态
        return self.run_command(
            "git status",
            "检查Git状态"
        )
    
    def stage_dependencies(self) -> bool:
        """阶段2: 依赖安装"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 2/7: 依赖检查{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 检查Python版本
        if not self.run_command(
            "python3 --version",
            "检查Python版本"
        ):
            return False
        
        # 检查requirements.txt
        req_file = self.backend_dir / "requirements.txt"
        if not req_file.exists():
            self.log("requirements.txt不存在", "error")
            return False
        
        self.log("依赖文件存在", "success")
        return True
    
    def stage_lint(self) -> bool:
        """阶段3: 代码检查"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 3/7: 代码质量检查{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 运行代码质量检查
        return self.run_command(
            "python3 code_quality.py",
            "代码质量检查",
            cwd=self.backend_dir
        )
    
    def stage_security(self) -> bool:
        """阶段4: 安全扫描"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 4/7: 安全扫描{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 运行安全扫描
        success = self.run_command(
            "python3 security_scanner.py",
            "安全漏洞扫描",
            cwd=self.backend_dir,
            timeout=60
        )
        
        # 安全扫描即使发现问题也继续（非阻断）
        if not success:
            self.log("安全扫描发现问题，但不阻断流程", "warning")
        
        return True
    
    def stage_test(self) -> bool:
        """阶段5: 运行测试"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 5/7: 自动化测试{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 运行简单测试
        if not self.run_command(
            "python3 simple_test.py",
            "快速测试",
            cwd=self.backend_dir
        ):
            return False
        
        # 运行集成测试
        if not self.run_command(
            "python3 integration_test_suite.py",
            "集成测试",
            cwd=self.backend_dir
        ):
            return False
        
        # 运行工具测试
        if not self.run_command(
            "python3 test_all_tools.py",
            "工具测试",
            cwd=self.backend_dir
        ):
            self.log("部分工具测试失败，但不阻断流程", "warning")
        
        return True
    
    def stage_build(self) -> bool:
        """阶段6: 构建"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 6/7: 构建镜像{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 检查Docker
        if not self.run_command(
            "docker --version",
            "检查Docker",
            timeout=10
        ):
            self.log("Docker未安装，跳过镜像构建", "warning")
            return True
        
        # 构建Docker镜像（如果需要）
        dockerfile = self.backend_dir / "Dockerfile.enhanced"
        if dockerfile.exists():
            self.log("发现Dockerfile，可以构建镜像", "info")
        
        return True
    
    def stage_deploy(self) -> bool:
        """阶段7: 部署"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}阶段 7/7: 部署检查{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 运行系统诊断
        self.run_command(
            "python3 system_diagnostics.py",
            "系统诊断",
            cwd=self.backend_dir
        )
        
        # 运行健康检查
        self.run_command(
            "python3 health_check.py",
            "健康检查",
            cwd=self.backend_dir
        )
        
        self.log("部署检查完成", "info")
        return True
    
    def generate_report(self):
        """生成报告"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}CI/CD 执行报告{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 统计
        total = len(self.results)
        passed = len([r for r in self.results if r['success']])
        failed = total - passed
        
        # 执行时间
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时:   {duration:.2f}秒")
        print()
        
        print(f"执行阶段: {total}")
        print(f"成功:     {passed}")
        print(f"失败:     {failed}")
        print(f"成功率:   {passed/total*100:.1f}%")
        print()
        
        # 详细结果
        print("详细结果:")
        print("-" * 70)
        
        for i, result in enumerate(self.results, 1):
            status = "✓" if result['success'] else "✗"
            color = Colors.GREEN if result['success'] else Colors.RED
            print(f"  {i}. [{color}{status}{Colors.END}] {result['stage']}")
        
        print()
        print("=" * 70)
        
        if failed == 0:
            print(f"{Colors.GREEN}✅ CI/CD流程执行成功！{Colors.END}")
        else:
            print(f"{Colors.RED}❌ CI/CD流程执行失败 ({failed}个阶段失败){Colors.END}")
        
        print("=" * 70)
        
        return failed == 0
    
    def run_pipeline(self) -> bool:
        """运行完整管道"""
        self.start_time = datetime.now()
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}智能知识平台 - CI/CD 管道{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        # 执行各阶段
        stages = [
            self.stage_checkout,
            self.stage_dependencies,
            self.stage_lint,
            self.stage_security,
            self.stage_test,
            self.stage_build,
            self.stage_deploy
        ]
        
        for stage in stages:
            if not stage():
                self.log(f"阶段失败，停止管道", "error")
                break
            time.sleep(1)  # 短暂延迟
        
        # 生成报告
        return self.generate_report()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD集成脚本')
    parser.add_argument('--stage', 
                       choices=['checkout', 'deps', 'lint', 'security', 'test', 'build', 'deploy', 'all'],
                       default='all',
                       help='执行的阶段')
    
    args = parser.parse_args()
    
    pipeline = CICDPipeline()
    
    if args.stage == 'all':
        success = pipeline.run_pipeline()
    else:
        # 执行单个阶段
        stage_map = {
            'checkout': pipeline.stage_checkout,
            'deps': pipeline.stage_dependencies,
            'lint': pipeline.stage_lint,
            'security': pipeline.stage_security,
            'test': pipeline.stage_test,
            'build': pipeline.stage_build,
            'deploy': pipeline.stage_deploy
        }
        
        success = stage_map[args.stage]()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
