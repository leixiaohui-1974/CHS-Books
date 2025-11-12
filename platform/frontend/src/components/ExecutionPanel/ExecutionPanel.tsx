/**
 * 代码执行结果面板
 *
 * 功能：
 * - 显示代码执行结果（输出、错误、图表）
 * - 支持实时流式输出
 * - 支持多种输出类型（文本、图像、表格、错误）
 * - 可折叠/展开
 */

import React, { useState, useEffect, useRef } from 'react'
import './ExecutionPanel.css'

// ==================== 类型定义 ====================

export interface ExecutionResult {
  status: 'success' | 'error' | 'timeout' | 'running'
  stdout?: string
  stderr?: string
  error?: string
  executionTime?: number
  outputs?: ExecutionOutput[]
}

export interface ExecutionOutput {
  type: 'text' | 'image' | 'table' | 'error' | 'plot'
  data: any
  timestamp?: number
}

export interface ExecutionPanelProps {
  result: ExecutionResult | null
  isExecuting: boolean
  onClear?: () => void
}

// ==================== 主组件 ====================

export const ExecutionPanel: React.FC<ExecutionPanelProps> = ({
  result,
  isExecuting,
  onClear
}) => {
  const [isExpanded, setIsExpanded] = useState(true)
  const outputRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  useEffect(() => {
    if (outputRef.current && result) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [result])

  // ==================== 渲染函数 ====================

  const renderStatusIcon = () => {
    if (isExecuting) {
      return <span className="status-icon executing">⏳</span>
    }

    if (!result) {
      return <span className="status-icon idle">💤</span>
    }

    switch (result.status) {
      case 'success':
        return <span className="status-icon success">✅</span>
      case 'error':
        return <span className="status-icon error">❌</span>
      case 'timeout':
        return <span className="status-icon timeout">⏱️</span>
      default:
        return <span className="status-icon">❓</span>
    }
  }

  const renderStatusText = () => {
    if (isExecuting) {
      return '执行中...'
    }

    if (!result) {
      return '等待执行'
    }

    switch (result.status) {
      case 'success':
        return `执行成功 (${result.executionTime}ms)`
      case 'error':
        return '执行失败'
      case 'timeout':
        return '执行超时'
      default:
        return '未知状态'
    }
  }

  const renderOutput = () => {
    if (isExecuting) {
      return (
        <div className="execution-loading">
          <div className="loading-spinner-small"></div>
          <p>代码执行中，请稍候...</p>
        </div>
      )
    }

    if (!result) {
      return (
        <div className="execution-empty">
          <p>点击"执行代码"按钮运行当前代码</p>
        </div>
      )
    }

    return (
      <div className="execution-results" ref={outputRef}>
        {/* 标准输出 */}
        {result.stdout && (
          <div className="output-section">
            <div className="output-section-header">
              <span className="output-icon">📤</span>
              <span>标准输出 (stdout)</span>
            </div>
            <pre className="output-content stdout">{result.stdout}</pre>
          </div>
        )}

        {/* 标准错误 */}
        {result.stderr && (
          <div className="output-section">
            <div className="output-section-header">
              <span className="output-icon">⚠️</span>
              <span>标准错误 (stderr)</span>
            </div>
            <pre className="output-content stderr">{result.stderr}</pre>
          </div>
        )}

        {/* 错误信息 */}
        {result.error && (
          <div className="output-section error">
            <div className="output-section-header">
              <span className="output-icon">❌</span>
              <span>错误信息</span>
            </div>
            <pre className="output-content error-message">{result.error}</pre>
          </div>
        )}

        {/* 富输出（图表、表格等） */}
        {result.outputs && result.outputs.length > 0 && (
          <div className="output-section">
            <div className="output-section-header">
              <span className="output-icon">📊</span>
              <span>输出结果</span>
            </div>
            <div className="rich-outputs">
              {result.outputs.map((output, index) => renderRichOutput(output, index))}
            </div>
          </div>
        )}

        {/* 无输出提示 */}
        {!result.stdout && !result.stderr && !result.error && (!result.outputs || result.outputs.length === 0) && (
          <div className="execution-empty">
            <p>代码执行完成，但没有产生输出</p>
          </div>
        )}
      </div>
    )
  }

  const renderRichOutput = (output: ExecutionOutput, index: number) => {
    switch (output.type) {
      case 'text':
        return (
          <div key={index} className="rich-output text-output">
            <pre>{output.data}</pre>
          </div>
        )

      case 'image':
      case 'plot':
        return (
          <div key={index} className="rich-output image-output">
            <img src={output.data} alt={`输出 ${index + 1}`} />
          </div>
        )

      case 'table':
        return (
          <div key={index} className="rich-output table-output">
            {renderTable(output.data)}
          </div>
        )

      case 'error':
        return (
          <div key={index} className="rich-output error-output">
            <pre>{output.data}</pre>
          </div>
        )

      default:
        return (
          <div key={index} className="rich-output unknown-output">
            <pre>{JSON.stringify(output.data, null, 2)}</pre>
          </div>
        )
    }
  }

  const renderTable = (data: any) => {
    // 简单的表格渲染
    if (Array.isArray(data) && data.length > 0) {
      const headers = Object.keys(data[0])

      return (
        <table className="output-table">
          <thead>
            <tr>
              {headers.map((header) => (
                <th key={header}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {headers.map((header) => (
                  <td key={header}>{row[header]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )
    }

    return <pre>{JSON.stringify(data, null, 2)}</pre>
  }

  // ==================== 渲染 ====================

  return (
    <div className={`execution-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* 标题栏 */}
      <div className="execution-panel-header">
        <div className="header-left">
          {renderStatusIcon()}
          <span className="status-text">{renderStatusText()}</span>
        </div>

        <div className="header-right">
          {result && onClear && (
            <button
              className="clear-button"
              onClick={onClear}
              title="清除结果"
            >
              🗑️ 清除
            </button>
          )}

          <button
            className="collapse-button"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? '折叠' : '展开'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>

      {/* 内容区域 */}
      {isExpanded && (
        <div className="execution-panel-content">
          {renderOutput()}
        </div>
      )}
    </div>
  )
}

export default ExecutionPanel
