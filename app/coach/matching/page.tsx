'use client';

export default function MatchingPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">匹配结果</h1>
        <p className="text-gray-400 mt-2">查看AI智能匹配的岗位推荐</p>
      </div>

      <div className="glass rounded-2xl p-12 text-center">
        <div className="text-6xl mb-4">🎯</div>
        <p className="text-gray-400">暂无匹配结果</p>
        <a href="/coach/upload" className="inline-block mt-4 text-blue-400 hover:underline">
          上传简历开始匹配 →
        </a>
      </div>
    </div>
  );
}
