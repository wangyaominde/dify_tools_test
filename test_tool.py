#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dify工具测试脚本
验证工具配置和功能是否正常
"""

import json
import os
try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for offline environments
    import json
    from types import SimpleNamespace

    def _load_json(stream):
        content = stream.read() if hasattr(stream, "read") else str(stream)
        return json.loads(content)

    yaml = SimpleNamespace(safe_load=_load_json)
import sys

def test_yaml_config():
    """测试YAML配置文件"""
    print("🧪 测试YAML配置文件...")

    try:
        with open('_assets.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 检查必需字段
        required_fields = [
            'identity',
            'parameters'
        ]

        for field in required_fields:
            if field not in config:
                print(f"❌ 缺少必需字段: {field}")
                return False

        # 检查identity字段
        identity = config['identity']
        required_identity_fields = [
            'author', 'name', 'label', 'description',
            'supported_model_types', 'configurate_methods',
            'provider_credential_schema', 'tool_credential_schema'
        ]

        for field in required_identity_fields:
            if field not in identity:
                print(f"❌ identity缺少字段: {field}")
                return False

        # 检查parameters字段
        parameters = config['parameters']
        if not isinstance(parameters, list):
            print("❌ parameters应该是一个列表")
            return False

        if len(parameters) == 0:
            print("❌ parameters不能为空")
            return False

        # 检查每个参数
        for param in parameters:
            required_param_fields = ['name', 'type', 'required', 'label', 'human_description', 'form']
            for field in required_param_fields:
                if field not in param:
                    print(f"❌ 参数 '{param.get('name', 'unknown')}' 缺少字段: {field}")
                    return False

        print("✅ YAML配置文件验证通过")
        return True

    except Exception as e:
        print(f"❌ YAML配置文件测试失败: {e}")
        return False

def test_main_script():
    """测试主脚本"""
    print("🧪 测试主脚本...")

    try:
        # 导入主模块
        import main

        # 检查MobileControlTool类是否存在
        if not hasattr(main, 'MobileControlTool'):
            print("❌ 缺少MobileControlTool类")
            return False

        # 创建工具实例
        tool = main.MobileControlTool()

        # 测试基本方法
        methods_to_test = [
            'phonebook_list',
            'phonebook_add',
            'phonebook_delete',
            'make_call',
            'send_sms',
            'control_volume',
            'control_brightness',
            'control_theme',
            '_invoke'  # Dify工具必需的方法
        ]

        for method_name in methods_to_test:
            if not hasattr(tool, method_name):
                print(f"❌ 缺少方法: {method_name}")
                return False

        print("✅ 主脚本验证通过")
        return True

    except Exception as e:
        print(f"❌ 主脚本测试失败: {e}")
        return False

def test_api_server():
    """测试API服务器"""
    print("🧪 测试API服务器导入...")

    try:
        # 尝试导入API服务器模块
        import api_server

        # 检查Flask应用是否存在
        if not hasattr(api_server, 'app'):
            print("❌ API服务器缺少app对象")
            return False

        print("✅ API服务器验证通过")
        return True

    except ImportError as e:
        print(f"❌ API服务器导入失败: {e}")
        print("   请确保安装了所需的依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ API服务器测试失败: {e}")
        return False

def test_tool_functionality():
    """测试工具功能"""
    print("🧪 测试工具功能...")

    try:
        from main import MobileControlTool

        tool = MobileControlTool()

        # 先清理可能存在的测试数据
        try:
            tool.phonebook_delete("测试联系人")
        except:
            pass  # 忽略删除失败

        # 测试电话本功能
        result = tool.phonebook_list()
        if not result.get('success', False):
            print(f"❌ 电话本功能测试失败: {result.get('message', 'unknown error')}")
            return False

        # 测试添加联系人
        result = tool.phonebook_add("测试联系人", "13800138000", "测试别名")
        if not result.get('success', False):
            print(f"❌ 添加联系人功能测试失败: {result.get('message', 'unknown error')}")
            return False

        # 清理测试数据
        try:
            tool.phonebook_delete("测试联系人")
        except:
            pass  # 忽略删除失败

        # 测试_invoke方法
        try:
            result = tool._invoke("test_user", {"action": "phonebook_list"})
            if not isinstance(result, list) or len(result) == 0:
                print("❌ _invoke方法返回格式不正确")
                return False
        except Exception as e:
            print(f"❌ _invoke方法测试失败: {e}")
            return False

        print("✅ 工具功能验证通过")
        return True

    except Exception as e:
        print(f"❌ 工具功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Dify工具验证测试")
    print("=" * 50)

    tests = [
        test_yaml_config,
        test_main_script,
        test_api_server,
        test_tool_functionality
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            print()

    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！工具可以正常导入到Dify")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
