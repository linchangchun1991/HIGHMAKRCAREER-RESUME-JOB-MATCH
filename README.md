# 🐴 HIGHMARK 海马职加 - 智能选岗系统

基于 AI 大模型的智能人岗匹配平台，为学员精准推荐最适合的职位。

## ✨ 功能特性

- 🤖 **AI 智能解析** - 自动解析 PDF/Word 简历，提取关键信息
- 🎯 **智能匹配** - 基于阿里通义千问大模型，多维度人岗匹配
- 📊 **可视化评分** - 技能、学历、经验、地点、薪资五维度评分
- 📁 **批量导入** - 支持 Excel 批量导入岗位数据
- 🎨 **精美界面** - 硅谷大厂设计风格，深色主题 + 玻璃拟态

## 🚀 快速开始

### 1. 安装依赖

\`\`\`bash
npm install
\`\`\`

### 2. 配置环境变量

1. 复制 `env.example` 为 `.env.local`

2. **配置阿里云 API Key**：
   - 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
   - 注册/登录后，创建 API Key
   - 填入 `.env.local`：

\`\`\`
QWEN_API_KEY=sk-xxxxxxxxxxxxxx
\`\`\`

3. **配置 Turso 数据库**：
   - 访问 [Turso 官网](https://turso.tech/) 注册账号
   - 创建数据库并获取连接信息
   - 填入 `.env.local`：

\`\`\`
TURSO_DATABASE_URL=libsql://your-database-url.turso.io
TURSO_AUTH_TOKEN=your_auth_token_here
\`\`\`

### 3. 启动项目

\`\`\`bash
npm run dev
\`\`\`

访问 http://localhost:3000

## 📖 使用说明

### 教练端
1. 上传学员简历（PDF/Word/粘贴）
2. AI 自动解析简历信息
3. 查看智能匹配的岗位推荐

### 企拓端
1. 手动添加或批量导入岗位
2. 管理岗位状态
3. 查看岗位匹配情况

## 🛠 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: TailwindCSS
- **数据库**: Turso (云端 SQLite)
- **AI**: 阿里通义千问 API
- **文件解析**: pdf-parse, mammoth, xlsx

## 📦 部署

### Vercel 部署（推荐）
1. Fork 本项目到你的 GitHub
2. 在 Vercel 导入项目
3. 设置环境变量：
   - `QWEN_API_KEY` - 阿里云 API Key
   - `TURSO_DATABASE_URL` - Turso 数据库 URL
   - `TURSO_AUTH_TOKEN` - Turso 认证 Token
4. 部署完成

### 本地/服务器部署
\`\`\`bash
npm run build
npm run start
\`\`\`

## 📄 License

MIT © 2024 HIGHMARK 海马职加
