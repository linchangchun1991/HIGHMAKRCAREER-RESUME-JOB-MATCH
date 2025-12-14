# HighMark-AI | 人岗匹配系统

一个基于 Next.js 14 的智能人岗匹配系统，采用硅谷顶级 SaaS 风格设计。

## 技术栈

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Lucide React** (图标库)
- **Shadcn/UI** (组件库)
- **Radix UI** (无障碍组件基础)
- **阿里云通义千问 API** (AI 分析)
- **pdf-parse** (PDF 解析)
- **mammoth** (Word 解析)
- **OpenAI SDK** (兼容模式调用 Qwen)

## 设计风格

- 极简主义设计
- 大量留白
- 配色方案：黑色(#000)、白色(#fff)、深灰色
- 现代高级字体（Inter）
- 流畅的动画交互

## 项目结构

```
highmark-ai/
├── app/
│   ├── dashboard/
│   │   ├── coach/          # 教练端：学员简历分析
│   │   ├── bd/             # 企拓端：岗位库管理
│   │   ├── history/        # 匹配记录
│   │   ├── layout.tsx      # 仪表盘布局（侧边栏）
│   │   └── page.tsx        # 仪表盘首页（重定向）
│   ├── globals.css         # 全局样式
│   ├── layout.tsx          # 根布局
│   └── page.tsx            # 登录页
├── components/
│   └── ui/                 # Shadcn/UI 组件
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── input.tsx
│       ├── table.tsx
│       ├── toast.tsx
│       └── toaster.tsx
├── hooks/
│   └── use-toast.ts        # Toast 钩子
└── lib/
    └── utils.ts            # 工具函数
```

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制环境变量示例文件并配置你的阿里云 API Key：

```bash
cp env.example .env.local
```

编辑 `.env.local` 文件，填入你的阿里云通义千问 API Key：

```env
ALIBABA_CLOUD_API_KEY=your_api_key_here
```

> **获取 API Key：** 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/) 创建 API Key

### 3. 运行开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 3. 构建生产版本

```bash
npm run build
npm start
```

## 功能特性

### 登录页 (`/`)
- 极简设计
- HIGHMARK Logo
- 邮箱和密码登录（目前为演示，可直接登录跳转）

### 仪表盘 (`/dashboard`)
- 侧边栏导航
- 响应式设计（移动端支持）
- 三个主要功能模块

### 教练端 (`/dashboard/coach`)
- 拖拽上传简历（支持 PDF/Word）
- 简历解析结果展示
- 匹配岗位列表
- 匹配度评分

### 企拓端 (`/dashboard/bd`)
- 批量导入岗位
- 手动添加岗位
- AI 解析 JD 功能
- 岗位列表管理

### 匹配记录 (`/dashboard/history`)
- 历史匹配记录查看
- 匹配详情展示

## UI 组件

项目已配置以下 Shadcn/UI 组件：

- ✅ Button
- ✅ Card
- ✅ Input
- ✅ Table
- ✅ Dialog
- ✅ Toast

所有组件都遵循设计系统，支持流畅的动画和交互。

## 开发说明

- 使用 TypeScript 进行类型安全开发
- 遵循 Next.js 14 App Router 规范
- 组件采用客户端组件（"use client"）以支持交互
- 样式使用 Tailwind CSS 工具类
- 动画通过 Tailwind 和 CSS 关键帧实现

## API 集成

项目已集成阿里云通义千问 API，实现以下功能：

- ✅ **简历解析** (`/api/analyze-resume`): 使用 AI 提取简历关键信息
- ✅ **岗位匹配** (`/api/match-jobs`): 智能匹配最合适的岗位

详细 API 使用说明请参考 [API_SETUP.md](./API_SETUP.md)

## 部署到 Vercel

### 快速部署（5 分钟）
1. 将代码推送到 Git 仓库（GitHub/GitLab/Bitbucket）
2. 访问 [Vercel Dashboard](https://vercel.com) 并登录
3. 点击 "Add New Project" 并选择你的仓库
4. 在 "Environment Variables" 中添加 `ALIBABA_CLOUD_API_KEY`
5. 点击 "Deploy" 完成部署

### 详细部署指南
查看 [DEPLOY_QUICK_START.md](./DEPLOY_QUICK_START.md) 或 [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)

### 环境变量配置
**必需**：
- `ALIBABA_CLOUD_API_KEY` - 阿里云通义千问 API Key

**可选**：
- `ALIBABA_CLOUD_API_ENDPOINT` - API 端点（默认已配置）

## 代码质量检查

✅ **无错误**：代码已通过全面检查
- ESLint 检查通过
- TypeScript 类型检查通过
- 所有依赖正确配置
- 错误处理完善

查看 [BUG_CHECK_REPORT.md](./BUG_CHECK_REPORT.md) 了解详细信息

## 后续开发建议

1. ✅ ~~集成真实的简历解析 API~~ (已完成)
2. ✅ ~~实现 AI 匹配算法~~ (已完成)
3. ✅ ~~完善教练端页面~~ (已完成)
4. ✅ ~~完善企拓端页面~~ (已完成)
5. ✅ ~~代码检查和 Bug 修复~~ (已完成)
6. 添加实际的登录认证逻辑
7. 添加数据库存储（岗位库、匹配记录）
8. 实现文件上传到云存储
9. 添加用户权限管理
10. 实现批量岗位导入功能
11. 添加匹配记录历史查询
