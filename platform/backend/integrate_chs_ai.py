#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合chs-ai知识库和平台到CHS-Books项目
使用说明：
1. 请先手动下载 https://github.com/leixiaohui-1974/chs-ai 到 E:\OneDrive\Documents\GitHub\Test\chs-ai
2. 然后运行此脚本: python integrate_chs_ai.py
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict
import re

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CHS_AI_PATH = PROJECT_ROOT.parent / "chs-ai"
TARGET_KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge-base"
TARGET_PLATFORM = PROJECT_ROOT / "platform"

print("="*70)
print("  CHS-AI 知识库与平台整合脚本")
print("="*70)
print(f"\n项目根目录: {PROJECT_ROOT}")
print(f"CHS-AI源目录: {CHS_AI_PATH}")
print(f"目标知识库: {TARGET_KNOWLEDGE_BASE}")
print(f"目标平台: {TARGET_PLATFORM}")

def check_chs_ai_exists():
    """检查chs-ai目录是否存在"""
    if not CHS_AI_PATH.exists():
        print(f"\n[ERROR] 未找到chs-ai目录: {CHS_AI_PATH}")
        print("\n请按以下步骤操作：")
        print("1. 访问 https://github.com/leixiaohui-1974/chs-ai")
        print("2. 点击 'Code' -> 'Download ZIP'")
        print(f"3. 解压到: {CHS_AI_PATH}")
        print("4. 重新运行此脚本")
        return False
    
    print(f"\n[OK] 找到chs-ai目录")
    return True

def analyze_chs_ai_structure():
    """分析chs-ai的目录结构"""
    print(f"\n{'='*70}")
    print("  分析chs-ai目录结构")
    print(f"{'='*70}")
    
    structure = {
        'knowledge': [],
        'platform': [],
        'docs': [],
        'code': [],
        'other': []
    }
    
    for item in CHS_AI_PATH.iterdir():
        if item.is_dir():
            item_type = classify_directory(item)
            structure[item_type].append({
                'name': item.name,
                'path': item,
                'files': count_files(item)
            })
            print(f"  [{item_type.upper()}] {item.name} ({count_files(item)} 文件)")
    
    return structure

def classify_directory(path: Path) -> str:
    """分类目录类型"""
    name = path.name.lower()
    
    if 'knowledge' in name or 'docs' in name or 'wiki' in name:
        return 'knowledge'
    elif 'platform' in name or 'web' in name or 'frontend' in name or 'backend' in name:
        return 'platform'
    elif 'doc' in name or 'tutorial' in name:
        return 'docs'
    elif 'code' in name or 'example' in name or 'src' in name:
        return 'code'
    else:
        return 'other'

def count_files(path: Path) -> int:
    """统计目录下的文件数"""
    count = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                count += 1
    except:
        pass
    return count

def integrate_knowledge_base(structure: Dict):
    """整合知识库"""
    print(f"\n{'='*70}")
    print("  整合知识库")
    print(f"{'='*70}")
    
    # 创建目标知识库目录
    TARGET_KNOWLEDGE_BASE.mkdir(parents=True, exist_ok=True)
    
    # 整合知识内容
    knowledge_items = structure.get('knowledge', []) + structure.get('docs', [])
    
    for item in knowledge_items:
        source = item['path']
        target = TARGET_KNOWLEDGE_BASE / item['name']
        
        print(f"\n正在整合: {item['name']}")
        print(f"  源: {source}")
        print(f"  目标: {target}")
        
        try:
            if target.exists():
                print(f"  [SKIP] 目标已存在，跳过")
            else:
                shutil.copytree(source, target)
                print(f"  [OK] 复制完成 ({item['files']} 文件)")
        except Exception as e:
            print(f"  [ERROR] 复制失败: {e}")
    
    # 创建知识库索引
    create_knowledge_index()

def create_knowledge_index():
    """创建知识库索引"""
    print(f"\n创建知识库索引...")
    
    index = {
        'categories': [],
        'total_items': 0
    }
    
    # 扫描所有Markdown文件
    for md_file in TARGET_KNOWLEDGE_BASE.rglob('*.md'):
        if md_file.name.lower() in ['readme.md', 'index.md']:
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem
            
            # 分类
            category = md_file.parent.name
            
            # 添加到索引
            category_data = next((c for c in index['categories'] if c['name'] == category), None)
            if not category_data:
                category_data = {'name': category, 'items': []}
                index['categories'].append(category_data)
            
            category_data['items'].append({
                'title': title,
                'file': str(md_file.relative_to(TARGET_KNOWLEDGE_BASE)),
                'path': str(md_file)
            })
            
            index['total_items'] += 1
        
        except Exception as e:
            print(f"  [WARN] 处理失败 {md_file.name}: {e}")
    
    # 保存索引
    index_file = TARGET_KNOWLEDGE_BASE / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"  [OK] 知识库索引已创建")
    print(f"  总计: {index['total_items']} 个知识点")
    print(f"  分类: {len(index['categories'])} 个")

def integrate_platform_code(structure: Dict):
    """整合平台代码"""
    print(f"\n{'='*70}")
    print("  整合平台代码")
    print(f"{'='*70}")
    
    platform_items = structure.get('platform', [])
    
    for item in platform_items:
        source = item['path']
        
        print(f"\n正在分析: {item['name']}")
        
        # 检测平台类型
        if (source / 'frontend').exists():
            integrate_frontend(source / 'frontend')
        if (source / 'backend').exists():
            integrate_backend(source / 'backend')
        if (source / 'api').exists():
            integrate_api(source / 'api')

def integrate_frontend(source: Path):
    """整合前端代码"""
    print(f"  发现前端代码: {source}")
    
    target = TARGET_PLATFORM / 'frontend' / 'chs-ai-components'
    target.mkdir(parents=True, exist_ok=True)
    
    # 复制前端组件
    for item in source.rglob('*'):
        if item.is_file() and item.suffix in ['.vue', '.js', '.ts', '.css', '.html']:
            rel_path = item.relative_to(source)
            target_file = target / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.copy2(item, target_file)
                print(f"    [OK] 复制: {rel_path}")
            except Exception as e:
                print(f"    [ERROR] 失败: {rel_path} - {e}")

def integrate_backend(source: Path):
    """整合后端代码"""
    print(f"  发现后端代码: {source}")
    
    target = TARGET_PLATFORM / 'backend' / 'chs_ai_services'
    target.mkdir(parents=True, exist_ok=True)
    
    # 复制后端服务
    for item in source.rglob('*.py'):
        rel_path = item.relative_to(source)
        target_file = target / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(item, target_file)
            print(f"    [OK] 复制: {rel_path}")
        except Exception as e:
            print(f"    [ERROR] 失败: {rel_path} - {e}")

def integrate_api(source: Path):
    """整合API定义"""
    print(f"  发现API代码: {source}")
    
    target = TARGET_PLATFORM / 'backend' / 'api' / 'chs_ai'
    target.mkdir(parents=True, exist_ok=True)
    
    # 复制API文件
    for item in source.rglob('*.py'):
        rel_path = item.relative_to(source)
        target_file = target / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(item, target_file)
            print(f"    [OK] 复制: {rel_path}")
        except Exception as e:
            print(f"    [ERROR] 失败: {rel_path} - {e}")

def create_integration_summary():
    """创建整合总结"""
    print(f"\n{'='*70}")
    print("  生成整合总结")
    print(f"{'='*70}")
    
    summary = {
        'timestamp': str(Path.ctime(Path(__file__))),
        'source': str(CHS_AI_PATH),
        'target': str(PROJECT_ROOT),
        'knowledge_base': {
            'location': str(TARGET_KNOWLEDGE_BASE),
            'items': count_files(TARGET_KNOWLEDGE_BASE)
        },
        'platform': {
            'frontend_components': count_files(TARGET_PLATFORM / 'frontend' / 'chs-ai-components') if (TARGET_PLATFORM / 'frontend' / 'chs-ai-components').exists() else 0,
            'backend_services': count_files(TARGET_PLATFORM / 'backend' / 'chs_ai_services') if (TARGET_PLATFORM / 'backend' / 'chs_ai_services').exists() else 0
        }
    }
    
    summary_file = PROJECT_ROOT / 'integration_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n整合完成！")
    print(f"  知识库: {summary['knowledge_base']['items']} 个文件")
    print(f"  前端组件: {summary['platform']['frontend_components']} 个文件")
    print(f"  后端服务: {summary['platform']['backend_services']} 个文件")
    print(f"\n总结已保存到: {summary_file}")

def create_next_steps_guide():
    """创建后续步骤指南"""
    guide = """
# CHS-AI 整合完成 - 后续步骤指南

## ✅ 已完成的工作

1. **知识库整合**
   - 位置: `knowledge-base/`
   - 索引: `knowledge-base/index.json`

2. **平台代码整合**
   - 前端组件: `platform/frontend/chs-ai-components/`
   - 后端服务: `platform/backend/chs_ai_services/`
   - API定义: `platform/backend/api/chs_ai/`

## 📋 下一步工作

### 1. 配置知识库API

```python
# 在 platform/backend/full_server.py 中添加

from chs_ai_services import knowledge_service

app.include_router(
    knowledge_service.router,
    prefix="/api/v1/knowledge",
    tags=["knowledge"]
)
```

### 2. 集成前端组件

```javascript
// 在 platform/frontend/unified.html 中引入

import KnowledgeLibrary from './chs-ai-components/KnowledgeLibrary.vue'
import AIAssistant from './chs-ai-components/AIAssistant.vue'
```

### 3. 创建统一导航

更新导航栏，添加"知识库"入口：

```html
<nav>
  <a href="#cases">案例库</a>
  <a href="#knowledge">知识库</a>  <!-- 新增 -->
  <a href="#lab">实验室</a>
  <a href="#ai">AI助手</a>
</nav>
```

### 4. 建立知识-案例关联

运行关联脚本：

```bash
python platform/backend/link_knowledge_to_cases.py
```

### 5. 测试整合效果

```bash
# 启动服务器
cd platform/backend
python full_server.py

# 访问
http://localhost:8000
```

## 🔧 可能需要的调整

1. **依赖安装**: 检查 `requirements.txt`，安装新增的依赖
2. **数据库初始化**: 如果使用数据库，运行迁移脚本
3. **环境变量**: 配置必要的API密钥和环境变量
4. **样式统一**: 调整CSS确保风格一致

## 📚 参考文档

- 融合方案详细说明: `platform/backend/深度融合方案-CHS水利水电学习平台.md`
- API文档: `http://localhost:8000/docs`
- 知识库索引: `knowledge-base/index.json`

---

**整合时间**: {timestamp}
"""
    
    guide_file = PROJECT_ROOT / 'INTEGRATION_GUIDE.md'
    with open(guide_file, 'w', encoding='utf-8') as f:
        from datetime import datetime
        f.write(guide.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    print(f"\n后续步骤指南已创建: {guide_file}")

def main():
    """主函数"""
    # 1. 检查chs-ai目录
    if not check_chs_ai_exists():
        return
    
    # 2. 分析目录结构
    structure = analyze_chs_ai_structure()
    
    # 3. 用户确认
    print(f"\n{'='*70}")
    print("  准备开始整合")
    print(f"{'='*70}")
    response = input("\n是否继续？(y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    # 4. 整合知识库
    integrate_knowledge_base(structure)
    
    # 5. 整合平台代码
    integrate_platform_code(structure)
    
    # 6. 创建整合总结
    create_integration_summary()
    
    # 7. 创建后续步骤指南
    create_next_steps_guide()
    
    print(f"\n{'='*70}")
    print("  🎉 整合完成！")
    print(f"{'='*70}")
    print("\n请查看 INTEGRATION_GUIDE.md 了解后续步骤")

if __name__ == '__main__':
    main()


