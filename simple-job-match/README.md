# AI 简历匹配助手

一个基于 Next.js 和阿里云通义千问的智能简历匹配系统。

## 功能特点

- 🎯 智能简历分析：AI 自动分析简历内容
- 📊 岗位匹配：从岗位库中推荐最匹配的岗位
- 💡 改进建议：提供针对性的简历优化建议
- 🎨 精美 UI：现代化的蓝色系界面设计

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

确保 `.env.local` 文件已正确配置：

```
ALI_API_KEY=sk-你的阿里云密钥
ALI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 3. 运行开发服务器

```bash
npm run dev
```

打开浏览器访问 [http://localhost:3000](http://localhost:3000)

## 如何添加岗位

直接编辑 `lib/data.ts` 文件，在 `JOBS` 数组中添加新的岗位对象：

```typescript
{
  id: "6",
  title: "岗位名称",
  company: "公司名称",
  salary: "薪资范围",
  description: "职责和要求描述"
}
```

## 部署到 Vercel

1. 将代码推送到 GitHub
2. 在 Vercel 中导入项目
3. 在 Vercel 的环境变量中添加：
   - `ALI_API_KEY`
   - `ALI_BASE_URL`
4. 点击部署

## 技术栈

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- OpenAI SDK (兼容阿里云 API)
