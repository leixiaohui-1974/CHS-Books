/**
 * 交互式教材组件（左文右码布局）
 *
 * 这是 Sprint 1 的核心组件，实现了：
 * 1. 左右分栏布局（教材 + 代码编辑器）
 * 2. 滚动同步（教材滚动 → 代码定位）
 * 3. 代码高亮引用
 * 4. Inline 代码运行
 *
 * @module components/InteractiveTextbook
 */

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import MonacoEditor from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import 'katex/dist/katex.min.css'
import './InteractiveTextbook.css'

// ==================== 类型定义 ====================

interface InteractiveTextbookProps {
  bookSlug: string
  chapterSlug: string
  caseSlug: string
  onCodeExecute?: (code: string) => void
}

// Backend API response types (snake_case from Python)
interface CodeLineMapping {
  start: number
  end: number
}

interface TextbookSection {
  id: string
  title: string
  content: string
  code_lines: CodeLineMapping | null
  order: number
}

interface TextbookAPIResponse {
  book_slug: string
  chapter_slug: string
  case_slug: string
  title: string
  description: string | null
  sections: TextbookSection[]
  starter_code: string
  solution_code: string | null
  difficulty: string
  estimated_minutes: number
  tags: string[]
}

// ==================== 主组件 ====================

export const InteractiveTextbook: React.FC<InteractiveTextbookProps> = ({
  bookSlug,
  chapterSlug,
  caseSlug,
  onCodeExecute
}) => {
  // ==================== State ====================

  const [code, setCode] = useState<string>('')
  const [currentSection, setCurrentSection] = useState<string>('')
  const [splitPosition, setSplitPosition] = useState<number>(50) // 分隔符位置（百分比）
  const [isDragging, setIsDragging] = useState(false)

  // ==================== Refs ====================

  const textbookRef = useRef<HTMLDivElement>(null)
  const editorRef = useRef<any>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // ==================== 数据获取 ====================

  const { data: textbook, isLoading, error } = useQuery<TextbookAPIResponse>(
    ['textbook', bookSlug, chapterSlug, caseSlug],
    async () => {
      const response = await fetch(
        `/api/v1/textbooks/${bookSlug}/${chapterSlug}/${caseSlug}`
      )
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to fetch textbook')
      }
      return response.json()
    }
  )

  // ==================== 初始化代码 ====================

  useEffect(() => {
    if (textbook?.starter_code) {
      setCode(textbook.starter_code)
    }
  }, [textbook])

  // ==================== 滚动同步：教材 → 代码 ====================

  const handleTextbookScroll = useCallback(() => {
    if (!textbookRef.current || !textbook) return

    const sections = textbookRef.current.querySelectorAll('[data-section-id]')
    const scrollTop = textbookRef.current.scrollTop
    const containerHeight = textbookRef.current.clientHeight

    // 找到当前可见的 section
    let visibleSection = ''
    sections.forEach((section) => {
      const rect = section.getBoundingClientRect()
      const sectionTop = rect.top - textbookRef.current!.getBoundingClientRect().top + scrollTop

      if (sectionTop <= scrollTop + containerHeight / 3) {
        visibleSection = section.getAttribute('data-section-id') || ''
      }
    })

    if (visibleSection && visibleSection !== currentSection) {
      setCurrentSection(visibleSection)
      syncCodeEditor(visibleSection)
    }
  }, [textbook, currentSection])

  // 同步代码编辑器到指定 section
  const syncCodeEditor = useCallback((sectionId: string) => {
    if (!editorRef.current || !textbook) return

    const section = textbook.sections.find(s => s.id === sectionId)
    if (section?.code_lines) {
      // 滚动到对应代码行
      editorRef.current.revealLineInCenter(section.code_lines.start)

      // 高亮代码行
      highlightCodeLines(section.code_lines.start, section.code_lines.end)
    }
  }, [textbook])

  // 高亮代码行
  const highlightCodeLines = useCallback((start: number, end: number) => {
    if (!editorRef.current) return

    const monaco = editorRef.current

    // 设置选中区域
    monaco.setSelection({
      startLineNumber: start,
      startColumn: 1,
      endLineNumber: end,
      endColumn: 999
    })

    // 添加装饰（背景色高亮）
    const decorations = monaco.deltaDecorations(
      [],
      [
        {
          range: {
            startLineNumber: start,
            startColumn: 1,
            endLineNumber: end,
            endColumn: 999
          },
          options: {
            isWholeLine: true,
            className: 'highlighted-code-line',
            inlineClassName: 'highlighted-code-line-inline'
          }
        }
      ]
    )

    // 2秒后移除高亮
    setTimeout(() => {
      monaco.deltaDecorations(decorations, [])
    }, 2000)
  }, [])

  // ==================== 滚动同步：代码 → 教材 ====================

  // 根据代码行号找到对应的section
  const findSectionByCodeLine = useCallback((lineNumber: number): string | null => {
    if (!textbook) return null

    // 遍历所有sections，找到包含此行号的section
    for (const section of textbook.sections) {
      if (section.code_lines) {
        const { start, end } = section.code_lines
        if (lineNumber >= start && lineNumber <= end) {
          return section.id
        }
      }
    }

    return null
  }, [textbook])

  // 滚动教材到指定section
  const scrollToTextbookSection = useCallback((sectionId: string) => {
    if (!textbookRef.current) return

    const sectionElement = textbookRef.current.querySelector(
      `[data-section-id="${sectionId}"]`
    ) as HTMLElement

    if (sectionElement) {
      // 平滑滚动到section
      sectionElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })

      // 添加临时高亮效果
      sectionElement.classList.add('highlighted-section')
      setTimeout(() => {
        sectionElement.classList.remove('highlighted-section')
      }, 2000)
    }
  }, [])

  // 监听代码编辑器滚动
  const handleCodeScroll = useCallback(() => {
    if (!editorRef.current || !textbook) return

    const monaco = editorRef.current

    // 获取当前可见区域的第一行
    const visibleRanges = monaco.getVisibleRanges()
    if (visibleRanges.length === 0) return

    const firstVisibleLine = visibleRanges[0].startLineNumber

    // 找到对应的section
    const sectionId = findSectionByCodeLine(firstVisibleLine)

    if (sectionId && sectionId !== currentSection) {
      setCurrentSection(sectionId)
      scrollToTextbookSection(sectionId)
    }
  }, [textbook, currentSection, findSectionByCodeLine, scrollToTextbookSection])

  // 添加滚动监听
  useEffect(() => {
    const textbookEl = textbookRef.current
    if (!textbookEl) return

    // 使用节流
    let timeoutId: NodeJS.Timeout
    const throttledScroll = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(handleTextbookScroll, 100)
    }

    textbookEl.addEventListener('scroll', throttledScroll)
    return () => {
      textbookEl.removeEventListener('scroll', throttledScroll)
      clearTimeout(timeoutId)
    }
  }, [handleTextbookScroll])

  // ==================== 代码引用点击处理 ====================

  const handleCodeReference = useCallback((lineNumber: number) => {
    if (!editorRef.current) return

    // 跳转到代码行
    editorRef.current.revealLineInCenter(lineNumber)

    // 高亮该行
    highlightCodeLines(lineNumber, lineNumber)
  }, [highlightCodeLines])

  // ==================== Inline 代码运行 ====================

  const handleInlineRun = useCallback((inlineCode: string) => {
    // 1. 加载代码到编辑器
    setCode(inlineCode)

    // 2. 执行代码（通过父组件传入的回调）
    if (onCodeExecute) {
      onCodeExecute(inlineCode)
    }
  }, [onCodeExecute])

  // ==================== 分隔符拖拽 ====================

  const handleMouseDown = useCallback(() => {
    setIsDragging(true)
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return

    const container = containerRef.current
    const containerRect = container.getBoundingClientRect()
    const newPosition = ((e.clientX - containerRect.left) / containerRect.width) * 100

    // 限制范围 30% - 70%
    if (newPosition >= 30 && newPosition <= 70) {
      setSplitPosition(newPosition)
    }
  }, [isDragging])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    } else {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  // ==================== 自定义 Markdown 组件 ====================

  const components = {
    // 代码块渲染
    code: ({ node, inline, className, children, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || '')
      const language = match ? match[1] : ''
      const codeString = String(children).replace(/\n$/, '')

      // 检查是否可运行
      const isRunnable = className?.includes('runnable')

      if (!inline && match) {
        return (
          <div className="code-block-wrapper">
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={language}
              PreTag="div"
              {...props}
            >
              {codeString}
            </SyntaxHighlighter>
            {isRunnable && (
              <button
                className="inline-run-button"
                onClick={() => handleInlineRun(codeString)}
                title="运行这段代码"
              >
                ▶ 运行
              </button>
            )}
          </div>
        )
      }

      return (
        <code className={className} {...props}>
          {children}
        </code>
      )
    },

    // 链接渲染（处理代码引用）
    a: ({ href, children, ...props }: any) => {
      // 检查是否是代码引用
      const codeRefMatch = href?.match(/#code-line-(\d+)/)
      if (codeRefMatch) {
        const lineNumber = parseInt(codeRefMatch[1], 10)
        return (
          <a
            href="#"
            className="code-reference"
            onClick={(e) => {
              e.preventDefault()
              handleCodeReference(lineNumber)
            }}
            {...props}
          >
            {children} 🔗
          </a>
        )
      }

      return <a href={href} {...props}>{children}</a>
    },

    // Section 包装器（添加 section-id）
    h2: ({ children, ...props }: any) => {
      const sectionId = String(children).toLowerCase().replace(/\s+/g, '-')
      return (
        <h2 data-section-id={sectionId} {...props}>
          {children}
        </h2>
      )
    }
  }

  // ==================== 渲染 ====================

  if (isLoading) {
    return (
      <div className="interactive-textbook-loading">
        <div className="loading-spinner"></div>
        <p>加载教材中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="interactive-textbook-error">
        <p>❌ 教材加载失败</p>
        <p style={{ fontSize: '0.875rem', marginTop: '0.5rem', color: '#999' }}>
          {error instanceof Error ? error.message : '未知错误'}
        </p>
      </div>
    )
  }

  if (!textbook) {
    return (
      <div className="interactive-textbook-error">
        <p>教材数据为空</p>
      </div>
    )
  }

  return (
    <div className="interactive-textbook" ref={containerRef}>
      {/* 左侧：教材内容 */}
      <div
        className="textbook-panel"
        ref={textbookRef}
        style={{ width: `${splitPosition}%` }}
      >
        <div className="textbook-header">
          <h1>{textbook.title}</h1>
        </div>
        <div className="textbook-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={components}
          >
            {textbook.sections
              .map(s => {
                // If section has a title (not intro), add it as ## heading
                if (s.id !== 'intro') {
                  return `## ${s.title}\n\n${s.content}`
                }
                return s.content
              })
              .join('\n\n')}
          </ReactMarkdown>
        </div>
      </div>

      {/* 分隔符 */}
      <div
        className={`split-divider ${isDragging ? 'dragging' : ''}`}
        onMouseDown={handleMouseDown}
      >
        <div className="split-handle">⋮</div>
      </div>

      {/* 右侧：代码编辑器 */}
      <div
        className="code-panel"
        style={{ width: `${100 - splitPosition}%` }}
      >
        <div className="code-header">
          <span>代码编辑器</span>
          <button
            className="execute-button"
            onClick={() => onCodeExecute?.(code)}
          >
            ▶ 执行代码
          </button>
        </div>
        <MonacoEditor
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value || '')}
          onMount={(editor) => {
            editorRef.current = editor

            // 监听代码编辑器的滚动事件（双向同步）
            editor.onDidScrollChange(() => {
              // 使用节流避免频繁触发
              const timeoutId = setTimeout(() => {
                handleCodeScroll()
              }, 150)

              // 清理函数
              return () => clearTimeout(timeoutId)
            })
          }}
          options={{
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            automaticLayout: true
          }}
        />
      </div>
    </div>
  )
}

export default InteractiveTextbook
