# 🚀 快速部署到 Vercel

## 最简单的方法（推荐）

### 方式 1: 通过 Vercel 网页部署（无需安装任何工具）

1. **访问 Vercel**
   - 打开 [https://vercel.com](https://vercel.com)
   - 使用 GitHub/Google 账号登录（免费）

2. **创建新项目**
   - 点击右上角 "Add New..." → "Project"
   - 如果项目在 GitHub：
     - 选择你的仓库
     - 点击 "Import"
   - 如果项目不在 GitHub：
     - 先在 GitHub 创建仓库并上传文件
     - 然后在 Vercel 中导入

3. **配置项目**
   - Framework Preset: 选择 **"Other"**
   - 其他设置保持默认
   - 点击 **"Deploy"**

4. **完成！**
   - 等待 1-2 分钟
   - 你会得到一个类似 `https://your-project.vercel.app` 的链接
   - 这个链接可以分享给任何人使用！

---

### 方式 2: 通过命令行部署

#### 步骤 1: 安装 Vercel CLI
```bash
npm install -g vercel
```

#### 步骤 2: 登录
```bash
vercel login
```

#### 步骤 3: 部署
在项目目录运行：
```bash
./deploy.sh
```

或者直接运行：
```bash
vercel --prod
```

---

## 📁 需要部署的文件

确保以下文件在项目根目录：
- ✅ `index.html` - 主页面
- ✅ `script.js` - JavaScript 逻辑
- ✅ `vercel.json` - Vercel 配置（可选）

---

## 🔒 关于 API Key

**重要提示**：当前 API Key 直接写在代码中。对于生产环境，建议：

1. **使用环境变量**（需要后端支持）
2. **或者**：在 Vercel 项目设置中配置环境变量
3. **或者**：暂时保持现状（仅用于演示）

---

## 🌐 自定义域名

部署后，你可以在 Vercel 项目设置中添加自定义域名：
- 项目 → Settings → Domains
- 添加你的域名（如：resume.highmarkcareer.com）
- Vercel 会自动配置免费 SSL 证书

---

## 🔄 更新部署

每次修改代码后：
- **网页方式**：如果连接了 GitHub，推送代码后会自动重新部署
- **命令行方式**：运行 `vercel --prod` 或 `./deploy.sh`

---

## ❓ 常见问题

**Q: 部署后无法访问？**
A: 检查 Vercel 部署日志，确保没有错误

**Q: API 调用失败？**
A: 检查 API Key 是否正确，以及是否有 CORS 限制

**Q: 如何查看部署日志？**
A: 在 Vercel 控制台的 "Deployments" 标签页查看

---

## 📞 需要帮助？

- Vercel 文档：https://vercel.com/docs
- Vercel 社区：https://github.com/vercel/vercel/discussions
