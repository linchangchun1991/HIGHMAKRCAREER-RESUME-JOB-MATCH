# HighMark-AI 快速启动指南

## 前置要求

确保你的系统已安装：
- Node.js 18+ 
- npm 或 yarn

## 安装步骤

1. **安装依赖**
   ```bash
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **访问应用**
   打开浏览器访问 [http://localhost:3000](http://localhost:3000)

## 页面路由

- `/` - 登录页
- `/dashboard` - 仪表盘（自动重定向到教练端）
- `/dashboard/coach` - 教练端：学员简历分析
- `/dashboard/bd` - 企拓端：岗位库管理
- `/dashboard/history` - 匹配记录

## 功能说明

### 登录页
- 目前为演示版本，输入任意邮箱和密码即可登录
- 登录后自动跳转到仪表盘

### 教练端
- 支持拖拽上传 PDF/Word 格式简历
- 自动解析简历信息
- 显示匹配的岗位列表和匹配度

### 企拓端
- 批量导入岗位（Excel）
- 手动添加岗位
- AI 解析 JD 功能

### 匹配记录
- 查看历史匹配记录
- 显示匹配详情和评分

## 开发说明

- 所有页面都使用客户端组件（"use client"）
- UI 组件位于 `components/ui/` 目录
- 样式使用 Tailwind CSS
- 图标使用 Lucide React

## 注意事项

- 当前版本为演示版本，部分功能（如文件上传、AI 解析）使用模拟数据
- 需要集成实际的 API 和数据库才能实现完整功能
