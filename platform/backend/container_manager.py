#!/usr/bin/env python3
"""
容器管理工具
管理和监控Docker容器
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path


class ContainerManager:
    """容器管理器"""
    
    def __init__(self):
        self.project_name = "platform"
    
    def run_command(self, cmd: str) -> tuple:
        """运行命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def list_containers(self):
        """列出所有容器"""
        print("📦 容器列表")
        print("-" * 80)
        
        success, stdout, stderr = self.run_command(
            f"docker ps -a --filter name={self.project_name}"
        )
        
        if success:
            print(stdout)
        else:
            print(f"⚠️  获取容器列表失败: {stderr}")
        
        print()
    
    def show_stats(self):
        """显示容器统计"""
        print("📊 容器统计")
        print("-" * 80)
        
        # 获取所有容器
        success, stdout, stderr = self.run_command(
            f"docker ps -a --filter name={self.project_name} --format '{{{{.Names}}}}|{{{{.Status}}}}'"
        )
        
        if not success:
            print(f"⚠️  获取统计失败: {stderr}")
            return
        
        lines = stdout.strip().split('\n')
        lines = [l for l in lines if l]
        
        running = sum(1 for l in lines if 'Up' in l)
        stopped = sum(1 for l in lines if 'Exited' in l)
        total = len(lines)
        
        print(f"总容器数:   {total}")
        print(f"运行中:     {running}")
        print(f"已停止:     {stopped}")
        print()
    
    def show_logs(self, container: str = "backend", lines: int = 50):
        """显示容器日志"""
        print(f"📋 容器日志: {container} (最近{lines}行)")
        print("-" * 80)
        
        success, stdout, stderr = self.run_command(
            f"docker logs --tail {lines} {self.project_name}_{container}_1 2>&1 || "
            f"docker logs --tail {lines} {self.project_name}-{container}-1 2>&1"
        )
        
        if success and stdout:
            print(stdout)
        else:
            print(f"⚠️  获取日志失败: {stderr}")
        
        print()
    
    def inspect_container(self, container: str):
        """检查容器详情"""
        print(f"🔍 容器详情: {container}")
        print("-" * 80)
        
        success, stdout, stderr = self.run_command(
            f"docker inspect {self.project_name}_{container}_1 2>&1 || "
            f"docker inspect {self.project_name}-{container}-1 2>&1"
        )
        
        if success and stdout:
            try:
                data = json.loads(stdout)
                if data and len(data) > 0:
                    container_info = data[0]
                    
                    # 状态
                    state = container_info.get('State', {})
                    print(f"状态:       {state.get('Status', 'unknown')}")
                    print(f"启动时间:   {state.get('StartedAt', 'N/A')}")
                    print(f"运行中:     {state.get('Running', False)}")
                    
                    # 网络
                    networks = container_info.get('NetworkSettings', {}).get('Networks', {})
                    print(f"网络:       {', '.join(networks.keys())}")
                    
                    # 资源
                    config = container_info.get('HostConfig', {})
                    memory = config.get('Memory', 0)
                    if memory > 0:
                        print(f"内存限制:   {memory / (1024**3):.2f} GB")
            
            except json.JSONDecodeError:
                print("解析容器信息失败")
        else:
            print(f"⚠️  获取详情失败")
        
        print()
    
    def restart_container(self, container: str):
        """重启容器"""
        print(f"🔄 重启容器: {container}...")
        
        success, stdout, stderr = self.run_command(
            f"docker restart {self.project_name}_{container}_1 2>&1 || "
            f"docker restart {self.project_name}-{container}-1 2>&1"
        )
        
        if success:
            print(f"✓ 容器已重启")
        else:
            print(f"✗ 重启失败: {stderr}")
        
        print()
    
    def clean_containers(self):
        """清理停止的容器"""
        print("🧹 清理停止的容器...")
        
        success, stdout, stderr = self.run_command(
            "docker container prune -f"
        )
        
        if success:
            print(f"✓ 清理完成")
            if stdout:
                print(stdout)
        else:
            print(f"✗ 清理失败: {stderr}")
        
        print()
    
    def show_resource_usage(self):
        """显示资源使用"""
        print("💻 资源使用情况")
        print("-" * 80)
        
        success, stdout, stderr = self.run_command(
            f"docker stats --no-stream --filter name={self.project_name}"
        )
        
        if success and stdout:
            print(stdout)
        else:
            print(f"⚠️  获取资源使用失败")
        
        print()
    
    def export_info(self):
        """导出容器信息"""
        print("📤 导出容器信息...")
        
        # 获取容器列表
        success, stdout, stderr = self.run_command(
            f"docker ps -a --filter name={self.project_name} --format '{{{{json .}}}}'"
        )
        
        if not success:
            print(f"✗ 导出失败: {stderr}")
            return
        
        containers = []
        for line in stdout.strip().split('\n'):
            if line:
                try:
                    containers.append(json.loads(line))
                except:
                    pass
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'project': self.project_name,
            'containers': containers
        }
        
        filename = f"containers_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ 信息已导出: {filename}")
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Docker容器管理工具')
    parser.add_argument('command', 
                       choices=['list', 'stats', 'logs', 'inspect', 'restart', 'clean', 'usage', 'export'],
                       help='命令')
    parser.add_argument('--container', default='backend', help='容器名称')
    parser.add_argument('--lines', type=int, default=50, help='日志行数')
    
    args = parser.parse_args()
    
    print()
    print("=" * 80)
    print(" Docker容器管理工具")
    print("=" * 80)
    print()
    
    manager = ContainerManager()
    
    if args.command == 'list':
        manager.list_containers()
    
    elif args.command == 'stats':
        manager.show_stats()
    
    elif args.command == 'logs':
        manager.show_logs(args.container, args.lines)
    
    elif args.command == 'inspect':
        manager.inspect_container(args.container)
    
    elif args.command == 'restart':
        manager.restart_container(args.container)
    
    elif args.command == 'clean':
        manager.clean_containers()
    
    elif args.command == 'usage':
        manager.show_resource_usage()
    
    elif args.command == 'export':
        manager.export_info()


if __name__ == "__main__":
    main()
