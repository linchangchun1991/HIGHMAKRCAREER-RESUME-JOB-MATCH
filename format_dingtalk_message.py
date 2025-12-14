#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化市场雷达日报为钉钉消息（确保所有链接完整）
"""

import pandas as pd
import os
from datetime import datetime

def format_dingtalk_message_with_links():
    """
    格式化报告，确保每条情报都包含原文链接
    """
    # 读取报告
    report_file = f"Market_Radar_{datetime.now().strftime('%Y-%m-%d')}.md"
    if not os.path.exists(report_file):
        return "报告文件不存在"
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 读取原始数据，构建链接映射
    links_by_keyword = {}
    try:
        if os.path.exists('raw_data.csv'):
            df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
            for _, row in df.iterrows():
                platform = str(row.get('平台', ''))
                keyword = str(row.get('关键词', ''))
                title = str(row.get('标题', ''))
                url = str(row.get('链接', ''))
                
                if url and url != 'nan' and url.strip():
                    key = f"{platform}_{keyword}"
                    if key not in links_by_keyword:
                        links_by_keyword[key] = []
                    links_by_keyword[key].append({
                        'title': title,
                        'url': url,
                        'platform': platform
                    })
    except Exception as e:
        print(f"读取CSV失败: {str(e)}")
    
    # 构建完整的钉钉消息
    message = f"""# 海马职加·市场雷达日报

**📅 生成时间**: {datetime.now().strftime('%Y年%m月%d日')}  
**📊 数据周期**: 最近3天  
**🔍 监测平台**: 抖音、小红书、搜狗微信

---

## ⚔️ 竞品动作监测 (Competitor Moves)

"""
    
    # 按平台和关键词组织数据
    try:
        df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
        
        # 抖音数据
        douyin_data = df[df['平台'] == '抖音']
        if len(douyin_data) > 0:
            message += "### 🎵 抖音平台\n\n"
            for keyword in ['DBC职梦', '途鸽求职', 'Offer先生', '爱思益', '海马职加']:
                keyword_data = douyin_data[douyin_data['关键词'] == keyword]
                if len(keyword_data) > 0:
                    message += f"**{keyword}**：\n"
                    for _, row in keyword_data.head(3).iterrows():
                        title = str(row.get('标题', ''))[:50]
                        url = str(row.get('链接', ''))
                        if url and url != 'nan':
                            message += f"- {title}  🔗 [查看原文]({url})\n"
                    message += "\n"
        
        # 小红书数据
        xhs_data = df[df['平台'] == '小红书']
        if len(xhs_data) > 0:
            message += "### 📕 小红书平台\n\n"
            for keyword in ['DBC职梦', '途鸽求职', 'Offer先生', '爱思益', '海马职加']:
                keyword_data = xhs_data[xhs_data['关键词'] == keyword]
                if len(keyword_data) > 0:
                    message += f"**{keyword}**：\n"
                    for _, row in keyword_data.head(3).iterrows():
                        title = str(row.get('标题', ''))[:50]
                        url = str(row.get('链接', ''))
                        if url and url != 'nan':
                            message += f"- {title}  🔗 [查看原文]({url})\n"
                    message += "\n"
        
        # 搜狗微信数据
        wechat_data = df[df['平台'] == '搜狗微信']
        if len(wechat_data) > 0:
            message += "### 🟢 搜狗微信平台\n\n"
            for keyword in ['DBC职梦', '途鸽求职', 'Offer先生', '爱思益', '海马职加']:
                keyword_data = wechat_data[wechat_data['关键词'] == keyword]
                if len(keyword_data) > 0:
                    message += f"**{keyword}**：\n"
                    for _, row in keyword_data.head(3).iterrows():
                        title = str(row.get('标题', ''))[:50]
                        url = str(row.get('链接', ''))
                        if url and url != 'nan':
                            message += f"- {title}  🔗 [查看原文]({url})\n"
                    message += "\n"
    
    except Exception as e:
        print(f"处理数据失败: {str(e)}")
    
    # 添加报告的核心内容（用户舆情和战略启示）
    message += """
---

## 📢 用户舆情透视 (Voice of Customer)

"""
    
    # 从报告中提取用户舆情部分
    if "## 📢 用户舆情透视" in report_content:
        start_idx = report_content.find("## 📢 用户舆情透视")
        end_idx = report_content.find("## 🧭 我们的战略启示")
        if end_idx > start_idx:
            voc_section = report_content[start_idx:end_idx]
            message += voc_section + "\n\n"
    
    message += """
---

## 🧭 我们的战略启示 (Strategic Insights)

"""
    
    # 从报告中提取战略启示部分
    if "## 🧭 我们的战略启示" in report_content:
        start_idx = report_content.find("## 🧭 我们的战略启示")
        message += report_content[start_idx:] + "\n"
    
    return message

if __name__ == "__main__":
    message = format_dingtalk_message_with_links()
    
    print("=" * 80)
    print("【完整钉钉消息模板 - 带所有原文链接】")
    print("=" * 80)
    print(message)
    print("=" * 80)
    print(f"\n消息长度: {len(message)} 字符")
