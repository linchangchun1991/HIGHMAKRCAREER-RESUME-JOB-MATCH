'use client';

import { useState } from 'react';

export default function RecruiterDashboard() {
  const [stats] = useState({
    totalJobs: 0,
    activeJobs: 0,
    matchedStudents: 0,
    companies: 0
  });

  const statCards = [
    { label: '岗位总数', value: stats.totalJobs, icon: '💼', color: 'from-blue-500 to-cyan-500' },
    { label: '在招岗位', value: stats.activeJobs, icon: '✅', color: 'from-green-500 to-emerald-500' },
    { label: '已匹配学员', value: stats.matchedStudents, icon: '🎯', color: 'from-purple-500 to-pink-500' },
    { label: '合作企业', value: stats.companies, icon: '🏢', color: 'from-orange-500 to-red-500' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">企拓工作台</h1>
        <p className="text-gray-400 mt-2">管理岗位信息，跟踪匹配情况</p>
      </div>

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

      <div className="grid md:grid-cols-2 gap-6">
        <a href="/recruiter/upload" className="glass rounded-2xl p-8 card-hover group">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-3xl">
              📋
            </div>
            <div>
              <h3 className="text-xl font-bold">批量上传岗位</h3>
              <p className="text-gray-400 mt-1">支持 Excel 批量导入</p>
            </div>
          </div>
        </a>

        <a href="/recruiter/jobs" className="glass rounded-2xl p-8 card-hover group">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-3xl">
              💼
            </div>
            <div>
              <h3 className="text-xl font-bold">岗位管理</h3>
              <p className="text-gray-400 mt-1">查看和管理所有岗位</p>
            </div>
          </div>
        </a>
      </div>
    </div>
  );
}
