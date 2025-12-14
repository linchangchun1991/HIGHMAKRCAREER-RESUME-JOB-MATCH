"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { User, GraduationCap, Briefcase, Target, Code } from "lucide-react"

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

interface ResumeProfileCardProps {
  resume: ParsedResume
}

export function ResumeProfileCard({ resume }: ResumeProfileCardProps) {
  return (
    <Card className="animate-slide-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          学员画像
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 基本信息 */}
        {resume.name && (
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">基本信息</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground w-20">姓名：</span>
                <span className="font-medium">{resume.name}</span>
              </div>
              {resume.email && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-muted-foreground w-20">邮箱：</span>
                  <span>{resume.email}</span>
                </div>
              )}
              {resume.phone && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-muted-foreground w-20">电话：</span>
                  <span>{resume.phone}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 教育背景 */}
        {resume.education && (
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <GraduationCap className="h-4 w-4" />
              教育背景
            </h3>
            <p className="text-sm text-muted-foreground">{resume.education}</p>
          </div>
        )}

        {/* 技能 */}
        {resume.skills && (
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <Code className="h-4 w-4" />
              核心技能
            </h3>
            {resume.skills.hard && resume.skills.hard.length > 0 && (
              <div className="mb-3">
                <p className="text-xs text-muted-foreground mb-2">硬技能</p>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.hard.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 text-xs font-medium bg-black text-white rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {resume.skills.soft && resume.skills.soft.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">软技能</p>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.soft.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 项目经验 */}
        {resume.experience && resume.experience.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              项目经验
            </h3>
            <ul className="space-y-2">
              {resume.experience.map((exp, idx) => (
                <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-black mt-1">•</span>
                  <span>{exp}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 求职意向 */}
        {resume.intention && (
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
              <Target className="h-4 w-4" />
              求职意向
            </h3>
            <p className="text-sm text-muted-foreground">{resume.intention}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
