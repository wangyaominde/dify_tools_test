# 移动设备控制工具部署指南

## 🚀 超级简单的部署方案

**只需要一个命令就能让Dify从您的服务器下载工具！**

### 在 hk.wangyaomin.com 上部署

```bash
# 1. 上传文件到服务器
git clone <your-repo-url>
cd mobile-control-tool

# 2. 打包工具（文件直接在zip根目录，符合Dify要求）
./package_tool.sh

# 3. 一键启动服务器
./run.sh

# 4. 现在Dify可以直接从您的服务器下载工具了！
# 下载链接: http://hk.wangyaomin.com:5000/download/tool
```

## ✅ 关键修复：工具包结构

**问题**：之前的zip包有子目录结构，Dify无法识别
```
❌ 错误的结构:
mobile_control_tool.zip
└── mobile_control_tool/
    ├── _assets.yaml
    └── main.py
```

**解决**：文件直接在zip包根目录
```
✅ 正确的结构:
mobile_control_tool.zip
├── _assets.yaml
├── main.py
├── requirements.txt
└── README.md
```

就这样！现在您可以在Dify中使用这个URL直接导入工具了。

## 在 hk.wangyaomin.com 服务器上部署和测试

### 1. 上传文件到服务器

使用Git同步或手动上传以下文件到服务器：
- `_assets.yaml`
- `main.py`
- `requirements.txt`
- `mobile_control_tool.zip` (可选，用于Dify导入测试)

```bash
# 如果使用Git
git clone <your-repo-url>
cd mobile-control-tool

# 或者直接上传文件
scp _assets.yaml main.py requirements.txt user@hk.wangyaomin.com:~/mobile-control-tool/
```

### 2. 安装依赖

```bash
# 连接到服务器
ssh user@hk.wangyaomin.com

# 创建虚拟环境
cd ~/mobile-control-tool
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 本地测试工具功能

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python3 test_tool.py

# 测试各个功能
python3 main.py phonebook_list
python3 main.py phonebook_add contact_name="张三" phone_number="13800138000" contact_alias="小张"
```

### 4. 启动API服务器（用于远程访问）

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务器
python3 api_server.py

# 或者使用包装脚本
./run.sh
```

### 5. 测试API接口

```bash
# 在另一个终端测试API
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/mobile-control \
  -H "Content-Type: application/json" \
  -d '{"action": "phonebook_list"}'
```

### 6. 配置Web服务器（可选，用于公开访问）

如果需要从外部访问API服务器，可以配置Nginx反向代理：

```nginx
# /etc/nginx/sites-available/mobile-control
server {
    listen 80;
    server_name hk.wangyaomin.com;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 提供静态文件访问
    location /tools/ {
        alias /home/user/mobile-control-tool/;
        autoindex on;
    }
}
```

### 7. 在Dify中测试导入

#### 方式1：本地文件导入
1. 下载 `mobile_control_tool.zip` 到本地
2. 在Dify Studio中选择"从本地导入"
3. 选择zip文件

#### 方式2：URL导入
1. 将zip文件上传到服务器的公开目录
2. 在Dify Studio中选择"从URL导入"
3. 输入URL：`http://hk.wangyaomin.com/tools/mobile_control_tool.zip`

### 8. 调试技巧

#### 检查日志
```bash
# 查看API服务器日志
tail -f /var/log/mobile-control.log

# 查看Dify导入错误
# 在Dify Studio的工具页面查看错误信息
```

#### 常见问题
1. **端口占用**：检查5000端口是否被占用
   ```bash
   lsof -i :5000
   ```

2. **权限问题**：确保用户有执行权限
   ```bash
   chmod +x run.sh
   ```

3. **依赖问题**：检查Python版本和依赖
   ```bash
   python3 --version
   pip list
   ```

4. **网络问题**：确保防火墙允许相应端口
   ```bash
   sudo ufw allow 5000
   ```

### 9. 生产环境部署

```bash
# 使用systemd管理服务
sudo tee /etc/systemd/system/mobile-control.service > /dev/null <<EOF
[Unit]
Description=Mobile Control Tool API
After=network.target

[Service]
User=your-user
WorkingDirectory=/home/your-user/mobile-control-tool
ExecStart=/home/your-user/mobile-control-tool/venv/bin/python3 api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable mobile-control
sudo systemctl start mobile-control

# 查看状态
sudo systemctl status mobile-control
```

### 10. 监控和维护

```bash
# 查看服务状态
sudo systemctl status mobile-control

# 查看日志
sudo journalctl -u mobile-control -f

# 重启服务
sudo systemctl restart mobile-control
```

现在您可以在 hk.wangyaomin.com 服务器上完整地测试和部署移动设备控制工具了！
