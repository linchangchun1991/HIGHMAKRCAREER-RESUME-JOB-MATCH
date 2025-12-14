# 数据库迁移总结：SQLite → Turso

## ✅ 已完成的更改

### 1. 依赖更新 (`package.json`)
- ❌ 移除：`better-sqlite3` 和 `@types/better-sqlite3`
- ✅ 添加：`@libsql/client@^0.4.3`

### 2. 数据库客户端 (`lib/db.ts`)
- ✅ 从 `better-sqlite3` 迁移到 `@libsql/client`
- ✅ 使用异步 API（`db.execute()` 替代 `db.prepare().run()`）
- ✅ 添加 `initDatabase()` 函数用于初始化表结构
- ✅ 支持 Turso 云端数据库

### 3. API 路由更新
所有 API 路由已更新为使用异步数据库操作：

- ✅ `app/api/resume/parse/route.ts`
- ✅ `app/api/jobs/route.ts`
- ✅ `app/api/jobs/batch/route.ts`
- ✅ `app/api/match/route.ts`

### 4. 配置文件更新
- ✅ `next.config.js` - 移除 better-sqlite3 相关配置
- ✅ `env.example` - 添加 Turso 环境变量
- ✅ `README.md` - 更新部署说明
- ✅ 新增 `TURSO_SETUP.md` - Turso 设置指南

## 🔄 API 变更说明

### 同步 → 异步

**之前 (better-sqlite3):**
```typescript
const jobs = db.prepare('SELECT * FROM jobs').all();
db.prepare('INSERT INTO jobs ...').run(...);
```

**现在 (Turso):**
```typescript
const result = await db.execute({ sql: 'SELECT * FROM jobs' });
const jobs = result.rows;
await db.execute({ sql: 'INSERT INTO jobs ...', args: [...] });
```

### 数据格式变更

Turso 返回的数据格式略有不同：
- 使用 `result.rows` 获取数据
- 每行数据是对象，字段名需要从 `row.fieldName` 访问
- JSON 字段需要手动解析

## 📝 下一步操作

### 1. 安装新依赖
```bash
npm install
```

### 2. 配置 Turso
参考 `TURSO_SETUP.md` 完成 Turso 数据库设置。

### 3. 设置环境变量
在 `.env.local` 中添加：
```env
TURSO_DATABASE_URL=libsql://your-database-url.turso.io
TURSO_AUTH_TOKEN=your_auth_token_here
```

### 4. 测试
```bash
npm run dev
```

首次运行时会自动创建数据库表。

## ⚠️ 注意事项

1. **异步操作**：所有数据库操作现在都是异步的，确保使用 `await`
2. **环境变量**：必须配置 `TURSO_DATABASE_URL` 和 `TURSO_AUTH_TOKEN`
3. **数据迁移**：如果有现有数据，需要手动迁移到 Turso
4. **本地开发**：本地开发也需要使用 Turso（或修改代码支持本地 SQLite）

## 🐛 故障排查

### 错误：`TURSO_DATABASE_URL is not defined`
- 检查 `.env.local` 文件是否存在
- 确认环境变量名称正确
- 重启开发服务器

### 错误：`Authentication failed`
- 检查 `TURSO_AUTH_TOKEN` 是否正确
- 确认 Token 未过期
- 重新生成 Token

### 表不存在错误
- 数据库表会在首次 API 调用时自动创建
- 确保至少调用一次需要数据库的 API

## 📚 相关文档

- [Turso 官方文档](https://docs.turso.tech/)
- [@libsql/client 文档](https://github.com/tursodatabase/libsql-client-ts)
- `TURSO_SETUP.md` - Turso 设置指南
