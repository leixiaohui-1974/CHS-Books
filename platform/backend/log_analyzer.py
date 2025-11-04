#!/usr/bin/env python3
"""
日志分析工具
分析应用日志，提取关键信息和统计数据
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List
import json


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or "/var/log/platform/app.log"
        self.logs = []
        self.stats = defaultdict(int)
    
    def parse_log_line(self, line: str) -> Dict:
        """解析日志行"""
        # 简化的日志格式解析
        # 2025-11-04 14:23:45 | INFO | module.function:123 | Message
        
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\|\s+(\w+)\s+\|\s+([\w.]+):(\d+)\s+\|\s+(.+)'
        
        match = re.match(pattern, line)
        if match:
            timestamp, level, location, lineno, message = match.groups()
            return {
                'timestamp': timestamp,
                'level': level,
                'location': location,
                'lineno': int(lineno),
                'message': message
            }
        
        return None
    
    def load_logs(self, limit: int = None):
        """加载日志文件"""
        print(f"📂 加载日志: {self.log_file}")
        
        try:
            log_path = Path(self.log_file)
            
            if not log_path.exists():
                print(f"⚠️  日志文件不存在，使用模拟数据")
                self.generate_sample_logs()
                return
            
            with open(log_path, 'r') as f:
                lines = f.readlines()
                
                if limit:
                    lines = lines[-limit:]
                
                for line in lines:
                    parsed = self.parse_log_line(line.strip())
                    if parsed:
                        self.logs.append(parsed)
            
            print(f"✓ 加载了 {len(self.logs)} 条日志")
            
        except Exception as e:
            print(f"✗ 加载失败: {e}")
            self.generate_sample_logs()
    
    def generate_sample_logs(self):
        """生成示例日志"""
        sample_logs = [
            {'timestamp': '2025-11-04 14:23:45', 'level': 'INFO', 'location': 'app.main', 'lineno': 45, 'message': 'Application started'},
            {'timestamp': '2025-11-04 14:23:46', 'level': 'INFO', 'location': 'app.api.sessions', 'lineno': 120, 'message': 'Session created: session_001'},
            {'timestamp': '2025-11-04 14:23:48', 'level': 'INFO', 'location': 'app.services.execution', 'lineno': 89, 'message': 'Execution started: exec_001'},
            {'timestamp': '2025-11-04 14:23:50', 'level': 'WARNING', 'location': 'app.services.execution', 'lineno': 156, 'message': 'High memory usage detected'},
            {'timestamp': '2025-11-04 14:23:52', 'level': 'INFO', 'location': 'app.services.execution', 'lineno': 234, 'message': 'Execution completed: exec_001'},
            {'timestamp': '2025-11-04 14:23:55', 'level': 'ERROR', 'location': 'app.services.ai', 'lineno': 67, 'message': 'API rate limit exceeded'},
            {'timestamp': '2025-11-04 14:23:58', 'level': 'INFO', 'location': 'app.api.sessions', 'lineno': 145, 'message': 'Session terminated: session_001'},
        ]
        
        self.logs = sample_logs * 10  # 重复以增加数量
        print(f"✓ 生成了 {len(self.logs)} 条示例日志")
    
    def analyze(self):
        """分析日志"""
        print("\n📊 分析日志...")
        
        # 按级别统计
        level_counter = Counter(log['level'] for log in self.logs)
        self.stats['by_level'] = dict(level_counter)
        
        # 按模块统计
        location_counter = Counter(log['location'] for log in self.logs)
        self.stats['by_module'] = dict(location_counter.most_common(10))
        
        # 错误统计
        errors = [log for log in self.logs if log['level'] == 'ERROR']
        error_messages = Counter(log['message'] for log in errors)
        self.stats['top_errors'] = dict(error_messages.most_common(5))
        
        # 时间范围
        if self.logs:
            self.stats['time_range'] = {
                'start': self.logs[0]['timestamp'],
                'end': self.logs[-1]['timestamp']
            }
        
        # 统计总数
        self.stats['total'] = len(self.logs)
        self.stats['error_rate'] = len(errors) / max(len(self.logs), 1) * 100
        
        print("✓ 分析完成")
    
    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 70)
        report.append(" 日志分析报告")
        report.append("=" * 70)
        report.append("")
        
        # 基本信息
        report.append("📋 基本信息")
        report.append("-" * 70)
        report.append(f"  日志文件: {self.log_file}")
        report.append(f"  总日志数: {self.stats['total']:,}")
        if 'time_range' in self.stats:
            report.append(f"  时间范围: {self.stats['time_range']['start']} 至 {self.stats['time_range']['end']}")
        report.append("")
        
        # 日志级别分布
        report.append("📊 日志级别分布")
        report.append("-" * 70)
        for level, count in sorted(self.stats['by_level'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / self.stats['total'] * 100
            bar = '█' * int(percentage / 2)
            report.append(f"  {level.ljust(10)} {count:6,} ({percentage:5.1f}%)  {bar}")
        report.append("")
        
        # 错误率
        report.append("⚠️  错误统计")
        report.append("-" * 70)
        report.append(f"  错误率: {self.stats['error_rate']:.2f}%")
        
        if self.stats.get('top_errors'):
            report.append("\n  常见错误:")
            for error, count in self.stats['top_errors'].items():
                report.append(f"    • {error[:60]} ({count}次)")
        report.append("")
        
        # 热点模块
        report.append("🔥 活跃模块 (Top 10)")
        report.append("-" * 70)
        for module, count in self.stats['by_module'].items():
            report.append(f"  {module.ljust(40)} {count:6,} 条日志")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_json(self, output_file: str):
        """导出JSON格式"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'sample_logs': self.logs[:10]  # 只导出前10条作为样本
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 导出JSON: {output_file}")


def main():
    """主函数"""
    print("=" * 70)
    print(" 智能知识平台 - 日志分析工具")
    print("=" * 70)
    print()
    
    # 创建分析器
    analyzer = LogAnalyzer()
    
    # 加载日志
    analyzer.load_logs(limit=1000)  # 分析最近1000条
    
    # 分析
    analyzer.analyze()
    
    # 生成报告
    report = analyzer.generate_report()
    print(report)
    
    # 导出
    output_file = f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.export_json(output_file)
    
    print()
    print("💡 提示:")
    print("  • 修改 log_file 参数可以分析不同的日志文件")
    print("  • 使用 limit 参数可以限制分析的日志数量")
    print("  • JSON导出文件可用于进一步分析或可视化")


if __name__ == "__main__":
    main()
