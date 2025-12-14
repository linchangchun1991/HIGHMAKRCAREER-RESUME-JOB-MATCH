#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘岗位抓取配置列表（适配main.py的导入）
从config.py导入配置
"""

# 直接从config.py导入配置
from config import SEARCH_CONFIGS, CITY_MAPPING

# 为了测试，可以创建一个简化的配置列表
# 如果要做快速测试，可以取消下面的注释并注释掉上面的导入

# 测试用简化配置（只包含1个配置项，快速测试）
TEST_SEARCH_CONFIGS = [
    {
        'keywords': ['数据分析', '商业分析'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    }
]

# 快速测试配置（3个配置项，便于快速查看结果）
QUICK_TEST_CONFIGS = [
    {
        'keywords': ['数据分析', '商业分析'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['法务', '法律'],
        'locations': ['北京', '深圳'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['审计', '财务'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': '四大',
        'education': None,
        'company_type': None,
    }
]

# 使用快速测试配置
SEARCH_CONFIGS = QUICK_TEST_CONFIGS
TEST_CONFIGS_WITH_MORE = [
    {
        'keywords': ['数据分析'],
        'locations': ['上海'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['产品经理'],
        'locations': ['北京'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['运营'],
        'locations': ['深圳'],
        'grad_year': 2026,
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    }
]

# 临时使用测试配置（搜索3个岗位，便于查看结果）
SEARCH_CONFIGS = TEST_CONFIGS_WITH_MORE
