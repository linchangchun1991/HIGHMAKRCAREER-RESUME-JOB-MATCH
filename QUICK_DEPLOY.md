# 🚀 一键部署指南

## ✅ 文件已准备就绪！

以下文件已经准备好：
- ✅ `index.html` - 主页面
- ✅ `script.js` - JavaScript 逻辑  
- ✅ `vercel.json` - Vercel 配置
- ✅ `.gitignore` - Git 忽略文件

## 📤 现在只需 3 步即可部署：

### 方法 1: 通过 Vercel 网页（最简单，推荐）

1. **打开 Vercel**
   - 访问：https://vercel.com
   - 使用 GitHub/Google 账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择 "Import Git Repository"
   - 如果项目在 GitHub：选择仓库并导入
   - 如果项目不在 GitHub：
     ```bash
     # 在项目目录运行这些命令，将代码推送到 GitHub
     git remote add origin https://github.com/你的用户名/你的仓库名.git
     git push -u origin main
     ```

3. **部署**
   - Framework Preset: 选择 **"Other"**
   - 点击 **"Deploy"**
   - 等待 1-2 分钟
   - 完成！你会得到一个公开链接

---

### 方法 2: 通过 Vercel CLI（如果已安装 Node.js）

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
cd /Users/changchun/Desktop/job_scraper
vercel --prod
```

---

## 🎯 部署后你会得到：

一个类似这样的链接：
```
https://your-project-name.vercel.app
```

这个链接可以：
- ✅ 分享给任何人使用
- ✅ 在任何设备上访问
- ✅ 自动支持 HTTPS
- ✅ 全球 CDN 加速

---

## 💡 提示

- 如果连接了 GitHub，每次推送代码会自动重新部署
- 可以在 Vercel 项目设置中添加自定义域名
- 所有部署都是免费的（Hobby 计划）

---

## 🆘 需要帮助？

如果遇到问题，检查：
1. 确保 `index.html` 和 `script.js` 在项目根目录
2. 确保 `vercel.json` 配置正确
3. 查看 Vercel 部署日志中的错误信息
