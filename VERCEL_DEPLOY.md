# Vercel 部署指南

## 📋 部署前检查清单

### 1. 代码检查
- ✅ 所有 TypeScript 类型错误已修复
- ✅ ESLint 检查通过
- ✅ 所有依赖已正确安装
- ✅ 环境变量配置正确

### 2. 环境变量准备
确保以下环境变量已准备好：
- `ALIBABA_CLOUD_API_KEY` - 阿里云通义千问 API Key
- `ALIBABA_CLOUD_API_ENDPOINT` (可选) - API 端点

## 🚀 部署步骤

### 方法一：通过 Vercel Dashboard（推荐）

#### 1. 准备代码仓库
```bash
# 确保代码已提交到 Git 仓库（GitHub、GitLab 或 Bitbucket）
git add .
git commit -m "准备部署到 Vercel"
git push origin main
```

#### 2. 登录 Vercel
1. 访问 [Vercel Dashboard](https://vercel.com)
2. 使用 GitHub/GitLab/Bitbucket 账号登录
3. 点击 "Add New Project"

#### 3. 导入项目
1. 选择你的代码仓库
2. Vercel 会自动检测 Next.js 项目
3. 点击 "Import"

#### 4. 配置项目
- **Framework Preset**: Next.js（自动检测）
- **Root Directory**: `./`（默认）
- **Build Command**: `npm run build`（默认）
- **Output Directory**: `.next`（默认）
- **Install Command**: `npm install`（默认）

#### 5. 配置环境变量
在 "Environment Variables" 部分添加：
```
ALIBABA_CLOUD_API_KEY=your_api_key_here
```

如果需要自定义端点：
```
ALIBABA_CLOUD_API_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1
```

#### 6. 部署
1. 点击 "Deploy"
2. 等待构建完成（通常 2-5 分钟）
3. 部署成功后会自动获得一个 URL

### 方法二：通过 Vercel CLI

#### 1. 安装 Vercel CLI
```bash
npm i -g vercel
```

#### 2. 登录 Vercel
```bash
vercel login
```

#### 3. 部署项目
```bash
# 在项目根目录执行
vercel
```

#### 4. 配置环境变量
```bash
# 设置环境变量
vercel env add ALIBABA_CLOUD_API_KEY

# 选择环境（Production、Preview、Development）
# 输入你的 API Key
```

#### 5. 生产环境部署
```bash
vercel --prod
```

## ⚙️ 项目配置说明

### vercel.json
项目已包含 `vercel.json` 配置文件：
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["hkg1"],
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 60
    }
  }
}
```

**配置说明**：
- `regions`: 选择香港区域（hkg1）以获得更好的中国访问速度
- `maxDuration`: API 路由最大执行时间 60 秒（用于 AI 解析）

### next.config.js
已配置：
- Webpack 配置以支持 Node.js 模块（pdf-parse）
- 增加 API 路由 body 大小限制（10mb）

## 🔧 常见问题解决

### 1. 构建失败：pdf-parse 模块错误
**问题**：`Module not found: Can't resolve 'pdf-parse'`

**解决方案**：
- 确保 `package.json` 中包含 `pdf-parse`
- 检查 `next.config.js` 中的 webpack 配置
- 如果问题持续，尝试添加 `serverComponentsExternalPackages`：

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['pdf-parse'],
  },
}
```

### 2. API 路由超时
**问题**：AI 解析请求超时

**解决方案**：
- 检查 `vercel.json` 中的 `maxDuration` 设置
- 确保 API 路由中设置了 `export const maxDuration = 60`
- 考虑优化 AI 调用逻辑

### 3. 环境变量未生效
**问题**：部署后环境变量未加载

**解决方案**：
- 在 Vercel Dashboard 中检查环境变量设置
- 确保环境变量名称正确（区分大小写）
- 重新部署项目以应用环境变量更改

### 4. 文件上传大小限制
**问题**：上传大文件时失败

**解决方案**：
- Vercel 默认限制为 4.5MB
- 对于更大的文件，考虑使用 Vercel Blob Storage
- 或调整 `next.config.js` 中的 `bodySizeLimit`

## 📊 部署后验证

### 1. 检查部署状态
访问 Vercel Dashboard，确认：
- ✅ 构建成功
- ✅ 部署成功
- ✅ 域名可访问

### 2. 功能测试
1. **登录页面**：访问根路径 `/`
2. **仪表盘**：登录后访问 `/dashboard`
3. **教练端**：测试文件上传和解析功能
4. **企拓端**：测试岗位添加和 AI 解析功能

### 3. API 测试
```bash
# 测试简历解析 API
curl -X POST https://your-domain.vercel.app/api/analyze-resume \
  -F "file=@resume.pdf"

# 测试 JD 解析 API
curl -X POST https://your-domain.vercel.app/api/parse-jd \
  -H "Content-Type: application/json" \
  -d '{"jdText":"招聘高级前端工程师..."}'
```

## 🔄 持续部署

### 自动部署
Vercel 会自动：
- 监听 Git 仓库的 push 事件
- 自动触发构建和部署
- 为每个分支创建预览部署

### 手动部署
```bash
# 部署到生产环境
vercel --prod

# 部署到预览环境
vercel
```

## 📝 环境变量管理

### 生产环境
在 Vercel Dashboard 中设置：
- `ALIBABA_CLOUD_API_KEY` (Production)

### 预览环境
为预览环境设置不同的 API Key（如果需要）

### 开发环境
本地使用 `.env.local` 文件

## 🎯 性能优化建议

1. **启用 Edge Functions**（如果适用）
2. **配置 CDN 缓存**
3. **优化图片加载**（使用 Next.js Image 组件）
4. **启用压缩**（Vercel 自动启用）

## 📚 相关资源

- [Vercel 文档](https://vercel.com/docs)
- [Next.js 部署文档](https://nextjs.org/docs/deployment)
- [Vercel CLI 文档](https://vercel.com/docs/cli)

## 🆘 获取帮助

如果遇到问题：
1. 查看 Vercel Dashboard 中的构建日志
2. 检查浏览器控制台的错误信息
3. 查看 Vercel 社区论坛
4. 联系 Vercel 支持
