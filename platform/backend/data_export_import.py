#!/usr/bin/env python3
"""
数据导入导出工具
支持多种格式的数据导入导出
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import zipfile
import shutil


class DataExporter:
    """数据导出器"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_project_structure(self) -> str:
        """导出项目结构"""
        print("📦 导出项目结构...")
        
        backend_dir = Path(__file__).parent
        platform_dir = backend_dir.parent
        
        structure = {
            'platform': {
                'name': 'intelligent-knowledge-platform',
                'version': 'V2.2.0 Final',
                'export_time': datetime.now().isoformat()
            },
            'directories': {},
            'files': {}
        }
        
        # 扫描目录结构
        for item in platform_dir.rglob("*"):
            if '.git' in str(item) or '__pycache__' in str(item) or 'node_modules' in str(item):
                continue
            
            rel_path = item.relative_to(platform_dir)
            
            if item.is_dir():
                structure['directories'][str(rel_path)] = {
                    'files': len(list(item.glob("*")))
                }
            elif item.is_file():
                structure['files'][str(rel_path)] = {
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
        
        # 保存
        output_file = self.output_dir / f"project_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 项目结构已导出: {output_file}")
        return str(output_file)
    
    def export_code_statistics(self) -> str:
        """导出代码统计"""
        print("📊 导出代码统计...")
        
        backend_dir = Path(__file__).parent
        
        stats = {
            'export_time': datetime.now().isoformat(),
            'by_extension': {},
            'by_directory': {},
            'total': {
                'files': 0,
                'lines': 0,
                'blank_lines': 0,
                'comment_lines': 0
            }
        }
        
        # 统计各类文件
        for ext in ['.py', '.md', '.txt', '.json', '.yml', '.yaml']:
            files = list(backend_dir.parent.rglob(f"*{ext}"))
            files = [f for f in files if '__pycache__' not in str(f) and '.git' not in str(f)]
            
            total_lines = 0
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                except:
                    pass
            
            if files:
                stats['by_extension'][ext] = {
                    'files': len(files),
                    'lines': total_lines
                }
                stats['total']['files'] += len(files)
                stats['total']['lines'] += total_lines
        
        # 保存
        output_file = self.output_dir / f"code_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 代码统计已导出: {output_file}")
        return str(output_file)
    
    def export_api_endpoints(self) -> str:
        """导出API端点列表"""
        print("🔌 导出API端点...")
        
        api_dir = Path(__file__).parent / 'app' / 'api' / 'endpoints'
        
        endpoints = []
        
        if api_dir.exists():
            import re
            
            for api_file in api_dir.glob("*.py"):
                try:
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取路由
                    routes = re.findall(
                        r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'](?:.*?summary=["\']([^"\']+))?',
                        content,
                        re.DOTALL
                    )
                    
                    for method, path, summary in routes:
                        endpoints.append({
                            'file': api_file.name,
                            'method': method.upper(),
                            'path': path,
                            'summary': summary if summary else ''
                        })
                
                except Exception as e:
                    pass
        
        # 保存为JSON
        json_file = self.output_dir / f"api_endpoints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(endpoints, f, indent=2, ensure_ascii=False)
        
        # 保存为CSV
        csv_file = self.output_dir / f"api_endpoints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'method', 'path', 'summary'])
            writer.writeheader()
            writer.writerows(endpoints)
        
        print(f"✓ API端点已导出: {json_file}")
        print(f"✓ API端点已导出: {csv_file}")
        return str(json_file)
    
    def export_documentation(self) -> str:
        """导出文档列表"""
        print("📚 导出文档列表...")
        
        platform_dir = Path(__file__).parent.parent
        
        docs = []
        
        for md_file in platform_dir.rglob("*.md"):
            if '.git' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # 提取第一个标题
                    title = ''
                    for line in lines:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                
                docs.append({
                    'file': str(md_file.relative_to(platform_dir)),
                    'title': title,
                    'size_kb': md_file.stat().st_size / 1024,
                    'lines': len(lines),
                    'modified': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })
            
            except Exception:
                pass
        
        # 按文件大小排序
        docs.sort(key=lambda x: x['size_kb'], reverse=True)
        
        # 保存
        output_file = self.output_dir / f"documentation_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 文档列表已导出: {output_file}")
        return str(output_file)
    
    def create_backup(self) -> str:
        """创建完整备份"""
        print("💾 创建项目备份...")
        
        platform_dir = Path(__file__).parent.parent
        backup_name = f"platform_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = self.output_dir / backup_name
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 关键目录
            important_dirs = [
                'backend/app',
                'backend/*.py',
                'sdk',
                'examples',
                '*.md',
                'docker-compose*.yml'
            ]
            
            file_count = 0
            
            # 添加Python文件
            for py_file in platform_dir.rglob("*.py"):
                if '__pycache__' not in str(py_file) and '.git' not in str(py_file):
                    arcname = py_file.relative_to(platform_dir)
                    zipf.write(py_file, arcname)
                    file_count += 1
            
            # 添加文档
            for md_file in platform_dir.glob("*.md"):
                arcname = md_file.relative_to(platform_dir)
                zipf.write(md_file, arcname)
                file_count += 1
            
            # 添加配置文件
            for config in ['docker-compose.v2.yml', 'backend/requirements.txt']:
                config_file = platform_dir / config
                if config_file.exists():
                    arcname = config_file.relative_to(platform_dir)
                    zipf.write(config_file, arcname)
                    file_count += 1
        
        size_mb = backup_path.stat().st_size / (1024 ** 2)
        print(f"✓ 备份已创建: {backup_path} ({size_mb:.2f}MB, {file_count}个文件)")
        return str(backup_path)


class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        pass
    
    def import_from_json(self, json_file: str) -> Dict[str, Any]:
        """从JSON导入"""
        print(f"📥 从JSON导入: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ 导入完成，包含{len(data)}条记录")
        return data
    
    def import_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """从CSV导入"""
        print(f"📥 从CSV导入: {csv_file}")
        
        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        print(f"✓ 导入完成，包含{len(data)}条记录")
        return data
    
    def restore_from_backup(self, backup_file: str, target_dir: str = None):
        """从备份恢复"""
        print(f"📥 从备份恢复: {backup_file}")
        
        if target_dir is None:
            target_dir = Path(__file__).parent.parent / "restored"
        else:
            target_dir = Path(target_dir)
        
        target_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(target_dir)
            file_count = len(zipf.namelist())
        
        print(f"✓ 恢复完成，共{file_count}个文件")
        print(f"  目标目录: {target_dir}")
        return str(target_dir)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据导入导出工具')
    parser.add_argument('command', 
                       choices=['export', 'import', 'backup', 'restore'],
                       help='操作命令')
    parser.add_argument('--type', 
                       choices=['structure', 'stats', 'api', 'docs', 'all'],
                       default='all',
                       help='导出类型')
    parser.add_argument('--file', help='导入/恢复的文件路径')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='文件格式')
    parser.add_argument('--target', help='恢复目标目录')
    
    args = parser.parse_args()
    
    print()
    print("=" * 70)
    print(" 数据导入导出工具")
    print("=" * 70)
    print()
    
    if args.command == 'export':
        exporter = DataExporter()
        
        if args.type in ['structure', 'all']:
            exporter.export_project_structure()
        
        if args.type in ['stats', 'all']:
            exporter.export_code_statistics()
        
        if args.type in ['api', 'all']:
            exporter.export_api_endpoints()
        
        if args.type in ['docs', 'all']:
            exporter.export_documentation()
        
        print()
        print(f"✅ 导出完成！文件保存在: {exporter.output_dir}")
    
    elif args.command == 'backup':
        exporter = DataExporter()
        backup_file = exporter.create_backup()
        print()
        print(f"✅ 备份完成！文件: {backup_file}")
    
    elif args.command == 'import':
        if not args.file:
            print("❌ 错误: 需要指定--file参数")
            sys.exit(1)
        
        importer = DataImporter()
        
        if args.format == 'json':
            data = importer.import_from_json(args.file)
        elif args.format == 'csv':
            data = importer.import_from_csv(args.file)
        
        print()
        print(f"✅ 导入完成！")
    
    elif args.command == 'restore':
        if not args.file:
            print("❌ 错误: 需要指定--file参数")
            sys.exit(1)
        
        importer = DataImporter()
        target = importer.restore_from_backup(args.file, args.target)
        print()
        print(f"✅ 恢复完成！位置: {target}")
    
    print()


if __name__ == "__main__":
    main()
