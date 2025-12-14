import time
import random
import traceback
import re
from urllib.parse import urlparse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    InvalidSessionIdException,
)
from bs4 import BeautifulSoup


# 配置
INPUT_FILE = "/Users/changchun/Desktop/最新学员需求投递表格.xlsx"  # 输入Excel文件路径
OUTPUT_FILE = "/Users/changchun/Desktop/招聘信息汇总.xlsx"  # 输出Excel文件路径
LINK_COLUMN = "真实投递链接"  # 链接所在的列名，如果列名不同请修改


def create_driver():
    """启动 Chrome 浏览器"""
    import subprocess
    
    # 清理可能存在的僵尸进程
    try:
        subprocess.run(["pkill", "-f", "chromedriver"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      timeout=2)
        time.sleep(1)
    except Exception:
        pass
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 可选：无头模式（不显示浏览器窗口）
    # options.add_argument("--headless")
    
    try:
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"使用 webdriver_manager 启动失败: {e}")
        print("尝试使用系统默认 ChromeDriver...")
        driver = webdriver.Chrome(options=options)
        return driver


def random_sleep(min_sec=2, max_sec=4):
    """防反爬：随机等待"""
    time.sleep(random.uniform(min_sec, max_sec))


def extract_company_name(driver, soup):
    """提取招聘公司名称"""
    company_name = ""
    
    # 策略1: 查找包含"公司"、"企业"等关键词的元素
    company_keywords = ['公司', '企业', '集团', '股份', '有限', '银行', '保险', '证券', '科技', '有限公司']
    
    # 尝试多种选择器
    selectors = [
        # 通过class查找
        "[class*='company']",
        "[class*='企业']",
        "[class*='corp']",
        "[class*='firm']",
        # 通过id查找
        "[id*='company']",
        "[id*='企业']",
        # 标题元素
        "h1, h2, h3",
        # 常见的公司名位置
        ".title, .name, .company-name, .enterprise-name",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if not text or len(text) > 100:
                    continue
                # 检查是否包含公司关键词
                if any(keyword in text for keyword in company_keywords):
                    # 提取公司名（通常在公司关键词之前）
                    for keyword in company_keywords:
                        if keyword in text:
                            # 尝试提取公司名部分
                            parts = text.split(keyword)
                            if parts[0]:
                                company_name = (parts[0] + keyword).strip()
                                if 2 <= len(company_name) <= 50:
                                    return company_name
                            # 如果分割失败，使用整个文本
                            if 2 <= len(text) <= 50:
                                company_name = text
                                return company_name
        except Exception:
            continue
    
    # 策略2: 从页面标题提取
    try:
        title = driver.title
        if title:
            # 移除常见的后缀
            title = title.replace("招聘", "").replace("校招", "").replace("岗位", "").strip()
            if any(keyword in title for keyword in company_keywords):
                if 2 <= len(title) <= 50:
                    company_name = title
                    return company_name
    except Exception:
        pass
    
    # 策略3: 从URL提取（某些网站URL包含公司名）
    try:
        url = driver.current_url
        domain = urlparse(url).netloc
        # 提取子域名或路径中的公司名
        parts = domain.split('.')
        if len(parts) > 2:
            potential_name = parts[0]
            if 2 <= len(potential_name) <= 20 and not potential_name.isdigit():
                company_name = potential_name
    except Exception:
        pass
    
    return company_name[:50] if company_name else ""


def extract_job_title(driver, soup):
    """提取招聘岗位"""
    job_title = ""
    
    # 岗位关键词
    job_keywords = ['岗位', '职位', '招聘', '校招', '职位名称', '岗位名称', 'Job', 'Position', 'Title']
    
    # 尝试多种选择器
    selectors = [
        "[class*='job']",
        "[class*='position']",
        "[class*='职位']",
        "[class*='岗位']",
        "[id*='job']",
        "[id*='position']",
        "h1, h2, h3, h4",
        ".title, .job-title, .position-title, .name",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if not text or len(text) > 100:
                    continue
                # 检查是否包含岗位关键词
                if any(keyword in text for keyword in job_keywords):
                    # 清理文本
                    text = text.replace("招聘", "").replace("校招", "").strip()
                    if 2 <= len(text) <= 100:
                        job_title = text
                        return job_title
        except Exception:
            continue
    
    # 策略2: 从页面标题提取
    try:
        title = driver.title
        if title:
            # 移除公司名，保留岗位名
            title = re.sub(r'.*?招聘', '', title)
            title = re.sub(r'.*?校招', '', title)
            title = title.strip()
            if 2 <= len(title) <= 100:
                job_title = title
                return job_title
    except Exception:
        pass
    
    return job_title[:100] if job_title else ""


def extract_base_location(driver, soup):
    """提取Base地点"""
    base_location = ""
    
    # 地点关键词
    location_keywords = ['地点', '工作地点', 'Base', 'Location', '工作城市', '城市', '地址', '工作地址']
    city_keywords = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', 
                     '苏州', '天津', '重庆', '青岛', '大连', '厦门', '宁波', '无锡', '长沙',
                     '郑州', '济南', '合肥', '福州', '石家庄', '哈尔滨', '长春', '沈阳',
                     '江苏', '浙江', '广东', '山东', '河南', '四川', '湖北', '陕西', '湖南']
    
    # 尝试多种选择器
    selectors = [
        "[class*='location']",
        "[class*='地点']",
        "[class*='city']",
        "[class*='address']",
        "[id*='location']",
        "[id*='地点']",
        ".location, .city, .address, .base",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if not text or len(text) > 30:
                    continue
                # 检查是否包含地点关键词
                if any(keyword in text for keyword in location_keywords + city_keywords):
                    # 提取城市名
                    for city in city_keywords:
                        if city in text:
                            base_location = city
                            return base_location
                    # 如果没有匹配到城市，使用整个文本
                    if 2 <= len(text) <= 30:
                        base_location = text
                        return base_location
        except Exception:
            continue
    
    # 策略2: 从文本中正则提取
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        # 查找城市名
        for city in city_keywords:
            if city in page_text:
                # 查找城市附近的上下文
                pattern = rf'[工作地点|Base|地点|城市].*?{city}'
                matches = re.findall(pattern, page_text)
                if matches:
                    base_location = city
                    return base_location
    except Exception:
        pass
    
    return base_location[:30] if base_location else ""


def extract_publish_time(driver, soup):
    """提取发布时间"""
    publish_time = ""
    
    # 时间关键词
    time_keywords = ['发布时间', '发布日期', '更新日期', '发布时间', 'Publish', 'Date', 'Time', '更新']
    
    # 日期格式模式
    date_patterns = [
        r'(\d{4}-\d{1,2}-\d{1,2})',  # 2025-12-05
        r'(\d{4}/\d{1,2}/\d{1,2})',  # 2025/12/05
        r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2025年12月5日
        r'(\d{4}\.\d{1,2}\.\d{1,2})',  # 2025.12.05
    ]
    
    # 尝试多种选择器
    selectors = [
        "[class*='time']",
        "[class*='date']",
        "[class*='时间']",
        "[class*='日期']",
        "[id*='time']",
        "[id*='date']",
        ".time, .date, .publish-time, .update-time",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if not text:
                    continue
                # 检查是否包含时间关键词或日期格式
                if any(keyword in text for keyword in time_keywords) or re.search(r'\d{4}[-/年]\d{1,2}', text):
                    # 提取日期
                    for pattern in date_patterns:
                        matches = re.findall(pattern, text)
                        if matches:
                            publish_time = matches[0]
                            return publish_time
        except Exception:
            continue
    
    # 策略2: 从整个页面文本中提取日期
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                # 取第一个匹配的日期
                publish_time = matches[0]
                return publish_time
    except Exception:
        pass
    
    return publish_time[:20] if publish_time else ""


def extract_apply_link(driver, soup):
    """提取投递链接"""
    apply_link = ""
    
    # 投递关键词
    apply_keywords = ['投递', '申请', '立即投递', '立即申请', 'Apply', 'Submit', '投递简历', '申请职位']
    
    # 尝试多种选择器
    selectors = [
        "a[href*='apply']",
        "a[href*='投递']",
        "a[href*='申请']",
        "button[onclick*='apply']",
        "a[class*='apply']",
        "button[class*='apply']",
        "a[class*='投递']",
        "button[class*='投递']",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                href = elem.get_attribute("href") or elem.get_attribute("onclick") or ""
                # 检查是否包含投递关键词
                if any(keyword in text for keyword in apply_keywords) or any(keyword in href.lower() for keyword in ['apply', '投递', '申请']):
                    if href and href.startswith("http"):
                        apply_link = href
                        return apply_link
        except Exception:
            continue
    
    # 策略2: 查找包含"投递"文本的链接
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            text = link.text.strip()
            href = link.get_attribute("href") or ""
            if any(keyword in text for keyword in apply_keywords) and href.startswith("http"):
                apply_link = href
                return apply_link
    except Exception:
        pass
    
    # 策略3: 如果找不到，返回当前URL
    try:
        current_url = driver.current_url
        if current_url and current_url.startswith("http"):
            apply_link = current_url
    except Exception:
        pass
    
    return apply_link[:500] if apply_link else ""


def extract_company_type(driver, soup):
    """提取企业类型"""
    company_type = ""
    
    # 企业类型关键词
    type_keywords = {
        '央/国企': ['央/国企', '央国企', '央企', '国企', '国有企业', '中央企业'],
        '内资': ['内资', '民营企业', '民营'],
        '外资': ['外资', '外企', 'Foreign'],
        '合资': ['合资', '中外合资'],
        '上市公司': ['上市公司', '上市'],
    }
    
    # 尝试多种选择器
    selectors = [
        "[class*='type']",
        "[class*='类型']",
        "[class*='tag']",
        "[class*='label']",
        "[class*='badge']",
        ".tag, .label, .badge, .type",
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if not text or len(text) > 20:
                    continue
                # 检查是否包含企业类型关键词
                for type_name, keywords in type_keywords.items():
                    if any(keyword in text for keyword in keywords):
                        company_type = type_name
                        return company_type
        except Exception:
            continue
    
    # 策略2: 从页面文本中查找
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        for type_name, keywords in type_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                company_type = type_name
                return company_type
    except Exception:
        pass
    
    return company_type[:20] if company_type else ""


def extract_job_info_from_url(driver, url):
    """从URL提取招聘信息"""
    result = {
        "公司名称": "",
        "岗位": "",
        "企业类型": "",
        "发布时间": "",
        "Base地点": "",
        "投递链接": "",
        "原始链接": url,
    }
    
    try:
        print(f"   正在访问: {url[:60]}...")
        driver.get(url)
        random_sleep(2, 3)  # 等待页面加载
        
        # 获取页面源码
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取各项信息
        result["公司名称"] = extract_company_name(driver, soup)
        result["岗位"] = extract_job_title(driver, soup)
        result["企业类型"] = extract_company_type(driver, soup)
        result["发布时间"] = extract_publish_time(driver, soup)
        result["Base地点"] = extract_base_location(driver, soup)
        result["投递链接"] = extract_apply_link(driver, soup)
        
        # 如果投递链接为空，使用原始URL
        if not result["投递链接"]:
            result["投递链接"] = url
        
        print(f"   ✅ 提取完成: 公司={result['公司名称'] or '(空)'}, "
              f"岗位={result['岗位'] or '(空)'}, "
              f"地点={result['Base地点'] or '(空)'}")
        
    except TimeoutException:
        print(f"   ⚠️  页面加载超时")
    except Exception as e:
        print(f"   ❌ 提取失败: {e}")
        traceback.print_exc()
    
    return result


def read_excel_links(file_path, link_column):
    """读取Excel文件中的链接"""
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 检查列是否存在
        if link_column not in df.columns:
            print(f"❌ 错误: 找不到列 '{link_column}'")
            print(f"可用列: {', '.join(df.columns.tolist())}")
            return []
        
        # 提取链接（去除空值）
        links = df[link_column].dropna().tolist()
        # 过滤掉非URL的条目
        links = [link for link in links if isinstance(link, str) and (link.startswith("http://") or link.startswith("https://"))]
        
        print(f"✅ 从Excel读取到 {len(links)} 个有效链接")
        return links
        
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {e}")
        traceback.print_exc()
        return []


def save_results(results, file_path):
    """保存结果到Excel"""
    try:
        if results:
            df = pd.DataFrame(results)
            # 重新排列列的顺序
            columns_order = ["公司名称", "岗位", "企业类型", "发布时间", "Base地点", "投递链接", "原始链接"]
            # 只保留存在的列
            columns_order = [col for col in columns_order if col in df.columns]
            df = df[columns_order]
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"✅ 已保存 {len(results)} 条数据到: {file_path}")
            return True
        else:
            # 创建空文件
            df = pd.DataFrame(columns=["公司名称", "岗位", "企业类型", "发布时间", "Base地点", "投递链接", "原始链接"])
            df.to_excel(file_path, index=False, engine='openpyxl')
            print("⚠️  没有数据，已创建空文件")
            return False
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        traceback.print_exc()
        return False


def main():
    driver = None
    all_results = []
    
    try:
        print("=" * 60)
        print("招聘信息提取程序")
        print("=" * 60)
        
        # 读取Excel文件
        print(f"\n1. 读取Excel文件: {INPUT_FILE}")
        links = read_excel_links(INPUT_FILE, LINK_COLUMN)
        
        if not links:
            print("❌ 没有找到有效链接，程序退出")
            return
        
        # 启动浏览器
        print("\n2. 启动浏览器...")
        driver = create_driver()
        time.sleep(2)
        
        # 处理每个链接
        print(f"\n3. 开始处理 {len(links)} 个链接...")
        for idx, url in enumerate(links, 1):
            try:
                print(f"\n[{idx}/{len(links)}] 处理链接...")
                result = extract_job_info_from_url(driver, url)
                all_results.append(result)
                
                # 每10条保存一次（防止数据丢失）
                if len(all_results) % 10 == 0:
                    save_results(all_results, OUTPUT_FILE)
                    print(f"   💾 已保存 {len(all_results)} 条数据（定期保存）")
                
                # 防反爬等待
                random_sleep(2, 4)
                
            except InvalidSessionIdException as e:
                print(f"\n⚠️  浏览器会话断开: {e}")
                print("尝试保存已提取的数据...")
                save_results(all_results, OUTPUT_FILE)
                break
            except Exception as e:
                print(f"   ❌ 处理链接时出错: {e}")
                # 即使出错也保存一个空结果
                all_results.append({
                    "公司名称": "",
                    "岗位": "",
                    "企业类型": "",
                    "发布时间": "",
                    "Base地点": "",
                    "投递链接": "",
                    "原始链接": url,
                })
                traceback.print_exc()
                random_sleep(1, 2)
                continue
        
        # 最终保存
        print("\n4. 保存最终结果...")
        save_results(all_results, OUTPUT_FILE)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("提取完成！")
        print("=" * 60)
        print(f"共处理 {len(links)} 个链接")
        print(f"成功提取 {len([r for r in all_results if r['公司名称'] or r['岗位']])} 条有效数据")
        print(f"文件保存位置: {OUTPUT_FILE}")
        
        if all_results:
            print("\n前5条数据预览：")
            for i, item in enumerate(all_results[:5], 1):
                print(f"  {i}. 公司={item['公司名称'] or '(空)'}, "
                      f"岗位={item['岗位'] or '(空)'}, "
                      f"企业类型={item['企业类型'] or '(空)'}, "
                      f"发布时间={item['发布时间'] or '(空)'}, "
                      f"地点={item['Base地点'] or '(空)'}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
        save_results(all_results, OUTPUT_FILE)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        traceback.print_exc()
        save_results(all_results, OUTPUT_FILE)
    finally:
        if driver:
            try:
                print("\n关闭浏览器...")
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()

