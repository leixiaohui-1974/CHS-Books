"""
内容扫描器主程序
自动扫描books目录，解析书籍、章节、案例信息
"""

import os
import sys
import asyncio
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import markdown
from loguru import logger


class ContentScanner:
    """内容扫描器"""
    
    def __init__(self, books_path: str = "/workspace/books"):
        self.books_path = Path(books_path)
        self.discovered_books: List[Dict] = []
        
        logger.info(f"🔍 初始化内容扫描器: {books_path}")
    
    def scan_all(self) -> Dict[str, Any]:
        """全量扫描所有内容"""
        logger.info("🚀 开始全量扫描...")
        
        start_time = datetime.now()
        
        # 扫描所有书籍目录
        for item in self.books_path.iterdir():
            if item.is_dir() and not item.name.startswith(('_', '.')):
                logger.info(f"📚 扫描书籍: {item.name}")
                book_info = self.scan_book(item)
                if book_info:
                    self.discovered_books.append(book_info)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        result = {
            "total_books": len(self.discovered_books),
            "books": self.discovered_books,
            "scan_time": elapsed,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ 扫描完成！发现 {len(self.discovered_books)} 本书，耗时 {elapsed:.2f}秒")
        
        return result
    
    def scan_book(self, book_path: Path) -> Optional[Dict]:
        """扫描单本书籍"""
        try:
            readme_path = book_path / "README.md"
            if not readme_path.exists():
                logger.warning(f"⚠️  未找到README.md: {book_path}")
                return None
            
            # 解析README获取书籍元数据
            book_info = self.parse_book_readme(readme_path)
            book_info["slug"] = book_path.name
            book_info["github_path"] = str(book_path.relative_to(self.books_path))
            
            # 扫描案例
            examples_path = book_path / "code" / "examples"
            if examples_path.exists():
                book_info["cases"] = self.scan_cases(examples_path)
                book_info["total_cases"] = len(book_info["cases"])
            else:
                book_info["cases"] = []
                book_info["total_cases"] = 0
            
            logger.info(f"  ✓ 发现 {book_info['total_cases']} 个案例")
            
            return book_info
            
        except Exception as e:
            logger.error(f"❌ 扫描书籍失败 {book_path}: {e}")
            return None
    
    def parse_book_readme(self, readme_path: Path) -> Dict:
        """解析README.md提取书籍信息"""
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题（第一个#标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "未命名"
        
        # 提取副标题（第二个#标题或第一行##）
        subtitle_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
        subtitle = subtitle_match.group(1) if subtitle_match else None
        
        # 提取描述（取前200字符）
        # 去除标题后的第一段内容
        description_match = re.search(r'^#.+?\n\n(.+?)(?:\n\n|$)', content, re.DOTALL | re.MULTILINE)
        description = description_match.group(1)[:200] if description_match else None
        
        return {
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "status": "published",  # 默认为已发布
            "version": "1.0.0",
        }
    
    def scan_cases(self, examples_path: Path) -> List[Dict]:
        """扫描案例目录"""
        cases = []
        
        for case_dir in sorted(examples_path.iterdir()):
            if not case_dir.is_dir() or case_dir.name.startswith(('_', '.')):
                continue
            
            case_info = self.scan_case(case_dir)
            if case_info:
                cases.append(case_info)
        
        return cases
    
    def scan_case(self, case_path: Path) -> Optional[Dict]:
        """扫描单个案例"""
        try:
            # 提取案例序号和名称
            # 例如: case_01_irrigation -> order=1, slug=irrigation
            match = re.match(r'case_(\d+)_(.+)', case_path.name)
            if not match:
                logger.warning(f"⚠️  无效的案例目录名: {case_path.name}")
                return None
            
            order = int(match.group(1))
            slug = match.group(2)
            
            case_info = {
                "order": order,
                "slug": slug,
                "directory": case_path.name,
            }
            
            # 检查main.py
            main_py = case_path / "main.py"
            if main_py.exists():
                case_info["has_main"] = True
                case_info["script_path"] = str(main_py)
                
                # 解析Python文件提取工具配置
                tool_config = self.parse_main_py(main_py)
                if tool_config:
                    case_info["tool_config"] = tool_config
                    case_info["has_tool"] = True
            else:
                case_info["has_main"] = False
                case_info["has_tool"] = False
            
            # 检查README.md
            readme = case_path / "README.md"
            if readme.exists():
                case_info["has_readme"] = True
                # 解析README获取标题、描述
                with open(readme, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                    title_match = re.search(r'^#\s+(.+)$', readme_content, re.MULTILINE)
                    if title_match:
                        case_info["title"] = title_match.group(1)
            else:
                case_info["has_readme"] = False
                case_info["title"] = slug.replace('_', ' ').title()
            
            return case_info
            
        except Exception as e:
            logger.error(f"❌ 扫描案例失败 {case_path}: {e}")
            return None
    
    def parse_main_py(self, main_py_path: Path) -> Optional[Dict]:
        """解析main.py提取函数签名和参数"""
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            # 查找主函数
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in ['run_simulation', 'main', 'demo', 'run']:
                        params = self.extract_function_params(node)
                        return {
                            "entry_function": node.name,
                            "inputs": params
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 解析main.py失败: {e}")
            return None
    
    def extract_function_params(self, func_node: ast.FunctionDef) -> List[Dict]:
        """从函数定义提取参数信息"""
        params = []
        
        for arg in func_node.args.args:
            if arg.arg == 'self':
                continue
            
            param_info = {
                "name": arg.arg,
                "type": "unknown",
                "default": None
            }
            
            # 提取类型注解
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            
            params.append(param_info)
        
        # 提取默认值
        defaults = func_node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                param_idx = len(params) - len(defaults) + i
                if param_idx >= 0:
                    try:
                        params[param_idx]["default"] = ast.literal_eval(default)
                    except:
                        params[param_idx]["default"] = ast.unparse(default)
        
        return params
    
    def save_results(self, output_path: str = "scan_results.json"):
        """保存扫描结果到JSON文件"""
        result = self.scan_all()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 扫描结果已保存到: {output_path}")
        
        return result


def main():
    """主函数"""
    scanner = ContentScanner(books_path="/workspace/books")
    
    # 执行扫描
    result = scanner.scan_all()
    
    # 保存结果
    scanner.save_results("/workspace/platform/scan_results.json")
    
    # 打印统计信息
    print("\n" + "="*50)
    print(f"📊 扫描统计")
    print("="*50)
    print(f"总书籍数: {result['total_books']}")
    for book in result['books']:
        print(f"  📚 {book['title']}")
        print(f"     - 案例数: {book['total_cases']}")
    print("="*50)


if __name__ == "__main__":
    main()
