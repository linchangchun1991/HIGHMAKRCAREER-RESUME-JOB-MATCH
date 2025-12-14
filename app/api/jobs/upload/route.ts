import { NextRequest, NextResponse } from 'next/server';
import * as XLSX from 'xlsx';
import db, { initDatabase } from '@/lib/db';
import { v4 as uuid } from 'uuid';

export async function POST(request: NextRequest) {
  try {
    await initDatabase();
    
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const workbook = XLSX.read(bytes, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet);

    const jobs = data.map((row: any) => ({
      id: uuid(),
      company: row['公司名称'] || row['company'] || row['Company'] || '',
      position: row['岗位名称'] || row['position'] || row['Position'] || '',
      city: row['工作城市'] || row['city'] || row['City'] || '',
      salaryRange: row['薪资范围'] || row['salary'] || row['Salary'] || row['salaryRange'] || '',
      education: row['学历要求'] || row['education'] || row['Education'] || '',
      experience: row['经验要求'] || row['experience'] || row['Experience'] || '',
      skills: (row['技能要求'] || row['skills'] || row['Skills'] || '').toString().split(/[,，]/).map((s: string) => s.trim()).filter(Boolean),
      description: row['岗位描述'] || row['description'] || row['Description'] || '',
      requirements: row['任职要求'] || row['requirements'] || row['Requirements'] || '',
    }));

    // 批量插入数据库
    for (const job of jobs) {
      await db.execute({
        sql: `INSERT INTO jobs (id, company, position, city, salary_range, education, experience, skills, description, requirements, status)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')`,
        args: [
          job.id,
          job.company,
          job.position,
          job.city,
          job.salaryRange,
          job.education,
          job.experience,
          JSON.stringify(job.skills),
          job.description,
          job.requirements
        ]
      });
    }

    return NextResponse.json({ 
      success: true, 
      jobs,
      count: jobs.length 
    });
  } catch (error: any) {
    console.error('Upload error:', error);
    return NextResponse.json({ error: error.message || 'Upload failed' }, { status: 500 });
  }
}
