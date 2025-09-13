"""测试文本风控API"""
import requests
import json
from datetime import datetime


def test_moderation_api():
    """测试文本风控API功能"""
    
    base_url = "http://localhost:18000"  # 简化版主应用端口
    
    print("=" * 60)
    print("文本风控系统API测试")
    print("=" * 60)
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 测试系统信息
    print("\n2. 测试系统信息...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 3. 测试风控健康检查
    print("\n3. 测试风控健康检查...")
    try:
        response = requests.get(f"{base_url}/v1/moderation/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 4. 测试综合内容检查 (主要功能)
    print("\n4. 测试综合内容检查 (核心功能)...")
    test_request = {
        "request_id": "test_001",
        "app_id": 1,
        "user_id": "12345",  # 修复为字符串类型
        "nickname": "测试用户",
        "content": "这是一个测试内容",
        "ip_address": "192.168.1.100",
        "account": "test_user",
        "role_id": "user",
        "speak_time": datetime.now().isoformat(),
        "case_sensitive": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/moderation/check",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   请求ID: {result.get('request_id')}")
            print(f"   是否违规: {result.get('is_violation')}")
            print(f"   风险等级: {result.get('max_risk_level')}")
            print(f"   处理状态: {result.get('status')}")
            print(f"   建议: {result.get('suggestion')}")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 5. 测试服务统计
    print("\n5. 测试服务统计...")
    try:
        response = requests.get(f"{base_url}/v1/moderation/statistics")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   总检查数: {stats.get('total_checks', 0)}")
            print(f"   违规检查数: {stats.get('violation_checks', 0)}")
            print(f"   缓存有效: {stats.get('cache_valid', False)}")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "=" * 60)
    print("完整系统API测试完成！")
    print("查看完整API文档: http://localhost:18000/docs")
    print("主应用端口: 18000 (包含所有功能)")
    print("文本风控测试端口: 18001 (仅风控功能)")
    print("=" * 60)


if __name__ == "__main__":
    test_moderation_api()