#!/usr/bin/env python3
"""
数据库迁移管理工具
管理数据库版本和迁移
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class MigrationManager:
    """迁移管理器"""
    
    def __init__(self):
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        
        self.versions_file = self.migrations_dir / "versions.json"
        self.current_version = self.load_current_version()
    
    def load_current_version(self) -> str:
        """加载当前版本"""
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                data = json.load(f)
                return data.get('current_version', '0.0.0')
        return '0.0.0'
    
    def save_version(self, version: str):
        """保存版本"""
        data = {
            'current_version': version,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.versions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_success(self, msg: str):
        print(f"{Colors.GREEN}✓ {msg}{Colors.END}")
    
    def print_warning(self, msg: str):
        print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")
    
    def print_error(self, msg: str):
        print(f"{Colors.RED}✗ {msg}{Colors.END}")
    
    def print_info(self, msg: str):
        print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")
    
    def create_migration(self, name: str):
        """创建新迁移"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{name}.py"
        filepath = self.migrations_dir / filename
        
        template = f'''"""
迁移: {name}
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

async def upgrade():
    """升级数据库"""
    print("执行升级...")
    
    # TODO: 在这里添加升级逻辑
    # 例如:
    # - 创建新表
    # - 添加列
    # - 修改数据
    
    print("✓ 升级完成")


async def downgrade():
    """回滚数据库"""
    print("执行回滚...")
    
    # TODO: 在这里添加回滚逻辑
    # 确保可以撤销upgrade中的所有更改
    
    print("✓ 回滚完成")
'''
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        self.print_success(f"创建迁移: {filename}")
        print(f"  位置: {filepath}")
        print()
        print("下一步:")
        print("  1. 编辑迁移文件，添加升级和回滚逻辑")
        print("  2. 运行 'python3 db_migrate.py upgrade' 执行迁移")
    
    def list_migrations(self):
        """列出所有迁移"""
        migrations = sorted(self.migrations_dir.glob("*.py"))
        migrations = [m for m in migrations if not m.name.startswith('__')]
        
        if not migrations:
            self.print_warning("没有找到迁移文件")
            return
        
        print(f"\n{Colors.BOLD}迁移列表:{Colors.END}")
        print("-" * 70)
        
        for i, migration in enumerate(migrations, 1):
            timestamp = migration.stem.split('_')[0]
            name = '_'.join(migration.stem.split('_')[2:])
            
            # 格式化时间戳
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d')
                date_str = dt.strftime('%Y-%m-%d')
            except:
                date_str = timestamp
            
            print(f"  {i}. [{date_str}] {name}")
            print(f"     文件: {migration.name}")
        
        print("-" * 70)
        print(f"总计: {len(migrations)} 个迁移")
    
    def show_status(self):
        """显示迁移状态"""
        print(f"\n{Colors.BOLD}数据库迁移状态:{Colors.END}")
        print("-" * 70)
        print(f"当前版本: {self.current_version}")
        print(f"迁移目录: {self.migrations_dir}")
        
        migrations = sorted(self.migrations_dir.glob("*.py"))
        migrations = [m for m in migrations if not m.name.startswith('__')]
        print(f"迁移文件: {len(migrations)} 个")
        print("-" * 70)
    
    async def upgrade(self, target: str = None):
        """执行升级"""
        print(f"\n{Colors.BOLD}执行数据库升级{Colors.END}")
        print("-" * 70)
        
        migrations = sorted(self.migrations_dir.glob("*.py"))
        migrations = [m for m in migrations if not m.name.startswith('__')]
        
        if not migrations:
            self.print_warning("没有找到迁移文件")
            return
        
        for migration in migrations:
            print(f"\n执行迁移: {migration.name}")
            
            try:
                # 动态导入迁移模块
                import importlib.util
                spec = importlib.util.spec_from_file_location("migration", migration)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 执行升级
                if hasattr(module, 'upgrade'):
                    await module.upgrade()
                    self.print_success(f"完成: {migration.name}")
                else:
                    self.print_warning(f"跳过: {migration.name} (没有upgrade函数)")
            
            except Exception as e:
                self.print_error(f"失败: {migration.name}")
                print(f"  错误: {e}")
                return
        
        # 更新版本
        new_version = "2.2.0"
        self.save_version(new_version)
        
        print()
        print("-" * 70)
        self.print_success("所有迁移执行完成")
        print(f"新版本: {new_version}")
    
    async def downgrade(self, steps: int = 1):
        """执行回滚"""
        print(f"\n{Colors.BOLD}执行数据库回滚{Colors.END}")
        print(f"回滚步数: {steps}")
        print("-" * 70)
        
        migrations = sorted(self.migrations_dir.glob("*.py"), reverse=True)
        migrations = [m for m in migrations if not m.name.startswith('__')]
        
        if not migrations:
            self.print_warning("没有找到迁移文件")
            return
        
        for i, migration in enumerate(migrations[:steps]):
            print(f"\n回滚迁移 {i+1}/{steps}: {migration.name}")
            
            try:
                # 动态导入迁移模块
                import importlib.util
                spec = importlib.util.spec_from_file_location("migration", migration)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 执行回滚
                if hasattr(module, 'downgrade'):
                    await module.downgrade()
                    self.print_success(f"完成: {migration.name}")
                else:
                    self.print_warning(f"跳过: {migration.name} (没有downgrade函数)")
            
            except Exception as e:
                self.print_error(f"失败: {migration.name}")
                print(f"  错误: {e}")
                return
        
        print()
        print("-" * 70)
        self.print_success(f"回滚完成 ({steps}步)")


def main():
    """主函数"""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description='数据库迁移管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create命令
    create_parser = subparsers.add_parser('create', help='创建新迁移')
    create_parser.add_argument('name', help='迁移名称')
    
    # list命令
    subparsers.add_parser('list', help='列出所有迁移')
    
    # status命令
    subparsers.add_parser('status', help='显示迁移状态')
    
    # upgrade命令
    upgrade_parser = subparsers.add_parser('upgrade', help='执行升级')
    upgrade_parser.add_argument('--target', help='目标版本')
    
    # downgrade命令
    downgrade_parser = subparsers.add_parser('downgrade', help='执行回滚')
    downgrade_parser.add_argument('--steps', type=int, default=1, help='回滚步数')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    print()
    print("=" * 70)
    print(" 数据库迁移管理工具")
    print("=" * 70)
    
    if args.command == 'create':
        manager.create_migration(args.name)
    
    elif args.command == 'list':
        manager.list_migrations()
    
    elif args.command == 'status':
        manager.show_status()
    
    elif args.command == 'upgrade':
        asyncio.run(manager.upgrade(args.target))
    
    elif args.command == 'downgrade':
        asyncio.run(manager.downgrade(args.steps))
    
    else:
        parser.print_help()
    
    print()


if __name__ == "__main__":
    main()
