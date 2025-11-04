"""
代码质量检查工具
检查代码规范、复杂度、注释覆盖率等
"""

import ast
from pathlib import Path
from typing import Dict, List
import re


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "documented_functions": 0,
            "documented_classes": 0,
            "avg_complexity": 0.0
        }
    
    def check_file(self, file_path: Path) -> Dict:
        """检查单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            
            # 统计函数
            functions = self._count_functions(tree)
            
            # 统计类
            classes = self._count_classes(tree)
            
            # 计算复杂度
            complexity = self._calculate_complexity(tree)
            
            # 统计行数
            lines = len(code.split('\n'))
            
            # 注释率
            comment_ratio = self._calculate_comment_ratio(code)
            
            return {
                "file": str(file_path),
                "lines": lines,
                "functions": len(functions),
                "classes": len(classes),
                "documented_functions": sum(1 for f in functions if f['docstring']),
                "documented_classes": sum(1 for c in classes if c['docstring']),
                "complexity": complexity,
                "comment_ratio": comment_ratio
            }
        
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e)
            }
    
    def _count_functions(self, tree: ast.AST) -> List[Dict]:
        """统计函数"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node)
                })
        return functions
    
    def _count_classes(self, tree: ast.AST) -> List[Dict]:
        """统计类"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node)
                })
        return classes
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _calculate_comment_ratio(self, code: str) -> float:
        """计算注释率"""
        lines = code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        total_lines = len([l for l in lines if l.strip()])
        
        if total_lines == 0:
            return 0.0
        
        return comment_lines / total_lines
    
    def check_directory(self, directory: str) -> Dict:
        """检查整个目录"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return {"error": "目录不存在"}
        
        results = []
        
        for py_file in directory_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            result = self.check_file(py_file)
            if "error" not in result:
                results.append(result)
                
                # 更新统计
                self.stats["total_files"] += 1
                self.stats["total_lines"] += result["lines"]
                self.stats["total_functions"] += result["functions"]
                self.stats["total_classes"] += result["classes"]
                self.stats["documented_functions"] += result["documented_functions"]
                self.stats["documented_classes"] += result["documented_classes"]
        
        # 计算平均复杂度
        if results:
            self.stats["avg_complexity"] = sum(r["complexity"] for r in results) / len(results)
        
        return {
            "files": results,
            "stats": self.stats
        }
    
    def generate_report(self) -> str:
        """生成质量报告"""
        stats = self.stats
        
        report = []
        report.append("=" * 60)
        report.append(" 代码质量报告")
        report.append("=" * 60)
        report.append("")
        
        report.append("📊 基础统计:")
        report.append(f"  总文件数: {stats['total_files']}")
        report.append(f"  总代码行: {stats['total_lines']}")
        report.append(f"  总函数数: {stats['total_functions']}")
        report.append(f"  总类数: {stats['total_classes']}")
        report.append("")
        
        report.append("📝 文档覆盖:")
        if stats['total_functions'] > 0:
            func_doc_rate = stats['documented_functions'] / stats['total_functions'] * 100
            report.append(f"  函数文档率: {func_doc_rate:.1f}%")
        
        if stats['total_classes'] > 0:
            class_doc_rate = stats['documented_classes'] / stats['total_classes'] * 100
            report.append(f"  类文档率: {class_doc_rate:.1f}%")
        report.append("")
        
        report.append("🔢 复杂度:")
        report.append(f"  平均圈复杂度: {stats['avg_complexity']:.1f}")
        
        # 评分
        report.append("")
        report.append("⭐ 总体评分:")
        
        score = 0
        if stats['total_functions'] > 0:
            score += (stats['documented_functions'] / stats['total_functions']) * 30
        if stats['total_classes'] > 0:
            score += (stats['documented_classes'] / stats['total_classes']) * 30
        if stats['avg_complexity'] < 10:
            score += 40
        
        report.append(f"  {score:.0f}/100 分")
        
        if score >= 80:
            report.append("  等级: A (优秀)")
        elif score >= 60:
            report.append("  等级: B (良好)")
        elif score >= 40:
            report.append("  等级: C (及格)")
        else:
            report.append("  等级: D (需改进)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """主函数"""
    print("=" * 60)
    print(" 代码质量检查工具")
    print("=" * 60)
    print()
    
    checker = CodeQualityChecker()
    
    # 检查app目录
    print("检查 app/ 目录...")
    result = checker.check_directory("app")
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    print(f"✅ 检查完成")
    print()
    
    # 生成报告
    print(checker.generate_report())
    
    # 详细信息
    if result["files"]:
        print()
        print("📋 文件详情 (前10个):")
        print()
        
        for file_info in result["files"][:10]:
            print(f"📄 {Path(file_info['file']).name}")
            print(f"   行数: {file_info['lines']}")
            print(f"   函数: {file_info['functions']}")
            print(f"   类: {file_info['classes']}")
            print(f"   复杂度: {file_info['complexity']}")
            print()


if __name__ == "__main__":
    main()
