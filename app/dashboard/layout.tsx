"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { 
  FileText, 
  Briefcase, 
  History,
  Menu,
  X
} from "lucide-react"
import { cn } from "@/lib/utils"
import { JobsProvider } from "@/contexts/jobs-context"

const navigation = [
  {
    name: "学员简历分析",
    href: "/dashboard/coach",
    icon: FileText,
  },
  {
    name: "岗位库管理",
    href: "/dashboard/bd",
    icon: Briefcase,
  },
  {
    name: "匹配记录",
    href: "/dashboard/history",
    icon: History,
  },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white">
      {/* Mobile sidebar toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-md hover:bg-gray-100 transition-colors"
        >
          {sidebarOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-40 h-screen w-64 bg-white border-r border-border transition-transform duration-300 ease-in-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-border">
            <Image
              src="/assets/highmark-logo.png"
              alt="海马职加 High Mark Career"
              width={160}
              height={50}
              className="h-auto w-auto max-w-[160px]"
              priority
            />
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-black text-white"
                      : "text-foreground hover:bg-gray-100"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="lg:pl-64 min-h-screen">
        <JobsProvider>
          <div className="p-8">
            {children}
          </div>
        </JobsProvider>
      </main>
    </div>
  )
}
