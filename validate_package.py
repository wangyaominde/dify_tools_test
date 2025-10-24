#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dify工具包验证脚本
验证zip包是否符合Dify导入要求
"""

import zipfile
import os
import yaml
import sys

def validate_package(package_path):
    """验证工具包"""
    if not os.path.exists(package_path):
        print(f"❌ 工具包不存在: {package_path}")
        return False

    print(f"📦 验证工具包: {package_path}")
    print(f"📊 文件大小: {os.path.getsize(package_path)} bytes")
    print()

    try:
        with zipfile.ZipFile(package_path, 'r') as zip_file:
            # 获取文件列表
            file_list = zip_file.namelist()
            print("📁 包内文件结构:")
            for file in file_list:
                print(f"  {file}")
            print()

            # 检查必需文件
            required_files = ['_assets.yaml', 'main.py']
            missing_files = []

            for required_file in required_files:
                if required_file not in file_list:
                    missing_files.append(required_file)

            if missing_files:
                print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
                return False

            print("✅ 必需文件检查通过")

            # 验证_assets.yaml
            print("\n🔍 验证 _assets.yaml...")
            try:
                with zip_file.open('_assets.yaml') as f:
                    config = yaml.safe_load(f)

                # 检查必需字段
                required_keys = ['identity', 'parameters']
                for key in required_keys:
                    if key not in config:
                        print(f"❌ _assets.yaml 缺少字段: {key}")
                        return False

                # 检查identity字段
                identity = config['identity']
                required_identity_keys = [
                    'author', 'name', 'label', 'description',
                    'supported_model_types', 'configurate_methods'
                ]

                for key in required_identity_keys:
                    if key not in identity:
                        print(f"❌ identity 缺少字段: {key}")
                        return False

                print("✅ _assets.yaml 验证通过")

            except Exception as e:
                print(f"❌ _assets.yaml 验证失败: {e}")
                return False

            # 检查是否有子目录
            has_subdir = any('/' in f for f in file_list if f != '')
            if has_subdir:
                print("⚠️  警告: 包中包含子目录，这可能导致Dify导入失败")
                print("   建议：文件应该直接在zip包根目录中")
            else:
                print("✅ 文件结构正确（无子目录）")

            return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python3 validate_package.py <工具包路径>")
        print("示例: python3 validate_package.py mobile_control_tool.zip")
        sys.exit(1)

    package_path = sys.argv[1]

    print("🚀 Dify工具包验证工具")
    print("=" * 50)

    if validate_package(package_path):
        print("\n" + "=" * 50)
        print("🎉 工具包验证通过！可以用于Dify导入")
        print("\n📋 验证结果:")
        print("✅ 文件结构正确")
        print("✅ 必需文件存在")
        print("✅ 配置文件有效")
        print("✅ 符合Dify导入要求")
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ 工具包验证失败！请修复上述问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
