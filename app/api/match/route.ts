import { NextRequest, NextResponse } from 'next/server';
import db, { initDatabase } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    await initDatabase();
    const { searchParams } = new URL(request.url);
    const studentId = searchParams.get('studentId');

    let query = `
      SELECT 
        mr.*,
        s.name as student_name,
        j.company,
        j.position,
        j.city,
        j.salary_range
      FROM match_results mr
      JOIN students s ON mr.student_id = s.id
      JOIN jobs j ON mr.job_id = j.id
    `;

    let result;
    if (studentId) {
      query += ` WHERE mr.student_id = ? ORDER BY mr.score DESC`;
      result = await db.execute({
        sql: query,
        args: [studentId]
      });
    } else {
      query += ` ORDER BY mr.score DESC`;
      result = await db.execute({
        sql: query
      });
    }

    // 解析 JSON 字段
    const formattedResults = result.rows.map((row: any) => ({
      id: row.id,
      student_id: row.student_id,
      job_id: row.job_id,
      score: row.score,
      dimensions: typeof row.dimensions === 'string' 
        ? JSON.parse(row.dimensions) 
        : row.dimensions,
      ai_analysis: row.ai_analysis,
      recommendation: row.recommendation,
      created_at: row.created_at,
      student_name: row.student_name,
      company: row.company,
      position: row.position,
      city: row.city,
      salary_range: row.salary_range,
    }));

    return NextResponse.json({ success: true, results: formattedResults });
  } catch (error) {
    console.error('Get matches error:', error);
    return NextResponse.json({ error: 'Failed to fetch matches' }, { status: 500 });
  }
}
