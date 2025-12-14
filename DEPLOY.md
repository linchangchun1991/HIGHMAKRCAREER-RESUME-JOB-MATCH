# 部署到 Vercel 指南

## 方法一：通过 Vercel 网站部署（推荐）

### 步骤 1: 准备项目
确保以下文件在项目根目录：
- `index.html`
- `script.js`

### 步骤 2: 访问 Vercel
1. 打开浏览器，访问 [https://vercel.com](https://vercel.com)
2. 使用 GitHub、GitLab 或 Bitbucket 账号登录（如果没有账号，先注册）

### 步骤 3: 创建新项目
1. 点击 "Add New..." → "Project"
2. 如果项目已经在 Git 仓库中：
   - 选择你的仓库
   - 点击 "Import"
3. 如果项目不在 Git 仓库中：
   - 先创建一个 Git 仓库（GitHub/GitLab）
   - 将项目文件推送到仓库
   - 然后在 Vercel 中导入

### 步骤 4: 配置项目
- **Framework Preset**: 选择 "Other" 或 "Static Site"
- **Root Directory**: 留空（如果文件在根目录）
- **Build Command**: 留空（静态站点不需要构建）
- **Output Directory**: 留空

### 步骤 5: 部署
1. 点击 "Deploy"
2. 等待部署完成（通常 1-2 分钟）
3. 部署完成后，你会得到一个类似 `https://your-project.vercel.app` 的链接

## 方法二：通过 Vercel CLI 部署

### 步骤 1: 安装 Vercel CLI
```bash
npm install -g vercel
```

### 步骤 2: 登录 Vercel
```bash
vercel login
```

### 步骤 3: 部署项目
在项目根目录运行：
```bash
vercel
```

按照提示操作：
- 是否要设置和部署？输入 `Y`
- 是否要覆盖现有设置？输入 `N`（首次部署）
- 项目名称：输入项目名称或直接回车使用默认值

### 步骤 4: 生产环境部署
```bash
vercel --prod
```

## 方法三：通过 GitHub 自动部署（推荐用于持续更新）

### 步骤 1: 创建 GitHub 仓库
1. 在 GitHub 上创建新仓库
2. 将项目文件推送到仓库：
```bash
git init
git add index.html script.js vercel.json
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 步骤 2: 在 Vercel 中连接 GitHub
1. 登录 Vercel
2. 点击 "Add New..." → "Project"
3. 选择 "Import Git Repository"
4. 选择你的 GitHub 仓库
5. 点击 "Import"

### 步骤 3: 配置自动部署
- Vercel 会自动检测到 `vercel.json` 配置文件
- 每次推送到 GitHub，Vercel 会自动重新部署

## 注意事项

1. **API Key 安全**：当前 API Key 直接写在 `script.js` 中。建议：
   - 使用 Vercel 的环境变量功能
   - 在 Vercel 项目设置中添加环境变量
   - 修改 `script.js` 使用环境变量（需要后端支持）

2. **CORS 问题**：如果遇到跨域问题，Vercel 会自动处理静态资源的 CORS。

3. **自定义域名**：
   - 在 Vercel 项目设置中可以添加自定义域名
   - 支持免费 SSL 证书

## 快速部署命令（如果已安装 Vercel CLI）

```bash
# 在项目根目录执行
vercel --prod
```

部署完成后，你会得到一个公开的 URL，可以分享给任何人使用！
