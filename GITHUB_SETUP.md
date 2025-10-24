# GitHub自动发布设置指南

本项目已配置GitHub Actions自动发布功能，可以自动打包和发布Mobile Control Tool到GitHub Releases。

## 🚀 自动发布流程

### 触发条件
- 推送到 `main` 分支
- 修改以下文件时触发：
  - `_assets.yaml`
  - `main.py`
  - `requirements.txt`
  - `package_tool.sh`

### 自动执行步骤
1. **测试阶段**: 运行所有测试确保代码正常
2. **打包阶段**: 自动创建工具包
3. **发布阶段**: 创建GitHub Release并上传工具包

## 📋 设置步骤

### 1. 创建GitHub仓库
```bash
# 在GitHub上创建新仓库
# 然后推送到GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2. 验证Actions运行
推送代码后，访问仓库的 **Actions** 标签页查看自动发布流程：
- https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions

### 3. 检查Releases
成功发布后，访问 **Releases** 页面获取下载链接：
- https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/releases

## 🔗 在Dify中使用

### 获取发布链接
在GitHub Releases页面，复制最新版本的工具包下载链接：
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/releases/download/v1/mobile_control_tool.zip
```

### 在Dify Studio中导入
1. 打开Dify Studio
2. 选择 **工具** → **自定义工具**
3. 点击 **从URL导入**
4. 粘贴上面的下载链接
5. 确认导入

## 📊 版本管理

每次推送代码到main分支时，Actions会自动：
- 递增版本号 (v1, v2, v3...)
- 生成包含最新更改的release notes
- 上传最新的工具包

## 🛠️ 自定义配置

### 修改触发条件
编辑 `.github/workflows/release.yml` 文件：

```yaml
on:
  push:
    branches: [ main, develop ]  # 添加其他分支
    paths:
      - '**/*.py'  # 监控所有Python文件
```

### 修改版本策略
当前使用 `github.run_number` 作为版本号，您可以修改为：
```yaml
tag_name: v${{ github.run_number }}  # 运行编号
# 或者使用日期
tag_name: v${{ github.event.head_commit.timestamp }}
```

## 🔍 故障排除

### Actions不触发
- 确认推送到正确的分支（main）
- 确认修改的文件在paths列表中
- 检查workflow文件语法

### 测试失败
- 查看Actions日志中的错误信息
- 确保所有依赖正确安装
- 检查Python版本兼容性

### 打包失败
- 确认package_tool.sh有执行权限
- 检查必需文件是否存在
- 查看Actions运行日志

### 发布失败
- 确认GITHUB_TOKEN权限
- 检查release是否已存在
- 查看详细错误日志

## 📈 优势

✅ **自动化**: 推送代码自动发布
✅ **测试保证**: 发布前运行完整测试
✅ **版本控制**: 自动版本管理和changelog
✅ **分发便捷**: 提供稳定下载链接
✅ **持续集成**: 确保代码质量

## 🎯 最佳实践

1. **提交规范**: 使用清晰的commit消息
2. **测试覆盖**: 确保测试覆盖所有功能
3. **文档更新**: 及时更新README和文档
4. **定期发布**: 定期推送改进到main分支

现在您的工具发布流程已经完全自动化了！🎉
