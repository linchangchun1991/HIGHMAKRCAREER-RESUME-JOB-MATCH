import { createClient } from '@libsql/client';

// Turso 数据库客户端
const db = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

// 初始化数据库表
export async function initDatabase() {
  await db.execute(`
    CREATE TABLE IF NOT EXISTS students (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      phone TEXT,
      email TEXT,
      education TEXT,
      major TEXT,
      graduation_year TEXT,
      skills TEXT,
      experience TEXT,
      target_position TEXT,
      target_city TEXT,
      salary_expectation TEXT,
      raw_content TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await db.execute(`
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      company TEXT NOT NULL,
      position TEXT NOT NULL,
      department TEXT,
      city TEXT,
      salary_range TEXT,
      education TEXT,
      experience TEXT,
      skills TEXT,
      description TEXT,
      requirements TEXT,
      benefits TEXT,
      status TEXT DEFAULT 'active',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await db.execute(`
    CREATE TABLE IF NOT EXISTS match_results (
      id TEXT PRIMARY KEY,
      student_id TEXT,
      job_id TEXT,
      score INTEGER,
      dimensions TEXT,
      ai_analysis TEXT,
      recommendation TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (student_id) REFERENCES students(id),
      FOREIGN KEY (job_id) REFERENCES jobs(id)
    )
  `);
}

export default db;
