#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时脚本：抓取当天更新的岗位
只抓取前5页，过滤当天更新的岗位
"""

import asyncio
import sys
import os
from datetime import datetime

# 导入主脚本
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aceoffer_scraper as scraper_module
from aceoffer_scraper import AceOfferRecruitScraper

# 修改抓取页数限制
scraper_module.MAX_PAGES = 20  # 最大页数上限（作为安全限制，实际会通过智能翻页提前停止）
scraper_module.ONLY_TODAY_UPDATED = True  # 启用日期过滤，只抓取今天更新的岗位
scraper_module.MAX_ITEMS_PER_PAGE = None  # 每页所有卡片
scraper_module.CONSECUTIVE_EMPTY_PAGES_THRESHOLD = 2  # 连续2页没有当天更新的岗位就停止翻页

# 不需要替换日期判断函数，直接使用原来的is_today_updated即可

async def main():
    """主函数"""
    today = datetime.now().strftime('%Y-%m-%d')
    print("="*80)
    print(f"开始抓取当天（{today}）更新的岗位")
    print(f"智能翻页：连续 {scraper_module.CONSECUTIVE_EMPTY_PAGES_THRESHOLD} 页没有当天更新的岗位将自动停止")
    print(f"最大页数上限: {scraper_module.MAX_PAGES} 页（作为安全限制）")
    print("="*80)
    
    scraper = AceOfferRecruitScraper()
    
    try:
        await scraper.run(overwrite=True)
        print("\n" + "="*80)
        print("抓取任务完成！")
        print("="*80)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())

