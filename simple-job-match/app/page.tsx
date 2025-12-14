'use client';

import { useState } from 'react';

interface MatchResult {
  jobName: string;
  matchScore: string;
  reason: string;
  advice: string;
}

export default function Home() {
  const [resume, setResume] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleMatch = async () => {
    if (!resume.trim()) {
      setError('请输入简历内容');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resume }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '匹配失败');
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message || '匹配失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-800 mb-3">
            AI 简历匹配助手
          </h1>
          <p className="text-gray-600 text-lg">
            智能分析你的简历，为你推荐最匹配的岗位
          </p>
        </div>

        {/* 输入区域 */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <label className="block text-gray-700 font-semibold mb-3 text-lg">
            简历内容
          </label>
          <textarea
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            placeholder="请把你的简历粘贴在这里..."
            className="w-full h-64 p-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none resize-none text-gray-700 placeholder-gray-400 transition-colors"
          />
          <button
            onClick={handleMatch}
            disabled={loading}
            className="mt-6 w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-4 px-8 rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                正在匹配中...
              </span>
            ) : (
              '立即匹配'
            )}
          </button>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-lg mb-8">
            <p className="font-semibold">错误</p>
            <p>{error}</p>
          </div>
        )}

        {/* 结果展示 */}
        {result && (
          <div className="bg-white rounded-2xl shadow-xl p-8 animate-fade-in">
            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
              匹配结果
            </h2>
            
            <div className="space-y-6">
              {/* 岗位名称 */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-xl">
                <div className="text-sm font-medium opacity-90 mb-1">推荐岗位</div>
                <div className="text-2xl font-bold">{result.jobName}</div>
              </div>

              {/* 匹配分数 */}
              <div className="bg-gray-50 p-6 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-700 font-semibold">匹配度</span>
                  <span className="text-3xl font-bold text-blue-600">{result.matchScore}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${result.matchScore}%` }}
                  ></div>
                </div>
              </div>

              {/* 推荐理由 */}
              <div className="bg-blue-50 p-6 rounded-xl border-l-4 border-blue-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  推荐理由
                </h3>
                <p className="text-gray-700 leading-relaxed">{result.reason}</p>
              </div>

              {/* 改进建议 */}
              <div className="bg-amber-50 p-6 rounded-xl border-l-4 border-amber-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  改进建议
                </h3>
                <p className="text-gray-700 leading-relaxed">{result.advice}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
