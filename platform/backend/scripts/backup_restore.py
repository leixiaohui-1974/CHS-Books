"""
数据库备份与恢复脚本
支持PostgreSQL数据库的完整备份和恢复

使用方法:
    备份: python3 -m scripts.backup_restore backup [--output backup.sql]
    恢复: python3 -m scripts.backup_restore restore [--input backup.sql]
    列表: python3 -m scripts.backup_restore list
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


class DatabaseBackup:
    """数据库备份恢复工具"""
    
    def __init__(self):
        self.backup_dir = Path("/workspace/platform/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 从settings获取数据库配置
        self.db_config = self._parse_database_url()
    
    def _parse_database_url(self) -> dict:
        """解析数据库URL"""
        # 简化版，实际应该正确解析DATABASE_URL
        return {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "database": os.getenv("POSTGRES_DB", "learning_platform")
        }
    
    def backup(self, output_file: str = None) -> str:
        """
        备份数据库
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            备份文件路径
        """
        try:
            # 生成备份文件名
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.backup_dir / f"backup_{timestamp}.sql"
            else:
                output_file = Path(output_file)
            
            logger.info(f"开始备份数据库到: {output_file}")
            
            # 构建pg_dump命令
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_config["password"]
            
            cmd = [
                "pg_dump",
                "-h", self.db_config["host"],
                "-p", self.db_config["port"],
                "-U", self.db_config["user"],
                "-d", self.db_config["database"],
                "-F", "c",  # 自定义格式
                "-b",  # 包含大对象
                "-v",  # 详细输出
                "-f", str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                file_size = output_file.stat().st_size / (1024 * 1024)  # MB
                logger.success(f"✅ 备份成功!")
                logger.info(f"  文件: {output_file}")
                logger.info(f"  大小: {file_size:.2f} MB")
                return str(output_file)
            else:
                logger.error(f"❌ 备份失败: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 备份过程出错: {str(e)}")
            raise
    
    def restore(self, input_file: str):
        """
        恢复数据库
        
        Args:
            input_file: 备份文件路径
        """
        try:
            input_file = Path(input_file)
            
            if not input_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {input_file}")
            
            logger.warning(f"⚠️  即将恢复数据库从: {input_file}")
            logger.warning("   这将覆盖当前数据库的所有数据!")
            
            # 在生产环境应该要求确认
            response = input("确认继续? (yes/no): ")
            if response.lower() != "yes":
                logger.info("已取消恢复操作")
                return
            
            logger.info("开始恢复数据库...")
            
            # 构建pg_restore命令
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_config["password"]
            
            cmd = [
                "pg_restore",
                "-h", self.db_config["host"],
                "-p", self.db_config["port"],
                "-U", self.db_config["user"],
                "-d", self.db_config["database"],
                "-c",  # 清理（删除）数据库对象
                "-v",  # 详细输出
                str(input_file)
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.success(f"✅ 恢复成功!")
            else:
                logger.error(f"❌ 恢复失败: {result.stderr}")
                raise Exception(f"Restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 恢复过程出错: {str(e)}")
            raise
    
    def list_backups(self):
        """列出所有备份文件"""
        logger.info(f"备份目录: {self.backup_dir}")
        logger.info("━" * 80)
        
        backups = sorted(self.backup_dir.glob("backup_*.sql"), reverse=True)
        
        if not backups:
            logger.info("没有找到备份文件")
            return
        
        logger.info(f"找到 {len(backups)} 个备份文件:\n")
        logger.info(f"{'文件名':<40} {'大小':<15} {'创建时间':<20}")
        logger.info("━" * 80)
        
        for backup in backups:
            size_mb = backup.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            logger.info(
                f"{backup.name:<40} {size_mb:>10.2f} MB   "
                f"{mtime.strftime('%Y-%m-%d %H:%M:%S')}"
            )
    
    def auto_backup(self):
        """自动备份（保留最近N个）"""
        max_backups = 10
        
        logger.info(f"执行自动备份 (保留最近{max_backups}个)")
        
        # 创建新备份
        backup_file = self.backup()
        
        # 清理旧备份
        backups = sorted(self.backup_dir.glob("backup_*.sql"), reverse=True)
        
        if len(backups) > max_backups:
            logger.info(f"清理旧备份文件...")
            for old_backup in backups[max_backups:]:
                old_backup.unlink()
                logger.info(f"  删除: {old_backup.name}")
        
        logger.success(f"✅ 自动备份完成，当前保留 {min(len(backups), max_backups)} 个备份")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    backup_tool = DatabaseBackup()
    
    try:
        if command == "backup":
            output_file = None
            if len(sys.argv) > 2 and sys.argv[2] == "--output":
                output_file = sys.argv[3] if len(sys.argv) > 3 else None
            backup_tool.backup(output_file)
            
        elif command == "restore":
            if len(sys.argv) < 3:
                logger.error("请指定备份文件: --input <file>")
                sys.exit(1)
            if sys.argv[2] == "--input":
                input_file = sys.argv[3] if len(sys.argv) > 3 else None
                if input_file:
                    backup_tool.restore(input_file)
                else:
                    logger.error("请指定备份文件路径")
                    sys.exit(1)
            
        elif command == "list":
            backup_tool.list_backups()
            
        elif command == "auto":
            backup_tool.auto_backup()
            
        else:
            logger.error(f"未知命令: {command}")
            print(__doc__)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
