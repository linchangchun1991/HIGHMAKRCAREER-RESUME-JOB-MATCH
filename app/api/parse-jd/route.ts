import { NextRequest, NextResponse } from "next/server"
import { callQwenTurbo } from "@/lib/qwen-client"

export const runtime = "nodejs"
export const maxDuration = 60

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { jdText } = body as { jdText: string }

    if (!jdText || jdText.trim().length === 0) {
      return NextResponse.json(
        { error: "JD 文本不能为空" },
        { status: 400 }
      )
    }

    // 构建系统提示词
    const systemPrompt = `你是一个资深的 HR 和招聘专家。请从一段招聘文本中提取以下信息，并以 JSON 格式返回：

{
  "title": "岗位名称（简洁明确，如：高级前端工程师）",
  "salary": "薪资范围（如：25K-40K，如果没有则返回"面议"）",
  "description": "岗位描述（整理后的完整描述，去除冗余信息）",
  "education": "最低学历要求（如：本科、硕士、不限等）",
  "requirements": ["要求1", "要求2", "要求3"]
}

请确保：
1. 岗位名称要简洁专业
2. 薪资范围要准确提取，如果没有明确说明则返回"面议"
3. 岗位描述要整理清晰，去除无关信息
4. 学历要求要准确识别（本科、硕士、博士、不限等）
5. requirements 数组包含主要技能要求和经验要求

返回的必须是有效的 JSON 格式，不要包含任何额外的文字说明。`

    const userPrompt = `请分析以下招聘文本：\n\n${jdText}`

    const aiResponse = await callQwenTurbo(systemPrompt, userPrompt, 0.3)

    // 解析 AI 响应
    let parsedResult
    try {
      // 尝试提取 JSON 部分
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        parsedResult = JSON.parse(jsonMatch[0])
      } else {
        parsedResult = JSON.parse(aiResponse)
      }
    } catch (parseError) {
      // 如果解析失败，使用备用方案
      parsedResult = {
        title: extractTitle(jdText),
        salary: extractSalary(jdText),
        description: jdText.substring(0, 500),
        education: extractEducation(jdText),
        requirements: extractRequirements(jdText),
      }
    }

    return NextResponse.json({
      success: true,
      data: parsedResult,
    })
  } catch (error) {
    console.error("JD 解析错误:", error)
    return NextResponse.json(
      {
        error: "JD 解析失败",
        message: error instanceof Error ? error.message : "未知错误",
      },
      { status: 500 }
    )
  }
}

// 备用提取函数
function extractTitle(text: string): string {
  const titlePatterns = [
    /招聘[：:]\s*([^\n]+)/,
    /岗位[：:]\s*([^\n]+)/,
    /职位[：:]\s*([^\n]+)/,
    /([^\n]{2,20}(?:工程师|开发|经理|专员|助理|总监))/,
  ]

  for (const pattern of titlePatterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }

  return "待定岗位"
}

function extractSalary(text: string): string {
  const salaryPatterns = [
    /(\d+[Kk万]?\s*[-~至]\s*\d+[Kk万]?)/,
    /(\d+[Kk万]\+)/,
    /薪资[：:]\s*([^\n]+)/,
    /薪酬[：:]\s*([^\n]+)/,
  ]

  for (const pattern of salaryPatterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }

  return "面议"
}

function extractEducation(text: string): string {
  const educationPatterns = [
    /(本科|硕士|博士|专科|不限)/,
    /学历[：:]\s*([^\n]+)/,
    /教育背景[：:]\s*([^\n]+)/,
  ]

  for (const pattern of educationPatterns) {
    const match = text.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }

  return "不限"
}

function extractRequirements(text: string): string[] {
  const requirements: string[] = []
  const skillKeywords = [
    "React",
    "Vue",
    "Angular",
    "TypeScript",
    "JavaScript",
    "Python",
    "Java",
    "Node.js",
    "前端",
    "后端",
    "全栈",
    "经验",
  ]

  skillKeywords.forEach((keyword) => {
    if (text.includes(keyword)) {
      requirements.push(keyword)
    }
  })

  // 提取经验要求
  const expMatch = text.match(/(\d+)\s*年/)
  if (expMatch) {
    requirements.push(`${expMatch[1]}年经验`)
  }

  return requirements.slice(0, 5) // 最多返回5个
}
