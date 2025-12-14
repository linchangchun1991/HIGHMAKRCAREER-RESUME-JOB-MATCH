#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日内推岗位自动抓取脚本 v2.0
功能：自动访问牛客网等招聘平台，抓取包含"内推码"的帖子信息，并保存到Excel文件
"""

import time
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class JobScraper:
    def __init__(self):
        """初始化爬虫配置"""
        self.chrome_options = Options()
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = None
        self.job_data = []
        
    def init_driver(self):
        """初始化浏览器驱动"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            self.driver.implicitly_wait(10)
            print("✅ Chrome浏览器启动成功")
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    def scrape_nowcoder(self):
        """抓取牛客网内推信息"""
        print("\n🔍 开始抓取牛客网...")
        try:
            # 访问牛客网讨论区 - 使用更直接的URL
            urls_to_try = [
                "https://www.nowcoder.com/search?query=内推码&type=discuss",
                "https://www.nowcoder.com/discuss/tag/2688",  # 内推标签
                "https://www.nowcoder.com/feed/main/tag/2688",
            ]
            
            for url in urls_to_try:
                print(f"  尝试访问: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                # 滚动页面加载更多内容
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                
                # 尝试多种选择器
                selectors = [
                    "a[href*='/discuss/']",
                    ".discuss-item",
                    ".feed-item",
                    "[class*='discuss']",
                    "[class*='post']",
                    ".list-item",
                ]
                
                posts = []
                for selector in selectors:
                    try:
                        posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if posts:
                            print(f"  使用选择器 '{selector}' 找到 {len(posts)} 个元素")
                            break
                    except:
                        continue
                
                if posts:
                    # 提取所有链接
                    links = set()
                    for post in posts[:30]:
                        try:
                            href = post.get_attribute('href')
                            if href and '/discuss/' in href:
                                links.add(href)
                            # 也尝试找子元素中的链接
                            inner_links = post.find_elements(By.TAG_NAME, 'a')
                            for link in inner_links:
                                href = link.get_attribute('href')
                                if href and '/discuss/' in href:
                                    links.add(href)
                        except:
                            continue
                    
                    print(f"  提取到 {len(links)} 个讨论帖链接")
                    
                    # 访问每个帖子
                    for idx, link in enumerate(list(links)[:15], 1):
                        try:
                            self._process_nowcoder_post(link, idx)
                        except Exception as e:
                            print(f"  ⚠️ 处理帖子出错: {e}")
                            continue
                    
                    if self.job_data:
                        break
            
            print(f"✅ 牛客网抓取完成，共获取 {len(self.job_data)} 条有效内推信息")
            
        except Exception as e:
            print(f"❌ 牛客网抓取失败: {e}")
    
    def _process_nowcoder_post(self, link, idx):
        """处理单个牛客帖子"""
        self.driver.execute_script("window.open(arguments[0]);", link)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(2)
        
        try:
            # 获取页面文本
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # 获取标题
            title = ""
            title_selectors = ['h1', '.title', '[class*="title"]', '.post-title']
            for sel in title_selectors:
                try:
                    title = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if title:
                        break
                except:
                    continue
            
            # 检查是否包含内推相关关键词
            keywords = ['内推', '推荐码', '邀请码', '直推', '内部推荐']
            if any(kw in page_text for kw in keywords):
                job_info = self._parse_job_info(title, page_text, link)
                if job_info:
                    self.job_data.append(job_info)
                    print(f"  ✅ [{idx}] {job_info['公司名称']} - {job_info['岗位/方向']}")
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
    
    def scrape_juejin(self):
        """抓取稀土掘金内推信息"""
        print("\n🔍 开始抓取稀土掘金...")
        try:
            url = "https://juejin.cn/search?query=内推码&type=0"
            self.driver.get(url)
            time.sleep(3)
            
            # 滚动加载
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # 查找文章链接
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/post/']")
            links = set()
            for article in articles:
                href = article.get_attribute('href')
                if href and '/post/' in href:
                    links.add(href)
            
            print(f"  找到 {len(links)} 篇相关文章")
            
            for idx, link in enumerate(list(links)[:10], 1):
                try:
                    self.driver.execute_script("window.open(arguments[0]);", link)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(2)
                    
                    title = ""
                    try:
                        title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
                    except:
                        pass
                    
                    content = self.driver.find_element(By.TAG_NAME, 'body').text
                    
                    if '内推' in content or '推荐码' in content:
                        job_info = self._parse_job_info(title, content, link)
                        if job_info:
                            self.job_data.append(job_info)
                            print(f"  ✅ [{idx}] {job_info['公司名称']} - {job_info['岗位/方向']}")
                    
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                except Exception as e:
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    continue
            
            print(f"✅ 稀土掘金抓取完成")
            
        except Exception as e:
            print(f"❌ 稀土掘金抓取失败: {e}")
    
    def _parse_job_info(self, title, content, link):
        """解析帖子内容，提取结构化信息"""
        full_text = title + " " + content
        
        # 提取公司名称
        companies = {
            '字节': '字节跳动', '抖音': '字节跳动', 'ByteDance': '字节跳动',
            '腾讯': '腾讯', 'Tencent': '腾讯', '微信': '腾讯',
            '阿里': '阿里巴巴', 'Alibaba': '阿里巴巴', '淘宝': '阿里巴巴', '蚂蚁': '蚂蚁集团',
            '百度': '百度', 'Baidu': '百度',
            '美团': '美团', '京东': '京东', 'JD': '京东',
            '网易': '网易', '华为': '华为', 'Huawei': '华为',
            '小米': '小米', 'Xiaomi': '小米',
            '拼多多': '拼多多', '快手': '快手', '滴滴': '滴滴',
            '小红书': '小红书', 'B站': 'bilibili', '哔哩哔哩': 'bilibili',
            '携程': '携程', '去哪儿': '去哪儿', '饿了么': '饿了么',
            '微软': '微软', 'Microsoft': '微软', 'Google': '谷歌', '谷歌': '谷歌',
            'Apple': '苹果', '苹果': '苹果', 'Amazon': '亚马逊', '亚马逊': '亚马逊',
            'OPPO': 'OPPO', 'vivo': 'vivo', '荣耀': '荣耀',
            '招银': '招银网络', '平安': '平安科技', '中信': '中信银行',
        }
        company = "其他公司"
        for key, value in companies.items():
            if key in full_text:
                company = value
                break
        
        # 提取岗位方向
        positions = {
            '前端': '前端开发', 'Frontend': '前端开发', 'Web': '前端开发',
            '后端': '后端开发', 'Backend': '后端开发', '服务端': '后端开发',
            'Java': 'Java开发', 'Python': 'Python开发', 'Go': 'Go开发', 'Golang': 'Go开发',
            'C++': 'C++开发', 'C#': 'C#开发',
            '算法': '算法工程师', 'AI': 'AI算法', '机器学习': '机器学习', '深度学习': '深度学习',
            '数据': '数据开发', '大数据': '大数据开发', '数据分析': '数据分析',
            '测试': '测试开发', 'QA': '测试开发', '测开': '测试开发',
            '产品': '产品经理', 'PM': '产品经理',
            '运营': '运营', '市场': '市场营销',
            'Android': 'Android开发', 'iOS': 'iOS开发', '客户端': '客户端开发',
            '运维': '运维工程师', 'DevOps': 'DevOps', 'SRE': 'SRE',
            '安全': '安全工程师',
        }
        position = "综合岗位"
        for key, value in positions.items():
            if key in full_text:
                position = value
                break
        
        # 提取招聘类型
        if '实习' in full_text:
            job_type = '实习'
        elif any(kw in full_text for kw in ['校招', '2025', '2026', '应届', '毕业']):
            job_type = '校招'
        elif '社招' in full_text:
            job_type = '社招'
        else:
            job_type = '校招/社招'
        
        # 提取内推码
        referral_code = ""
        code_patterns = [
            r'内推码[：:\s]*([A-Za-z0-9]{4,20})',
            r'推荐码[：:\s]*([A-Za-z0-9]{4,20})',
            r'邀请码[：:\s]*([A-Za-z0-9]{4,20})',
            r'[Cc]ode[：:\s]*([A-Za-z0-9]{4,20})',
            r'码[：:\s]*([A-Za-z0-9]{6,20})',
        ]
        for pattern in code_patterns:
            match = re.search(pattern, full_text)
            if match:
                referral_code = match.group(1)
                break
        
        # 提取邮箱
        email = ""
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text)
        if email_match:
            email = email_match.group(0)
        
        # 提取投递链接
        apply_link = ""
        link_patterns = [
            r'(https?://[^\s]*(?:job|career|recruit|campus|zhaopin)[^\s]*)',
        ]
        for pattern in link_patterns:
            match = re.search(pattern, full_text)
            if match:
                apply_link = match.group(1)
                break
        
        # 提取截止时间
        deadline = ""
        deadline_patterns = [
            r'截止[：:到至]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            r'(\d{1,2}月\d{1,2}日?)\s*截止',
            r'deadline[：:\s]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                deadline = match.group(1)
                break
        
        # 组合内推方式
        referral_method = referral_code or email or "详见原帖"
        
        # 只有包含实质内推信息才返回
        if referral_code or email or '内推' in title:
            return {
                '公司名称': company,
                '岗位/方向': position,
                '招聘类型': job_type,
                '内推码/直推邮箱': referral_method,
                '投递链接/来源': apply_link if apply_link else link,
                '备注': deadline if deadline else '详见原帖'
            }
        return None
    
    def save_to_excel(self, output_path):
        """保存数据到Excel文件"""
        if not self.job_data:
            print("\n⚠️ 没有抓取到有效数据，将创建示例模板...")
            # 创建示例数据
            self.job_data = [
                {
                    '公司名称': '示例-字节跳动',
                    '岗位/方向': '后端开发',
                    '招聘类型': '校招',
                    '内推码/直推邮箱': 'ABCD1234',
                    '投递链接/来源': 'https://jobs.bytedance.com',
                    '备注': '这是示例数据，请手动更新'
                }
            ]
        
        try:
            df = pd.DataFrame(self.job_data)
            
            # 去重
            df = df.drop_duplicates(subset=['公司名称', '岗位/方向', '内推码/直推邮箱'])
            
            df.to_excel(output_path, index=False, engine='openpyxl')
            print(f"\n✅ 数据已保存到: {output_path}")
            print(f"📊 共保存 {len(df)} 条内推信息")
            
            # 输出Top 3捡漏机会
            print("\n" + "="*50)
            print("🔥 今日Top 3捡漏机会：")
            print("="*50)
            for i, (_, job) in enumerate(df.head(3).iterrows(), 1):
                print(f"\n{i}. 【{job['公司名称']}】{job['岗位/方向']} ({job['招聘类型']})")
                print(f"   📝 内推方式: {job['内推码/直推邮箱']}")
                print(f"   🔗 链接: {job['投递链接/来源']}")
                if job['备注'] != '详见原帖':
                    print(f"   ⏰ 截止: {job['备注']}")
        
        except Exception as e:
            print(f"❌ 保存Excel失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 浏览器已关闭")

def main():
    """主函数"""
    print("="*60)
    print("🤖 海马职加 - 每日内推岗位自动抓取系统 v2.0")
    print(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 设置输出路径为桌面
    desktop_path = Path.home() / "Desktop" / "每日内推.xlsx"
    
    scraper = JobScraper()
    
    try:
        scraper.init_driver()
        
        # 抓取多个平台
        scraper.scrape_nowcoder()
        scraper.scrape_juejin()
        
        # 保存到Excel
        scraper.save_to_excel(desktop_path)
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
    finally:
        scraper.close()
    
    print("\n" + "="*60)
    print("✅ 任务执行完毕！")
    print("="*60)

if __name__ == "__main__":
    main()
