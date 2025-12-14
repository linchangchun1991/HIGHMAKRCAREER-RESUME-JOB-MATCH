#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历批量下载脚本 - 最终版本
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


class ResumeDownloader:
    def __init__(self):
        self.download_dir = Path(__file__).parent / 'resumes'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start(self):
        print("="*60)
        print("简历批量下载工具")
        print("="*60)
        print(f"下载目录: {self.download_dir}\n")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=100)
        self.page = self.browser.new_page(accept_downloads=True)
        
    def login(self):
        print("正在登录...")
        self.page.goto("https://xcx.highmarkcareer.com/console/deliveryrecord/index.html", timeout=30000)
        time.sleep(2)
        
        # 自动登录
        try:
            username = self.page.query_selector('input[type="text"]')
            if username:
                username.fill("wzw")
                time.sleep(0.3)
            
            password = self.page.query_selector('input[type="password"]')
            if password:
                password.fill("12345")
                time.sleep(0.3)
            
            login_btn = self.page.query_selector('button[type="submit"], button:has-text("登录")')
            if login_btn:
                login_btn.click()
            elif password:
                password.press('Enter')
            
            time.sleep(3)
            print("✓ 登录完成\n")
        except Exception as e:
            print(f"自动登录失败: {e}")
            print("请手动登录，等待5秒...")
            time.sleep(5)
    
    def get_filename(self, info_text):
        """根据信息构建文件名：姓名_城市_岗位"""
        name_match = re.search(r'姓名[：:]\s*([^，,]+)', info_text)
        name = name_match.group(1).strip() if name_match else ""
        
        city_match = re.search(r'期望城市[：:]\s*([^，,；;]+)', info_text)
        city = city_match.group(1).strip() if city_match else ""
        if '、' in city or ' ' in city:
            city = city.split('、')[0].split()[0].strip()
        
        job_match = re.search(r'投递岗位[：:]\s*([^，,；;]+)', info_text)
        job = job_match.group(1).strip() if job_match else ""
        job = re.sub(r'[/\\|；;]', '_', job).strip()
        if len(job) > 20:
            job = job[:20]
        
        parts = []
        if name:
            parts.append(name)
        if city and city != name:
            parts.append(city)
        if job and job != name and job != city:
            parts.append(job)
        
        if parts:
            filename = '_'.join(parts)
        else:
            filename = "未知学员"
        
        # 清理非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
        filename = re.sub(r'[，,、\s]+', '_', filename)
        filename = re.sub(r'_+', '_', filename).strip('_')
        if len(filename) > 80:
            filename = filename[:80]
        
        return filename
    
    def download_all(self):
        print("正在收集数据...")
        
        # 等待表格加载
        time.sleep(3)
        
        # 设置每页100条
        try:
            self.page.select_option('select[name="table1_length"]', value='100')
            time.sleep(2)
        except:
            pass
        
        # 等待数据加载
        print("等待表格数据加载...")
        max_wait = 30
        for i in range(max_wait):
            rows = self.page.query_selector_all('#table1 tbody tr')
            if len(rows) > 0:
                print(f"✓ 数据已加载，找到 {len(rows)} 行")
                break
            time.sleep(1)
            if (i + 1) % 5 == 0:
                print(f"  等待中... ({i+1}秒)")
        else:
            print("⚠ 等待超时，继续执行...")
        
        time.sleep(2)
        
        # 设置每页100条（如果还没设置）
        try:
            current_length = self.page.query_selector('select[name="table1_length"]')
            if current_length:
                self.page.select_option('select[name="table1_length"]', value='100')
                time.sleep(3)  # 等待数据重新加载
        except:
            pass
        
        # 加载所有分页
        print("正在加载所有分页...")
        page_count = 1
        max_pages = 50
        while page_count <= max_pages:
            # 先获取当前页的行数
            rows = self.page.query_selector_all('#table1 tbody tr')
            
            # 检查是否有下一页
            next_btn = self.page.query_selector('#table1_next.paginate_button:not(.disabled)')
            if not next_btn:
                break
            
            next_btn.click()
            time.sleep(1.5)
            page_count += 1
            if page_count % 10 == 0:
                print(f"  已加载 {page_count} 页...")
        
        print(f"✓ 共加载 {page_count} 页\n")
        time.sleep(2)
        
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
        
        print(f"简历列: {resume_idx}, 学员列: {student_idx}\n")
        
        # 开始下载
        print("="*60)
        print("开始下载简历...")
        print("="*60)
        
        downloaded = 0
        failed = 0
        
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.query_selector_all('td')
                if len(cells) <= max(resume_idx or 0, student_idx or 0):
                    continue
                
                # 获取学员信息
                info_text = ""
                if student_idx is not None and student_idx < len(cells):
                    info_text = cells[student_idx].inner_text()
                
                # 获取下载链接
                link = None
                if resume_idx is not None and resume_idx < len(cells):
                    link = cells[resume_idx].query_selector('a[href]')
                
                if not link:
                    continue
                
                href = link.get_attribute('href')
                if not href:
                    continue
                
                if not href.startswith('http'):
                    href = f"https://xcx.highmarkcareer.com{href}"
                
                # 构建文件名
                filename = self.get_filename(info_text)
                ext = os.path.splitext(href.split('?')[0])[1] or '.pdf'
                full_filename = f"{filename}{ext}"
                filepath = self.download_dir / full_filename
                
                # 处理重名
                counter = 1
                while filepath.exists():
                    full_filename = f"{filename}_{counter}{ext}"
                    filepath = self.download_dir / full_filename
                    counter += 1
                
                # 下载
                print(f"[{idx}/{len(rows)}] {full_filename}")
                try:
                    with self.page.expect_download(timeout=15000) as dl:
                        link.click()
                    dl.value.save_as(filepath)
                    downloaded += 1
                    time.sleep(0.2)
                except Exception as e:
                    print(f"  ✗ 失败: {e}")
                    failed += 1
                    
            except Exception as e:
                print(f"  行{idx}错误: {e}")
                failed += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"下载完成！")
        print(f"成功: {downloaded} 个")
        print(f"失败: {failed} 个")
        print(f"保存位置: {self.download_dir}")
        print(f"{'='*60}")
    
    def close(self):
        time.sleep(2)
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == '__main__':
    downloader = ResumeDownloader()
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
        downloader.close()

