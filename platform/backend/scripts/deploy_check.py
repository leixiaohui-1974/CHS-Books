#!/usr/bin/env python3
"""
部署前检查脚本
验证系统配置、依赖、环境变量等是否就绪

使用方法:
    python3 -m scripts.deploy_check
"""

import sys
import os
from pathlib import Path
from loguru import logger
import subprocess

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class DeploymentChecker:
    """部署检查器"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
    
    def check(self, name: str, condition: bool, error_msg: str = "", is_warning: bool = False):
        """执行检查"""
        if condition:
            logger.success(f"✅ {name}")
            self.checks_passed += 1
            return True
        else:
            if is_warning:
                logger.warning(f"⚠️  {name}: {error_msg}")
                self.warnings += 1
            else:
                logger.error(f"❌ {name}: {error_msg}")
                self.checks_failed += 1
            return False
    
    def check_python_version(self):
        """检查Python版本"""
        logger.info("\n📌 检查Python环境...")
        
        version = sys.version_info
        is_valid = version.major == 3 and version.minor >= 11
        
        self.check(
            "Python版本",
            is_valid,
            f"需要Python 3.11+，当前版本: {version.major}.{version.minor}.{version.micro}"
        )
    
    def check_dependencies(self):
        """检查依赖包"""
        logger.info("\n📌 检查依赖包...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "loguru",
            "pytest",
            "psutil",
            "prometheus_client"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.check(f"依赖包: {package}", True)
            except ImportError:
                self.check(f"依赖包: {package}", False, "未安装")
    
    def check_environment_variables(self):
        """检查环境变量"""
        logger.info("\n📌 检查环境变量...")
        
        # 必需的环境变量
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
        ]
        
        for var in required_vars:
            exists = os.getenv(var) is not None
            self.check(
                f"环境变量: {var}",
                exists,
                "未设置",
                is_warning=True  # 环境变量可能在.env文件中
            )
    
    def check_database_connection(self):
        """检查数据库连接"""
        logger.info("\n📌 检查数据库连接...")
        
        try:
            from app.core.config import settings
            
            # 检查DATABASE_URL是否配置
            has_db_url = bool(settings.DATABASE_URL)
            self.check(
                "数据库URL配置",
                has_db_url,
                "DATABASE_URL未配置"
            )
            
        except Exception as e:
            self.check("数据库配置", False, str(e))
    
    def check_directory_structure(self):
        """检查目录结构"""
        logger.info("\n📌 检查目录结构...")
        
        base_path = Path(__file__).parent.parent
        
        required_dirs = [
            "app",
            "app/api",
            "app/models",
            "app/services",
            "app/core",
            "tests",
            "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            self.check(
                f"目录: {dir_name}",
                dir_path.exists() and dir_path.is_dir(),
                "目录不存在"
            )
    
    def check_critical_files(self):
        """检查关键文件"""
        logger.info("\n📌 检查关键文件...")
        
        base_path = Path(__file__).parent.parent
        
        critical_files = [
            "app/main.py",
            "app/core/config.py",
            "app/core/database.py",
            "app/core/security.py",
            "requirements.txt",
            ".env.example"
        ]
        
        for file_name in critical_files:
            file_path = base_path / file_name
            self.check(
                f"文件: {file_name}",
                file_path.exists() and file_path.is_file(),
                "文件不存在"
            )
    
    def check_code_quality(self):
        """检查代码质量工具"""
        logger.info("\n📌 检查代码质量工具...")
        
        tools = ["black", "isort", "flake8", "mypy"]
        
        for tool in tools:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                text=True
            )
            self.check(
                f"代码质量工具: {tool}",
                result.returncode == 0,
                "未安装",
                is_warning=True
            )
    
    def check_docker(self):
        """检查Docker环境"""
        logger.info("\n📌 检查Docker环境...")
        
        # 检查docker命令
        result = subprocess.run(
            ["which", "docker"],
            capture_output=True,
            text=True
        )
        
        self.check(
            "Docker",
            result.returncode == 0,
            "Docker未安装",
            is_warning=True
        )
        
        # 检查docker-compose
        result = subprocess.run(
            ["which", "docker-compose"],
            capture_output=True,
            text=True
        )
        
        self.check(
            "Docker Compose",
            result.returncode == 0,
            "Docker Compose未安装",
            is_warning=True
        )
    
    def run_all_checks(self):
        """运行所有检查"""
        logger.info("=" * 80)
        logger.info("🚀 部署前检查开始...")
        logger.info("=" * 80)
        
        self.check_python_version()
        self.check_dependencies()
        self.check_environment_variables()
        self.check_database_connection()
        self.check_directory_structure()
        self.check_critical_files()
        self.check_code_quality()
        self.check_docker()
        
        # 汇总结果
        logger.info("\n" + "=" * 80)
        logger.info("📊 检查结果汇总")
        logger.info("=" * 80)
        logger.info(f"✅ 通过: {self.checks_passed}")
        logger.info(f"❌ 失败: {self.checks_failed}")
        logger.info(f"⚠️  警告: {self.warnings}")
        
        total = self.checks_passed + self.checks_failed + self.warnings
        success_rate = (self.checks_passed / total * 100) if total > 0 else 0
        
        logger.info(f"📈 通过率: {success_rate:.1f}%")
        
        if self.checks_failed == 0:
            logger.success("\n🎉 所有关键检查通过！系统可以部署！")
            return 0
        else:
            logger.error(f"\n❌ 有 {self.checks_failed} 项检查失败，请修复后再部署！")
            return 1


def main():
    """主函数"""
    checker = DeploymentChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
