'use client'

/**
 * 交互式教材演示页面
 *
 * 演示新的左文右码布局功能
 * URL: /textbook-demo
 */

import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import InteractiveTextbook from '@/components/InteractiveTextbook/InteractiveTextbook'

// 创建 React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export default function TextbookDemoPage() {
  const handleCodeExecute = async (code: string) => {
    console.log('执行代码:', code)

    // TODO: 集成实际的代码执行API
    // const response = await fetch('/api/v1/execution/run', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ code, language: 'python' })
    // })

    alert('代码执行功能待集成\n\n将会调用: POST /api/v1/execution/run')
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div style={{ width: '100vw', height: '100vh' }}>
        <InteractiveTextbook
          bookSlug="water-system-intro"
          chapterSlug="chapter-01"
          caseSlug="case-water-tank"
          onCodeExecute={handleCodeExecute}
        />
      </div>
    </QueryClientProvider>
  )
}
