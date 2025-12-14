# API 配置和使用说明

## 环境变量配置

1. **复制环境变量示例文件**
   ```bash
   cp env.example .env.local
   ```

2. **配置阿里云通义千问 API Key**
   
   编辑 `.env.local` 文件，填入你的阿里云 API Key：
   ```env
   ALIBABA_CLOUD_API_KEY=your_actual_api_key_here
   ```

   > **获取 API Key 的方法：**
   > 1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
   > 2. 创建 API Key
   > 3. 将 API Key 复制到 `.env.local` 文件中

3. **（可选）自定义 API 端点**
   
   如果需要使用自定义端点，可以添加：
   ```env
   ALIBABA_CLOUD_API_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

## API 端点说明

### 1. `/api/analyze-resume` - 简历解析

**功能：** 解析上传的 PDF 或 Word 简历文件，使用 AI 提取关键信息。

**请求方法：** `POST`

**请求格式：** `multipart/form-data`

**请求参数：**
- `file` (File): PDF 或 Word 文档文件

**响应格式：**
```json
{
  "success": true,
  "data": {
    "name": "姓名",
    "education": "教育背景",
    "skills": {
      "hard": ["硬技能1", "硬技能2"],
      "soft": ["软技能1", "软技能2"]
    },
    "experience": ["项目经验1", "项目经验2"],
    "intention": "求职意向"
  },
  "rawText": "原始文本内容（前500字符）"
}
```

**错误响应：**
```json
{
  "error": "错误信息",
  "message": "详细错误描述"
}
```

**使用示例：**
```typescript
const formData = new FormData()
formData.append("file", file)

const response = await fetch("/api/analyze-resume", {
  method: "POST",
  body: formData,
})

const result = await response.json()
```

### 2. `/api/match-jobs` - 岗位匹配

**功能：** 根据简历分析结果，匹配最合适的岗位。

**请求方法：** `POST`

**请求格式：** `application/json`

**请求体：**
```json
{
  "resumeAnalysis": {
    "name": "姓名",
    "education": "教育背景",
    "skills": {
      "hard": ["硬技能"],
      "soft": ["软技能"]
    },
    "experience": ["项目经验"],
    "intention": "求职意向"
  },
  "jobs": [
    {
      "id": "1",
      "title": "岗位名称",
      "company": "公司名称",
      "location": "工作地点",
      "salary": "薪资范围",
      "description": "岗位描述",
      "requirements": ["要求1", "要求2"]
    }
  ]
}
```

**响应格式：**
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "title": "岗位名称",
      "company": "公司名称",
      "matchScore": 95,
      "recommendation": "推荐理由",
      "gapAnalysis": "差距分析"
    }
  ]
}
```

**使用示例：**
```typescript
const response = await fetch("/api/match-jobs", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    resumeAnalysis: parsedResume,
    jobs: jobList,
  }),
})

const result = await response.json()
```

## AI 提示词说明

### 简历解析提示词

系统会使用以下提示词调用 Qwen-Turbo 模型：

```
你是一个资深的职业规划专家。请分析这份简历，提取以下信息并以 JSON 格式返回：
{
  "name": "姓名",
  "education": "教育背景（包括学校、专业、学历）",
  "skills": {
    "hard": ["硬技能1", "硬技能2"],
    "soft": ["软技能1", "软技能2"]
  },
  "experience": ["项目经验摘要1", "项目经验摘要2"],
  "intention": "求职意向（岗位方向、行业偏好等）"
}
```

### 岗位匹配提示词

系统会使用以下评分标准进行匹配：

1. **专业是否对口**（30分）：教育背景与岗位要求的匹配度
2. **技能重合度**（40分）：硬技能和软技能与岗位要求的匹配度
3. **项目经验相关性**（20分）：项目经验与岗位职责的匹配度
4. **求职意向匹配度**（10分）：求职意向与岗位的匹配度

## 支持的文件格式

- **PDF**: `.pdf`
- **Word**: `.doc`, `.docx`

## 错误处理

API 包含完善的错误处理机制：

1. **文件格式验证**：自动检测文件类型
2. **内容验证**：确保文件内容不为空
3. **API 调用错误**：捕获并返回详细的错误信息
4. **JSON 解析失败**：提供备用解析方案

## 注意事项

1. **API Key 安全**：请勿将 `.env.local` 文件提交到版本控制系统
2. **文件大小限制**：建议文件大小不超过 10MB
3. **API 调用频率**：注意阿里云的 API 调用频率限制
4. **错误处理**：前端应妥善处理 API 返回的错误信息

## 开发调试

如果遇到问题，可以：

1. 检查 `.env.local` 文件是否正确配置
2. 查看浏览器控制台的网络请求
3. 查看服务器日志输出
4. 使用备用匹配算法（当 AI 解析失败时自动启用）
