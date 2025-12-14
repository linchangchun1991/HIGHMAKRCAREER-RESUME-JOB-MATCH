import { NextRequest, NextResponse } from 'next/server';
import { parseResume, matchJobsForStudent } from '@/lib/ai';
import db, { initDatabase } from '@/lib/db';
import { v4 as uuid } from 'uuid';

export async function POST(request: NextRequest) {
  try {
    await initDatabase();
    
    const { content } = await request.json();
    
    if (!content) {
      return NextResponse.json({ error: 'No content provided' }, { status: 400 });
    }

    // 使用 AI 解析简历
    const parsed = await parseResume(content);
    
    if (!parsed) {
      return NextResponse.json({ error: 'Failed to parse resume' }, { status: 500 });
    }

    // 保存学员信息到数据库
    const studentId = uuid();
    await db.execute({
      sql: `INSERT INTO students (id, name, phone, email, education, major, graduation_year, skills, experience, target_position, target_city, raw_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        studentId,
        parsed.name || '',
        parsed.phone || '',
        parsed.email || '',
        parsed.education || '',
        parsed.major || '',
        parsed.graduationYear || '',
        JSON.stringify(parsed.skills || []),
        parsed.experience || '',
        parsed.targetPosition || '',
        parsed.targetCity || '',
        content
      ]
    });

    // 获取所有活跃岗位
    const jobsResult = await db.execute(`SELECT * FROM jobs WHERE status = 'active'`);
    const jobs = jobsResult.rows as any[];
    
    let matches = [];
    if (jobs.length > 0) {
      // 格式化岗位数据用于 AI 匹配
      const jobsData = jobs.map((row: any) => ({
        id: row.id as string,
        company: row.company as string,
        position: row.position as string,
        city: row.city as string,
        education: row.education as string,
        skills: typeof row.skills === 'string' ? JSON.parse(row.skills || '[]') : (row.skills || []),
        description: row.description as string,
      }));
      
      // AI 匹配岗位
      matches = await matchJobsForStudent(parsed, jobsData);
      
      // 保存匹配结果
      for (const match of matches) {
        await db.execute({
          sql: `INSERT INTO match_results (id, student_id, job_id, score, dimensions, ai_analysis, recommendation)
                VALUES (?, ?, ?, ?, ?, ?, ?)`,
          args: [
            uuid(),
            studentId,
            match.jobId,
            match.score,
            JSON.stringify(match.dimensions),
            match.analysis || '',
            match.recommendation || ''
          ]
        });
      }
    }

    // 格式化返回数据，包含岗位信息
    const formattedMatches = matches.map((match: any) => {
      const job = jobs.find((j: any) => j.id === match.jobId);
      return {
        ...match,
        company: job?.company || '',
        position: job?.position || '',
        city: job?.city || '',
      };
    });

    return NextResponse.json({ 
      success: true, 
      parsed,
      studentId,
      matches: formattedMatches
    });
  } catch (error: any) {
    console.error('Parse error:', error);
    return NextResponse.json({ error: error.message || 'Parse failed' }, { status: 500 });
  }
}
