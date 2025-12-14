#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出所有岗位到Excel文件
用于查看数据库中的所有岗位
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "jobs.db"
EXCEL_FILE = f"job_hunting_results_{datetime.now().strftime('%Y%m%d')}.xlsx"

def export_all_jobs():
    """导出所有岗位到Excel"""
    try:
        print("正在导出所有岗位到Excel...")
        
        # 连接数据库
        conn = sqlite3.connect(DB_FILE)
        
        # 查询所有岗位（包含所有9个字段）
        df = pd.read_sql_query("""
            SELECT 
                company_name as '公司名称',
                company_type as '公司类型',
                work_location as '工作地点',
                recruit_type as '招聘类型',
                recruit_target as '招聘对象',
                job_title as '岗位(大都不限专业)',
                update_time as '更新时间',
                deadline as '投递截止',
                url as '相关链接'
            FROM posted_jobs 
            ORDER BY created_at DESC
        """, conn)
        
        conn.close()
        
        if df.empty:
            print("⚠ 数据库中没有岗位数据")
            return None
        
        # 保存到Excel
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        
        print(f"✓ 导出成功！")
        print(f"📁 文件: {EXCEL_FILE}")
        print(f"📊 共 {len(df)} 个岗位")
        
        return EXCEL_FILE
        
    except Exception as e:
        print(f"✗ 导出失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    export_all_jobs()

