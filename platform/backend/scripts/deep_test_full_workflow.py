# coding: utf-8
"""
深度测试脚本 - 完整工作流
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test(name, result, details=""):
    """测试结果输出"""
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} {name}")
    if details:
        print(f"       {details}")
    return result

print("="*60)
print("深度测试: 案例学习功能完整工作流")
print("="*60)
print()

# 阶段1: 基础API测试
print("[阶段1] 基础API连通性测试")
print("-"*60)

# 1.1 测试章节API
try:
    response = requests.get(
        f"{BASE_URL}/api/textbooks/chapters/c94f25d8-6b9d-4f9e-bf32-b0b562d72b59/full",
        timeout=5
    )
    data = response.json()
    
    test("1.1 章节API响应", response.status_code == 200)
    test("1.2 返回章节内容", 'chapter' in data)
    test("1.3 返回关联案例", 'related_cases' in data)
    
    cases = data.get('related_cases', [])
    test("1.4 案例数量", len(cases) >= 3, f"找到{len(cases)}个案例")
    
    if cases:
        case_id = cases[0]['case_id']
        case_title = cases[0]['title']
        print(f"       首个案例: {case_id} - {case_title}")
except Exception as e:
    test("1.1 章节API响应", False, str(e))
    case_id = "case_01_home_water_tower"  # 使用默认值继续测试

print()

# 阶段2: 案例文档测试
print("[阶段2] 案例文档查看测试")
print("-"*60)

try:
    response = requests.get(f"{BASE_URL}/api/cases/{case_id}/readme", timeout=5)
    data = response.json()
    
    test("2.1 文档API响应", response.status_code == 200)
    test("2.2 success标志", data.get('success') == True)
    test("2.3 返回标题", 'title' in data and len(data['title']) > 0)
    test("2.4 返回内容", 'content' in data and len(data['content']) > 100)
    
    content = data.get('content', '')
    test("2.5 Markdown格式", content.startswith('#'))
    test("2.6 内容完整性", len(content) > 1000, f"{len(content)}字符")
    
except Exception as e:
    test("2.1 文档API响应", False, str(e))

print()

# 阶段3: 案例代码测试
print("[阶段3] 案例代码获取测试")
print("-"*60)

try:
    response = requests.get(f"{BASE_URL}/api/cases/{case_id}/code", timeout=5)
    data = response.json()
    
    test("3.1 代码API响应", response.status_code == 200)
    test("3.2 success标志", data.get('success') == True)
    test("3.3 返回文件名", 'filename' in data)
    test("3.4 返回代码", 'code' in data and len(data['code']) > 0)
    
    code = data.get('code', '')
    test("3.5 Python代码", 'import' in code or 'def' in code)
    test("3.6 代码长度", len(code) > 100, f"{len(code)}字符")
    
except Exception as e:
    test("3.1 代码API响应", False, str(e))

print()

# 阶段4: 代码执行测试
print("[阶段4] 代码执行功能测试")
print("-"*60)

# 4.1 简单代码测试
test_cases = [
    ("4.1 Hello World", "print('Hello World')", "Hello World"),
    ("4.2 数学运算", "print(1 + 2 + 3)", "6"),
    ("4.3 变量定义", "x = 10; y = 20; print(x + y)", "30"),
    ("4.4 循环", "for i in range(3): print(i)", "0"),
]

for name, code, expected in test_cases:
    try:
        response = requests.post(
            f"{BASE_URL}/api/execute/python",
            json={"code": code},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', '')
            error = result.get('error', '')
            
            if error:
                test(name, False, f"错误: {error[:50]}")
            else:
                has_expected = expected in output
                test(name, has_expected, f"输出: {output[:30]}")
        else:
            test(name, False, f"HTTP {response.status_code}")
    except Exception as e:
        test(name, False, str(e)[:50])

print()

# 阶段5: 错误处理测试
print("[阶段5] 错误处理测试")
print("-"*60)

# 5.1 语法错误
try:
    response = requests.post(
        f"{BASE_URL}/api/execute/python",
        json={"code": "print('missing quote)"},
        timeout=10
    )
    result = response.json()
    has_error = 'error' in result and result['error']
    test("5.1 语法错误捕获", has_error, "正确返回错误信息")
except Exception as e:
    test("5.1 语法错误捕获", False, str(e))

# 5.2 运行时错误
try:
    response = requests.post(
        f"{BASE_URL}/api/execute/python",
        json={"code": "print(1/0)"},
        timeout=10
    )
    result = response.json()
    has_error = 'error' in result and 'ZeroDivisionError' in str(result.get('error', ''))
    test("5.2 运行时错误捕获", has_error, "捕获除零错误")
except Exception as e:
    test("5.2 运行时错误捕获", False, str(e))

# 5.3 不存在的案例
try:
    response = requests.get(f"{BASE_URL}/api/cases/nonexistent_case/readme", timeout=5)
    test("5.3 不存在案例处理", response.status_code == 404, "返回404")
except Exception as e:
    test("5.3 不存在案例处理", False, str(e))

print()

# 阶段6: 前端页面测试
print("[阶段6] 前端页面测试")
print("-"*60)

try:
    response = requests.get(f"{BASE_URL}/learning", timeout=5)
    content = response.text
    
    test("6.1 页面加载", response.status_code == 200)
    test("6.2 包含标题", "统一学习平台" in content or "learning" in content.lower())
    test("6.3 包含marked.js", "marked" in content.lower())
    test("6.4 包含Monaco", "monaco" in content.lower())
    test("6.5 包含viewCase函数", "viewCase" in content)
    test("6.6 包含runCase函数", "runCase" in content)
    test("6.7 包含executeCode函数", "executeCode" in content)
    
except Exception as e:
    test("6.1 页面加载", False, str(e))

print()

# 阶段7: 性能测试
print("[阶段7] 性能测试")
print("-"*60)

try:
    # 7.1 API响应时间
    start = time.time()
    requests.get(f"{BASE_URL}/api/cases/{case_id}/readme", timeout=5)
    duration = time.time() - start
    test("7.1 文档API响应时间", duration < 1.0, f"{duration:.3f}秒")
    
    # 7.2 代码执行时间
    start = time.time()
    requests.post(
        f"{BASE_URL}/api/execute/python",
        json={"code": "print('test')"},
        timeout=10
    )
    duration = time.time() - start
    test("7.2 代码执行时间", duration < 5.0, f"{duration:.3f}秒")
    
except Exception as e:
    test("7.1 性能测试", False, str(e))

print()
print("="*60)
print("深度测试完成!")
print("="*60)
print()
print("后续测试建议:")
print("1. 在浏览器中手动测试UI交互")
print("2. 测试不同浏览器的兼容性")
print("3. 测试更复杂的Python代码")
print("4. 测试长时间运行的代码(>10秒)")

