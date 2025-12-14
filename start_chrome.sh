#!/bin/bash
# 启动Chrome浏览器（调试模式）

# 关闭可能存在的Chrome进程
pkill -f "Google Chrome.*remote-debugging-port" 2>/dev/null
sleep 1

# 启动Chrome（调试模式）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  > /dev/null 2>&1 &

echo "✓ Chrome浏览器已启动（调试模式，端口9222）"
echo ""
echo "请在浏览器中："
echo "1. 登录系统: https://www.xianfasj.com"
echo "2. 导航到通话记录查询页面"
echo "3. 完成后运行: python3 call_quality_check.py"

