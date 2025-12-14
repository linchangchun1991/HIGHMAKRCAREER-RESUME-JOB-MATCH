# 🚀 完整部署指南：GitHub + Vercel

## 第一步：推送到 GitHub

### 1.1 检查 Git 状态

```bash
# 在项目根目录执行
cd /Users/changchun/Desktop/job_scraper

# 检查当前状态
git status
```

### 1.2 初始化 Git（如果还没有）

```bash
# 如果还没有初始化 Git
git init

# 检查 .gitignore 是否存在（确保敏感文件不会被提交）
ls -la .gitignore
```

### 1.3 添加所有文件

```bash
# 添加所有文件到暂存区
git add .

# 查看将要提交的文件
git status
```

### 1.4 提交代码

```bash
# 提交代码
git commit -m "Initial commit: HIGHMARK 智能选岗系统"
```

### 1.5 在 GitHub 创建仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写仓库信息：
   - **Repository name**: `highmark-job-matcher`（或你喜欢的名字）
   - **Description**: `HIGHMARK 海马职加 - 智能选岗系统`
   - **Visibility**: 选择 **Public** 或 **Private**
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 **Create repository**

### 1.6 连接本地仓库到 GitHub

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/highmark-job-matcher.git

# 或者使用 SSH（如果你配置了 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/highmark-job-matcher.git

# 验证远程仓库
git remote -v
```

### 1.7 推送到 GitHub

```bash
# 设置主分支为 main
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**如果遇到认证问题**：
- 使用 Personal Access Token（推荐）
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. 点击 **Generate new token**
  3. 选择权限：`repo`（完整仓库访问权限）
  4. 复制生成的 token
  5. 推送时使用 token 作为密码

```bash
# 推送时，用户名输入你的 GitHub 用户名
# 密码输入刚才生成的 Personal Access Token
git push -u origin main
```

### 1.8 验证推送成功

1. 访问你的 GitHub 仓库页面
2. 确认所有文件都已上传
3. 确认 `.env.local` 文件**不在**仓库中（应该在 .gitignore 中）

---

## 第二步：部署到 Vercel

### 2.1 登录 Vercel

1. 访问 [Vercel 官网](https://vercel.com/)
2. 点击 **Sign Up** 或 **Log In**
3. 选择 **Continue with GitHub**（推荐，方便连接仓库）

### 2.2 导入项目

1. 登录后，点击 **Add New...** → **Project**
2. 在 **Import Git Repository** 中，你会看到你的 GitHub 仓库列表
3. 找到 `highmark-job-matcher`（或你的仓库名）
4. 点击 **Import**

**如果看不到仓库**：
- 点击 **Adjust GitHub App Permissions**
- 授权 Vercel 访问你的仓库
- 刷新页面

### 2.3 配置项目

在 **Configure Project** 页面：

1. **Project Name**: `highmark-job-matcher`（或自定义）
2. **Framework Preset**: 选择 **Next.js**（会自动检测）
3. **Root Directory**: 保持默认 `./`
4. **Build Command**: 保持默认 `npm run build`
5. **Output Directory**: 保持默认 `.next`
6. **Install Command**: 保持默认 `npm install`

### 2.4 配置环境变量（重要！）

在 **Environment Variables** 部分，点击 **Add** 添加以下变量：

#### 变量 1：QWEN_API_KEY
- **Name**: `QWEN_API_KEY`
- **Value**: 你的阿里云 API Key（从 `.env.local` 中复制）
- **Environment**: 勾选所有三个（Production、Preview、Development）

#### 变量 2：TURSO_DATABASE_URL
- **Name**: `TURSO_DATABASE_URL`
- **Value**: `libsql://highmark-db-你的用户名.turso.io`（从 `.env.local` 中复制）
- **Environment**: 勾选所有三个

#### 变量 3：TURSO_AUTH_TOKEN
- **Name**: `TURSO_AUTH_TOKEN`
- **Value**: 你的 Turso Token（从 `.env.local` 中复制）
- **Environment**: 勾选所有三个

**重要提示**：
- 确保每个变量都添加到所有环境（点击变量名旁边的三个环境图标）
- 不要有空格或多余字符
- 复制时确保完整复制

### 2.5 部署

1. 确认所有环境变量都已添加
2. 点击 **Deploy** 按钮
3. 等待构建完成（通常 2-5 分钟）

### 2.6 查看部署结果

部署完成后：

1. 你会看到 **Congratulations** 页面
2. 点击 **Visit** 查看你的网站
3. 你的网站 URL 格式：`https://highmark-job-matcher.vercel.app`

---

## 第三步：验证部署

### 3.1 测试网站

访问你的网站，测试以下功能：

1. ✅ **首页加载**：访问首页，确认界面正常显示
2. ✅ **教练端**：点击"教练端"，尝试上传简历
3. ✅ **企拓端**：点击"企拓端"，尝试上传岗位
4. ✅ **AI 功能**：测试简历解析和岗位匹配

### 3.2 检查日志

如果遇到问题：

1. 在 Vercel Dashboard 中，点击 **Deployments**
2. 选择最新的部署
3. 点击 **View Function Logs** 查看错误日志

### 3.3 常见问题排查

#### 问题：环境变量未生效
**解决**：
- 检查环境变量是否正确添加
- 确保添加到所有环境（Production、Preview、Development）
- 重新部署项目

#### 问题：数据库连接失败
**解决**：
- 检查 `TURSO_DATABASE_URL` 和 `TURSO_AUTH_TOKEN` 是否正确
- 确认 Token 未过期
- 查看 Vercel 日志获取详细错误

#### 问题：构建失败
**解决**：
- 查看构建日志中的具体错误
- 检查 `package.json` 依赖是否正确
- 确保没有 TypeScript 错误

---

## 第四步：后续更新

### 4.1 更新代码并推送

```bash
# 修改代码后
git add .
git commit -m "Update: 描述你的更改"
git push origin main
```

### 4.2 自动部署

Vercel 会自动：
- ✅ 检测到 GitHub 推送
- ✅ 自动重新构建
- ✅ 自动部署到生产环境

你可以在 Vercel Dashboard 的 **Deployments** 中查看部署状态。

### 4.3 预览部署

当你创建 Pull Request 时：
- Vercel 会自动创建预览环境
- 每个 PR 都有独立的预览 URL
- 方便测试新功能

---

## 📝 快速命令参考

### Git 命令
```bash
# 检查状态
git status

# 添加文件
git add .

# 提交
git commit -m "你的提交信息"

# 推送到 GitHub
git push origin main

# 查看远程仓库
git remote -v
```

### Vercel CLI（可选）
```bash
# 安装
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 生产环境部署
vercel --prod
```

---

## 🔗 相关链接

- [GitHub 文档](https://docs.github.com/)
- [Vercel 文档](https://vercel.com/docs)
- [项目 README](./README.md)
- [Turso 设置指南](./TURSO_SETUP.md)

---

## 💡 提示

1. **保护敏感信息**：确保 `.env.local` 在 `.gitignore` 中
2. **环境变量**：每次修改环境变量后需要重新部署
3. **自定义域名**：在 Vercel Dashboard → Settings → Domains 中添加
4. **监控**：在 Vercel Dashboard 中查看 Analytics 了解访问情况

---

**完成！** 🎉 你的网站现在应该可以通过 Vercel URL 访问了！
