'use client';

import { useState, useEffect } from 'react';

export default function CoachDashboard() {
  const [stats, setStats] = useState({
    totalStudents: 0,
    matchedStudents: 0,
    pendingReview: 0,
    successRate: 0
  });

  const statCards = [
    { label: '学员总数', value: stats.totalStudents, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: '已匹配', value: stats.matchedStudents, icon: '✅', color: 'from-green-500 to-emerald-500' },
    { label: '待处理', value: stats.pendingReview, icon: '⏳', color: 'from-yellow-500 to-orange-500' },
    { label: '匹配成功率', value: `${stats.successRate}%`, icon: '📈', color: 'from-purple-500 to-pink-500' },
  ];

  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">教练工作台</h1>
        <p className="text-gray-400 mt-2">管理学员简历，查看AI匹配结果</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="glass rounded-2xl p-6 card-hover">
            <div className="flex items-center justify-between mb-4">
              <span className="text-3xl">{stat.icon}</span>
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} opacity-20`} />
            </div>
            <p className="text-gray-400 text-sm">{stat.label}</p>
            <p className="text-3xl font-bold mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* 快捷操作 */}
      <div className="grid md:grid-cols-2 gap-6">
        <a href="/coach/upload" className="glass rounded-2xl p-8 card-hover group">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-3xl">
              📄
            </div>
            <div>
              <h3 className="text-xl font-bold">上传新简历</h3>
              <p className="text-gray-400 mt-1">支持 PDF、Word 或直接粘贴</p>
            </div>
          </div>
          <div className="flex items-center text-blue-400 mt-6 group-hover:translate-x-2 transition-transform">
            <span>开始上传</span>
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
        </a>

        <a href="/coach/matching" className="glass rounded-2xl p-8 card-hover group">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-3xl">
              🎯
            </div>
            <div>
              <h3 className="text-xl font-bold">查看匹配结果</h3>
              <p className="text-gray-400 mt-1">AI 智能推荐最适合的岗位</p>
            </div>
          </div>
          <div className="flex items-center text-purple-400 mt-6 group-hover:translate-x-2 transition-transform">
            <span>查看详情</span>
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
        </a>
      </div>

      {/* 最近上传的学员 */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-xl font-bold mb-6">最近上传</h2>
        <div className="text-center py-12 text-gray-400">
          <p className="text-6xl mb-4">📭</p>
          <p>暂无学员数据</p>
          <a href="/coach/upload" className="inline-block mt-4 text-blue-400 hover:underline">
            上传第一份简历 →
          </a>
        </div>
      </div>
    </div>
  );
}
