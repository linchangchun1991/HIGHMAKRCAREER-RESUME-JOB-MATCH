"use client"

import { useState, useCallback, useEffect } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X, Loader2, CheckCircle2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { ResumeProfileCard } from "@/components/coach/resume-profile-card"
import { JobMatchCard } from "@/components/coach/job-match-card"
import { useJobs } from "@/contexts/jobs-context"

interface ParsedResume {
  name?: string
  email?: string
  phone?: string
  education?: string
  skills?: {
    hard?: string[]
    soft?: string[]
  }
  experience?: string[]
  intention?: string
  [key: string]: any
}

interface MatchedJob {
  id: string
  title: string
  company: string
  location?: string
  salary?: string
  matchScore: number
  description?: string
  recommendation?: string
  gapAnalysis?: string
}

export default function CoachPage() {
  const { jobs } = useJobs()
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null)
  const [matchedJobs, setMatchedJobs] = useState<MatchedJob[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isMatching, setIsMatching] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const { toast } = useToast()

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    const file = files[0]

    if (file && (file.type === "application/pdf" || file.type.includes("word"))) {
      handleFileUpload(file)
    } else {
      toast({
        title: "文件格式不支持",
        description: "请上传 PDF 或 Word 文档",
        variant: "destructive",
      })
    }
  }, [toast])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file)
    setIsAnalyzing(true)
    setParsedResume(null)
    setMatchedJobs([])
    setUploadProgress(0)

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      // 1. 上传文件并解析简历
      const formData = new FormData()
      formData.append("file", file)

      const analyzeResponse = await fetch("/api/analyze-resume", {
        method: "POST",
        body: formData,
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json()
        throw new Error(errorData.error || "简历解析失败")
      }

      const analyzeResult = await analyzeResponse.json()
      
      if (!analyzeResult.success) {
        throw new Error(analyzeResult.error || "简历解析失败")
      }

      setParsedResume(analyzeResult.data)
      setIsAnalyzing(false)
      setIsMatching(true)

      toast({
        title: "解析成功",
        description: "简历已成功解析，正在匹配岗位...",
      })

      // 2. 获取岗位列表并匹配（使用 Context 中的岗位数据）
      const activeJobs = jobs.filter((job) => job.status === "active")

      if (activeJobs.length === 0) {
        toast({
          title: "暂无岗位",
          description: "请先在岗位库中添加岗位",
          variant: "destructive",
        })
        setIsMatching(false)
        return
      }

      const matchResponse = await fetch("/api/match-jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resumeAnalysis: analyzeResult.data,
          jobs: activeJobs,
        }),
      })

      if (!matchResponse.ok) {
        const errorData = await matchResponse.json()
        throw new Error(errorData.error || "岗位匹配失败")
      }

      const matchResult = await matchResponse.json()

      if (!matchResult.success) {
        throw new Error(matchResult.error || "岗位匹配失败")
      }

      // 流式渲染：逐个添加岗位
      const jobsToAdd = matchResult.data || []
      setMatchedJobs([]) // 清空现有列表

      // 逐个添加岗位，实现流式渲染效果
      for (let i = 0; i < jobsToAdd.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 400)) // 延迟400ms，更流畅
        setMatchedJobs((prev) => [...prev, jobsToAdd[i]])
      }

      setIsMatching(false)

      toast({
        title: "匹配完成",
        description: `已找到 ${jobsToAdd.length} 个匹配岗位`,
      })
    } catch (error) {
      setIsAnalyzing(false)
      setIsMatching(false)
      setUploadProgress(0)
      console.error("处理失败:", error)
      toast({
        title: "处理失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      })
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    setParsedResume(null)
    setMatchedJobs([])
    setUploadProgress(0)
  }

  return (
    <div className="min-h-screen bg-white">
      {/* 海马职加 Logo */}
      <div className="absolute top-4 left-4 lg:top-8 lg:left-8 z-10">
        <Image
          src="/assets/highmark-logo.png"
          alt="海马职加 High Mark Career"
          width={180}
          height={60}
          className="h-auto w-auto max-w-[180px] lg:max-w-[220px]"
          priority
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 p-4 lg:p-8 pt-20">
        {/* 左侧：上传区域 */}
        <div className="col-span-1 lg:col-span-4">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
              className={`
              relative h-[500px] lg:h-[600px] border-2 border-dashed rounded-2xl
              flex flex-col items-center justify-center
              transition-all duration-300 ease-out
              ${
                isDragging
                  ? "border-black bg-black/5 scale-[1.02]"
                  : uploadedFile
                  ? "border-gray-200 bg-gray-50"
                  : "border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50"
              }
            `}
          >
            {!uploadedFile ? (
              <>
                <div className="text-center space-y-6 px-8">
                  <div
                    className={`
                      mx-auto w-24 h-24 rounded-full
                      flex items-center justify-center
                      transition-all duration-300
                      ${
                        isDragging
                          ? "bg-black text-white scale-110"
                          : "bg-gray-100 text-gray-400"
                      }
                    `}
                  >
                    <Upload className="h-12 w-12" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-foreground">
                      {isDragging ? "松开以上传文件" : "拖拽文件到此处"}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      或点击下方按钮选择文件
                    </p>
                    <p className="text-xs text-muted-foreground">
                      支持 PDF、Word 格式
                    </p>
                  </div>
                  <label>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="hidden"
                      disabled={isAnalyzing || isMatching}
                    />
                    <Button
                      asChild
                      className="gap-2"
                      disabled={isAnalyzing || isMatching}
                    >
                      <span>选择文件</span>
                    </Button>
                  </label>
                </div>
              </>
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center p-8 space-y-6">
                {/* 上传进度 */}
                {isAnalyzing && (
                  <div className="w-full space-y-4">
                    <div className="flex items-center justify-center gap-2">
                      <Loader2 className="h-6 w-6 animate-spin text-black" />
                      <span className="text-sm font-medium">正在解析简历...</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-black h-full transition-all duration-300 ease-out"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* 文件信息 */}
                {!isAnalyzing && (
                  <>
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                        <CheckCircle2 className="h-8 w-8 text-green-600" />
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-medium text-foreground">
                          {uploadedFile.name}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {(uploadedFile.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>

                    {isMatching && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>正在匹配岗位...</span>
                      </div>
                    )}

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={removeFile}
                      disabled={isAnalyzing || isMatching}
                      className="gap-2"
                    >
                      <X className="h-4 w-4" />
                      重新上传
                    </Button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 中间：学员画像卡片 */}
        <div className="col-span-1 lg:col-span-4">
          {parsedResume ? (
            <ResumeProfileCard resume={parsedResume} />
          ) : (
            <div className="h-[500px] lg:h-[600px] flex items-center justify-center border-2 border-dashed border-gray-200 rounded-2xl">
              <div className="text-center space-y-2">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  上传简历后将显示学员画像
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 右侧：推荐岗位列表 */}
        <div className="col-span-1 lg:col-span-4">
          <div className="space-y-4">
            {matchedJobs.length > 0 ? (
              <>
                <div className="mb-4">
                  <h2 className="text-xl font-semibold text-foreground mb-1">
                    推荐岗位
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    找到 {matchedJobs.length} 个匹配岗位
                  </p>
                </div>
                {matchedJobs.map((job, index) => (
                  <JobMatchCard key={job.id} job={job} index={index} />
                ))}
                {isMatching && (
                  <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>正在匹配更多岗位...</span>
                  </div>
                )}
              </>
            ) : (
              <div className="min-h-[500px] lg:min-h-[600px] flex items-center justify-center border-2 border-dashed border-gray-200 rounded-2xl">
                <div className="text-center space-y-2">
                  <FileText className="h-12 w-12 mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    {parsedResume
                      ? "正在匹配岗位..."
                      : "上传简历后将显示推荐岗位"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
