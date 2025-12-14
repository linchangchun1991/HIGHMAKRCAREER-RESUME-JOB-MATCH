"use client"

import { cn } from "@/lib/utils"

interface CircularProgressProps {
  value: number // 0-100
  size?: number
  strokeWidth?: number
  className?: string
  showLabel?: boolean
}

export function CircularProgress({
  value,
  size = 80,
  strokeWidth = 8,
  className,
  showLabel = true,
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  // 根据分数确定颜色
  const getColor = () => {
    if (value >= 80) return "text-green-600"
    if (value >= 60) return "text-blue-600"
    if (value >= 40) return "text-yellow-600"
    return "text-red-600"
  }

  const getStrokeColor = () => {
    if (value >= 80) return "stroke-green-600"
    if (value >= 60) return "stroke-blue-600"
    if (value >= 40) return "stroke-yellow-600"
    return "stroke-red-600"
  }

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* 背景圆 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-gray-200"
        />
        {/* 进度圆 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={cn("transition-all duration-500 ease-out", getStrokeColor())}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("text-lg font-bold", getColor())}>
            {Math.round(value)}
          </span>
        </div>
      )}
    </div>
  )
}
