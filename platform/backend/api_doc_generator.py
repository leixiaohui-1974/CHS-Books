#!/usr/bin/env python3
"""
API文档生成器
自动生成API文档和Postman集合
"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))


class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self):
        self.endpoints = []
        self.base_url = "http://localhost:8000"
    
    def add_endpoint(self, method: str, path: str, description: str, 
                    request_body: dict = None, response_body: dict = None):
        """添加端点"""
        self.endpoints.append({
            'method': method,
            'path': path,
            'description': description,
            'request_body': request_body,
            'response_body': response_body
        })
    
    def generate_markdown(self) -> str:
        """生成Markdown文档"""
        doc = []
        doc.append("# API文档\n")
        doc.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        doc.append(f"**基础URL**: {self.base_url}\n")
        doc.append("---\n")
        
        # 按模块分组
        modules = {}
        for endpoint in self.endpoints:
            module = endpoint['path'].split('/')[3] if len(endpoint['path'].split('/')) > 3 else 'other'
            if module not in modules:
                modules[module] = []
            modules[module].append(endpoint)
        
        # 生成每个模块的文档
        for module, endpoints in modules.items():
            doc.append(f"## {module.title()} 模块\n")
            
            for endpoint in endpoints:
                doc.append(f"### {endpoint['method']} {endpoint['path']}\n")
                doc.append(f"{endpoint['description']}\n")
                
                if endpoint['request_body']:
                    doc.append("**请求体**:\n")
                    doc.append("```json\n")
                    doc.append(json.dumps(endpoint['request_body'], indent=2, ensure_ascii=False))
                    doc.append("\n```\n")
                
                if endpoint['response_body']:
                    doc.append("**响应体**:\n")
                    doc.append("```json\n")
                    doc.append(json.dumps(endpoint['response_body'], indent=2, ensure_ascii=False))
                    doc.append("\n```\n")
                
                doc.append("---\n")
        
        return '\n'.join(doc)
    
    def generate_postman_collection(self) -> dict:
        """生成Postman集合"""
        collection = {
            "info": {
                "name": "智能知识平台 V2.2 API",
                "description": "完整的API集合",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # 按模块分组
        modules = {}
        for endpoint in self.endpoints:
            module = endpoint['path'].split('/')[3] if len(endpoint['path'].split('/')) > 3 else 'other'
            if module not in modules:
                modules[module] = []
            modules[module].append(endpoint)
        
        # 生成每个模块的请求
        for module, endpoints in modules.items():
            folder = {
                "name": module.title(),
                "item": []
            }
            
            for endpoint in endpoints:
                request_item = {
                    "name": endpoint['description'],
                    "request": {
                        "method": endpoint['method'],
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": f"{self.base_url}{endpoint['path']}",
                            "protocol": "http",
                            "host": ["localhost"],
                            "port": "8000",
                            "path": endpoint['path'].split('/')[1:]
                        }
                    }
                }
                
                if endpoint['request_body']:
                    request_item['request']['body'] = {
                        "mode": "raw",
                        "raw": json.dumps(endpoint['request_body'], indent=2, ensure_ascii=False)
                    }
                
                folder['item'].append(request_item)
            
            collection['item'].append(folder)
        
        return collection
    
    def load_api_definitions(self):
        """加载API定义"""
        # 会话管理API
        self.add_endpoint(
            'POST', '/api/v2/sessions/create',
            '创建学习会话',
            request_body={
                "user_id": "user_001",
                "book_slug": "water-environment-simulation",
                "case_slug": "case_01_diffusion"
            },
            response_body={
                "session_id": "session_20251104_120000",
                "user_id": "user_001",
                "status": "active",
                "created_at": "2025-11-04T12:00:00Z"
            }
        )
        
        self.add_endpoint(
            'GET', '/api/v2/sessions/{session_id}',
            '获取会话信息',
            response_body={
                "session_id": "session_20251104_120000",
                "status": "active",
                "files": []
            }
        )
        
        self.add_endpoint(
            'POST', '/api/v2/sessions/{session_id}/pause',
            '暂停会话'
        )
        
        self.add_endpoint(
            'POST', '/api/v2/sessions/{session_id}/resume',
            '恢复会话'
        )
        
        # 代码管理API
        self.add_endpoint(
            'POST', '/api/v2/code/load',
            '加载案例代码',
            request_body={
                "book_slug": "water-environment-simulation",
                "case_slug": "case_01_diffusion"
            },
            response_body={
                "main_file": "main.py",
                "files": [
                    {"name": "main.py", "content": "...", "analysis": {}}
                ]
            }
        )
        
        self.add_endpoint(
            'POST', '/api/v2/code/analyze',
            '分析代码结构',
            request_body={"code": "def test(): pass"},
            response_body={
                "functions": 1,
                "classes": 0,
                "imports": []
            }
        )
        
        # 执行管理API
        self.add_endpoint(
            'POST', '/api/v2/execution/start',
            '启动代码执行',
            request_body={
                "session_id": "session_123",
                "script_path": "main.py",
                "parameters": {}
            },
            response_body={
                "execution_id": "exec_456",
                "status": "running"
            }
        )
        
        # AI助手API
        self.add_endpoint(
            'POST', '/api/v2/ai/explain-code',
            'AI代码讲解',
            request_body={
                "code": "def add(a, b): return a + b",
                "context": "加法函数"
            },
            response_body={
                "explanation": "这是一个简单的加法函数...",
                "key_points": ["使用def定义函数", "返回两数之和"]
            }
        )
        
        print(f"✓ 加载了 {len(self.endpoints)} 个API端点")


def main():
    """主函数"""
    print("=" * 70)
    print(" API文档生成器")
    print("=" * 70)
    print()
    
    generator = APIDocGenerator()
    
    # 加载API定义
    print("📚 加载API定义...")
    generator.load_api_definitions()
    print()
    
    # 生成Markdown文档
    print("📝 生成Markdown文档...")
    markdown = generator.generate_markdown()
    
    md_file = "API_REFERENCE.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✓ Markdown文档已生成: {md_file}")
    print()
    
    # 生成Postman集合
    print("📮 生成Postman集合...")
    collection = generator.generate_postman_collection()
    
    postman_file = "postman_collection.json"
    with open(postman_file, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Postman集合已生成: {postman_file}")
    print()
    
    print("=" * 70)
    print("✅ 文档生成完成")
    print("=" * 70)
    print()
    print("使用方法:")
    print(f"  • Markdown: cat {md_file}")
    print(f"  • Postman: 导入 {postman_file} 到Postman")


if __name__ == "__main__":
    main()
