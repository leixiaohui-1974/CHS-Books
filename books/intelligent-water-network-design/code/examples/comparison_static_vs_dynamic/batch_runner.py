#!/usr/bin/env python3
"""
批处理运行工具
==============

功能: 批量运行多个配置的对比测试

使用方法:
    python3 batch_runner.py
    
输出:
    - 多组配置的对比结果
    - 批量测试报告
"""

import os
import json
import subprocess
import time
from typing import List, Dict
from datetime import datetime

print("="*80)
print("  批处理运行工具 v1.0")
print("="*80)
print()

# ============================================================================
# 批处理配置
# ============================================================================

BATCH_CONFIGS = [
    {
        'name': '小型闸门',
        'params': {
            'width': 2.0,
            'height': 2.0,
            'design_flow': 5.0,
            'Kp': 2.0,
            'Ki': 0.5,
            'Kd': 0.1
        }
    },
    {
        'name': '中型闸门',
        'params': {
            'width': 3.0,
            'height': 3.0,
            'design_flow': 10.0,
            'Kp': 2.5,
            'Ki': 0.6,
            'Kd': 0.15
        }
    },
    {
        'name': '大型闸门',
        'params': {
            'width': 5.0,
            'height': 4.0,
            'design_flow': 20.0,
            'Kp': 3.0,
            'Ki': 0.7,
            'Kd': 0.2
        }
    }
]

# ============================================================================
# 批处理运行器
# ============================================================================

class BatchRunner:
    """批处理运行器"""
    
    def __init__(self):
        self.results = []
    
    def run_quick_tests(self):
        """运行快速测试（不含耗时的仿真）"""
        print("【批量运行快速工具】")
        print("-" * 80)
        
        quick_tools = [
            ('visualize_comparison.py', '可视化对比'),
            ('performance_analyzer.py', '性能分析'),
            ('pid_tuner.py', 'PID优化'),
            ('intelligence_evaluator.py', '智能评估'),
            ('cost_benefit_calculator.py', '成本分析'),
            ('config_generator.py', '配置生成'),
            ('report_generator.py', '报告生成')
        ]
        
        results = []
        total_time = 0
        
        for i, (script, desc) in enumerate(quick_tools, 1):
            print(f"\n[{i}/{len(quick_tools)}] 运行: {desc} ({script})")
            
            if not os.path.exists(script):
                print(f"  ✗ 脚本不存在")
                results.append({'tool': desc, 'status': 'missing', 'time': 0})
                continue
            
            start = time.time()
            
            try:
                result = subprocess.run(
                    ['python3', script],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                elapsed = time.time() - start
                total_time += elapsed
                
                if result.returncode == 0:
                    print(f"  ✓ 成功 (耗时{elapsed:.1f}秒)")
                    results.append({'tool': desc, 'status': 'success', 'time': elapsed})
                else:
                    print(f"  ✗ 失败 (退出码: {result.returncode})")
                    results.append({'tool': desc, 'status': 'failed', 'time': elapsed})
            
            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                print(f"  ✗ 超时")
                results.append({'tool': desc, 'status': 'timeout', 'time': elapsed})
            
            except Exception as e:
                elapsed = time.time() - start
                print(f"  ✗ 异常: {e}")
                results.append({'tool': desc, 'status': 'error', 'time': elapsed})
        
        print("\n" + "="*80)
        print("  批量运行完成")
        print("="*80)
        print(f"\n总耗时: {total_time:.1f}秒")
        
        # 统计
        success = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - success
        
        print(f"成功: {success}/{len(results)}")
        print(f"失败: {failed}/{len(results)}")
        
        return results
    
    def generate_batch_report(self, results: List[Dict], 
                             output_file: str = 'batch_test_report.txt'):
        """生成批量测试报告"""
        lines = []
        lines.append("="*80)
        lines.append("  批量测试报告")
        lines.append("="*80)
        lines.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"测试工具数: {len(results)}")
        lines.append("")
        
        lines.append("="*80)
        lines.append("  测试结果")
        lines.append("="*80)
        lines.append("")
        lines.append(f"{'工具':<30} {'状态':<10} {'耗时(秒)'}")
        lines.append("-"*80)
        
        for r in results:
            status_map = {
                'success': '✓ 成功',
                'failed': '✗ 失败',
                'timeout': '✗ 超时',
                'error': '✗ 异常',
                'missing': '✗ 缺失'
            }
            status_str = status_map.get(r['status'], r['status'])
            lines.append(f"{r['tool']:<30} {status_str:<10} {r['time']:.2f}")
        
        lines.append("")
        lines.append("="*80)
        lines.append("  统计")
        lines.append("="*80)
        lines.append("")
        
        success = sum(1 for r in results if r['status'] == 'success')
        total_time = sum(r['time'] for r in results)
        
        lines.append(f"成功: {success}/{len(results)} ({success/len(results)*100:.0f}%)")
        lines.append(f"总耗时: {total_time:.1f}秒")
        lines.append("")
        lines.append("="*80)
        
        report_text = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text

# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    runner = BatchRunner()
    
    results = runner.run_quick_tests()
    
    print()
    print("【生成批量测试报告】")
    print("-" * 80)
    
    report = runner.generate_batch_report(results)
    print(report)
    print("\n✓ 批量测试报告已保存: batch_test_report.txt")
    
    print()
    print("="*80)
    print("  批处理完成!")
    print("="*80)
    print()
    print("生成的文件:")
    print("  1. batch_test_report.txt - 批量测试报告")
    print()
    print("="*80)
