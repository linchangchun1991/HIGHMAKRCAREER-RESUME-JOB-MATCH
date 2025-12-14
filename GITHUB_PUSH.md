# 推送到 GitHub 仓库指南

## 📋 当前状态

代码已提交到本地 Git 仓库，现在需要推送到 GitHub。

## 🚀 推送到 GitHub 的步骤

### 方法一：创建新仓库并推送（推荐）

#### 1. 在 GitHub 上创建新仓库
1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `highmark-ai` (或你喜欢的名称)
   - **Description**: `HighMark-AI 人岗匹配系统 - 基于 Next.js 14 的智能人岗匹配平台`
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 "Create repository"

#### 2. 连接远程仓库并推送
```bash
# 在项目目录下执行
cd /Users/changchun/Desktop/job_scraper

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/highmark-ai.git

# 或者使用 SSH（如果已配置 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/highmark-ai.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 方法二：推送到现有仓库

如果你已经有一个 GitHub 仓库：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送到 GitHub
git push -u origin main
```

### 方法三：使用 GitHub CLI（如果已安装）

```bash
# 创建并推送仓库
gh repo create highmark-ai --public --source=. --remote=origin --push
```

## 🔐 身份验证

### 使用 Personal Access Token（推荐）

1. 在 GitHub 上生成 Token：
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token"
   - 选择权限：`repo`（完整仓库访问权限）
   - 复制生成的 token

2. 推送时使用 token 作为密码：
```bash
git push -u origin main
# Username: 你的 GitHub 用户名
# Password: 粘贴你的 token（不是 GitHub 密码）
```

### 使用 SSH Key（更安全）

1. 生成 SSH key（如果还没有）：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. 添加 SSH key 到 GitHub：
   - 复制公钥：`cat ~/.ssh/id_ed25519.pub`
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - 粘贴公钥并保存

3. 使用 SSH URL：
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/highmark-ai.git
git push -u origin main
```

## 📝 快速命令参考

```bash
# 检查远程仓库配置
git remote -v

# 查看当前分支
git branch

# 查看提交历史
git log --oneline

# 推送到 GitHub
git push origin main

# 如果遇到冲突，先拉取
git pull origin main --rebase
git push origin main
```

## ⚠️ 注意事项

1. **不要提交敏感信息**：
   - ✅ `.env.local` 已在 `.gitignore` 中
   - ✅ 确保没有提交 API Key
   - ✅ 确保没有提交密码

2. **文件大小限制**：
   - GitHub 单个文件限制：100MB
   - 大文件考虑使用 Git LFS

3. **已忽略的文件**：
   - `node_modules/` - 依赖包
   - `.env.local` - 环境变量
   - `*.log` - 日志文件
   - `*.db` - 数据库文件
   - `data/` - 数据文件

## 🎯 推送后的操作

### 1. 在 GitHub 上验证
- 检查所有文件是否已上传
- 检查 README.md 是否正确显示
- 检查代码结构是否完整

### 2. 配置仓库设置
- 添加仓库描述
- 添加 Topics（标签）：`nextjs`, `typescript`, `ai`, `job-matching`
- 设置仓库可见性

### 3. 连接 Vercel（可选）
- 在 Vercel Dashboard 中导入 GitHub 仓库
- 配置环境变量
- 自动部署

## 🆘 常见问题

### 问题 1: 推送被拒绝
```bash
# 先拉取远程更改
git pull origin main --rebase
# 然后再次推送
git push origin main
```

### 问题 2: 认证失败
- 检查用户名和密码是否正确
- 如果使用 token，确保 token 有正确的权限
- 考虑使用 SSH key

### 问题 3: 文件太大
```bash
# 检查大文件
git ls-files | xargs ls -la | sort -k5 -rn | head -10

# 如果文件确实太大，考虑使用 Git LFS
git lfs install
git lfs track "*.pdf"
git add .gitattributes
```

## 📚 相关资源

- [GitHub 文档](https://docs.github.com)
- [Git 官方文档](https://git-scm.com/doc)
- [GitHub CLI 文档](https://cli.github.com)
