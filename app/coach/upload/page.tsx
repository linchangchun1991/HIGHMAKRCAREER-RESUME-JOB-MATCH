'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export default function UploadResume() {
  const [content, setContent] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [parsedData, setParsedData] = useState<any>(null);
  const [matchResults, setMatchResults] = useState<any[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/resume/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setContent(data.content || '');
    } catch (error) {
      console.error('Upload error:', error);
      alert('上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const handleParse = async () => {
    if (!content.trim()) return;

    setIsParsing(true);
    try {
      const response = await fetch('/api/resume/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      const data = await response.json();
      if (data.success) {
        setParsedData(data.parsed);
        setMatchResults(data.matches || []);
      } else {
        alert('解析失败：' + (data.error || '未知错误'));
      }
    } catch (error) {
      console.error('Parse error:', error);
      alert('解析失败，请检查网络连接和API配置');
    } finally {
      setIsParsing(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold">上传学员简历</h1>
        <p className="text-gray-400 mt-2">支持 PDF、Word 文档或直接粘贴简历内容</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* 左侧：上传区域 */}
        <div className="space-y-6">
          {/* 拖拽上传 */}
          <div
            {...getRootProps()}
            className={`glass rounded-2xl p-12 border-2 border-dashed transition-all cursor-pointer text-center ${
              isDragActive ? 'border-blue-500 bg-blue-500/10' : 'border-gray-600 hover:border-gray-500'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-6xl mb-4">📁</div>
            {isUploading ? (
              <p className="text-gray-400">正在上传...</p>
            ) : isDragActive ? (
              <p className="text-blue-400">放开即可上传</p>
            ) : (
              <>
                <p className="text-gray-300">拖拽文件到这里，或点击选择</p>
                <p className="text-gray-500 text-sm mt-2">支持 PDF、DOC、DOCX</p>
              </>
            )}
          </div>

          {/* 或者粘贴 */}
          <div className="text-center text-gray-500">—— 或者 ——</div>

          {/* 文本输入 */}
          <div className="glass rounded-2xl p-6">
            <label className="block text-sm font-medium mb-3">直接粘贴简历内容</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="在这里粘贴简历文本内容..."
              className="w-full h-64 bg-black/30 rounded-xl p-4 text-gray-300 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none"
            />
          </div>

          {/* 解析按钮 */}
          <button
            onClick={handleParse}
            disabled={!content.trim() || isParsing}
            className={`w-full py-4 rounded-xl font-medium transition-all ${
              content.trim() && !isParsing
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:opacity-90'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isParsing ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                AI 正在解析...
              </span>
            ) : (
              '🚀 AI 智能解析并匹配岗位'
            )}
          </button>
        </div>

        {/* 右侧：解析结果 */}
        <div className="space-y-6">
          {parsedData ? (
            <>
              {/* 解析出的信息 */}
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>✅</span> 简历解析结果
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <InfoItem label="姓名" value={parsedData.name} />
                  <InfoItem label="学历" value={parsedData.education} />
                  <InfoItem label="专业" value={parsedData.major} />
                  <InfoItem label="毕业年份" value={parsedData.graduationYear} />
                  <InfoItem label="目标岗位" value={parsedData.targetPosition} />
                  <InfoItem label="目标城市" value={parsedData.targetCity} />
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">技能标签</p>
                  <div className="flex flex-wrap gap-2">
                    {parsedData.skills?.map((skill: string, i: number) => (
                      <span key={i} className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* 匹配结果 */}
              {matchResults.length > 0 && (
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <span>🎯</span> AI 推荐岗位 TOP {matchResults.length}
                  </h3>
                  <div className="space-y-4">
                    {matchResults.map((match, index) => (
                      <div key={index} className="bg-black/30 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{match.company} - {match.position}</h4>
                          <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                            match.score >= 80 ? 'bg-green-500/20 text-green-400' :
                            match.score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {match.score}分
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">{match.recommendation}</p>
                        {/* 维度评分 */}
                        <div className="grid grid-cols-5 gap-2 mt-3">
                          {Object.entries(match.dimensions || {}).map(([key, value]) => (
                            <div key={key} className="text-center">
                              <div className="text-xs text-gray-500">{
                                { skills: '技能', education: '学历', experience: '经验', location: '地点', salary: '薪资' }[key] || key
                              }</div>
                              <div className="text-sm font-medium">{value as number}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="glass rounded-2xl p-12 text-center">
              <div className="text-6xl mb-4">🤖</div>
              <p className="text-gray-400">上传或粘贴简历后</p>
              <p className="text-gray-400">AI 将自动解析并推荐匹配岗位</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-medium">{value || '-'}</p>
    </div>
  );
}
