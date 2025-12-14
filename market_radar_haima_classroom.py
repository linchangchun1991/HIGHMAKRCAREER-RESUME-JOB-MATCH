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
import platform
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

# ==================== 优化后的关键词配置 ====================
# 使用组合关键词搜索，避免匹配到无关内容（咖啡、鞋子等）

# 竞品品牌组合搜索关键词
SEARCH_QUERIES = {
    '路觅': [
        '路觅留学',
        '路觅辅导',
        '路觅网课',
        '路觅作业辅导',
        '路觅论文',
        '路觅课程',
        '路觅 挂科',
        '路觅 GPA'
    ],
    '考而思': [
        '考而思留学',
        '考而思辅导',
        '考而思网课',
        '考而思怎么样',
        '考而思课程',
        '考而思 退费'
    ],
    '辅无忧': [
        '辅无忧留学',
        '辅无忧辅导',
        '辅无忧网课',
        '辅无忧怎么样',
        '辅无忧论文'
    ],
    '万能班长': [
        '万能班长留学',
        '万能班长辅导',
        '万能班长网课',
        '万能班长怎么样'
    ],
    '海马课堂': [
        '海马课堂',
        '海马课堂怎么样',
        '海马课堂辅导',
        '海马课堂论文',
        '海马课堂 退费',
        '海马课堂 避雷'
    ]
}

# 竞品品牌列表（用于遍历）
KEYWORDS = list(SEARCH_QUERIES.keys())

# ==================== Chrome用户数据目录配置 ====================
# 使用已登录的Chrome配置（反爬策略）

if platform.system() == 'Darwin':  # Mac
    CHROME_USER_DATA_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome")
elif platform.system() == 'Windows':
    CHROME_USER_DATA_DIR = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
else:  # Linux
    CHROME_USER_DATA_DIR = os.path.expanduser("~/.config/google-chrome")

CHROME_PROFILE = "Default"  # 或 "Profile 1", "Profile 2" 等

# ==================== 留学辅导赛道专属关键词（放宽版） ====================
# 必须命中以下关键词之一，才认为是留学辅导相关内容

STUDY_ABROAD_KEYWORDS = [
    # 核心词（放宽）
    '留学', '辅导', '网课', '论文', '作业', '课程',
    '教育', '培训', '学术', '考试', '补习',
    
    # 地区
    '英国', '澳洲', '美国', '加拿大', '香港', '新加坡',
    '澳大利亚', '英联邦', '海外',
    
    # 学校类型
    '大学', '本科', '硕士', '研究生', 'Master', 'PhD', '博士',
    'University', 'College', '留学生',
    
    # 具体学校（常见）
    '悉尼', '墨尔本', 'UNSW', 'ANU', 'UQ', '莫纳什', '新南',
    '帝国理工', 'UCL', 'KCL', 'LSE', '曼大', '爱丁堡', '华威',
    '多伦多', 'UBC', '麦吉尔', '滑铁卢',
    '港大', '港中文', '港科技', 'NUS', 'NTU', '港理工',
    
    # 服务类型（留学专属）
    '论文辅导', '网课辅导', '课程辅导', '作业辅导', '考前辅导',
    'GPA', '学分', '挂科', '补考', 'Appeal', '申诉',
    '课业', '学术', '留学生辅导',
    
    # 学科（留学生常见）
    '商科', '会计', '金融', 'Economics', '经济学',
    '计算机', 'CS', '工程', 'Engineering', 'IT',
    '统计', '数学',
    
    # 评价相关（放宽）
    '怎么样', '靠谱', '推荐', '好不好', '评价',
    '真实', '体验', '避雷', '口碑',
]

# 国内考证赛道（必须排除）
DOMESTIC_EXAM_KEYWORDS = [
    '基金从业', '证券从业', '银行从业', '期货从业',
    '会计师', 'CPA', '税务师', '审计师', 'ACCA',
    '教师资格', '教资', '普通话',
    '公务员', '事业单位', '考编', '国考', '省考',
    '考研', '四六级', 'CET', '英语四六级',
    '驾照', '驾考',
    '健康管理师', '心理咨询师', '营养师',
    '建造师', '造价师', '监理工程师',
]

# 教育相关关键词（通用，用于基础过滤）
EDUCATION_KEYWORDS = STUDY_ABROAD_KEYWORDS + [
    # 服务类型（通用）
    '辅导', '网课', '论文', '作业', '课程', '补习',
    '学术', '考试', '挂科', 'GPA', '学分', '毕业', '答疑',
    # 评价相关
    '靠谱', '怎么样', '好不好', '推荐', '避雷', '踩坑',
    '退费', '退款', '价格', '收费', '导师', '老师', '教授'
]

# 必须排除的干扰词（命中任意1个就丢弃）
EXCLUDE_KEYWORDS = [
    '咖啡', '德训鞋', '鞋子', '穿搭', '徒步', '骑行',
    '茶路', '酒业', '旅游', '景区', '美食', '餐厅',
    '手机', 'iPhone', '数码', '护肤', '美妆', '服装',
    '品牌', '联名', '种草', '开箱', '测评', 'OOTD'
]

# ==================== 品牌消歧配置 ====================
# 精准判断是否是目标品牌的教育内容，排除同名但不同业务的品牌

BRAND_DISAMBIGUATION = {
    '路觅': {
        # 我们要找的：留学辅导机构
        'target_context': ['留学', '辅导', '网课', '论文', '作业', '考试', 'GPA', '补习', '课程', '学术'],
        # 需要排除的同名品牌/内容
        'exclude_patterns': [
            '路觅斯',      # 德训鞋品牌
            'LUMES',       # 德训鞋英文
            '德训鞋',
            '咖啡',
            '咖啡车',
            '茶路觅',      # 茶文化
            '万里茶路',
            '乔家大院',
            '酒业',
            '徒步',
            '骑行',
            '穿搭',
            'OOTD',
        ]
    },
    '考而思': {
        'target_context': ['留学', '辅导', '大学', '硕士', '论文', '网课', '课程', '考试'],
        'exclude_patterns': []  # 这个品牌名比较独特，干扰少
    },
    '辅无忧': {
        'target_context': ['留学', '辅导', '大学', '硕士', '论文', '网课', '课程', '考试'],
        'exclude_patterns': [
            '检车无忧',   # 汽车服务
            '债车无忧',
            '捷车无忧',
            '人车无忧',
        ]
    },
    '万能班长': {
        'target_context': ['留学', '辅导', '大学', '澳洲', '英国', '论文', '网课', '课程'],
        'exclude_patterns': [
            '小学',
            '中学',
            '班长竞选',
            '班级',
        ]
    },
    '海马课堂': {
        'target_context': ['留学', '辅导', '论文', '网课', 'GPA', '课程', '考试'],
        'exclude_patterns': [
            '海马体',      # 脑科学
            '海马汽车',
        ]
    }
}

# 全局黑名单（任何品牌都排除）
GLOBAL_BLACKLIST = [
    # 服装/鞋类
    '德训鞋', '鞋子', '穿搭', 'OOTD', '服装', '衣服', 'LUMES', '路觅斯',
    # 餐饮/旅游
    '咖啡', '餐厅', '美食', '徒步', '骑行', '旅游', '景区', '茶路', '酒业', '乔家大院',
    # 数码/3C
    'iPhone', '手机', '数码', '科技',
    # K12教育（我们是留学赛道）
    '小升初', '中小学', '幼儿园', '小学', '初中', '高中', '红领巾奖章', '少先队', '入团', '班主任',
    '荡起双桨', '童年', '童声',
    # 其他无关
    '海马体', '海马汽车', '爬山', '异性',
]

# 时间范围（最近一周）
DAYS_BACK = 7
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")


class MarketRadarHaimaClassroom:
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
        
        # 配置浏览器（使用已登录的Chrome配置 - 反爬策略）
        try:
            if use_debug_port:
                # 尝试连接本地 9222 端口的 Chrome（用于小红书采集）
                try:
                    self.page = ChromiumPage(addr='127.0.0.1:9222')
                    logger.info("成功连接到本地 Chrome 调试端口 (9222)")
                    logger.info("提示：请确保 Chrome 已以调试模式启动，并已登录小红书账号")
                    # 注入反检测JS
                    self._inject_anti_detect()
                except Exception as e:
                    logger.warning(f"连接本地 Chrome 调试端口失败: {str(e)}")
                    logger.warning("=" * 80)
                    logger.warning("【重要提示】请先启动 Chrome 调试模式：")
                    logger.warning("Mac: open -n /Applications/Google\\ Chrome.app --args --remote-debugging-port=9222")
                    logger.warning("Windows: \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port=9222")
                    logger.warning("=" * 80)
                    # 降级为使用Chrome用户数据目录
                    self._init_with_user_data()
            else:
                # 使用Chrome用户数据目录（已登录配置）
                self._init_with_user_data()
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            logger.error("提示：如果遇到连接错误，请先手动启动 Chrome 调试模式")
            self.page = None
        
        # 存储采集的数据
        self.douyin_data = []
        self.xhs_data = []
        self.wechat_data = []
        
        logger.info(f"市场雷达系统初始化完成，当前日期: {CURRENT_DATE}")
    
    def _init_with_user_data(self):
        """使用Chrome用户数据目录初始化浏览器（反爬策略）"""
        try:
            options = ChromiumOptions()
            options.headless(False)
            
            # 关键！使用已登录的Chrome配置
            # 注意：如果Chrome正在运行，需要使用不同的Profile或临时目录
            if os.path.exists(CHROME_USER_DATA_DIR):
                # 尝试使用临时Profile目录，避免与正在运行的Chrome冲突
                # 或者使用Profile 1（如果Default正在使用）
                profile_to_use = CHROME_PROFILE
                
                # 检查Default是否被占用，如果是，尝试Profile 1
                default_lock = os.path.join(CHROME_USER_DATA_DIR, CHROME_PROFILE, 'SingletonLock')
                if os.path.exists(default_lock):
                    logger.warning(f"检测到Chrome可能正在运行，尝试使用Profile 1")
                    profile_to_use = "Profile 1"
                
                try:
                    options.set_user_data_path(CHROME_USER_DATA_DIR)
                    options.set_argument(f'--profile-directory={profile_to_use}')
                    logger.info(f"使用Chrome用户数据目录: {CHROME_USER_DATA_DIR} (Profile: {profile_to_use})")
                except:
                    # 如果设置失败，使用默认配置
                    logger.warning("无法设置用户数据目录，使用默认配置")
            else:
                logger.warning(f"Chrome用户数据目录不存在: {CHROME_USER_DATA_DIR}，使用默认配置")
            
            # 反检测设置
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-infobars')
            options.set_argument('--no-first-run')
            options.set_argument('--no-default-browser-check')
            
            # 随机窗口大小（模拟真人）
            width = random.randint(1200, 1600)
            height = random.randint(800, 1000)
            options.set_argument(f'--window-size={width},{height}')
            
            # 尝试创建浏览器实例
            try:
                self.page = ChromiumPage(addr_or_opts=options)
                # 注入反检测JS
                self._inject_anti_detect()
                logger.info("浏览器初始化成功（使用已登录Chrome配置 + 反检测）")
            except Exception as e:
                # 如果失败，可能是Chrome正在运行，使用普通模式
                logger.warning(f"使用Chrome用户数据目录创建浏览器失败: {str(e)}")
                raise
            
        except Exception as e:
            logger.warning(f"使用Chrome用户数据目录失败: {str(e)}，降级为普通模式")
            options = ChromiumOptions()
            options.headless(False)
            options.set_argument('--disable-blink-features=AutomationControlled')
            self.page = ChromiumPage(addr_or_opts=options)
            self._inject_anti_detect()
            logger.info("浏览器初始化成功（普通模式 + 反检测）")
    
    def _inject_anti_detect(self):
        """注入反检测脚本"""
        if not self.page:
            return
        
        js = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        window.chrome = {
            runtime: {}
        };
        """
        try:
            self.page.run_js(js)
            logger.debug("反检测JS注入成功")
        except Exception as e:
            logger.debug(f"反检测JS注入失败: {str(e)}")
    
    def human_like_delay(self, min_sec=2, max_sec=5):
        """模拟人类随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        # 加入微小的随机波动
        delay += random.uniform(-0.5, 0.5)
        time.sleep(max(0.5, delay))
    
    def human_like_scroll(self):
        """模拟人类滚动"""
        if not self.page:
            return
        
        for _ in range(random.randint(2, 4)):
            # 随机滚动距离
            scroll_distance = random.randint(200, 500)
            try:
                self.page.scroll.down(scroll_distance)
            except:
                pass
            
            # 随机停顿
            time.sleep(random.uniform(0.5, 1.5))
            
            # 偶尔往上滚一点（更像真人）
            if random.random() < 0.3:
                try:
                    self.page.scroll.up(random.randint(50, 100))
                except:
                    pass
                time.sleep(random.uniform(0.3, 0.8))
    
    def move_mouse_randomly(self):
        """随机移动鼠标（更像真人）"""
        if not self.page:
            return
        
        try:
            # 获取页面尺寸
            width = self.page.run_js('return window.innerWidth') or 1200
            height = self.page.run_js('return window.innerHeight') or 800
            
            # 随机移动几次
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, max(200, width - 100))
                y = random.randint(100, max(200, height - 100))
                self.page.run_js(f'''
                    var event = new MouseEvent('mousemove', {{
                        'clientX': {x},
                        'clientY': {y}
                    }});
                    document.dispatchEvent(event);
                ''')
                time.sleep(random.uniform(0.1, 0.3))
        except:
            pass
    
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
    
    def _find_videos_in_json(self, data, videos=None):
        """
        递归从JSON中查找视频信息
        
        Args:
            data: JSON数据（dict或list）
            videos: 视频列表（用于递归）
        
        Returns:
            视频列表
        """
        if videos is None:
            videos = []
        
        if isinstance(data, dict):
            # 检查是否是视频对象
            if 'aweme_id' in data or ('id' in data and 'desc' in data):
                videos.append(data)
            else:
                for value in data.values():
                    self._find_videos_in_json(value, videos)
        elif isinstance(data, list):
            for item in data:
                self._find_videos_in_json(item, videos)
        
        return videos
    
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
        
        days_ago = datetime.now() - timedelta(days=DAYS_BACK)
        return parsed_time >= days_ago
    
    def is_education_related(self, title: str, content: str = "") -> bool:
        """
        判断内容是否与教育相关（第一层过滤：规则过滤）
        
        Args:
            title: 标题
            content: 内容/摘要
        
        Returns:
            是否与教育相关
        """
        if not title:
            return False
        
        text = f"{title} {content}".lower()
        
        # 排除明显无关的
        for kw in EXCLUDE_KEYWORDS:
            if kw in text:
                logger.debug(f"  排除（包含干扰词 '{kw}'）: {title[:50]}")
                return False
        
        # 必须包含教育关键词
        for kw in EDUCATION_KEYWORDS:
            if kw in text:
                return True
        
        # 如果都不匹配，返回False
        logger.debug(f"  排除（未包含教育关键词）: {title[:50]}")
        return False
    
    def is_study_abroad_content(self, title: str, content: str = "", brand: str = "") -> tuple[bool, str]:
        """
        判断是否是留学辅导赛道内容（放宽版过滤）
        
        Args:
            title: 标题
            content: 内容/摘要
            brand: 品牌名（用于判断品牌名是否在标题中）
        
        Returns:
            (是否有效, 原因说明)
        """
        if not title:
            return False, "标题为空"
        
        text = f"{title} {content}".lower()
        title_lower = title.lower()
        
        # 第一步：排除国内考证赛道
        for kw in DOMESTIC_EXAM_KEYWORDS:
            if kw in text:
                return False, f"排除: {kw}"
        
        # 第二步：如果品牌名在标题中，直接通过（放宽）
        if brand:
            brand_lower = brand.lower()
            if brand_lower in title_lower:
                return True, "品牌名在标题中"
        
        # 第三步：检查留学关键词（放宽）
        hit_keywords = []
        for kw in STUDY_ABROAD_KEYWORDS:
            if kw.lower() in text:
                hit_keywords.append(kw)
        
        if hit_keywords:
            return True, f"命中: {', '.join(hit_keywords[:3])}"
        
        # 第四步：如果内容较长且包含品牌名，也通过（放宽）
        if brand and len(text) > 50:
            brand_lower = brand.lower()
            if brand_lower in text:
                return True, "内容较长且包含品牌名，保留观察"
        
        return False, "未命中关键词"
    
    def is_target_brand_content(self, brand_name: str, title: str, content: str = "") -> tuple[bool, str]:
        """
        精准判断是否是目标品牌的教育内容（品牌消歧）
        
        Args:
            brand_name: 品牌名
            title: 标题
            content: 内容/摘要
        
        Returns:
            (是否有效, 原因说明)
        """
        if not title:
            return False, "标题为空"
        
        text = f"{title} {content}".lower()
        config = BRAND_DISAMBIGUATION.get(brand_name, {})
        
        # 第一步：全局黑名单过滤
        for word in GLOBAL_BLACKLIST:
            if word.lower() in text:
                return False, f"全局黑名单: {word}"
        
        # 第二步：品牌专属排除词
        for pattern in config.get('exclude_patterns', []):
            if pattern.lower() in text:
                return False, f"品牌排除词: {pattern}"
        
        # 第三步：必须命中教育场景词
        target_words = config.get('target_context', EDUCATION_KEYWORDS)
        hit_words = [w for w in target_words if w in text]
        
        if not hit_words:
            return False, "未命中教育场景词"
        
        return True, f"命中: {', '.join(hit_words[:3])}"
    
    def strict_content_filter(self, brand_name: str, item: dict) -> tuple[bool, str]:
        """
        严格过滤无关内容（四层过滤）
        
        Args:
            brand_name: 品牌名
            item: 数据项
        
        Returns:
            (是否有效, 原因说明)
        """
        title = item.get('title', '')
        content = item.get('content', '') or item.get('snippet', '')
        
        # 第一层：必须有实质内容
        if len(title) < 5:
            return False, "标题过短"
        
        # 第二层：留学赛道过滤（最重要！排除国内考证，但放宽条件）
        is_study_abroad, reason = self.is_study_abroad_content(title, content, brand_name)
        if not is_study_abroad:
            return False, reason
        
        # 第三层：基础教育过滤（大幅放宽）
        # 如果已经通过留学赛道过滤，且品牌名在标题中，直接跳过基础教育过滤
        if brand_name and brand_name.lower() in title.lower():
            pass  # 品牌名在标题中，直接通过
        # 如果标题包含"教育"、"辅导"、"课程"等核心词，也直接通过
        elif any(kw in title.lower() for kw in ['教育', '辅导', '课程', '培训', '学习', '教学']):
            pass  # 包含核心教育词，直接通过
        elif not self.is_education_related(title, content):
            # 其他情况才进行基础教育过滤
            return False, "未通过基础教育过滤"
        
        # 第四层：品牌消歧过滤
        is_valid, reason = self.is_target_brand_content(brand_name, title, content)
        if not is_valid:
            return False, reason
        
        return True, "通过"
    
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
            
            for brand_name in KEYWORDS:
                # 使用组合关键词搜索
                search_queries = SEARCH_QUERIES.get(brand_name, [brand_name])
                logger.info(f"品牌: {brand_name}，使用 {len(search_queries)} 个组合关键词搜索")
                
                for keyword in search_queries:
                    try:
                        logger.info(f"搜索关键词: {keyword}")
                        print(f"[抖音深潜] 搜索关键词: {keyword}")
                        
                        # 优化：访问综合搜索页（不是视频页），并设置时间排序
                        # 第一步：先访问首页，建立session（反爬策略）
                        try:
                            self.page.get("https://www.douyin.com/")
                            self.human_like_delay(3, 5)
                            self.move_mouse_randomly()
                        except:
                            pass
                        
                        # 第二步：访问搜索页
                        search_url = f"https://www.douyin.com/search/{keyword}"
                        logger.info(f"  访问搜索页: {search_url}")
                        print(f"[抖音搜索] 访问搜索页: {search_url}")
                        self.page.get(search_url)
                        self.human_like_delay(4, 6)
                        self.move_mouse_randomly()
                        
                        # 第三步：点击"综合"Tab（不是视频Tab）
                        try:
                            logger.info("  尝试点击'综合'Tab...")
                            print("[抖音搜索] 尝试点击'综合'Tab...")
                            # 尝试多种方式找到"综合"Tab
                            general_tab = None
                            tab_selectors = [
                                'text:综合',
                                'xpath://div[contains(text(), "综合")]',
                                'xpath://span[contains(text(), "综合")]',
                                'css:[data-e2e="search-result-tab-general"]',
                            ]
                            for selector in tab_selectors:
                                try:
                                    general_tab = self.page.ele(selector, timeout=2)
                                    if general_tab:
                                        logger.info(f"  ✓ 找到'综合'Tab（使用: {selector}）")
                                        print(f"[抖音搜索] ✓ 找到'综合'Tab")
                                        general_tab.click()
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if not general_tab:
                                logger.warning("  ⚠️ 未找到'综合'Tab，可能已在综合页面")
                                print("[抖音搜索] ⚠️ 未找到'综合'Tab，可能已在综合页面")
                        except Exception as e:
                            logger.warning(f"  点击'综合'Tab失败: {str(e)}")
                            print(f"[抖音搜索] 点击'综合'Tab失败: {str(e)}")
                        
                        # 第四步：尝试点击"最新"排序按钮
                        try:
                            logger.info("  尝试点击'最新'排序...")
                            print("[抖音搜索] 尝试点击'最新'排序...")
                            sort_btn = None
                            sort_selectors = [
                                'text:最新',
                                'text:按时间',
                                'xpath://div[contains(text(), "最新")]',
                                'css:[data-e2e="search-result-sort-time"]',
                            ]
                            for selector in sort_selectors:
                                try:
                                    sort_btn = self.page.ele(selector, timeout=2)
                                    if sort_btn:
                                        logger.info(f"  ✓ 找到'最新'排序（使用: {selector}）")
                                        print(f"[抖音搜索] ✓ 找到'最新'排序")
                                        sort_btn.click()
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if not sort_btn:
                                logger.warning("  ⚠️ 未找到'最新'排序按钮")
                                print("[抖音搜索] ⚠️ 未找到'最新'排序按钮")
                        except Exception as e:
                            logger.warning(f"  点击'最新'排序失败: {str(e)}")
                            print(f"[抖音搜索] 点击'最新'排序失败: {str(e)}")
                        
                        # 打印当前页面URL确认
                        logger.info(f"  当前页面URL: {self.page.url}")
                        print(f"[抖音搜索] 当前页面URL: {self.page.url}")
                        
                        logger.info(f"当前页面 URL: {self.page.url}")
                        print(f"[抖音深潜] 当前页面 URL: {self.page.url}")
                        
                        # 等待内容加载
                        try:
                            self.page.wait.ele_displayed('css:div[data-e2e="scroll-list"]', timeout=10)
                            logger.info("  ✓ 页面内容已加载")
                        except:
                            logger.warning("  ⚠️ 未检测到内容容器，继续尝试...")
                        
                        # 人类行为模拟：滚动加载更多内容
                        self.human_like_scroll()
                        self.move_mouse_randomly()
                        
                        # 使用多种选择器查找内容（综合搜索页面）
                        # 根据调试结果，使用 div.search-result-card 或 div[contains(@class, "search-result")]
                        result_items = []
                        video_urls = []
                        
                        try:
                            print("[抖音搜索] 尝试多种选择器查找内容...")
                            
                            # 策略1：查找搜索结果卡片（综合搜索页面）
                            selectors_to_try = [
                                ('css:div.search-result-card', '搜索结果卡片'),
                                ('xpath://div[contains(@class, "search-result")]', '搜索结果容器'),
                                ('css:div[data-e2e="scroll-list"] > div', '滚动列表项'),
                            ]
                            
                            for selector, desc in selectors_to_try:
                                try:
                                    items = self.page.eles(selector, timeout=5)
                                    if items and len(items) > 0:
                                        result_items = items
                                        logger.info(f"  [{desc}] 找到 {len(items)} 个结果项")
                                        print(f"[抖音搜索] [{desc}] 找到 {len(items)} 个结果项")
                                        break
                                except Exception as e:
                                    logger.debug(f"  选择器 {desc} 失败: {str(e)}")
                                    continue
                            
                            # 从结果项中提取链接
                            for item in result_items[:20]:  # 最多处理20个
                                try:
                                    # 尝试多种方式提取链接
                                    link = None
                                    link_selectors = [
                                        'css:a',
                                        'xpath:.//a[contains(@href, "/video/")]',
                                        'xpath:.//a[contains(@href, "/user/")]',
                                        'xpath:.//a',
                                    ]
                                    
                                    for link_sel in link_selectors:
                                        try:
                                            link_elem = item.ele(link_sel, timeout=1)
                                            if link_elem:
                                                href = link_elem.attr('href') or ''
                                                if href:
                                                    # 处理相对链接
                                                    if not href.startswith('http'):
                                                        if href.startswith('//'):
                                                            href = 'https:' + href
                                                        elif href.startswith('/'):
                                                            href = 'https://www.douyin.com' + href
                                                        else:
                                                            continue
                                                    
                                                    # 只保留视频链接或用户链接（综合搜索可能包含用户）
                                                    if ('/video/' in href or '/user/' in href) and 'douyin.com' in href:
                                                        link = href
                                                        break
                                        except:
                                            continue
                                    
                                    if link and link not in video_urls:
                                        video_urls.append(link)
                                        print(f"[抖音搜索] ✓ 找到链接: {link[:60]}...")
                                        
                                        if len(video_urls) >= 10:
                                            break
                                            
                                except Exception as e:
                                    logger.debug(f"  处理结果项时出错: {str(e)}")
                                    continue
                            
                            video_urls = video_urls[:10]  # 先取10个，后续会过滤
                            logger.info(f"找到 {len(video_urls)} 个链接")
                            print(f"[抖音搜索] 最终找到 {len(video_urls)} 个链接")
                            
                            if not video_urls:
                                # 如果还是找不到，打印调试信息
                                logger.warning("  ⚠️ 未找到任何链接，打印页面信息...")
                                try:
                                    page_html_preview = self.page.html[:1000] if hasattr(self.page, 'html') else "无法获取HTML"
                                    logger.warning(f"页面前1000字符: {page_html_preview}")
                                except:
                                    pass
                            
                        except Exception as e:
                            logger.warning(f"提取链接失败: {str(e)}")
                            print(f"[抖音搜索] 提取失败: {str(e)}")
                            continue
                        
                        if not video_urls:
                            logger.warning(f"未找到任何视频，跳过关键词: {keyword}")
                            print(f"[抖音深潜] 未找到任何视频，跳过关键词: {keyword}")
                            continue
                        
                        # 循环采集：真人深潜模式
                        for idx, video_url in enumerate(video_urls, 1):
                            new_tab = None
                            try:
                                logger.info(f"  处理内容 {idx}/{len(video_urls)}: {video_url[:60]}...")
                                print(f"[抖音搜索] 正在处理内容 {idx}/{len(video_urls)}: {video_url[:60]}...")
                                
                                # 如果是用户链接，跳过（综合搜索可能包含用户）
                                if '/user/' in video_url:
                                    logger.info(f"    跳过用户链接: {video_url}")
                                    continue
                                
                                # 打开新标签页
                                new_tab = self.page.new_tab()
                                new_tab.get(video_url)
                                
                                # 强制等待：必须等够时间
                                print(f"  [抖音搜索] 强制等待 3 秒，确保页面渲染...")
                                time.sleep(3)
                                
                                # 提取标题（终极优化：RENDER_DATA + DOM + HTML正则）
                                title = ""
                                try:
                                    # 方法1：从 RENDER_DATA 提取（最准确）
                                    try:
                                        html = new_tab.html
                                        import json
                                        import urllib.parse
                                        
                                        # 查找 RENDER_DATA script 标签
                                        render_match = re.search(r'<script id="RENDER_DATA"[^>]*>(.+?)</script>', html)
                                        if render_match:
                                            try:
                                                json_str = urllib.parse.unquote(render_match.group(1))
                                                data = json.loads(json_str)
                                                
                                                # 递归查找视频信息
                                                videos = self._find_videos_in_json(data)
                                                if videos:
                                                    video = videos[0]  # 取第一个
                                                    desc = video.get('desc') or video.get('title', '')
                                                    if desc and len(desc) > 5:
                                                        title = desc.strip()
                                                        print(f"  [抖音深潜] 从RENDER_DATA提取到标题: {title[:50]}...")
                                            except Exception as e:
                                                logger.debug(f"  RENDER_DATA解析失败: {str(e)}")
                                    except:
                                        pass
                                    
                                    # 方法2：从DOM元素提取（备选）
                                    if not title:
                                        try:
                                            title_selectors = [
                                                'tag:h1',
                                                'tag:div@class*=title',
                                                'tag:p@class*=title',
                                                'tag:span@class*=title',
                                                'css:div[class*="title"]',
                                                'css:p[class*="title"]',
                                                'css:span[class*="title"]',
                                            ]
                                            for sel in title_selectors:
                                                try:
                                                    title_elem = new_tab.ele(sel, timeout=1)
                                                    if title_elem:
                                                        title_text = title_elem.text or ""
                                                        if title_text and len(title_text.strip()) > 5:
                                                            title = title_text.strip()
                                                            print(f"  [抖音深潜] 从DOM提取到标题: {title[:50]}...")
                                                            break
                                                except:
                                                    continue
                                        except:
                                            pass
                                    
                                    # 方法3：从页面文本中提取（兜底）
                                    if not title:
                                        try:
                                            # 获取页面所有文本，找最长的段落作为标题
                                            body_elem = new_tab.ele('tag:body', timeout=2)
                                            if body_elem:
                                                full_text = body_elem.text or ""
                                                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                                                # 找长度在10-200之间的文本作为标题候选
                                                candidates = [line for line in lines if 10 <= len(line) <= 200]
                                                if candidates:
                                                    # 优先选择包含关键词的
                                                    for candidate in candidates:
                                                        if any(kw in candidate for kw in [brand_name, keyword]):
                                                            title = candidate
                                                            break
                                                    # 如果没有包含关键词的，选第一个
                                                    if not title and candidates:
                                                        title = candidates[0]
                                                        print(f"  [抖音深潜] 从页面文本提取到标题: {title[:50]}...")
                                        except:
                                            pass
                                except Exception as e:
                                    logger.debug(f"  提取标题失败: {str(e)}")
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
                                
                                # 严格时间过滤：只保留最近3天
                                if date_str:
                                    if not self.is_recent(date_str):
                                        logger.info(f"    视频超出3天范围，跳过: {date_str}")
                                        print(f"  [抖音深潜] 视频超出3天范围，跳过: {date_str}")
                                        try:
                                            new_tab.close()
                                        except:
                                            pass
                                        continue
                                else:
                                    # 如果没有时间信息，尝试从页面提取
                                    try:
                                        time_elems = new_tab.eles('tag:span@class*=time', timeout=1)
                                        for te in time_elems[:3]:
                                            time_text = te.text or ""
                                            if time_text and not self.is_recent(time_text):
                                                logger.info(f"    视频超出3天范围（从页面提取），跳过: {time_text}")
                                                try:
                                                    new_tab.close()
                                                except:
                                                    pass
                                                continue
                                    except:
                                        pass
                                
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
                                    # 严格内容过滤（三层过滤）
                                    snippet_text = " ".join(comments[:3]) if comments else ""
                                    item_data = {
                                        "title": title,
                                        "content": snippet_text,
                                        "snippet": snippet_text
                                    }
                                    is_valid, reason = self.strict_content_filter(brand_name, item_data)
                                    
                                    if not is_valid:
                                        logger.info(f"  ✗ 过滤: {reason} - {title[:50] if title else '无标题'}...")
                                        print(f"[抖音深潜] ✗ 过滤: {reason} - {title[:50] if title else '无标题'}...")
                                        try:
                                            new_tab.close()
                                        except:
                                            pass
                                        continue
                                    
                                    # 提取互动数据（点赞数等）
                                    likes = "0"
                                    try:
                                        like_elems = new_tab.eles('tag:span@class*=like', timeout=1)
                                        for le in like_elems[:1]:
                                            like_text = le.text or ""
                                            if like_text and any(c.isdigit() for c in like_text):
                                                likes = like_text
                                                break
                                    except:
                                        pass
                                    
                                    result = {
                                        "platform": "抖音",
                                        "keyword": brand_name,  # 使用品牌名而不是搜索关键词
                                        "search_query": keyword,  # 记录实际搜索的关键词
                                        "title": title.strip() or f"视频 {idx}",
                                        "url": video_url,
                                        "date": date_str.strip(),
                                        "likes": likes,  # 新增点赞数
                                        "comments": comments,  # 纯文本列表
                                        "comment_count": len(comments),
                                        "is_valid": True
                                    }
                                    results.append(result)
                                    logger.info(f"  ✓ 采集成功: {title[:50] if title else '无标题'}... (评论: {len(comments)}条, 点赞: {likes})")
                                    print(f"[抖音深潜] ✓ 采集成功: {title[:50] if title else '无标题'}... (评论: {len(comments)}条, 点赞: {likes})")
                                    
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
                
                # 每个品牌搜索完成后稍作停顿
                time.sleep(random.uniform(1, 2))
            
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
    
    def _get_xhs_note_detail(self, note_url: str, brand_name: str) -> Dict[str, Any]:
        """
        获取小红书笔记详情（标题、内容、评论、互动数据）
        
        Args:
            note_url: 笔记URL
            brand_name: 品牌名
        
        Returns:
            详情数据字典
        """
        detail = {}
        new_tab = None
        
        try:
            new_tab = self.page.new_tab()
            new_tab.get(note_url)
            time.sleep(random.uniform(3, 5))
            
            # 提取标题
            try:
                title_ele = new_tab.ele('tag:h1', timeout=3)
                if not title_ele:
                    title_ele = new_tab.ele('tag:div@class*=title', timeout=3)
                if title_ele:
                    detail['title'] = title_ele.text.strip()
            except:
                pass
            
            # 提取正文内容
            try:
                content_ele = new_tab.ele('tag:div@class*=desc', timeout=3)
                if not content_ele:
                    content_ele = new_tab.ele('tag:div@class*=content', timeout=3)
                if content_ele:
                    detail['content'] = content_ele.text.strip()[:500]  # 截取前500字
            except:
                pass
            
            # 提取作者
            try:
                author_ele = new_tab.ele('tag:span@class*=author', timeout=2)
                if not author_ele:
                    author_ele = new_tab.ele('tag:a@class*=user', timeout=2)
                if author_ele:
                    detail['author'] = author_ele.text.strip()
            except:
                pass
            
            # 提取发布时间
            try:
                time_ele = new_tab.ele('tag:span@class*=time', timeout=2)
                if time_ele:
                    detail['date'] = time_ele.text.strip()
            except:
                pass
            
            # 提取互动数据（点赞、收藏、评论数）
            try:
                # 点赞数
                like_ele = new_tab.ele('tag:span@class*=like', timeout=2)
                if like_ele:
                    detail['likes'] = like_ele.text.strip() or "0"
                
                # 收藏数
                collect_ele = new_tab.ele('tag:span@class*=collect', timeout=2)
                if collect_ele:
                    detail['collects'] = collect_ele.text.strip() or "0"
                
                # 评论数
                comment_count_ele = new_tab.ele('tag:span@class*=comment', timeout=2)
                if comment_count_ele:
                    detail['comment_count'] = comment_count_ele.text.strip() or "0"
            except:
                pass
            
            # 获取热门评论（前5条）
            comments = []
            try:
                # 滚动到评论区
                new_tab.scroll.down(500)
                time.sleep(2)
                
                comment_items = new_tab.eles('tag:div@class*=comment', timeout=3)
                for item in comment_items[:5]:
                    try:
                        content_ele = item.ele('tag:p', timeout=1)
                        if not content_ele:
                            content_ele = item.ele('tag:span', timeout=1)
                        if content_ele:
                            comment_text = content_ele.text.strip()
                            if comment_text and 10 <= len(comment_text) <= 200:
                                # 提取点赞数
                                like_count = "0"
                                try:
                                    like_ele = item.ele('tag:span@class*=like', timeout=1)
                                    if like_ele:
                                        like_count = like_ele.text.strip() or "0"
                                except:
                                    pass
                                
                                comments.append({
                                    'content': comment_text[:200],
                                    'likes': like_count
                                })
                    except:
                        continue
                
                detail['top_comments'] = comments
                detail['comment_count'] = len(comments)
            except:
                pass
            
            new_tab.close()
            
        except Exception as e:
            logger.debug(f"  获取详情失败: {str(e)}")
            if new_tab:
                try:
                    new_tab.close()
                except:
                    pass
        
        return detail
    
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
            for brand_name in KEYWORDS:
                # 使用组合关键词搜索
                search_queries = SEARCH_QUERIES.get(brand_name, [brand_name])
                logger.info(f"品牌: {brand_name}，使用 {len(search_queries)} 个组合关键词搜索")
                
                for keyword in search_queries:
                    try:
                        logger.info(f"搜索关键词: {keyword}")
                        print(f"[小红书列表页] 搜索关键词: {keyword}")
                        
                        # 先访问首页，建立session（反爬策略）
                        try:
                            self.page.get("https://www.xiaohongshu.com/explore")
                            self.human_like_delay(3, 5)
                            self.move_mouse_randomly()
                        except:
                            pass
                        
                        # 访问小红书搜索结果页
                        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
                        logger.info(f"  访问搜索页: {search_url}")
                        print(f"[小红书搜索] 访问搜索页: {search_url}")
                        self.page.get(search_url)
                        self.human_like_delay(4, 6)
                        self.move_mouse_randomly()
                        
                        logger.info(f"  当前页面 URL: {self.page.url}")
                        print(f"[小红书搜索] 当前页面 URL: {self.page.url}")
                        
                        # 尝试点击"最新"排序（如果存在）
                        try:
                            logger.info("  尝试点击'最新'排序...")
                            print("[小红书搜索] 尝试点击'最新'排序...")
                            sort_btn = None
                            sort_selectors = [
                                'text:最新',
                                'text:按时间',
                                'xpath://div[contains(text(), "最新")]',
                            ]
                            for selector in sort_selectors:
                                try:
                                    sort_btn = self.page.ele(selector, timeout=2)
                                    if sort_btn:
                                        logger.info(f"  ✓ 找到'最新'排序")
                                        print(f"[小红书搜索] ✓ 找到'最新'排序")
                                        sort_btn.click()
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                        except Exception as e:
                            logger.warning(f"  点击'最新'排序失败: {str(e)}")
                            print(f"[小红书搜索] 点击'最新'排序失败: {str(e)}")
                        
                        # Smart Wait: 等待页面元素加载（检测 .note-item 是否出现）
                        print("[小红书搜索] Smart Wait: 等待笔记卡片加载...")
                        note_items = []
                        max_wait_time = 10  # 最多等待10秒
                        wait_interval = 1
                        waited_time = 0
                        
                        # 尝试多种选择器查找笔记卡片
                        selectors_to_try = [
                            'css:section.note-item',
                            'css:div.note-item',
                            'css:div[class*="note-item"]',
                            'css:a.cover',
                            'css:div[class*="note"]',
                            'xpath://section[contains(@class, "note")]',
                            'xpath://div[contains(@class, "note-item")]',
                            'xpath://a[contains(@href, "/explore/")]',
                        ]
                        
                        while waited_time < max_wait_time:
                            try:
                                for selector in selectors_to_try:
                                    try:
                                        items = self.page.eles(selector, timeout=2)
                                        if items and len(items) > 0:
                                            note_items = items
                                            logger.info(f"  ✓ 找到 {len(items)} 个笔记卡片（使用: {selector}）")
                                            print(f"[小红书搜索] ✓ 找到 {len(items)} 个笔记卡片（使用: {selector}）")
                                            break
                                    except:
                                        continue
                                
                                if note_items:
                                    break
                                
                                time.sleep(wait_interval)
                                waited_time += wait_interval
                                print(f"  [小红书搜索] 等待中... ({waited_time}/{max_wait_time}秒)")
                                
                            except Exception as e:
                                logger.debug(f"  Smart Wait 检测失败: {str(e)}")
                                time.sleep(wait_interval)
                                waited_time += wait_interval
                        
                        if not note_items:
                            logger.warning(f"未找到笔记卡片，尝试滚动加载...")
                            print("[小红书搜索] 未找到笔记卡片，尝试滚动加载...")
                        
                        # 人类行为模拟：滚动加载更多内容
                        self.human_like_scroll()
                        self.move_mouse_randomly()
                        
                        # 滚动后再次尝试查找笔记卡片
                        if not note_items:
                            for selector in selectors_to_try[:3]:  # 只试前3个
                                try:
                                    items = self.page.eles(selector, timeout=2)
                                    if items and len(items) > 0:
                                        note_items = items
                                        logger.info(f"  ✓ 滚动后找到 {len(items)} 个笔记卡片")
                                        print(f"[小红书搜索] ✓ 滚动后找到 {len(items)} 个笔记卡片")
                                        break
                                except:
                                    continue
                        
                        # Data Extraction: 从列表页提取数据（不进入详情页）
                        print("[小红书列表页] 开始提取列表页数据...")
                        keyword_results = []
                        
                        if note_items:
                            print(f"[小红书列表页] 找到 {len(note_items)} 个笔记卡片，开始提取...")
                            
                            for idx, card in enumerate(note_items[:10], 1):  # 最多处理10个
                                try:
                                    # 提取标题（终极优化：多种方式 + HTML正则备选）
                                    title = ""
                                    try:
                                        # 方法1：从卡片元素直接提取（多种选择器）
                                        title_selectors = [
                                            'css:a.title span',
                                            'css:span.title',
                                            'css:div.title span',
                                            'css:p.title',
                                            'css:a span[class*="title"]',
                                            'css:a.title',
                                            'css:span.title',
                                            'css:div.title',
                                            'tag:h2',
                                            'tag:h3',
                                            'tag:a',
                                            'tag:div@class*=title',
                                            'tag:span@class*=title',
                                            'xpath://a[contains(@href, "/explore/")]//span',
                                            'xpath://div[contains(@class, "title")]',
                                        ]
                                        
                                        for sel in title_selectors:
                                            try:
                                                title_elem = card.ele(sel, timeout=1)
                                                if title_elem:
                                                    title_text = title_elem.text or ""
                                                    # 如果找到标题，清理一下
                                                    if title_text and len(title_text.strip()) > 3:
                                                        title = title_text.strip()
                                                        logger.debug(f"    使用 {sel} 提取到标题: {title[:30]}")
                                                        break
                                            except:
                                                continue
                                        
                                        # 方法2：获取卡片内第一个有意义的文本（过滤掉数字和太短的文本）
                                        if not title:
                                            try:
                                                all_spans = card.eles('css:span')
                                                for span in all_spans:
                                                    text = span.text.strip() if span.text else ""
                                                    # 过滤掉数字（点赞数）和太短的文本
                                                    if len(text) > 5 and not text.isdigit() and not text.startswith('@'):
                                                        title = text
                                                        logger.debug(f"    从span提取到标题: {title[:30]}")
                                                        break
                                            except:
                                                pass
                                        
                                        # 方法3：从链接的title属性获取
                                        if not title:
                                            try:
                                                link_ele = card.ele('css:a', timeout=1)
                                                if link_ele:
                                                    title = link_ele.attr('title') or ""
                                                    if title:
                                                        logger.debug(f"    从链接title属性提取到标题: {title[:30]}")
                                            except:
                                                pass
                                        
                                        # 方法4：从链接文本提取
                                        if not title:
                                            try:
                                                link_elem = card.ele('tag:a', timeout=1)
                                                if link_elem:
                                                    link_text = link_elem.text or ""
                                                    if link_text and len(link_text.strip()) > 3:
                                                        title = link_text.strip()
                                                        logger.debug(f"    从链接文本提取到标题: {title[:30]}")
                                            except:
                                                pass
                                        
                                        # 方法5：从HTML正则提取（如果前面都失败）
                                        if not title:
                                            try:
                                                card_html = card.html
                                                # 匹配 href + 标题文本的模式
                                                title_patterns = [
                                                    r'href="(/explore/[a-f0-9]{24})"[^>]*>.*?<span[^>]*>([^<]{5,100})</span>',
                                                    r'<a[^>]*href="(/explore/[a-f0-9]{24})"[^>]*>.*?<span[^>]*>([^<]+)</span>',
                                                    r'title["\s:=]+["\']?([^"\']{5,100})["\']?',
                                                ]
                                                for pattern in title_patterns:
                                                    match = re.search(pattern, card_html, re.DOTALL | re.IGNORECASE)
                                                    if match:
                                                        if len(match.groups()) > 1:
                                                            title = match.group(2).strip()
                                                        else:
                                                            title = match.group(1).strip()
                                                        if title and len(title) > 3:
                                                            logger.debug(f"    从HTML正则提取到标题: {title[:30]}")
                                                            break
                                            except:
                                                pass
                                    except Exception as e:
                                        logger.debug(f"  提取标题失败: {str(e)}")
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
                                        # 如果标题为空，尝试从链接或其他地方提取
                                        if not title or len(title.strip()) < 3:
                                            # 尝试从链接文本提取
                                            try:
                                                link_elem = card.ele('tag:a', timeout=1)
                                                if link_elem:
                                                    link_text = link_elem.text or ""
                                                    if link_text and len(link_text.strip()) > 3:
                                                        title = link_text.strip()
                                            except:
                                                pass
                                        
                                        # 如果还是没有标题，跳过
                                        if not title or len(title.strip()) < 3:
                                            logger.debug(f"  跳过（标题为空或过短）: {url[:50] if url else '无链接'}")
                                            continue
                                        
                                        # 严格内容过滤（四层过滤）
                                        item_data = {
                                            "title": title,
                                            "content": snippet,
                                            "snippet": snippet
                                        }
                                        is_valid, reason = self.strict_content_filter(brand_name, item_data)
                                        
                                        if not is_valid:
                                            logger.info(f"  ✗ 过滤: {reason} - {title[:50] if title else '无标题'}...")
                                            print(f"[小红书搜索] ✗ 过滤: {reason} - {title[:50] if title else '无标题'}...")
                                            continue
                                        
                                        # 检查是否包含负面关键词
                                        negative_keywords = ['避雷', '坑', '退费', '骗局', '投诉', '差评', '垃圾', '不要', '千万别', '吵架']
                                        has_negative = any(kw in (title + snippet) for kw in negative_keywords)
                                        
                                        result = {
                                            "platform": "小红书",
                                            "keyword": brand_name,  # 使用品牌名而不是搜索关键词
                                            "search_query": keyword,  # 记录实际搜索的关键词
                                            "title": title.strip() or f"笔记 {idx}",
                                            "url": url,
                                            "date": "",  # 列表页通常没有发布时间
                                            "snippet": snippet.strip(),
                                            "content": snippet.strip(),  # 添加content字段用于详情
                                            "author": author.strip(),  # 新增作者字段
                                            "has_negative": has_negative,
                                            "comments": [],  # 列表页不抓取评论，后续会补充
                                            "comment_count": 0,
                                            "likes": "0",  # 列表页暂不获取，后续补充
                                            "is_valid": True
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
                            bing_results = self.fetch_from_bing(keyword)
                            # 对Bing结果也进行严格过滤
                            for bing_item in bing_results:
                                is_valid, reason = self.strict_content_filter(brand_name, bing_item)
                                if is_valid:
                                    bing_item['keyword'] = brand_name
                                    bing_item['search_query'] = keyword
                                    bing_item['is_valid'] = True
                                    keyword_results.append(bing_item)
                        
                        # 尝试获取详情页内容（最多3个，避免被风控）
                        for item in keyword_results[:3]:
                            if item.get('url'):
                                try:
                                    detail = self._get_xhs_note_detail(item['url'], brand_name)
                                    if detail:
                                        item.update(detail)
                                        time.sleep(random.uniform(3, 5))  # 每个详情页间隔久一点
                                except Exception as e:
                                    logger.debug(f"  获取详情失败: {str(e)}")
                                    continue
                        
                        results.extend(keyword_results)
                        time.sleep(random.uniform(2, 3))
                    
                    except Exception as e:
                        logger.error(f"采集关键词 {keyword} 失败: {str(e)}")
                        print(f"[小红书列表页] 采集关键词 {keyword} 失败: {str(e)}")
                        continue
                
                # 每个品牌搜索完成后稍作停顿
                time.sleep(random.uniform(1, 2))
            
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
            
            for brand_name in KEYWORDS:
                # 使用组合关键词搜索
                search_queries = SEARCH_QUERIES.get(brand_name, [brand_name])
                logger.info(f"品牌: {brand_name}，使用 {len(search_queries)} 个组合关键词搜索")
                
                for keyword in search_queries:
                    try:
                        logger.info(f"搜索关键词: {keyword}")
                        
                        # 访问搜索结果页
                        search_url = f"https://weixin.sogou.com/weixin?type=2&query={keyword}"
                        logger.info(f"  访问搜索页: {search_url}")
                        print(f"[搜狗微信搜索] 访问搜索页: {search_url}")
                        self.page.get(search_url)
                        time.sleep(random.uniform(3, 5))
                        
                        # 调试信息：打印当前页面状态
                        logger.info(f"  当前页面 URL: {self.page.url}")
                        print(f"[搜狗微信搜索] 当前页面 URL: {self.page.url}")
                        
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
                                
                                # 时间过滤：只保留最近一周内
                                if date_str and not self.is_recent(date_str):
                                    logger.info(f"    文章超出{DAYS_BACK}天范围，跳过: {date_str}")
                                    continue
                                
                                if title or url:
                                    # 严格内容过滤
                                    item_data = {
                                        "title": title,
                                        "content": snippet,
                                        "snippet": snippet
                                    }
                                    is_valid, reason = self.strict_content_filter(brand_name, item_data)
                                    
                                    if not is_valid:
                                        logger.info(f"  ✗ 过滤: {reason} - {title[:50] if title else '无标题'}...")
                                        continue
                                    
                                    result = {
                                        "platform": "搜狗微信",
                                        "keyword": brand_name,  # 使用品牌名而不是搜索关键词
                                        "search_query": keyword,  # 记录实际搜索的关键词
                                        "title": title.strip() or f"文章 {idx}",
                                        "url": url or "",
                                        "date": date_str.strip(),
                                        "snippet": snippet.strip(),
                                        "content": snippet.strip(),  # 添加content字段
                                        "comments": [],  # 微信文章不抓评论
                                        "comment_count": 0,
                                        "is_valid": True
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
                
                # 每个品牌搜索完成后稍作停顿
                time.sleep(random.uniform(1, 2))
            
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
            # 处理评论数据（可能是列表或字典列表）
            comments_text = ""
            if item.get("comments"):
                comments_list = item.get("comments", [])
                if comments_list and isinstance(comments_list[0], dict):
                    # 如果是字典列表（包含content和likes）
                    comments_text = "\n".join([f"{c.get('content', '')} (👍{c.get('likes', '0')})" for c in comments_list])
                else:
                    # 如果是纯文本列表
                    comments_text = "\n".join(comments_list)
            
            row = {
                "平台": item.get("platform", ""),
                "关键词": item.get("keyword", ""),  # 品牌名
                "搜索关键词": item.get("search_query", ""),  # 实际搜索的关键词
                "标题": item.get("title", ""),
                "链接": item.get("url", ""),
                "发布时间": item.get("date", ""),
                "摘要": item.get("snippet", "") or item.get("content", ""),
                "内容": item.get("content", ""),  # 新增内容字段
                "作者": item.get("author", ""),  # 新增作者字段（小红书）
                "点赞数": item.get("likes", "0"),  # 新增点赞数
                "收藏数": item.get("collects", "0"),  # 新增收藏数（小红书）
                "包含负面": item.get("has_negative", False),
                "评论数": item.get("comment_count", 0),
                "评论内容": comments_text
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv('raw_data_classroom.csv', index=False, encoding='utf-8-sig')
        logger.info(f"原始数据已保存到: raw_data_classroom.csv (共 {len(df_data)} 条，已过滤非教育内容)")
    
    def get_xhs_comments(self, note_url: str, max_comments: int = 10) -> List[Dict[str, Any]]:
        """
        获取小红书笔记评论
        
        Args:
            note_url: 笔记URL
            max_comments: 最大评论数
        
        Returns:
            评论列表
        """
        comments = []
        
        if not self.page:
            return comments
        
        try:
            # 打开笔记详情页
            new_tab = self.page.new_tab()
            new_tab.get(note_url)
            time.sleep(5)
            
            # 滚动到评论区
            new_tab.run_js('window.scrollBy(0, 500)')
            time.sleep(2)
            
            # 找评论元素
            comment_selectors = [
                'css:div.comment-item',
                'css:div[class*="comment"]',
                'css:div.note-comment',
                'xpath://div[contains(@class, "comment")]',
            ]
            
            comment_eles = []
            for sel in comment_selectors:
                try:
                    comment_eles = new_tab.eles(sel, timeout=3)
                    if comment_eles:
                        logger.info(f"  找到 {len(comment_eles)} 个评论元素（使用: {sel}）")
                        break
                except:
                    continue
            
            for ele in comment_eles[:max_comments]:
                try:
                    # 评论内容
                    content = ""
                    content_ele = ele.ele('css:span.content, div.content, p', timeout=1)
                    if content_ele:
                        content = content_ele.text.strip()
                    
                    # 用户名
                    username = ""
                    user_ele = ele.ele('css:span.name, a.user', timeout=1)
                    if user_ele:
                        username = user_ele.text.strip()
                    
                    # 点赞数
                    likes = "0"
                    like_ele = ele.ele('css:span.like-count, span.count', timeout=1)
                    if like_ele:
                        likes = like_ele.text.strip()
                    
                    if content and len(content) > 5:
                        comments.append({
                            'username': username,
                            'content': content[:300],
                            'likes': likes,
                            'source': note_url
                        })
                except:
                    continue
            
            new_tab.close()
        except Exception as e:
            logger.debug(f"评论抓取失败: {str(e)}")
            try:
                new_tab.close()
            except:
                pass
        
        return comments
    
    def get_douyin_comments(self, video_url: str, max_comments: int = 10) -> List[Dict[str, Any]]:
        """
        获取抖音视频评论
        
        Args:
            video_url: 视频URL
            max_comments: 最大评论数
        
        Returns:
            评论列表
        """
        comments = []
        
        if not self.page:
            return comments
        
        try:
            # 打开视频详情页
            new_tab = self.page.new_tab()
            new_tab.get(video_url)
            time.sleep(5)
            
            # 滚动加载评论
            new_tab.run_js('window.scrollBy(0, 600)')
            time.sleep(2)
            
            # 找评论元素
            comment_eles = new_tab.eles('css:div[class*="comment-item"], div[class*="comment-content"]', timeout=3)
            
            for ele in comment_eles[:max_comments]:
                try:
                    content = ele.text.strip() if ele.text else ""
                    
                    if content and len(content) > 5:
                        comments.append({
                            'content': content[:300],
                            'source': video_url
                        })
                except:
                    continue
            
            new_tab.close()
        except Exception as e:
            logger.debug(f"抖音评论抓取失败: {str(e)}")
            try:
                new_tab.close()
            except:
                pass
        
        return comments
    
    def collect_user_comments(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        收集用户评论（用于日报的"用户真实声音"板块）
        
        Args:
            data_list: 数据列表
        
        Returns:
            评论列表
        """
        comments = []
        
        for item in data_list:
            platform = item.get('platform', '')
            brand = item.get('keyword', '')
            item_comments = item.get('comments', [])
            
            if not item_comments:
                continue
            
            for comment in item_comments:
                if isinstance(comment, dict):
                    # 如果是字典格式（包含content和likes）
                    content = comment.get('content', '')
                    likes = comment.get('likes', '0')
                else:
                    # 如果是纯文本
                    content = str(comment)
                    likes = '0'
                
                if content and len(content) >= 10:
                    comments.append({
                        'content': content[:200],
                        'likes': likes,
                        'source': f"{brand} - {platform}"
                    })
        
        # 按点赞数排序（如果有）
        try:
            comments.sort(key=lambda x: int(str(x['likes']).replace('万', '0000').replace('k', '000') or '0'), reverse=True)
        except:
            pass
        
        return comments[:20]  # 返回前20条
    
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
            if not os.path.exists('raw_data_classroom.csv'):
                logger.warning("raw_data_classroom.csv 文件不存在")
                return {"douyin_data": [], "xhs_data": [], "wechat_data": []}
            
            df = pd.read_csv('raw_data_classroom.csv', encoding='utf-8-sig')
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
                    "snippet": row.get('摘要', '') or row.get('内容', ''),
                    "content": row.get('内容', '') or row.get('摘要', ''),
                    "has_negative": row.get('包含负面', False) if isinstance(row.get('包含负面'), bool) else False,
                    "comments": comments,
                    "comment_count": len(comments),
                    "is_valid": True  # CSV中的数据已经经过过滤，默认都是有效的
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
        
        # 数据源双重保障：优先使用内存数据，如果为空则从 CSV 读取
        douyin_data = self.douyin_data
        xhs_data = self.xhs_data
        wechat_data = self.wechat_data
        
        logger.info(f"内存数据：抖音 {len(douyin_data)} 条，小红书 {len(xhs_data)} 条，搜狗微信 {len(wechat_data)} 条")
        
        # 如果内存数据为空或很少，从 CSV 读取作为补充
        if (not douyin_data and not xhs_data and not wechat_data) or (len(douyin_data) + len(xhs_data) + len(wechat_data)) < 10:
            logger.warning("内存数据为空或不足，尝试从 CSV 文件加载...")
            csv_data = self.load_data_from_csv()
            csv_douyin = csv_data.get('douyin_data', [])
            csv_xhs = csv_data.get('xhs_data', [])
            csv_wechat = csv_data.get('wechat_data', [])
            
            # 合并内存数据和CSV数据（去重）
            if not douyin_data:
                douyin_data = csv_douyin
            if not xhs_data:
                xhs_data = csv_xhs
            if not wechat_data:
                wechat_data = csv_wechat
            
            logger.info(f"从 CSV 加载后：抖音 {len(douyin_data)} 条，小红书 {len(xhs_data)} 条，搜狗微信 {len(wechat_data)} 条")
        
        # 合并所有数据
        all_data_list = douyin_data + xhs_data + wechat_data
        
        # 过滤有效数据（放宽：默认保留所有数据，除非明确标记为无效）
        # 注意：CSV中保存的数据已经经过过滤，默认都是有效的
        valid_data = []
        for item in all_data_list:
            # 如果明确标记为无效，跳过
            if item.get('is_valid') is False:
                logger.debug(f"  跳过无效数据: {item.get('title', '')[:50]}")
                continue
            # 否则保留（包括is_valid为True或未设置的情况）
            # 对于从CSV加载的数据，如果没有is_valid字段，默认认为是有效的
            valid_data.append(item)
        
        logger.info(f"数据过滤：原始 {len(all_data_list)} 条 -> 有效 {len(valid_data)} 条")
        
        # 如果有效数据为空，但原始数据不为空，说明可能所有数据都没有is_valid字段
        # 这种情况下，我们放宽条件：默认保留所有数据
        if not valid_data and all_data_list:
            logger.warning("所有数据都没有is_valid字段或都被标记为无效，放宽条件：默认保留所有数据")
            valid_data = all_data_list
            # 确保所有数据都有is_valid=True标记
            for item in valid_data:
                if 'is_valid' not in item:
                    item['is_valid'] = True
        
        if not valid_data:
            logger.warning("所有数据源都为空或全部被过滤，无法生成报告")
            return f"""# 海马课堂·市场雷达日报

**生成时间**: {CURRENT_DATE}

## ⚠️ 数据采集结果

- 抖音数据: {len(douyin_data)} 条（有效: {len([i for i in douyin_data if i.get('is_valid', True)])} 条）
- 小红书数据: {len(xhs_data)} 条（有效: {len([i for i in xhs_data if i.get('is_valid', True)])} 条）
- 搜狗微信数据: {len(wechat_data)} 条（有效: {len([i for i in wechat_data if i.get('is_valid', True)])} 条）

*注：未采集到任何有效数据，可能所有内容都被过滤器过滤。*
"""
        
        # 收集用户评论
        user_comments = self.collect_user_comments(valid_data)
        
        # 格式化数据
        formatted_data = self.format_data_for_ai(valid_data)
        
        # 调试打印
        logger.info(f"正在发送给 AI 的数据长度: {len(formatted_data)} 字符")
        logger.info(f"数据统计：抖音 {len(douyin_data)} 条（有效: {len([i for i in douyin_data if i.get('is_valid', True)])}），小红书 {len(xhs_data)} 条（有效: {len([i for i in xhs_data if i.get('is_valid', True)])}），搜狗微信 {len(wechat_data)} 条（有效: {len([i for i in wechat_data if i.get('is_valid', True)])}）")
        logger.info(f"收集到用户评论: {len(user_comments)} 条")
        
        system_prompt = """你不是销售，你是海马课堂的**首席战略官 (CSO)**。
你拥有敏锐的市场洞察力。请根据采集到的全网数据（抖音/小红书/微信），为管理层撰写一份《全网市场雷达日报》。

**重要说明**：
- 本次数据已经过教育场景过滤，只包含与教育辅导相关的内容
- 如果某个竞品没有数据，说明近一周无教育相关内容更新，请直接标注"无更新"
- 不要展示无关内容（如咖啡、鞋子、旅游等）

**分析逻辑与输出格式 (Markdown)**：

**第一部分：⚔️ 竞品动作监测 (Competitor Moves)**
- 核心关注：竞品（路觅、考而思、辅无忧、万能班长等）最近发了什么新产品？搞了什么活动？有什么价格变动？
- 格式：`[平台] 竞品名：具体动作`，必须包含原文链接。
- **如果某个竞品没有数据，直接写：`[平台] 竞品名：近一周无教育相关内容更新`**
- 每条情报必须包含原始链接，格式：`🔗 [查看原文](链接)`
- 优先分析小红书平台的负面评价，因为通常最真实
- 请标注互动数据（点赞数、评论数等）

**第二部分：📢 用户舆情透视 (Voice of Customer)**

### 🔴 负面评论原声（摘录自小红书及抖音评论区）
- **必须摘录**：从数据中提取 3-5 条最具代表性的**负面评论原话**，作为"用户原声"展示。
- 格式：【平台用户 @xxx】（评论于xxx笔记/视频下）"评论内容"
- 如果数据中没有评论，请明确说明"本次未采集到用户评论数据"

### 🌡 舆情热词分析
- 核心负面热词：列出5-8个（如：退费难、导师水、虚假内推、服务差等）
- 情绪关键词：列出3-5个（如：愤怒、失望、投诉等）

### ✅ 结论
- 一句话总结当前用户情绪趋势

**第三部分：🧭 我们的战略启示 (Strategic Insights)**
- **这是最重要的部分**。基于上述竞品动作和用户舆情，给我们（海马课堂）提出 3 条具体的战略建议。
- 每条建议包含：
  1. 【标题】简短有力的策略名称
  2. **事实依据**：基于数据的支撑
  3. **策略建议**：具体的执行方案
  4. **目的**：预期达成的效果
- *不要写话术*，要写策略。
- 例如：'竞品A因为退费难被骂 -> 启示：我们应在宣发中强调资金监管和透明退费流程，建立信任壁垒。'

**风格要求**：
- 语言简练、专业、毒辣。
- 拒绝废话，直击本质。
- **建议必须基于今日抓取的具体数据，严禁生成通用建议。**
- **如果数据量少，不要编造内容，如实说明数据情况。**
- **所有链接必须完整，确保可以点击访问。**"""

        # 构建用户评论文本（如果有）
        comments_text = ""
        if user_comments:
            comments_text = "\n\n**用户评论数据**（共{}条）：\n".format(len(user_comments))
            for idx, comment in enumerate(user_comments[:10], 1):
                comments_text += f"{idx}. 「{comment['content']}」 (来源: {comment['source']}, 👍{comment['likes']})\n"
        else:
            comments_text = "\n\n**用户评论数据**：本次未采集到用户评论数据。\n"
        
        user_prompt = f"""以下是今日采集到的最新竞品情报数据（最近一周）：

{formatted_data}
{comments_text}

请根据以上数据生成《全网市场雷达日报》，格式为 Markdown。
每条情报必须包含原始链接，严禁编造信息。
**特别注意**：
1. 如果上述用户评论数据中有内容，必须摘录 3-5 条最具代表性的评论原话展示。
2. 战略建议必须基于上述具体数据，不能写通用建议。
3. 如果数据中没有评论，请明确说明"本次未采集到用户评论数据"。
4. 优先分析小红书平台的负面评价，因为通常最真实。
5. 在"竞品动作监测"部分，请标注互动数据（点赞数、评论数等）。"""

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
                full_report = f"# 海马课堂·市场雷达日报\n\n**生成时间**: {CURRENT_DATE}\n\n---\n\n{report}"
                
                logger.info("阿里千问 报告生成完成")
                return full_report
            else:
                raise Exception(f"API 调用失败: {response.status_code}, {response.message}")
            
        except Exception as e:
            logger.error(f"阿里千问 生成失败: {str(e)}")
            # 如果生成失败，返回基础报告
            return f"""# 海马课堂·市场雷达日报

**生成时间**: {CURRENT_DATE}

## 数据统计

- 抖音数据: {len(douyin_data)} 条
- 小红书数据: {len(xhs_data)} 条
- 搜狗微信数据: {len(wechat_data)} 条

*注：AI 分析失败，请查看 raw_data_classroom.csv 获取原始数据。*
"""
    
    def run(self, skip_login: bool = False):
        """
        执行完整的采集流程
        
        Args:
            skip_login: 是否跳过登录步骤（假设已登录）
        """
        logger.info("=" * 80)
        logger.info("海马课堂·市场雷达日报 - 开始运行")
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
            report_file = f"Market_Radar_Classroom_{CURRENT_DATE}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"报告已保存到: {report_file}")
            
            print(f"\n✅ 采集完成！")
            print(f"📊 数据统计：抖音 {len(self.douyin_data)} 条，小红书 {len(self.xhs_data)} 条，搜狗微信 {len(self.wechat_data)} 条")
            print(f"📄 原始数据：raw_data_classroom.csv")
            print(f"📋 分析报告：{report_file}")
            
            logger.info("=" * 80)
            logger.info("市场雷达日报生成完成")
            logger.info("=" * 80)
            
            # 测试模式：只打印消息，不发送到钉钉
            self.send_to_dingtalk(report, test_mode=True)
            
        except Exception as e:
            logger.error(f"运行异常: {str(e)}", exc_info=True)
            raise
        finally:
            # 不自动关闭浏览器，让用户查看结果
            logger.info("浏览器保持打开状态，请手动关闭")
    
    def send_to_dingtalk(self, report_content: str, test_mode: bool = True):
        """
        发送报告到钉钉群（确保所有链接完整）
        
        Args:
            report_content: 报告内容（Markdown格式）
            test_mode: 测试模式，如果为True则只打印不发送
        """
        try:
            import requests
            
            # 读取原始数据，补充链接信息
            try:
                csv_file = 'raw_data_classroom.csv'
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file, encoding='utf-8-sig')
                    
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
            
            # 测试模式：只打印消息，不发送
            if test_mode:
                print("\n" + "=" * 80)
                print("【测试模式】完整钉钉消息内容（带所有原文链接）")
                print("=" * 80)
                print(report_content)
                print("=" * 80)
                logger.info("测试模式：消息已打印到控制台，未发送到钉钉")
                return
            
            # 发送到钉钉（非测试模式）
            DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=ac8d1c6332c8a047b8786a930ab08d7f6db490843edca2de1bb65c68301c3113"
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "海马课堂·市场雷达日报",
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
    
    radar = MarketRadarHaimaClassroom()
    radar.run(skip_login=skip_login)


if __name__ == "__main__":
    main()
