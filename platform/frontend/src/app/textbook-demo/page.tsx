'use client'

/**
 * 交互式教材演示页面
 *
 * 演示新的左文右码布局功能
 * URL: /textbook-demo
 *
 * 注意：QueryClientProvider已在layout.tsx中配置，这里无需重复包装
 */

import React from 'react'
import InteractiveTextbook from '@/components/InteractiveTextbook/InteractiveTextbook'

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
    <div style={{ width: '100vw', height: '100vh' }}>
      <InteractiveTextbook
        bookSlug="water-system-intro"
        chapterSlug="chapter-01"
        caseSlug="case-water-tank"
        onCodeExecute={handleCodeExecute}
      />
    </div>
  )
}
