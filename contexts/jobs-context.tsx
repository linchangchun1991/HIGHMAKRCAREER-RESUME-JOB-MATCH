"use client"

import { createContext, useContext, useState, ReactNode } from "react"

export interface Job {
  id: string
  title: string
  company: string
  location: string
  salary: string
  description: string
  requirements?: string[]
  education?: string
  status: "active" | "draft"
  createdAt: string
  updatedAt: string
}

interface JobsContextType {
  jobs: Job[]
  addJob: (job: Omit<Job, "id" | "createdAt" | "updatedAt">) => void
  updateJob: (id: string, job: Partial<Job>) => void
  deleteJob: (id: string) => void
  getJob: (id: string) => Job | undefined
}

const JobsContext = createContext<JobsContextType | undefined>(undefined)

// 初始模拟数据
const initialJobs: Job[] = [
  {
    id: "1",
    title: "高级前端工程师",
    company: "科技公司A",
    location: "北京",
    salary: "25K-40K",
    description: "负责前端架构设计和开发，需要5年以上React开发经验，熟悉TypeScript、Next.js等现代前端技术栈。",
    requirements: ["React", "TypeScript", "Next.js", "5年经验"],
    education: "本科",
    status: "active",
    createdAt: "2024-01-15T10:00:00Z",
    updatedAt: "2024-01-15T10:00:00Z",
  },
  {
    id: "2",
    title: "全栈开发工程师",
    company: "科技公司B",
    location: "上海",
    salary: "30K-50K",
    description: "负责全栈应用开发，需要熟悉React、Node.js、数据库设计，有大型项目经验。",
    requirements: ["React", "Node.js", "全栈开发", "项目经验"],
    education: "本科",
    status: "active",
    createdAt: "2024-01-14T15:00:00Z",
    updatedAt: "2024-01-14T15:00:00Z",
  },
  {
    id: "3",
    title: "前端技术专家",
    company: "科技公司C",
    location: "深圳",
    salary: "35K-60K",
    description: "负责前端技术团队管理和技术方案设计，需要丰富的项目管理和团队协作经验。",
    requirements: ["前端架构", "团队管理", "项目管理"],
    education: "硕士",
    status: "active",
    createdAt: "2024-01-13T09:00:00Z",
    updatedAt: "2024-01-13T09:00:00Z",
  },
]

export function JobsProvider({ children }: { children: ReactNode }) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs)

  const addJob = (jobData: Omit<Job, "id" | "createdAt" | "updatedAt">) => {
    const now = new Date().toISOString()
    const newJob: Job = {
      ...jobData,
      id: Date.now().toString(),
      createdAt: now,
      updatedAt: now,
    }
    setJobs((prev) => [newJob, ...prev])
  }

  const updateJob = (id: string, jobData: Partial<Job>) => {
    setJobs((prev) =>
      prev.map((job) =>
        job.id === id
          ? { ...job, ...jobData, updatedAt: new Date().toISOString() }
          : job
      )
    )
  }

  const deleteJob = (id: string) => {
    setJobs((prev) => prev.filter((job) => job.id !== id))
  }

  const getJob = (id: string) => {
    return jobs.find((job) => job.id === id)
  }

  return (
    <JobsContext.Provider value={{ jobs, addJob, updateJob, deleteJob, getJob }}>
      {children}
    </JobsContext.Provider>
  )
}

export function useJobs() {
  const context = useContext(JobsContext)
  if (context === undefined) {
    throw new Error("useJobs must be used within a JobsProvider")
  }
  return context
}
