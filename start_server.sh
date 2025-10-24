#!/bin/bash

# Mobile Control Tool API Server启动脚本
# Mobile Control Tool API服务器启动脚本

echo "启动Mobile Control Tool API服务器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请确保Python 3.6+已安装"
    exit 1
fi

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 建议在虚拟环境中运行"
    echo "您可以运行以下命令创建虚拟环境:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
fi

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

# 设置默认环境变量
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"5000"}
export DEBUG=${DEBUG:-"false"}

echo "服务器配置:"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  调试模式: $DEBUG"
echo ""

# 启动服务器
echo "启动服务器..."
python3 api_server.py
