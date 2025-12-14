import { NextRequest, NextResponse } from 'next/server';
import db, { initDatabase } from '@/lib/db';
import { v4 as uuid } from 'uuid';

// 获取所有岗位
export async function GET() {
  try {
    await initDatabase();
    const result = await db.execute({
      sql: `SELECT * FROM jobs ORDER BY created_at DESC`
    });
    
    const jobs = result.rows.map((row: any) => ({
      id: row.id,
      company: row.company,
      position: row.position,
      department: row.department,
      city: row.city,
      salary_range: row.salary_range,
      education: row.education,
      experience: row.experience,
      skills: typeof row.skills === 'string' ? JSON.parse(row.skills) : row.skills,
      description: row.description,
      requirements: row.requirements,
      benefits: row.benefits,
      status: row.status,
      created_at: row.created_at,
      updated_at: row.updated_at,
    }));

    return NextResponse.json({ success: true, jobs });
  } catch (error) {
    console.error('Get jobs error:', error);
    return NextResponse.json({ error: 'Failed to fetch jobs' }, { status: 500 });
  }
}

// 添加新岗位
export async function POST(request: NextRequest) {
  try {
    await initDatabase();
    const data = await request.json();
    const id = uuid();
    
    await db.execute({
      sql: `
        INSERT INTO jobs (id, company, position, department, city, salary_range, education, experience, skills, description, requirements, benefits, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `,
      args: [
        id,
        data.company,
        data.position,
        data.department || '',
        data.city,
        data.salaryRange || '',
        data.education || '',
        data.experience || '',
        JSON.stringify(data.skills || []),
        data.description || '',
        data.requirements || '',
        data.benefits || '',
        'active'
      ]
    });

    return NextResponse.json({ success: true, id });
  } catch (error) {
    console.error('Create job error:', error);
    return NextResponse.json({ error: 'Failed to create job' }, { status: 500 });
  }
}
