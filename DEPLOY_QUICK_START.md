# Vercel 快速部署指南

## 🚀 5 分钟快速部署

### 步骤 1: 准备代码
```bash
# 确保代码已提交到 Git
git add .
git commit -m "准备部署"
git push origin main
```

### 步骤 2: 登录 Vercel
1. 访问 https://vercel.com
2. 使用 GitHub/GitLab/Bitbucket 账号登录
3. 点击 "Add New Project"

### 步骤 3: 导入项目
1. 选择你的代码仓库
2. Vercel 会自动检测 Next.js
3. 点击 "Import"

### 步骤 4: 配置环境变量
在 "Environment Variables" 添加：
```
ALIBABA_CLOUD_API_KEY = your_api_key_here
```

### 步骤 5: 部署
点击 "Deploy" 按钮，等待 2-5 分钟完成！

## 📝 详细说明

### 必需的环境变量
- `ALIBABA_CLOUD_API_KEY` - 阿里云通义千问 API Key

### 可选的环境变量
- `ALIBABA_CLOUD_API_ENDPOINT` - API 端点（默认已配置）

### 项目配置
项目已包含以下配置文件：
- ✅ `vercel.json` - Vercel 配置（API 超时 60 秒）
- ✅ `next.config.js` - Next.js 配置（支持 pdf-parse）
- ✅ `.gitignore` - Git 忽略文件（已排除 .env.local）

## ⚠️ 重要提示

1. **API 超时**：Vercel 免费版 API 超时是 10 秒，如果需要 60 秒需要升级到 Pro 计划
2. **文件大小**：上传文件限制 4.5MB（Vercel 免费版）
3. **环境变量**：必须在 Vercel Dashboard 中配置，不要提交到 Git

## 🔧 常见问题

### 构建失败？
- 检查 `package.json` 中的依赖是否正确
- 查看 Vercel 构建日志

### API 超时？
- 免费版限制 10 秒
- 考虑升级到 Pro 计划（60 秒）

### 环境变量未生效？
- 在 Vercel Dashboard 中重新设置
- 重新部署项目

## 📚 更多信息

查看 `VERCEL_DEPLOY.md` 获取详细部署文档。
