#!/bin/bash

# HIGHMARK CAREER 简历分析工具 - Vercel 部署脚本

echo "🚀 HIGHMARK CAREER 部署到 Vercel"
echo "================================"
echo ""

# 检查是否已安装 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 正在安装 Vercel CLI..."
    npm install -g vercel
    echo "✅ Vercel CLI 安装完成"
    echo ""
fi

# 检查是否已登录
echo "🔐 检查登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "请先登录 Vercel..."
    vercel login
fi

echo ""
echo "📤 开始部署..."
echo ""

# 部署到生产环境
vercel --prod

echo ""
echo "✅ 部署完成！"
echo ""
echo "💡 提示："
echo "   - 部署后你会得到一个公开的 URL"
echo "   - 可以在 Vercel 控制台查看和管理项目"
echo "   - 每次运行此脚本都会更新部署"
echo ""
