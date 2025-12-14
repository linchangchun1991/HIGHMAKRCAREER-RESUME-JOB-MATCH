#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试教育场景过滤器
"""

# 教育相关关键词（至少命中1个才保留）
EDUCATION_KEYWORDS = [
    # 服务类型
    '辅导', '网课', '论文', '作业', '课程', '留学', '补习',
    '学术', '考试', '挂科', 'GPA', '学分', '毕业', '答疑',
    # 学科相关
    '数学', '统计', '会计', '金融', '经济', '商科', '工程',
    '计算机', '编程', 'CS', '物理', '化学', '生物',
    # 学校相关
    '大学', '本科', '硕士', '研究生', '博士', '留学生',
    '英国', '澳洲', '美国', '加拿大', '香港', '新加坡',
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

def is_education_related(title, content=""):
    """判断内容是否与教育相关"""
    if not title:
        return False
    
    text = f"{title} {content}".lower()
    
    # 排除明显无关的
    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False
    
    # 必须包含教育关键词
    for kw in EDUCATION_KEYWORDS:
        if kw in text:
            return True
    
    return False

# 测试用例
test_contents = [
    {"title": "路觅留学辅导怎么样？有人用过吗", "content": "想找个辅导机构补习统计"},
    {"title": "路觅咖啡车来啦！京西古道徒步必打卡", "content": "风里雪里等你"},
    {"title": "路觅斯德训鞋开箱测评", "content": "这双鞋颜值太高了"},
    {"title": "考而思的网课质量如何？价格贵吗", "content": "留学生课程辅导"},
    {"title": "辅无忧论文辅导靠谱吗", "content": "有没有用过的同学分享下"},
    {"title": "路觅万里茶路觅商脉，乔家大院酒业", "content": "晋商文化"},
    {"title": "万能班长留学辅导服务怎么样", "content": "想了解下价格和导师水平"},
]

print("=" * 80)
print("【教育场景过滤器测试】")
print("=" * 80)

for item in test_contents:
    result = is_education_related(item['title'], item['content'])
    status = "✅" if result else "❌"
    print(f"{status} {item['title'][:50]}")

print("=" * 80)
print("期望输出：")
print("✅ 路觅留学辅导怎么样？有人用过吗")
print("❌ 路觅咖啡车来啦！京西古道徒步必打卡")
print("❌ 路觅斯德训鞋开箱测评")
print("✅ 考而思的网课质量如何？价格贵吗")
print("✅ 辅无忧论文辅导靠谱吗")
print("❌ 路觅万里茶路觅商脉，乔家大院酒业")
print("✅ 万能班长留学辅导服务怎么样")
print("=" * 80)
