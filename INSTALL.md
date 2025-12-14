# 安装和使用指南

## 快速开始

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

**注意**：这一步很重要！如果不安装浏览器组件，脚本将无法运行。

### 3. 运行脚本

```bash
python job_scraper_main.py
```

## 详细说明

### 环境要求

- Python 3.7 或更高版本
- 稳定的网络连接
- 足够的磁盘空间（用于存储Excel文件）

### 安装步骤详解

#### 步骤1：检查Python版本

```bash
python --version
# 或
python3 --version
```

确保版本 >= 3.7

#### 步骤2：安装依赖库

```bash
# 使用pip
pip install playwright pandas openpyxl

# 或使用pip3
pip3 install playwright pandas openpyxl

# 或从requirements.txt安装
pip install -r requirements.txt
```

#### 步骤3：安装Playwright浏览器

```bash
# 安装Chromium浏览器（推荐，体积较小）
playwright install chromium

# 或安装所有浏览器（包括Firefox和WebKit）
playwright install
```

**常见问题**：

- 如果 `playwright` 命令找不到，尝试：
  ```bash
  python -m playwright install chromium
  ```

- 如果下载速度慢，可以设置镜像：
  ```bash
  export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
  playwright install chromium
  ```

### 配置说明

脚本会自动读取 `job_search_configs.py` 中的配置。如果需要修改搜索条件，请编辑该文件。

### 运行选项

#### 后台运行（无界面）

编辑 `job_scraper_main.py`，将第527行的 `headless=False` 改为 `headless=True`：

```python
scraper = JobScraper(headless=True)
```

#### 自定义输出文件名

修改 `save_to_excel` 方法调用，传入自定义文件名。

### 输出文件

脚本运行完成后，会在当前目录生成Excel文件：

- 文件名格式：`job_hunting_results_YYYY-MM-DD.xlsx`
- 包含所有抓取到的职位信息
- 已自动去重和格式化

### 故障排除

#### 问题1：ModuleNotFoundError

**错误信息**：`ModuleNotFoundError: No module named 'playwright'`

**解决方法**：
```bash
pip install playwright
playwright install chromium
```

#### 问题2：浏览器启动失败

**错误信息**：`Executable doesn't exist`

**解决方法**：
```bash
playwright install chromium
```

#### 问题3：网络连接超时

**解决方法**：
- 检查网络连接
- 尝试使用VPN或代理
- 增加超时时间（修改代码中的timeout参数）

#### 问题4：找不到职位数据

**可能原因**：
- 网站结构已变化
- 搜索关键词无结果
- 城市名称不匹配

**解决方法**：
- 手动访问网站确认结构
- 检查配置中的关键词和城市是否正确
- 查看控制台输出的错误信息

### 性能优化建议

1. **减少配置数量**：如果配置太多，可以分批运行
2. **调整休眠时间**：如果网络稳定，可以减少 `random_sleep` 的时间
3. **使用代理**：如果频繁被封IP，考虑使用代理服务

### 注意事项

⚠️ **重要提示**：

1. 请遵守网站的robots.txt和使用条款
2. 不要过于频繁地运行脚本，避免给服务器造成压力
3. 抓取的数据仅供个人使用，请勿用于商业用途
4. 网站结构可能会变化，需要定期更新选择器

### 技术支持

如果遇到问题：

1. 检查控制台输出的错误信息
2. 确认所有依赖已正确安装
3. 验证网络连接是否正常
4. 查看 `job_scraper_README.md` 获取更多信息

