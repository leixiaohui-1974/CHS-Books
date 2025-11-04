#!/usr/bin/env python3
"""
数据导出工具
============

功能: 将所有分析结果导出为多种格式(CSV, JSON, Excel等)

使用方法:
    python3 data_exporter.py
    
输出:
    - export/comparison_data.csv (对比数据CSV)
    - export/comparison_data.json (对比数据JSON)
    - export/performance_metrics.csv (性能指标CSV)
    - export/cost_analysis.csv (成本分析CSV)
    - export/all_data_summary.txt (数据汇总)
"""

import os
import json
import csv
from typing import Dict, List
from datetime import datetime

print("="*80)
print("  数据导出工具 v1.0")
print("="*80)
print()

# ============================================================================
# 数据定义
# ============================================================================

# 基础对比数据
COMPARISON_DATA = {
    '设计方案': ['静态设计', 'L2级动态设计', 'L3级协调控制'],
    '设计方法': ['恒定流水力计算', 'PID控制+数字孪生', '协调控制+解耦算法'],
    '设计工况数': [2, 100, 200],
    '控制点数': [1, 1, 4],
    '控制精度(cm)': [30.0, 3.0, 2.0],
    '响应时间(分钟)': [45.0, 4.0, 3.5],
    '自动化程度(%)': [0, 100, 95],
    '初始投资(万元)': [30, 35, 180],
    '年运行成本(万元)': [180, 120, 380],
    '运行人员数': [13, 3, 8],
    '智能化等级': ['L0', 'L2', 'L3'],
    '智能化得分': [30, 86, 88],
    '代码行数': [400, 600, 900]
}

# 性能指标详细数据
PERFORMANCE_METRICS = {
    '静态设计': {
        '传感器数量': 0,
        '控制器数量': 0,
        '通信设备数': 0,
        '控制精度(cm)': 30.0,
        '响应时间(分钟)': 45.0,
        '自动化能力(分)': 0,
        '精度能力(分)': 30,
        '速度能力(分)': 25,
        '鲁棒性(分)': 20,
        '可维护性(分)': 40,
        '综合得分': 30,
        '等级认证': 'L0'
    },
    'L2级动态设计': {
        '传感器数量': 2,
        '控制器数量': 1,
        '通信设备数': 1,
        '控制精度(cm)': 3.0,
        '响应时间(分钟)': 4.0,
        '自动化能力(分)': 100,
        '精度能力(分)': 75,
        '速度能力(分)': 85,
        '鲁棒性(分)': 75,
        '可维护性(分)': 85,
        '综合得分': 86,
        '等级认证': 'L2'
    },
    'L3级协调控制': {
        '传感器数量': 8,
        '控制器数量': 4,
        '通信设备数': 5,
        '控制精度(cm)': 2.0,
        '响应时间(分钟)': 3.5,
        '自动化能力(分)': 95,
        '精度能力(分)': 85,
        '速度能力(分)': 90,
        '鲁棒性(分)': 85,
        '可维护性(分)': 90,
        '综合得分': 88,
        '等级认证': 'L3'
    }
}

# 成本分析数据
COST_ANALYSIS = {
    '静态设计': {
        '初始投资(万元)': 30,
        '年人工成本(万元)': 130,
        '年维护成本(万元)': 30,
        '年电力成本(万元)': 20,
        '年运行总成本(万元)': 180,
        '20年总成本(万元)': 3630,
        '投资回收期(年)': 0
    },
    'L2级动态设计': {
        '初始投资(万元)': 35,
        '年人工成本(万元)': 30,
        '年维护成本(万元)': 60,
        '年电力成本(万元)': 30,
        '年运行总成本(万元)': 120,
        '20年总成本(万元)': 2435,
        '投资回收期(年)': 0.08
    },
    'L3级协调控制': {
        '初始投资(万元)': 180,
        '年人工成本(万元)': 80,
        '年维护成本(万元)': 200,
        '年电力成本(万元)': 100,
        '年运行总成本(万元)': 380,
        '20年总成本(万元)': 7780,
        '投资回收期(年)': 'N/A'
    }
}

# PID参数推荐
PID_PARAMETERS = {
    '默认参数': {
        'Kp': 2.0,
        'Ki': 0.5,
        'Kd': 0.1,
        '稳态误差(cm)': 1.42,
        '最大误差(cm)': 1.95
    },
    '优化参数': {
        'Kp': 3.0,
        'Ki': 0.7,
        'Kd': 0.3,
        '稳态误差(cm)': 1.07,
        '最大误差(cm)': 1.74
    },
    '敏感性分析推荐': {
        'Kp': 4.53,
        'Ki': 1.50,
        'Kd': 0.0,
        '稳态误差(cm)': 0.01,
        '最大误差(cm)': 'N/A'
    }
}

# ============================================================================
# 数据导出器
# ============================================================================

class DataExporter:
    """数据导出器"""
    
    def __init__(self, output_dir: str = 'export'):
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ 创建输出目录: {output_dir}/")
    
    def export_comparison_csv(self):
        """导出对比数据为CSV"""
        output_file = os.path.join(self.output_dir, 'comparison_data.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = ['指标'] + COMPARISON_DATA['设计方案']
            writer.writerow(headers)
            
            # 写入数据
            for key in COMPARISON_DATA.keys():
                if key == '设计方案':
                    continue
                row = [key] + COMPARISON_DATA[key]
                writer.writerow(row)
        
        print(f"✓ 对比数据CSV已导出: {output_file}")
        return output_file
    
    def export_comparison_json(self):
        """导出对比数据为JSON"""
        output_file = os.path.join(self.output_dir, 'comparison_data.json')
        
        # 转换为更友好的JSON结构
        json_data = []
        for i, scheme in enumerate(COMPARISON_DATA['设计方案']):
            item = {'设计方案': scheme}
            for key in COMPARISON_DATA.keys():
                if key == '设计方案':
                    continue
                item[key] = COMPARISON_DATA[key][i]
            json_data.append(item)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 对比数据JSON已导出: {output_file}")
        return output_file
    
    def export_performance_csv(self):
        """导出性能指标为CSV"""
        output_file = os.path.join(self.output_dir, 'performance_metrics.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = ['指标', '静态设计', 'L2级动态设计', 'L3级协调控制']
            writer.writerow(headers)
            
            # 获取所有指标
            metrics = list(PERFORMANCE_METRICS['静态设计'].keys())
            
            # 写入数据
            for metric in metrics:
                row = [metric]
                for scheme in ['静态设计', 'L2级动态设计', 'L3级协调控制']:
                    row.append(PERFORMANCE_METRICS[scheme][metric])
                writer.writerow(row)
        
        print(f"✓ 性能指标CSV已导出: {output_file}")
        return output_file
    
    def export_cost_csv(self):
        """导出成本分析为CSV"""
        output_file = os.path.join(self.output_dir, 'cost_analysis.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = ['成本项', '静态设计', 'L2级动态设计', 'L3级协调控制']
            writer.writerow(headers)
            
            # 获取所有成本项
            cost_items = list(COST_ANALYSIS['静态设计'].keys())
            
            # 写入数据
            for item in cost_items:
                row = [item]
                for scheme in ['静态设计', 'L2级动态设计', 'L3级协调控制']:
                    row.append(COST_ANALYSIS[scheme][item])
                writer.writerow(row)
        
        print(f"✓ 成本分析CSV已导出: {output_file}")
        return output_file
    
    def export_pid_csv(self):
        """导出PID参数为CSV"""
        output_file = os.path.join(self.output_dir, 'pid_parameters.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = ['参数组', 'Kp', 'Ki', 'Kd', '稳态误差(cm)', '最大误差(cm)']
            writer.writerow(headers)
            
            # 写入数据
            for param_set, values in PID_PARAMETERS.items():
                row = [param_set, values['Kp'], values['Ki'], values['Kd'],
                       values['稳态误差(cm)'], values['最大误差(cm)']]
                writer.writerow(row)
        
        print(f"✓ PID参数CSV已导出: {output_file}")
        return output_file
    
    def export_all_json(self):
        """导出所有数据为一个完整的JSON"""
        output_file = os.path.join(self.output_dir, 'all_data.json')
        
        all_data = {
            '元数据': {
                '导出时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '版本': 'v3.5-final',
                '项目': '静态设计与动态设计对比专题'
            },
            '对比数据': COMPARISON_DATA,
            '性能指标': PERFORMANCE_METRICS,
            '成本分析': COST_ANALYSIS,
            'PID参数': PID_PARAMETERS
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 完整数据JSON已导出: {output_file}")
        return output_file
    
    def generate_summary(self):
        """生成数据汇总文本"""
        output_file = os.path.join(self.output_dir, 'all_data_summary.txt')
        
        lines = []
        lines.append("="*80)
        lines.append("  数据汇总")
        lines.append("="*80)
        lines.append(f"\n导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 对比数据
        lines.append("【基础对比数据】")
        lines.append("-" * 80)
        schemes = COMPARISON_DATA['设计方案']
        lines.append(f"{'指标':<20} {schemes[0]:<15} {schemes[1]:<15} {schemes[2]:<15}")
        lines.append("-" * 80)
        for key in COMPARISON_DATA.keys():
            if key == '设计方案':
                continue
            values = COMPARISON_DATA[key]
            lines.append(f"{key:<20} {str(values[0]):<15} {str(values[1]):<15} {str(values[2]):<15}")
        lines.append("")
        
        # 性能指标
        lines.append("【性能指标】")
        lines.append("-" * 80)
        lines.append(f"{'指标':<20} {'静态':<12} {'L2级':<12} {'L3级':<12}")
        lines.append("-" * 80)
        metrics = list(PERFORMANCE_METRICS['静态设计'].keys())
        for metric in metrics[:8]:  # 只显示前8个
            v1 = PERFORMANCE_METRICS['静态设计'][metric]
            v2 = PERFORMANCE_METRICS['L2级动态设计'][metric]
            v3 = PERFORMANCE_METRICS['L3级协调控制'][metric]
            lines.append(f"{metric:<20} {str(v1):<12} {str(v2):<12} {str(v3):<12}")
        lines.append("")
        
        # 成本分析
        lines.append("【成本分析】")
        lines.append("-" * 80)
        lines.append(f"{'成本项':<24} {'静态':<12} {'L2级':<12} {'L3级':<12}")
        lines.append("-" * 80)
        cost_items = list(COST_ANALYSIS['静态设计'].keys())
        for item in cost_items:
            v1 = COST_ANALYSIS['静态设计'][item]
            v2 = COST_ANALYSIS['L2级动态设计'][item]
            v3 = COST_ANALYSIS['L3级协调控制'][item]
            lines.append(f"{item:<24} {str(v1):<12} {str(v2):<12} {str(v3):<12}")
        lines.append("")
        
        # PID参数
        lines.append("【PID参数推荐】")
        lines.append("-" * 80)
        lines.append(f"{'参数组':<20} {'Kp':<8} {'Ki':<8} {'Kd':<8} {'稳态误差':<12}")
        lines.append("-" * 80)
        for param_set, values in PID_PARAMETERS.items():
            lines.append(f"{param_set:<20} {values['Kp']:<8.2f} {values['Ki']:<8.2f} "
                        f"{values['Kd']:<8.2f} {str(values['稳态误差(cm)']):<12}")
        lines.append("")
        
        lines.append("="*80)
        
        summary_text = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        print(f"✓ 数据汇总已保存: {output_file}")
        
        return summary_text
    
    def export_all(self):
        """导出所有格式"""
        print("\n【导出所有数据】")
        print("-" * 80)
        
        files = []
        
        # CSV格式
        files.append(self.export_comparison_csv())
        files.append(self.export_performance_csv())
        files.append(self.export_cost_csv())
        files.append(self.export_pid_csv())
        
        # JSON格式
        files.append(self.export_comparison_json())
        files.append(self.export_all_json())
        
        # 汇总文本
        summary_text = self.generate_summary()
        
        return files, summary_text

# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("【数据导出】")
    print("-" * 80)
    print("导出格式: CSV, JSON, TXT")
    print()
    
    exporter = DataExporter()
    
    files, summary = exporter.export_all()
    
    print()
    print("="*80)
    print("  导出完成!")
    print("="*80)
    print()
    print(f"输出目录: {exporter.output_dir}/")
    print(f"文件数量: {len(files) + 1}")
    print()
    print("导出的文件:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {os.path.basename(f)}")
    print(f"  {len(files)+1}. all_data_summary.txt")
    print()
    print("数据汇总:")
    print(summary)
    print()
    print("="*80)
