#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预览钉钉消息完整内容（带所有原文链接）
"""

import pandas as pd
import os
from datetime import datetime

def generate_complete_dingtalk_message():
    """
    生成完整的钉钉消息，确保每条情报都有原文链接
    """
    # 读取报告
    report_file = f"Market_Radar_{datetime.now().strftime('%Y-%m-%d')}.md"
    if not os.path.exists(report_file):
        return "报告文件不存在"
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 读取原始数据
    df = pd.read_csv('raw_data.csv', encoding='utf-8-sig')
    
    # 构建完整的消息
    message = f"""# 海马职加·市场雷达日报

**📅 生成时间**: {datetime.now().strftime('%Y年%m月%d日')}  
**📊 数据周期**: 最近3天  
**🔍 监测平台**: 抖音、小红书、搜狗微信  
**📈 数据统计**: 抖音 {len(df[df['平台'] == '抖音'])} 条，小红书 {len(df[df['平台'] == '小红书'])} 条，搜狗微信 {len(df[df['平台'] == '搜狗微信'])} 条

---

## ⚔️ 竞品动作监测 (Competitor Moves)

"""
    
    # 按平台和关键词组织数据，确保每条都有链接
    platforms_data = {
        '抖音': df[df['平台'] == '抖音'],
        '小红书': df[df['平台'] == '小红书'],
        '搜狗微信': df[df['平台'] == '搜狗微信']
    }
    
    platform_icons = {'抖音': '🎵', '小红书': '📕', '搜狗微信': '🟢'}
    
    for platform, platform_df in platforms_data.items():
        if len(platform_df) > 0:
            icon = platform_icons.get(platform, '📄')
            message += f"### {icon} {platform}平台\n\n"
            
            for keyword in ['DBC职梦', '途鸽求职', 'Offer先生', '爱思益', '海马职加']:
                keyword_data = platform_df[platform_df['关键词'] == keyword]
                if len(keyword_data) > 0:
                    message += f"**{keyword}**：\n"
                    for idx, (_, row) in enumerate(keyword_data.head(5).iterrows(), 1):
                        title = str(row.get('标题', '')).strip()
                        if not title or title == 'nan':
                            title = f"{platform}内容 {idx}"
                        url = str(row.get('链接', '')).strip()
                        
                        if url and url != 'nan':
                            message += f"{idx}. {title[:80]}  🔗 [查看原文]({url})\n"
                        else:
                            message += f"{idx}. {title[:80]}  ⚠️ 链接缺失\n"
                    message += "\n"
    
    # 添加报告的核心分析部分
    message += """
---

## 📢 用户舆情透视 (Voice of Customer)

"""
    
    # 从报告中提取用户舆情部分
    if "## 📢 用户舆情透视" in report_content:
        start_idx = report_content.find("## 📢 用户舆情透视")
        end_idx = report_content.find("## 🧭 我们的战略启示")
        if end_idx > start_idx:
            voc_section = report_content[start_idx:end_idx].strip()
            message += voc_section + "\n\n"
    
    message += """
---

## 🧭 我们的战略启示 (Strategic Insights)

"""
    
    # 从报告中提取战略启示部分
    if "## 🧭 我们的战略启示" in report_content:
        start_idx = report_content.find("## 🧭 我们的战略启示")
        strategy_section = report_content[start_idx:].strip()
        message += strategy_section + "\n"
    
    return message

if __name__ == "__main__":
    message = generate_complete_dingtalk_message()
    
    print("=" * 80)
    print("【完整钉钉消息模板 - 每条情报都带原文链接】")
    print("=" * 80)
    print(message)
    print("=" * 80)
    print(f"\n消息长度: {len(message)} 字符")
    
    # 保存到文件
    with open('dingtalk_message_preview.md', 'w', encoding='utf-8') as f:
        f.write(message)
    print("\n✓ 消息已保存到: dingtalk_message_preview.md")
