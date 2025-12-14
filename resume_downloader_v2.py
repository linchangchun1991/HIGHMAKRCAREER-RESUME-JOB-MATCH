#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历批量下载脚本 V2
1. 用户手动登录后，脚本自动操作
2. 依次点击"投递简历"列的所有链接下载
3. 使用"名企直推投递"列的完整文本重命名
"""

import os
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


class ResumeDownloaderV2:
    def __init__(self):
        self.download_dir = Path(__file__).parent / 'resumes'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start(self):
        print("="*60)
        print("简历批量下载工具 V2")
        print("="*60)
        print(f"下载目录: {self.download_dir}\n")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=50)
        self.page = self.browser.new_page(accept_downloads=True)
        
    def wait_for_login(self):
        """等待用户手动登录"""
        print("正在打开登录页面...")
        try:
            self.page.goto("https://xcx.highmarkcareer.com/console/deliveryrecord/index.html", timeout=30000)
        except:
            pass
        time.sleep(2)
        
        print("\n" + "="*60)
        print("请手动完成登录：")
        print("1. 在浏览器中输入账号和密码")
        print("2. 点击登录按钮")
        print("3. 等待页面跳转到投递记录页面")
        print("="*60)
        print("\n等待登录完成（最多等待5分钟）...")
        
        # 等待登录完成（检测表格出现）
        max_wait = 300  # 最多等待5分钟
        for i in range(max_wait):
            try:
                # 检查页面是否还在（防止浏览器被关闭）
                try:
                    if not self.page or self.page.is_closed():
                        print("\n⚠ 浏览器页面已关闭，请重新运行脚本")
                        return False
                except:
                    # 如果检查页面状态时出错，继续等待
                    pass
                
                # 检查是否有表格
                table = self.page.query_selector('#table1')
                if table:
                    # 检查是否有数据行
                    rows = self.page.query_selector_all('#table1 tbody tr')
                    if len(rows) > 0:
                        print(f"\n✓ 登录成功！检测到 {len(rows)} 行数据\n")
                        return True
            except Exception as e:
                # 如果页面出错，继续等待
                pass
            
            time.sleep(1)
            if (i + 1) % 10 == 0:
                print(f"  等待中... ({i+1}秒)")
        
        print("\n⚠ 等待超时，但继续尝试执行...")
        return True  # 即使超时也继续执行
    
    def sanitize_filename(self, text):
        """清理文件名，将非法字符替换为下划线"""
        if not text:
            return "未知"
        
        # 替换所有非法字符为下划线
        filename = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', text)
        # 替换多个连续的下划线为一个
        filename = re.sub(r'_+', '_', filename)
        # 移除首尾空格和下划线
        filename = filename.strip(' _')
        # 限制长度
        if len(filename) > 150:
            filename = filename[:150]
        
        return filename if filename else "未知"
    
    def download_all(self):
        """快速下载所有简历（测试模式：前5个）"""
        print("="*60)
        print("开始收集数据并下载（测试模式）...")
        print("="*60)
        
        # 确保页面还在
        try:
            if self.page.is_closed():
                print("✗ 页面已关闭，无法继续")
                return
        except:
            print("⚠ 无法检查页面状态，继续执行...")
        
        # 等待表格完全加载
        print("等待表格数据加载...")
        time.sleep(3)
        
        # 不需要加载所有分页，只处理当前页的前5个
        print("✓ 使用当前页数据（测试模式）\n")
        time.sleep(1)
        
        # 获取所有行（多次尝试）
        rows = []
        for attempt in range(5):
            try:
                rows = self.page.query_selector_all('#table1 tbody tr')
                if len(rows) > 0:
                    break
                time.sleep(1)
            except Exception as e:
                print(f"  尝试 {attempt+1}/5 获取数据行...")
                time.sleep(1)
        
        print(f"找到 {len(rows)} 行数据\n")
        
        if len(rows) == 0:
            print("✗ 未找到数据！")
            print("请确保已登录并看到投递记录表格")
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
        
        print(f"简历列索引: {resume_idx}, 名企直推投递列索引: {student_idx}\n")
        
        if resume_idx is None:
            print("✗ 未找到'投递简历'列！")
            return
        
        # 开始下载（先处理前5个作为测试）
        print("="*60)
        print("开始批量下载（测试模式：前5个）...")
        print("="*60)
        
        downloaded = 0
        failed = 0
        skipped = 0
        test_count = 5  # 只处理前5个
        
        for idx, row in enumerate(rows, 1):
            if idx > test_count:
                print(f"\n测试模式：已处理前{test_count}个，停止")
                break
                
            try:
                cells = row.query_selector_all('td')
                if len(cells) <= max(resume_idx or 0, student_idx or 0):
                    skipped += 1
                    continue
                
                # 获取"名企直推投递"列的完整文本（用于重命名）
                rename_text = ""
                if student_idx is not None and student_idx < len(cells):
                    rename_text = cells[student_idx].inner_text().strip()
                
                # 获取下载链接
                link = None
                if resume_idx < len(cells):
                    link = cells[resume_idx].query_selector('a[href]')
                
                if not link:
                    skipped += 1
                    print(f"[{idx}/{test_count}] 跳过：无下载链接")
                    continue
                
                href = link.get_attribute('href')
                if not href:
                    skipped += 1
                    print(f"[{idx}/{test_count}] 跳过：链接为空")
                    continue
                
                # 获取文件扩展名
                ext = os.path.splitext(href.split('?')[0])[1] or '.pdf'
                
                # 使用"名企直推投递"列的完整文本作为文件名
                filename = self.sanitize_filename(rename_text)
                full_filename = f"{filename}{ext}"
                filepath = self.download_dir / full_filename
                
                # 处理重名（添加序号）
                counter = 1
                while filepath.exists():
                    full_filename = f"{filename}_{counter}{ext}"
                    filepath = self.download_dir / full_filename
                    counter += 1
                
                # 下载
                print(f"\n[{idx}/{test_count}] 正在下载: {full_filename}")
                print(f"  名企直推投递: {rename_text[:80]}...")
                
                try:
                    # 直接点击链接下载
                    with self.page.expect_download(timeout=15000) as download_info:
                        link.click()
                    
                    # 保存文件（使用重命名后的文件名）
                    download = download_info.value
                    download.save_as(filepath)
                    
                    # 关闭可能打开的新标签页（通过context获取）
                    try:
                        context = self.page.context
                        pages = context.pages
                        if len(pages) > 1:
                            # 关闭除主页面外的其他页面
                            for page in pages:
                                if page != self.page and not page.is_closed():
                                    try:
                                        page.close()
                                    except:
                                        pass
                    except:
                        pass
                    
                    downloaded += 1
                    print(f"  ✓ 下载成功: {full_filename}")
                    time.sleep(0.3)  # 短暂延迟
                    
                except Exception as e:
                    print(f"  ✗ 下载失败: {str(e)[:80]}")
                    failed += 1
                    # 确保关闭可能打开的标签页
                    try:
                        context = self.page.context
                        pages = context.pages
                        if len(pages) > 1:
                            for page in pages:
                                if page != self.page and not page.is_closed():
                                    try:
                                        page.close()
                                    except:
                                        pass
                    except:
                        pass
                    
            except Exception as e:
                print(f"  行{idx}处理错误: {str(e)[:80]}")
                failed += 1
                continue
        
        print(f"\n{'='*60}")
        print("下载完成！")
        print(f"成功: {downloaded} 个")
        print(f"失败: {failed} 个")
        print(f"跳过: {skipped} 个")
        print(f"保存位置: {self.download_dir}")
        print(f"{'='*60}")
    
    def close(self):
        time.sleep(1)
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == '__main__':
    downloader = ResumeDownloaderV2()
    try:
        # 1. 启动浏览器
        downloader.start()
        
        # 2. 等待用户手动登录
        login_success = downloader.wait_for_login()
        
        if login_success:
            # 3. 批量下载并重命名
            print("开始下载流程...\n")
            downloader.download_all()
        else:
            print("登录检测失败，但继续尝试下载...\n")
            downloader.download_all()
        
        print("\n" + "="*60)
        print("所有操作完成！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        print("脚本执行完成")
        print("="*60)
        # 不自动关闭浏览器，让用户手动关闭
        print("\n浏览器将保持打开状态，请手动关闭浏览器窗口")
        print("或者按 Ctrl+C 退出脚本")
        try:
            # 等待用户操作，不强制关闭
            import signal
            def signal_handler(sig, frame):
                print("\n\n收到中断信号，正在关闭...")
                downloader.close()
                exit(0)
            signal.signal(signal.SIGINT, signal_handler)
            
            # 保持脚本运行，直到用户手动关闭
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n用户中断，正在关闭浏览器...")
            downloader.close()
        except Exception as e:
            print(f"\n发生错误: {e}")
            downloader.close()

