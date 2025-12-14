#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历批量下载脚本 V3
功能：自动下载网页中的简历文件，并按照特定规则重命名
"""

import os
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class ResumeDownloaderV3:
    """简历下载器 V3"""
    
    def __init__(self):
        """初始化下载器"""
        # 创建下载文件夹
        self.download_dir = Path(__file__).parent / 'resumes_download'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        
    def start_browser(self):
        """启动浏览器"""
        print("="*60)
        print("简历批量下载工具 V3")
        print("="*60)
        print(f"下载目录: {self.download_dir.absolute()}\n")
        
        # 启动 Playwright
        self.playwright = sync_playwright().start()
        
        # 启动 Chromium 浏览器（非无头模式，可以看到界面）
        self.browser = self.playwright.chromium.launch(
            headless=False,
            slow_mo=100  # 减慢操作速度，便于观察
        )
        
        # 创建浏览器上下文，启用下载功能
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        
        print("✓ 浏览器已启动\n")
    
    def open_page_and_wait_login(self):
        """打开目标页面并等待用户手动登录"""
        url = "https://xcx.highmarkcareer.com/console/deliveryrecord/index.html"
        
        print(f"正在打开页面: {url}")
        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            print("✓ 页面已打开\n")
        except Exception as e:
            print(f"⚠ 打开页面时出现错误: {e}")
            print("继续执行...\n")
        
        # 等待用户手动登录
        print("="*60)
        print("请手动完成登录操作：")
        print("1. 在浏览器中输入账号密码或扫码登录")
        print("2. 等待页面跳转到投递记录列表页")
        print("3. 确保能看到表格数据")
        print("="*60)
        print("\n等待登录完成（自动检测，最多等待5分钟）...")
        
        # 自动检测登录状态
        max_wait = 300  # 最多等待5分钟
        logged_in = False
        
        for i in range(max_wait):
            try:
                # 检查是否有表格和数据
                table = self.page.query_selector('#table1')
                if table:
                    rows = self.page.query_selector_all('#table1 tbody tr')
                    if len(rows) > 0:
                        print(f"\n✓ 检测到登录成功！找到 {len(rows)} 行数据\n")
                        logged_in = True
                        break
            except:
                pass
            
            time.sleep(1)
            if (i + 1) % 10 == 0:
                print(f"  等待中... ({i+1}秒)")
        
        if not logged_in:
            print("\n⚠ 等待超时，但继续尝试执行...\n")
        
        # 等待页面稳定
        time.sleep(2)
        print("✓ 开始执行下载流程...\n")
    
    def extract_student_name(self, text):
        """
        从"名企直推投递"列的文本中提取学员姓名
        
        Args:
            text: "名企直推投递"列的完整文本
            
        Returns:
            提取的学员姓名，如果提取失败返回"未知学员"
        """
        if not text:
            return "未知学员"
        
        # 使用正则表达式提取"姓名："后面的名字
        # 匹配模式：姓名：xxx（后面可能是逗号、换行等）
        pattern = r'姓名[：:]\s*([^，,\n\r]+)'
        match = re.search(pattern, text)
        
        if match:
            name = match.group(1).strip()
            # 清理名字中的多余空格
            name = ' '.join(name.split())
            return name if name else "未知学员"
        else:
            return "未知学员"
    
    def sanitize_filename(self, text):
        """
        清洗文件名，将非法字符替换为下划线
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文件名
        """
        if not text:
            return ""
        
        # 替换所有非法字符为下划线
        # 非法字符包括：< > : " / \ | ? * \n \r \t 以及中文标点
        # 特别注意：换行符 \n 必须替换
        filename = re.sub(r'[\n\r\t]', '_', text)  # 先处理换行符和制表符
        filename = re.sub(r'[<>:"/\\|?*，,。.；;：:！!？?、]', '_', filename)  # 再处理其他特殊字符
        
        # 替换多个连续的下划线为一个
        filename = re.sub(r'_+', '_', filename)
        
        # 移除首尾空格和下划线
        filename = filename.strip(' _')
        
        return filename if filename else "未知"
    
    def get_table_data(self):
        """
        获取表格中的所有数据行
        
        Returns:
            list: 包含(简历链接, 名企直推投递文本, 学员姓名)的元组列表
        """
        print("正在获取表格数据...")
        
        # 等待表格加载
        try:
            # 等待表格出现
            self.page.wait_for_selector('#table1', timeout=10000)
            time.sleep(1)
        except PlaywrightTimeoutError:
            print("⚠ 未找到表格，尝试继续执行...")
        
        # 获取所有数据行
        rows = self.page.query_selector_all('#table1 tbody tr')
        print(f"找到 {len(rows)} 行数据\n")
        
        if len(rows) == 0:
            print("✗ 未找到数据行！")
            return []
        
        # 获取表头，确定列索引
        headers = self.page.query_selector_all('#table1 thead tr th')
        resume_col_idx = None  # "投递简历"列的索引
        student_col_idx = None  # "名企直推投递"列的索引
        
        for i, header in enumerate(headers):
            header_text = header.inner_text().strip()
            if '投递简历' in header_text:
                resume_col_idx = i
                print(f"✓ 找到'投递简历'列，索引: {i}")
            if '名企直推投递' in header_text:
                student_col_idx = i
                print(f"✓ 找到'名企直推投递'列，索引: {i}")
        
        if resume_col_idx is None:
            print("✗ 未找到'投递简历'列！")
            return []
        
        if student_col_idx is None:
            print("⚠ 未找到'名企直推投递'列，将使用默认名称")
        
        # 提取每一行的数据
        data_list = []
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.query_selector_all('td')
                
                # 检查单元格数量是否足够
                if len(cells) <= max(resume_col_idx, student_col_idx or 0):
                    print(f"  [行{idx}] 跳过：单元格数量不足")
                    continue
                
                # 提取简历链接
                resume_cell = cells[resume_col_idx]
                link = resume_cell.query_selector('a[href]')
                
                if not link:
                    print(f"  [行{idx}] 跳过：未找到简历链接")
                    continue
                
                href = link.get_attribute('href')
                if not href:
                    print(f"  [行{idx}] 跳过：链接为空")
                    continue
                
                # 处理相对路径
                if not href.startswith('http'):
                    href = f"https://xcx.highmarkcareer.com{href}"
                
                # 保存链接元素，用于后续点击下载
                # 注意：我们需要保存链接元素，而不是只保存href
                
                # 提取"名企直推投递"列的完整文本
                student_info_text = ""
                if student_col_idx is not None and student_col_idx < len(cells):
                    student_info_text = cells[student_col_idx].inner_text().strip()
                
                # 提取学员姓名
                student_name = self.extract_student_name(student_info_text)
                
                # 保存链接元素和href，用于后续下载
                data_list.append((link, href, student_info_text, student_name))
                
            except Exception as e:
                print(f"  [行{idx}] 处理错误: {str(e)[:50]}")
                continue
        
        print(f"✓ 成功提取 {len(data_list)} 条有效数据\n")
        return data_list
    
    def download_resume_fast(self, href, student_info_text, student_name, index, total, cookies_dict):
        """
        快速下载单个简历文件（多线程版本，不依赖self.context）
        
        Args:
            href: 简历下载链接URL
            student_info_text: "名企直推投递"列的完整文本
            student_name: 学员姓名
            index: 当前索引
            total: 总数
            cookies_dict: cookies字典（从外部传入）
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 获取文件扩展名
            ext = os.path.splitext(href.split('?')[0])[1]
            if not ext:
                ext = '.pdf'  # 默认扩展名
            
            # 构建新文件名：学员名_名企直推投递完整内容.扩展名
            # 先清洗"名企直推投递"的文本
            cleaned_info = self.sanitize_filename(student_info_text)
            
            # 限制文件名长度（前50个字符）
            if len(cleaned_info) > 50:
                cleaned_info = cleaned_info[:50]
            
            # 构建文件名
            filename = f"{student_name}_{cleaned_info}{ext}"
            
            # 再次确保文件名不超过限制（总长度限制200字符）
            if len(filename) > 200:
                # 保留学员名和部分信息
                max_info_len = 200 - len(student_name) - len(ext) - 1
                if max_info_len > 0:
                    cleaned_info = cleaned_info[:max_info_len]
                    filename = f"{student_name}_{cleaned_info}{ext}"
                else:
                    # 如果学员名太长，只保留学员名
                    filename = f"{student_name[:200-len(ext)]}{ext}"
            
            filepath = self.download_dir / filename
            
            # 处理重名文件（添加序号）
            counter = 1
            while filepath.exists():
                name_part = f"{student_name}_{cleaned_info}_{counter}"
                if len(name_part) > 200 - len(ext):
                    name_part = name_part[:200 - len(ext)]
                filename = f"{name_part}{ext}"
                filepath = self.download_dir / filename
                counter += 1
            
            # 打印进度（线程安全）
            print(f"[{index}/{total}] 正在下载 {student_name} 的简历...")
            
            # 直接请求下载文件（不点击链接，不打开新标签页）
            response = requests.get(
                href,
                cookies=cookies_dict,
                timeout=20,  # 减少超时时间
                stream=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 检查文件是否成功保存
            if filepath.exists() and filepath.stat().st_size > 0:
                file_size = filepath.stat().st_size / 1024  # KB
                print(f"  ✓ [{index}/{total}] 下载成功: {filepath.name} ({file_size:.1f} KB)")
                return True
            else:
                print(f"  ✗ [{index}/{total}] 下载失败: 文件为空或未保存")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ [{index}/{total}] 下载失败（网络错误）: {str(e)[:50]}")
            return False
        except Exception as e:
            print(f"  ✗ [{index}/{total}] 下载失败: {str(e)[:50]}")
            return False
    
    def download_resume(self, link, href, student_info_text, student_name, index, total):
        """
        下载单个简历文件并重命名（使用直接请求方式，不点击链接）
        
        Args:
            link: 链接元素（仅用于获取href，不点击）
            href: 简历下载链接URL
            student_info_text: "名企直推投递"列的完整文本
            student_name: 学员姓名
            index: 当前索引
            total: 总数
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 获取文件扩展名
            ext = os.path.splitext(href.split('?')[0])[1]
            if not ext:
                ext = '.pdf'  # 默认扩展名
            
            # 构建新文件名：学员名_名企直推投递完整内容.扩展名
            # 先清洗"名企直推投递"的文本
            cleaned_info = self.sanitize_filename(student_info_text)
            
            # 限制文件名长度（前50个字符）
            if len(cleaned_info) > 50:
                cleaned_info = cleaned_info[:50]
            
            # 构建文件名
            filename = f"{student_name}_{cleaned_info}{ext}"
            
            # 再次确保文件名不超过限制（总长度限制200字符）
            if len(filename) > 200:
                # 保留学员名和部分信息
                max_info_len = 200 - len(student_name) - len(ext) - 1
                if max_info_len > 0:
                    cleaned_info = cleaned_info[:max_info_len]
                    filename = f"{student_name}_{cleaned_info}{ext}"
                else:
                    # 如果学员名太长，只保留学员名
                    filename = f"{student_name[:200-len(ext)]}{ext}"
            
            filepath = self.download_dir / filename
            
            # 处理重名文件（添加序号）
            counter = 1
            while filepath.exists():
                name_part = f"{student_name}_{cleaned_info}_{counter}"
                if len(name_part) > 200 - len(ext):
                    name_part = name_part[:200 - len(ext)]
                filename = f"{name_part}{ext}"
                filepath = self.download_dir / filename
                counter += 1
            
            # 打印进度
            print(f"[{index}/{total}] 正在下载 {student_name} 的简历...")
            print(f"  文件名: {filename}")
            print(f"  链接: {href[:80]}...")
            
            # cookies通过参数传入（避免重复获取）
            
            # 获取当前浏览器的cookies（用于身份验证）
            cookies = self.context.cookies()
            
            # 构建cookies字典供requests使用
            cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # 直接请求下载文件（不点击链接，不打开新标签页）
            response = requests.get(
                href,
                cookies=cookies_dict,
                timeout=20,  # 减少超时时间
                stream=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 检查文件是否成功保存
            if filepath.exists() and filepath.stat().st_size > 0:
                file_size = filepath.stat().st_size / 1024  # KB
                print(f"  ✓ 下载成功: {filepath.name} ({file_size:.1f} KB)\n")
                return True
            else:
                print(f"  ✗ 下载失败: 文件为空或未保存\n")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ 下载失败（网络错误）: {str(e)[:80]}\n")
            return False
        except Exception as e:
            print(f"  ✗ 下载失败: {str(e)[:80]}\n")
            return False
    
    def download_all(self):
        """下载所有简历（使用多线程加速）"""
        # 获取表格数据
        data_list = self.get_table_data()
        
        if not data_list:
            print("没有数据可下载！")
            return
        
        print("="*60)
        print(f"开始下载 {len(data_list)} 个简历文件（多线程加速）...")
        print("="*60)
        print()
        
        # 获取cookies（所有线程共享）
        cookies = self.context.cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # 统计信息
        success_count = 0
        failed_count = 0
        
        # 使用线程池并发下载（最多5个并发）
        max_workers = 5
        
        def download_single(args):
            """单个下载任务的包装函数"""
            idx, link, href, student_info_text, student_name, total = args
            return self.download_resume_fast(
                href, 
                student_info_text, 
                student_name, 
                idx, 
                total,
                cookies_dict
            )
        
        # 准备参数列表
        download_args = [
            (idx, link, href, student_info_text, student_name, len(data_list))
            for idx, (link, href, student_info_text, student_name) in enumerate(data_list, 1)
        ]
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_args = {
                executor.submit(download_single, args): args 
                for args in download_args
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_args):
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"  ✗ 任务执行错误: {str(e)[:80]}")
                    failed_count += 1
        
        # 打印总结
        print("="*60)
        print("下载完成！")
        print(f"成功: {success_count} 个")
        print(f"失败: {failed_count} 个")
        print(f"保存位置: {self.download_dir.absolute()}")
        print("="*60)
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            try:
                self.page.close()
            except:
                pass
        if self.context:
            try:
                self.context.close()
            except:
                pass
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
        print("\n浏览器已关闭")


def main():
    """主函数"""
    downloader = ResumeDownloaderV3()
    
    try:
        # 1. 启动浏览器
        downloader.start_browser()
        
        # 2. 打开页面并等待登录
        downloader.open_page_and_wait_login()
        
        # 3. 下载所有简历
        downloader.download_all()
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n脚本执行完成")
        print("浏览器将保持打开状态，请手动关闭")
        # 不自动关闭，让用户手动关闭浏览器
        try:
            # 保持脚本运行一段时间，然后退出
            time.sleep(5)
        except:
            pass
        downloader.close()


if __name__ == '__main__':
    main()

