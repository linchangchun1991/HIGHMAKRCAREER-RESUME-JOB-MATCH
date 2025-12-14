#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AceOffer 招聘信息定时抓取脚本
功能：每天早上9点和晚上5点自动抓取当天更新的招聘信息，并覆盖更新到Excel文件

安装依赖：
    pip install playwright pandas openpyxl schedule

安装Playwright浏览器：
    playwright install chromium

使用方法：
    python aceoffer_recruit_scheduler.py
"""

import asyncio
import schedule
import time
from datetime import datetime
import sys
import os

# 导入主抓取脚本
import aceoffer_recruit_scraper as scraper_module
from aceoffer_recruit_scraper import AceOfferRecruitScraper

# ==================== 配置区域 ====================

# 定时任务时间（24小时制）
MORNING_TIME = "08:00"  # 早上8点
EVENING_TIME = "18:00"  # 晚上6点

# ==================== 定时任务函数 ====================

async def run_daily_scrape():
    """执行每日抓取任务"""
    print("\n" + "="*80)
    print(f"开始执行定时抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # 启用日期过滤（只抓取今天更新的岗位）
        scraper_module.ONLY_TODAY_UPDATED = True
        # 设置抓取页数（确保能找到所有今天更新的岗位）
        scraper_module.MAX_PAGES = 20  # 抓取前20页，确保覆盖所有可能
        
        # 创建爬虫实例
        scraper = AceOfferRecruitScraper()
        
        # 运行抓取（覆盖更新模式，只抓取今天更新的岗位，覆盖原文件）
        await scraper.run(overwrite=True)
        
        print("\n" + "="*80)
        print(f"定时抓取任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n⚠ 定时抓取任务出错: {str(e)}")
        import traceback
        traceback.print_exc()

def scheduled_job():
    """定时任务包装函数（同步）"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 触发定时任务...")
    asyncio.run(run_daily_scrape())

# ==================== 主程序 ====================

def main():
    """主函数"""
    print("="*80)
    print("AceOffer 招聘信息定时抓取服务")
    print("="*80)
    print(f"\n启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n定时任务配置:")
    print(f"  - 每天早上 {MORNING_TIME} 执行")
    print(f"  - 每天晚上 {EVENING_TIME} 执行")
    print(f"  - 只抓取当天更新的岗位")
    print(f"  - 覆盖更新到文件: {scraper_module.EXCEL_FILE_PATH}")
    print("\n" + "="*80)
    print("服务运行中，按 Ctrl+C 停止...")
    print("="*80 + "\n")
    
    # 设置定时任务
    schedule.every().day.at(MORNING_TIME).do(scheduled_job)
    schedule.every().day.at(EVENING_TIME).do(scheduled_job)
    
    # 检查是否立即执行一次（如果当前时间接近定时时间）
    current_time = datetime.now().strftime('%H:%M')
    if current_time >= MORNING_TIME or current_time >= EVENING_TIME:
        print(f"当前时间 {current_time}，立即执行一次抓取任务...")
        scheduled_job()
    
    # 持续运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("收到停止信号，正在退出...")
        print("="*80)
        sys.exit(0)

if __name__ == "__main__":
    main()

