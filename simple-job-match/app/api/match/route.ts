import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { JOBS } from '@/lib/data';

// 初始化阿里云 OpenAI 兼容客户端
const openai = new OpenAI({
  apiKey: process.env.ALI_API_KEY,
  baseURL: process.env.ALI_BASE_URL,
});

export async function POST(request: NextRequest) {
  try {
    const { resume } = await request.json();

    if (!resume || resume.trim().length === 0) {
      return NextResponse.json(
        { error: '简历内容不能为空' },
        { status: 400 }
      );
    }

    // 将岗位数据格式化为文本
    const jobsText = JOBS.map(job => 
      `岗位${job.id}: ${job.title} - ${job.company}\n薪资: ${job.salary}\n描述: ${job.description}\n`
    ).join('\n');

    // 构建 Prompt
    const prompt = `你是资深HR。这是我的简历：\n\n${resume}\n\n这是当下的岗位库：\n\n${jobsText}\n\n请从库里挑出最匹配的 1 个岗位。返回格式必须是严格的JSON格式：\n{\n  "jobName": "岗位名称",\n  "matchScore": "匹配分数(0-100)",\n  "reason": "推荐理由(50-100字)",\n  "advice": "改进建议(50-100字)"\n}`;

    // 调用阿里云 API
    const completion = await openai.chat.completions.create({
      model: 'qwen-turbo', // 使用通义千问模型
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.7,
    });

    const aiResponse = completion.choices[0]?.message?.content || '';

    // 尝试解析 JSON 响应
    let result;
    try {
      // 提取 JSON 部分（AI 可能返回带 markdown 格式的 JSON）
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        result = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('未找到有效的 JSON 格式');
      }
    } catch (parseError) {
      // 如果解析失败，返回默认格式
      result = {
        jobName: JOBS[0].title,
        matchScore: '75',
        reason: 'AI 响应解析失败，已为您推荐第一个岗位',
        advice: '请检查简历格式，确保信息完整',
      };
    }

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: '匹配失败，请稍后重试', details: error.message },
      { status: 500 }
    );
  }
}
