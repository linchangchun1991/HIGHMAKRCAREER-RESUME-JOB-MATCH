# Vercel 部署指南

## 📋 部署前准备

### 1. 确保代码已提交到 GitHub

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: HIGHMARK 智能选岗系统"

# 在 GitHub 创建新仓库，然后推送
git remote add origin https://github.com/你的用户名/highmark-job-matcher.git
git branch -M main
git push -u origin main
```

### 2. 准备环境变量

在部署前，确保你已经准备好以下环境变量：

- `QWEN_API_KEY` - 阿里云通义千问 API Key
- `TURSO_DATABASE_URL` - Turso 数据库 URL
- `TURSO_AUTH_TOKEN` - Turso 认证 Token

## 🚀 部署步骤

### 方法一：通过 Vercel 网站部署（推荐）

#### 步骤 1：登录 Vercel

1. 访问 [Vercel 官网](https://vercel.com/)
2. 点击 **Sign Up** 或 **Log In**
3. 使用 GitHub 账号登录（推荐）

#### 步骤 2：导入项目

1. 登录后，点击 **Add New...** → **Project**
2. 在 **Import Git Repository** 中，选择你的 GitHub 仓库
3. 如果看不到仓库，点击 **Adjust GitHub App Permissions** 授权访问

#### 步骤 3：配置项目

1. **Project Name**：输入项目名称（如：`highmark-job-matcher`）
2. **Framework Preset**：选择 **Next.js**（会自动检测）
3. **Root Directory**：保持默认 `./`
4. **Build Command**：保持默认 `npm run build`
5. **Output Directory**：保持默认 `.next`
6. **Install Command**：保持默认 `npm install`

#### 步骤 4：配置环境变量

在 **Environment Variables** 部分，添加以下变量：

```
QWEN_API_KEY = 你的阿里云API Key
TURSO_DATABASE_URL = libsql://highmark-db-你的用户名.turso.io
TURSO_AUTH_TOKEN = 你的Turso Token
```

**注意**：
- 确保所有环境变量都添加到 **Production**、**Preview** 和 **Development** 环境
- 点击每个变量旁边的三个环境图标来设置

#### 步骤 5：部署

1. 点击 **Deploy** 按钮
2. 等待构建完成（通常 2-5 分钟）
3. 部署成功后，你会看到一个 **Congratulations** 页面
4. 点击 **Visit** 查看你的网站

### 方法二：通过 Vercel CLI 部署

#### 步骤 1：安装 Vercel CLI

```bash
npm i -g vercel
```

#### 步骤 2：登录 Vercel

```bash
vercel login
```

#### 步骤 3：部署项目

```bash
# 在项目根目录执行
vercel
```

按照提示操作：
- 选择项目范围（个人或团队）
- 确认项目设置
- 添加环境变量（或稍后在 Dashboard 添加）

#### 步骤 4：配置环境变量

```bash
# 添加环境变量
vercel env add QWEN_API_KEY
vercel env add TURSO_DATABASE_URL
vercel env add TURSO_AUTH_TOKEN
```

或者通过 Vercel Dashboard：
1. 进入项目设置
2. 点击 **Environment Variables**
3. 添加所有环境变量

#### 步骤 5：生产环境部署

```bash
# 部署到生产环境
vercel --prod
```

## ✅ 部署后验证

### 1. 检查部署状态

1. 访问 Vercel Dashboard
2. 查看 **Deployments** 标签
3. 确认最新部署状态为 **Ready**

### 2. 测试网站功能

1. 访问你的网站 URL（格式：`https://your-project.vercel.app`）
2. 测试以下功能：
   - ✅ 首页加载正常
   - ✅ 教练端可以上传简历
   - ✅ 企拓端可以上传岗位
   - ✅ AI 解析功能正常
   - ✅ 数据库连接正常

### 3. 检查日志

如果遇到问题，查看 Vercel 日志：

1. 在 Vercel Dashboard 中，点击 **Deployments**
2. 选择最新的部署
3. 点击 **View Function Logs** 查看日志

## 🔧 常见问题

### 问题 1：构建失败

**错误信息**：`Module not found` 或 `Build failed`

**解决方案**：
1. 检查 `package.json` 中所有依赖是否正确
2. 确保 `node_modules` 已提交到 Git（不应该提交）
3. 检查是否有 TypeScript 错误
4. 查看构建日志中的具体错误信息

### 问题 2：环境变量未生效

**错误信息**：`QWEN_API_KEY is not defined` 或 `TURSO_DATABASE_URL is not defined`

**解决方案**：
1. 在 Vercel Dashboard 中检查环境变量是否正确添加
2. 确保环境变量添加到所有环境（Production、Preview、Development）
3. 重新部署项目（环境变量更改后需要重新部署）
4. 检查环境变量名称是否正确（区分大小写）

### 问题 3：数据库连接失败

**错误信息**：`Authentication failed` 或 `Connection timeout`

**解决方案**：
1. 检查 `TURSO_DATABASE_URL` 格式是否正确
2. 确认 `TURSO_AUTH_TOKEN` 未过期
3. 在 Turso Dashboard 中验证数据库状态
4. 检查网络连接（Vercel 服务器需要能访问 Turso）

### 问题 4：API 路由返回 500 错误

**解决方案**：
1. 查看 Vercel Function Logs 获取详细错误信息
2. 检查 API 路由中的错误处理
3. 确认所有依赖都已正确安装
4. 检查 API 响应大小（Vercel 有响应大小限制）

### 问题 5：文件上传失败

**错误信息**：`File too large` 或 `Upload failed`

**解决方案**：
1. Vercel 免费版有文件大小限制（4.5MB）
2. 考虑使用 Vercel Blob Storage 或其他存储服务
3. 或升级到 Vercel Pro 计划

## 📝 部署后维护

### 自动部署

Vercel 会自动部署：
- ✅ 推送到 `main` 分支 → 生产环境
- ✅ 推送到其他分支 → Preview 环境
- ✅ 创建 Pull Request → Preview 环境

### 手动重新部署

1. 在 Vercel Dashboard 中
2. 进入 **Deployments**
3. 找到要重新部署的版本
4. 点击 **...** → **Redeploy**

### 更新环境变量

1. 在 Vercel Dashboard 中
2. 进入 **Settings** → **Environment Variables**
3. 修改或添加环境变量
4. 重新部署项目使更改生效

### 查看分析

1. 在 Vercel Dashboard 中
2. 进入 **Analytics** 标签
3. 查看访问量、性能等数据

## 🔗 相关链接

- [Vercel 官方文档](https://vercel.com/docs)
- [Next.js 部署指南](https://nextjs.org/docs/deployment)
- [Turso 文档](https://docs.turso.tech/)
- [项目 README](./README.md)

## 💡 提示

1. **自定义域名**：在 Vercel Dashboard 的 **Settings** → **Domains** 中添加你的域名
2. **环境变量加密**：Vercel 会自动加密存储环境变量
3. **预览环境**：每个 PR 都会创建一个预览 URL，方便测试
4. **回滚部署**：如果新部署有问题，可以在 Dashboard 中快速回滚到之前的版本

---

部署成功后，你的网站就可以通过 `https://your-project.vercel.app` 访问了！🎉
