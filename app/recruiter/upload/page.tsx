'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export default function UploadJobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    company: '',
    position: '',
    city: '',
    salaryRange: '',
    education: '',
    experience: '',
    skills: '',
    description: '',
    requirements: '',
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/jobs/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.success) {
        setJobs(data.jobs || []);
        alert(`成功导入 ${data.count} 个岗位！`);
      } else {
        alert('上传失败：' + (data.error || '未知错误'));
      }
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
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean)
        }),
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setFormData({
            company: '', position: '', city: '', salaryRange: '',
            education: '', experience: '', skills: '', description: '', requirements: ''
          });
          alert('岗位添加成功！');
        }
      }
    } catch (error) {
      console.error('Submit error:', error);
      alert('添加失败，请重试');
    }
  };


  return (
    <div className="space-y-8 max-w-6xl">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">上传岗位</h1>
          <p className="text-gray-400 mt-2">批量导入或手动添加岗位信息</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:opacity-90 transition-opacity"
        >
          {showForm ? '返回批量上传' : '➕ 手动添加岗位'}
        </button>
      </div>

      {showForm ? (
        <form onSubmit={handleSubmit} className="glass rounded-2xl p-8">
          <h2 className="text-xl font-bold mb-6">添加新岗位</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <Input label="公司名称" value={formData.company} onChange={v => setFormData({...formData, company: v})} required />
            <Input label="岗位名称" value={formData.position} onChange={v => setFormData({...formData, position: v})} required />
            <Input label="工作城市" value={formData.city} onChange={v => setFormData({...formData, city: v})} required />
            <Input label="薪资范围" value={formData.salaryRange} onChange={v => setFormData({...formData, salaryRange: v})} placeholder="如：15-25K" />
            <Input label="学历要求" value={formData.education} onChange={v => setFormData({...formData, education: v})} placeholder="如：本科及以上" />
            <Input label="经验要求" value={formData.experience} onChange={v => setFormData({...formData, experience: v})} placeholder="如：1-3年" />
            <div className="md:col-span-2">
              <Input label="技能要求" value={formData.skills} onChange={v => setFormData({...formData, skills: v})} placeholder="用逗号分隔，如：Python, Java, SQL" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">岗位描述</label>
              <textarea
                value={formData.description}
                onChange={e => setFormData({...formData, description: e.target.value})}
                className="w-full h-32 bg-black/30 rounded-xl p-4 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none"
                placeholder="请输入岗位职责描述..."
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">任职要求</label>
              <textarea
                value={formData.requirements}
                onChange={e => setFormData({...formData, requirements: e.target.value})}
                className="w-full h-32 bg-black/30 rounded-xl p-4 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none"
                placeholder="请输入任职要求..."
              />
            </div>
          </div>
          <button type="submit" className="mt-6 w-full py-4 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:opacity-90 font-medium">
            保存岗位
          </button>
        </form>
      ) : (
        <>
          {/* Excel 上传区 */}
          <div
            {...getRootProps()}
            className={`glass rounded-2xl p-12 border-2 border-dashed text-center cursor-pointer transition-all ${
              isDragActive ? 'border-purple-500 bg-purple-500/10' : 'border-gray-600 hover:border-gray-500'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-6xl mb-4">📊</div>
            {isUploading ? (
              <p className="text-gray-400">正在解析...</p>
            ) : (
              <>
                <p className="text-gray-300 text-lg">拖拽 Excel 文件到这里，或点击选择</p>
                <p className="text-gray-500 text-sm mt-2">支持 .xlsx, .xls, .csv 格式</p>
              </>
            )}
          </div>

          {/* 模板下载 */}
          <div className="glass rounded-2xl p-6 flex items-center justify-between">
            <div>
              <h3 className="font-medium">下载导入模板</h3>
              <p className="text-gray-400 text-sm mt-1">按照模板格式填写岗位信息，确保导入成功</p>
            </div>
            <button className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors">
              📥 下载模板
            </button>
          </div>

          {/* 预览已导入的数据 */}
          {jobs.length > 0 && (
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>✅</span> 已成功导入 ({jobs.length} 条)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="py-3 px-4 text-left text-gray-400">公司</th>
                      <th className="py-3 px-4 text-left text-gray-400">岗位</th>
                      <th className="py-3 px-4 text-left text-gray-400">城市</th>
                      <th className="py-3 px-4 text-left text-gray-400">薪资</th>
                      <th className="py-3 px-4 text-left text-gray-400">学历</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.slice(0, 10).map((job, index) => (
                      <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4">{job.company}</td>
                        <td className="py-3 px-4">{job.position}</td>
                        <td className="py-3 px-4">{job.city}</td>
                        <td className="py-3 px-4">{job.salaryRange}</td>
                        <td className="py-3 px-4">{job.education}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {jobs.length > 10 && (
                <p className="mt-4 text-sm text-gray-400 text-center">
                  显示前 10 条，共 {jobs.length} 条已导入
                </p>
              )}
              <button 
                onClick={() => setJobs([])}
                className="mt-6 w-full py-4 rounded-xl bg-white/10 hover:bg-white/20 transition-colors font-medium"
              >
                清空列表
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Input({ label, value, onChange, placeholder, required }: any) {
  return (
    <div>
      <label className="block text-sm font-medium mb-2">{label}</label>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full bg-black/30 rounded-xl px-4 py-3 text-gray-300 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
      />
    </div>
  );
}
