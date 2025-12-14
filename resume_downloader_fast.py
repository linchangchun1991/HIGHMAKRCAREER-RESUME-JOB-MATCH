#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速简历下载脚本 - 优化版本
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import urllib.parse


class FastResumeDownloader:
    """快速简历下载器"""
    
    def __init__(self, download_dir=None):
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), 'resumes')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        
    def start(self):
        """启动浏览器"""
        print("="*60)
        print("快速简历下载工具")
        print("="*60)
        print(f"下载目录: {self.download_dir}\n")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=100)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        
    def login(self):
        """快速登录"""
        print("正在访问登录页面...")
        self.page.goto("https://xcx.highmarkcareer.com/console/deliveryrecord/index.html", timeout=30000)
        time.sleep(1)
        
        # 快速查找并填写登录表单
        print("正在自动登录...")
        try:
            # 查找用户名输入框
            username = self.page.query_selector('input[type="text"]')
            if username:
                username.fill("wzw")
                time.sleep(0.2)
            
            # 查找密码输入框
            password = self.page.query_selector('input[type="password"]')
            if password:
                password.fill("12345")
                time.sleep(0.2)
            
            # 点击登录按钮或按回车
            login_btn = self.page.query_selector('button[type="submit"], button:has-text("登录")')
            if login_btn:
                login_btn.click()
            elif password:
                password.press('Enter')
            
            time.sleep(2)
            print("✓ 登录完成")
        except Exception as e:
            print(f"自动登录失败: {e}，请手动登录...")
            time.sleep(5)
    
    def download_all(self):
        """快速下载所有简历"""
        print("\n开始下载...")
        
        # 等待表格加载
        time.sleep(2)
        
        # 设置每页100条
        try:
            self.page.select_option('select[name="table1_length"]', value='100')
            time.sleep(1.5)
        except:
            pass
        
        # 等待数据加载
        self.page.wait_for_function("document.querySelector('#table1 tbody tr')", timeout=10000)
        time.sleep(1)
        
        # 处理分页 - 加载所有数据
        print("正在加载所有分页数据...")
        page_count = 1
        while True:
            # 检查是否有下一页
            next_btn = self.page.query_selector('#table1_next.paginate_button:not(.disabled)')
            if not next_btn:
                break
            next_btn.click()
            time.sleep(0.8)
            page_count += 1
            if page_count % 5 == 0:
                print(f"  已加载 {page_count} 页...")
        
        print(f"✓ 共加载 {page_count} 页数据")
        time.sleep(1)
        
        # 获取所有行
        rows = self.page.query_selector_all('#table1 tbody tr')
        print(f"找到 {len(rows)} 行数据\n")
        
        if len(rows) == 0:
            print("未找到数据！")
            return
        
        # 获取表头索引
        headers = self.page.query_selector_all('#table1 thead tr th')
        resume_idx = None
        student_idx = None
        
        for i, h in enumerate(headers):
            text = h.inner_text()
            if '投递简历' in text:
                resume_idx = i
            if '名企直推投递' in text:
                student_idx = i
        
        print(f"简历列索引: {resume_idx}, 学员列索引: {student_idx}\n")
        
        # 批量下载
        downloaded = 0
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.query_selector_all('td')
                if len(cells) <= max(resume_idx or 0, student_idx or 0):
                    continue
                
                # 获取学员名称
                student_name = ""
                if student_idx is not None:
                    info = cells[student_idx].inner_text()
                    match = re.search(r'姓名[：:]\s*([^，,]+)', info)
                    student_name = match.group(1).strip() if match else info[:20]
                    student_name = re.sub(r'[<>:"/\\|?*]', '_', student_name).strip()[:50]
                
                if not student_name:
                    student_name = f"学员_{idx}"
                
                # 获取下载链接
                if resume_idx is not None:
                    link = cells[resume_idx].query_selector('a[href]')
                    if link:
                        href = link.get_attribute('href')
                        if href:
                            if not href.startswith('http'):
                                href = f"https://xcx.highmarkcareer.com{href}"
                            
                            # 获取扩展名
                            ext = os.path.splitext(href.split('?')[0])[1] or '.pdf'
                            filename = f"{student_name}{ext}"
                            filepath = self.download_dir / filename
                            
                            # 处理重名
                            counter = 1
                            while filepath.exists():
                                filepath = self.download_dir / f"{student_name}_{counter}{ext}"
                                counter += 1
                            
                            # 下载
                            print(f"[{idx}/{len(rows)}] {filename}")
                            try:
                                with self.page.expect_download(timeout=10000) as dl:
                                    link.click()
                                dl.value.save_as(filepath)
                                downloaded += 1
                                time.sleep(0.1)
                            except Exception as e:
                                print(f"  ✗ 失败: {e}")
            except Exception as e:
                print(f"  行{idx}错误: {e}")
                continue
        
        print(f"\n✓ 完成！共下载 {downloaded} 个文件")
        print(f"保存位置: {self.download_dir}")
    
    def close(self):
        """关闭"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == '__main__':
    downloader = FastResumeDownloader()
    try:
        downloader.start()
        downloader.login()
        downloader.download_all()
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        time.sleep(2)
        downloader.close()

