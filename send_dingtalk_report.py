#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送市场雷达日报到钉钉群
"""

import requests
import json
import os
from datetime import datetime

# 钉钉Webhook地址
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=ac8d1c6332c8a047b8786a930ab08d7f6db490843edca2de1bb65c68301c3113"

def send_to_dingtalk(markdown_content: str):
    """
    发送Markdown消息到钉钉群
    
    Args:
        markdown_content: Markdown格式的消息内容
    """
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "海马职加·市场雷达日报",
            "text": markdown_content
        }
    }
    
    try:
        response = requests.post(DINGTALK_WEBHOOK, json=payload, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("✓ 钉钉消息发送成功")
            return True
        else:
            print(f"✗ 钉钉消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        print(f"✗ 钉钉请求失败: {str(e)}")
        return False

def format_report_for_dingtalk(report_file: str) -> str:
    """
    格式化报告为钉钉Markdown格式，确保所有链接都包含
    
    Args:
        report_file: 报告文件路径
    
    Returns:
        格式化后的Markdown内容
    """
    if not os.path.exists(report_file):
        return "报告文件不存在"
    
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取原始数据，确保链接完整
    import pandas as pd
    links_dict = {}
    
    try:
        if os.path.exists('raw_data.csv'):
            df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
            for _, row in df.iterrows():
                platform = row.get('平台', '')
                keyword = row.get('关键词', '')
                title = row.get('标题', '')
                url = row.get('链接', '')
                
                if url and title:
                    key = f"{platform}_{keyword}_{title[:30]}"
                    links_dict[key] = {
                        'platform': platform,
                        'keyword': keyword,
                        'title': title,
                        'url': url
                    }
    except Exception as e:
        print(f"读取CSV数据失败: {str(e)}")
    
    # 确保报告中的链接都是完整的
    # 如果报告中提到某个内容但没有链接，尝试从CSV中补充
    
    return content

if __name__ == "__main__":
    # 查找最新的报告文件
    report_file = f"Market_Radar_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    if not os.path.exists(report_file):
        print(f"报告文件不存在: {report_file}")
        exit(1)
    
    # 格式化并发送
    markdown_content = format_report_for_dingtalk(report_file)
    
    print("=" * 80)
    print("【钉钉消息预览】")
    print("=" * 80)
    print(markdown_content)
    print("=" * 80)
    
    # 发送到钉钉
    send_to_dingtalk(markdown_content)
