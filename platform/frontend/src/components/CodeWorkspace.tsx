/**
 * 代码工作台组件 - V2.0
 * 集成代码编辑、实时执行、结果展示
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { 
  Card, 
  Button, 
  Space, 
  Tabs, 
  Tree, 
  Input,
  message,
  Tag,
  Progress,
  Divider,
  Spin
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  SaveOutlined,
  ReloadOutlined,
  CodeOutlined,
  FileOutlined,
  FolderOutlined,
  RobotOutlined
} from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'

const { TextArea } = Input
const { TabPane } = Tabs

interface CodeWorkspaceProps {
  sessionId: string
  caseSlug: string
  bookSlug: string
  onExecutionComplete?: (result: any) => void
}

interface ExecutionStatus {
  status: 'idle' | 'loading' | 'running' | 'completed' | 'failed'
  progress: number
  output: string[]
  result?: any
  error?: string
}

export const CodeWorkspace: React.FC<CodeWorkspaceProps> = ({
  sessionId,
  caseSlug,
  bookSlug,
  onExecutionComplete
}) => {
  // 状态管理
  const [files, setFiles] = useState<any>({})
  const [currentFile, setCurrentFile] = useState<string>('main.py')
  const [code, setCode] = useState<string>('')
  const [originalCode, setOriginalCode] = useState<string>('')
  const [execution, setExecution] = useState<ExecutionStatus>({
    status: 'idle',
    progress: 0,
    output: []
  })
  const [aiExplanation, setAiExplanation] = useState<string>('')
  const [isLoadingAI, setIsLoadingAI] = useState(false)
  
  const wsRef = useRef<WebSocket | null>(null)
  const outputEndRef = useRef<HTMLDivElement>(null)

  // 加载代码文件
  useEffect(() => {
    loadCaseFiles()
  }, [sessionId, caseSlug])

  // 自动滚动到输出底部
  useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [execution.output])

  /**
   * 加载案例代码文件
   */
  const loadCaseFiles = async () => {
    try {
      const response = await fetch(`/api/v1/code/${sessionId}/files`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setFiles(data.files)
        
        // 加载主文件
        if (data.files['main.py']) {
          setCode(data.files['main.py'])
          setOriginalCode(data.files['main.py'])
        }
        
        message.success(`加载了 ${Object.keys(data.files).length} 个文件`)
      }
    } catch (error) {
      message.error('加载代码文件失败')
      console.error(error)
    }
  }

  /**
   * 保存代码修改
   */
  const saveCode = async () => {
    try {
      const response = await fetch(`/api/v1/code/${sessionId}/edit`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          file_path: currentFile,
          content: code
        })
      })
      
      const data = await response.json()
      
      if (data.success) {
        message.success('代码已保存')
        setOriginalCode(code)
      } else {
        message.error(data.error || '保存失败')
      }
    } catch (error) {
      message.error('保存代码失败')
      console.error(error)
    }
  }

  /**
   * 执行代码
   */
  const executeCode = async () => {
    // 先保存代码
    await saveCode()
    
    try {
      setExecution({
        status: 'loading',
        progress: 0,
        output: ['正在启动执行...']
      })
      
      // 发起执行请求
      const response = await fetch('/api/v1/execution/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          script_path: 'main.py',
          input_params: {
            // 可以从UI收集参数
          }
        })
      })
      
      const data = await response.json()
      
      if (data.execution_id) {
        // 建立WebSocket连接
        connectWebSocket(data.execution_id)
        
        setExecution(prev => ({
          ...prev,
          status: 'running',
          output: [...prev.output, `执行ID: ${data.execution_id}`]
        }))
      }
    } catch (error) {
      setExecution(prev => ({
        ...prev,
        status: 'failed',
        error: '启动执行失败'
      }))
      message.error('启动执行失败')
    }
  }

  /**
   * 连接WebSocket接收实时输出
   */
  const connectWebSocket = (executionId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/execution/ws/${executionId}`)
    wsRef.current = ws
    
    ws.onopen = () => {
      console.log('WebSocket连接已建立')
    }
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      switch (message.type) {
        case 'status':
          setExecution(prev => ({
            ...prev,
            output: [...prev.output, `状态: ${message.data.status}`]
          }))
          break
          
        case 'output':
          setExecution(prev => ({
            ...prev,
            output: [...prev.output, message.data.text]
          }))
          break
          
        case 'progress':
          setExecution(prev => ({
            ...prev,
            progress: message.data.percentage || 0
          }))
          break
          
        case 'completed':
          setExecution(prev => ({
            ...prev,
            status: 'completed',
            progress: 100,
            output: [...prev.output, '✅ 执行完成！'],
            result: message.data
          }))
          
          if (onExecutionComplete) {
            onExecutionComplete(message.data)
          }
          break
          
        case 'failed':
          setExecution(prev => ({
            ...prev,
            status: 'failed',
            output: [...prev.output, `❌ 执行失败: ${message.data.error}`],
            error: message.data.error
          }))
          break
          
        case 'timeout':
          setExecution(prev => ({
            ...prev,
            status: 'failed',
            output: [...prev.output, '⏱️ 执行超时']
          }))
          break
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      setExecution(prev => ({
        ...prev,
        status: 'failed',
        output: [...prev.output, '❌ WebSocket连接错误']
      }))
    }
    
    ws.onclose = () => {
      console.log('WebSocket连接已关闭')
    }
  }

  /**
   * AI代码讲解
   */
  const explainCode = async () => {
    setIsLoadingAI(true)
    
    try {
      const response = await fetch('/api/v1/ai/explain-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          code: code,
          context: `这是${caseSlug}的代码`
        })
      })
      
      const data = await response.json()
      setAiExplanation(data.explanation)
      message.success('AI讲解已生成')
    } catch (error) {
      message.error('AI讲解失败')
    } finally {
      setIsLoadingAI(false)
    }
  }

  /**
   * 恢复原始代码
   */
  const resetCode = () => {
    setCode(originalCode)
    message.info('已恢复到原始版本')
  }

  // 文件树数据
  const fileTreeData: DataNode[] = Object.keys(files).map(filePath => ({
    title: filePath,
    key: filePath,
    icon: <FileOutlined />
  }))

  const hasChanges = code !== originalCode

  return (
    <div className="code-workspace">
      <Card
        title={
          <Space>
            <CodeOutlined />
            <span>代码工作台 - {caseSlug}</span>
            {hasChanges && <Tag color="orange">已修改</Tag>}
          </Space>
        }
        extra={
          <Space>
            <Button
              icon={<RobotOutlined />}
              onClick={explainCode}
              loading={isLoadingAI}
            >
              AI讲解
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={resetCode}
              disabled={!hasChanges}
            >
              恢复
            </Button>
            <Button
              icon={<SaveOutlined />}
              onClick={saveCode}
              type="primary"
              disabled={!hasChanges}
            >
              保存
            </Button>
            <Button
              icon={<PlayCircleOutlined />}
              onClick={executeCode}
              type="primary"
              loading={execution.status === 'running'}
              danger
            >
              运行
            </Button>
          </Space>
        }
      >
        <div style={{ display: 'flex', height: '600px' }}>
          {/* 左侧文件树 */}
          <div style={{ width: '200px', borderRight: '1px solid #f0f0f0', padding: '10px' }}>
            <h4>📁 文件</h4>
            <Tree
              treeData={fileTreeData}
              onSelect={(keys) => {
                if (keys[0]) {
                  setCurrentFile(keys[0] as string)
                  setCode(files[keys[0]] || '')
                  setOriginalCode(files[keys[0]] || '')
                }
              }}
              selectedKeys={[currentFile]}
            />
          </div>

          {/* 中间代码编辑器 */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Tabs defaultActiveKey="editor" style={{ flex: 1 }}>
              <TabPane tab="编辑器" key="editor">
                <TextArea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  style={{ 
                    height: '550px', 
                    fontFamily: 'Monaco, Consolas, monospace',
                    fontSize: '14px'
                  }}
                  placeholder="在此编辑代码..."
                />
              </TabPane>
              
              <TabPane tab="AI讲解" key="ai">
                <div style={{ padding: '10px', height: '550px', overflow: 'auto' }}>
                  {isLoadingAI ? (
                    <Spin tip="AI正在分析代码..." />
                  ) : aiExplanation ? (
                    <div dangerouslySetInnerHTML={{ __html: aiExplanation.replace(/\n/g, '<br/>') }} />
                  ) : (
                    <p style={{ color: '#999' }}>点击"AI讲解"按钮获取代码解释</p>
                  )}
                </div>
              </TabPane>
            </Tabs>
          </div>

          {/* 右侧输出和结果 */}
          <div style={{ width: '350px', borderLeft: '1px solid #f0f0f0', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '10px', borderBottom: '1px solid #f0f0f0' }}>
              <h4>📟 控制台</h4>
              {execution.status === 'running' && (
                <Progress percent={execution.progress} size="small" />
              )}
            </div>
            
            <div 
              style={{ 
                flex: 1, 
                padding: '10px', 
                overflow: 'auto',
                backgroundColor: '#1e1e1e',
                color: '#d4d4d4',
                fontFamily: 'Monaco, Consolas, monospace',
                fontSize: '12px'
              }}
            >
              {execution.output.map((line, index) => (
                <div key={index}>{line}</div>
              ))}
              <div ref={outputEndRef} />
            </div>
            
            {execution.status === 'completed' && execution.result && (
              <div style={{ padding: '10px', borderTop: '1px solid #f0f0f0' }}>
                <Button type="link" onClick={() => {
                  // 跳转到结果页面
                  window.location.href = `/results/${execution.result.execution_id}`
                }}>
                  查看完整结果 →
                </Button>
              </div>
            )}
          </div>
        </div>
      </Card>

      <style jsx>{`
        .code-workspace :global(.ant-card-body) {
          padding: 0 !important;
        }
      `}</style>
    </div>
  )
}

export default CodeWorkspace
