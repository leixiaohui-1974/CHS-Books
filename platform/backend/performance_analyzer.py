#!/usr/bin/env python3
"""
性能分析和优化工具
分析代码性能瓶颈并提供优化建议
"""

import time
import psutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.results = []
        self.recommendations = []
    
    def analyze_system_resources(self) -> Dict[str, Any]:
        """分析系统资源使用"""
        print("🔍 分析系统资源...")
        
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # 内存信息
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # 网络信息
        net_io = psutil.net_io_counters()
        
        result = {
            'cpu': {
                'usage_percent': cpu_percent,
                'count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else None,
                'status': 'good' if cpu_percent < 70 else 'warning' if cpu_percent < 90 else 'critical'
            },
            'memory': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_percent': memory.percent,
                'status': 'good' if memory.percent < 70 else 'warning' if memory.percent < 90 else 'critical'
            },
            'swap': {
                'total_gb': swap.total / (1024**3),
                'used_percent': swap.percent,
                'status': 'good' if swap.percent < 50 else 'warning'
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'used_percent': disk.percent,
                'read_mb': disk_io.read_bytes / (1024**2) if disk_io else 0,
                'write_mb': disk_io.write_bytes / (1024**2) if disk_io else 0,
                'status': 'good' if disk.percent < 80 else 'warning' if disk.percent < 95 else 'critical'
            },
            'network': {
                'sent_mb': net_io.bytes_sent / (1024**2),
                'recv_mb': net_io.bytes_recv / (1024**2),
                'status': 'good'
            }
        }
        
        # 生成建议
        if result['cpu']['status'] != 'good':
            self.recommendations.append({
                'type': 'cpu',
                'level': 'high',
                'message': f"CPU使用率过高({cpu_percent:.1f}%)，考虑优化计算密集型任务或增加CPU资源"
            })
        
        if result['memory']['status'] != 'good':
            self.recommendations.append({
                'type': 'memory',
                'level': 'high',
                'message': f"内存使用率过高({memory.percent:.1f}%)，考虑优化内存使用或增加内存"
            })
        
        if result['disk']['status'] != 'good':
            self.recommendations.append({
                'type': 'disk',
                'level': 'medium',
                'message': f"磁盘空间不足({disk.percent:.1f}%)，建议清理临时文件或扩展磁盘"
            })
        
        return result
    
    def analyze_code_hotspots(self) -> Dict[str, Any]:
        """分析代码热点"""
        print("🔍 分析代码热点...")
        
        backend_dir = Path(__file__).parent
        
        hotspots = []
        
        # 分析Python文件
        py_files = list(backend_dir.rglob("*.py"))
        
        for py_file in py_files[:20]:  # 限制分析数量
            if '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 简单的热点检测
                issues = []
                
                # 检查循环嵌套
                nested_loops = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('for ') or stripped.startswith('while '):
                        nested_loops += 1
                        if nested_loops > 2:
                            issues.append('深度嵌套循环')
                            break
                
                # 检查大函数
                func_lines = 0
                in_function = False
                for line in lines:
                    if line.strip().startswith('def '):
                        in_function = True
                        func_lines = 0
                    elif in_function:
                        func_lines += 1
                        if func_lines > 100:
                            issues.append('函数过长(>100行)')
                            in_function = False
                
                if issues:
                    hotspots.append({
                        'file': str(py_file.relative_to(backend_dir)),
                        'issues': issues,
                        'lines': len(lines)
                    })
            
            except Exception as e:
                pass
        
        result = {
            'files_analyzed': len(py_files),
            'hotspots_found': len(hotspots),
            'hotspots': hotspots[:10]  # 返回前10个
        }
        
        if hotspots:
            self.recommendations.append({
                'type': 'code',
                'level': 'medium',
                'message': f"发现{len(hotspots)}个代码热点，建议重构优化"
            })
        
        return result
    
    def analyze_database_queries(self) -> Dict[str, Any]:
        """分析数据库查询性能"""
        print("🔍 分析数据库查询...")
        
        # 模拟分析（实际需要连接数据库）
        result = {
            'slow_queries': 0,
            'total_queries': 0,
            'avg_query_time_ms': 0,
            'recommendations': []
        }
        
        # 检查模型文件中的查询
        models_dir = Path(__file__).parent / 'app' / 'models'
        
        if models_dir.exists():
            model_files = list(models_dir.glob("*.py"))
            
            for model_file in model_files:
                try:
                    with open(model_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查是否使用了索引
                    if 'index=True' not in content and 'relationship' in content:
                        result['recommendations'].append(
                            f"{model_file.name}: 考虑为关联字段添加索引"
                        )
                
                except Exception:
                    pass
        
        if result['recommendations']:
            self.recommendations.append({
                'type': 'database',
                'level': 'medium',
                'message': '数据库模型可以进一步优化索引'
            })
        
        return result
    
    def analyze_api_performance(self) -> Dict[str, Any]:
        """分析API性能"""
        print("🔍 分析API性能...")
        
        api_dir = Path(__file__).parent / 'app' / 'api' / 'endpoints'
        
        endpoints = []
        
        if api_dir.exists():
            for api_file in api_dir.glob("*.py"):
                try:
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 统计端点数量
                    import re
                    routes = re.findall(r'@router\.(get|post|put|delete|patch)', content)
                    
                    # 检查是否有async
                    async_count = content.count('async def')
                    sync_count = content.count('def ') - async_count
                    
                    endpoints.append({
                        'file': api_file.name,
                        'routes': len(routes),
                        'async_endpoints': async_count,
                        'sync_endpoints': sync_count
                    })
                    
                    if sync_count > async_count:
                        self.recommendations.append({
                            'type': 'api',
                            'level': 'low',
                            'message': f"{api_file.name}: 考虑使用async/await提高并发性能"
                        })
                
                except Exception:
                    pass
        
        result = {
            'total_endpoints': sum(e['routes'] for e in endpoints),
            'files': len(endpoints),
            'endpoints': endpoints
        }
        
        return result
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖包性能"""
        print("🔍 分析依赖包...")
        
        requirements_file = Path(__file__).parent / 'requirements.txt'
        
        result = {
            'total_packages': 0,
            'heavy_packages': [],
            'recommendations': []
        }
        
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            result['total_packages'] = len(packages)
            
            # 识别重量级包
            heavy = ['tensorflow', 'torch', 'pandas', 'numpy', 'opencv']
            for pkg in packages:
                pkg_name = pkg.split('==')[0].split('>=')[0].lower()
                if any(h in pkg_name for h in heavy):
                    result['heavy_packages'].append(pkg)
            
            if result['heavy_packages']:
                result['recommendations'].append(
                    f"发现{len(result['heavy_packages'])}个重量级依赖，考虑按需导入"
                )
        
        return result
    
    def generate_optimization_plan(self) -> List[Dict[str, Any]]:
        """生成优化计划"""
        print("\n📋 生成优化计划...")
        
        plan = []
        
        # 按优先级排序建议
        high_priority = [r for r in self.recommendations if r.get('level') == 'high']
        medium_priority = [r for r in self.recommendations if r.get('level') == 'medium']
        low_priority = [r for r in self.recommendations if r.get('level') == 'low']
        
        for priority, items in [('高', high_priority), ('中', medium_priority), ('低', low_priority)]:
            for item in items:
                plan.append({
                    'priority': priority,
                    'type': item['type'],
                    'recommendation': item['message']
                })
        
        return plan
    
    def generate_report(self) -> str:
        """生成性能报告"""
        report = []
        report.append("\n" + "=" * 70)
        report.append(" 性能分析报告")
        report.append("=" * 70)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 系统资源
        if 'system' in [r['name'] for r in self.results]:
            system = next(r for r in self.results if r['name'] == 'system')['data']
            report.append("📊 系统资源:")
            report.append("-" * 70)
            report.append(f"  CPU:    使用率 {system['cpu']['usage_percent']:.1f}% ({system['cpu']['count']}核)")
            report.append(f"  内存:   使用率 {system['memory']['used_percent']:.1f}% ({system['memory']['available_gb']:.1f}GB可用)")
            report.append(f"  磁盘:   使用率 {system['disk']['used_percent']:.1f}% ({system['disk']['total_gb'] - system['disk']['used_gb']:.1f}GB可用)")
            report.append("")
        
        # 优化建议
        if self.recommendations:
            report.append("💡 优化建议:")
            report.append("-" * 70)
            
            plan = self.generate_optimization_plan()
            for i, item in enumerate(plan, 1):
                priority_icon = "🔴" if item['priority'] == '高' else "🟡" if item['priority'] == '中' else "🟢"
                report.append(f"  {i}. [{priority_icon} {item['priority']}] {item['type'].upper()}")
                report.append(f"     {item['recommendation']}")
            
            report.append("")
        else:
            report.append("✅ 未发现明显性能问题")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_json(self, filename: str):
        """导出JSON报告"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'recommendations': self.recommendations,
            'optimization_plan': self.generate_optimization_plan()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 JSON报告已导出: {filename}")
    
    def run_analysis(self):
        """运行完整分析"""
        print("=" * 70)
        print(" 性能分析和优化工具")
        print("=" * 70)
        print()
        
        # 系统资源分析
        system_result = self.analyze_system_resources()
        self.results.append({'name': 'system', 'data': system_result})
        print("✓ 系统资源分析完成")
        
        # 代码热点分析
        code_result = self.analyze_code_hotspots()
        self.results.append({'name': 'code', 'data': code_result})
        print("✓ 代码热点分析完成")
        
        # 数据库分析
        db_result = self.analyze_database_queries()
        self.results.append({'name': 'database', 'data': db_result})
        print("✓ 数据库查询分析完成")
        
        # API性能分析
        api_result = self.analyze_api_performance()
        self.results.append({'name': 'api', 'data': api_result})
        print("✓ API性能分析完成")
        
        # 依赖分析
        dep_result = self.analyze_dependencies()
        self.results.append({'name': 'dependencies', 'data': dep_result})
        print("✓ 依赖包分析完成")
        
        # 生成报告
        print(self.generate_report())
        
        # 导出JSON
        filename = f"performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.export_json(filename)


def main():
    """主函数"""
    analyzer = PerformanceAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
