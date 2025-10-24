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
            'openapi',
            'info',
            'paths'
        ]

        for field in required_fields:
            if field not in config:
                print(f"❌ 缺少必需字段: {field}")
                return False

        # 检查openapi版本
        if not isinstance(config['openapi'], str):
            print("❌ openapi字段必须是字符串")
            return False

        # 检查info字段
        info = config['info']
        if not isinstance(info, dict):
            print("❌ info字段必须是对象")
            return False

        required_info_fields = ['title', 'description', 'version']

        for field in required_info_fields:
            if field not in info:
                print(f"❌ info缺少字段: {field}")
                return False

        # 检查paths字段
        paths = config['paths']
        if not isinstance(paths, dict) or not paths:
            print("❌ paths必须是非空对象")
            return False

        # 检查每个路径的定义
        for path, methods in paths.items():
            if not isinstance(methods, dict) or not methods:
                print(f"❌ 路径 '{path}' 必须包含至少一个方法")
                return False

            for method, definition in methods.items():
                if not isinstance(definition, dict):
                    print(f"❌ 路径 '{path}' 的方法 '{method}' 定义必须是对象")
                    return False
                if 'operationId' not in definition:
                    print(f"❌ 路径 '{path}' 的方法 '{method}' 缺少operationId")
                    return False
                if 'responses' not in definition:
                    print(f"❌ 路径 '{path}' 的方法 '{method}' 缺少responses定义")
                    return False

        # 检查components.schemas
        components = config.get('components', {})
        schemas = components.get('schemas', {})
        required_schemas = ['MobileControlRequest', 'MobileControlResponse']
        for schema_name in required_schemas:
            if schema_name not in schemas:
                print(f"❌ 缺少schema定义: {schema_name}")
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
