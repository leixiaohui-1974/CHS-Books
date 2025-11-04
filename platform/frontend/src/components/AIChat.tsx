/**
 * AI对话组件 - V2.0
 * 智能问答、代码讲解、错误诊断
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import {
  Card,
  Input,
  Button,
  Space,
  Avatar,
  Tag,
  Divider,
  Spin
} from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  BulbOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'

const { TextArea } = Input

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  type?: 'text' | 'code' | 'error'
}

interface AIChatProps {
  sessionId: string
  onClose?: () => void
}

export const AIChat: React.FC<AIChatProps> = ({
  sessionId,
  onClose
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是AI学习助手，有什么可以帮你的吗？\n\n我可以帮你：\n- 📖 解答理论问题\n- 💻 讲解代码逻辑\n- 🐛 诊断代码错误\n- 💡 提供学习建议',
      timestamp: new Date(),
      type: 'text'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<any>(null)

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 聚焦输入框
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  /**
   * 发送消息
   */
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('/api/v1/ai/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: input,
          context: {
            // 可以包含当前代码、案例信息等
          }
        })
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || '抱歉，我遇到了一些问题，请稍后再试。',
        timestamp: new Date(),
        type: 'text'
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('发送消息失败:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，发送消息失败，请检查网络连接后重试。',
        timestamp: new Date(),
        type: 'error'
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  /**
   * 快捷问题
   */
  const quickQuestions = [
    '解释扩散方程的原理',
    '如何选择时间步长？',
    'Crank-Nicolson格式是什么？',
    '显式格式的稳定性条件'
  ]

  const handleQuickQuestion = (question: string) => {
    setInput(question)
    inputRef.current?.focus()
  }

  /**
   * 格式化时间
   */
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <Card
      title={
        <Space>
          <RobotOutlined style={{ color: '#1890ff' }} />
          <span>AI学习助手</span>
          <Tag color="blue">V2.0</Tag>
        </Space>
      }
      extra={
        onClose && (
          <Button type="text" onClick={onClose}>
            收起
          </Button>
        )
      }
      style={{ height: '600px', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
    >
      {/* 消息列表 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          backgroundColor: '#f5f5f5'
        }}
      >
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              marginBottom: '16px',
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
            }}
          >
            <div
              style={{
                maxWidth: '80%',
                display: 'flex',
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                gap: '8px'
              }}
            >
              {/* 头像 */}
              <Avatar
                icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{
                  backgroundColor: message.role === 'user' ? '#1890ff' : '#52c41a',
                  flexShrink: 0
                }}
              />

              {/* 消息内容 */}
              <div>
                <div
                  style={{
                    backgroundColor: message.role === 'user' ? '#1890ff' : '#fff',
                    color: message.role === 'user' ? '#fff' : '#000',
                    padding: '12px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}
                >
                  {message.type === 'text' ? (
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  ) : message.type === 'code' ? (
                    <pre
                      style={{
                        backgroundColor: '#1e1e1e',
                        color: '#d4d4d4',
                        padding: '8px',
                        borderRadius: '4px',
                        overflow: 'auto'
                      }}
                    >
                      {message.content}
                    </pre>
                  ) : (
                    <span>{message.content}</span>
                  )}
                </div>
                
                <div
                  style={{
                    fontSize: '12px',
                    color: '#999',
                    marginTop: '4px',
                    textAlign: message.role === 'user' ? 'right' : 'left'
                  }}
                >
                  {formatTime(message.timestamp)}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ textAlign: 'center', padding: '16px' }}>
            <Spin tip="AI正在思考..." />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 快捷问题 */}
      {messages.length === 1 && (
        <div style={{ padding: '12px', backgroundColor: '#fff', borderTop: '1px solid #f0f0f0' }}>
          <div style={{ fontSize: '12px', color: '#999', marginBottom: '8px' }}>
            <QuestionCircleOutlined /> 快捷问题：
          </div>
          <Space wrap>
            {quickQuestions.map((question, index) => (
              <Tag
                key={index}
                onClick={() => handleQuickQuestion(question)}
                style={{ cursor: 'pointer' }}
                icon={<BulbOutlined />}
              >
                {question}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {/* 输入框 */}
      <div
        style={{
          padding: '16px',
          backgroundColor: '#fff',
          borderTop: '1px solid #f0f0f0'
        }}
      >
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            placeholder="输入你的问题... (Shift+Enter换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
            style={{ resize: 'none' }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={sendMessage}
            loading={loading}
            disabled={!input.trim()}
          >
            发送
          </Button>
        </Space.Compact>
        
        <div style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
          💡 提示：可以问我理论问题、代码问题或请求学习建议
        </div>
      </div>
    </Card>
  )
}

export default AIChat
