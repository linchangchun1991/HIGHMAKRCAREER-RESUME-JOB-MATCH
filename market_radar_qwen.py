#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海马职加·市场雷达日报
基于 DrissionPage + 阿里通义千问 (Qwen) 的市场情报自动化系统

================================================================================
【重要】运行前必须操作：启动 Chrome 调试模式
================================================================================

小红书采集需要接管您本地已登录的 Chrome 浏览器，请先执行以下操作：

【Mac 系统】
在终端执行：
    open -n /Applications/Google\ Chrome.app --args --remote-debugging-port=9222

【Windows 系统】
在命令提示符（CMD）或 PowerShell 执行：
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

【Linux 系统】
在终端执行：
    google-chrome --remote-debugging-port=9222

执行后，Chrome 会以调试模式启动，然后：
1. 手动登录小红书账号（https://www.xiaohongshu.com）
2. 保持 Chrome 浏览器打开状态
3. 再运行本脚本

如果忘记启动调试模式，脚本会提示错误并退出。
================================================================================
"""

import json
import time
import random
import re
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from DrissionPage import ChromiumPage, ChromiumOptions
import dashscope
from dashscope import Generation
import logging

# 导入备用方案所需的库
try:
    import requests
    from bs4 import BeautifulSoup
    BING_BACKUP_AVAILABLE = True
except ImportError:
    BING_BACKUP_AVAILABLE = False
    logger.warning("requests 或 BeautifulSoup 未安装，Bing 备用方案不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_radar_qwen.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 硬编码配置 ====================
# 阿里通义千问 API Key
DASHSCOPE_API_KEY = "sk-668c28bae516493d9ea8a3662118ec98"

# 竞品关键词列表
KEYWORDS = ['DBC职梦', '途鸽求职', 'Offer先生', '爱思益', '海马职加']

# 时间范围（最近3天）
DAYS_BACK = 3
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")


class MarketRadarQwen:
    """市场雷达系统（基于 Qwen）"""
    
    def __init__(self, use_debug_port: bool = True):
        """
        初始化浏览器和 AI 客户端
        
        Args:
            use_debug_port: 是否使用调试端口连接已打开的 Chrome（用于小红书采集）
        """
        # 配置 DashScope
        dashscope.api_key = DASHSCOPE_API_KEY
        logger.info("阿里通义千问 (Qwen) 初始化成功")
        
        # 配置浏览器
        try:
            if use_debug_port:
                # 尝试连接本地 9222 端口的 Chrome（用于小红书采集）
                try:
                    self.page = ChromiumPage(addr='127.0.0.1:9222')
                    logger.info("成功连接到本地 Chrome 调试端口 (9222)")
                    logger.info("提示：请确保 Chrome 已以调试模式启动，并已登录小红书账号")
                except Exception as e:
                    logger.warning(f"连接本地 Chrome 调试端口失败: {str(e)}")
                    logger.warning("=" * 80)
                    logger.warning("【重要提示】请先启动 Chrome 调试模式：")
                    logger.warning("Mac: open -n /Applications/Google\\ Chrome.app --args --remote-debugging-port=9222")
                    logger.warning("Windows: \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port=9222")
                    logger.warning("=" * 80)
                    # 降级为普通模式
                    options = ChromiumOptions()
                    options.headless(False)
                    options.set_argument('--disable-blink-features=AutomationControlled')
                    self.page = ChromiumPage(addr_or_opts=options)
                    logger.info("已降级为普通浏览器模式（小红书采集可能受限）")
            else:
                # 普通模式
                options = ChromiumOptions()
                options.headless(False)
                options.set_argument('--disable-blink-features=AutomationControlled')
                self.page = ChromiumPage(addr_or_opts=options)
                logger.info("浏览器初始化成功（普通模式）")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            logger.error("提示：如果遇到连接错误，请先手动启动 Chrome 调试模式")
            self.page = None
        
        # 存储采集的数据
        self.douyin_data = []
        self.xhs_data = []
        self.wechat_data = []
        
        logger.info(f"市场雷达系统初始化完成，当前日期: {CURRENT_DATE}")
    
    def parse_time(self, time_str: str) -> Optional[datetime]:
        """
        解析时间字符串，返回 datetime 对象
        
        Args:
            time_str: 时间字符串，可能是"2小时前"、"昨天"、"2025-12-10"等格式
        
        Returns:
            datetime 对象，如果无法解析返回 None
        """
        if not time_str:
            return None
        
        time_str = time_str.strip()
        now = datetime.now()
        
        try:
            # 处理"X小时前"、"X分钟前"
            if "分钟前" in time_str:
                match = re.search(r'(\d+)分钟前', time_str)
                if match:
                    minutes = int(match.group(1))
                    return now - timedelta(minutes=minutes)
            
            if "小时前" in time_str:
                match = re.search(r'(\d+)小时前', time_str)
                if match:
                    hours = int(match.group(1))
                    return now - timedelta(hours=hours)
            
            # 处理"昨天"
            if "昨天" in time_str:
                return now - timedelta(days=1)
            
            # 处理"X天前"
            match = re.search(r'(\d+)天前', time_str)
            if match:
                days = int(match.group(1))
                return now - timedelta(days=days)
            
            # 处理标准日期格式 "2025-12-10"
            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', time_str)
            if date_match:
                year, month, day = map(int, date_match.groups())
                return datetime(year, month, day)
            
            # 处理"12-10"格式（假设是今年）
            date_match = re.search(r'(\d{1,2})-(\d{1,2})', time_str)
            if date_match:
                month, day = map(int, date_match.groups())
                return datetime(now.year, month, day)
            
            return None
            
        except Exception as e:
            logger.warning(f"时间解析失败: {time_str}, 错误: {str(e)}")
            return None
    
    def is_recent(self, time_str: str) -> bool:
        """
        判断时间字符串是否在最近3天内
        
        Args:
            time_str: 时间字符串
        
        Returns:
            是否在最近3天内
        """
        parsed_time = self.parse_time(time_str)
        if not parsed_time:
            return True  # 无法解析时默认保留
        
        three_days_ago = datetime.now() - timedelta(days=DAYS_BACK)
        return parsed_time >= three_days_ago
    
    def manual_login(self):
        """
        第一阶段：人工登录 (Blocking Wait)
        打开三个标签页，等待用户手动登录
        """
        if not self.page:
            raise RuntimeError("浏览器未初始化，无法执行登录")
        
        logger.info("=" * 80)
        logger.info("第一阶段：人工登录")
        logger.info("=" * 80)
        
        # 打开抖音标签页 (Tab 1)
        logger.info("正在打开抖音...")
        self.page.get('https://www.douyin.com')
        time.sleep(3)
        print("✅ 抖音标签页已打开")
        
        # 打开小红书标签页 (Tab 2)
        logger.info("正在打开小红书...")
        self.page.new_tab()
        time.sleep(1)
        self.page.get('https://www.xiaohongshu.com')
        time.sleep(3)
        print("✅ 小红书标签页已打开")
        
        # 打开搜狗微信标签页 (Tab 3)
        logger.info("正在打开搜狗微信...")
        self.page.new_tab()
        time.sleep(1)
        self.page.get('https://weixin.sogou.com')
        time.sleep(3)
        print("✅ 搜狗微信标签页已打开")
        
        # 等待用户手动登录
        print("\n" + "=" * 80)
        print("🔴 【重要】请手动完成以下操作：")
        print("")
        print("1️⃣  抖音：扫码或输入账号密码登录，确保能看到首页推荐内容")
        print("2️⃣  小红书：扫码或输入账号密码登录，确保能看到首页推荐内容")
        print("3️⃣  搜狗微信：如果出现验证码，请手动完成验证")
        print("")
        print("⚠️  请确保三个平台都已成功登录！")
        print("   登录完成后，请回到这里按【回车键】开始自动化采集...")
        print("=" * 80)
        
        # 阻塞等待用户按回车
        try:
            input("\n👉 确认已全部登录后，按回车键继续...")
        except EOFError:
            # 非交互式环境，等待60秒
            logger.warning("检测到非交互式环境，等待60秒后自动继续...")
            for i in range(60, 0, -10):
                print(f"⏳ 等待中... {i}秒后自动继续")
                time.sleep(10)
        
        logger.info("用户确认登录完成，开始执行采集")
        time.sleep(2)  # 额外等待2秒确保页面稳定
    
    def crawl_douyin(self) -> List[Dict[str, Any]]:
        """
        第二阶段：抖音采集（真人深潜模式）
        彻底重写：使用暴力文本提取，严禁使用 HTML
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 80)
        logger.info("第二阶段：抖音采集（真人深潜模式）")
        logger.info("=" * 80)
        
        results = []
        
        try:
            # 切换到抖音标签页
            self.page.get('https://www.douyin.com')
            time.sleep(3)
            
            for keyword in KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    print(f"[抖音深潜] 搜索关键词: {keyword}")
                    
                    # URL 注入策略：直接访问排序后的搜索结果
                    search_url = f"https://www.douyin.com/search/{keyword}?publish_time=1&sort_type=2&source=switch_tab&type=video"
                    self.page.get(search_url)
                    time.sleep(random.uniform(3, 5))
                    
                    logger.info(f"当前页面 URL: {self.page.url}")
                    print(f"[抖音深潜] 当前页面 URL: {self.page.url}")
                    
                    # 使用 XPath 查找所有视频链接
                    video_urls = []
                    try:
                        print("[抖音深潜] 使用 XPath 查找视频链接...")
                        links = self.page.eles('xpath://a[contains(@href, "/video/")]', timeout=10)
                        logger.info(f"XPath 找到 {len(links)} 个包含 /video/ 的链接")
                        print(f"[抖音深潜] XPath 找到 {len(links)} 个链接")
                        
                        for link in links:
                            try:
                                href = link.attr('href') or ''
                                link_text = link.text or ''
                                
                                # 过滤条件：链接文本长度 > 5
                                if '/video/' in href and len(link_text.strip()) > 5:
                                    # 处理相对链接
                                    if not href.startswith('http'):
                                        if href.startswith('//'):
                                            href = 'https:' + href
                                        elif href.startswith('/'):
                                            href = 'https://www.douyin.com' + href
                                        else:
                                            continue
                                    
                                    # 去重
                                    if href not in video_urls and 'douyin.com' in href:
                                        video_urls.append(href)
                                        print(f"[抖音深潜] ✓ 找到视频: {link_text[:30] if link_text else href[:50]}...")
                                        
                                        # 限制为前5个
                                        if len(video_urls) >= 5:
                                            break
                            except Exception as e:
                                logger.debug(f"  处理链接时出错: {str(e)}")
                                continue
                        
                        video_urls = video_urls[:5]
                        logger.info(f"找到 {len(video_urls)} 个视频链接")
                        print(f"[抖音深潜] 最终找到 {len(video_urls)} 个视频链接")
                        
                    except Exception as e:
                        logger.warning(f"提取视频链接失败: {str(e)}")
                        print(f"[抖音深潜] 提取失败: {str(e)}")
                        continue
                    
                    if not video_urls:
                        logger.warning(f"未找到任何视频，跳过关键词: {keyword}")
                        print(f"[抖音深潜] 未找到任何视频，跳过关键词: {keyword}")
                        continue
                    
                    # 循环采集：真人深潜模式
                    for idx, video_url in enumerate(video_urls, 1):
                        new_tab = None
                        try:
                            logger.info(f"  处理视频 {idx}/{len(video_urls)}: {video_url[:60]}...")
                            print(f"[抖音深潜] 正在深潜视频 {idx}/{len(video_urls)}: {video_url[:60]}...")
                            
                            # 打开新标签页
                            new_tab = self.page.new_tab()
                            new_tab.get(video_url)
                            
                            # 强制等待：必须等够时间
                            print(f"  [抖音深潜] 强制等待 3 秒，确保页面渲染...")
                            time.sleep(3)
                            
                            # 提取标题
                            title = ""
                            try:
                                title_elem = new_tab.ele('tag:h1', timeout=2)
                                if not title_elem:
                                    title_elem = new_tab.ele('tag:div@class*=title', timeout=2)
                                if title_elem:
                                    title = title_elem.text or ""
                                    print(f"  [抖音深潜] 提取到标题: {title[:50]}...")
                            except:
                                pass
                            
                            # 提取发布时间
                            date_str = ""
                            try:
                                date_selectors = ['tag:span@class*=time', 'tag:time', 'tag:div@class*=date']
                                for sel in date_selectors:
                                    try:
                                        date_elem = new_tab.ele(sel, timeout=1)
                                        if date_elem:
                                            date_str = date_elem.text or ""
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            # 时间过滤
                            if date_str and not self.is_recent(date_str):
                                logger.info(f"    视频超出3天范围，跳过: {date_str}")
                                print(f"  [抖音深潜] 视频超出3天范围，跳过: {date_str}")
                                new_tab.close()
                                continue
                            
                            # 滚动评论区（关键步骤）
                            print(f"  [抖音深潜] 滚动评论区加载内容...")
                            try:
                                new_tab.scroll.down(1000)
                                time.sleep(2)
                                new_tab.scroll.down(500)
                                time.sleep(1)
                            except Exception as e:
                                print(f"  [抖音深潜] 滚动失败: {str(e)}")
                            
                            # 文本提取（严禁使用 HTML）+ 二次清洗
                            print(f"  [抖音优化] 开始提取评论文本（严禁使用HTML）...")
                            comments = []
                            
                            # 尝试点击"展开更多评论"
                            try:
                                expand_btns = new_tab.eles('xpath://button[contains(text(), "展开") or contains(text(), "更多") or contains(@class, "expand")]', timeout=2)
                                for btn in expand_btns[:3]:  # 点击前3个展开按钮
                                    try:
                                        btn.click()
                                        time.sleep(1)
                                        print(f"  [抖音优化] ✓ 点击展开按钮")
                                    except:
                                        continue
                            except:
                                pass
                            
                            try:
                                # 策略1：尝试查找评论容器（使用 class*="comment" 或 data-e2e="comment"）
                                comment_selectors = [
                                    'xpath://div[contains(@class, "comment")]',
                                    'xpath://div[@data-e2e="comment"]',
                                    'xpath://div[contains(@class, "comment-item")]',
                                ]
                                
                                comment_items = []
                                for selector in comment_selectors:
                                    try:
                                        items = new_tab.eles(selector, timeout=3)
                                        if items:
                                            comment_items = items
                                            print(f"  [抖音优化] 使用选择器 '{selector}' 找到 {len(items)} 个评论元素")
                                            break
                                    except:
                                        continue
                                
                                # 从评论元素中提取文本
                                for item in comment_items[:30]:  # 检查前30个
                                    try:
                                        text = item.text or ""
                                        text = self._clean_html_text(text)  # 二次清洗HTML残留
                                        text = text.strip()
                                        
                                        # 过滤条件：长度 5-200，且不包含系统词
                                        if 5 <= len(text) <= 200:
                                            system_words = ['关注', '点赞', '收藏', '分享', '评论', '回复', '查看更多', '展开', '收起', '转发', '举报', '抖音', '记录美好生活']
                                            if not any(sys_word in text for sys_word in system_words):
                                                if text not in comments:
                                                    comments.append(text)
                                                    print(f"  [抖音优化] ✓ 找到评论: {text[:50]}...")
                                                    print(f"  [抖音优化]   原始文本前200字符: {text[:200]}")
                                                    if len(comments) >= 5:
                                                        break
                                    except:
                                        continue
                                
                            except Exception as e:
                                print(f"  [抖音优化] 策略1失败: {str(e)}")
                            
                            # 策略2：兜底策略 - 获取整个页面文本，二次清洗后过滤
                            if not comments:
                                print(f"  [抖音优化] 策略1未找到评论，使用兜底策略...")
                                try:
                                    body_elem = new_tab.ele('tag:body', timeout=2)
                                    if body_elem:
                                        full_text = body_elem.text or ""
                                        print(f"  [抖音优化] 页面文本总长度: {len(full_text)} 字符")
                                        
                                        # 按行分割，二次清洗，保留长度 5-200 的行
                                        lines = full_text.split('\n')
                                        for line in lines:
                                            line = self._clean_html_text(line)  # 二次清洗
                                            line = line.strip()
                                            
                                            if 5 <= len(line) <= 200:
                                                system_words = ['关注', '点赞', '收藏', '分享', '评论', '回复', '查看更多', '展开', '收起', '转发', '举报', '抖音', '记录美好生活']
                                                if not any(sys_word in line for sys_word in system_words):
                                                    # 检查是否像评论（包含常见评论关键词）
                                                    if any(kw in line for kw in ['说', '觉得', '真的', '太', '好', '差', '避雷', '坑', '退费', '骗局', '投诉', '不要', '千万别', '？', '！']):
                                                        if line not in comments:
                                                            comments.append(line)
                                                            print(f"  [抖音优化] ✓ 兜底找到评论: {line[:50]}...")
                                                            print(f"  [抖音优化]   原始文本前200字符: {line[:200]}")
                                                            if len(comments) >= 5:
                                                                break
                                except Exception as e:
                                    print(f"  [抖音优化] 兜底策略失败: {str(e)}")
                            
                            comments = comments[:5]  # 限制为前5条
                            print(f"  [抖音优化] 最终提取到 {len(comments)} 条评论")
                            
                            # 关闭标签页
                            try:
                                new_tab.close()
                            except:
                                pass
                            
                            if title or video_url:
                                result = {
                                    "platform": "抖音",
                                    "keyword": keyword,
                                    "title": title.strip() or f"视频 {idx}",
                                    "url": video_url,
                                    "date": date_str.strip(),
                                    "comments": comments,  # 纯文本列表
                                    "comment_count": len(comments)
                                }
                                results.append(result)
                                logger.info(f"  ✓ 采集成功: {title[:50] if title else '无标题'}... (评论: {len(comments)}条)")
                                print(f"[抖音深潜] ✓ 采集成功: {title[:50] if title else '无标题'}... (评论: {len(comments)}条)")
                            
                            time.sleep(random.uniform(1, 2))
                            
                        except Exception as e:
                            logger.warning(f"  处理视频 {idx} 失败: {str(e)}")
                            print(f"  [抖音深潜] 处理视频 {idx} 失败: {str(e)}")
                            # 确保关闭标签页
                            try:
                                if new_tab:
                                    new_tab.close()
                            except:
                                pass
                            continue
                    
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    print(f"[抖音深潜] 采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"抖音采集异常: {str(e)}", exc_info=True)
            print(f"[抖音深潜] 采集异常: {str(e)}")
        
        logger.info(f"抖音采集完成，共找到 {len(results)} 条有效数据")
        print(f"[抖音深潜] 采集完成，共找到 {len(results)} 条有效数据")
        self.douyin_data = results
        return results
    
    def _clean_html_text(self, text: str) -> str:
        """
        二次清洗HTML残留文本
        
        Args:
            text: 原始文本（可能包含HTML标签残留）
        
        Returns:
            清洗后的纯文本
        """
        if not text:
            return ""
        
        # 移除HTML标签残留
        text = re.sub(r'<[^>]+>', '', text)  # 移除 <tag> 标签
        text = re.sub(r'&[a-zA-Z]+;', '', text)  # 移除 &nbsp; 等实体
        text = re.sub(r'class\s*=\s*["\'][^"\']*["\']', '', text)  # 移除 class="xxx"
        text = re.sub(r'id\s*=\s*["\'][^"\']*["\']', '', text)  # 移除 id="xxx"
        text = re.sub(r'style\s*=\s*["\'][^"\']*["\']', '', text)  # 移除 style="xxx"
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_xhs_comments(self, page) -> List[str]:
        """
        提取小红书详情页的评论（文本块暴力提取法）
        
        Args:
            page: ChromiumPage 对象（详情页）
        
        Returns:
            评论列表
        """
        comments = []
        print("  [小红书评论提取] 开始提取评论...")
        
        try:
            # 等待页面加载
            time.sleep(3)
            print("  [小红书评论提取] 页面等待完成")
            
            # 尝试定位评论容器
            print("  [小红书评论提取] 尝试定位评论容器...")
            comment_container = None
            try:
                # 查找包含"评论"文本的 div
                comment_container = page.ele('xpath://div[contains(text(), "评论")]', timeout=3)
                if comment_container:
                    print("  [小红书评论提取] 找到评论容器（通过文本定位）")
            except:
                pass
            
            # 如果找不到，尝试 class 包含 comments
            if not comment_container:
                try:
                    comment_container = page.ele('xpath://div[contains(@class, "comment")]', timeout=2)
                    if comment_container:
                        print("  [小红书评论提取] 找到评论容器（通过 class 定位）")
                except:
                    pass
            
            # 暴力方案：直接获取页面文本块
            if not comment_container:
                print("  [小红书评论提取] 未找到特定容器，使用暴力文本提取法...")
                try:
                    # 获取页面所有 div
                    all_divs = page.eles('tag:div', timeout=3)
                    print(f"  [小红书评论提取] 找到 {len(all_divs)} 个 div 元素")
                    
                    system_words = ['关注', '点赞', '收藏', '分享', '评论', '回复', '查看更多', '展开', '收起']
                    
                    for div in all_divs:
                        try:
                            text = div.text or ""
                            text = text.strip()
                            
                            # 过滤条件：字数在 10-50 字，且不包含系统词
                            if 10 <= len(text) <= 50:
                                # 排除系统词
                                if not any(sys_word in text for sys_word in system_words):
                                    # 检查是否像评论（包含常见评论关键词）
                                    if any(kw in text for kw in ['说', '觉得', '真的', '太', '好', '差', '避雷', '坑', '退费', '骗局', '投诉', '不要', '千万别']):
                                        if text not in comments:
                                            comments.append(text)
                                            print(f"  [小红书评论提取] ✓ 找到评论: {text[:50]}...")
                                            if len(comments) >= 5:
                                                break
                        except:
                            continue
                    
                    print(f"  [小红书评论提取] 暴力提取完成，找到 {len(comments)} 条评论")
                    
                except Exception as e:
                    print(f"  [小红书评论提取] 暴力提取失败: {str(e)}")
            else:
                # 如果找到了评论容器，在容器内提取
                print("  [小红书评论提取] 在评论容器内提取...")
                try:
                    comment_items = comment_container.eles('tag:div', timeout=2)
                    print(f"  [小红书评论提取] 评论容器内找到 {len(comment_items)} 个子元素")
                    
                    for item in comment_items[:10]:
                        text = item.text or ""
                        text = text.strip()
                        if 10 <= len(text) <= 200 and text:
                            if text not in comments:
                                comments.append(text)
                                print(f"  [小红书评论提取] ✓ 找到评论: {text[:50]}...")
                                if len(comments) >= 5:
                                    break
                except Exception as e:
                    print(f"  [小红书评论提取] 容器内提取失败: {str(e)}")
            
            # 如果还是找不到，尝试正则提取页面 HTML
            if not comments:
                print("  [小红书评论提取] 尝试从 HTML 中正则提取...")
                try:
                    page_html = page.html or ""
                    # 查找"评论"关键字之后的文本
                    comment_match = re.search(r'评论[^<]*', page_html, re.IGNORECASE)
                    if comment_match:
                        comment_section = page_html[comment_match.start():comment_match.start()+500]
                        # 提取可能的评论文本
                        text_blocks = re.findall(r'>([^<>]{10,50})<', comment_section)
                        for block in text_blocks[:5]:
                            block = block.strip()
                            if block and len(block) >= 10:
                                comments.append(block)
                                print(f"  [小红书评论提取] ✓ 从HTML提取评论: {block[:50]}...")
                except Exception as e:
                    print(f"  [小红书评论提取] HTML 提取失败: {str(e)}")
            
            comments = comments[:5]
            print(f"  [小红书评论提取] 最终提取到 {len(comments)} 条评论")
            
        except Exception as e:
            print(f"  [小红书评论提取] 提取过程出错: {str(e)}")
        
        return comments
    
    def get_douyin_comments(self, page) -> List[str]:
        """
        提取抖音视频详情页的评论（侧边栏滚动法）
        
        Args:
            page: ChromiumPage 对象（视频详情页）
        
        Returns:
            评论列表
        """
        comments = []
        print("  [抖音评论提取] 开始提取评论...")
        
        try:
            # 等待页面加载
            time.sleep(3)
            print("  [抖音评论提取] 页面等待完成")
            
            # 定位评论区（通常在右侧侧边栏）
            print("  [抖音评论提取] 尝试定位评论区...")
            comment_container = None
            
            try:
                # 尝试多种方式定位评论区
                selectors = [
                    'xpath://div[contains(@class, "comment")]',
                    'xpath://div[contains(text(), "评论")]',
                    'xpath://div[@id*="comment"]',
                ]
                
                for selector in selectors:
                    try:
                        comment_container = page.ele(selector, timeout=2)
                        if comment_container:
                            print(f"  [抖音评论提取] 找到评论容器（使用: {selector}）")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"  [抖音评论提取] 定位评论容器失败: {str(e)}")
            
            # 如果找到评论容器，移动鼠标并滚动
            if comment_container:
                try:
                    print("  [抖音评论提取] 移动鼠标到评论区...")
                    comment_container.scroll.to_see()
                    time.sleep(1)
                    
                    print("  [抖音评论提取] 向下滚动加载评论...")
                    page.scroll.down(500)
                    time.sleep(2)
                    page.scroll.down(500)
                    time.sleep(2)
                    print("  [抖音评论提取] 滚动完成")
                except Exception as e:
                    print(f"  [抖音评论提取] 滚动操作失败: {str(e)}")
            else:
                # 如果找不到，直接滚动页面
                print("  [抖音评论提取] 未找到评论容器，直接滚动页面...")
                try:
                    page.scroll.to_bottom()
                    time.sleep(2)
                    page.scroll.up(300)
                    time.sleep(1)
                except:
                    pass
            
            # 提取评论文本
            print("  [抖音评论提取] 开始提取评论文本...")
            try:
                # 尝试查找评论元素
                comment_selectors = [
                    'tag:p',
                    'tag:span',
                    'tag:div',
                ]
                
                for selector in comment_selectors:
                    try:
                        elems = page.eles(selector, timeout=3)
                        print(f"  [抖音评论提取] 使用 {selector} 找到 {len(elems)} 个元素")
                        
                        for elem in elems[:100]:  # 检查前100个元素
                            try:
                                text = elem.text or ""
                                text = text.strip()
                                
                                # 过滤条件：长度在 5-200 字，且不包含系统词
                                if 5 <= len(text) <= 200:
                                    system_words = ['关注', '点赞', '收藏', '分享', '评论', '回复', '查看更多', '展开', '收起', '转发']
                                    if not any(sys_word in text for sys_word in system_words):
                                        # 检查是否像评论（包含常见评论关键词或表情）
                                        if any(kw in text for kw in ['说', '觉得', '真的', '太', '好', '差', '避雷', '坑', '退费', '骗局', '投诉', '不要', '千万别']) or 'emoji' in str(type(elem)):
                                            if text not in comments:
                                                comments.append(text)
                                                print(f"  [抖音评论提取] ✓ 找到评论: {text[:50]}...")
                                                if len(comments) >= 5:
                                                    break
                            except:
                                continue
                        
                        if comments:
                            break
                    except:
                        continue
                
                print(f"  [抖音评论提取] 提取完成，找到 {len(comments)} 条评论")
                
            except Exception as e:
                print(f"  [抖音评论提取] 提取评论文本失败: {str(e)}")
            
            # 如果还是找不到，尝试从页面文本中提取
            if not comments:
                print("  [抖音评论提取] 尝试从页面文本中提取...")
                try:
                    page_text = page.html or ""
                    # 查找可能的评论模式
                    comment_patterns = [
                        r'([^<>]{10,100}(?:说|觉得|真的|太|好|差|避雷|坑|退费)[^<>]{0,50})',
                    ]
                    
                    for pattern in comment_patterns:
                        matches = re.findall(pattern, page_text)
                        for match in matches[:5]:
                            match = match.strip()
                            if match and 10 <= len(match) <= 200:
                                comments.append(match)
                                print(f"  [抖音评论提取] ✓ 从文本提取评论: {match[:50]}...")
                except Exception as e:
                    print(f"  [抖音评论提取] 文本提取失败: {str(e)}")
            
            comments = comments[:5]
            print(f"  [抖音评论提取] 最终提取到 {len(comments)} 条评论")
            
        except Exception as e:
            print(f"  [抖音评论提取] 提取过程出错: {str(e)}")
        
        return comments
    
    def fetch_from_bing(self, keyword: str) -> List[Dict[str, Any]]:
        """
        备用方案：从 Bing 搜索获取小红书内容
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            包含标题、链接、来源的字典列表
        """
        if not BING_BACKUP_AVAILABLE:
            logger.warning("Bing 备用方案不可用（缺少 requests 或 BeautifulSoup）")
            return []
        
        results = []
        try:
            logger.info(f"[Bing备用] 搜索关键词: {keyword}")
            
            # 构造搜索词：site:xiaohongshu.com {keyword} after:2023-10-01
            search_query = f"site:xiaohongshu.com {keyword}"
            bing_url = f"https://www.bing.com/search?q={search_query}&count=10"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(bing_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找搜索结果
            search_results = soup.find_all('li', class_='b_algo')[:10]
            
            for result in search_results:
                try:
                    # 提取标题
                    title_elem = result.find('h2')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 提取链接
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    
                    # 提取摘要
                    snippet_elem = result.find('p')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # 只保留小红书链接
                    if 'xiaohongshu.com' in url:
                        results.append({
                            "platform": "小红书",
                            "keyword": keyword,
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "date": "",
                            "has_negative": False,
                            "comments": [],
                            "comment_count": 0
                        })
                        logger.info(f"  [Bing备用] ✓ 找到: {title[:50]}...")
                        
                except Exception as e:
                    logger.debug(f"  处理 Bing 结果失败: {str(e)}")
                    continue
            
            logger.info(f"[Bing备用] 共找到 {len(results)} 条结果")
            
        except Exception as e:
            logger.warning(f"Bing 备用方案失败: {str(e)}")
        
        return results
    
    def crawl_xhs(self) -> List[Dict[str, Any]]:
        """
        第二阶段：小红书采集（列表页抓取 - 不进入详情页）
        
        核心策略：
        1. 使用 DrissionPage 接管已登录的 Chrome 浏览器（端口 9222）
        2. 只抓取列表页能看到的标题、链接、作者名
        3. 不进入详情页，避免被风控屏蔽
        4. 如果列表页获取失败，使用 Bing 搜索作为备用方案
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 80)
        logger.info("第二阶段：小红书采集（列表页抓取模式）")
        logger.info("=" * 80)
        
        results = []
        
        try:
            for keyword in KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    print(f"[小红书列表页] 搜索关键词: {keyword}")
                    
                    # 访问小红书搜索结果页
                    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
                    self.page.get(search_url)
                    
                    logger.info(f"当前页面 URL: {self.page.url}")
                    print(f"[小红书列表页] 当前页面 URL: {self.page.url}")
                    
                    # Smart Wait: 等待页面元素加载（检测 .note-item 是否出现）
                    print("[小红书列表页] Smart Wait: 等待笔记卡片加载...")
                    note_items = []
                    max_wait_time = 10  # 最多等待10秒
                    wait_interval = 1
                    waited_time = 0
                    
                    while waited_time < max_wait_time:
                        try:
                            # 尝试多种选择器查找笔记卡片
                            selectors = [
                                'css:.note-item',
                                'css:.feed-item',
                                'css:[class*="note"]',
                                'css:[class*="feed"]',
                                'xpath://div[contains(@class, "note")]',
                                'xpath://div[contains(@class, "feed")]',
                            ]
                            
                            for selector in selectors:
                                try:
                                    items = self.page.eles(selector, timeout=1)
                                    if items:
                                        note_items = items
                                        print(f"  [小红书列表页] ✓ 找到 {len(items)} 个笔记卡片（使用: {selector}）")
                                        break
                                except:
                                    continue
                            
                            if note_items:
                                break
                            
                            time.sleep(wait_interval)
                            waited_time += wait_interval
                            print(f"  [小红书列表页] 等待中... ({waited_time}/{max_wait_time}秒)")
                            
                        except Exception as e:
                            logger.debug(f"  Smart Wait 检测失败: {str(e)}")
                            time.sleep(wait_interval)
                            waited_time += wait_interval
                    
                    if not note_items:
                        logger.warning(f"未找到笔记卡片，尝试滚动加载...")
                        print("[小红书列表页] 未找到笔记卡片，尝试滚动加载...")
                    
                    # Scroll: 模拟鼠标滚轮向下滚动页面 3-5 次（每次间隔 2 秒）
                    scroll_count = random.randint(3, 5)
                    print(f"[小红书列表页] 开始滚动加载（{scroll_count} 次）...")
                    for scroll_idx in range(scroll_count):
                        try:
                            self.page.scroll.down(800)
                            time.sleep(2)
                            print(f"  [小红书列表页] 滚动 {scroll_idx + 1}/{scroll_count} 完成")
                            
                            # 滚动后再次尝试查找笔记卡片
                            if not note_items:
                                try:
                                    items = self.page.eles('css:.note-item', timeout=2)
                                    if items:
                                        note_items = items
                                        print(f"  [小红书列表页] ✓ 滚动后找到 {len(items)} 个笔记卡片")
                                except:
                                    pass
                        except Exception as e:
                            print(f"  [小红书列表页] 滚动失败: {str(e)}")
                    
                    # Data Extraction: 从列表页提取数据（不进入详情页）
                    print("[小红书列表页] 开始提取列表页数据...")
                    keyword_results = []
                    
                    if note_items:
                        print(f"[小红书列表页] 找到 {len(note_items)} 个笔记卡片，开始提取...")
                        
                        for idx, card in enumerate(note_items[:10], 1):  # 最多处理10个
                            try:
                                # 提取标题
                                title = ""
                                try:
                                    # 尝试多种方式提取标题
                                    title_selectors = [
                                        'tag:h2',
                                        'tag:h3',
                                        'tag:a',
                                        'tag:div@class*=title',
                                        'tag:span@class*=title',
                                    ]
                                    
                                    for sel in title_selectors:
                                        try:
                                            title_elem = card.ele(sel, timeout=1)
                                            if title_elem:
                                                title = title_elem.text or ""
                                                if title:
                                                    break
                                        except:
                                            continue
                                except:
                                    pass
                                
                                # 提取链接
                                url = ""
                                try:
                                    link_elem = card.ele('tag:a', timeout=1)
                                    if link_elem:
                                        href = link_elem.attr('href') or ''
                                        
                                        # 处理相对链接
                                        if href:
                                            if not href.startswith('http'):
                                                if href.startswith('//'):
                                                    href = 'https:' + href
                                                elif href.startswith('/'):
                                                    href = 'https://www.xiaohongshu.com' + href
                                                else:
                                                    continue
                                            
                                            if 'explore' in href and 'xiaohongshu.com' in href:
                                                url = href
                                except:
                                    pass
                                
                                # 提取作者名
                                author = ""
                                try:
                                    author_selectors = [
                                        'tag:span@class*=author',
                                        'tag:div@class*=author',
                                        'tag:a@class*=user',
                                    ]
                                    
                                    for sel in author_selectors:
                                        try:
                                            author_elem = card.ele(sel, timeout=1)
                                            if author_elem:
                                                author = author_elem.text or ""
                                                if author:
                                                    break
                                        except:
                                            continue
                                except:
                                    pass
                                
                                # 提取封面文字（如果有）
                                snippet = ""
                                try:
                                    desc_elem = card.ele('tag:div@class*=desc', timeout=1)
                                    if desc_elem:
                                        snippet = desc_elem.text or ""
                                except:
                                    pass
                                
                                # 只保存有标题或链接的数据
                                if title or url:
                                    # 检查是否包含负面关键词
                                    negative_keywords = ['避雷', '坑', '退费', '骗局', '投诉', '差评', '垃圾', '不要', '千万别', '吵架']
                                    has_negative = any(kw in (title + snippet) for kw in negative_keywords)
                                    
                                    result = {
                                        "platform": "小红书",
                                        "keyword": keyword,
                                        "title": title.strip() or f"笔记 {idx}",
                                        "url": url,
                                        "date": "",  # 列表页通常没有发布时间
                                        "snippet": snippet.strip(),
                                        "author": author.strip(),  # 新增作者字段
                                        "has_negative": has_negative,
                                        "comments": [],  # 列表页不抓取评论
                                        "comment_count": 0
                                    }
                                    
                                    keyword_results.append(result)
                                    logger.info(f"  ✓ 提取成功: {title[:50] if title else '无标题'}... (作者: {author[:20] if author else '未知'})")
                                    print(f"[小红书列表页] ✓ 提取成功: {title[:50] if title else '无标题'}... (作者: {author[:20] if author else '未知'})")
                                    
                                    if len(keyword_results) >= 5:
                                        break
                                    
                            except Exception as e:
                                logger.debug(f"  处理笔记卡片 {idx} 失败: {str(e)}")
                                continue
                    
                    # 如果列表页获取失败，使用 Bing 备用方案
                    if not keyword_results:
                        logger.warning(f"列表页未获取到数据，启用 Bing 备用方案...")
                        print(f"[小红书列表页] 列表页未获取到数据，启用 Bing 备用方案...")
                        keyword_results = self.fetch_from_bing(keyword)
                    
                    results.extend(keyword_results)
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    print(f"[小红书列表页] 采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"小红书采集异常: {str(e)}", exc_info=True)
            print(f"[小红书列表页] 采集异常: {str(e)}")
        
        logger.info(f"小红书采集完成，共找到 {len(results)} 条有效数据")
        print(f"[小红书列表页] 采集完成，共找到 {len(results)} 条有效数据")
        self.xhs_data = results
        return results
    
    def crawl_wechat(self) -> List[Dict[str, Any]]:
        """
        第二阶段：搜狗微信采集
        抓取文章标题、摘要、时间（无需进入详情页）
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 80)
        logger.info("第二阶段：搜狗微信采集")
        logger.info("=" * 80)
        
        results = []
        
        try:
            # 切换到搜狗微信标签页
            self.page.get('https://weixin.sogou.com')
            time.sleep(3)
            
            for keyword in KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    
                    # 访问搜索结果页
                    search_url = f"https://weixin.sogou.com/weixin?type=2&query={keyword}"
                    self.page.get(search_url)
                    time.sleep(random.uniform(3, 5))
                    
                    # 调试信息：打印当前页面状态
                    logger.info(f"当前页面 URL: {self.page.url}")
                    
                    # 处理可能的验证码
                    try:
                        verify_img = self.page.ele('tag:img@id=seccodeImage', timeout=2)
                        if verify_img:
                            logger.warning("⚠️ 检测到验证码，请手动完成验证后按回车继续...")
                            try:
                                input("验证完成后按回车继续...")
                            except EOFError:
                                time.sleep(10)
                    except:
                        pass
                    
                    # 提取文章列表（前5条）- 使用 class="txt-box" 策略
                    txt_boxes = []
                    try:
                        # 新逻辑：直接查找包含 class="txt-box" 的 div 元素
                        txt_boxes = self.page.eles('tag:div@class=txt-box', timeout=5)
                        logger.info(f"页面中共找到 {len(txt_boxes)} 个 txt-box 元素")
                        
                        # 如果找不到，尝试部分匹配
                        if not txt_boxes:
                            txt_boxes = self.page.eles('tag:div@class*=txt-box', timeout=5)
                            logger.info(f"使用部分匹配找到 {len(txt_boxes)} 个 txt-box 元素")
                        
                        # 限制为前5个
                        txt_boxes = txt_boxes[:5]
                        
                        # 如果未找到，打印调试信息
                        if not txt_boxes:
                            logger.warning(f"⚠️ 警告：未找到 txt-box 元素")
                            try:
                                page_html_preview = self.page.html[:500] if hasattr(self.page, 'html') else "无法获取HTML"
                                logger.warning(f"页面前500字符预览: {page_html_preview}")
                            except:
                                logger.warning("无法获取页面HTML预览")
                        
                    except Exception as e:
                        logger.warning(f"提取文章列表失败: {str(e)}")
                        # 打印调试信息
                        try:
                            page_html_preview = self.page.html[:500] if hasattr(self.page, 'html') else "无法获取HTML"
                            logger.warning(f"错误时页面前500字符预览: {page_html_preview}")
                        except:
                            pass
                        continue
                    
                    if not txt_boxes:
                        logger.warning(f"未找到任何文章，跳过关键词: {keyword}")
                        continue
                    
                    # 提取文章信息
                    for idx, txt_box in enumerate(txt_boxes, 1):
                        try:
                            # 在 txt-box 下查找 h3 a 获取标题和链接
                            title = ""
                            url = ""
                            
                            try:
                                # 查找 h3 下的 a 标签
                                h3_elem = txt_box.ele('tag:h3', timeout=1)
                                if h3_elem:
                                    link_elem = h3_elem.ele('tag:a', timeout=1)
                                    if link_elem:
                                        url = link_elem.attr('href') or ""
                                        title = link_elem.text or ""
                                    
                                    # 如果 h3 下没有 a，直接取 h3 文本
                                    if not title:
                                        title = h3_elem.text or ""
                            except Exception as e:
                                logger.debug(f"    提取标题失败: {str(e)}")
                            
                            # 处理链接
                            if url and not url.startswith('http'):
                                if url.startswith('//'):
                                    url = 'https:' + url
                                elif url.startswith('/'):
                                    url = 'https://weixin.sogou.com' + url
                            
                            # 在 txt-box 下查找 p 获取摘要
                            snippet = ""
                            try:
                                p_elem = txt_box.ele('tag:p', timeout=1)
                                if p_elem:
                                    snippet = p_elem.text or ""
                            except:
                                pass
                            
                            # 提取发布时间（通常在 txt-box 同级或父级）
                            date_str = ""
                            try:
                                # 尝试在 txt-box 内查找时间
                                date_elem = txt_box.ele('tag:span@class*=time', timeout=1)
                                if not date_elem:
                                    date_elem = txt_box.ele('tag:span', timeout=1)
                                if date_elem:
                                    date_text = date_elem.text or ""
                                    # 检查是否包含日期格式
                                    if any(kw in date_text for kw in ['-', '年', '月', '日', '前', '小时', '分钟']):
                                        date_str = date_text
                            except:
                                pass
                            
                            # 时间过滤：只保留3天内
                            if date_str and not self.is_recent(date_str):
                                logger.info(f"    文章超出3天范围，跳过: {date_str}")
                                continue
                            
                            if title or url:
                                result = {
                                    "platform": "搜狗微信",
                                    "keyword": keyword,
                                    "title": title.strip() or f"文章 {idx}",
                                    "url": url or "",
                                    "date": date_str.strip(),
                                    "snippet": snippet.strip(),
                                    "comments": [],  # 微信文章不抓评论
                                    "comment_count": 0
                                }
                                results.append(result)
                                logger.info(f"  ✓ 采集成功: {title[:50] if title else '无标题'}...")
                            
                        except Exception as e:
                            logger.warning(f"  处理文章 {idx} 失败: {str(e)}")
                            continue
                    
                    time.sleep(random.uniform(2, 3))
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"搜狗微信采集异常: {str(e)}", exc_info=True)
        
        logger.info(f"搜狗微信采集完成，共找到 {len(results)} 条有效数据")
        self.wechat_data = results
        return results
    
    def save_raw_data(self):
        """保存原始数据到 CSV"""
        all_data = self.douyin_data + self.xhs_data + self.wechat_data
        
        if not all_data:
            logger.warning("没有数据可保存")
            return
        
        # 转换为 DataFrame
        df_data = []
        for item in all_data:
            row = {
                "平台": item.get("platform", ""),
                "关键词": item.get("keyword", ""),
                "标题": item.get("title", ""),
                "链接": item.get("url", ""),
                "发布时间": item.get("date", ""),
                "摘要": item.get("snippet", ""),
                "作者": item.get("author", ""),  # 新增作者字段（小红书）
                "包含负面": item.get("has_negative", False),
                "评论数": item.get("comment_count", 0),
                "评论内容": "\n".join(item.get("comments", []))
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv('raw_data.csv', index=False, encoding='utf-8-sig')
        logger.info(f"原始数据已保存到: raw_data.csv (共 {len(df_data)} 条)")
    
    def format_data_for_ai(self, data_list: List[Dict[str, Any]]) -> str:
        """
        将数据格式化为 AI 易读的文本格式
        
        Args:
            data_list: 数据列表
        
        Returns:
            格式化后的文本字符串
        """
        if not data_list:
            return "（暂无数据）"
        
        context = ""
        negative_keywords = ['避雷', '坑', '退费', '骗局', '投诉', '差评', '垃圾', '不要', '千万别', '吵架']
        
        # 优先处理包含负面关键词的数据
        priority_data = []
        normal_data = []
        
        for item in data_list:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            has_negative = item.get('has_negative', False)
            
            if has_negative or any(kw in (title + snippet) for kw in negative_keywords):
                priority_data.append(item)
            else:
                normal_data.append(item)
        
        # 合并：优先数据在前
        sorted_data = priority_data + normal_data
        
        # 截断保护：如果数据太多，只取前50条
        if len(sorted_data) > 50:
            sorted_data = sorted_data[:50]
            logger.warning(f"数据量过大，截取前50条最重要的数据")
        
        for item in sorted_data:
            platform = item.get('platform', '未知平台')
            # 特别标注小红书，因为这里黑料最多
            if platform == '小红书':
                icon = "📕"
            elif platform == '抖音':
                icon = "🎵"
            elif platform == '搜狗微信':
                icon = "🟢"
            else:
                icon = "📄"
            
            context += f"【平台：{icon} {platform}】\n"
            context += f"关键词：{item.get('keyword', '')}\n"
            context += f"标题：{item.get('title', '无标题')}\n"
            context += f"链接：{item.get('url', '')}\n"
            
            # 添加摘要（如果有）
            snippet = item.get('snippet', '')
            if snippet:
                context += f"摘要：{snippet[:200]}\n"
            
            # 重点：如果有评论，必须全部拼进去，这是销售回怼的关键
            comments = item.get('comments', [])
            if comments:
                comments_text = "\n".join([f"  - {c}" for c in comments if c])
                context += f"🔥 用户高赞吐槽：\n{comments_text}\n"
            
            # 标记是否包含负面
            if item.get('has_negative', False):
                context += "⚠️ 包含负面关键词\n"
            
            context += "-------------------\n"
        
        # 检查总长度，如果超过5000字，截取
        if len(context) > 5000:
            logger.warning(f"格式化数据过长 ({len(context)} 字符)，截取前5000字符")
            context = context[:5000] + "\n...（数据已截断）"
        
        return context
    
    def load_data_from_csv(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        从 CSV 文件加载数据（数据源双重保障）
        
        Returns:
            包含 douyin_data, xhs_data, wechat_data 的字典
        """
        try:
            if not os.path.exists('raw_data.csv'):
                logger.warning("raw_data.csv 文件不存在")
                return {"douyin_data": [], "xhs_data": [], "wechat_data": []}
            
            df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
            logger.info(f"从 CSV 加载数据，共 {len(df)} 条")
            
            douyin_data = []
            xhs_data = []
            wechat_data = []
            
            for _, row in df.iterrows():
                platform = row.get('平台', '')
                comments_text = row.get('评论内容', '')
                comments = [c.strip() for c in comments_text.split('\n') if c.strip()] if comments_text else []
                
                item = {
                    "platform": platform,
                    "keyword": row.get('关键词', ''),
                    "title": row.get('标题', ''),
                    "url": row.get('链接', ''),
                    "date": row.get('发布时间', ''),
                    "snippet": row.get('摘要', ''),
                    "has_negative": row.get('包含负面', False) if isinstance(row.get('包含负面'), bool) else False,
                    "comments": comments,
                    "comment_count": len(comments)
                }
                
                if platform == '抖音':
                    douyin_data.append(item)
                elif platform == '小红书':
                    xhs_data.append(item)
                elif platform == '搜狗微信':
                    wechat_data.append(item)
            
            logger.info(f"CSV 数据加载完成：抖音 {len(douyin_data)} 条，小红书 {len(xhs_data)} 条，搜狗微信 {len(wechat_data)} 条")
            return {
                "douyin_data": douyin_data,
                "xhs_data": xhs_data,
                "wechat_data": wechat_data
            }
            
        except Exception as e:
            logger.error(f"从 CSV 加载数据失败: {str(e)}")
            return {"douyin_data": [], "xhs_data": [], "wechat_data": []}
    
    def generate_report(self) -> str:
        """
        第三阶段：阿里千问 (Qwen) 销冠分析
        调用 dashscope.Generation.call 生成报告
        """
        logger.info("=" * 80)
        logger.info("第三阶段：阿里千问 (Qwen) 销冠分析")
        logger.info("=" * 80)
        
        # 数据源双重保障：如果内存数据为空，从 CSV 读取
        douyin_data = self.douyin_data
        xhs_data = self.xhs_data
        wechat_data = self.wechat_data
        
        if not douyin_data and not xhs_data and not wechat_data:
            logger.warning("内存数据为空，尝试从 CSV 文件加载...")
            csv_data = self.load_data_from_csv()
            douyin_data = csv_data.get('douyin_data', [])
            xhs_data = csv_data.get('xhs_data', [])
            wechat_data = csv_data.get('wechat_data', [])
            logger.info(f"从 CSV 加载后：抖音 {len(douyin_data)} 条，小红书 {len(xhs_data)} 条，搜狗微信 {len(wechat_data)} 条")
        
        # 合并所有数据
        all_data_list = douyin_data + xhs_data + wechat_data
        
        if not all_data_list:
            logger.warning("所有数据源都为空，无法生成报告")
            return f"""# 海马职加·市场雷达日报

**生成时间**: {CURRENT_DATE}

## ⚠️ 数据采集结果

- 抖音数据: 0 条
- 小红书数据: 0 条
- 搜狗微信数据: 0 条

*注：未采集到任何数据，请检查采集逻辑或网络连接。*
"""
        
        # 格式化数据
        formatted_data = self.format_data_for_ai(all_data_list)
        
        # 调试打印
        logger.info(f"正在发送给 AI 的数据长度: {len(formatted_data)} 字符")
        logger.info(f"数据统计：抖音 {len(douyin_data)} 条，小红书 {len(xhs_data)} 条，搜狗微信 {len(wechat_data)} 条")
        
        system_prompt = """你不是销售，你是海马职加的**首席战略官 (CSO)**。
你拥有敏锐的市场洞察力。请根据采集到的全网数据（抖音/小红书/微信），为管理层撰写一份《全网市场雷达日报》。

**分析逻辑与输出格式 (Markdown)**：

**第一部分：⚔️ 竞品动作监测 (Competitor Moves)**
- 核心关注：竞品（DBC、途鸽、Offer先生等）最近发了什么新产品？搞了什么活动？有什么价格变动？
- 格式：`[平台] 竞品名：具体动作`。

**第二部分：📢 用户舆情透视 (Voice of Customer)**
- 核心关注：用户在评论区骂什么？痛点在哪里？
- **必须摘录**：从数据中提取 3-5 条最具代表性的**负面评论原话**，作为"用户原声"展示。
- 总结：当前的舆情热词是什么（如：退费难、导师水）。

**第三部分：🧭 我们的战略启示 (Strategic Insights)**
- **这是最重要的部分**。基于上述竞品动作和用户舆情，给我们（海马职加）提出 3 条具体的战略建议。
- *不要写话术*，要写策略。
- 例如：'竞品A因为退费难被骂 -> 启示：我们应在宣发中强调资金监管和透明退费流程，建立信任壁垒。'

**风格要求**：
- 语言简练、专业、毒辣。
- 拒绝废话，直击本质。
- **建议必须基于今日抓取的具体数据，严禁生成通用建议。**"""

        user_prompt = f"""以下是今日采集到的最新竞品情报数据（最近3天）：

{formatted_data}

请根据以上数据生成《全网市场雷达日报》，格式为 Markdown。
每条情报必须包含原始链接，严禁编造信息。
**特别注意**：
1. 如果数据中包含用户评论，必须摘录原话展示。
2. 战略建议必须基于上述具体数据，不能写通用建议。
3. 如果数据中没有评论，请明确说明"本次未采集到用户评论数据"。
4. 优先分析小红书平台的负面评价，因为通常最真实。"""

        try:
            logger.info("调用阿里千问 (qwen-plus) API 生成报告...")
            
            # 使用 dashscope.Generation.call
            response = Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                result_format='message'
            )
            
            if response.status_code == 200:
                report = response.output.choices[0].message.content
                
                # 添加标题和日期
                full_report = f"# 海马职加·市场雷达日报\n\n**生成时间**: {CURRENT_DATE}\n\n---\n\n{report}"
                
                logger.info("阿里千问 报告生成完成")
                return full_report
            else:
                raise Exception(f"API 调用失败: {response.status_code}, {response.message}")
            
        except Exception as e:
            logger.error(f"阿里千问 生成失败: {str(e)}")
            # 如果生成失败，返回基础报告
            return f"""# 海马职加·市场雷达日报

**生成时间**: {CURRENT_DATE}

## 数据统计

- 抖音数据: {len(douyin_data)} 条
- 小红书数据: {len(xhs_data)} 条
- 搜狗微信数据: {len(wechat_data)} 条

*注：AI 分析失败，请查看 raw_data.csv 获取原始数据。*
"""
    
    def run(self, skip_login: bool = False):
        """
        执行完整的采集流程
        
        Args:
            skip_login: 是否跳过登录步骤（假设已登录）
        """
        logger.info("=" * 80)
        logger.info("海马职加·市场雷达日报 - 开始运行")
        logger.info("=" * 80)
        
        try:
            if not skip_login:
                # 第一阶段：人工登录
                self.manual_login()
            else:
                logger.info("跳过登录步骤，假设浏览器已登录")
                # 打开三个标签页（如果还没有）
                try:
                    tabs = self.page.tab_ids
                    if len(tabs) == 0:
                        self.page.get('https://www.douyin.com')
                        time.sleep(2)
                        self.page.new_tab()
                        self.page.get('https://www.xiaohongshu.com')
                        time.sleep(2)
                        self.page.new_tab()
                        self.page.get('https://weixin.sogou.com')
                        time.sleep(2)
                except:
                    pass
            
            # 第二阶段：多平台采集
            self.crawl_douyin()
            self.crawl_xhs()
            self.crawl_wechat()
            
            # 保存原始数据
            self.save_raw_data()
            
            # 第三阶段：生成报告
            report = self.generate_report()
            
            # 保存报告
            report_file = f"Market_Radar_{CURRENT_DATE}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"报告已保存到: {report_file}")
            
            print(f"\n✅ 采集完成！")
            print(f"📊 数据统计：抖音 {len(self.douyin_data)} 条，小红书 {len(self.xhs_data)} 条，搜狗微信 {len(self.wechat_data)} 条")
            print(f"📄 原始数据：raw_data.csv")
            print(f"📋 分析报告：{report_file}")
            
            logger.info("=" * 80)
            logger.info("市场雷达日报生成完成")
            logger.info("=" * 80)
            
            # 发送到钉钉群
            self.send_to_dingtalk(report)
            
        except Exception as e:
            logger.error(f"运行异常: {str(e)}", exc_info=True)
            raise
        finally:
            # 不自动关闭浏览器，让用户查看结果
            logger.info("浏览器保持打开状态，请手动关闭")
    
    def send_to_dingtalk(self, report_content: str):
        """
        发送报告到钉钉群（确保所有链接完整）
        
        Args:
            report_content: 报告内容（Markdown格式）
        """
        try:
            import requests
            
            # 钉钉Webhook地址
            DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=ac8d1c6332c8a047b8786a930ab08d7f6db490843edca2de1bb65c68301c3113"
            
            # 读取原始数据，补充链接信息
            try:
                if os.path.exists('raw_data.csv'):
                    df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
                    
                    # 构建链接补充信息
                    links_section = "\n\n---\n\n## 📎 完整原文链接清单\n\n"
                    
                    # 按平台分组
                    for platform in ['抖音', '小红书', '搜狗微信']:
                        platform_data = df[df['平台'] == platform]
                        if len(platform_data) > 0:
                            links_section += f"### {platform}平台\n\n"
                            for _, row in platform_data.head(10).iterrows():
                                title = str(row.get('标题', ''))[:60]
                                url = str(row.get('链接', ''))
                                keyword = str(row.get('关键词', ''))
                                
                                if url and url != 'nan' and url.strip():
                                    links_section += f"- **{keyword}** - {title}  🔗 [查看原文]({url})\n"
                            links_section += "\n"
                    
                    # 将链接补充信息添加到报告末尾
                    report_content = report_content.rstrip() + links_section
            except Exception as e:
                logger.warning(f"补充链接信息失败: {str(e)}")
            
            # 发送到钉钉
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "海马职加·市场雷达日报",
                    "text": report_content
                }
            }
            
            logger.info("正在发送报告到钉钉群...")
            response = requests.post(DINGTALK_WEBHOOK, json=payload, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info("✓ 钉钉消息发送成功")
                print("✓ 报告已发送到钉钉群")
            else:
                logger.warning(f"✗ 钉钉消息发送失败: {result.get('errmsg')}")
                print(f"✗ 钉钉消息发送失败: {result.get('errmsg')}")
                
        except ImportError:
            logger.warning("requests 库未安装，跳过钉钉推送")
            print("⚠  requests 库未安装，跳过钉钉推送")
        except Exception as e:
            logger.error(f"发送钉钉消息失败: {str(e)}")
            print(f"✗ 发送钉钉消息失败: {str(e)}")


def main():
    """主函数"""
    import sys
    # 如果命令行参数包含 --skip-login，则跳过登录步骤
    skip_login = '--skip-login' in sys.argv or '--skip' in sys.argv
    
    radar = MarketRadarQwen()
    radar.run(skip_login=skip_login)


if __name__ == "__main__":
    main()
