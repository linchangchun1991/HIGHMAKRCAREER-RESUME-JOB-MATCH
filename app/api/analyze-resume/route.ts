import { NextRequest, NextResponse } from "next/server"
import { parseFile } from "@/lib/file-parser"
import { callQwenTurbo } from "@/lib/qwen-client"

export const runtime = "nodejs"
export const maxDuration = 60 // 60 seconds

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json(
        { error: "未找到上传的文件" },
        { status: 400 }
      )
    }

    // 验证文件类型
    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    const allowedExtensions = [".pdf", ".doc", ".docx"]

    const isValidType =
      allowedTypes.includes(file.type) ||
      allowedExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))

    if (!isValidType) {
      return NextResponse.json(
        { error: "不支持的文件格式，请上传 PDF 或 Word 文档" },
        { status: 400 }
      )
    }

    // 解析文件内容
    const textContent = await parseFile(file)

    if (!textContent || textContent.trim().length === 0) {
      return NextResponse.json(
        { error: "文件内容为空，无法解析" },
        { status: 400 }
      )
    }

    // 调用 Qwen API 分析简历
    const systemPrompt = `你是一个资深的职业规划专家。请分析这份简历，提取以下信息并以 JSON 格式返回：
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

请确保返回的是有效的 JSON 格式，不要包含任何额外的文字说明。`

    const userPrompt = `请分析以下简历内容：\n\n${textContent}`

    const aiResponse = await callQwenTurbo(systemPrompt, userPrompt, 0.3)

    // 尝试解析 JSON 响应
    let parsedResult
    try {
      // 尝试提取 JSON 部分（AI 可能返回带说明的文本）
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        parsedResult = JSON.parse(jsonMatch[0])
      } else {
        parsedResult = JSON.parse(aiResponse)
      }
    } catch (parseError) {
      // 如果解析失败，返回原始文本和结构化数据
      parsedResult = {
        rawText: textContent,
        aiAnalysis: aiResponse,
        name: extractName(textContent),
        education: extractEducation(textContent),
        skills: {
          hard: extractHardSkills(textContent),
          soft: extractSoftSkills(textContent),
        },
        experience: extractExperience(textContent),
        intention: extractIntention(textContent),
      }
    }

    return NextResponse.json({
      success: true,
      data: parsedResult,
      rawText: textContent.substring(0, 500), // 返回前500字符用于调试
    })
  } catch (error) {
    console.error("简历分析错误:", error)
    return NextResponse.json(
      {
        error: "简历分析失败",
        message: error instanceof Error ? error.message : "未知错误",
      },
      { status: 500 }
    )
  }
}

// 辅助函数：从文本中提取基本信息（备用方案）
function extractName(text: string): string {
  const nameMatch = text.match(/(?:姓名|名字)[：:]\s*([^\n]+)/i)
  return nameMatch ? nameMatch[1].trim() : ""
}

function extractEducation(text: string): string {
  const eduMatch = text.match(/(?:教育背景|学历|毕业院校)[：:]\s*([^\n]+)/i)
  return eduMatch ? eduMatch[1].trim() : ""
}

function extractHardSkills(text: string): string[] {
  const skills: string[] = []
  const skillKeywords = [
    "JavaScript",
    "TypeScript",
    "React",
    "Vue",
    "Python",
    "Java",
    "Node.js",
    "SQL",
    "Git",
  ]
  skillKeywords.forEach((skill) => {
    if (text.includes(skill)) {
      skills.push(skill)
    }
  })
  return skills
}

function extractSoftSkills(text: string): string[] {
  const skills: string[] = []
  const skillKeywords = ["沟通", "团队协作", "项目管理", "领导力", "学习能力"]
  skillKeywords.forEach((skill) => {
    if (text.includes(skill)) {
      skills.push(skill)
    }
  })
  return skills
}

function extractExperience(text: string): string[] {
  const experiences: string[] = []
  const expMatch = text.match(/(?:项目经验|工作经历|项目经历)[：:]\s*([^\n]+)/i)
  if (expMatch) {
    experiences.push(expMatch[1].trim())
  }
  return experiences
}

function extractIntention(text: string): string {
  const intentionMatch = text.match(/(?:求职意向|期望岗位|目标职位)[：:]\s*([^\n]+)/i)
  return intentionMatch ? intentionMatch[1].trim() : ""
}
