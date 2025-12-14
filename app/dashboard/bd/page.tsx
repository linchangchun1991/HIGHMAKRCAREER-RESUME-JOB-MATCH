"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"
import { Upload, Plus, Sparkles, Loader2, MapPin, DollarSign, GraduationCap, Briefcase, X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useJobs, type Job } from "@/contexts/jobs-context"

export default function BDPage() {
  const { jobs, addJob } = useJobs()
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [isParsing, setIsParsing] = useState(false)
  const [jdText, setJdText] = useState("")
  const [formData, setFormData] = useState({
    title: "",
    company: "",
    location: "",
    salary: "",
    description: "",
    education: "",
    requirements: [] as string[],
  })
  const { toast } = useToast()

  const handleAIParse = async () => {
    if (!jdText.trim()) {
      toast({
        title: "请输入 JD 文本",
        description: "请先输入招聘文本内容",
        variant: "destructive",
      })
      return
    }

    setIsParsing(true)
    try {
      const response = await fetch("/api/parse-jd", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ jdText }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "解析失败")
      }

      const result = await response.json()
      if (!result.success) {
        throw new Error(result.error || "解析失败")
      }

      const parsed = result.data
      setFormData({
        title: parsed.title || "",
        company: formData.company, // 保留公司名称
        location: formData.location, // 保留地点
        salary: parsed.salary || "",
        description: parsed.description || "",
        education: parsed.education || "",
        requirements: parsed.requirements || [],
      })

      toast({
        title: "解析成功",
        description: "AI 已成功解析岗位信息",
      })
    } catch (error) {
      console.error("解析失败:", error)
      toast({
        title: "解析失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      })
    } finally {
      setIsParsing(false)
    }
  }

  const handleAddJob = () => {
    if (!formData.title || !formData.company) {
      toast({
        title: "请填写必填字段",
        description: "岗位名称和公司名称是必填项",
        variant: "destructive",
      })
      return
    }

    addJob({
      title: formData.title,
      company: formData.company,
      location: formData.location,
      salary: formData.salary,
      description: formData.description,
      education: formData.education,
      requirements: formData.requirements,
      status: "active",
    })

    // 重置表单
    setFormData({
      title: "",
      company: "",
      location: "",
      salary: "",
      description: "",
      education: "",
      requirements: [],
    })
    setJdText("")
    setIsDrawerOpen(false)

    toast({
      title: "添加成功",
      description: "岗位已添加到岗位库",
    })
  }

  const handleRemoveRequirement = (index: number) => {
    setFormData({
      ...formData,
      requirements: formData.requirements.filter((_, i) => i !== index),
    })
  }

  const handleAddRequirement = () => {
    const requirement = prompt("请输入要求：")
    if (requirement && requirement.trim()) {
      setFormData({
        ...formData,
        requirements: [...formData.requirements, requirement.trim()],
      })
    }
  }

  const activeJobs = jobs.filter((job) => job.status === "active")

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-black mb-1">
            岗位库管理
          </h1>
          <p className="text-sm text-muted-foreground">
            共 {activeJobs.length} 个活跃岗位
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => {
              toast({
                title: "批量导入",
                description: "批量导入功能开发中",
              })
            }}
            className="gap-2"
          >
            <Upload className="h-4 w-4" />
            批量导入
          </Button>
          <Drawer open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
            <DrawerTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                新增岗位
              </Button>
            </DrawerTrigger>
            <DrawerContent side="right" className="h-full max-w-2xl">
              <DrawerHeader className="border-b">
                <DrawerTitle>新增岗位</DrawerTitle>
                <DrawerDescription>
                  填写岗位信息，或使用 AI 智能解析 JD
                </DrawerDescription>
              </DrawerHeader>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* AI 解析区域 */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">AI 智能解析 JD</label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleAIParse}
                      disabled={isParsing}
                      className="gap-2"
                    >
                      {isParsing ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          解析中...
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4" />
                          AI 识别
                        </>
                      )}
                    </Button>
                  </div>
                  <textarea
                    className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                    placeholder="粘贴招聘文本，点击"AI 识别"自动填充岗位信息..."
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    disabled={isParsing}
                  />
                </div>

                {/* 基本信息 */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-foreground">基本信息</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">岗位名称 *</label>
                      <Input
                        placeholder="例如：高级前端工程师"
                        value={formData.title}
                        onChange={(e) =>
                          setFormData({ ...formData, title: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">公司名称 *</label>
                      <Input
                        placeholder="例如：科技公司"
                        value={formData.company}
                        onChange={(e) =>
                          setFormData({ ...formData, company: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">工作地点</label>
                      <Input
                        placeholder="例如：北京"
                        value={formData.location}
                        onChange={(e) =>
                          setFormData({ ...formData, location: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">薪资范围</label>
                      <Input
                        placeholder="例如：25K-40K"
                        value={formData.salary}
                        onChange={(e) =>
                          setFormData({ ...formData, salary: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">最低学历</label>
                      <Input
                        placeholder="例如：本科"
                        value={formData.education}
                        onChange={(e) =>
                          setFormData({ ...formData, education: e.target.value })
                        }
                      />
                    </div>
                  </div>
                </div>

                {/* 岗位描述 */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">岗位描述</label>
                  <textarea
                    className="flex min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                    placeholder="输入岗位描述..."
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                  />
                </div>

                {/* 岗位要求 */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">岗位要求</label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleAddRequirement}
                      className="h-7 text-xs"
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      添加
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {formData.requirements.length > 0 ? (
                      formData.requirements.map((req, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 p-2 bg-gray-50 rounded-md"
                        >
                          <span className="flex-1 text-sm">{req}</span>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => handleRemoveRequirement(index)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground py-2">
                        暂无要求，点击"添加"按钮添加
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <DrawerFooter className="border-t">
                <div className="flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setIsDrawerOpen(false)}
                  >
                    取消
                  </Button>
                  <Button onClick={handleAddJob}>添加岗位</Button>
                </div>
              </DrawerFooter>
            </DrawerContent>
          </Drawer>
        </div>
      </div>

      {/* 岗位列表 */}
      {activeJobs.length > 0 ? (
        <div className="grid gap-4">
          {activeJobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <Briefcase className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">暂无岗位</h3>
          <p className="text-sm text-muted-foreground mb-6">
            点击"新增岗位"按钮开始添加岗位
          </p>
          <Button onClick={() => setIsDrawerOpen(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            新增岗位
          </Button>
        </div>
      )}
    </div>
  )
}

function JobCard({ job }: { job: Job }) {
  return (
    <div className="group relative p-6 bg-white border border-border rounded-lg hover:shadow-md transition-all duration-200 animate-slide-in">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <div>
            <h3 className="text-lg font-semibold text-foreground mb-1">
              {job.title}
            </h3>
            <p className="text-sm text-muted-foreground">{job.company}</p>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            {job.location && (
              <div className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                <span>{job.location}</span>
              </div>
            )}
            {job.salary && (
              <div className="flex items-center gap-1.5">
                <DollarSign className="h-4 w-4" />
                <span>{job.salary}</span>
              </div>
            )}
            {job.education && (
              <div className="flex items-center gap-1.5">
                <GraduationCap className="h-4 w-4" />
                <span>{job.education}</span>
              </div>
            )}
          </div>

          {job.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {job.description}
            </p>
          )}

          {job.requirements && job.requirements.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {job.requirements.slice(0, 5).map((req, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md"
                >
                  {req}
                </span>
              ))}
              {job.requirements.length > 5 && (
                <span className="px-2 py-1 text-xs text-muted-foreground">
                  +{job.requirements.length - 5} 更多
                </span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
            编辑
          </Button>
        </div>
      </div>
    </div>
  )
}
