import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 简历匹配助手",
  description: "智能分析你的简历，为你推荐最匹配的岗位",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
