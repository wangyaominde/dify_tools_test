#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mobile Control Tool API 测试脚本
移动设备控制工具API测试脚本
"""

import requests
import json
import time

# API服务器地址
BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("🩺 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_phonebook_operations():
    """测试电话本操作"""
    print("\n📞 测试电话本操作...")

    # 测试获取电话本
    try:
        response = requests.get(f"{BASE_URL}/api/phonebook")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取电话本成功: {result.get('message', '')}")
        else:
            print(f"❌ 获取电话本失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取电话本异常: {e}")

    # 测试添加联系人
    try:
        contact_data = {
            "name": "测试联系人",
            "phone": "13900000000",
            "alias": "测试别名"
        }
        response = requests.post(f"{BASE_URL}/api/phonebook",
                               json=contact_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 添加联系人成功: {result.get('message', '')}")
        else:
            print(f"❌ 添加联系人失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 添加联系人异常: {e}")

    # 等待一下再获取
    time.sleep(1)

    # 再次获取电话本确认添加成功
    try:
        response = requests.get(f"{BASE_URL}/api/phonebook")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 确认联系人已添加: {len(result.get('data', []))} 个联系人")
    except Exception as e:
        print(f"❌ 确认联系人异常: {e}")

def test_system_controls():
    """测试系统控制功能"""
    print("\n🔊 测试系统控制功能...")

    # 测试音量控制
    try:
        response = requests.post(f"{BASE_URL}/api/system/volume",
                               json={"level": 50},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 音量控制: {result.get('message', '')}")
        else:
            print(f"❌ 音量控制失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 音量控制异常: {e}")

    # 测试亮度控制
    try:
        response = requests.post(f"{BASE_URL}/api/system/brightness",
                               json={"level": 80},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 亮度控制: {result.get('message', '')}")
        else:
            print(f"❌ 亮度控制失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 亮度控制异常: {e}")

    # 测试主题控制
    try:
        response = requests.post(f"{BASE_URL}/api/system/theme",
                               json={"mode": "dark"},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 主题控制: {result.get('message', '')}")
        else:
            print(f"❌ 主题控制失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主题控制异常: {e}")

def test_communication():
    """测试通信功能"""
    print("\n📱 测试通信功能...")

    # 测试拨打电话（注意：这会在实际环境中拨打电话，请谨慎测试）
    try:
        # 这里使用一个测试号码，实际使用时请替换为真实号码
        response = requests.post(f"{BASE_URL}/api/communication/call",
                               json={"phone_number": "13800138000"},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 拨打电话: {result.get('message', '')}")
        else:
            print(f"❌ 拨打电话失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 拨打电话异常: {e}")

    # 测试发送短信（注意：这会在实际环境中发送短信，请谨慎测试）
    try:
        response = requests.post(f"{BASE_URL}/api/communication/sms",
                               json={
                                   "phone_number": "13800138000",
                                   "message": "测试短信 from Mobile Control Tool API"
                               },
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 发送短信: {result.get('message', '')}")
        else:
            print(f"❌ 发送短信失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 发送短信异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试Mobile Control Tool API")
    print(f"API服务器地址: {BASE_URL}")
    print("=" * 50)

    # 测试健康检查
    if not test_health():
        print("❌ 服务器未运行，请先启动API服务器")
        print("运行命令: python3 api_server.py")
        return

    # 测试各项功能
    test_phonebook_operations()
    test_system_controls()
    test_communication()

    print("\n" + "=" * 50)
    print("✅ API测试完成")
    print("\n💡 注意事项:")
    print("1. 通信功能（打电话、发短信）在测试环境中可能不会实际执行")
    print("2. 系统控制功能需要在相应的操作系统上才能完全生效")
    print("3. 建议在生产环境中添加适当的认证和权限控制")

if __name__ == "__main__":
    main()
