# Mobile Control Tool (移动设备控制工具)

这是一个为Dify平台设计的移动设备控制工具，支持电话本管理、拨打电话、发短信、音量控制、亮度控制和主题控制等功能。

## ✨ 主要特性

- 🚀 **一键启动**: 运行 `./run.sh` 自动创建虚拟环境并安装依赖
- 📱 **完整功能**: 电话本、通信、系统控制
- 🌐 **RESTful API**: 标准HTTP接口，支持远程访问
- 🐳 **Docker支持**: 容器化部署
- 🔒 **环境隔离**: 自动创建Python虚拟环境
- 📊 **智能检查**: 自动检测端口占用和依赖状态
- 🩺 **健康监控**: 内置健康检查端点

## 🌐 在Dify中使用工具

### 方式一：直接导入到Dify Studio
1. **准备工具文件**：
   - 确保有 `_assets.yaml` 和 `main.py` 文件
   - 可选：`requirements.txt` 和 `README.md`

2. **在Dify Studio中导入**：
   - 进入Dify Studio
   - 选择"工具" → "自定义工具"
   - 点击"导入工具"
   - 选择整个工具文件夹或压缩包
   - 系统会自动解析 `_assets.yaml` 配置

3. **配置工具参数**：
   - 根据界面提示配置各项参数
   - 测试工具连接性

### 方式二：直接导入Schema（推荐！最简单）

**直接在Dify Studio中粘贴 `_assets.yaml` 的内容！**

#### 1. 复制Schema内容
复制 `_assets.yaml` 文件的完整内容

#### 2. 在Dify中导入
- 在Dify Studio中选择"工具" → "自定义工具"
- 点击"从Schema导入"或直接粘贴YAML内容
- 粘贴 `_assets.yaml` 的完整内容
- 完成导入！

#### 服务器地址
工具会自动连接到 `http://hk.wangyaomin.com:5000`，确保您的服务器运行正常。

#### 故障排除

**如果Schema导入仍然失败，请检查：**

1. **验证Schema格式**：
   ```bash
   # 检查YAML语法
   python3 -c "import yaml; yaml.safe_load(open('_assets.yaml'))"
   ```

2. **检查必需字段**：
   - `info` - 工具基本信息
   - `servers` - 服务器地址
   - `parameters` - 参数定义

3. **常见错误原因**：
   - YAML格式错误（缩进、引号等）
   - 缺少必需字段
   - 字段名称拼写错误
   - 参数定义格式不正确

4. **服务器连接**：
   确保 `http://hk.wangyaomin.com:5000` 可以访问

### 方式二：部署为独立的API服务
如果需要远程访问，可以将工具部署为独立的Web API服务：

#### 快速启动（一键启动）
```bash
# 一键启动（自动创建虚拟环境并安装依赖）
./run.sh

# 或者使用其他端口
PORT=5001 ./run.sh

# 或者启用调试模式
DEBUG=true ./run.sh
```

#### 手动启动（如果需要自定义环境）
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python3 api_server.py
```

#### Docker部署
```bash
# 使用Docker Compose一键部署
docker-compose up -d

# 或者使用Docker
docker build -t mobile-control-tool .
docker run -p 5000:5000 mobile-control-tool
```

#### API端点
- `GET /health` - 健康检查
- `POST /api/mobile-control` - 主控制接口
- `GET /api/phonebook` - 获取电话本
- `POST /api/phonebook` - 添加联系人
- `DELETE /api/phonebook/<name>` - 删除联系人
- `POST /api/system/volume` - 控制音量
- `POST /api/system/brightness` - 控制亮度
- `POST /api/system/theme` - 控制主题
- `POST /api/communication/call` - 拨打电话
- `POST /api/communication/sms` - 发送短信
- `GET /download/tool` - 下载Dify工具包

#### API使用示例
```bash
# 添加联系人
curl -X POST "http://localhost:5000/api/phonebook" \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "phone": "13800138000", "alias": "小张"}'

# 获取电话本
curl -X GET "http://localhost:5000/api/phonebook"

# 控制音量
curl -X POST "http://localhost:5000/api/system/volume" \
  -H "Content-Type: application/json" \
  -d '{"level": 75}'

# 拨打电话
curl -X POST "http://localhost:5000/api/communication/call" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "13800138000"}'
```

### 方式三：通过Dify Cloud使用
- 将工具上传到Dify Cloud
- 通过Dify提供的API接口远程调用
- 支持RESTful API调用

## 📡 远程访问说明

### Dify平台远程调用
一旦工具导入到Dify，您可以通过以下方式远程访问：

1. **通过Dify Web界面**：
   - 登录Dify平台
   - 在对话中选择工具
   - 填写参数并执行

2. **通过Dify API**：
   ```bash
   curl -X POST "https://api.dify.ai/v1/chat-messages" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "inputs": {},
       "query": "帮我添加一个联系人",
       "user": "user123",
       "conversation_id": "conv123"
     }'
   ```

3. **通过编程方式**：
   ```python
   import requests

   def call_mobile_tool(action, **params):
       url = "https://api.dify.ai/v1/chat-messages"
       headers = {
           "Authorization": f"Bearer {YOUR_API_KEY}",
           "Content-Type": "application/json"
       }
       data = {
           "inputs": {"action": action, **params},
           "query": f"执行{action}操作",
           "user": "user123"
       }
       response = requests.post(url, headers=headers, json=data)
       return response.json()
   ```

## 🔧 注意事项

### 远程访问限制
- **系统权限**：音量、亮度、主题控制需要在运行工具的服务器上执行
- **电话功能**：拨打电话和发短信功能依赖于服务器端的电话应用
- **数据持久化**：电话本数据存储在服务器端，需要考虑数据同步

### 安全性考虑
- 敏感操作需要适当的权限验证
- API密钥要妥善保管
- 考虑网络传输的安全性

### 性能优化
- 工具执行时间可能受网络延迟影响
- 大量并发请求需要考虑服务器负载
- 可以考虑使用缓存来优化响应速度

## 功能特性

### 📞 电话本管理
- **查看电话本**: 列出所有联系人及其电话号码和别名
- **添加联系人**: 添加新联系人，支持设置别名
- **删除联系人**: 删除指定联系人

### 📱 通信功能
- **拨打电话**: 使用系统默认电话应用拨打电话
- **发送短信**: 使用系统默认短信应用发送短信

### 🔊 系统控制
- **音量控制**: 设置系统音量（0-100%）
- **亮度控制**: 调整屏幕亮度（0-100%）
- **主题控制**: 切换系统主题（浅色/深色/自动）

## 安装和使用

### 环境要求
- Python 3.6+
- 支持的操作系统：macOS、Windows、Linux

### 安装依赖
```bash
pip install -r requirements.txt
```

### 作为Dify工具使用
1. 将整个项目文件夹复制到Dify工具目录
2. 在Dify中配置工具参数
3. 使用工具调用相应功能

### 命令行测试
```bash
# 查看电话本
python3 main.py phonebook_list

# 添加联系人（带别名）
python3 main.py phonebook_add contact_name="张三" phone_number="13800138000" contact_alias="小张"

# 删除联系人
python3 main.py phonebook_delete contact_name="张三"

# 拨打电话
python3 main.py call phone_number="13800138000"

# 发送短信
python3 main.py sms phone_number="13800138000" sms_message="你好！"

# 控制音量
python3 main.py volume volume_level=50

# 控制亮度
python3 main.py brightness brightness_level=75

# 控制主题
python3 main.py theme theme_mode=dark
```

## 数据存储

电话本数据存储在 `phonebook.json` 文件中，格式如下：
```json
{
  "联系人姓名": {
    "phone": "电话号码",
    "alias": "别名"
  }
}
```

## 系统兼容性

### macOS
- 电话和短信：使用系统默认应用
- 音量：使用osascript控制
- 亮度：需要安装brightness工具
- 主题：使用osascript控制

### Windows
- 电话和短信：使用系统默认应用
- 音量：使用nircmd工具
- 亮度：使用PowerShell
- 主题：修改注册表

### Linux
- 电话和短信：使用xdg-open
- 音量：使用amixer
- 亮度：使用brightnessctl
- 主题：使用gsettings（GNOME）

## 注意事项

1. 某些系统控制功能可能需要管理员权限或额外工具
2. 亮度和主题控制在不同桌面环境下可能表现不同
3. 电话本数据会自动兼容旧版本格式
4. 所有操作都会记录日志到控制台

## 错误处理

工具包含完善的错误处理机制，操作失败时会返回详细的错误信息，不会影响系统的正常运行。
