#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘岗位抓取配置列表
解析后的搜索配置，用于自动化抓取脚本
"""

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
        'locations': ['非偏远地区'],  # 需要转换为具体城市列表
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
        'locations': ['南方城市'],  # 需要转换为具体城市列表
        'grad_year': [2025, 2026],  # 25/26届
        'recruit_type': '校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['CSR', 'ESG', '咨询', '行研', '政策研究', '市场调研'],
        'locations': ['广州', '珠三角'],  # 珠三角需要转换为具体城市
        'grad_year': 2025,
        'recruit_type': '社招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['精算师'],
        'locations': ['一线城市'],  # 需要转换为具体城市列表
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
        'grad_year': None,  # 社招/校招
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': '中学/大学',
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['政府事务', '国际组织'],
        'locations': ['全国'],
        'grad_year': None,  # 社招/校招
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
    {
        'keywords': ['国际学校非教职', '辅导员', '教务'],
        'locations': ['杭州'],
        'grad_year': None,  # 社招/校招
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
        'grad_year': None,  # 社招(2年)
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
        'locations': ['东三省', '北京'],  # 东三省需要转换为具体城市
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
        'locations': ['北方二线城市'],  # 需要转换为具体城市列表
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
        'locations': ['广东'],  # 需要转换为具体城市或保持为省
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
        'locations': ['广东'],  # 需要转换为具体城市或保持为省
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
        'grad_year': None,  # 社招/校招
        'recruit_type': '社招/校招',
        'industry': None,
        'notes': None,
        'education': None,
        'company_type': None,
    },
]

# 城市映射配置（用于将模糊地区转换为具体城市列表）
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

# 统计信息
def get_config_stats():
    """获取配置统计信息"""
    total_configs = len(SEARCH_CONFIGS)
    grad_years = {}
    recruit_types = {}
    total_keywords = set()
    total_locations = set()
    
    for config in SEARCH_CONFIGS:
        # 统计届数
        grad_year = config['grad_year']
        if isinstance(grad_year, list):
            for year in grad_year:
                grad_years[year] = grad_years.get(year, 0) + 1
        elif grad_year:
            grad_years[grad_year] = grad_years.get(grad_year, 0) + 1
        
        # 统计招聘类型
        recruit_type = config['recruit_type']
        recruit_types[recruit_type] = recruit_types.get(recruit_type, 0) + 1
        
        # 统计关键词
        total_keywords.update(config['keywords'])
        
        # 统计城市
        for loc in config['locations']:
            if loc in CITY_MAPPING:
                total_locations.update(CITY_MAPPING[loc])
            else:
                total_locations.add(loc)
    
    return {
        'total_configs': total_configs,
        'grad_years': grad_years,
        'recruit_types': recruit_types,
        'total_keywords_count': len(total_keywords),
        'total_locations_count': len(total_locations),
    }


if __name__ == '__main__':
    # 打印配置统计信息
    stats = get_config_stats()
    print("=" * 60)
    print("招聘岗位抓取配置列表")
    print("=" * 60)
    print(f"\n总配置数: {stats['total_configs']}")
    print(f"\n届数分布:")
    for year, count in sorted(stats['grad_years'].items()):
        print(f"  {year}届: {count}个配置")
    print(f"\n招聘类型分布:")
    for rtype, count in sorted(stats['recruit_types'].items()):
        print(f"  {rtype}: {count}个配置")
    print(f"\n总关键词数: {stats['total_keywords_count']}")
    print(f"总城市数: {stats['total_locations_count']}")
    print("\n" + "=" * 60)
    print("\n配置列表预览（前5个）:")
    print("-" * 60)
    for i, config in enumerate(SEARCH_CONFIGS[:5], 1):
        print(f"\n配置 {i}:")
        print(f"  关键词: {', '.join(config['keywords'])}")
        print(f"  城市: {', '.join(config['locations'])}")
        print(f"  届数: {config['grad_year']}")
        print(f"  类型: {config['recruit_type']}")
        if config['notes']:
            print(f"  备注: {config['notes']}")
        if config['company_type']:
            print(f"  公司类型: {config['company_type']}")

