'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Logo from './Logo';

interface SidebarProps {
  type: 'coach' | 'recruiter';
}

export default function Sidebar({ type }: SidebarProps) {
  const pathname = usePathname();

  const coachMenus = [
    { name: '仪表盘', path: '/coach', icon: '📊' },
    { name: '上传简历', path: '/coach/upload', icon: '📄' },
    { name: '学员管理', path: '/coach/students', icon: '👥' },
    { name: '匹配结果', path: '/coach/matching', icon: '🎯' },
  ];

  const recruiterMenus = [
    { name: '仪表盘', path: '/recruiter', icon: '📊' },
    { name: '上传岗位', path: '/recruiter/upload', icon: '📋' },
    { name: '岗位管理', path: '/recruiter/jobs', icon: '💼' },
  ];

  const menus = type === 'coach' ? coachMenus : recruiterMenus;

  return (
    <aside className="w-64 h-screen glass border-r border-white/10 p-6 flex flex-col">
      <Logo size="small" />
      
      <nav className="mt-10 flex-1">
        <ul className="space-y-2">
          {menus.map((menu) => {
            const isActive = pathname === menu.path;
            return (
              <li key={menu.path}>
                <Link
                  href={menu.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive 
                      ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-blue-500/30' 
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span className="text-xl">{menu.icon}</span>
                  <span>{menu.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
        <span>←</span>
        <span>返回首页</span>
      </Link>
    </aside>
  );
}
