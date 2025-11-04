#!/usr/bin/env python3
"""
实时监控仪表板
在终端中显示系统状态、性能指标和活动信息
"""

import asyncio
import time
from datetime import datetime
import psutil
import os


class Dashboard:
    """监控仪表板"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.active_sessions = 0
        self.active_executions = 0
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def get_system_stats(self):
        """获取系统统计"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'memory_used': memory.used / (1024**3),
            'memory_total': memory.total / (1024**3),
            'disk': disk.percent,
            'disk_used': disk.used / (1024**3),
            'disk_total': disk.total / (1024**3)
        }
    
    def format_uptime(self, seconds):
        """格式化运行时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_bar(self, percent, width=20):
        """生成进度条"""
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        
        # 颜色
        if percent < 60:
            color = '\033[92m'  # 绿色
        elif percent < 80:
            color = '\033[93m'  # 黄色
        else:
            color = '\033[91m'  # 红色
        
        return f"{color}{bar}\033[0m {percent:5.1f}%"
    
    def render(self):
        """渲染仪表板"""
        self.clear_screen()
        
        # 获取数据
        stats = self.get_system_stats()
        uptime = time.time() - self.start_time
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 标题
        print("╔" + "═" * 78 + "╗")
        print("║" + " 智能知识平台 V2.1 - 监控仪表板".center(78) + "║")
        print("╠" + "═" * 78 + "╣")
        print(f"║  时间: {now}          运行时间: {self.format_uptime(uptime)}" + " " * (78 - 50) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        # 系统资源
        print("┌─ 系统资源 " + "─" * 65 + "┐")
        print(f"│  CPU使用率:     {self.get_bar(stats['cpu'])}  │")
        print(f"│  内存使用率:    {self.get_bar(stats['memory'])}  │")
        print(f"│  内存详情:      {stats['memory_used']:.2f} GB / {stats['memory_total']:.2f} GB" + " " * 20 + "│")
        print(f"│  磁盘使用率:    {self.get_bar(stats['disk'])}  │")
        print(f"│  磁盘详情:      {stats['disk_used']:.2f} GB / {stats['disk_total']:.2f} GB" + " " * 20 + "│")
        print("└" + "─" * 77 + "┘")
        print()
        
        # 平台状态
        print("┌─ 平台状态 " + "─" * 65 + "┐")
        print(f"│  总请求数:      {self.request_count:,}".ljust(77) + " │")
        print(f"│  错误数:        {self.error_count:,}".ljust(77) + " │")
        print(f"│  错误率:        {(self.error_count / max(self.request_count, 1) * 100):.2f}%".ljust(77) + " │")
        print(f"│  活跃会话:      {self.active_sessions:,}".ljust(77) + " │")
        print(f"│  执行中任务:    {self.active_executions:,}".ljust(77) + " │")
        print("└" + "─" * 77 + "┘")
        print()
        
        # 服务状态
        print("┌─ 服务状态 " + "─" * 65 + "┐")
        
        services = [
            ("API服务", True, "http://localhost:8000"),
            ("PostgreSQL", self.check_service("postgresql"), "localhost:5432"),
            ("Redis", self.check_service("redis"), "localhost:6379"),
            ("MongoDB", self.check_service("mongodb"), "localhost:27017"),
        ]
        
        for service, status, addr in services:
            status_icon = "🟢" if status else "🔴"
            status_text = "运行中" if status else "未运行"
            print(f"│  {status_icon} {service.ljust(15)} {status_text.ljust(10)} {addr.ljust(40)}│")
        
        print("└" + "─" * 77 + "┘")
        print()
        
        # 最近活动
        print("┌─ 最近活动 " + "─" * 65 + "┐")
        print("│  [14:23:45] 用户 user_001 创建会话".ljust(77) + " │")
        print("│  [14:23:48] 会话 session_123 开始执行".ljust(77) + " │")
        print("│  [14:23:51] 执行 exec_456 完成".ljust(77) + " │")
        print("│  [14:23:55] AI请求处理完成 (2.3s)".ljust(77) + " │")
        print("└" + "─" * 77 + "┘")
        print()
        
        # 控制提示
        print("按 Ctrl+C 退出")
    
    def check_service(self, service_name):
        """检查服务状态（简化版）"""
        # 实际应该检查进程或端口
        return True  # 模拟
    
    async def update_loop(self, interval=2):
        """更新循环"""
        try:
            while True:
                self.render()
                
                # 模拟数据更新
                self.request_count += 1
                if self.request_count % 20 == 0:
                    self.error_count += 1
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n监控已停止")


async def main():
    """主函数"""
    dashboard = Dashboard()
    await dashboard.update_loop(interval=2)


if __name__ == "__main__":
    asyncio.run(main())
