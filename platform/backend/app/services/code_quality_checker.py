"""
代码质量检查器
提供全面的代码质量分析和建议
"""

import ast
from typing import Dict, List, Any
from loguru import logger
import re


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.rules = self._load_rules()
        logger.info("✅ 代码质量检查器已初始化")
    
    def _load_rules(self) -> List[Dict]:
        """加载检查规则"""
        return [
            {
                "id": "func_length",
                "name": "函数长度检查",
                "check": self._check_function_length,
                "severity": "warning"
            },
            {
                "id": "complexity",
                "name": "复杂度检查",
                "check": self._check_complexity,
                "severity": "warning"
            },
            {
                "id": "docstring",
                "name": "文档字符串检查",
                "check": self._check_docstrings,
                "severity": "info"
            },
            {
                "id": "naming",
                "name": "命名规范检查",
                "check": self._check_naming,
                "severity": "info"
            },
            {
                "id": "imports",
                "name": "导入语句检查",
                "check": self._check_imports,
                "severity": "info"
            }
        ]
    
    async def check(self, code: str) -> Dict[str, Any]:
        """
        检查代码质量
        
        Args:
            code: Python代码
            
        Returns:
            检查结果
        """
        try:
            tree = ast.parse(code)
            
            issues = []
            for rule in self.rules:
                try:
                    rule_issues = await rule["check"](tree, code)
                    for issue in rule_issues:
                        issue["rule_id"] = rule["id"]
                        issue["rule_name"] = rule["name"]
                        issue["severity"] = rule["severity"]
                        issues.append(issue)
                except Exception as e:
                    logger.warning(f"规则 {rule['id']} 检查失败: {e}")
            
            # 计算总分
            error_count = len([i for i in issues if i["severity"] == "error"])
            warning_count = len([i for i in issues if i["severity"] == "warning"])
            info_count = len([i for i in issues if i["severity"] == "info"])
            
            total_score = 100 - (error_count * 15 + warning_count * 5 + info_count * 2)
            total_score = max(0, min(100, total_score))
            
            return {
                "score": total_score,
                "grade": self._get_grade(total_score),
                "issues": issues,
                "summary": {
                    "errors": error_count,
                    "warnings": warning_count,
                    "info": info_count,
                    "total": len(issues)
                },
                "recommendations": self._generate_recommendations(issues, total_score)
            }
            
        except SyntaxError as e:
            return {
                "score": 0,
                "grade": "F",
                "issues": [{
                    "severity": "error",
                    "rule_id": "syntax",
                    "rule_name": "语法检查",
                    "line": e.lineno,
                    "message": f"语法错误: {e.msg}",
                    "suggestion": "请修复语法错误后重新检查"
                }],
                "summary": {
                    "errors": 1,
                    "warnings": 0,
                    "info": 0,
                    "total": 1
                }
            }
        except Exception as e:
            logger.error(f"❌ 代码质量检查失败: {e}")
            return {
                "score": 0,
                "grade": "F",
                "error": str(e)
            }
    
    async def _check_function_length(self, tree: ast.AST, code: str) -> List[Dict]:
        """检查函数长度"""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        issues.append({
                            "line": node.lineno,
                            "message": f"函数 '{node.name}' 过长 ({length} 行)",
                            "suggestion": "考虑将函数拆分为更小的函数，每个函数应该只做一件事"
                        })
        return issues
    
    async def _check_complexity(self, tree: ast.AST, code: str) -> List[Dict]:
        """检查代码复杂度"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_function_complexity(node)
                if complexity > 10:
                    issues.append({
                        "line": node.lineno,
                        "message": f"函数 '{node.name}' 循环复杂度过高 ({complexity})",
                        "suggestion": "考虑重构函数，降低复杂度。目标是保持复杂度在10以下"
                    })
        
        return issues
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """计算函数的循环复杂度"""
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    async def _check_docstrings(self, tree: ast.AST, code: str) -> List[Dict]:
        """检查文档字符串"""
        issues = []
        
        # 检查模块文档字符串
        if not ast.get_docstring(tree):
            issues.append({
                "line": 1,
                "message": "模块缺少文档字符串",
                "suggestion": "在文件开头添加模块级文档字符串，说明模块的用途"
            })
        
        # 检查函数和类的文档字符串
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    issues.append({
                        "line": node.lineno,
                        "message": f"函数 '{node.name}' 缺少文档字符串",
                        "suggestion": "添加文档字符串说明函数的用途、参数和返回值"
                    })
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    issues.append({
                        "line": node.lineno,
                        "message": f"类 '{node.name}' 缺少文档字符串",
                        "suggestion": "添加文档字符串说明类的用途和主要属性"
                    })
        
        return issues
    
    async def _check_naming(self, tree: ast.AST, code: str) -> List[Dict]:
        """检查命名规范"""
        issues = []
        
        for node in ast.walk(tree):
            # 检查函数命名
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name) and not node.name.startswith('_'):
                    if node.name[0].isupper():  # 可能是测试类的方法
                        continue
                    issues.append({
                        "line": node.lineno,
                        "message": f"函数名 '{node.name}' 不符合命名规范",
                        "suggestion": f"建议使用小写字母和下划线: '{self._to_snake_case(node.name)}'"
                    })
            
            # 检查类命名
            elif isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    issues.append({
                        "line": node.lineno,
                        "message": f"类名 '{node.name}' 不符合命名规范",
                        "suggestion": f"建议使用大驼峰命名: '{self._to_pascal_case(node.name)}'"
                    })
            
            # 检查常量命名
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # 如果是全大写，应该是常量
                        if name.isupper() and len(name) > 1:
                            # 这是正确的常量命名
                            pass
                        elif '_' not in name and name[0].isupper():
                            # 可能是错误的常量命名
                            pass
        
        return issues
    
    async def _check_imports(self, tree: ast.AST, code: str) -> List[Dict]:
        """检查导入语句"""
        issues = []
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append((node.lineno, node))
        
        # 检查是否有未使用的导入
        # (这需要更复杂的分析，这里只做基本检查)
        
        # 检查导入顺序 (标准库 -> 第三方 -> 本地)
        # 这需要更详细的实现
        
        return issues
    
    def _is_snake_case(self, name: str) -> bool:
        """检查是否为蛇形命名"""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None
    
    def _is_pascal_case(self, name: str) -> bool:
        """检查是否为大驼峰命名"""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def _to_snake_case(self, name: str) -> str:
        """转换为蛇形命名"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为大驼峰命名"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _get_grade(self, score: int) -> str:
        """根据分数获取等级"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, issues: List[Dict], score: int) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if score >= 90:
            recommendations.append("✨ 代码质量优秀！继续保持")
        elif score >= 75:
            recommendations.append("👍 代码质量良好，还有一些小问题可以改进")
        elif score >= 60:
            recommendations.append("⚠️ 代码质量一般，建议重点关注以下问题")
        else:
            recommendations.append("❌ 代码质量需要改进，请优先修复高优先级问题")
        
        # 根据问题类型提供建议
        if any(i["rule_id"] == "func_length" for i in issues):
            recommendations.append("• 拆分过长的函数，提高代码可读性")
        
        if any(i["rule_id"] == "complexity" for i in issues):
            recommendations.append("• 降低函数复杂度，使代码更易于维护")
        
        if any(i["rule_id"] == "docstring" for i in issues):
            recommendations.append("• 添加文档字符串，帮助其他开发者理解代码")
        
        if any(i["rule_id"] == "naming" for i in issues):
            recommendations.append("• 遵循Python命名规范 (PEP 8)")
        
        return recommendations


# 创建全局实例
code_quality_checker = CodeQualityChecker()

