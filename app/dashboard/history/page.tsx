"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { History as HistoryIcon } from "lucide-react"

interface MatchRecord {
  id: string
  resumeName: string
  jobTitle: string
  company: string
  matchScore: number
  date: string
}

export default function HistoryPage() {
  // 模拟数据
  const records: MatchRecord[] = [
    {
      id: "1",
      resumeName: "张三_简历.pdf",
      jobTitle: "高级前端工程师",
      company: "科技公司A",
      matchScore: 95,
      date: "2024-01-15 10:30",
    },
    {
      id: "2",
      resumeName: "李四_简历.docx",
      jobTitle: "全栈开发工程师",
      company: "科技公司B",
      matchScore: 88,
      date: "2024-01-14 15:20",
    },
    {
      id: "3",
      resumeName: "王五_简历.pdf",
      jobTitle: "前端技术专家",
      company: "科技公司C",
      matchScore: 82,
      date: "2024-01-13 09:15",
    },
  ]

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-black mb-2">
          匹配记录
        </h1>
        <p className="text-muted-foreground">
          查看历史匹配记录和结果
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>匹配历史</CardTitle>
          <CardDescription>
            共 {records.length} 条匹配记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>简历名称</TableHead>
                <TableHead>匹配岗位</TableHead>
                <TableHead>公司</TableHead>
                <TableHead>匹配度</TableHead>
                <TableHead>匹配时间</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.length > 0 ? (
                records.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell className="font-medium">{record.resumeName}</TableCell>
                    <TableCell>{record.jobTitle}</TableCell>
                    <TableCell>{record.company}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold">{record.matchScore}</span>
                        <span className="text-xs text-muted-foreground">分</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{record.date}</TableCell>
                    <TableCell className="text-right">
                      <button className="text-sm text-foreground hover:underline">
                        查看详情
                      </button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12">
                    <HistoryIcon className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      暂无匹配记录
                    </p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
