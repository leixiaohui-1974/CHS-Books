# coding: utf-8
"""
最终功能验证脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api(name, url, method="GET", data=None):
    """测试API"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        status = "[OK]" if response.status_code == 200 else "[FAIL]"
        print(f"{status} {name}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

print("="*50)
print("API功能验证")
print("="*50)

# 1. 测试章节完整信息API
test_api(
    "获取章节完整信息",
    f"{BASE_URL}/api/textbooks/chapters/c94f25d8-6b9d-4f9e-bf32-b0b562d72b59/full"
)

# 2. 测试案例README API
test_api(
    "获取案例README",
    f"{BASE_URL}/api/cases/case_01_home_water_tower/readme"
)

# 3. 测试案例代码API
test_api(
    "获取案例代码",
    f"{BASE_URL}/api/cases/case_01_home_water_tower/code"
)

# 4. 测试代码执行API
test_api(
    "执行Python代码",
    f"{BASE_URL}/api/execute/python",
    method="POST",
    data={"code": "print('Hello World')"}
)

# 5. 测试前端页面
test_api(
    "学习平台首页",
    f"{BASE_URL}/learning"
)

print("="*50)
print("验证完成!")
print("="*50)
print("\n请在浏览器中测试完整功能:")
print(f"1. 打开: {BASE_URL}/learning")
print("2. 选择教材 -> 选择章节")
print("3. 点击案例的'查看文档'按钮")
print("4. 点击案例的'运行代码'按钮")

