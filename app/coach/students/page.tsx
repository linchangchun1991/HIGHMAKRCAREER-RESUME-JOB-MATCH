'use client';

export default function StudentsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">学员管理</h1>
        <p className="text-gray-400 mt-2">查看和管理所有学员信息</p>
      </div>

      <div className="glass rounded-2xl p-12 text-center">
        <div className="text-6xl mb-4">👥</div>
        <p className="text-gray-400">暂无学员数据</p>
        <a href="/coach/upload" className="inline-block mt-4 text-blue-400 hover:underline">
          上传第一份简历 →
        </a>
      </div>
    </div>
  );
}
