"use client"

import { Card } from "@/components/ui/card"
import { CircularProgress } from "@/components/ui/circular-progress"
import { Button } from "@/components/ui/button"
import { MapPin, DollarSign, Sparkles } from "lucide-react"

interface MatchedJob {
  id: string
  title: string
  company: string
  location?: string
  salary?: string
  matchScore: number
  recommendation?: string
  gapAnalysis?: string
}

interface JobMatchCardProps {
  job: MatchedJob
  index: number
}

export function JobMatchCard({ job, index }: JobMatchCardProps) {
  return (
    <Card
      className="p-6 hover:shadow-lg transition-all duration-300 animate-slide-in"
      style={{
        animationDelay: `${index * 100}ms`,
      }}
    >
      <div className="flex items-start gap-4">
        {/* 左侧：匹配度环形进度条 */}
        <div className="flex-shrink-0">
          <CircularProgress value={job.matchScore} size={72} strokeWidth={6} />
        </div>

        {/* 中间：岗位信息 */}
        <div className="flex-1 space-y-3">
          <div>
            <h3 className="text-lg font-semibold text-foreground mb-1">
              {job.title}
            </h3>
            <p className="text-sm text-muted-foreground">{job.company}</p>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            {job.location && (
              <div className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                <span>{job.location}</span>
              </div>
            )}
            {job.salary && (
              <div className="flex items-center gap-1">
                <DollarSign className="h-3.5 w-3.5" />
                <span>{job.salary}</span>
              </div>
            )}
          </div>

          {/* AI 推荐理由 */}
          {job.recommendation && (
            <div className="pt-2 border-t border-border">
              <div className="flex items-start gap-2">
                <Sparkles className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-medium text-foreground mb-1">推荐理由</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {job.recommendation}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <Button variant="outline" className="w-full" size="sm">
          查看详情
        </Button>
      </div>
    </Card>
  )
}
