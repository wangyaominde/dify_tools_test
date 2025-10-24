#!/bin/bash

# Mobile Control Tool API Server自动启动脚本
# Mobile Control Tool API服务器自动启动脚本

set -e  # 遇到错误立即退出

echo "🚀 启动Mobile Control Tool API服务器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请确保Python 3.6+已安装"
    exit 1
fi

# 检查并创建虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 检查虚拟环境..."
    if [ ! -d "venv" ]; then
        echo "🔧 创建虚拟环境..."
        python3 -m venv venv
        echo "✅ 虚拟环境创建完成"
    else
        echo "✅ 虚拟环境已存在"
    fi

    echo "🔄 激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "✅ 已在虚拟环境中运行"
fi

# 检查并安装依赖
echo "📚 检查Python依赖..."
if [ ! -f "venv/requirements_installed" ]; then
    echo "⬇️ 安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/requirements_installed
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装，跳过安装步骤"
fi

# 设置默认环境变量
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"5000"}
export DEBUG=${DEBUG:-"false"}

echo ""
echo "⚙️  服务器配置:"
echo "  🌐 主机: $HOST"
echo "  🔌 端口: $PORT"
echo "  🐛 调试模式: $DEBUG"
echo ""

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口 $PORT 已被占用"
    echo "   您可以修改PORT环境变量来使用其他端口"
    echo "   例如: PORT=5001 ./run.sh"
    exit 1
fi

# 启动服务器
echo "🎯 启动服务器..."
echo "📡 API服务器地址: http://$HOST:$PORT"
echo "🩺 健康检查: http://$HOST:$PORT/health"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 api_server.py
