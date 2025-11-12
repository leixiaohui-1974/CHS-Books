"""快速测试案例API"""
import requests

# 测试API
case_id = "case_01_home_water_tower"
url = f"http://localhost:8000/api/cases/{case_id}/readme"

print(f"测试API: {url}")
try:
    response = requests.get(url, timeout=5)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功!")
        print(f"标题: {data.get('title', 'N/A')}")
        print(f"内容长度: {len(data.get('content', ''))} 字符")
    else:
        print(f"❌ 失败!")
        print(f"响应: {response.text[:200]}")
except Exception as e:
    print(f"❌ 错误: {e}")

