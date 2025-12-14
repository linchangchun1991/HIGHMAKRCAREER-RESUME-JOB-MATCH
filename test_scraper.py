#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：立即执行一次抓取（应届生求职网）
"""

import sys
sys.path.insert(0, '/Users/changchun/Desktop')

from job_scraper_scheduler import DBManager, DingTalkSender, JobScraper, Scheduler

def test_scrape_once():
    """执行一次抓取测试"""
    print("="*60)
    print("开始测试抓取（应届生求职网）")
    print("="*60)
    
    # 初始化组件
    db_manager = DBManager()
    dingtalk_sender = DingTalkSender()
    scheduler = Scheduler(db_manager, dingtalk_sender)
    
    # 执行一次抓取
    scheduler.run_once()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == '__main__':
    test_scrape_once()

