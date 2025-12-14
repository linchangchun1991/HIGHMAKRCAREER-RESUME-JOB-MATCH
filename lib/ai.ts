const QWEN_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation';

export async function callQwen(prompt: string, systemPrompt?: string) {
  const apiKey = process.env.QWEN_API_KEY;
  
  if (!apiKey) {
    throw new Error('QWEN_API_KEY is not configured');
  }

  const response = await fetch(QWEN_API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'qwen-max',
      input: {
        messages: [
          { role: 'system', content: systemPrompt || '你是一个专业的HR和职业规划专家' },
          { role: 'user', content: prompt }
        ]
      },
      parameters: {
        temperature: 0.7,
        max_tokens: 2000
      }
    })
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Qwen API error: ${error}`);
  }
  
  const data = await response.json();
  return data.output?.choices?.[0]?.message?.content || data.output?.text || '';
}

// 简历解析
export async function parseResume(content: string) {
  const prompt = `请分析以下简历内容，提取关键信息并以JSON格式返回：
  
简历内容：
${content}

请返回以下格式的JSON：
{
  "name": "姓名",
  "phone": "电话",
  "email": "邮箱",
  "education": "最高学历",
  "major": "专业",
  "graduationYear": "毕业年份",
  "skills": ["技能1", "技能2"],
  "experience": "工作/实习经历摘要",
  "targetPosition": "目标岗位",
  "targetCity": "目标城市"
}

只返回JSON，不要其他内容。`;

  const result = await callQwen(prompt);
  try {
    // 尝试提取JSON部分
    const jsonMatch = result.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    return JSON.parse(result);
  } catch (error) {
    console.error('Failed to parse resume:', error);
    console.error('Raw result:', result);
    return null;
  }
}

// 人岗匹配
export async function matchJobsForStudent(student: any, jobs: any[]) {
  const prompt = `作为专业HR，请分析以下学员与岗位的匹配度：

学员信息：
- 姓名：${student.name}
- 学历：${student.education}
- 专业：${student.major}
- 技能：${student.skills?.join(', ') || '无'}
- 经历：${student.experience}
- 目标岗位：${student.targetPosition}
- 目标城市：${student.targetCity}

岗位列表：
${jobs.map((job, i) => `
${i + 1}. ${job.company} - ${job.position}
   城市：${job.city}
   学历要求：${job.education}
   技能要求：${Array.isArray(job.skills) ? job.skills.join(', ') : job.skills}
   岗位描述：${job.description}
`).join('\n')}

请为每个岗位评分(0-100)，并返回JSON格式：
[
  {
    "jobId": "岗位ID",
    "score": 85,
    "dimensions": {
      "skills": 90,
      "education": 80,
      "experience": 75,
      "location": 100,
      "salary": 85
    },
    "analysis": "匹配分析说明",
    "recommendation": "推荐理由"
  }
]

按匹配分数从高到低排序，只返回JSON。`;

  const result = await callQwen(prompt);
  try {
    // 尝试提取JSON部分
    const jsonMatch = result.match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    return JSON.parse(result);
  } catch (error) {
    console.error('Failed to parse match results:', error);
    console.error('Raw result:', result);
    return [];
  }
}
