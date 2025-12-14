#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查下载进度"""

import os
from pathlib import Path
from datetime import datetime

download_dir = Path(__file__).parent / 'resumes'

if download_dir.exists():
    files = list(download_dir.glob('*'))
    # 排除HTML调试文件
    resume_files = [f for f in files if not f.name.startswith('page_debug')]
    
    print(f"\n下载目录: {download_dir}")
    print(f"找到 {len(resume_files)} 个简历文件\n")
    
    if resume_files:
        print("已下载的简历：")
        for i, file in enumerate(sorted(resume_files), 1):
            size = file.stat().st_size / 1024  # KB
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  {i}. {file.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print("还没有下载任何文件")
        print("\n提示：")
        print("1. 确保已在浏览器中完成登录")
        print("2. 等待脚本自动下载")
        print("3. 如果长时间没有下载，请检查浏览器窗口是否有错误提示")
else:
    print(f"下载目录不存在: {download_dir}")

