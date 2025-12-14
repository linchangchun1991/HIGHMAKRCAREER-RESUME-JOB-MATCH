# Turso 数据库设置指南

## 什么是 Turso？

Turso 是一个基于 SQLite 的云端数据库服务，完美适配 Vercel 等 Serverless 平台。它提供了：
- 🌐 全球分布式数据库
- ⚡ 低延迟访问
- 💰 免费额度充足
- 🔒 安全可靠

## 设置步骤

### 第一步：注册 Turso 账号

1. 打开 https://turso.tech/
2. 点击 **Get Started Free**
3. 使用 GitHub 登录（推荐）

### 第二步：安装 Turso CLI 并创建数据库

在你的电脑终端（不是 Cursor）执行：

```bash
# Mac 用户
brew install tursodatabase/tap/turso

# Windows 用户 (PowerShell)
irm https://get.turso.tech/install.ps1 | iex

# Linux 用户
curl -sSfL https://get.tur.so/install.sh | bash
```

### 第三步：登录并创建数据库

```bash
# 登录 Turso（会打开浏览器进行认证）
turso auth login

# 创建数据库
turso db create highmark-db

# 获取数据库 URL
turso db show highmark-db --url

# 创建访问令牌
turso db tokens create highmark-db
```

### 第四步：配置环境变量

将获取到的信息填入 `.env.local`：

```env
TURSO_DATABASE_URL=libsql://highmark-db-你的用户名.turso.io
TURSO_AUTH_TOKEN=你生成的token
```

**格式说明**：
- `TURSO_DATABASE_URL` 格式：`libsql://数据库名-你的用户名.turso.io`
  - 示例：`libsql://highmark-db-john.turso.io`
  - 获取方式：执行 `turso db show highmark-db --url`
  
- `TURSO_AUTH_TOKEN` 格式：一串长字符串
  - 示例：`eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...`
  - 获取方式：执行 `turso db tokens create highmark-db`

### 第五步：验证连接

启动项目后，数据库表会在首次 API 调用时自动创建。你可以：

1. 运行 `npm run dev`
2. 访问 http://localhost:3000
3. 尝试上传一份简历或岗位
4. 如果成功，说明数据库连接正常

## 本地开发

如果你需要在本地使用 Turso，可以：

1. 使用 Turso 远程数据库（推荐）- 直接使用上面的配置
2. 或使用本地 SQLite（需要修改 `lib/db.ts`）

## 迁移现有数据

如果你有本地 SQLite 数据库需要迁移：

```bash
# 导出本地数据
sqlite3 data/highmark.db .dump > backup.sql

# 在 Turso 中执行 SQL（通过 Turso CLI）
turso db shell highmark-db < backup.sql
```

或者使用 Turso Dashboard 的 SQL 编辑器直接执行 SQL。

## 常用命令

```bash
# 查看所有数据库
turso db list

# 查看数据库信息
turso db show highmark-db

# 查看数据库 URL
turso db show highmark-db --url

# 创建新的访问令牌
turso db tokens create highmark-db

# 列出所有令牌
turso db tokens list highmark-db

# 删除令牌
turso db tokens revoke highmark-db <token-name>

# 打开数据库 Shell（执行 SQL）
turso db shell highmark-db
```

## 注意事项

- Turso 使用异步 API，所有数据库操作都是异步的
- 首次连接可能需要几秒钟建立连接
- 免费版有请求限制，生产环境建议升级
- 数据库表会在首次使用时自动创建（通过 `initDatabase()` 函数）
- 访问令牌要妥善保管，不要提交到 Git

## 故障排查

### 连接失败

1. 检查 `TURSO_DATABASE_URL` 和 `TURSO_AUTH_TOKEN` 是否正确
2. 确认 Token 未过期或被撤销
3. 检查网络连接
4. 确认数据库名称正确

### 表不存在

数据库表会在首次 API 调用时自动创建。如果遇到表不存在的错误，确保：
1. 环境变量配置正确
2. 至少调用一次需要数据库的 API（如上传简历）
3. 检查 `lib/db.ts` 中的 `initDatabase()` 函数是否被调用

### Token 权限问题

如果遇到权限错误：
1. 确认使用的是数据库级别的 token（不是组织 token）
2. 重新创建 token：`turso db tokens create highmark-db`
3. 更新 `.env.local` 中的 `TURSO_AUTH_TOKEN`

## 更多信息

- [Turso 官方文档](https://docs.turso.tech/)
- [Turso CLI 参考](https://docs.turso.tech/cli)
- [Turso Dashboard](https://turso.tech/dashboard)
- [@libsql/client 文档](https://github.com/tursodatabase/libsql-client-ts)
