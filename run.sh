#!/bin/bash
# 每日内推信息抓取 - 快速启动脚本

echo "================================="
echo "  每日内推信息自动抓取工具"
echo "================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python3: brew install python3"
    exit 1
fi

echo "✓ Python3已安装"

# 检查依赖
echo "正在检查依赖包..."
python3 -c "import selenium, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo "✓ 依赖包完整"
echo ""

# 运行脚本
echo "开始抓取内推信息..."
echo ""
python3 daily_referral_scraper_v2.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "================================="
    echo "  ✅ 任务执行成功！"
    echo "================================="
    echo ""
    echo "生成的文件在桌面:"
    echo "  📄 今日内推汇总_$(date +%Y-%m-%d).md"
    echo "  📊 每日内推.xlsx"
    echo ""
    
    # 询问是否打开文件
    read -p "是否打开生成的报告？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open ~/Desktop/今日内推汇总_$(date +%Y-%m-%d).md
    fi
else
    echo ""
    echo "================================="
    echo "  ❌ 任务执行失败"
    echo "================================="
    echo ""
    echo "请检查错误信息并重试"
    exit 1
fi
