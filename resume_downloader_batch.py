#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量简历下载脚本 - 优化版本
1. 一次登录
2. 批量下载所有简历（临时文件名）
3. 批量重命名
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import urllib.parse


class BatchResumeDownloader:
    """批量简历下载器"""
    
    def __init__(self, download_dir=None):
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), 'resumes')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.download_dir / 'temp'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        
        # 存储下载信息：{临时文件名: (学员名称, 原始链接)}
        self.download_info = {}
        
    def start(self):
        """启动浏览器"""
        print("="*60)
        print("批量简历下载工具")
        print("="*60)
        print(f"下载目录: {self.download_dir}\n")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=50)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        
    def login_once(self):
        """一次性登录"""
        print("正在访问登录页面...")
        self.page.goto("https://xcx.highmarkcareer.com/console/deliveryrecord/index.html", timeout=30000)
        time.sleep(1)
        
        print("正在自动登录...")
        try:
            # 查找并填写登录表单
            username = self.page.query_selector('input[type="text"]')
            if username:
                username.fill("wzw")
                time.sleep(0.2)
            
            password = self.page.query_selector('input[type="password"]')
            if password:
                password.fill("12345")
                time.sleep(0.2)
            
            # 点击登录
            login_btn = self.page.query_selector('button[type="submit"], button:has-text("登录")')
            if login_btn:
                login_btn.click()
            elif password:
                password.press('Enter')
            
            # 等待登录完成
            time.sleep(2)
            self.page.wait_for_function("document.querySelector('#table1')", timeout=10000)
            print("✓ 登录成功！\n")
        except Exception as e:
            print(f"自动登录失败: {e}")
            print("请手动登录，然后按回车继续...")
            input()
    
    def collect_all_data(self):
        """收集所有数据：学员名称和下载链接"""
        print("正在收集所有数据...")
        
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
            next_btn = self.page.query_selector('#table1_next.paginate_button:not(.disabled)')
            if not next_btn:
                break
            next_btn.click()
            time.sleep(0.6)
            page_count += 1
            if page_count % 10 == 0:
                print(f"  已加载 {page_count} 页...")
        
        print(f"✓ 共加载 {page_count} 页数据")
        time.sleep(1)
        
        # 获取所有行
        rows = self.page.query_selector_all('#table1 tbody tr')
        print(f"找到 {len(rows)} 行数据\n")
        
        if len(rows) == 0:
            print("未找到数据！")
            return []
        
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
        
        # 收集所有数据
        data_list = []
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.query_selector_all('td')
                if len(cells) <= max(resume_idx or 0, student_idx or 0):
                    continue
                
                # 获取学员信息并构建文件名
                student_name = ""
                if student_idx is not None and student_idx < len(cells):
                    info = cells[student_idx].inner_text()
                    
                    # 提取姓名
                    name_match = re.search(r'姓名[：:]\s*([^，,]+)', info)
                    name = name_match.group(1).strip() if name_match else ""
                    
                    # 提取岗位（用于区分同名学员）
                    job_match = re.search(r'投递岗位[：:]\s*([^，,]+)', info)
                    job = job_match.group(1).strip() if job_match else ""
                    
                    # 提取城市（用于区分同名学员）
                    city_match = re.search(r'期望城市[：:]\s*([^，,]+)', info)
                    city = city_match.group(1).strip() if city_match else ""
                    
                    # 构建文件名：姓名_城市_岗位（更精确的区分同名学员）
                    parts = []
                    if name:
                        parts.append(name)
                    if city and city != name:  # 避免重复
                        # 只取第一个城市（如果有多个）
                        city_clean = city.split('、')[0].split()[0].strip() if '、' in city or ' ' in city else city
                        parts.append(city_clean)
                    if job and job != name and job != city:  # 避免重复
                        # 清理岗位名称中的特殊字符，截取前20个字符
                        job_clean = re.sub(r'[/\\|；;]', '_', job).strip()
                        job_short = job_clean[:20] if len(job_clean) > 20 else job_clean
                        parts.append(job_short)
                    
                    if parts:
                        student_name = '_'.join(parts)
                    else:
                        student_name = f"学员_{idx}"
                    
                    # 清理非法字符
                    student_name = re.sub(r'[<>:"/\\|?*]', '_', student_name).strip()
                    # 移除多余空格和标点
                    student_name = re.sub(r'[，,、\s]+', '_', student_name)
                    student_name = re.sub(r'_+', '_', student_name).strip('_')
                    # 限制长度但保留关键信息
                    if len(student_name) > 80:
                        # 优先保留姓名和城市
                        if len(name) + len(city) + 3 < 80:
                            student_name = f"{name}_{city}_{job[:80-len(name)-len(city)-5]}"
                        else:
                            student_name = student_name[:80]
                
                if not student_name:
                    # 如果还是找不到，使用ID
                    try:
                        id_cell = cells[0] if cells else None
                        if id_cell:
                            row_id = id_cell.inner_text().strip()
                            student_name = f"学员_{row_id}"
                    except:
                        student_name = f"学员_{idx}"
                
                # 获取下载链接
                download_link = None
                if resume_idx is not None and resume_idx < len(cells):
                    link = cells[resume_idx].query_selector('a[href]')
                    if link:
                        href = link.get_attribute('href')
                        if href:
                            if not href.startswith('http'):
                                href = f"https://xcx.highmarkcareer.com{href}"
                            download_link = (link, href)
                
                if download_link:
                    data_list.append((idx, student_name, download_link))
                    
            except Exception as e:
                print(f"  行{idx}收集错误: {e}")
                continue
        
        print(f"✓ 收集到 {len(data_list)} 个有效数据\n")
        return data_list
    
    def batch_download(self, data_list):
        """批量下载所有简历（使用临时文件名）"""
        print("="*60)
        print("开始批量下载...")
        print("="*60)
        
        downloaded = 0
        failed = 0
        
        for idx, (row_idx, student_name, (link, href)) in enumerate(data_list, 1):
            try:
                # 获取文件扩展名
                ext = os.path.splitext(href.split('?')[0])[1] or '.pdf'
                temp_filename = f"temp_{row_idx:04d}{ext}"
                temp_filepath = self.temp_dir / temp_filename
                
                # 存储重命名信息
                self.download_info[temp_filename] = (student_name, ext, row_idx)
                
                # 下载
                print(f"[{idx}/{len(data_list)}] 下载中... {student_name}")
                try:
                    with self.page.expect_download(timeout=10000) as dl:
                        link.click()
                    dl.value.save_as(temp_filepath)
                    downloaded += 1
                    time.sleep(0.05)  # 最小延迟
                except Exception as e:
                    print(f"  ✗ 下载失败: {e}")
                    failed += 1
                    if temp_filename in self.download_info:
                        del self.download_info[temp_filename]
                    
            except Exception as e:
                print(f"  处理失败: {e}")
                failed += 1
        
        print(f"\n✓ 下载完成！成功: {downloaded}, 失败: {failed}\n")
        return downloaded
    
    def batch_rename(self):
        """批量重命名所有文件"""
        print("="*60)
        print("开始批量重命名...")
        print("="*60)
        
        renamed = 0
        skipped = 0
        
        for temp_filename, (student_name, ext, row_idx) in self.download_info.items():
            temp_path = self.temp_dir / temp_filename
            if not temp_path.exists():
                skipped += 1
                continue
            
            # 构建新文件名
            new_filename = f"{student_name}{ext}"
            new_filepath = self.download_dir / new_filename
            
            # 处理重名
            counter = 1
            while new_filepath.exists():
                new_filename = f"{student_name}_{counter}{ext}"
                new_filepath = self.download_dir / new_filename
                counter += 1
            
            # 重命名
            try:
                temp_path.rename(new_filepath)
                print(f"  ✓ {temp_filename} -> {new_filename}")
                renamed += 1
            except Exception as e:
                print(f"  ✗ 重命名失败 {temp_filename}: {e}")
                skipped += 1
        
        # 清理临时文件夹
        try:
            if self.temp_dir.exists():
                self.temp_dir.rmdir()
        except:
            pass
        
        print(f"\n✓ 重命名完成！成功: {renamed}, 跳过: {skipped}\n")
        return renamed
    
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
    downloader = BatchResumeDownloader()
    try:
        # 1. 启动浏览器
        downloader.start()
        
        # 2. 一次性登录
        downloader.login_once()
        
        # 3. 收集所有数据
        data_list = downloader.collect_all_data()
        
        if not data_list:
            print("没有数据可下载！")
        else:
            # 4. 批量下载（临时文件名）
            downloaded = downloader.batch_download(data_list)
            
            # 5. 批量重命名
            if downloaded > 0:
                renamed = downloader.batch_rename()
                
                print("="*60)
                print("全部完成！")
                print(f"下载目录: {downloader.download_dir}")
                print(f"共下载并重命名 {renamed} 个文件")
                print("="*60)
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        time.sleep(2)
        downloader.close()

