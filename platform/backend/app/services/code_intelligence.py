"""
代码智能服务
提供代码加载、分析、编辑、差异对比等功能
"""

import ast
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import difflib
from loguru import logger


class CodeAnalyzer:
    """代码分析器 - 基于AST"""
    
    @staticmethod
    def analyze_file(file_path: str) -> Dict[str, Any]:
        """
        分析Python文件
        
        Returns:
            {
                "imports": [...],
                "functions": [...],
                "classes": [...],
                "globals": [...],
                "complexity": int
            }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            
            return {
                "imports": CodeAnalyzer._extract_imports(tree),
                "functions": CodeAnalyzer._extract_functions(tree),
                "classes": CodeAnalyzer._extract_classes(tree),
                "globals": CodeAnalyzer._extract_globals(tree),
                "complexity": CodeAnalyzer._calculate_complexity(tree),
                "line_count": len(code.split('\n'))
            }
        
        except Exception as e:
            logger.error(f"❌ 代码分析失败: {file_path}, {e}")
            return {}
    
    @staticmethod
    def _extract_imports(tree: ast.AST) -> List[str]:
        """提取导入语句"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return imports
    
    @staticmethod
    def _extract_functions(tree: ast.AST) -> List[Dict]:
        """提取函数定义"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
        
        return functions
    
    @staticmethod
    def _extract_classes(tree: ast.AST) -> List[Dict]:
        """提取类定义"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name for n in node.body 
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                
                classes.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "methods": methods,
                    "docstring": ast.get_docstring(node)
                })
        
        return classes
    
    @staticmethod
    def _extract_globals(tree: ast.AST) -> List[str]:
        """提取全局变量"""
        globals_vars = []
        
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_vars.append(target.id)
        
        return globals_vars
    
    @staticmethod
    def _calculate_complexity(tree: ast.AST) -> int:
        """计算循环复杂度（简化版）"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity


class CodeLoader:
    """代码加载器"""
    
    @staticmethod
    def load_case_files(case_path: str) -> Dict[str, str]:
        """
        加载案例的所有代码文件
        
        Args:
            case_path: 案例目录路径
            
        Returns:
            {relative_path: content}
        """
        files = {}
        case_dir = Path(case_path)
        
        if not case_dir.exists():
            logger.error(f"❌ 案例目录不存在: {case_path}")
            return files
        
        # 遍历Python文件
        for py_file in case_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                relative_path = py_file.relative_to(case_dir)
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                files[str(relative_path)] = content
                logger.debug(f"  ✓ 加载文件: {relative_path}")
            
            except Exception as e:
                logger.error(f"  ✗ 加载文件失败: {py_file}, {e}")
        
        logger.info(f"📂 加载案例文件: {case_path} ({len(files)} 个文件)")
        
        return files
    
    @staticmethod
    def get_file_tree(case_path: str) -> List[Dict]:
        """
        获取案例文件树结构
        
        Returns:
            [{
                "name": "main.py",
                "path": "main.py",
                "type": "file",
                "size": 1234
            }, ...]
        """
        tree = []
        case_dir = Path(case_path)
        
        if not case_dir.exists():
            return tree
        
        def build_tree(directory: Path, prefix: str = "") -> List[Dict]:
            items = []
            
            for item in sorted(directory.iterdir()):
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                
                relative_path = item.relative_to(case_dir)
                
                if item.is_file():
                    items.append({
                        "name": item.name,
                        "path": str(relative_path),
                        "type": "file",
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
                
                elif item.is_dir():
                    folder_item = {
                        "name": item.name,
                        "path": str(relative_path),
                        "type": "folder",
                        "children": build_tree(item, str(relative_path) + "/")
                    }
                    items.append(folder_item)
            
            return items
        
        tree = build_tree(case_dir)
        
        return tree


class CodeDiffer:
    """代码差异对比"""
    
    @staticmethod
    def get_diff(original: str, modified: str, filename: str = "file") -> Dict[str, Any]:
        """
        获取代码差异
        
        Returns:
            {
                "has_changes": bool,
                "diff_html": str,
                "diff_unified": str,
                "stats": {
                    "additions": int,
                    "deletions": int,
                    "changes": int
                }
            }
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        # 生成unified diff
        diff_gen = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"{filename} (原始)",
            tofile=f"{filename} (修改后)",
            lineterm=''
        )
        
        diff_unified = '\n'.join(diff_gen)
        
        # 生成HTML diff
        html_diff = difflib.HtmlDiff().make_file(
            original_lines,
            modified_lines,
            fromdesc=f"{filename} (原始)",
            todesc=f"{filename} (修改后)"
        )
        
        # 统计变更
        additions = 0
        deletions = 0
        changes = 0
        
        for line in diff_unified.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        changes = additions + deletions
        
        return {
            "has_changes": changes > 0,
            "diff_html": html_diff,
            "diff_unified": diff_unified,
            "stats": {
                "additions": additions,
                "deletions": deletions,
                "changes": changes
            }
        }
    
    @staticmethod
    def get_similarity(text1: str, text2: str) -> float:
        """计算文本相似度 (0-1)"""
        return difflib.SequenceMatcher(None, text1, text2).ratio()


class CodeEditor:
    """代码编辑器辅助"""
    
    @staticmethod
    def format_code(code: str) -> Tuple[str, bool]:
        """
        格式化代码（使用black）
        
        Returns:
            (formatted_code, success)
        """
        try:
            import black
            
            formatted = black.format_str(code, mode=black.FileMode())
            return formatted, True
        
        except ImportError:
            logger.warning("⚠️  black未安装，跳过格式化")
            return code, False
        
        except Exception as e:
            logger.error(f"❌ 代码格式化失败: {e}")
            return code, False
    
    @staticmethod
    def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        验证Python语法
        
        Returns:
            (is_valid, error_message)
        """
        try:
            ast.parse(code)
            return True, None
        
        except SyntaxError as e:
            return False, f"语法错误: 第{e.lineno}行 - {e.msg}"
        
        except Exception as e:
            return False, f"解析错误: {str(e)}"
    
    @staticmethod
    def extract_function(code: str, function_name: str) -> Optional[str]:
        """提取指定函数的代码"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
                    
                    return '\n'.join(lines[start_line:end_line])
            
            return None
        
        except Exception as e:
            logger.error(f"❌ 提取函数失败: {e}")
            return None


class DependencyExtractor:
    """依赖提取器"""
    
    @staticmethod
    def extract_from_code(code: str) -> List[str]:
        """从代码中提取依赖"""
        try:
            tree = ast.parse(code)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # 获取顶层包名
                        package = alias.name.split('.')[0]
                        imports.add(package)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        imports.add(package)
            
            # 过滤标准库
            stdlib_modules = {
                'os', 'sys', 'json', 'time', 'datetime', 'math', 'random',
                'collections', 'itertools', 'functools', 're', 'io', 'pathlib'
            }
            
            third_party = [imp for imp in imports if imp not in stdlib_modules]
            
            return sorted(third_party)
        
        except Exception as e:
            logger.error(f"❌ 提取依赖失败: {e}")
            return []
    
    @staticmethod
    def extract_from_file(file_path: str) -> List[str]:
        """从文件中提取依赖"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return DependencyExtractor.extract_from_code(code)
        
        except Exception as e:
            logger.error(f"❌ 读取文件失败: {file_path}, {e}")
            return []
    
    @staticmethod
    def load_requirements(requirements_file: str) -> List[str]:
        """加载requirements.txt"""
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 解析requirements
            requirements = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 移除版本号
                    package = line.split('==')[0].split('>=')[0].split('<=')[0]
                    requirements.append(package)
            
            return requirements
        
        except Exception as e:
            logger.error(f"❌ 加载requirements.txt失败: {e}")
            return []


class CodeIntelligenceService:
    """代码智能服务 - 统一接口"""
    
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.loader = CodeLoader()
        self.differ = CodeDiffer()
        self.editor = CodeEditor()
        self.dependency_extractor = DependencyExtractor()
    
    async def load_case(self, case_path: str) -> Dict[str, Any]:
        """
        加载案例代码
        
        Returns:
            {
                "files": {path: content},
                "file_tree": [...],
                "dependencies": [...]
            }
        """
        files = self.loader.load_case_files(case_path)
        file_tree = self.loader.get_file_tree(case_path)
        
        # 提取依赖
        dependencies = set()
        
        # 尝试从requirements.txt加载
        req_file = Path(case_path) / "requirements.txt"
        if req_file.exists():
            dependencies.update(self.dependency_extractor.load_requirements(str(req_file)))
        
        # 从代码中提取
        for content in files.values():
            dependencies.update(self.dependency_extractor.extract_from_code(content))
        
        return {
            "files": files,
            "file_tree": file_tree,
            "dependencies": sorted(list(dependencies))
        }
    
    async def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """分析代码文件"""
        return self.analyzer.analyze_file(file_path)
    
    async def get_diff(self, original: str, modified: str, filename: str) -> Dict[str, Any]:
        """获取代码差异"""
        return self.differ.get_diff(original, modified, filename)
    
    async def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证代码语法"""
        return self.editor.validate_syntax(code)
    
    async def format_code(self, code: str) -> Tuple[str, bool]:
        """格式化代码"""
        return self.editor.format_code(code)


# 全局服务实例
code_intelligence_service = CodeIntelligenceService()
