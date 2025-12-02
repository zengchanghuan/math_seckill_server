# 部署到 GitHub 指南

本指南将帮助你将这个服务器端项目提交到 GitHub 新仓库。

## 📋 前提条件

- 已安装 Git
- 拥有 GitHub 账户
- 已配置 Git 用户信息（如果还没有，请先配置）

### 配置 Git 用户信息（如果尚未配置）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🚀 提交到 GitHub 的步骤

### 1. 在 GitHub 上创建新仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角的 **"+"** 按钮，选择 **"New repository"**
3. 填写仓库信息：
   - **Repository name**: `math-seckill-server`（或你喜欢的名称）
   - **Description**: "Math Seckill Server Backend API - FastAPI based math problem generator"
   - **Visibility**: 选择 Public 或 Private
   - **⚠️ 重要**: **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 **"Create repository"**

### 2. 连接本地仓库到 GitHub

创建仓库后，GitHub 会显示一个页面，上面有仓库的 URL。使用以下命令连接：

```bash
cd /Users/zengchanghuan/Desktop/workspace/flutter/math_seckill_server

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/math-seckill-server.git

# 或者如果你使用 SSH（推荐）
git remote add origin git@github.com:YOUR_USERNAME/math-seckill-server.git
```

### 3. 推送代码到 GitHub

```bash
# 推送代码到 GitHub（首次推送）
git branch -M main
git push -u origin main
```

如果你使用 HTTPS，GitHub 可能会要求你输入用户名和密码（或访问令牌）。

### 4. 验证

访问你的 GitHub 仓库页面，应该能看到所有文件都已上传。

## 🔐 使用 GitHub Personal Access Token（推荐）

如果使用 HTTPS，GitHub 不再支持密码认证，需要使用 Personal Access Token：

1. 访问 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 **"Generate new token (classic)"**
3. 选择权限：至少勾选 `repo`
4. 生成并复制 token（只显示一次，请保存好）
5. 在推送时，使用 token 作为密码

## 📝 后续更新代码

当你修改代码后，使用以下命令提交和推送：

```bash
# 查看更改
git status

# 添加更改的文件
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push
```

## 🔄 检查远程仓库配置

```bash
# 查看远程仓库
git remote -v

# 如果需要更改远程仓库 URL
git remote set-url origin NEW_URL
```

## ⚠️ 注意事项

1. **venv 目录不会被提交**：`.gitignore` 已配置忽略虚拟环境目录，这是正确的做法
2. **敏感信息**：不要提交包含 API 密钥、密码等敏感信息的文件
3. **分支管理**：当前使用的是 `main` 分支，这是 GitHub 的默认主分支

## 🆘 常见问题

### 问题：推送时提示 "remote origin already exists"

**解决方案**：
```bash
# 删除现有的远程仓库配置
git remote remove origin

# 重新添加
git remote add origin YOUR_REPOSITORY_URL
```

### 问题：推送时认证失败

**解决方案**：
- 确认使用的是 Personal Access Token 而不是密码
- 或者切换到 SSH 认证方式

### 问题：想要重新开始

**解决方案**：
```bash
# 删除 .git 目录（谨慎操作！）
rm -rf .git

# 重新初始化
git init
git add .
git commit -m "Initial commit"
```

