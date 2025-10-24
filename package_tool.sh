#!/bin/bash

# Mobile Control Tool 打包脚本
# 用于创建Dify工具导入包

set -e

echo "📦 开始打包Mobile Control Tool..."

# 检查必需文件
required_files=("_assets.yaml" "main.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 缺少必需文件 $file"
        exit 1
    fi
done

echo "✅ 必需文件检查通过"

# 定义要包含的文件
include_files=(
    "_assets.yaml"
    "main.py"
    "requirements.txt"
    "README.md"
    "api_server.py"
    "docker-compose.yml"
    "Dockerfile"
    "run.sh"
)

# 创建临时目录
temp_dir=$(mktemp -d)
package_dir="$temp_dir/mobile_control_tool"

echo "🔧 创建包结构..."
mkdir -p "$package_dir"

# 复制文件
for file in "${include_files[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$package_dir/"
        echo "  📄 复制: $file"
    else
        echo "  ⚠️  跳过: $file (文件不存在)"
    fi
done

# 创建zip包
package_name="mobile_control_tool.zip"
echo "🗜️  创建压缩包: $package_name"
cd "$temp_dir"
zip -r "$package_name" "mobile_control_tool/"

# 移动到当前目录
mv "$package_name" "$OLDPWD/"

# 清理临时文件
cd "$OLDPWD"
rm -rf "$temp_dir"

echo ""
echo "🎉 打包完成！"
echo "📁 生成的文件: $package_name"
echo ""

# 显示文件信息
if command -v ls &> /dev/null; then
    ls -lh "$package_name"
fi

echo ""
echo "🚀 接下来您可以："
echo "1. 将 $package_name 上传到GitHub Release或文件共享服务"
echo "2. 在Dify Studio中通过URL导入工具"
echo "3. 或者直接使用本地文件导入"

# 检查文件大小
if command -v stat &> /dev/null; then
    file_size=$(stat -f%z "$package_name" 2>/dev/null || stat -c%s "$package_name" 2>/dev/null || echo "unknown")
    if [ "$file_size" != "unknown" ]; then
        echo "📊 文件大小: $file_size bytes"
        if [ "$file_size" -gt 52428800 ]; then  # 50MB
            echo "⚠️  警告: 文件大小超过50MB，可能无法导入到Dify"
        fi
    fi
fi
