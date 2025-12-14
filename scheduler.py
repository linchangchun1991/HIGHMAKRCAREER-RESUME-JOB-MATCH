#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘岗位定时抓取与钉钉推送脚本
功能：每3小时自动抓取最新岗位，去重后推送到钉钉群

⚠️ 重要提示：请务必保管好你的 DingTalk Token，不要泄露给他人！

安装依赖：
    pip install playwright schedule requests

安装Playwright浏览器：
    playwright install chromium

使用方法：
    python job_scraper_scheduler.py
"""

import time
import random
import sqlite3
import requests
import urllib.parse
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ==================== 配置区域 ====================

# 钉钉Webhook地址（请替换为你的实际Token）
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=c5b4858e08eb2b4cbf4e1678368b3ed64d82eb0b3083dd8c77964126f4ac7994"

# 数据库文件路径
DB_FILE = "jobs.db"

# 抓取间隔（秒）- 3小时 = 10800秒
SCRAPE_INTERVAL = 10800  # 3小时

# 随机等待时间范围（秒）- 模拟人类操作（已优化为更快速度）
# 快速模式：1-3秒，平衡模式：2-5秒，安全模式：5-15秒
RANDOM_WAIT_MIN = 1
RANDOM_WAIT_MAX = 3

# 城市映射配置（用于将模糊地区转换为具体城市）
CITY_MAPPING = {
    '非偏远地区': [
        '北京', '上海', '广州', '深圳', '杭州', '南京', '苏州', '成都', '重庆', 
        '武汉', '西安', '天津', '青岛', '大连', '宁波', '无锡', '长沙', '郑州',
        '济南', '合肥', '福州', '厦门', '昆明', '南宁', '石家庄', '哈尔滨', '长春', '沈阳'
    ],
    '南方城市': [
        '上海', '广州', '深圳', '杭州', '南京', '苏州', '成都', '重庆', '武汉',
        '长沙', '福州', '厦门', '昆明', '南宁', '海口', '三亚', '珠海', '东莞',
        '佛山', '中山', '惠州', '宁波', '无锡', '合肥', '南昌', '贵阳'
    ],
    '珠三角': [
        '广州', '深圳', '珠海', '东莞', '佛山', '中山', '惠州', '江门', '肇庆'
    ],
    '一线城市': [
        '北京', '上海', '广州', '深圳'
    ],
    '北上广深': [
        '北京', '上海', '广州', '深圳'
    ],
    '北上广深杭': [
        '北京', '上海', '广州', '深圳', '杭州'
    ],
    '江浙沪': [
        '江苏', '浙江', '上海'
    ],
    '东三省': [
        '哈尔滨', '长春', '沈阳', '大连'
    ],
    '北方二线城市': [
        '天津', '青岛', '大连', '济南', '石家庄', '太原', '郑州', '西安', '哈尔滨', '长春', '沈阳'
    ],
    '广东': [
        '广州', '深圳', '珠海', '东莞', '佛山', '中山', '惠州', '江门', '肇庆', '汕头', '湛江'
    ],
}

# 搜索配置列表（完整版，包含所有43个配置）
SEARCH_CONFIGS = [
    {
        'keywords': ['化学药物研发'],
        'locations': ['江苏', '浙江', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['策展助理', '科普展览', '文案编辑', '环保公益', '自然保护', 'CRO', 'CDMO', '医疗器械', 'IVD'],
        'locations': ['非偏远地区'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['外贸业务', '海外客户', '咨询', '国际化'],
        'locations': ['上海'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': '大公司优先',
        'education': '本科',
        'company_type': None,
    },
    {
        'keywords': ['法务', '法律'],
        'locations': ['山西', '陕西', '成都', '杭州', '深圳', '青岛', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': '央国企',
    },
    {
        'keywords': ['生物医疗技术', '临床应用', '产品推广'],
        'locations': ['江苏', '浙江', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': '企业/科研/卫生系统',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['环境', 'ESG', '稀土'],
        'locations': ['北京', '上海', '广州', '深圳', '杭州', '贵州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['Tesol', '国际学校老师', '心理辅导', '辅导员', '学校行政', '升学指导'],
        'locations': ['南方城市'],
        'grad_year': [2025, 2026],
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['CSR', 'ESG', '咨询', '行研', '政策研究', '市场调研'],
        'locations': ['广州', '珠三角'],
        'grad_year': 2025,
        'recruit_type': '社招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['精算师'],
        'locations': ['一线城市'],
        'grad_year': 2023,
        'recruit_type': '校招',
        'industry': ['保险', '金融'],
        'notes': '无经验',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['体育老师'],
        'locations': ['北京'],
        'grad_year': None,
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': '中学/大学',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['政府事务', '国际组织'],
        'locations': ['全国'],
        'grad_year': None,
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['国际学校非教职', '辅导员', '教务'],
        'locations': ['杭州'],
        'grad_year': None,
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['插画', '平面设计'],
        'locations': ['江苏', '浙江', '上海'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': '材料专业背景优先(难以筛选，先抓关键词)',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['金融'],
        'locations': ['深圳'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['人力资源'],
        'locations': ['北京'],
        'grad_year': 2024,
        'recruit_type': '校招',
        'industry': None,
        'notes': '大厂, 八大',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['快消市场', '互联网运营', '管培生'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['数据相关'],
        'locations': ['全国'],
        'grad_year': 2024,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['数据分析', '商业分析'],
        'locations': ['上海'],
        'grad_year': 2024,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['内容运营', '市场品牌'],
        'locations': ['杭州'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['控制算法'],
        'locations': ['苏州', '上海', '杭州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['机械'],
        'locations': ['湖南'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': '大专',
        'company_type': None,
    },
    {
        'keywords': ['应届生'],
        'locations': ['上海'],
        'grad_year': 2024,
        'recruit_type': '校招',
        'industry': None,
        'notes': '毕业时间：24年8月',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['影视总裁特助', '演出管理', '演唱会策划', '策展'],
        'locations': ['北京', '杭州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['内容运营'],
        'locations': ['广州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['量化'],
        'locations': ['北京', '上海', '广州', '深圳', '杭州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['供应链管理', '项目管理'],
        'locations': ['上海', '杭州', '深圳', '广州'],
        'grad_year': None,
        'recruit_type': '社招',
        'industry': None,
        'notes': '2年经验',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['审计', '财务', '投资'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['市场', '品牌', '运营', '创意策划'],
        'locations': ['江苏', '浙江', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['策划'],
        'locations': ['北京'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': '国央企',
    },
    {
        'keywords': ['英语教师'],
        'locations': ['杭州', '南京', '苏州', '深圳', '广州', '南宁', '成都', '重庆', '武汉', '宁波', '无锡', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': '高校/国际学校',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['体育老师'],
        'locations': ['东三省', '北京'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': '公办院校',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['主持', '播音', '宣传岗', '企业文化', '党群工作'],
        'locations': ['北京'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': '广电央企',
    },
    {
        'keywords': ['城乡规划', '出行', '运营'],
        'locations': ['南京', '江苏', '长沙', '成都', '广州', '深圳', '杭州', '上海', '北京'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['法律', '航运险资法律', '法务', '律师'],
        'locations': ['北京', '上海', '广州', '深圳', '杭州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['自动化'],
        'locations': ['北方二线城市'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': '国央企',
    },
    {
        'keywords': ['游戏策划', '游戏运营'],
        'locations': ['全国'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['项目管理'],
        'locations': ['江苏', '浙江', '上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['审计'],
        'locations': ['深圳', '广州'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': '四大',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['网络安全'],
        'locations': ['广东'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['机械销售'],
        'locations': ['深圳', '广州'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['生物医药', '农业科技'],
        'locations': ['广东'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['产品研究员', '投资分析师', '行研', '数据分析'],
        'locations': ['北京'],
        'grad_year': 2025,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['国际学校英语教师', '双语老师', '教培英语'],
        'locations': ['全国'],
        'grad_year': None,
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
]


# ==================== 数据库模块 ====================

class DBManager:
    """数据库管理器 - 用于记录已推送的岗位"""
    
    def __init__(self, db_file: str = DB_FILE):
        """初始化数据库连接"""
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构（包含所有9个字段）"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建表：posted_jobs（包含所有必需字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posted_jobs (
                url TEXT PRIMARY KEY,
                company_name TEXT,
                company_type TEXT,
                work_location TEXT,
                recruit_type TEXT,
                recruit_target TEXT,
                job_title TEXT NOT NULL,
                update_time TEXT,
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 如果表已存在但字段不完整，尝试添加新字段
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN company_type TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN work_location TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN recruit_type TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN recruit_target TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN update_time TEXT')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE posted_jobs ADD COLUMN deadline TEXT')
        except:
            pass
        
        conn.commit()
        conn.close()
        print(f"✓ 数据库初始化完成: {self.db_file}")
    
    def is_job_exists(self, url: str) -> bool:
        """判断岗位是否已存在"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM posted_jobs WHERE url = ?', (url,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def save_job(self, data: Dict):
        """保存新岗位到数据库（包含所有9个字段）"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO posted_jobs (
                    url, company_name, company_type, work_location,
                    recruit_type, recruit_target, job_title,
                    update_time, deadline, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url', ''),
                data.get('company_name', '未知'),
                data.get('company_type', '未知'),
                data.get('work_location', ''),
                data.get('recruit_type', ''),
                data.get('recruit_target', ''),
                data.get('job_title', ''),
                data.get('update_time', '未知'),
                data.get('deadline', '详见链接'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"⚠ 保存岗位到数据库时出错: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_total_count(self) -> int:
        """获取数据库中总岗位数"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM posted_jobs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count


# ==================== 钉钉通知模块 ====================

class DingTalkSender:
    """钉钉消息发送器"""
    
    def __init__(self, webhook: str = DINGTALK_WEBHOOK):
        """初始化钉钉发送器"""
        self.webhook = webhook
        if "YOUR_TOKEN" in webhook:
            print("⚠ 警告: 请先配置钉钉Webhook地址！")
    
    def send_file(self, file_path: str, file_name: str = None) -> bool:
        """发送文件到钉钉群（通过文件上传API）"""
        if "YOUR_TOKEN" in self.webhook:
            print("⚠ 钉钉Webhook未配置，跳过文件发送")
            return False
        
        if not file_name:
            file_name = file_path.split('/')[-1]
        
        try:
            # 读取文件
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 钉钉机器人发送文件需要先上传到钉钉服务器
            # 方法1: 使用钉钉的文件上传接口（需要access_token）
            # 方法2: 使用钉钉的"文件"消息类型（需要media_id）
            # 
            # 由于钉钉机器人Webhook不支持直接发送文件，我们使用以下方案：
            # 1. 将文件转换为base64（但钉钉不支持）
            # 2. 上传到云存储后发送链接（需要云存储服务）
            # 3. 使用钉钉企业应用API上传文件（需要额外权限）
            #
            # 最实用的方案：在消息中添加文件下载说明，并提供本地文件路径
            # 或者：使用钉钉的文件上传功能（需要从webhook中提取access_token）
            
            # 尝试使用钉钉的文件上传API
            # 从webhook URL中提取access_token
            import re
            token_match = re.search(r'access_token=([^&]+)', self.webhook)
            if not token_match:
                print("⚠ 无法从Webhook中提取access_token")
                return False
            
            access_token = token_match.group(1)
            
            # 钉钉文件上传接口
            upload_url = "https://oapi.dingtalk.com/media/upload"
            
            # 准备文件
            files = {
                'media': (file_name, file_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'type': 'file',
                'access_token': access_token
            }
            
            # 上传文件
            print(f"正在上传文件到钉钉: {file_name}...")
            response = requests.post(upload_url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    media_id = result.get('media_id')
                    print(f"✓ 文件上传成功，media_id: {media_id[:20]}...")
                    
                    # 发送文件消息
                    return self._send_file_message(media_id, file_name)
                else:
                    print(f"✗ 文件上传失败: {result.get('errmsg')}")
                    # 如果上传失败，尝试发送文件链接消息
                    return self._send_file_link_message(file_path, file_name)
            else:
                print(f"✗ 文件上传请求失败: HTTP {response.status_code}")
                # 如果上传失败，尝试发送文件链接消息
                return self._send_file_link_message(file_path, file_name)
                
        except Exception as e:
            print(f"✗ 发送文件时出错: {str(e)}")
            # 如果出错，尝试发送文件链接消息
            return self._send_file_link_message(file_path, file_name)
    
    def _send_file_message(self, media_id: str, file_name: str) -> bool:
        """发送文件消息（使用media_id）"""
        payload = {
            "msgtype": "file",
            "file": {
                "media_id": media_id
            }
        }
        
        try:
            response = requests.post(self.webhook, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"✓ 文件消息发送成功: {file_name}")
                    return True
                else:
                    print(f"✗ 文件消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"✗ 文件消息请求失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 发送文件消息时出错: {str(e)}")
            return False
    
    def _send_file_link_message(self, file_path: str, file_name: str) -> bool:
        """发送文件链接消息（备用方案：钉钉机器人不支持直接发送文件）"""
        import os
        abs_path = os.path.abspath(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # 发送包含文件信息的消息卡片
        content = f"""## 📎 岗位数据Excel文件

**文件名**: `{file_name}`

**文件大小**: {file_size_mb:.2f} MB

**文件位置**: 
```
{abs_path}
```

**查看方式**:
1. 💻 在电脑上直接打开文件
2. 📱 通过文件共享工具访问
3. ☁️ 如需在线查看，可将文件上传到云盘

**提示**: 
- 文件已自动生成并保存在脚本运行目录
- 每次抓取完成后会自动更新此文件
- 包含所有岗位的完整数据（{file_size_mb:.1f}MB）
"""
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"📎 Excel文件: {file_name}",
                "text": content
            }
        }
        
        try:
            response = requests.post(self.webhook, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"✓ 文件信息消息发送成功: {file_name}")
                    return True
                else:
                    print(f"✗ 文件信息消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"✗ 文件信息消息请求失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 发送文件信息消息时出错: {str(e)}")
            return False
    
    def send_markdown(self, title: str, content: str) -> bool:
        """发送Markdown格式消息"""
        if "YOUR_TOKEN" in self.webhook:
            print("⚠ 钉钉Webhook未配置，跳过推送")
            return False
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
        }
        
        try:
            response = requests.post(self.webhook, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("✓ 钉钉消息发送成功")
                    return True
                else:
                    print(f"✗ 钉钉消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"✗ 钉钉请求失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 发送钉钉消息时出错: {str(e)}")
            return False
    
    def format_jobs_message(self, new_jobs: List[Dict], total_count: int, excel_file: Optional[str] = None) -> tuple:
        """格式化岗位消息为Markdown格式（优化版：只显示最新50个，逻辑清晰）"""
        if not new_jobs:
            return None, None
        
        # 只取最新50个岗位
        display_jobs = new_jobs[:50] if len(new_jobs) > 50 else new_jobs
        remaining_count = len(new_jobs) - len(display_jobs)
        
        # 标题
        title = f"📢 招聘雷达 | 新增岗位 {len(new_jobs)} 个"
        
        # 按需求分类分组（按配置关键词分组）
        grouped_jobs = {}
        for job in display_jobs:
            group_key = job.get('config_keywords', '其他')
            if group_key not in grouped_jobs:
                grouped_jobs[group_key] = []
            grouped_jobs[group_key].append(job)
        
        # 构建Markdown内容（逻辑清晰，展示清晰）
        content_parts = []
        
        # 头部信息（清晰展示）
        content_parts.append(f"## 📢 招聘雷达\n\n")
        content_parts.append(f"**📅 抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        content_parts.append(f"**📊 本次新增**: {len(new_jobs)} 个岗位\n")
        content_parts.append(f"**💾 数据库总计**: {total_count} 个岗位\n\n")
        
        if excel_file:
            import os
            if os.path.exists(excel_file):
                file_size = os.path.getsize(excel_file) / (1024 * 1024)
                content_parts.append(f"**📁 Excel文件**: `{excel_file}` ({file_size:.1f}MB)\n\n")
        
        content_parts.append("---\n\n")
        
        # 岗位列表（按分类清晰展示）
        if len(display_jobs) > 0:
            content_parts.append(f"### 📋 最新岗位列表（显示前{len(display_jobs)}个）\n\n")
            
            # 按分组显示
            for idx, (group_key, jobs) in enumerate(grouped_jobs.items(), 1):
                if not jobs:
                    continue
                
                # 分组标题（清晰标识）
                content_parts.append(f"**{idx}. {group_key}** ({len(jobs)}个岗位)\n\n")
                
                # 岗位列表（格式清晰）
                for job_idx, job in enumerate(jobs, 1):
                    title_text = job.get('job_title', job.get('title', '未知岗位'))
                    url = job.get('url', '#')
                    company = job.get('company_name', job.get('company', '未知公司'))
                    location = job.get('work_location', job.get('location', '未知地点'))
                    recruit_type = job.get('recruit_type', '')
                    recruit_target = job.get('recruit_target', '')
                    
                    # 清晰的格式：岗位名 | 公司 | 地点 | 类型
                    line_parts = []
                    line_parts.append(f"   {job_idx}. **[{title_text}]({url})**")
                    
                    if company and company != '未知':
                        line_parts.append(f" | {company}")
                    
                    if location and location != '未知地点':
                        line_parts.append(f" | 📍 {location}")
                    
                    if recruit_type:
                        line_parts.append(f" | {recruit_type}")
                    
                    if recruit_target:
                        line_parts.append(f" | {recruit_target}")
                    
                    content_parts.append("".join(line_parts) + "\n")
                
                content_parts.append("\n")
        
        # 底部提示（如果有更多岗位）
        if remaining_count > 0:
            content_parts.append("---\n\n")
            content_parts.append(f"**💡 提示**: 还有 {remaining_count} 个岗位未显示，请查看Excel文件获取完整数据\n\n")
        
        content = "".join(content_parts)
        return title, content


# ==================== 爬虫模块 ====================

class JobScraper:
    """岗位抓取器"""
    
    def __init__(self, db_manager: DBManager):
        """初始化爬虫"""
        self.db = db_manager
        self.playwright = None
        self.browser = None
        self.page = None
    
    def start_browser(self, headless: bool = True):
        """启动浏览器"""
        print("正在启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = context.new_page()
        print("✓ 浏览器启动成功")
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("✓ 浏览器已关闭")
    
    def random_sleep(self, min_time: int = RANDOM_WAIT_MIN, max_time: int = RANDOM_WAIT_MAX):
        """随机休眠"""
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)
    
    def expand_city_list(self, locations: List[str]) -> List[str]:
        """展开城市列表"""
        expanded = []
        for loc in locations:
            if loc in CITY_MAPPING:
                expanded.extend(CITY_MAPPING[loc])
            else:
                expanded.append(loc)
        # 去重
        seen = set()
        result = []
        for city in expanded:
            if city not in seen:
                seen.add(city)
                result.append(city)
        return result
    
    def search_yingjiesheng(self, keyword: str, city: str, grad_year: Optional[int], 
                           recruit_type: str, config_keywords: str) -> List[Dict]:
        """在应届生求职网搜索岗位"""
        results = []
        
        try:
            keyword_encoded = urllib.parse.quote(keyword)
            city_encoded = urllib.parse.quote(city)
            
            # 应届生求职网的搜索URL格式
            # 实际URL格式：https://www.yingjiesheng.com/job/?keyword=关键词&city=城市
            if recruit_type == '校招' or '校招' in recruit_type or recruit_type == '实习' or grad_year:
                # 应届生求职网主要针对校招，使用标准搜索URL
                url = f"https://www.yingjiesheng.com/job/?keyword={keyword_encoded}&city={city_encoded}"
            else:
                return results
            
            print(f"    搜索应届生求职网: {keyword} | {city}")
            print(f"    URL: {url}")
            try:
                self.page.goto(url, wait_until="networkidle", timeout=20000)
                self.random_sleep(2, 3)  # 等待页面加载
            except Exception as e:
                print(f"    ⚠ 访问页面失败: {str(e)[:50]}")
                return results
            self.random_sleep(0.5, 1.5)  # 快速模式：减少等待时间
            
            # 等待页面加载
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                self.random_sleep(0.5, 1)  # 快速模式：减少等待时间
                
                # 尝试多种选择器（应届生求职网的常见选择器）
                selectors = [
                    '.job-list-item',
                    '.job-item',
                    '.job-info',
                    '[class*="job"]',
                    '.list-item',
                    'tr',  # 可能是表格形式
                ]
                
                job_elements = None
                for selector in selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        if elements and len(elements) > 1:  # 至少2个（排除表头）
                            # 过滤掉表头行
                            if selector == 'tr':
                                filtered = [e for e in elements if e.query_selector('a[href*="job"]') or e.query_selector('a[href*="/job-"]')]
                                if filtered:
                                    job_elements = filtered
                                    print(f"    ✓ 找到 {len(job_elements)} 个职位元素（选择器: {selector}）")
                                    break
                            else:
                                job_elements = elements
                                print(f"    ✓ 找到 {len(job_elements)} 个职位元素（选择器: {selector}）")
                                break
                    except:
                        continue
                
                if not job_elements:
                    print(f"    ⚠ 未找到职位列表，尝试其他方法...")
                    # 尝试获取页面标题确认是否加载成功
                    try:
                        title = self.page.title()
                        print(f"    页面标题: {title[:50]}")
                        # 尝试获取页面文本，看看是否有"职位"、"招聘"等关键词
                        page_text = self.page.inner_text('body')[:200]
                        if '职位' in page_text or '招聘' in page_text or '岗位' in page_text:
                            print(f"    ℹ 页面似乎已加载，但选择器不匹配")
                            # 尝试更通用的选择器
                            all_links = self.page.query_selector_all('a[href*="job"], a[href*="/job-"]')
                            if all_links:
                                print(f"    ✓ 找到 {len(all_links)} 个职位链接，尝试提取...")
                                job_elements = all_links[:20]  # 限制数量
                    except Exception as e:
                        print(f"    ⚠ 检查页面时出错: {str(e)[:30]}")
                    
                    if not job_elements:
                        return results
                
                # 提取职位信息
                for job_elem in job_elements[:15]:  # 限制每页15个
                    try:
                        # 提取职位名称和链接（优化：优先使用最常见的选择器）
                        job_title = None
                        job_link = None
                        
                        # 优先尝试链接元素（应届生求职网的链接格式）
                        try:
                            # 应届生求职网通常是表格形式，链接在第一列
                            link_elem = (job_elem.query_selector('td:first-child a') or 
                                        job_elem.query_selector('a[href*="/job-"]') or 
                                        job_elem.query_selector('a[href*="job"]') or 
                                        job_elem.query_selector('a'))
                            if link_elem:
                                job_title = link_elem.inner_text().strip()
                                href = link_elem.get_attribute('href')
                                if href:
                                    if href.startswith('http'):
                                        job_link = href
                                    elif href.startswith('/'):
                                        job_link = f"https://www.yingjiesheng.com{href}"
                                    else:
                                        job_link = f"https://www.yingjiesheng.com/{href}"
                        except:
                            pass
                        
                        # 如果上面没找到，再尝试其他选择器
                        if not job_title:
                            # 尝试从表格单元格获取
                            try:
                                first_td = job_elem.query_selector('td:first-child')
                                if first_td:
                                    job_title = first_td.inner_text().strip()
                                    link = first_td.query_selector('a')
                                    if link and not job_link:
                                        href = link.get_attribute('href')
                                        if href:
                                            if href.startswith('http'):
                                                job_link = href
                                            elif href.startswith('/'):
                                                job_link = f"https://www.yingjiesheng.com{href}"
                                            else:
                                                job_link = f"https://www.yingjiesheng.com/{href}"
                            except:
                                pass
                            
                            # 如果还是没找到，尝试其他选择器
                            if not job_title:
                                title_selectors = ['.job-name', '.job-title', '.title', 'h3', 'h4', '[class*="job-name"]', '[class*="title"]']
                                for sel in title_selectors[:3]:
                                    try:
                                        elem = job_elem.query_selector(sel)
                                        if elem:
                                            job_title = elem.inner_text().strip()
                                            break
                                    except:
                                        continue
                        
                        if not job_title or not job_link:
                            continue
                        
                        # 检查是否已存在
                        if self.db.is_job_exists(job_link):
                            continue
                        
                        # 提取公司名称（应届生求职网通常是表格，公司名在第二列）
                        company_name = '未知'
                        try:
                            # 优先尝试表格第二列
                            company_td = job_elem.query_selector('td:nth-child(2)')
                            if company_td:
                                company_name = company_td.inner_text().strip()
                        except:
                            pass
                        
                        if company_name == '未知' or not company_name:
                            company_selectors = ['.company-name', '.company', '[class*="company"]', '.firm-name', '.employer']
                            for sel in company_selectors[:3]:
                                try:
                                    elem = job_elem.query_selector(sel)
                                    if elem:
                                        company_name = elem.inner_text().strip()
                                        if company_name:
                                            break
                                except:
                                    continue
                        
                        # 提取工作地点（应届生求职网通常是表格，地点在第三列）
                        work_location = city  # 默认使用搜索的城市
                        try:
                            location_td = job_elem.query_selector('td:nth-child(3)')
                            if location_td:
                                work_location = location_td.inner_text().strip()
                        except:
                            pass
                        
                        if not work_location or work_location == city:
                            location_selectors = ['.city', '.location', '[class*="city"]', '[class*="location"]', '.work-place']
                            for sel in location_selectors[:3]:
                                try:
                                    elem = job_elem.query_selector(sel)
                                    if elem:
                                        work_location = elem.inner_text().strip()
                                        if work_location:
                                            break
                                except:
                                    continue
                        
                        # 提取更新时间（应届生求职网通常是表格，时间在第四列）
                        update_time = '未知'
                        try:
                            time_td = job_elem.query_selector('td:nth-child(4)')
                            if time_td:
                                update_time = time_td.inner_text().strip()
                        except:
                            pass
                        
                        if not update_time or update_time == '未知':
                            time_selectors = ['.update-time', '.time', '.publish-time', '[class*="time"]', '[class*="update"]']
                            for sel in time_selectors[:3]:
                                try:
                                    elem = job_elem.query_selector(sel)
                                    if elem:
                                        update_time = elem.inner_text().strip()
                                        if update_time:
                                            break
                                except:
                                    continue
                        
                        # 判断招聘类型
                        if '实习' in job_title or '实习' in company_name:
                            recruit_type_str = '实习'
                        elif recruit_type == '社招':
                            recruit_type_str = '社招'
                        else:
                            recruit_type_str = '校招'
                        
                        # 招聘对象
                        if grad_year:
                            if isinstance(grad_year, list):
                                recruit_target = f"{'/'.join(map(str, grad_year))}届"
                            else:
                                recruit_target = f"{grad_year}届"
                        else:
                            recruit_target = '不限'
                        
                        # 公司类型（列表页通常没有，设为未知，后续可进入详情页获取）
                        company_type = '未知'
                        
                        # 投递截止（列表页通常没有，设为默认值）
                        deadline = '详见链接'
                        
                        # 构建完整的岗位数据（包含所有9个字段）
                        job_data = {
                            'url': job_link,
                            'company_name': company_name,
                            'company_type': company_type,
                            'work_location': work_location,
                            'recruit_type': recruit_type_str,
                            'recruit_target': recruit_target,
                            'job_title': job_title,
                            'update_time': update_time,
                            'deadline': deadline,
                            'config_keywords': config_keywords,  # 用于消息分组
                        }
                        
                        # 保存到数据库（包含所有字段）
                        self.db.save_job({
                            'url': job_link,
                            'company_name': company_name,
                            'company_type': company_type,
                            'work_location': work_location,
                            'recruit_type': recruit_type_str,
                            'recruit_target': recruit_target,
                            'job_title': job_title,
                            'update_time': update_time,
                            'deadline': deadline,
                        })
                        
                        results.append(job_data)
                        
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"    ⚠ 解析页面时出错: {str(e)[:50]}")
        
        except Exception as e:
            print(f"    ✗ 搜索时出错: {str(e)[:50]}")
        
        return results
    
    def scrape_all_configs(self) -> List[Dict]:
        """抓取所有配置的岗位"""
        all_new_jobs = []
        
        total_configs = len(SEARCH_CONFIGS)
        print(f"\n开始抓取，共 {total_configs} 个配置...")
        
        for idx, config in enumerate(SEARCH_CONFIGS, 1):
            try:
                print(f"\n[{idx}/{total_configs}] 处理配置: {', '.join(config['keywords'][:2])}...")
                
                # 展开城市列表
                cities = self.expand_city_list(config['locations'])
                keywords = config['keywords']
                grad_year = config['grad_year']
                recruit_type = config['recruit_type']
                config_keywords = ', '.join(keywords[:3])
                
                # 遍历关键词和城市
                for keyword in keywords:
                    for city in cities:
                        if recruit_type == '校招' or '校招' in recruit_type or grad_year or recruit_type == '实习':
                            # 使用应届生求职网抓取
                            jobs = self.search_yingjiesheng(keyword, city, grad_year, recruit_type, config_keywords)
                            all_new_jobs.extend(jobs)
                            self.random_sleep(0.5, 1.5)  # 快速模式：减少等待时间
                
                print(f"  ✓ 本配置新增 {len([j for j in all_new_jobs if j.get('config_keywords') == config_keywords])} 个岗位")
                
            except Exception as e:
                print(f"  ✗ 处理配置时出错: {str(e)[:100]}")
                continue
        
        return all_new_jobs


# ==================== 调度模块 ====================

class Scheduler:
    """定时调度器"""
    
    def __init__(self, db_manager: DBManager, dingtalk_sender: DingTalkSender):
        """初始化调度器"""
        self.db = db_manager
        self.dingtalk = dingtalk_sender
        self.scraper = None
    
    def export_to_excel(self) -> Optional[str]:
        """导出所有岗位到Excel文件（包含所有9个字段）"""
        try:
            conn = sqlite3.connect(DB_FILE)
            df = pd.read_sql_query("""
                SELECT 
                    company_name as '公司名称',
                    company_type as '公司类型',
                    work_location as '工作地点',
                    recruit_type as '招聘类型',
                    recruit_target as '招聘对象',
                    job_title as '岗位(大都不限专业)',
                    update_time as '更新时间',
                    deadline as '投递截止',
                    url as '相关链接'
                FROM posted_jobs 
                ORDER BY created_at DESC
            """, conn)
            conn.close()
            
            if df.empty:
                return None
            
            # 生成文件名
            excel_file = f"job_hunting_results_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            # 保存到Excel
            df.to_excel(excel_file, index=False, engine='openpyxl')
            
            return excel_file
        except Exception as e:
            print(f"⚠ 导出Excel时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_once(self):
        """执行一次抓取任务"""
        print("\n" + "="*60)
        print(f"开始执行抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # 初始化爬虫
            self.scraper = JobScraper(self.db)
            self.scraper.start_browser(headless=True)
            
            # 抓取所有配置
            new_jobs = self.scraper.scrape_all_configs()
            
            # 关闭浏览器
            self.scraper.close_browser()
            
            # 统计信息
            total_count = self.db.get_total_count()
            
            print(f"\n✓ 抓取完成: 新增 {len(new_jobs)} 个岗位，数据库总计 {total_count} 个")
            
            # 导出Excel文件（包含所有岗位）
            excel_file = self.export_to_excel()
            if excel_file:
                print(f"✓ Excel文件已生成: {excel_file}")
            
            # 发送钉钉通知（只发送消息卡片，Excel文件信息不发送）
            if new_jobs:
                title, content = self.dingtalk.format_jobs_message(new_jobs, total_count, excel_file)
                if title and content:
                    # 只发送消息卡片
                    self.dingtalk.send_markdown(title, content)
                    if excel_file:
                        print(f"✓ Excel文件已保存到本地: {excel_file}")
            else:
                print("ℹ 本次无新增岗位，不发送通知")
            
        except Exception as e:
            print(f"\n✗ 执行任务时出错: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.scraper:
                self.scraper.close_browser()
    
    def run_forever(self):
        """持续运行调度器"""
        print("\n" + "="*60)
        print("招聘岗位定时抓取服务已启动")
        print("="*60)
        print(f"抓取间隔: {SCRAPE_INTERVAL // 3600} 小时")
        print(f"下次运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print("\n提示: 按 Ctrl+C 可停止服务\n")
        
        # 立即执行一次
        self.run_once()
        
        # 定时执行
        while True:
            try:
                # 等待指定时间
                print(f"\n等待 {SCRAPE_INTERVAL // 3600} 小时后执行下一次抓取...")
                time.sleep(SCRAPE_INTERVAL)
                
                # 执行任务
                self.run_once()
                
            except KeyboardInterrupt:
                print("\n\n收到停止信号，正在退出...")
                break
            except Exception as e:
                print(f"\n✗ 调度器出错: {str(e)}")
                import traceback
                traceback.print_exc()
                print(f"\n等待 {SCRAPE_INTERVAL // 3600} 小时后重试...")
                time.sleep(SCRAPE_INTERVAL)


# ==================== 主程序 ====================

def main():
    """主函数"""
    print("\n" + "="*60)
    print("招聘岗位定时抓取与钉钉推送脚本")
    print("="*60)
    print("\n⚠️  重要提示: 请务必保管好你的 DingTalk Token！")
    print("\n安装依赖:")
    print("  pip install playwright schedule requests")
    print("\n安装Playwright浏览器:")
    print("  playwright install chromium")
    print("="*60)
    
    # 初始化组件
    db_manager = DBManager()
    dingtalk_sender = DingTalkSender()
    scheduler = Scheduler(db_manager, dingtalk_sender)
    
    # 启动调度器
    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n程序异常退出: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

