"""
前端连接诊断脚本
测试后端API是否正常工作
"""
import requests
import sys

def test_backend_connection():
    """测试后端连接"""
    print("=" * 60)
    print("前端连接诊断")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 测试1: 根路径
    print("\n[1/4] 测试根路径...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"  状态: {'OK' if response.status_code == 200 else 'FAIL'} ({response.status_code})")
    except Exception as e:
        print(f"  状态: FAIL - {e}")
    
    # 测试2: API文档
    print("\n[2/4] 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"  状态: {'OK' if response.status_code == 200 else 'FAIL'} ({response.status_code})")
    except Exception as e:
        print(f"  状态: FAIL - {e}")
    
    # 测试3: 获取Agents
    print("\n[3/4] 测试获取Agents...")
    try:
        response = requests.get(f"{base_url}/hedge-fund/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"  状态: OK")
            print(f"  获取到 {len(agents)} 个Agent")
            if agents:
                print(f"  第一个Agent: {agents[0].get('display_name', 'N/A')}")
        else:
            print(f"  状态: FAIL ({response.status_code})")
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  状态: FAIL - {e}")
    
    # 测试4: 获取Models
    print("\n[4/4] 测试获取Models...")
    try:
        response = requests.get(f"{base_url}/language-models/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"  状态: OK")
            print(f"  获取到 {len(models)} 个模型")
        else:
            print(f"  状态: FAIL ({response.status_code})")
    except Exception as e:
        print(f"  状态: FAIL - {e}")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("\n如果以上测试都失败，请检查:")
    print("  1. 后端是否已启动: poetry run uvicorn app.backend.main:app --reload")
    print("  2. 后端是否在端口8000运行")
    print("  3. 是否有防火墙阻止连接")

if __name__ == "__main__":
    test_backend_connection()
