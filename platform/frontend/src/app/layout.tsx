import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AntdRegistry } from '@ant-design/nextjs-registry'
import { QueryProvider } from '@/providers/QueryProvider'
import { AuthProvider } from '@/contexts/AuthContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Engineering Learning Platform - 智能工程教学平台',
  description: '教材 + 工具 + AI助手三位一体的专业学习平台',
  keywords: ['工程教育', '水力学', '控制理论', '在线学习', 'AI助手'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <QueryProvider>
          <AntdRegistry>
            <AuthProvider>
              {children}
            </AuthProvider>
          </AntdRegistry>
        </QueryProvider>
      </body>
    </html>
  )
}
