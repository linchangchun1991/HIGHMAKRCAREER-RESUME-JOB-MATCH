#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：将旧表结构迁移到新表结构（9个字段）
"""

import sqlite3
import shutil
from datetime import datetime

DB_FILE = "jobs.db"
BACKUP_FILE = f"jobs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def migrate_database():
    """迁移数据库到新结构"""
    try:
        # 备份数据库
        print("正在备份数据库...")
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"✓ 备份完成: {BACKUP_FILE}")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(posted_jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 如果已经有新字段，说明已经迁移过
        if 'job_title' in columns and 'company_name' in columns:
            print("✓ 数据库已是最新结构，无需迁移")
            conn.close()
            return
        
        # 创建新表
        print("正在创建新表结构...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posted_jobs_new (
                url TEXT PRIMARY KEY,
                company_name TEXT,
                company_type TEXT,
                work_location TEXT,
                recruit_type TEXT,
                recruit_target TEXT,
                job_title TEXT NOT NULL,
                update_time TEXT,
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 迁移数据
        print("正在迁移数据...")
        cursor.execute("SELECT COUNT(*) FROM posted_jobs")
        old_count = cursor.fetchone()[0]
        
        if old_count > 0:
            # 如果有旧数据，尝试迁移
            try:
                cursor.execute('''
                    INSERT INTO posted_jobs_new (url, company_name, job_title, created_at)
                    SELECT url, 
                           COALESCE(company, '未知') as company_name,
                           COALESCE(title, '未知岗位') as job_title,
                           created_at
                    FROM posted_jobs
                ''')
                print(f"✓ 已迁移 {cursor.rowcount} 条数据")
            except Exception as e:
                print(f"⚠ 迁移数据时出错: {str(e)}")
                print("  将保留旧数据，新数据将使用新结构")
        
        # 删除旧表，重命名新表
        cursor.execute("DROP TABLE IF EXISTS posted_jobs")
        cursor.execute("ALTER TABLE posted_jobs_new RENAME TO posted_jobs")
        
        conn.commit()
        conn.close()
        
        print("✓ 数据库迁移完成！")
        print(f"  备份文件: {BACKUP_FILE}")
        
    except Exception as e:
        print(f"✗ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_database()

