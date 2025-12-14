import time
import random
import traceback
import re

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

# 配置
START_URL = "https://material.zhiyeli.cn/recruit"
MAX_PAGE = 1  # 先只抓一页测试
OUTPUT_FILE = "/Users/changchun/Desktop/最新学员需求投递表格.xlsx"


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


def random_sleep(min_sec=2, max_sec=3):
    """防反爬：随机等待"""
    time.sleep(random.uniform(min_sec, max_sec))


def wait_for_apply_buttons(driver, timeout=15):
    """等待并查找所有'立即投递'按钮"""
    print("正在查找'立即投递'按钮...")
    
    # 等待页面加载
    time.sleep(3)
    
    # 多种策略查找按钮
    strategies = [
        # 策略1: 精确匹配"立即投递"
        (By.XPATH, "//a[contains(text(), '立即投递')] | //button[contains(text(), '立即投递')] | //span[contains(text(), '立即投递')] | //div[contains(text(), '立即投递')]"),
        # 策略2: 模糊匹配"投递"
        (By.XPATH, "//a[contains(text(), '投递')] | //button[contains(text(), '投递')] | //span[contains(text(), '投递')] | //div[contains(text(), '投递')]"),
        # 策略3: 通过class查找
        (By.CSS_SELECTOR, "a[class*='apply'], button[class*='apply'], a[class*='deliver'], button[class*='deliver']"),
    ]
    
    for strategy_type, strategy_value in strategies:
        try:
            if strategy_type == By.XPATH:
                buttons = driver.find_elements(strategy_type, strategy_value)
            else:
                buttons = driver.find_elements(strategy_type, strategy_value)
            
            # 过滤出真正包含"立即投递"或"投递"文本的按钮
            filtered_buttons = []
            for btn in buttons:
                try:
                    text = btn.text.strip()
                    if "立即投递" in text or "投递" in text:
                        filtered_buttons.append(btn)
                except Exception:
                    pass
            
            if filtered_buttons:
                print(f"✅ 找到 {len(filtered_buttons)} 个'立即投递'按钮（使用策略: {strategy_type}）")
                return filtered_buttons
        except Exception as e:
            continue
    
    print("❌ 未找到'立即投递'按钮")
    return []


def extract_card_info(card_element, driver, button):
    """从卡片元素中提取完整信息：公司名、岗位、企业类型、发布时间、Base地点"""
    company_name = ""
    job_title = ""
    company_type = ""
    publish_time = ""
    base_location = ""
    
    try:
        # 获取整个卡片的HTML和文本，用于调试
        card_html = card_element.get_attribute('outerHTML')
        card_text = card_element.text
        lines = [line.strip() for line in card_text.split('\n') if line.strip()]
        
        # 策略1: 提取日期（通常在卡片顶部，红色显示，格式如 2025-12-05）
        # 先尝试通过元素查找日期
        date_selectors = [
            ".//*[contains(@class, 'date')]",
            ".//*[contains(@class, 'time')]",
            ".//*[contains(@style, 'red')]",
            ".//*[contains(@style, 'color:')]",
            ".//span[contains(@style, 'red')]",
            ".//div[contains(@style, 'red')]",
        ]
        
        for selector in date_selectors:
            try:
                date_elems = card_element.find_elements(By.XPATH, selector)
                for elem in date_elems:
                    text = elem.text.strip()
                    # 检查是否是日期格式
                    if re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$', text):
                        publish_time = text
                        break
                if publish_time:
                    break
            except Exception:
                continue
        
        # 如果元素查找失败，从文本中提取日期
        if not publish_time:
            date_patterns = [
                r'(\d{4}-\d{1,2}-\d{1,2})',  # 2025-12-05
                r'(\d{4}/\d{1,2}/\d{1,2})',  # 2025/12/05
                r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2025年12月5日
            ]
            for pattern in date_patterns:
                matches = re.findall(pattern, card_text)
                if matches:
                    publish_time = matches[0].strip()
                    break
        
        # 策略2: 提取公司名称和岗位标题
        # 根据页面结构，标题通常在特定的元素中
        title_selectors = [
            ".//*[contains(@class, 'title')]",
            ".//*[contains(@class, 'job-title')]",
            ".//*[contains(@class, 'company-name')]",
            ".//*[contains(@class, 'name')]",
            ".//h1",
            ".//h2",
            ".//h3",
            ".//h4",
            ".//*[contains(@class, 'card-title')]",
        ]
        
        full_title = ""
        for selector in title_selectors:
            try:
                title_elem = card_element.find_element(By.XPATH, selector)
                full_title = title_elem.text.strip()
                if full_title and len(full_title) > 5:
                    break
            except Exception:
                continue
        
        # 如果没找到标题元素，从文本行中查找
        if not full_title:
            # 查找最长的文本行（通常是标题）
            for line in lines:
                if len(line) > 20 and any(kw in line for kw in ['公司', '企业', '集团', '招聘', '校招', '岗位']):
                    full_title = line
                    break
        
        # 分离公司名和岗位
        if full_title:
            # 如果包含"招聘"，通常格式是：公司名 + "招聘" + 岗位信息
            if '招聘' in full_title:
                parts = full_title.split('招聘', 1)
                company_name = parts[0].strip()
                if len(parts) > 1:
                    job_title = parts[1].strip()
            # 如果包含"校招"、"秋招"、"春招"等
            elif any(kw in full_title for kw in ['校招', '秋招', '春招', '实习']):
                # 尝试找到公司名（招聘类型前面的部分）
                for kw in ['校招', '秋招', '春招', '实习']:
                    if kw in full_title:
                        idx = full_title.find(kw)
                        potential_company = full_title[:idx].strip()
                        if len(potential_company) > 2:
                            company_name = potential_company
                        job_title = full_title[idx:].strip()
                        break
            else:
                # 如果都不包含，尝试智能分离
                # 查找公司关键词的位置
                company_keywords = ['公司', '企业', '集团', '股份', '有限', '银行', '保险', '证券', '科技', '技术']
                for kw in company_keywords:
                    if kw in full_title:
                        idx = full_title.find(kw)
                        # 公司名通常是关键词及其前面的部分
                        potential_company = full_title[:idx + len(kw)].strip()
                        if len(potential_company) > 2 and len(potential_company) < 50:
                            company_name = potential_company
                            # 剩余部分作为岗位
                            if idx + len(kw) < len(full_title):
                                job_title = full_title[idx + len(kw):].strip()
                        break
        
        # 策略3: 提取企业类型和地点（从标签元素中）
        company_type_keywords = ['央/国企', '央国企', '国企', '央企', '内资', '外资', '合资', '民营', '上市公司']
        location_keywords = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '江苏', '浙江', '广东', '山东', '河南', '四川', '湖北', '陕西', '安徽', '湖南', '重庆', '天津', '青岛', '苏州', '无锡', '宁波', '厦门', '福州', '济南', '郑州', '长沙', '合肥', '南昌', '石家庄', '太原', '沈阳', '大连', '长春', '哈尔滨', '昆明', '贵阳', '南宁', '海口', '乌鲁木齐', '拉萨', '银川', '西宁']
        
        # 查找所有可能的标签/徽章元素
        tag_selectors = [
            ".//span",
            ".//div[contains(@class, 'tag')]",
            ".//span[contains(@class, 'tag')]",
            ".//*[contains(@class, 'badge')]",
            ".//*[contains(@class, 'label')]",
        ]
        
        all_tags = []
        for selector in tag_selectors:
            try:
                tags = card_element.find_elements(By.XPATH, selector)
                for tag in tags:
                    text = tag.text.strip()
                    if text and len(text) < 30:
                        all_tags.append(text)
            except Exception:
                continue
        
        # 从标签中提取企业类型和地点
        for tag_text in all_tags:
            # 检查是否是企业类型
            if not company_type:
                for keyword in company_type_keywords:
                    if keyword in tag_text:
                        company_type = tag_text
                        break
            
            # 检查是否是地点
            if not base_location:
                for keyword in location_keywords:
                    if keyword in tag_text and len(tag_text) <= len(keyword) + 2:
                        base_location = tag_text
                        break
        
        # 策略4: 从文本行中提取企业类型和地点（如果元素查找失败）
        if not company_type or not base_location:
            for line in lines:
                # 检查企业类型
                if not company_type:
                    for keyword in company_type_keywords:
                        if keyword in line and len(line) < 30:
                            company_type = line
                            break
                
                # 检查地点
                if not base_location:
                    for keyword in location_keywords:
                        if keyword in line and len(line) < 20:
                            base_location = line
                            break
        
        # 清理和验证
        # 公司名：去除明显不是公司名的内容
        if company_name:
            # 如果公司名太短或包含明显错误，清空
            if len(company_name) < 2 or company_name.lower() in ['mp', 'www', 'career', 'campus', 'wx', 'rsc', 'rsj', 'cfit']:
                company_name = ""
            else:
                company_name = company_name[:50]
        
        # 岗位：去除明显不是岗位的内容
        if job_title:
            if job_title.lower() in ['职位描述', '岗位列表', '门户', '官网', '平台', '人才']:
                job_title = ""
            else:
                job_title = job_title[:100]
        
        # 企业类型和地点：限制长度
        company_type = company_type[:20] if company_type else ""
        publish_time = publish_time[:20] if publish_time else ""
        base_location = base_location[:20] if base_location else ""
                
    except Exception as e:
        print(f"   提取卡片信息时出错: {e}")
        import traceback
        traceback.print_exc()
    
    return company_name, job_title, company_type, publish_time, base_location


def click_apply_button(driver, button):
    """点击'立即投递'按钮"""
    try:
        # 先尝试普通点击
        button.click()
        return True
    except (ElementClickInterceptedException, StaleElementReferenceException):
        try:
            # 如果普通点击失败，使用JS点击
            driver.execute_script("arguments[0].click();", button)
            return True
        except Exception:
            return False
    except Exception:
        return False


def get_real_url_from_new_window(driver, original_window, timeout=15):
    """等待新窗口打开，获取URL，然后关闭新窗口"""
    try:
        # 等待新窗口出现
        WebDriverWait(driver, timeout).until(lambda d: len(d.window_handles) > 1)
        
        # 找到新窗口
        new_window = None
        for handle in driver.window_handles:
            if handle != original_window:
                new_window = handle
                break
        
        if not new_window:
            return None
        
        # 切换到新窗口
        driver.switch_to.window(new_window)
        time.sleep(2)  # 等待页面加载
        
        # 获取URL
        real_url = driver.current_url
        
        # 关闭新窗口
        driver.close()
        
        # 切回原窗口
        driver.switch_to.window(original_window)
        
        return real_url
        
    except TimeoutException:
        print("等待新窗口超时")
        try:
            driver.switch_to.window(original_window)
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"获取新窗口URL时出错: {e}")
        try:
            driver.switch_to.window(original_window)
        except Exception:
            pass
        return None


def save_data(all_data, file_path):
    """保存数据到Excel"""
    try:
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"✅ 已保存 {len(all_data)} 条数据到: {file_path}")
            return True
        else:
            # 创建空文件
            df = pd.DataFrame(columns=["公司名称", "岗位", "企业类型", "发布时间", "Base地点", "真实投递链接", "所在页码"])
            df.to_excel(file_path, index=False, engine='openpyxl')
            print("⚠️  没有数据，已创建空文件")
            return False
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        traceback.print_exc()
        return False


def main():
    driver = None
    all_data = []
    
    try:
        print("=" * 60)
        print("开始抓取招聘信息（测试模式：只抓第1页）")
        print("=" * 60)
        
        # 启动浏览器
        print("\n1. 启动浏览器...")
        driver = create_driver()
        time.sleep(2)
        
        # 打开目标网站
        print(f"2. 打开目标网站: {START_URL}")
        current_url = driver.current_url
        
        if current_url.startswith("data:") or current_url == "about:blank":
            print("检测到空白页面，正在导航...")
            driver.get(START_URL)
        else:
            driver.get(START_URL)
        
        time.sleep(5)
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        
        # 等待用户登录
        print("\n3. 等待用户操作...")
        try:
            input("\n请在浏览器中完成以下操作：\n"
                  "  1. 扫码登录\n"
                  "  2. 切换到【招聘信息-校招信息-网申开启】列表页\n"
                  "  3. 确认页面上有'立即投递'按钮\n"
                  "然后按回车继续...\n")
        except EOFError:
            print("\n检测到非交互式环境，等待 60 秒...")
            time.sleep(60)
        
        # 查找按钮
        print("\n4. 查找'立即投递'按钮...")
        apply_buttons = wait_for_apply_buttons(driver, timeout=20)
        
        if not apply_buttons:
            print("❌ 未找到'立即投递'按钮，程序退出")
            print("请确认：")
            print("  1. 已经登录成功")
            print("  2. 已经在【招聘信息-校招信息-网申开启】列表页")
            print("  3. 页面上确实有'立即投递'按钮")
            return
        
        buttons_count = len(apply_buttons)
        print(f"✅ 找到 {buttons_count} 个'立即投递'按钮，开始抓取...\n")
        
        # 抓取数据
        print("5. 开始抓取数据...")
        original_window = driver.current_window_handle
        
        for idx, apply_btn in enumerate(apply_buttons, 1):
            try:
                print(f"\n处理第 {idx}/{buttons_count} 个按钮...")
                
                # 获取卡片信息（向上查找父元素）
                card = apply_btn
                try:
                    # 向上查找3层父元素，找到卡片容器
                    for i in range(3):
                        card = card.find_element(By.XPATH, "./..")
                        if card:
                            break
                except Exception:
                    pass
                
                # 提取完整信息
                company_name, job_title, company_type, publish_time, base_location = extract_card_info(card, driver, apply_btn)
                print(f"   公司: {company_name or '(未提取到)'}")
                print(f"   岗位: {job_title or '(未提取到)'}")
                print(f"   企业类型: {company_type or '(未提取到)'}")
                print(f"   发布时间: {publish_time or '(未提取到)'}")
                print(f"   Base地点: {base_location or '(未提取到)'}")
                
                # 点击按钮
                print("   点击'立即投递'按钮...")
                success = click_apply_button(driver, apply_btn)
                
                if not success:
                    print("   ❌ 点击失败，跳过")
                    continue
                
                # 获取真实URL
                print("   等待新窗口打开...")
                real_url = get_real_url_from_new_window(driver, original_window, timeout=15)
                
                if not real_url:
                    print("   ❌ 未获取到真实链接，跳过")
                    continue
                
                print(f"   ✅ 成功获取链接: {real_url[:60]}...")
                
                # 保存数据
                all_data.append({
                    "公司名称": company_name,
                    "岗位": job_title,
                    "企业类型": company_type,
                    "发布时间": publish_time,
                    "Base地点": base_location,
                    "真实投递链接": real_url,
                    "所在页码": 1,
                })
                
                # 每5条保存一次
                if len(all_data) % 5 == 0:
                    save_data(all_data, OUTPUT_FILE)
                    print(f"   💾 已保存 {len(all_data)} 条数据（定期保存）")
                
                # 防反爬等待
                random_sleep()
                
            except InvalidSessionIdException as e:
                print(f"\n⚠️  浏览器会话断开: {e}")
                print("尝试保存已抓取的数据...")
                save_data(all_data, OUTPUT_FILE)
                break
            except Exception as e:
                print(f"   ❌ 处理第 {idx} 个按钮时出错: {e}")
                traceback.print_exc()
                try:
                    driver.switch_to.window(original_window)
                except Exception:
                    pass
                random_sleep()
                continue
        
        # 最终保存
        print("\n6. 保存最终数据...")
        save_data(all_data, OUTPUT_FILE)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("抓取完成！")
        print("=" * 60)
        print(f"共抓取到 {len(all_data)} 条数据")
        print(f"文件保存位置: {OUTPUT_FILE}")
        
        if all_data:
            print("\n前5条数据预览：")
            for i, item in enumerate(all_data[:5], 1):
                print(f"  {i}. 公司={item['公司名称'] or '(空)'}, "
                      f"岗位={item['岗位'] or '(空)'}, "
                      f"企业类型={item['企业类型'] or '(空)'}, "
                      f"发布时间={item['发布时间'] or '(空)'}, "
                      f"地点={item['Base地点'] or '(空)'}, "
                      f"URL={item['真实投递链接'][:50]}...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
        save_data(all_data, OUTPUT_FILE)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        traceback.print_exc()
        save_data(all_data, OUTPUT_FILE)
    finally:
        if driver:
            try:
                print("\n浏览器将保持打开状态，你可以手动关闭")
                # driver.quit()  # 如果需要自动关闭，取消注释
            except Exception:
                pass


if __name__ == "__main__":
    main()
