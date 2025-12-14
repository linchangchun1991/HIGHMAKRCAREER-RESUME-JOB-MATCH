"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const router = useRouter()

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    // 临时跳转到仪表盘，后续可以添加实际的登录逻辑
    router.push("/dashboard")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4 animate-fade-in">
      <div className="w-full max-w-md space-y-12">
        {/* Logo */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Image
              src="/assets/highmark-logo.png"
              alt="海马职加 High Mark Career"
              width={240}
              height={80}
              className="h-auto w-auto max-w-[240px]"
              priority
            />
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            人岗匹配系统
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-4">
            <div>
              <Input
                type="email"
                placeholder="邮箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-12 border-black/20 focus:border-black transition-all duration-200"
                required
              />
            </div>
            <div>
              <Input
                type="password"
                placeholder="密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-12 border-black/20 focus:border-black transition-all duration-200"
                required
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full h-12 bg-black text-white hover:opacity-90 transition-all duration-200"
          >
            登录
          </Button>
        </form>
      </div>
    </div>
  )
}
