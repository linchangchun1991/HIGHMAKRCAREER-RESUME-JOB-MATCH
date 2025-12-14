#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日内推信息自动抓取脚本
功能：自动抓取牛客网、知乎等平台的最新内推信息，并保存到Excel文件
"""

import time
import re
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

class ReferralScraper:
    def __init__(self):
        """初始化爬虫"""
        self.chrome_options = Options()
        # 使用用户现有的Chrome配置，避免登录问题
        user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
        self.chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        self.chrome_options.add_argument('--profile-directory=Default')
        # 可选：无头模式（后台运行）
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        self.results = []
        
    def start_driver(self):
        """启动浏览器"""
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("浏览器启动成功！")
        
    def scrape_nowcoder(self, keywords=['内推码', '2026校招', '内推']):
        """抓取牛客网内推信息"""
        print("\n开始抓取牛客网...")
        base_url = "https://www.nowcoder.com/discuss/experience"
        
        try:
            self.driver.get(base_url)
            time.sleep(3)
            
            # 搜索内推相关帖子
            for keyword in keywords:
                try:
                    search_url = f"https://www.nowcoder.com/search?query={keyword}&type=discuss"
                    self.driver.get(search_url)
                    time.sleep(2)
                    
                    # 获取帖子列表
                    posts = self.driver.find_elements(By.CSS_SELECTOR, '.discuss-item, .feed-item')
                    
                    for post in posts[:10]:  # 只取前10条
                        try:
                            title_elem = post.find_element(By.CSS_SELECTOR, '.discuss-title, .feed-title')
                            title = title_elem.text
                            link = title_elem.get_attribute('href')
                            
                            # 检查是否包含内推码
                            if any(kw in title for kw in ['内推码', '内推', '校招']):
                                # 提取内推码
                                referral_code = self.extract_referral_code(title)
                                
                                # 获取发布时间
                                try:
                                    time_elem = post.find_element(By.CSS_SELECTOR, '.time, .post-time')
                                    post_time = time_elem.text
                                except:
                                    post_time = "未知"
                                
                                # 提取公司名称
                                company = self.extract_company_name(title)
                                
                                self.results.append({
                                    '公司名称': company,
                                    '岗位/方向': '校招',
                                    '招聘类型': '校招',
                                    '内推码/直推邮箱': referral_code,
                                    '投递链接/来源': link,
                                    '备注': f"发布时间: {post_time}",
                                    '来源平台': '牛客网',
                                    '抓取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                print(f"✓ 找到: {company} - {referral_code}")
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"搜索关键词 '{keyword}' 时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"抓取牛客网时出错: {str(e)}")
    
    def extract_referral_code(self, text):
        """从文本中提取内推码"""
        # 常见内推码格式
        patterns = [
            r'内推码[：:](\w+)',
            r'推荐码[：:](\w+)',
            r'内推[：:]\s*(\w+)',
            r'码[：:](\w+)',
            r'[A-Z0-9]{6,10}',  # 纯大写字母+数字组合
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        
        return "见原文"
    
    def extract_company_name(self, text):
        """从文本中提取公司名称"""
        companies = [
            '字节跳动', '腾讯', '阿里巴巴', '阿里', '百度', '美团', '京东', 
            '拼多多', '小米', '华为', '网易', '滴滴', '快手', 'B站', 'bilibili',
            '小红书', '蔚来', '理想', '比亚迪', '大疆', '海康威视', '科大讯飞',
            '米哈游', '莉莉丝', '完美世界', '三七互娱', '基恩士', '施耐德',
            '西门子', 'OPPO', 'vivo', 'realme', '荣耀', '联想', 'TP-LINK'
        ]
        
        for company in companies:
            if company in text:
                return company
        
        return "未知公司"
    
    def save_to_excel(self, filename='每日内推.xlsx'):
        """保存结果到Excel"""
        if not self.results:
            print("\n没有抓取到任何数据！")
            return
        
        # 去重
        df = pd.DataFrame(self.results)
        df = df.drop_duplicates(subset=['公司名称', '内推码/直推邮箱'])
        
        # 保存到桌面
        desktop_path = os.path.expanduser('~/Desktop')
        file_path = os.path.join(desktop_path, filename)
        
        # 如果文件已存在，追加数据
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            df = pd.concat([existing_df, df], ignore_index=True)
            df = df.drop_duplicates(subset=['公司名称', '内推码/直推邮箱'], keep='last')
        
        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"\n✓ 数据已保存到: {file_path}")
        print(f"✓ 共抓取 {len(df)} 条内推信息")
        
        # 打印Top 3捡漏机会
        self.print_top_opportunities(df)
    
    def print_top_opportunities(self, df):
        """打印Top 3捡漏机会"""
        print("\n" + "="*50)
        print("今日Top 3捡漏机会：")
        print("="*50)
        
        # 筛选最新的3条
        recent = df.nlargest(3, '抓取时间')
        
        for idx, row in recent.iterrows():
            print(f"\n{idx+1}. {row['公司名称']}")
            print(f"   内推码: {row['内推码/直推邮箱']}")
            print(f"   链接: {row['投递链接/来源']}")
            print(f"   备注: {row['备注']}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("\n浏览器已关闭")

def main():
    """主函数"""
    print("="*60)
    print("每日内推信息自动抓取工具")
    print("="*60)
    
    scraper = ReferralScraper()
    
    try:
        # 启动浏览器
        scraper.start_driver()
        
        # 抓取牛客网
        scraper.scrape_nowcoder()
        
        # 保存结果
        scraper.save_to_excel()
        
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
    
    finally:
        # 关闭浏览器
        scraper.close()
    
    print("\n程序执行完毕！")

if __name__ == "__main__":
    main()
