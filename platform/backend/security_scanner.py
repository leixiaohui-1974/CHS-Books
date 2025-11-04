#!/usr/bin/env python3
"""
安全扫描工具
扫描代码安全漏洞和配置问题
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime


class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.info = []
        
        # 危险模式
        self.dangerous_patterns = {
            'sql_injection': [
                (r'execute\s*\(\s*["\'].*\%s.*["\']\s*\%', '可能的SQL注入'),
                (r'\.format\s*\(.*\)\s*\)', '使用format可能导致SQL注入'),
            ],
            'command_injection': [
                (r'os\.system\s*\(', '使用os.system可能导致命令注入'),
                (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', '启用shell可能导致命令注入'),
                (r'eval\s*\(', '使用eval存在代码注入风险'),
                (r'exec\s*\(', '使用exec存在代码注入风险'),
            ],
            'path_traversal': [
                (r'open\s*\([^)]*\+', '文件路径拼接可能导致路径遍历'),
                (r'os\.path\.join\s*\(.*input', '用户输入拼接路径存在风险'),
            ],
            'hardcoded_secrets': [
                (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
                (r'api_key\s*=\s*["\'][^"\']+["\']', '硬编码API密钥'),
                (r'secret\s*=\s*["\'][^"\']+["\']', '硬编码密钥'),
                (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', '硬编码令牌'),
            ],
            'weak_crypto': [
                (r'hashlib\.md5', '使用MD5哈希算法（已不安全）'),
                (r'hashlib\.sha1', '使用SHA1哈希算法（已不安全）'),
                (r'random\.random', '使用random模块（不适合安全用途）'),
            ]
        }
    
    def scan_code_files(self) -> Dict[str, Any]:
        """扫描代码文件"""
        print("🔍 扫描代码文件...")
        
        backend_dir = Path(__file__).parent
        py_files = list(backend_dir.rglob("*.py"))
        
        scanned = 0
        issues_found = 0
        
        for py_file in py_files:
            if '__pycache__' in str(py_file) or 'venv' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                scanned += 1
                
                # 检查每种漏洞模式
                for vuln_type, patterns in self.dangerous_patterns.items():
                    for pattern, description in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # 找到匹配的行号
                            line_num = content[:match.start()].count('\n') + 1
                            
                            self.vulnerabilities.append({
                                'type': vuln_type,
                                'severity': 'high' if vuln_type in ['sql_injection', 'command_injection'] else 'medium',
                                'file': str(py_file.relative_to(backend_dir)),
                                'line': line_num,
                                'description': description,
                                'code': lines[line_num - 1].strip() if line_num <= len(lines) else ''
                            })
                            issues_found += 1
            
            except Exception as e:
                pass
        
        return {
            'files_scanned': scanned,
            'issues_found': issues_found,
            'by_severity': {
                'high': len([v for v in self.vulnerabilities if v['severity'] == 'high']),
                'medium': len([v for v in self.vulnerabilities if v['severity'] == 'medium']),
                'low': len([v for v in self.vulnerabilities if v['severity'] == 'low'])
            }
        }
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """扫描依赖包安全"""
        print("🔍 扫描依赖包...")
        
        requirements_file = Path(__file__).parent / 'requirements.txt'
        
        result = {
            'total_packages': 0,
            'potential_risks': []
        }
        
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            result['total_packages'] = len(packages)
            
            # 检查是否固定版本
            for pkg in packages:
                if '==' not in pkg and '>=' not in pkg:
                    self.warnings.append({
                        'type': 'dependency',
                        'severity': 'medium',
                        'description': f"依赖包未固定版本: {pkg}",
                        'recommendation': '建议使用==固定版本号'
                    })
                    result['potential_risks'].append(pkg)
        
        return result
    
    def scan_config_files(self) -> Dict[str, Any]:
        """扫描配置文件"""
        print("🔍 扫描配置文件...")
        
        backend_dir = Path(__file__).parent
        
        result = {
            'files_checked': 0,
            'issues': []
        }
        
        # 检查.env文件
        env_file = backend_dir / '.env'
        env_example = backend_dir / '.env.example'
        
        if env_file.exists():
            result['files_checked'] += 1
            
            # 检查.env是否在.gitignore中
            gitignore = backend_dir.parent / '.gitignore'
            if gitignore.exists():
                with open(gitignore, 'r') as f:
                    gitignore_content = f.read()
                
                if '.env' not in gitignore_content:
                    self.vulnerabilities.append({
                        'type': 'config',
                        'severity': 'high',
                        'file': '.env',
                        'description': '.env文件未加入.gitignore',
                        'recommendation': '立即将.env添加到.gitignore'
                    })
                    result['issues'].append('.env未被忽略')
        
        # 检查是否有.env.example
        if not env_example.exists() and env_file.exists():
            self.warnings.append({
                'type': 'config',
                'severity': 'low',
                'description': '缺少.env.example示例文件',
                'recommendation': '创建.env.example作为配置模板'
            })
        
        # 检查Docker配置
        docker_compose = backend_dir.parent / 'docker-compose.v2.yml'
        if docker_compose.exists():
            result['files_checked'] += 1
            
            with open(docker_compose, 'r') as f:
                compose_content = f.read()
            
            # 检查默认密码
            if 'password: postgres' in compose_content or 'PASSWORD=password' in compose_content:
                self.vulnerabilities.append({
                    'type': 'config',
                    'severity': 'high',
                    'file': 'docker-compose.v2.yml',
                    'description': '使用默认密码',
                    'recommendation': '更改为强密码'
                })
                result['issues'].append('默认密码')
        
        return result
    
    def scan_api_security(self) -> Dict[str, Any]:
        """扫描API安全"""
        print("🔍 扫描API安全...")
        
        api_dir = Path(__file__).parent / 'app' / 'api'
        
        result = {
            'endpoints_checked': 0,
            'missing_auth': [],
            'missing_validation': []
        }
        
        if api_dir.exists():
            for api_file in api_dir.rglob("*.py"):
                try:
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 查找所有端点
                    endpoints = re.findall(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)', content)
                    result['endpoints_checked'] += len(endpoints)
                    
                    # 检查是否有依赖注入（认证）
                    has_depends = 'Depends(' in content
                    
                    if endpoints and not has_depends:
                        self.warnings.append({
                            'type': 'api',
                            'severity': 'high',
                            'file': str(api_file.name),
                            'description': '端点可能缺少身份认证',
                            'recommendation': '添加认证依赖'
                        })
                        result['missing_auth'].append(api_file.name)
                    
                    # 检查输入验证
                    has_pydantic = 'BaseModel' in content or 'from pydantic' in content
                    
                    if 'post' in str(endpoints) and not has_pydantic:
                        self.warnings.append({
                            'type': 'api',
                            'severity': 'medium',
                            'file': str(api_file.name),
                            'description': 'POST端点可能缺少输入验证',
                            'recommendation': '使用Pydantic模型验证输入'
                        })
                        result['missing_validation'].append(api_file.name)
                
                except Exception:
                    pass
        
        return result
    
    def scan_file_permissions(self) -> Dict[str, Any]:
        """扫描文件权限"""
        print("🔍 扫描文件权限...")
        
        backend_dir = Path(__file__).parent
        
        result = {
            'files_checked': 0,
            'world_writable': [],
            'executable_not_marked': []
        }
        
        for py_file in backend_dir.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            
            result['files_checked'] += 1
            
            try:
                stat = os.stat(py_file)
                mode = stat.st_mode
                
                # 检查是否全局可写（危险）
                if mode & 0o002:
                    self.vulnerabilities.append({
                        'type': 'permission',
                        'severity': 'high',
                        'file': str(py_file.relative_to(backend_dir)),
                        'description': '文件全局可写',
                        'recommendation': '修改权限：chmod 644'
                    })
                    result['world_writable'].append(str(py_file.name))
                
                # 检查执行权限
                if py_file.name.endswith('_tool.py') or py_file.name in ['manage.py', 'deploy.py']:
                    if not (mode & 0o100):
                        self.info.append({
                            'type': 'permission',
                            'file': str(py_file.relative_to(backend_dir)),
                            'description': '工具脚本未设置执行权限',
                            'recommendation': f'chmod +x {py_file}'
                        })
            
            except Exception:
                pass
        
        return result
    
    def generate_report(self) -> str:
        """生成安全报告"""
        report = []
        report.append("\n" + "=" * 70)
        report.append(" 安全扫描报告")
        report.append("=" * 70)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 统计
        high = len([v for v in self.vulnerabilities if v.get('severity') == 'high'])
        medium = len([v for v in self.vulnerabilities if v.get('severity') == 'medium'])
        low = len([v for v in self.vulnerabilities if v.get('severity') == 'low'])
        
        report.append("📊 扫描统计:")
        report.append("-" * 70)
        report.append(f"  高危漏洞:   {high}")
        report.append(f"  中危漏洞:   {medium}")
        report.append(f"  低危漏洞:   {low}")
        report.append(f"  警告:       {len(self.warnings)}")
        report.append(f"  信息:       {len(self.info)}")
        report.append("")
        
        # 高危漏洞
        if high > 0:
            report.append("🔴 高危漏洞:")
            report.append("-" * 70)
            for vuln in self.vulnerabilities:
                if vuln.get('severity') == 'high':
                    report.append(f"  [{vuln['type'].upper()}] {vuln['description']}")
                    report.append(f"  文件: {vuln.get('file', 'N/A')}")
                    if 'line' in vuln:
                        report.append(f"  行号: {vuln['line']}")
                    if 'code' in vuln and vuln['code']:
                        report.append(f"  代码: {vuln['code'][:60]}...")
                    if 'recommendation' in vuln:
                        report.append(f"  建议: {vuln['recommendation']}")
                    report.append("")
        
        # 中危漏洞
        if medium > 0:
            report.append("🟡 中危漏洞:")
            report.append("-" * 70)
            for vuln in self.vulnerabilities[:5]:  # 显示前5个
                if vuln.get('severity') == 'medium':
                    report.append(f"  [{vuln['type'].upper()}] {vuln['description']}")
                    report.append(f"  文件: {vuln.get('file', 'N/A')}")
                    report.append("")
        
        # 安全建议
        report.append("💡 安全建议:")
        report.append("-" * 70)
        
        suggestions = [
            "1. 定期更新依赖包，修复已知漏洞",
            "2. 使用环境变量管理敏感信息",
            "3. 启用HTTPS加密传输",
            "4. 实施输入验证和输出编码",
            "5. 添加速率限制防止滥用",
            "6. 定期进行安全审计",
            "7. 使用强密码策略",
            "8. 启用日志监控和告警"
        ]
        
        for suggestion in suggestions:
            report.append(f"  {suggestion}")
        
        report.append("")
        report.append("=" * 70)
        
        if high == 0 and medium == 0:
            report.append("✅ 未发现明显安全漏洞")
        else:
            report.append(f"⚠️  发现 {high + medium} 个需要关注的安全问题")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_json(self, filename: str):
        """导出JSON报告"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'high': len([v for v in self.vulnerabilities if v.get('severity') == 'high']),
                'medium': len([v for v in self.vulnerabilities if v.get('severity') == 'medium']),
                'low': len([v for v in self.vulnerabilities if v.get('severity') == 'low']),
                'warnings': len(self.warnings),
                'info': len(self.info)
            },
            'vulnerabilities': self.vulnerabilities,
            'warnings': self.warnings,
            'info': self.info
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 JSON报告已导出: {filename}")
    
    def run_scan(self):
        """运行完整扫描"""
        print("=" * 70)
        print(" 安全扫描工具")
        print("=" * 70)
        print()
        
        # 代码扫描
        code_result = self.scan_code_files()
        print(f"✓ 代码文件扫描完成 (扫描{code_result['files_scanned']}个文件)")
        
        # 依赖扫描
        dep_result = self.scan_dependencies()
        print(f"✓ 依赖包扫描完成 (检查{dep_result['total_packages']}个包)")
        
        # 配置扫描
        config_result = self.scan_config_files()
        print(f"✓ 配置文件扫描完成")
        
        # API扫描
        api_result = self.scan_api_security()
        print(f"✓ API安全扫描完成 (检查{api_result['endpoints_checked']}个端点)")
        
        # 权限扫描
        perm_result = self.scan_file_permissions()
        print(f"✓ 文件权限扫描完成")
        
        # 生成报告
        print(self.generate_report())
        
        # 导出JSON
        filename = f"security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.export_json(filename)


def main():
    """主函数"""
    scanner = SecurityScanner()
    scanner.run_scan()


if __name__ == "__main__":
    main()
