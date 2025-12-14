#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历批量下载脚本
登录指定网页，批量下载"投递简历"列的附件，并根据"名气直推投递"列重命名
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import urllib.parse


class ResumeDownloader:
    """简历下载器"""
    
    def __init__(self, download_dir=None, headless=False):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录，默认为当前目录下的 resumes 文件夹
            headless: 是否使用无头模式
        """
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), 'resumes')
        
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        
    def start_browser(self):
        """启动浏览器"""
        print("\n" + "="*60)
        print("简历批量下载脚本")
        print("="*60)
        print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"下载目录: {self.download_dir}")
        print("正在启动浏览器...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=500  # 减慢操作速度，便于观察
        )
        
        # 配置下载路径
        self.context = self.browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        
        print("浏览器启动成功！")
        
    def login(self, username="wzw", password="12345"):
        """
        登录网页
        
        Args:
            username: 用户名
            password: 密码
        """
        url = "https://xcx.highmarkcareer.com/console/deliveryrecord/index.html"
        print(f"\n正在访问: {url}")
        
        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(1)
            
            # 自动登录
            print("正在自动登录...")
            
            # 查找登录表单
            username_input = None
            password_input = None
            login_button = None
            
            # 尝试多种选择器查找用户名输入框
            username_selectors = [
                'input[type="text"]',
                'input[name="username"]',
                'input[placeholder*="用户名"]',
                'input[placeholder*="账号"]',
                'input[placeholder*="手机"]',
                'input[id*="user"]',
                'input[id*="name"]',
            ]
            
            for selector in username_selectors:
                try:
                    username_input = self.page.wait_for_selector(selector, timeout=2000)
                    if username_input and username_input.is_visible():
                        break
                except:
                    continue
            
            if username_input:
                username_input.fill(username)
                time.sleep(0.3)
                print(f"✓ 已输入用户名: {username}")
            
            # 查找密码输入框
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="密码"]',
                'input[id*="pass"]',
            ]
            
            for selector in password_selectors:
                try:
                    password_input = self.page.wait_for_selector(selector, timeout=2000)
                    if password_input and password_input.is_visible():
                        break
                except:
                    continue
            
            if password_input:
                password_input.fill(password)
                time.sleep(0.3)
                print("✓ 已输入密码")
            
            # 查找登录按钮
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("登陆")',
                'input[type="submit"]',
                'button.btn-primary',
                '.login-btn',
            ]
            
            for selector in login_selectors:
                try:
                    login_button = self.page.query_selector(selector)
                    if login_button and login_button.is_visible():
                        break
                except:
                    continue
            
            if login_button:
                login_button.click()
                print("✓ 已点击登录按钮")
                time.sleep(2)
            else:
                print("⚠ 未找到登录按钮，尝试按回车键...")
                if password_input:
                    password_input.press('Enter')
                    time.sleep(2)
            
            # 等待登录完成
            print("等待登录完成...")
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                current_url = self.page.url
                # 检查是否已跳转到目标页面
                if 'deliveryrecord' in current_url or 'index.html' in current_url:
                    # 检查是否有表格
                    try:
                        table = self.page.query_selector('#table1, table')
                        if table:
                            print(f"✓ 登录成功！(等待了{i+1}秒)")
                            break
                    except:
                        pass
            else:
                print("⚠ 登录检测超时，继续执行...")
            
            time.sleep(1)
            print("开始下载简历...")
            
        except Exception as e:
            print(f"访问页面时出现错误: {e}")
            print("请检查网络连接或网页是否可访问")
            time.sleep(5)
    
    def sanitize_filename(self, filename):
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        # 移除首尾空格和点
        filename = filename.strip(' .')
        # 限制文件名长度
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def find_table_headers(self):
        """查找表头，确定列索引"""
        headers = self.page.query_selector_all('table thead tr th, .table thead tr th, table thead tr td')
        if not headers:
            headers = self.page.query_selector_all('table tr:first-child th, table tr:first-child td')
        
        resume_col_idx = None
        student_col_idx = None
        
        if headers:
            print("\n表头信息：")
            for i, header in enumerate(headers):
                header_text = header.inner_text().strip()
                print(f"  列 {i}: {header_text}")
                if '投递简历' in header_text or '简历' in header_text:
                    resume_col_idx = i
                    print(f"    -> 找到'投递简历'列，索引: {i}")
                if '名气直推投递' in header_text or '学员' in header_text:
                    student_col_idx = i
                    print(f"    -> 找到'名气直推投递'列，索引: {i}")
        
        return resume_col_idx, student_col_idx
    
    def handle_pagination(self):
        """处理分页，加载所有数据 - 优化版本：先获取所有数据再下载"""
        print("\n检查分页并加载所有数据...")
        
        # 先尝试将每页显示数量设置为最大（100条）
        try:
            # 查找每页显示数量的下拉框
            length_select = self.page.query_selector('select[name="table1_length"]')
            if length_select:
                # 设置为100
                self.page.select_option('select[name="table1_length"]', value='100')
                time.sleep(1)  # 等待数据重新加载
                print("✓ 已设置每页显示100条记录")
        except:
            pass
        
        # 尝试查找分页控件并获取总页数
        try:
            # DataTables通常会在info中显示总记录数
            info_text = self.page.query_selector('#table1_info')
            if info_text:
                info = info_text.inner_text()
                print(f"表格信息: {info}")
        except:
            pass
        
        # 尝试点击所有"下一页"按钮，快速加载所有数据
        page_num = 1
        max_pages = 50  # 防止无限循环
        
        while page_num <= max_pages:
            # 查找下一页按钮（DataTables的分页按钮）
            next_button = None
            try:
                # DataTables的下一页按钮通常是 .paginate_button.next
                next_button = self.page.query_selector('#table1_next.paginate_button:not(.disabled)')
                if not next_button:
                    # 尝试其他选择器
                    next_buttons = self.page.query_selector_all('a.paginate_button.next:not(.disabled), button:has-text("下一页"), a:has-text("下一页")')
                    if next_buttons:
                        next_button = next_buttons[0]
            except:
                pass
            
            if not next_button:
                print(f"已加载所有 {page_num} 页数据")
                break
            
            # 快速点击下一页
            try:
                next_button.click()
                time.sleep(0.8)  # 减少等待时间
                page_num += 1
                if page_num % 5 == 0:
                    print(f"  已加载 {page_num} 页...")
            except Exception as e:
                print(f"点击下一页失败: {e}")
                break
        
        print(f"✓ 共加载 {page_num} 页数据")
    
    def download_resumes(self):
        """下载所有简历"""
        print("\n开始查找表格数据...")
        
        # 等待表格加载（DataTables需要时间加载数据）
        print("等待DataTables加载数据...")
        time.sleep(2)  # 减少等待时间
        
        # 等待表格数据加载完成
        try:
            # 检查DataTables是否已初始化并加载数据
            self.page.wait_for_function("""
                () => {
                    const table = document.querySelector('#table1');
                    if (!table) return false;
                    const tbody = table.querySelector('tbody');
                    if (!tbody) return false;
                    const rows = tbody.querySelectorAll('tr');
                    return rows.length > 0;
                }
            """, timeout=10000)  # 减少超时时间
            print("✓ 表格数据已加载")
        except:
            print("⚠ 等待表格数据加载超时，继续执行...")
            time.sleep(1)  # 减少等待时间
        
        # 保存页面HTML用于调试
        html_content = self.page.content()
        debug_file = self.download_dir / f'page_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已保存页面HTML到: {debug_file}（用于调试）")
        
        # 查找表格（使用ID table1）
        table = None
        try:
            table = self.page.wait_for_selector('#table1', timeout=10000)
            if table:
                print("✓ 找到表格: #table1")
        except:
            # 尝试其他选择器
            table_selectors = ['table', '.table', '[class*="table"]']
            for selector in table_selectors:
                try:
                    table = self.page.wait_for_selector(selector, timeout=3000)
                    if table:
                        print(f"✓ 找到表格: {selector}")
                        break
                except:
                    continue
        
        if not table:
            print("✗ 未找到表格，请检查页面结构")
            print("已保存页面HTML，请查看调试文件")
            return
        
        # 处理分页（如果需要）- 快速加载所有数据
        print("\n正在快速加载所有分页数据...")
        self.handle_pagination()
        
        # 重新获取所有行（包括新加载的）
        time.sleep(1)  # 等待最后一页数据加载
        rows = self.page.query_selector_all('#table1 tbody tr')
        if not rows:
            rows = self.page.query_selector_all('table tbody tr, .table tbody tr')
        print(f"✓ 总共找到 {len(rows)} 行数据，开始批量下载...")
        
        # 获取表格数据
        print("\n正在提取表格数据...")
        
        # 获取表格数据行（使用table1的tbody）
        rows = self.page.query_selector_all('#table1 tbody tr')
        if not rows:
            # 尝试其他选择器
            rows = self.page.query_selector_all('table tbody tr, .table tbody tr')
        
        print(f"找到 {len(rows)} 行数据")
        
        if len(rows) == 0:
            print("未找到数据行，尝试滚动加载...")
            # 尝试滚动页面加载更多数据
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                rows = self.page.query_selector_all('table tbody tr, .table tbody tr, [class*="row"]')
                if rows:
                    break
            print(f"滚动后找到 {len(rows)} 行数据")
        
        # 获取表头信息（针对table1）
        headers = self.page.query_selector_all('#table1 thead tr th')
        if not headers:
            headers = self.page.query_selector_all('table thead tr th, .table thead tr th')
        
        resume_col_idx = None
        student_col_idx = None
        
        if headers:
            print("\n表头信息：")
            for i, header in enumerate(headers):
                header_text = header.inner_text().strip()
                print(f"  列 {i}: {header_text}")
                if '投递简历' in header_text:
                    resume_col_idx = i
                    print(f"    -> 找到'投递简历'列，索引: {i}")
                if '名企直推投递' in header_text or '名气直推投递' in header_text:
                    student_col_idx = i
                    print(f"    -> 找到'名企直推投递'列，索引: {i}")
        
        if resume_col_idx is None or student_col_idx is None:
            print("⚠ 警告：未找到所有必需的列，将尝试自动识别...")
        
        downloaded_count = 0
        skipped_count = 0
        error_count = 0
        
        # 遍历每一行（批量处理，提高速度）
        print(f"\n开始批量下载，共 {len(rows)} 个文件...\n")
        for idx, row in enumerate(rows, 1):
            try:
                print(f"\n处理第 {idx}/{len(rows)} 行...")
                
                # 获取所有单元格
                cells = row.query_selector_all('td, th')
                if len(cells) < 2:
                    print(f"  跳过：单元格数量不足 ({len(cells)})")
                    skipped_count += 1
                    continue
                
                # 如果找不到表头，尝试通过内容判断
                if resume_col_idx is None or student_col_idx is None:
                    # 遍历单元格查找
                    for i, cell in enumerate(cells):
                        cell_text = cell.inner_text().strip()
                        # 查找包含下载链接或附件的单元格
                        links = cell.query_selector_all('a[href*="download"], a[href*="file"], a[href*=".pdf"], a[href*=".doc"], a[href*=".docx"]')
                        if links and resume_col_idx is None:
                            resume_col_idx = i
                        # 查找学员信息
                        if ('学员' in cell_text or len(cell_text) > 0) and student_col_idx is None:
                            student_col_idx = i
                
                # 获取学员名称（用于重命名）- 从"名企直推投递"列提取姓名
                student_name = ""
                if student_col_idx is not None and student_col_idx < len(cells):
                    student_info = cells[student_col_idx].inner_text().strip()
                    # 提取姓名（格式：姓名：xxx）
                    name_match = re.search(r'姓名[：:]\s*([^，,]+)', student_info)
                    if name_match:
                        student_name = name_match.group(1).strip()
                    else:
                        # 如果没有找到，使用整个文本的前20个字符
                        student_name = student_info[:20] if student_info else ""
                    # 清理换行符和多余空格
                    student_name = ' '.join(student_name.split())
                    student_name = self.sanitize_filename(student_name)
                
                if not student_name:
                    # 如果找不到学员名称，尝试从其他列获取
                    for cell in cells:
                        cell_text = cell.inner_text().strip()
                        if cell_text and len(cell_text) < 50 and cell_text != '下载' and cell_text != '查看':
                            # 可能是学员名称
                            student_name = self.sanitize_filename(cell_text)
                            if student_name:
                                break
                
                if not student_name:
                    student_name = f"学员_{idx}"
                
                # 获取简历下载链接
                resume_cell = None
                if resume_col_idx is not None and resume_col_idx < len(cells):
                    resume_cell = cells[resume_col_idx]
                else:
                    # 如果找不到，尝试在所有单元格中查找
                    for cell in cells:
                        links = cell.query_selector_all('a[href*="download"], a[href*="file"], a[href*=".pdf"], a[href*=".doc"], a[href*=".docx"]')
                        if links:
                            resume_cell = cell
                            break
                
                if not resume_cell:
                    print(f"  跳过：未找到简历链接")
                    skipped_count += 1
                    continue
                
                # 查找下载链接（尝试多种方式）
                download_links = resume_cell.query_selector_all('a[href]')
                if not download_links:
                    # 尝试查找按钮
                    buttons = resume_cell.query_selector_all('button, [class*="btn"], [class*="download"]')
                    if buttons:
                        # 如果有按钮，可能需要点击按钮触发下载
                        download_link = buttons[0]
                        # 尝试从按钮的onclick或data属性获取链接
                        onclick = download_link.get_attribute('onclick') or ''
                        data_url = download_link.get_attribute('data-url') or download_link.get_attribute('data-href') or ''
                        href = data_url if data_url else None
                    else:
                        print(f"  跳过：未找到下载链接或按钮")
                        skipped_count += 1
                        continue
                else:
                    # 获取第一个链接
                    download_link = download_links[0]
                    href = download_link.get_attribute('href')
                
                if not href:
                    # 如果链接为空，尝试从onclick中提取
                    onclick = download_link.get_attribute('onclick') or ''
                    url_match = re.search(r'["\']([^"\']*(?:download|file|\.pdf|\.doc)[^"\']*)["\']', onclick)
                    if url_match:
                        href = url_match.group(1)
                    else:
                        print(f"  跳过：无法获取下载链接")
                        skipped_count += 1
                        continue
                
                # 处理相对路径
                if href.startswith('/'):
                    href = f"https://xcx.highmarkcareer.com{href}"
                elif not href.startswith('http'):
                    base_url = self.page.url.split('/console')[0] if '/console' in self.page.url else self.page.url
                    href = urllib.parse.urljoin(base_url, href)
                
                print(f"  学员: {student_name}")
                print(f"  链接: {href}")
                
                # 获取原始文件名
                link_text = download_link.inner_text().strip()
                if not link_text or link_text == '下载' or link_text == '查看':
                    # 尝试从href中提取文件名
                    original_filename = href.split('/')[-1].split('?')[0]
                else:
                    original_filename = link_text
                
                # 获取文件扩展名
                file_ext = os.path.splitext(original_filename)[1]
                if not file_ext:
                    file_ext = '.pdf'  # 默认扩展名
                
                # 构建新文件名
                new_filename = f"{student_name}{file_ext}"
                filepath = self.download_dir / new_filename
                
                # 如果文件已存在，添加序号
                counter = 1
                while filepath.exists():
                    name_part = f"{student_name}_{counter}{file_ext}"
                    filepath = self.download_dir / name_part
                    counter += 1
                
                # 下载文件
                print(f"  [{idx}/{len(rows)}] 下载: {new_filename}")
                try:
                    with self.page.expect_download(timeout=15000) as download_info:  # 减少超时时间
                        # 点击下载链接
                        download_link.click()
                    
                    download = download_info.value
                    # 保存文件
                    download.save_as(filepath)
                    print(f"  ✓ 成功: {filepath.name}")
                    downloaded_count += 1
                    
                except Exception as e:
                    print(f"  ✗ 失败: {e}")
                    error_count += 1
                
                # 减少延迟，提高速度
                if idx % 5 == 0:
                    time.sleep(0.3)  # 每5个文件稍作停顿
                else:
                    time.sleep(0.1)  # 减少延迟
                
            except Exception as e:
                print(f"  处理第 {idx} 行时出错: {e}")
                error_count += 1
                continue
        
        print("\n" + "="*60)
        print("下载完成！")
        print(f"成功下载: {downloaded_count} 个文件")
        print(f"跳过: {skipped_count} 个")
        print(f"错误: {error_count} 个")
        print(f"下载目录: {self.download_dir}")
        print("="*60)
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("\n浏览器已关闭")


def main():
    """主函数"""
    downloader = ResumeDownloader(headless=False)  # 设置为False以便观察和手动操作
    
    try:
        downloader.start_browser()
        downloader.login(username="wzw", password="12345")
        
        # 直接开始下载
        print("\n" + "="*60)
        print("开始批量下载简历...")
        print("="*60)
        
        downloader.download_resumes()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n下载任务完成！")
        print(f"所有简历已保存到: {downloader.download_dir}")
        # 等待5秒后自动关闭，给用户时间查看结果
        print("5秒后自动关闭浏览器...")
        time.sleep(5)
        downloader.close()


if __name__ == '__main__':
    main()

