"""
性能监控工具
实时监控系统性能、资源使用、API响应时间等
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List
import psutil


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "cpu_percent": [],
            "memory_percent": [],
            "api_response_times": [],
            "container_count": [],
            "active_sessions": []
        }
        self.start_time = time.time()
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used / (1024**3),  # GB
                "total": psutil.virtual_memory().total / (1024**3)  # GB
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent,
                "used": psutil.disk_usage('/').used / (1024**3),  # GB
                "total": psutil.disk_usage('/').total / (1024**3)  # GB
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def record_metric(self, metric_name: str, value: float):
        """记录指标"""
        if metric_name in self.metrics:
            self.metrics[metric_name].append({
                "value": value,
                "timestamp": time.time()
            })
            
            # 只保留最近1000条记录
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name].pop(0)
    
    def get_average(self, metric_name: str, last_n: int = 10) -> float:
        """获取平均值"""
        if metric_name not in self.metrics:
            return 0.0
        
        recent = self.metrics[metric_name][-last_n:]
        if not recent:
            return 0.0
        
        return sum(m["value"] for m in recent) / len(recent)
    
    def get_report(self) -> str:
        """生成性能报告"""
        uptime = time.time() - self.start_time
        
        report = []
        report.append("=" * 60)
        report.append(" 性能监控报告")
        report.append("=" * 60)
        report.append("")
        
        # 运行时间
        report.append(f"运行时间: {uptime/3600:.2f} 小时")
        report.append("")
        
        # 系统资源
        metrics = self.get_system_metrics()
        report.append("系统资源:")
        report.append(f"  CPU使用率: {metrics['cpu_percent']:.1f}%")
        report.append(f"  内存使用率: {metrics['memory']['percent']:.1f}%")
        report.append(f"  内存使用: {metrics['memory']['used']:.2f}GB / {metrics['memory']['total']:.2f}GB")
        report.append(f"  磁盘使用率: {metrics['disk']['percent']:.1f}%")
        report.append("")
        
        # 平均指标
        if self.metrics["api_response_times"]:
            avg_response = self.get_average("api_response_times")
            report.append(f"平均API响应时间: {avg_response:.3f}秒")
        
        if self.metrics["active_sessions"]:
            avg_sessions = self.get_average("active_sessions")
            report.append(f"平均活跃会话数: {avg_sessions:.0f}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    async def monitor_loop(self, interval: int = 5):
        """监控循环"""
        print("🔍 性能监控已启动...")
        print(f"监控间隔: {interval}秒")
        print()
        
        try:
            while True:
                metrics = self.get_system_metrics()
                
                # 记录指标
                self.record_metric("cpu_percent", metrics["cpu_percent"])
                self.record_metric("memory_percent", metrics["memory"]["percent"])
                
                # 显示实时信息
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {metrics['cpu_percent']:.1f}% | "
                      f"内存: {metrics['memory']['percent']:.1f}% | "
                      f"磁盘: {metrics['disk']['percent']:.1f}%", 
                      end="", flush=True)
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n监控已停止")
            print(self.get_report())


async def main():
    """主函数"""
    monitor = PerformanceMonitor()
    
    print("=" * 60)
    print(" 智能知识平台 V2.0 - 性能监控工具")
    print("=" * 60)
    print()
    
    # 显示初始指标
    metrics = monitor.get_system_metrics()
    print("当前系统状态:")
    print(f"  CPU使用率: {metrics['cpu_percent']:.1f}%")
    print(f"  内存使用: {metrics['memory']['used']:.2f}GB / {metrics['memory']['total']:.2f}GB ({metrics['memory']['percent']:.1f}%)")
    print(f"  磁盘使用: {metrics['disk']['used']:.2f}GB / {metrics['disk']['total']:.2f}GB ({metrics['disk']['percent']:.1f}%)")
    print()
    
    # 启动监控
    await monitor.monitor_loop(interval=5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见！")
