'use client';

import { useRouter } from 'next/navigation';
import Logo from '@/components/layout/Logo';
import { motion } from 'framer-motion';

export default function Home() {
  const router = useRouter();

  const roles = [
    {
      id: 'coach',
      title: '教练端',
      subtitle: 'Coach Portal',
      description: '上传学员简历，AI智能匹配岗位',
      icon: '👨‍🏫',
      gradient: 'from-blue-500 to-cyan-500',
      path: '/coach'
    },
    {
      id: 'recruiter',
      title: '企拓端',
      subtitle: 'Recruiter Portal',
      description: '批量上传岗位，管理招聘需求',
      icon: '🏢',
      gradient: 'from-purple-500 to-pink-500',
      path: '/recruiter'
    }
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '-3s' }} />
      </div>

      {/* Logo */}
      <div className="mb-16 animate-fade-in">
        <Logo size="large" />
      </div>

      {/* 标题 */}
      <h1 className="text-4xl md:text-5xl font-bold text-center mb-4">
        <span className="gradient-text">智能选岗系统</span>
      </h1>
      <p className="text-gray-400 text-lg mb-16 text-center max-w-xl">
        基于AI大模型的人岗匹配平台，为学员精准推荐最适合的职位
      </p>

      {/* 角色选择卡片 */}
      <div className="grid md:grid-cols-2 gap-8 max-w-4xl w-full">
        {roles.map((role, index) => (
          <motion.div
            key={role.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => router.push(role.path)}
            className="glass rounded-2xl p-8 cursor-pointer card-hover group"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${role.gradient} flex items-center justify-center text-3xl shadow-lg`}>
                {role.icon}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{role.title}</h2>
                <p className="text-gray-400 text-sm">{role.subtitle}</p>
              </div>
            </div>
            <p className="text-gray-300 mb-6">{role.description}</p>
            <div className="flex items-center text-blue-400 group-hover:translate-x-2 transition-transform">
              <span>进入系统</span>
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </motion.div>
        ))}
      </div>

      {/* 底部版权 */}
      <footer className="mt-20 text-gray-500 text-sm">
        © 2024 HIGHMARK 海马职加. All rights reserved.
      </footer>
    </main>
  );
}
