#!/usr/bin/env python3
"""
自动化部署脚本
简化部署流程，一键完成环境检查、服务启动、健康验证
"""

import subprocess
import sys
import time
from pathlib import Path
import json
from typing import List, Dict


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step: str):
    """打印步骤"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {step}{Colors.END}")


def print_success(msg: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def run_command(cmd: str, cwd: str = None, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"命令执行失败: {cmd}")
            print_error(f"错误: {e.stderr}")
            raise
        return e


class DeploymentManager:
    """部署管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.checks_passed = []
        self.checks_failed = []
    
    def check_docker(self) -> bool:
        """检查Docker是否安装"""
        print_step("1. 检查Docker环境")
        
        # 检查docker命令
        result = run_command("docker --version", check=False)
        if result.returncode != 0:
            print_error("Docker未安装")
            print("请访问 https://docs.docker.com/get-docker/ 安装Docker")
            return False
        
        print_success(f"Docker已安装: {result.stdout.strip()}")
        
        # 检查docker-compose命令
        result = run_command("docker-compose --version", check=False)
        if result.returncode != 0:
            print_error("docker-compose未安装")
            return False
        
        print_success(f"docker-compose已安装: {result.stdout.strip()}")
        
        # 检查Docker守护进程
        result = run_command("docker ps", check=False)
        if result.returncode != 0:
            print_error("Docker守护进程未运行")
            print("请启动Docker Desktop或运行: sudo systemctl start docker")
            return False
        
        print_success("Docker守护进程正常运行")
        self.checks_passed.append("Docker环境")
        return True
    
    def check_files(self) -> bool:
        """检查必要文件"""
        print_step("2. 检查项目文件")
        
        required_files = [
            "docker-compose.v2.yml",
            "backend/Dockerfile.enhanced",
            "backend/requirements.txt",
            "backend/app/main.py",
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print_error(f"缺少文件:")
            for f in missing_files:
                print(f"  - {f}")
            return False
        
        print_success(f"所有必要文件完整 ({len(required_files)}个)")
        self.checks_passed.append("项目文件")
        return True
    
    def check_ports(self) -> bool:
        """检查端口占用"""
        print_step("3. 检查端口占用")
        
        ports_to_check = [8000, 5432, 6379, 27017]
        occupied_ports = []
        
        for port in ports_to_check:
            # 在不同系统上检查端口的方式不同
            if sys.platform == 'darwin' or sys.platform.startswith('linux'):
                cmd = f"lsof -i :{port} -t"
            else:
                cmd = f"netstat -ano | findstr :{port}"
            
            result = run_command(cmd, check=False)
            if result.returncode == 0 and result.stdout.strip():
                occupied_ports.append(port)
        
        if occupied_ports:
            print_warning(f"以下端口被占用: {', '.join(map(str, occupied_ports))}")
            print("这些端口可能会导致冲突，是否继续？")
            response = input("继续部署? (y/n): ").lower()
            if response != 'y':
                return False
        else:
            print_success("所有端口可用")
        
        self.checks_passed.append("端口检查")
        return True
    
    def stop_existing_services(self):
        """停止现有服务"""
        print_step("4. 停止现有服务")
        
        result = run_command(
            "docker-compose -f docker-compose.v2.yml down",
            cwd=self.project_root,
            check=False
        )
        
        if result.returncode == 0:
            print_success("现有服务已停止")
        else:
            print_warning("没有运行中的服务")
    
    def build_images(self):
        """构建Docker镜像"""
        print_step("5. 构建Docker镜像")
        
        print("正在构建镜像，这可能需要几分钟...")
        
        result = run_command(
            "docker-compose -f docker-compose.v2.yml build",
            cwd=self.project_root,
            check=False
        )
        
        if result.returncode == 0:
            print_success("镜像构建完成")
            self.checks_passed.append("镜像构建")
        else:
            print_error("镜像构建失败")
            print(result.stderr)
            self.checks_failed.append("镜像构建")
            raise Exception("镜像构建失败")
    
    def start_services(self):
        """启动服务"""
        print_step("6. 启动服务")
        
        print("正在启动服务...")
        
        result = run_command(
            "docker-compose -f docker-compose.v2.yml up -d",
            cwd=self.project_root,
            check=False
        )
        
        if result.returncode == 0:
            print_success("服务已启动")
            self.checks_passed.append("服务启动")
        else:
            print_error("服务启动失败")
            print(result.stderr)
            self.checks_failed.append("服务启动")
            raise Exception("服务启动失败")
    
    def wait_for_services(self, timeout: int = 60):
        """等待服务就绪"""
        print_step("7. 等待服务就绪")
        
        print(f"等待服务启动（最多{timeout}秒）...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = run_command(
                "docker-compose -f docker-compose.v2.yml ps",
                cwd=self.project_root,
                check=False
            )
            
            if result.returncode == 0:
                # 简单判断：如果没有"Exit"状态的容器
                if "Exit" not in result.stdout:
                    time.sleep(5)  # 额外等待5秒确保完全就绪
                    print_success("服务已就绪")
                    self.checks_passed.append("服务就绪")
                    return True
            
            time.sleep(2)
            print(".", end="", flush=True)
        
        print()
        print_warning("服务启动超时，但可能仍在初始化中")
        return False
    
    def health_check(self):
        """健康检查"""
        print_step("8. 健康检查")
        
        # 检查API是否可访问
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print_success("API健康检查通过")
                self.checks_passed.append("健康检查")
                return True
        except Exception as e:
            print_warning(f"健康检查失败: {e}")
            print_warning("服务可能仍在初始化，请稍后手动验证")
            return False
    
    def show_info(self):
        """显示信息"""
        print_step("9. 部署信息")
        
        print(f"\n{Colors.BOLD}服务访问地址:{Colors.END}")
        print(f"  • API文档:    http://localhost:8000/docs")
        print(f"  • 健康检查:   http://localhost:8000/health")
        print(f"  • 系统信息:   http://localhost:8000/api/v1/system/info")
        
        print(f"\n{Colors.BOLD}常用命令:{Colors.END}")
        print(f"  • 查看日志:   docker-compose -f docker-compose.v2.yml logs -f")
        print(f"  • 查看状态:   docker-compose -f docker-compose.v2.yml ps")
        print(f"  • 停止服务:   docker-compose -f docker-compose.v2.yml down")
        print(f"  • 重启服务:   docker-compose -f docker-compose.v2.yml restart")
        
        print(f"\n{Colors.BOLD}管理工具:{Colors.END}")
        print(f"  • 管理CLI:    cd backend && ./manage.py --help")
        print(f"  • 健康检查:   cd backend && python3 health_check.py")
        print(f"  • 性能监控:   cd backend && python3 performance_monitor.py")
    
    def show_summary(self):
        """显示总结"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}部署总结{Colors.END}")
        print("=" * 70)
        
        if self.checks_passed:
            print(f"\n{Colors.GREEN}✓ 通过的检查:{Colors.END}")
            for check in self.checks_passed:
                print(f"  • {check}")
        
        if self.checks_failed:
            print(f"\n{Colors.RED}✗ 失败的检查:{Colors.END}")
            for check in self.checks_failed:
                print(f"  • {check}")
        
        print("\n" + "=" * 70)
        
        if not self.checks_failed:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ 部署成功！{Colors.END}")
            print(f"\n访问 {Colors.BLUE}http://localhost:8000/docs{Colors.END} 开始使用")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ 部署完成，但有警告{Colors.END}")
            print(f"\n请检查失败的项目，或查看日志获取更多信息")
    
    def deploy(self):
        """执行部署"""
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}智能知识平台 V2.0 - 自动化部署{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
        
        try:
            # 1. 环境检查
            if not self.check_docker():
                return False
            
            if not self.check_files():
                return False
            
            if not self.check_ports():
                return False
            
            # 2. 停止现有服务
            self.stop_existing_services()
            
            # 3. 构建和启动
            self.build_images()
            self.start_services()
            self.wait_for_services()
            
            # 4. 验证
            self.health_check()
            
            # 5. 显示信息
            self.show_info()
            self.show_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n部署已取消")
            return False
        except Exception as e:
            print_error(f"部署失败: {e}")
            self.show_summary()
            return False


def main():
    """主函数"""
    manager = DeploymentManager()
    success = manager.deploy()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
