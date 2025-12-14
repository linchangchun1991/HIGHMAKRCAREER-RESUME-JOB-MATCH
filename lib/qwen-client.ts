import OpenAI from "openai"

/**
 * 创建阿里云通义千问客户端
 * 使用 OpenAI SDK 兼容模式
 */
export function createQwenClient() {
  const apiKey = process.env.ALIBABA_CLOUD_API_KEY

  if (!apiKey) {
    throw new Error("ALIBABA_CLOUD_API_KEY 环境变量未设置")
  }

  // 阿里云通义千问的兼容端点
  const baseURL = process.env.ALIBABA_CLOUD_API_ENDPOINT || 
    "https://dashscope.aliyuncs.com/compatible-mode/v1"

  return new OpenAI({
    apiKey,
    baseURL,
  })
}

/**
 * 调用 Qwen-Turbo 模型
 */
export async function callQwenTurbo(
  systemPrompt: string,
  userPrompt: string,
  temperature: number = 0.7
): Promise<string> {
  const client = createQwenClient()

  try {
    const response = await client.chat.completions.create({
      model: "qwen-turbo",
      messages: [
        {
          role: "system",
          content: systemPrompt,
        },
        {
          role: "user",
          content: userPrompt,
        },
      ],
      temperature,
    })

    const content = response.choices[0]?.message?.content

    if (!content) {
      throw new Error("API 返回空内容")
    }

    return content
  } catch (error) {
    console.error("Qwen API 调用失败:", error)
    throw new Error(
      `API 调用失败: ${error instanceof Error ? error.message : "未知错误"}`
    )
  }
}
