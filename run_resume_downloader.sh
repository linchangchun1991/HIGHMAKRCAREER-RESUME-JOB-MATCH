#!/bin/bash
# 简历下载启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "简历批量下载工具"
echo "=========================================="
echo ""
echo "脚本将打开浏览器，请按以下步骤操作："
echo "1. 在浏览器中完成登录"
echo "2. 等待脚本自动下载所有简历"
echo "3. 下载完成后，所有文件将保存在 resumes 文件夹中"
echo ""
echo "按回车开始..."
read

# 运行Python脚本
python3 resume_downloader.py

# 检查下载结果
echo ""
echo "=========================================="
echo "下载完成！检查结果..."
echo "=========================================="
python3 check_downloads.py

# 打开文件夹（macOS）
if [ -d "resumes" ]; then
    echo ""
    echo "正在打开下载文件夹..."
    open resumes
fi

