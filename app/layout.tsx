import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'HIGHMARK 海马职加 - 智能选岗系统',
  description: '基于AI的智能人岗匹配平台',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body className={`${inter.className} text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
