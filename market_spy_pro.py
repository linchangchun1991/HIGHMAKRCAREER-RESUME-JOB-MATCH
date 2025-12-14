#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海马职加·市场雷达日报
基于 DrissionPage 的自动化情报系统
支持：抖音、小红书、微信公众号
"""

import json
import time
import re
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from openai import OpenAI
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_spy_pro.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 硬编码配置 ====================
# 阿里千问（通义千问）API 配置
QWEN_API_KEY = "sk-668c28bae516493d9ea8a3662118ec98"
# 尝试多个可能的 endpoint
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 国内版
# QWEN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"  # 国际版
QWEN_MODEL = "qwen-plus"  # 或使用 "qwen-turbo" 更快但质量稍低

# 竞品关键词列表（扩展版）
COMPETITOR_KEYWORDS = [
    'DBC职梦', 
    '途鸽求职', 
    'Offer先生', 
    '爱思益', 
    '留学生求职',
    '留学生实习',
    '英国留学生实习',
    '美国留学生实习',
    '澳洲留学生实习',
    '美国留学生求职',
    '英国留学生求职',
    '澳洲留学生求职'
]

# 负面关键词（用于筛选高价值内容）
NEGATIVE_KEYWORDS = ['避雷', '坑', '退费', '骗局', '投诉', '差评', '垃圾', '不要', '千万别', '吵架']

# 时间范围（最近3天）
DAYS_BACK = 3
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")


class MarketSpyPro:
    """市场雷达专业版"""
    
    def __init__(self):
        """初始化浏览器和 AI 客户端"""
        # 配置阿里千问（通义千问）
        self.ai_client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL
        )
        logger.info("阿里千问（通义千问）初始化成功")
        
        # 配置浏览器
        options = ChromiumOptions()
        options.headless(False)  # 显示浏览器窗口
        options.set_argument('--disable-blink-features=AutomationControlled')
        
        try:
            self.page = ChromiumPage(addr_or_opts=options)
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.warning(f"浏览器初始化失败: {str(e)}")
            logger.warning("提示：如果遇到连接错误，请先手动启动 Chrome 调试模式")
            self.page = None
        
        # 存储采集的数据
        self.douyin_data = []
        self.xhs_data = []
        self.wechat_data = []
        
        logger.info(f"市场雷达专业版初始化完成，当前日期: {CURRENT_DATE}")
    
    def is_recent(self, date_str: str) -> bool:
        """
        判断日期字符串是否在最近3天内
        
        Args:
            date_str: 日期字符串，可能是"2小时前"、"昨天"、"2025-12-10"等格式
        
        Returns:
            是否在最近3天内
        """
        if not date_str:
            return False
        
        date_str = date_str.strip()
        now = datetime.now()
        three_days_ago = now - timedelta(days=DAYS_BACK)
        
        try:
            # 处理"X小时前"、"X分钟前"
            if "小时前" in date_str or "分钟前" in date_str:
                return True  # 假设是最近的
            
            # 处理"昨天"
            if "昨天" in date_str:
                return True
            
            # 处理"X天前"
            match = re.search(r'(\d+)天前', date_str)
            if match:
                days = int(match.group(1))
                return days <= DAYS_BACK
            
            # 处理标准日期格式 "2025-12-10"
            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
            if date_match:
                year, month, day = map(int, date_match.groups())
                post_date = datetime(year, month, day)
                return post_date >= three_days_ago
            
            # 处理"12-10"格式（假设是今年）
            date_match = re.search(r'(\d{1,2})-(\d{1,2})', date_str)
            if date_match:
                month, day = map(int, date_match.groups())
                post_date = datetime(now.year, month, day)
                return post_date >= three_days_ago
            
            # 如果无法解析，默认返回 True（保守策略）
            logger.warning(f"无法解析日期格式: {date_str}，默认保留")
            return True
            
        except Exception as e:
            logger.warning(f"日期解析失败: {date_str}, 错误: {str(e)}")
            return True  # 保守策略：无法判断时保留
    
    def manual_login(self):
        """
        第一阶段：人工登录 (三平台热启动)
        打开抖音、小红书、微信公众号三个标签页，等待用户手动登录
        """
        if not self.page:
            raise RuntimeError("浏览器未初始化，无法执行登录")
        
        logger.info("=" * 60)
        logger.info("第一阶段：人工登录")
        logger.info("=" * 60)
        
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
        
        # 打开微信公众号搜索页 (Tab 3)
        logger.info("正在打开微信公众号搜索页...")
        self.page.new_tab()
        time.sleep(1)
        self.page.get('https://weixin.sogou.com/')
        time.sleep(3)
        print("✅ 微信公众号搜索页已打开")
        
        # 等待用户手动登录
        print("\n" + "=" * 80)
        print("🔴 【重要】请在浏览器中手动完成以下操作：")
        print("")
        print("1️⃣  抖音：扫码或输入账号密码登录，确保能看到首页推荐内容")
        print("2️⃣  小红书：扫码或输入账号密码登录，确保能看到首页推荐内容")
        print("3️⃣  微信公众号：如果出现验证码，请手动完成验证")
        print("")
        print("⚠️  请确保三个平台都已成功登录！")
        print("   登录完成后，请回到这里按【回车键】继续采集...")
        print("=" * 80)
        
        # 阻塞等待用户按回车
        try:
            input("\n👉 确认已全部登录后，按回车键继续...")
        except EOFError:
            # 非交互式环境，等待60秒
            logger.warning("检测到非交互式环境，等待60秒后自动继续...")
            for i in range(60, 0, -10):
                print(f"⏳ 等待中... {i}秒后自动继续（如果已登录，程序会自动开始采集）")
                time.sleep(10)
        
        logger.info("用户确认登录完成，开始执行采集")
        time.sleep(2)  # 额外等待2秒确保页面稳定
    
    def crawl_douyin(self) -> List[Dict[str, Any]]:
        """
        第二阶段：抖音采集逻辑
        
        Returns:
            抖音数据列表
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 60)
        logger.info("第二阶段：抖音采集")
        logger.info("=" * 60)
        
        results = []
        
        try:
            # 切换到抖音标签页（第一个标签）
            self.page.get('https://www.douyin.com')
            time.sleep(3)
            
            for keyword in COMPETITOR_KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    
                    # 查找搜索框
                    search_input = None
                    selectors = [
                        'tag:input@placeholder*=搜索',
                        'tag:input@class*=search',
                        'tag:input@type=text',
                    ]
                    
                    for selector in selectors:
                        try:
                            search_input = self.page.ele(selector, timeout=3)
                            if search_input:
                                break
                        except:
                            continue
                    
                    if not search_input:
                        logger.warning(f"未找到搜索框，跳过关键词: {keyword}")
                        continue
                    
                    # 输入关键词
                    search_input.clear()
                    search_input.input(keyword)
                    time.sleep(1)
                    
                    # 点击搜索按钮或按回车
                    search_btn = self.page.ele('tag:button@class*=search', timeout=2)
                    if search_btn:
                        search_btn.click()
                    else:
                        search_input.input('\n')
                    
                    time.sleep(5)  # 等待搜索结果加载
                    
                    # 尝试点击"最新"排序
                    try:
                        latest_btn = self.page.ele('text:最新', timeout=3)
                        if latest_btn:
                            latest_btn.click()
                            time.sleep(3)
                            logger.info("已切换到'最新'排序")
                    except:
                        logger.info("未找到'最新'排序按钮，使用默认排序")
                    
                    time.sleep(3)  # 再次等待页面加载
                    
                    # 提取视频列表
                    videos = []
                    selectors = [
                        'tag:a@href*=/video/',
                        'tag:div@class*=video-item',
                        'tag:div@class*=video',
                    ]
                    
                    for selector in selectors:
                        try:
                            videos = self.page.eles(selector, timeout=5)
                            if videos and len(videos) > 0:
                                logger.info(f"使用选择器 '{selector}' 找到 {len(videos)} 个视频")
                                break
                        except:
                            continue
                    
                    # 如果还是找不到，尝试通过链接特征查找
                    if not videos:
                        try:
                            all_links = self.page.eles('tag:a', timeout=5)
                            video_links = [link for link in all_links if '/video/' in (link.attr('href') or '')]
                            if video_links:
                                videos = video_links[:10]
                                logger.info(f"通过链接特征找到 {len(videos)} 个视频")
                        except Exception as e:
                            logger.warning(f"通过链接查找失败: {str(e)}")
                    
                    # 限制为前10条
                    videos = videos[:10]
                    
                    if not videos:
                        logger.warning(f"未找到任何视频，当前页面URL: {self.page.url}")
                        continue
                    
                    for idx, video in enumerate(videos, 1):
                        try:
                            # 提取标题和链接
                            title = ""
                            url = ""
                            
                            try:
                                if hasattr(video, 'tag') and video.tag == 'a':
                                    title = video.text or ""
                                    url = video.attr('href') or ""
                                else:
                                    link_elem = video.ele('tag:a', timeout=1)
                                    if link_elem:
                                        url = link_elem.attr('href') or ""
                                        title = link_elem.text or ""
                                    
                                    if not title:
                                        for tag in ['tag:span', 'tag:p', 'tag:div', 'tag:h3']:
                                            try:
                                                title_elem = video.ele(tag, timeout=0.5)
                                                if title_elem and title_elem.text:
                                                    title = title_elem.text
                                                    break
                                            except:
                                                continue
                            except Exception as e:
                                logger.warning(f"提取视频信息失败: {str(e)}")
                                continue
                            
                            if url and not url.startswith('http'):
                                url = 'https://www.douyin.com' + url
                            
                            # 提取发布时间
                            date_str = ""
                            try:
                                date_selectors = ['tag:span', 'tag:time', 'tag:div']
                                for sel in date_selectors:
                                    try:
                                        elems = video.eles(sel, timeout=0.5)
                                        for elem in elems:
                                            text = elem.text or ""
                                            if any(kw in text for kw in ['前', '天', '小时', '分钟', '昨天', '今天']):
                                                date_str = text
                                                break
                                        if date_str:
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            # 时间过滤：只保留3天内
                            if not self.is_recent(date_str):
                                logger.info(f"  视频 {idx} 超出3天范围，跳过: {title[:30] if title else '无标题'}...")
                                continue
                            
                            if not title or not url:
                                continue
                            
                            # 点击进入视频详情页获取评论（前5条高赞）
                            comments = []
                            try:
                                click_link = video if hasattr(video, 'tag') and video.tag == 'a' else video.ele('tag:a', timeout=1)
                                if click_link:
                                    click_link.click()
                                    time.sleep(3)  # 等待详情页加载
                                    
                                    # 提取评论（前5条高赞）
                                    comment_selectors = [
                                        'tag:div@class*=comment-item',
                                        'tag:div@class*=comment',
                                        'tag:li@class*=comment',
                                    ]
                                    
                                    for selector in comment_selectors:
                                        try:
                                            comment_elems = self.page.eles(selector, timeout=2)
                                            if comment_elems:
                                                for comment_elem in comment_elems[:5]:
                                                    comment_text = comment_elem.text
                                                    if comment_text:
                                                        comments.append(comment_text)
                                                break
                                        except:
                                            continue
                                    
                                    # 返回列表页
                                    self.page.back()
                                    time.sleep(2)
                            except Exception as e:
                                logger.warning(f"获取评论失败: {str(e)}")
                            
                            result = {
                                "platform": "抖音",
                                "keyword": keyword,
                                "title": title.strip(),
                                "url": url.strip(),
                                "date": date_str.strip(),
                                "comments": comments,
                                "comment_count": len(comments)
                            }
                            results.append(result)
                            logger.info(f"  ✓ 采集视频 {idx}: {title[:50]}... (评论: {len(comments)}条)")
                            
                        except Exception as e:
                            logger.warning(f"处理视频 {idx} 失败: {str(e)}")
                            continue
                    
                    time.sleep(2)  # 避免请求过快
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"抖音采集异常: {str(e)}", exc_info=True)
        
        logger.info(f"抖音采集完成，共找到 {len(results)} 条有效数据")
        self.douyin_data = results
        return results
    
    def crawl_xhs(self) -> List[Dict[str, Any]]:
        """
        第三阶段：小红书采集逻辑
        
        Returns:
            小红书数据列表
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 60)
        logger.info("第三阶段：小红书采集")
        logger.info("=" * 60)
        
        results = []
        
        try:
            # 切换到小红书标签页
            self.page.get('https://www.xiaohongshu.com')
            time.sleep(3)
            
            for keyword in COMPETITOR_KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    
                    # 查找搜索框
                    search_input = None
                    selectors = [
                        'tag:input@placeholder*=搜索',
                        'tag:input@class*=search',
                        'tag:input@type=text',
                    ]
                    
                    for selector in selectors:
                        try:
                            search_input = self.page.ele(selector, timeout=3)
                            if search_input:
                                break
                        except:
                            continue
                    
                    if not search_input:
                        logger.warning(f"未找到搜索框，跳过关键词: {keyword}")
                        continue
                    
                    # 输入关键词
                    search_input.clear()
                    search_input.input(keyword)
                    time.sleep(1)
                    
                    # 点击搜索
                    search_btn = self.page.ele('tag:button@class*=search', timeout=2)
                    if search_btn:
                        search_btn.click()
                    else:
                        search_input.input('\n')
                    
                    time.sleep(5)  # 等待搜索结果加载
                    
                    # 尝试点击"最新"排序
                    try:
                        latest_btn = self.page.ele('text:最新', timeout=3)
                        if latest_btn:
                            latest_btn.click()
                            time.sleep(3)
                            logger.info("已切换到'最新'排序")
                    except:
                        logger.info("未找到'最新'排序按钮，使用默认排序")
                    
                    time.sleep(3)  # 再次等待页面加载
                    
                    # 提取笔记列表（前10-15条）
                    notes = []
                    selectors = [
                        'tag:a@href*=/explore/',
                        'tag:div@class*=note-item',
                        'tag:div@class*=note',
                    ]
                    
                    for selector in selectors:
                        try:
                            notes = self.page.eles(selector, timeout=5)
                            if notes and len(notes) > 0:
                                logger.info(f"使用选择器 '{selector}' 找到 {len(notes)} 条笔记")
                                break
                        except:
                            continue
                    
                    # 如果还是找不到，尝试通过链接特征查找
                    if not notes:
                        try:
                            all_links = self.page.eles('tag:a', timeout=5)
                            explore_links = [link for link in all_links if '/explore/' in (link.attr('href') or '')]
                            if explore_links:
                                notes = explore_links[:15]
                                logger.info(f"通过链接特征找到 {len(notes)} 条笔记")
                        except Exception as e:
                            logger.warning(f"通过链接查找失败: {str(e)}")
                    
                    # 限制为前15条
                    notes = notes[:15]
                    
                    if not notes:
                        logger.warning(f"未找到任何笔记，当前页面URL: {self.page.url}")
                        continue
                    
                    for idx, note in enumerate(notes, 1):
                        try:
                            # 提取标题和链接
                            title = ""
                            url = ""
                            
                            try:
                                if hasattr(note, 'tag') and note.tag == 'a':
                                    title = note.text or ""
                                    url = note.attr('href') or ""
                                else:
                                    link_elem = note.ele('tag:a', timeout=1)
                                    if link_elem:
                                        url = link_elem.attr('href') or ""
                                        title = link_elem.text or ""
                                    
                                    if not title:
                                        for tag in ['tag:span', 'tag:p', 'tag:div', 'tag:h3']:
                                            try:
                                                title_elem = note.ele(tag, timeout=0.5)
                                                if title_elem and title_elem.text:
                                                    title = title_elem.text
                                                    break
                                            except:
                                                continue
                            except Exception as e:
                                logger.warning(f"提取笔记信息失败: {str(e)}")
                                continue
                            
                            if url and not url.startswith('http'):
                                url = 'https://www.xiaohongshu.com' + url
                            
                            # 提取发布时间
                            date_str = ""
                            try:
                                date_selectors = ['tag:span', 'tag:time', 'tag:div']
                                for sel in date_selectors:
                                    try:
                                        elems = note.eles(sel, timeout=0.5)
                                        for elem in elems:
                                            text = elem.text or ""
                                            if any(kw in text for kw in ['前', '天', '小时', '分钟', '昨天', '今天']):
                                                date_str = text
                                                break
                                        if date_str:
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            # 时间过滤：只保留3天内
                            if date_str and not self.is_recent(date_str):
                                logger.info(f"  笔记 {idx} 超出3天范围，跳过: {title[:30] if title else '无标题'}...")
                                continue
                            
                            if not title or not url:
                                continue
                            
                            # 提取摘要
                            snippet = ""
                            try:
                                all_text = note.text or ""
                                if all_text and len(all_text) > len(title):
                                    snippet = all_text[:200]
                            except:
                                pass
                            
                            # 检查是否包含负面关键词
                            has_negative = any(kw in (title + snippet) for kw in NEGATIVE_KEYWORDS)
                            
                            # 如果包含负面关键词，必须点进去获取评论
                            comments = []
                            if has_negative or any(kw in snippet for kw in NEGATIVE_KEYWORDS):
                                try:
                                    click_link = note if hasattr(note, 'tag') and note.tag == 'a' else note.ele('tag:a', timeout=1)
                                    if click_link:
                                        click_link.click()
                                        time.sleep(3)  # 等待详情页加载
                                        
                                        # 提取评论（置顶或高赞）
                                        comment_selectors = [
                                            'tag:div@class*=comment-item',
                                            'tag:div@class*=comment',
                                            'tag:li@class*=comment',
                                        ]
                                        
                                        for selector in comment_selectors:
                                            try:
                                                comment_elems = self.page.eles(selector, timeout=2)
                                                if comment_elems:
                                                    for comment_elem in comment_elems[:5]:
                                                        comment_text = comment_elem.text
                                                        if comment_text:
                                                            comments.append(comment_text)
                                                    break
                                            except:
                                                continue
                                        
                                        # 返回列表页
                                        self.page.back()
                                        time.sleep(2)
                                except Exception as e:
                                    logger.warning(f"获取评论失败: {str(e)}")
                            
                            result = {
                                "platform": "小红书",
                                "keyword": keyword,
                                "title": title.strip(),
                                "url": url.strip(),
                                "date": date_str.strip(),
                                "snippet": snippet.strip(),
                                "has_negative": has_negative,
                                "comments": comments,
                                "comment_count": len(comments)
                            }
                            results.append(result)
                            logger.info(f"  ✓ 采集笔记 {idx}: {title[:50]}... (负面: {has_negative}, 评论: {len(comments)}条)")
                            
                        except Exception as e:
                            logger.warning(f"处理笔记 {idx} 失败: {str(e)}")
                            continue
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"小红书采集异常: {str(e)}", exc_info=True)
        
        logger.info(f"小红书采集完成，共找到 {len(results)} 条有效数据")
        self.xhs_data = results
        return results
    
    def crawl_wechat(self) -> List[Dict[str, Any]]:
        """
        第三阶段（补充）：微信公众号采集逻辑
        
        Returns:
            微信公众号数据列表
        """
        if not self.page:
            logger.error("浏览器未初始化")
            return []
        
        logger.info("=" * 60)
        logger.info("第三阶段（补充）：微信公众号采集")
        logger.info("=" * 60)
        
        results = []
        
        try:
            # 切换到微信公众号搜索页（搜狗微信）
            self.page.get('https://weixin.sogou.com/')
            time.sleep(3)
            
            # 处理可能的验证码
            try:
                # 检查是否有验证码
                verify_img = self.page.ele('tag:img@id=seccodeImage', timeout=2)
                if verify_img:
                    logger.warning("⚠️ 检测到验证码，请手动完成验证后按回车继续...")
                    try:
                        input("验证完成后按回车继续...")
                    except EOFError:
                        time.sleep(10)
            except:
                pass  # 没有验证码，继续
            
            for keyword in COMPETITOR_KEYWORDS:
                try:
                    logger.info(f"搜索关键词: {keyword}")
                    
                    # 查找搜索框
                    search_input = None
                    selectors = [
                        'tag:input@id=query',
                        'tag:input@name=query',
                        'tag:input@class*=search',
                        'tag:input@type=text',
                    ]
                    
                    for selector in selectors:
                        try:
                            search_input = self.page.ele(selector, timeout=3)
                            if search_input:
                                break
                        except:
                            continue
                    
                    if not search_input:
                        logger.warning(f"未找到搜索框，跳过关键词: {keyword}")
                        continue
                    
                    # 输入关键词
                    search_input.clear()
                    search_input.input(keyword)
                    time.sleep(1)
                    
                    # 点击搜索按钮
                    search_btn = self.page.ele('tag:input@type=submit', timeout=2)
                    if search_btn:
                        search_btn.click()
                    else:
                        search_input.input('\n')
                    
                    time.sleep(5)  # 等待搜索结果加载
                    
                    # 处理可能的验证码（再次检查）
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
                    
                    # 提取文章列表
                    articles = []
                    selectors = [
                        'tag:div@class*=news-box',
                        'tag:div@class*=news-item',
                        'tag:div@class*=news',
                        'tag:h3@class*=news-title',
                    ]
                    
                    for selector in selectors:
                        try:
                            articles = self.page.eles(selector, timeout=5)
                            if articles and len(articles) > 0:
                                logger.info(f"使用选择器 '{selector}' 找到 {len(articles)} 篇文章")
                                break
                        except:
                            continue
                    
                    # 如果还是找不到，尝试通过链接特征查找
                    if not articles:
                        try:
                            all_links = self.page.eles('tag:a', timeout=5)
                            wechat_links = [link for link in all_links if 'mp.weixin.qq.com' in (link.attr('href') or '')]
                            if wechat_links:
                                articles = wechat_links[:15]
                                logger.info(f"通过链接特征找到 {len(articles)} 篇文章")
                        except Exception as e:
                            logger.warning(f"通过链接查找失败: {str(e)}")
                    
                    # 限制为前15条
                    articles = articles[:15]
                    
                    if not articles:
                        logger.warning(f"未找到任何文章，当前页面URL: {self.page.url}")
                        continue
                    
                    for idx, article in enumerate(articles, 1):
                        try:
                            # 提取标题和链接
                            title = ""
                            url = ""
                            
                            try:
                                if hasattr(article, 'tag') and article.tag == 'a':
                                    title = article.text or ""
                                    url = article.attr('href') or ""
                                else:
                                    link_elem = article.ele('tag:a', timeout=1)
                                    if link_elem:
                                        url = link_elem.attr('href') or ""
                                        title = link_elem.text or ""
                                    
                                    if not title:
                                        for tag in ['tag:h3', 'tag:h2', 'tag:span', 'tag:p']:
                                            try:
                                                title_elem = article.ele(tag, timeout=0.5)
                                                if title_elem and title_elem.text:
                                                    title = title_elem.text
                                                    break
                                            except:
                                                continue
                            except Exception as e:
                                logger.warning(f"提取文章信息失败: {str(e)}")
                                continue
                            
                            if not url.startswith('http'):
                                # 处理相对链接
                                if url.startswith('//'):
                                    url = 'https:' + url
                                elif url.startswith('/'):
                                    url = 'https://weixin.sogou.com' + url
                            
                            # 提取发布时间
                            date_str = ""
                            try:
                                date_selectors = ['tag:span@class*=news-time', 'tag:span', 'tag:time']
                                for sel in date_selectors:
                                    try:
                                        elems = article.eles(sel, timeout=0.5)
                                        for elem in elems:
                                            text = elem.text or ""
                                            if any(kw in text for kw in ['前', '天', '小时', '分钟', '昨天', '今天', '-']):
                                                date_str = text
                                                break
                                        if date_str:
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            # 时间过滤：只保留3天内
                            if date_str and not self.is_recent(date_str):
                                logger.info(f"  文章 {idx} 超出3天范围，跳过: {title[:30] if title else '无标题'}...")
                                continue
                            
                            if not title or not url:
                                continue
                            
                            # 提取摘要
                            snippet = ""
                            try:
                                snippet_elem = article.ele('tag:p@class*=news-text', timeout=1)
                                if snippet_elem:
                                    snippet = snippet_elem.text or ""
                                else:
                                    all_text = article.text or ""
                                    if all_text and len(all_text) > len(title):
                                        snippet = all_text[:200]
                            except:
                                pass
                            
                            # 检查是否包含负面关键词
                            has_negative = any(kw in (title + snippet) for kw in NEGATIVE_KEYWORDS)
                            
                            # 如果包含负面关键词，点进去获取评论
                            comments = []
                            if has_negative or any(kw in snippet for kw in NEGATIVE_KEYWORDS):
                                try:
                                    click_link = article if hasattr(article, 'tag') and article.tag == 'a' else article.ele('tag:a', timeout=1)
                                    if click_link:
                                        click_link.click()
                                        time.sleep(3)  # 等待详情页加载
                                        
                                        # 提取评论（微信公众号的评论在文章底部）
                                        comment_selectors = [
                                            'tag:div@class*=comment',
                                            'tag:div@id*=comment',
                                            'tag:div@class*=msg',
                                        ]
                                        
                                        for selector in comment_selectors:
                                            try:
                                                comment_elems = self.page.eles(selector, timeout=2)
                                                if comment_elems:
                                                    for comment_elem in comment_elems[:5]:
                                                        comment_text = comment_elem.text
                                                        if comment_text:
                                                            comments.append(comment_text)
                                                    break
                                            except:
                                                continue
                                        
                                        # 返回列表页
                                        self.page.back()
                                        time.sleep(2)
                                except Exception as e:
                                    logger.warning(f"获取评论失败: {str(e)}")
                            
                            result = {
                                "platform": "微信公众号",
                                "keyword": keyword,
                                "title": title.strip(),
                                "url": url.strip(),
                                "date": date_str.strip(),
                                "snippet": snippet.strip(),
                                "has_negative": has_negative,
                                "comments": comments,
                                "comment_count": len(comments)
                            }
                            results.append(result)
                            logger.info(f"  ✓ 采集文章 {idx}: {title[:50]}... (负面: {has_negative}, 评论: {len(comments)}条)")
                            
                        except Exception as e:
                            logger.warning(f"处理文章 {idx} 失败: {str(e)}")
                            continue
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"微信公众号采集异常: {str(e)}", exc_info=True)
        
        logger.info(f"微信公众号采集完成，共找到 {len(results)} 条有效数据")
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
                "包含负面": item.get("has_negative", False),
                "评论数": item.get("comment_count", 0),
                "评论内容": "\n".join(item.get("comments", []))
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv('raw_data.csv', index=False, encoding='utf-8-sig')
        logger.info(f"原始数据已保存到: raw_data.csv (共 {len(df_data)} 条)")
    
    def generate_report(self) -> str:
        """
        第四阶段：使用 Gemini Pro 生成市场雷达日报
        
        Returns:
            Markdown 格式的报告
        """
        logger.info("=" * 60)
        logger.info("第四阶段：阿里千问 销冠分析")
        logger.info("=" * 60)
        
        all_data = {
            "douyin_data": self.douyin_data,
            "xhs_data": self.xhs_data,
            "wechat_data": self.wechat_data,
            "current_date": CURRENT_DATE
        }
        data_json = json.dumps(all_data, ensure_ascii=False, indent=2)
        
        system_prompt = """你不是AI，你是海马职加的**首席市场官**。你的受众是一线销售团队。
请阅读以下从抖音、小红书和微信公众号抓取的最近3天竞品情报。
请生成一份《市场雷达日报》，包含三个板块：

1. **🚨 竞品暴雷区 (重点)**：
   - 谁家最近被骂了？用户痛点是什么？
   - **销售话术**：销售遇到客户提这家竞品时，如何用这个黑料一招制敌？

2. **📉 价格/活动监测**：
   - 竞品有没有发"降价"、"保Offer"等新海报？我们该怎么应对？

3. **🗣️ 真实学员声音 (评论区精华)**：
   - 摘录 3-5 条最有代表性的用户吐槽评论（原话）。"""

        user_prompt = f"""请分析以下采集到的竞品情报（最近3天）：

{data_json}

请按照上述要求生成《市场雷达日报》，格式为 Markdown。
每条情报必须包含原始链接，严禁编造信息。"""

        try:
            logger.info("调用阿里千问 API 生成报告...")
            
            # 使用阿里千问生成内容（添加重试机制）
            max_retries = 3
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    response = self.ai_client.chat.completions.create(
                        model=QWEN_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=2048,
                        timeout=60  # 60秒超时
                    )
                    
                    report = response.choices[0].message.content
                    break  # 成功，退出重试循环
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"阿里千问 API 调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                        logger.info(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        raise  # 最后一次尝试失败，抛出异常
            
            # 添加标题和日期
            full_report = f"# 海马职加·市场雷达日报\n\n**生成时间**: {CURRENT_DATE}\n\n---\n\n{report}"
            
            logger.info("阿里千问 报告生成完成")
            return full_report
            
        except Exception as e:
            logger.error(f"阿里千问 生成失败: {str(e)}")
            # 如果生成失败，返回基础报告
            return f"""# 海马职加·市场雷达日报

**生成时间**: {CURRENT_DATE}

## 数据统计

- 抖音数据: {len(self.douyin_data)} 条
- 小红书数据: {len(self.xhs_data)} 条
- 微信公众号数据: {len(self.wechat_data)} 条

*注：AI 分析失败，请查看 raw_data.csv 获取原始数据。*
"""
    
    def run(self, test_mode: bool = False, skip_login: bool = False):
        """
        执行完整的采集流程
        
        Args:
            test_mode: 是否为测试模式，True 时使用模拟数据
            skip_login: 是否跳过登录步骤（假设已登录）
        """
        logger.info("=" * 80)
        logger.info("海马职加·市场雷达日报 - 开始运行" + (" [测试模式]" if test_mode else ""))
        logger.info("=" * 80)
        
        try:
            if test_mode:
                # 测试模式：使用模拟数据
                logger.info("使用模拟数据进行测试...")
                self.douyin_data = [
                    {
                        "platform": "抖音",
                        "keyword": "DBC职梦",
                        "title": "DBC职梦学员分享：拿到Amazon offer的真实经历",
                        "url": "https://www.douyin.com/video/example1",
                        "date": "2小时前",
                        "comments": [
                            "我也报了DBC，但是服务真的很一般，导师回复很慢",
                            "他们价格太贵了，性价比不高",
                            "DBC的保offer承诺根本兑现不了，我朋友退费拖了3个月"
                        ],
                        "comment_count": 3
                    }
                ]
                self.xhs_data = [
                    {
                        "platform": "小红书",
                        "keyword": "爱思益",
                        "title": "避雷！爱思益退费拖延，客服不回复",
                        "url": "https://www.xiaohongshu.com/explore/example1",
                        "date": "1天前",
                        "snippet": "报了爱思益的课程，申请退费已经2个月了，客服一直说在处理，但就是不退钱",
                        "has_negative": True,
                        "comments": [
                            "我也是，退费拖了3个月才到账",
                            "爱思益的客服态度很差，根本不解决问题",
                        ],
                        "comment_count": 2
                    }
                ]
                self.wechat_data = [
                    {
                        "platform": "微信公众号",
                        "keyword": "途鸽求职",
                        "title": "途鸽求职2025春季课程上线",
                        "url": "https://mp.weixin.qq.com/s/example",
                        "date": "昨天",
                        "snippet": "途鸽推出2025春季课程，包含保offer服务",
                        "has_negative": False,
                        "comments": [],
                        "comment_count": 0
                    }
                ]
                logger.info(f"模拟数据：抖音 {len(self.douyin_data)} 条，小红书 {len(self.xhs_data)} 条，微信公众号 {len(self.wechat_data)} 条")
            else:
                # 正常模式：真实采集
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
                            self.page.get('https://weixin.sogou.com/')
                            time.sleep(2)
                    except:
                        pass
                
                # 第二阶段：抖音采集
                self.crawl_douyin()
                
                # 第三阶段：小红书采集
                self.crawl_xhs()
                
                # 第三阶段（补充）：微信公众号采集
                self.crawl_wechat()
            
            # 保存原始数据
            self.save_raw_data()
            
            # 第四阶段：生成报告
            report = self.generate_report()
            
            # 保存报告
            report_file = f"Market_Daily_Report_{CURRENT_DATE}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"报告已保存到: {report_file}")
            
            if test_mode:
                # 测试模式：打印报告到控制台
                print("\n" + "=" * 80)
                print("【测试模式 - 消息预览】")
                print("=" * 80)
                print(report)
                print("=" * 80)
                print(f"\n✅ 测试完成，消息未发送")
                print(f"📊 数据统计：抖音 {len(self.douyin_data)} 条，小红书 {len(self.xhs_data)} 条，微信公众号 {len(self.wechat_data)} 条")
                logger.info("测试模式：消息已打印到控制台")
            else:
                print(f"\n✅ 采集完成！")
                print(f"📊 数据统计：抖音 {len(self.douyin_data)} 条，小红书 {len(self.xhs_data)} 条，微信公众号 {len(self.wechat_data)} 条")
                print(f"📄 原始数据：raw_data.csv")
                print(f"📋 分析报告：{report_file}")
            
            logger.info("=" * 80)
            logger.info("市场雷达日报生成完成")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"运行异常: {str(e)}", exc_info=True)
            raise
        finally:
            # 不自动关闭浏览器，让用户查看结果
            logger.info("浏览器保持打开状态，请手动关闭")


def main():
    """主函数"""
    import sys
    # 如果命令行参数包含 --test 或 -t，则进入测试模式
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    # 如果命令行参数包含 --skip-login，则跳过登录步骤
    skip_login = '--skip-login' in sys.argv or '--skip' in sys.argv
    
    spy = MarketSpyPro()
    spy.run(test_mode=test_mode, skip_login=skip_login)


if __name__ == "__main__":
    main()
