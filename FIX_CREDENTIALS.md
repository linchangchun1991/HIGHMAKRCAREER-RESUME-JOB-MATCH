# 修复 Git 凭据问题

## 🔍 问题分析

错误信息显示 Git 使用了错误的用户名 `jasonlinchangchun-stack`，但应该使用 `linchangchun1991`。

## ✅ 解决方案

### 方法一：清除凭据缓存后重新推送（推荐）

已执行的步骤：
1. ✅ 清除了 macOS Keychain 中缓存的 GitHub 凭据
2. ✅ 更新了远程仓库 URL，包含正确的用户名

现在执行推送：

```bash
cd /Users/changchun/Desktop/job_scraper
git push -u origin main
```

**认证提示**：
- **Username**: `linchangchun1991`
- **Password**: 输入你的 **Personal Access Token**

### 方法二：使用 Personal Access Token 直接推送

```bash
# 使用 token 作为密码推送
git push -u origin main
# Username: linchangchun1991
# Password: <粘贴你的 Personal Access Token>
```

### 方法三：在 URL 中包含 token（临时方案）

```bash
# 替换 YOUR_TOKEN 为你的实际 token
git remote set-url origin https://linchangchun1991:YOUR_TOKEN@github.com/linchangchun1991/HIGHMAKRCAREER-RESUME-JOB-MATCH.git
git push -u origin main
```

### 方法四：使用 SSH（最安全）

```bash
# 1. 切换到 SSH URL
git remote set-url origin git@github.com:linchangchun1991/HIGHMAKRCAREER-RESUME-JOB-MATCH.git

# 2. 推送（不需要输入密码，如果已配置 SSH key）
git push -u origin main
```

## 🔐 获取 Personal Access Token

如果还没有 Token：

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写信息：
   - **Note**: `HighMark-AI Project`
   - **Expiration**: 选择过期时间
   - **Scopes**: 勾选 `repo`（完整仓库访问权限）
4. 点击 "Generate token"
5. **重要**：复制生成的 token（只显示一次）

## 🛠️ 清除所有缓存的凭据

如果方法一不起作用，可以手动清除：

```bash
# macOS Keychain
git credential-osxkeychain erase
host=github.com
protocol=https
# 按两次回车

# 或者删除 Keychain 中的 GitHub 条目
# 打开"钥匙串访问"应用，搜索 "github.com"，删除相关条目
```

## ✅ 验证配置

```bash
# 检查远程仓库 URL
git remote -v

# 应该显示：
# origin  https://linchangchun1991@github.com/linchangchun1991/HIGHMAKRCAREER-RESUME-JOB-MATCH.git (fetch)
# origin  https://linchangchun1991@github.com/linchangchun1991/HIGHMAKRCAREER-RESUME-JOB-MATCH.git (push)
```

## 📝 推送命令

```bash
cd /Users/changchun/Desktop/job_scraper
git push -u origin main
```

输入：
- Username: `linchangchun1991`
- Password: `<你的 Personal Access Token>`
