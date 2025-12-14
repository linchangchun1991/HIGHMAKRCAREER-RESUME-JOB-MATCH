import { NextRequest, NextResponse } from 'next/server';
import db, { initDatabase } from '@/lib/db';
import { v4 as uuid } from 'uuid';

export async function POST(request: NextRequest) {
  try {
    await initDatabase();
    const { jobs } = await request.json();
    
    if (!jobs || !Array.isArray(jobs)) {
      return NextResponse.json({ error: 'Invalid jobs data' }, { status: 400 });
    }

    // 批量插入数据库
    for (const job of jobs) {
      await db.execute({
        sql: `
          INSERT INTO jobs (id, company, position, city, salary_range, education, experience, skills, description, requirements, status)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        `,
        args: [
          uuid(),
          job.company,
          job.position,
          job.city,
          job.salaryRange || '',
          job.education || '',
          job.experience || '',
          JSON.stringify(job.skills || []),
          job.description || '',
          job.requirements || ''
        ]
      });
    }

    return NextResponse.json({ 
      success: true, 
      count: jobs.length 
    });
  } catch (error) {
    console.error('Batch insert error:', error);
    return NextResponse.json({ error: 'Failed to import jobs' }, { status: 500 });
  }
}
