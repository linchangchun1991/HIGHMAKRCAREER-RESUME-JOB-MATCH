import { NextRequest, NextResponse } from "next/server"
import { callQwenTurbo } from "@/lib/qwen-client"

export const runtime = "nodejs"
export const maxDuration = 60 // 60 seconds

interface ResumeAnalysis {
  name?: string
  education?: string
  skills?: {
    hard?: string[]
    soft?: string[]
  }
  experience?: string[]
  intention?: string
  [key: string]: any
}

interface Job {
  id: string
  title: string
  company: string
  location?: string
  salary?: string
  description?: string
  requirements?: string[]
  [key: string]: any
}

interface MatchedJob extends Job {
  matchScore: number
  recommendation?: string
  gapAnalysis?: string
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { resumeAnalysis, jobs } = body as {
      resumeAnalysis: ResumeAnalysis
      jobs: Job[]
    }

    if (!resumeAnalysis) {
      return NextResponse.json(
        { error: "缺少简历分析结果" },
        { status: 400 }
      )
    }

    if (!jobs || !Array.isArray(jobs) || jobs.length === 0) {
      return NextResponse.json(
        { error: "缺少岗位列表或岗位列表为空" },
        { status: 400 }
      )
    }

    // 构建系统提示词
    const systemPrompt = `你是一个资深的职业匹配专家。请对比简历和岗位列表，为每个岗位进行严格评分（0-100分）。

评分标准：
1. 专业是否对口（30分）：教育背景与岗位要求的匹配度
2. 技能重合度（40分）：硬技能和软技能与岗位要求的匹配度
3. 项目经验相关性（20分）：项目经验与岗位职责的匹配度
4. 求职意向匹配度（10分）：求职意向与岗位的匹配度

请返回匹配度最高的3个岗位，每个岗位包含：
- matchScore: 匹配分数（0-100）
- recommendation: 推荐理由（50字以内）
- gapAnalysis: 差距分析（指出需要提升的方面，50字以内）

返回格式必须是有效的 JSON 数组：
[
  {
    "id": "岗位ID",
    "matchScore": 95,
    "recommendation": "推荐理由",
    "gapAnalysis": "差距分析"
  }
]`

    // 构建用户提示词
    const resumeSummary = `
简历信息：
- 姓名：${resumeAnalysis.name || "未提供"}
- 教育背景：${resumeAnalysis.education || "未提供"}
- 硬技能：${resumeAnalysis.skills?.hard?.join("、") || "未提供"}
- 软技能：${resumeAnalysis.skills?.soft?.join("、") || "未提供"}
- 项目经验：${resumeAnalysis.experience?.join("；") || "未提供"}
- 求职意向：${resumeAnalysis.intention || "未提供"}
`

    const jobsSummary = jobs
      .map(
        (job, index) => `
岗位 ${index + 1}：
- ID: ${job.id}
- 岗位名称：${job.title}
- 公司：${job.company}
- 岗位描述：${job.description || "未提供"}
- 岗位要求：${job.requirements?.join("、") || "未提供"}
`
      )
      .join("\n")

    const userPrompt = `${resumeSummary}\n\n岗位列表：\n${jobsSummary}\n\n请为这些岗位评分，返回匹配度最高的3个岗位。`

    // 调用 Qwen API
    const aiResponse = await callQwenTurbo(systemPrompt, userPrompt, 0.3)

    // 解析 AI 响应
    let matchedJobs: MatchedJob[]
    try {
      // 尝试提取 JSON 数组
      const jsonMatch = aiResponse.match(/\[[\s\S]*\]/)
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0])
        matchedJobs = parsed.map((item: any) => {
          // 找到对应的原始岗位信息
          const originalJob = jobs.find((j) => j.id === item.id)
          return {
            ...originalJob,
            matchScore: item.matchScore || 0,
            recommendation: item.recommendation || "",
            gapAnalysis: item.gapAnalysis || "",
          }
        })
      } else {
        throw new Error("无法解析 JSON")
      }
    } catch (parseError) {
      // 如果解析失败，使用简单的匹配算法作为备用方案
      matchedJobs = fallbackMatch(resumeAnalysis, jobs)
    }

    // 按匹配分数排序
    matchedJobs.sort((a, b) => b.matchScore - a.matchScore)

    // 只返回前3个
    matchedJobs = matchedJobs.slice(0, 3)

    return NextResponse.json({
      success: true,
      data: matchedJobs,
    })
  } catch (error) {
    console.error("岗位匹配错误:", error)
    return NextResponse.json(
      {
        error: "岗位匹配失败",
        message: error instanceof Error ? error.message : "未知错误",
      },
      { status: 500 }
    )
  }
}

// 备用匹配算法（当 AI 解析失败时使用）
function fallbackMatch(
  resumeAnalysis: ResumeAnalysis,
  jobs: Job[]
): MatchedJob[] {
  return jobs.map((job) => {
    let score = 50 // 基础分

    // 简单的关键词匹配
    const resumeText = JSON.stringify(resumeAnalysis).toLowerCase()
    const jobText = (job.description || "").toLowerCase()

    // 技能匹配
    const resumeSkills = resumeAnalysis.skills?.hard || []
    resumeSkills.forEach((skill) => {
      if (jobText.includes(skill.toLowerCase())) {
        score += 10
      }
    })

    // 经验匹配
    const resumeExp = resumeAnalysis.experience || []
    resumeExp.forEach((exp) => {
      if (jobText.includes(exp.toLowerCase().substring(0, 10))) {
        score += 5
      }
    })

    // 限制分数范围
    score = Math.min(100, Math.max(0, score))

    return {
      ...job,
      matchScore: score,
      recommendation: "基于关键词匹配的推荐",
      gapAnalysis: "建议完善相关技能和经验",
    }
  })
}
