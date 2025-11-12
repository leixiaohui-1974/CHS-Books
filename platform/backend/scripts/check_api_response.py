"""检查API响应结构"""
import requests
import json

case_id = "case_01_home_water_tower"
url = f"http://localhost:8000/api/cases/{case_id}/readme"

print(f"测试: {url}\n")
try:
    response = requests.get(url, timeout=5)
    print(f"状态码: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("JSON结构:")
        print(f"- success: {data.get('success', 'MISSING')}")
        print(f"- case_id: {data.get('case_id', 'MISSING')}")
        print(f"- title: {data.get('title', 'MISSING')}")
        print(f"- content: {'存在' if 'content' in data else 'MISSING'} ({len(data.get('content', ''))} chars)")
        print(f"- path: {data.get('path', 'MISSING')}")
        
        # 检查success字段
        if data.get('success'):
            print("\n[OK] success=True")
        else:
            print(f"\n[WARN] success={data.get('success')}")
    else:
        print(f"[ERROR] {response.text[:300]}")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

