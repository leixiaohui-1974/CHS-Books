'use client'

import React, { useState, useEffect } from 'react'
import { Layout, Typography, Card, Button, Tag, Space, Spin, message, Tabs, Tree, Row, Col, Image, Divider, Statistic, Alert } from 'antd'
import { BookOutlined, PlayCircleOutlined, CheckCircleOutlined, CloseCircleOutlined, CodeOutlined, FileTextOutlined, LineChartOutlined, FolderOutlined, HomeOutlined } from '@ant-design/icons'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize'

// 配置sanitize以允许details和summary标签
const sanitizeSchema = {
  ...defaultSchema,
  tagNames: [
    ...(defaultSchema.tagNames || []),
    'details',
    'summary'
  ]
}

const { Header, Content, Sider } = Layout
const { Title, Paragraph, Text } = Typography
const { TabPane } = Tabs

interface Book {
  id: string
  slug: string
  title: string
  subtitle: string
  description: string
  level: string
  tags: string[]
  stats: {
    cases: number
    hours: number
    students: number
  }
  rating: number
  price: {
    original: number
    current: number
  }
  cases?: any[]
  actual_cases?: number
}

interface CaseInfo {
  id: string
  name: string
  path: string
  has_readme: boolean
  has_main: boolean
  title?: string
}

interface TestResult {
  success: boolean
  returncode?: number
  stdout?: string
  stderr?: string
  case_id: string
  images?: Array<{
    filename: string
    url: string
  }>
}

export default function BookDetailPage() {
  const params = useParams()
  const bookSlug = params.slug as string

  const [book, setBook] = useState<Book | null>(null)
  const [cases, setCases] = useState<CaseInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCase, setSelectedCase] = useState<CaseInfo | null>(null)
  const [testing, setTesting] = useState(false)
  const [testResults, setTestResults] = useState<Map<string, TestResult>>(new Map())
  const [currentResult, setCurrentResult] = useState<TestResult | null>(null)
  const [caseCode, setCaseCode] = useState<string>('')
  const [caseReadme, setCaseReadme] = useState<string>('')

  useEffect(() => {
    loadBookData()
  }, [bookSlug])

  useEffect(() => {
    if (selectedCase) {
      loadCaseDetail(selectedCase.id)
    }
  }, [selectedCase])

  const loadBookData = async () => {
    try {
      const bookRes = await fetch(`http://localhost:8000/api/v1/books/${bookSlug}`)
      const bookData = await bookRes.json()
      
      if (bookData.success) {
        setBook(bookData.book)
        
        const casesRes = await fetch(`http://localhost:8000/api/v1/books/${bookSlug}/cases`)
        const casesData = await casesRes.json()
        
        if (casesData.success) {
          const casesList = casesData.cases || []
          setCases(casesList)
          // 默认选中第一个案例
          if (casesList.length > 0) {
            setSelectedCase(casesList[0])
          }
        }
      }
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const loadCaseDetail = async (caseId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/books/${bookSlug}/cases/${caseId}`)
      const data = await res.json()
      
      if (data.success) {
        setCaseCode(data.case.code || '// 代码文件不存在')
        setCaseReadme(data.case.readme || '# 暂无文档')
      }
    } catch (error) {
      console.error('加载案例详情失败:', error)
    }
  }

  const runCase = async () => {
    if (!selectedCase) return
    
    setTesting(true)
    setCurrentResult(null)
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/books/${bookSlug}/cases/${selectedCase.id}/run`, {
        method: 'POST'
      })
      const result = await res.json()
      
      const newResults = new Map(testResults)
      newResults.set(selectedCase.id, result)
      setTestResults(newResults)
      setCurrentResult(result)
      
      if (result.success) {
        message.success('执行成功！')
      } else {
        message.error('执行失败')
      }
    } catch (error) {
      message.error('执行失败')
    } finally {
      setTesting(false)
    }
  }

  // 构建树形数据
  const buildTreeData = () => {
    return cases.map((caseInfo, index) => {
      const result = testResults.get(caseInfo.id)
      const icon = result ? (
        result.success ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      ) : <CodeOutlined style={{ color: '#999' }} />
      
      return {
        title: `案例${index + 1}：${caseInfo.title || caseInfo.id}`,
        key: caseInfo.id,
        icon,
        caseInfo
      }
    })
  }

  const onSelectCase = (selectedKeys: any[], info: any) => {
    if (selectedKeys.length > 0 && info.node.caseInfo) {
      setSelectedCase(info.node.caseInfo)
      setCurrentResult(testResults.get(info.node.caseInfo.id) || null)
    }
  }

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin size="large" tip="加载中..." />
        </Content>
      </Layout>
    )
  }

  if (!book) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px' }}>
          <Title level={2}>书籍不存在</Title>
        </Content>
      </Layout>
    )
  }

  const testedCount = Array.from(testResults.values()).filter(r => r.success).length
  const totalCount = cases.length

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ 
        background: '#fff', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <Link href="/" style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff', textDecoration: 'none' }}>
          <BookOutlined /> Engineering Learning Platform
        </Link>
        <Space>
          <Link href="/"><Button type="text" icon={<HomeOutlined />}>首页</Button></Link>
          <Link href="/books"><Button type="text" icon={<FolderOutlined />}>所有课程</Button></Link>
        </Space>
      </Header>

      <Layout>
        {/* 左侧树形导航 */}
        <Sider 
          width={320} 
          style={{ 
            background: '#fff', 
            borderRight: '1px solid #f0f0f0',
            height: 'calc(100vh - 64px)',
            overflow: 'auto',
            position: 'sticky',
            top: 64
          }}
        >
          <div style={{ padding: '16px' }}>
            <Title level={4} style={{ marginBottom: '8px' }}>{book.title}</Title>
            <Paragraph type="secondary" style={{ fontSize: '12px', marginBottom: '16px' }}>
              {book.subtitle}
            </Paragraph>
            
            <Space direction="vertical" style={{ width: '100%', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary">测试进度</Text>
                <Text strong>{testedCount}/{totalCount}</Text>
              </div>
              <div style={{ 
                height: '8px', 
                background: '#f0f0f0', 
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${totalCount > 0 ? (testedCount / totalCount * 100) : 0}%`,
                  height: '100%',
                  background: '#52c41a',
                  transition: 'width 0.3s'
                }} />
              </div>
            </Space>

            <Divider style={{ margin: '12px 0' }} />

            <Tree
              showIcon
              defaultExpandAll
              selectedKeys={selectedCase ? [selectedCase.id] : []}
              treeData={buildTreeData()}
              onSelect={onSelectCase}
              style={{ background: '#fff' }}
            />
          </div>
        </Sider>

        {/* 右侧内容区 */}
        <Content style={{ padding: '24px', background: '#f5f5f5', minHeight: 'calc(100vh - 64px)', overflow: 'auto' }}>
          {selectedCase ? (
            <div>
              {/* 案例标题和操作栏 */}
              <Card 
                style={{ marginBottom: '16px' }}
                bodyStyle={{ padding: '16px 24px' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Title level={3} style={{ marginBottom: '4px' }}>
                      {selectedCase.title || selectedCase.name}
                    </Title>
                    <Space size="small">
                      <Text type="secondary" code>{selectedCase.id}</Text>
                      {selectedCase.has_readme && <Tag color="green">有文档</Tag>}
                      {selectedCase.has_main && <Tag color="blue">有代码</Tag>}
                    </Space>
                  </div>
                  <Button 
                    type="primary" 
                    size="large"
                    icon={<PlayCircleOutlined />}
                    onClick={runCase}
                    loading={testing}
                  >
                    {testing ? '运行中...' : '运行测试'}
                  </Button>
                </div>
              </Card>

              {/* 测试结果统计 */}
              {currentResult && (
                <Card 
                  style={{ marginBottom: '16px' }}
                  bodyStyle={{ padding: '16px 24px' }}
                >
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic 
                        title="执行状态" 
                        value={currentResult.success ? '成功' : '失败'} 
                        valueStyle={{ color: currentResult.success ? '#3f8600' : '#cf1322' }}
                        prefix={currentResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic title="返回码" value={currentResult.returncode || 0} />
                    </Col>
                    <Col span={6}>
                      <Statistic 
                        title="生成图表" 
                        value={currentResult.images?.length || 0} 
                        suffix="张"
                        prefix={<LineChartOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic 
                        title="输出行数" 
                        value={currentResult.stdout?.split('\n').length || 0} 
                        suffix="行"
                      />
                    </Col>
                  </Row>
                </Card>
              )}

              {/* 主要内容标签页 */}
              <Card>
                <Tabs defaultActiveKey="results" size="large">
                  {/* 运行结果 */}
                  <TabPane 
                    tab={<span><LineChartOutlined />运行结果</span>} 
                    key="results"
                  >
                    {currentResult ? (
                      <div>
                        {/* 生成的图表 */}
                        {currentResult.images && currentResult.images.length > 0 && (
                          <div style={{ marginBottom: '24px' }}>
                            <Title level={4}>
                              <LineChartOutlined /> 生成的图表 ({currentResult.images.length})
                            </Title>
                            <Row gutter={[16, 16]}>
                              {currentResult.images.map((img, idx) => (
                                <Col span={12} key={idx}>
                                  <Card 
                                    hoverable
                                    cover={
                                      <Image
                                        src={`http://localhost:8000${img.url}`}
                                        alt={img.filename}
                                        style={{ width: '100%' }}
                                      />
                                    }
                                  >
                                    <Card.Meta 
                                      title={img.filename}
                                      description={`图表 ${idx + 1}`}
                                    />
                                  </Card>
                                </Col>
                              ))}
                            </Row>
                            <Divider />
                          </div>
                        )}

                        {/* 控制台输出 */}
                        <Title level={4}>
                          <FileTextOutlined /> 控制台输出
                        </Title>
                        <div style={{ 
                          background: '#0d1117', 
                          padding: '20px', 
                          borderRadius: '8px',
                          maxHeight: '600px',
                          overflow: 'auto',
                          border: '1px solid #30363d'
                        }}>
                          <pre style={{ 
                            margin: 0,
                            background: 'transparent',
                            color: '#c9d1d9',
                            fontFamily: "'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace",
                            fontSize: '14px',
                            lineHeight: '1.8',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word'
                          }}>
                            {currentResult.stdout || '无输出'}
                          </pre>
                        </div>

                        {/* 错误信息 */}
                        {currentResult.stderr && (
                          <>
                            <Divider />
                            <Alert
                              message="错误信息"
                              description={
                                <pre style={{ 
                                  margin: 0, 
                                  whiteSpace: 'pre-wrap', 
                                  wordBreak: 'break-all',
                                  fontSize: '12px'
                                }}>
                                  {currentResult.stderr}
                                </pre>
                              }
                              type="error"
                              showIcon
                            />
                          </>
                        )}
                      </div>
                    ) : (
                      <div style={{ 
                        textAlign: 'center', 
                        padding: '60px 20px',
                        color: '#999'
                      }}>
                        <PlayCircleOutlined style={{ fontSize: '64px', marginBottom: '16px' }} />
                        <div style={{ fontSize: '16px' }}>点击"运行测试"按钮查看结果</div>
                      </div>
                    )}
                  </TabPane>

                  {/* 源代码 */}
                  <TabPane 
                    tab={<span><CodeOutlined />源代码</span>} 
                    key="code"
                  >
                    <div style={{ 
                      maxHeight: '700px',
                      overflow: 'auto',
                      borderRadius: '8px',
                      border: '1px solid #e1e4e8'
                    }}>
                      <SyntaxHighlighter
                        language="python"
                        style={vscDarkPlus}
                        showLineNumbers={true}
                        customStyle={{
                          margin: 0,
                          borderRadius: '8px',
                          fontSize: '14px',
                          lineHeight: '1.6'
                        }}
                        codeTagProps={{
                          style: {
                            fontFamily: "'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace"
                          }
                        }}
                      >
                        {caseCode || '// 代码文件不存在'}
                      </SyntaxHighlighter>
                    </div>
                  </TabPane>

                  {/* 文档说明 */}
                  <TabPane 
                    tab={<span><FileTextOutlined />文档说明</span>} 
                    key="readme"
                  >
                    <div style={{ 
                      background: '#fff',
                      padding: '32px',
                      borderRadius: '8px',
                      minHeight: '500px',
                      border: '1px solid #e1e4e8'
                    }}>
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw, [rehypeSanitize, sanitizeSchema]]}
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '')
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                customStyle={{
                                  borderRadius: '8px',
                                  fontSize: '13px',
                                  margin: '16px 0'
                                }}
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} style={{
                                background: '#f6f8fa',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontFamily: "'Fira Code', 'Consolas', monospace",
                                fontSize: '13px',
                                color: '#24292f'
                              }} {...props}>
                                {children}
                              </code>
                            )
                          },
                          h1: ({ node, ...props }) => <h1 style={{ borderBottom: '2px solid #e1e4e8', paddingBottom: '8px', marginTop: '24px', color: '#24292f' }} {...props} />,
                          h2: ({ node, ...props }) => <h2 style={{ borderBottom: '1px solid #e1e4e8', paddingBottom: '6px', marginTop: '24px', color: '#24292f' }} {...props} />,
                          h3: ({ node, ...props }) => <h3 style={{ marginTop: '20px', color: '#24292f' }} {...props} />,
                          table: ({ node, ...props }) => (
                            <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
                              <table style={{ borderCollapse: 'collapse', width: '100%' }} {...props} />
                            </div>
                          ),
                          th: ({ node, ...props }) => <th style={{ border: '1px solid #d0d7de', padding: '8px 12px', background: '#f6f8fa', fontWeight: 600 }} {...props} />,
                          td: ({ node, ...props }) => <td style={{ border: '1px solid #d0d7de', padding: '8px 12px' }} {...props} />,
                          ul: ({ node, ...props }) => <ul style={{ paddingLeft: '24px', marginBottom: '16px' }} {...props} />,
                          ol: ({ node, ...props }) => <ol style={{ paddingLeft: '24px', marginBottom: '16px' }} {...props} />,
                          li: ({ node, ...props }) => <li style={{ marginBottom: '4px' }} {...props} />,
                          blockquote: ({ node, ...props }) => <blockquote style={{ borderLeft: '4px solid #d0d7de', padding: '0 16px', color: '#57606a', margin: '16px 0' }} {...props} />,
                          p: ({ node, ...props }) => <p style={{ marginBottom: '16px', lineHeight: '1.7', color: '#24292f' }} {...props} />,
                          a: ({ node, ...props }) => <a style={{ color: '#0969da', textDecoration: 'none' }} {...props} />,
                          img: ({ node, src, alt, ...props }) => {
                            // 如果是本地图片路径，转换为API URL
                            const imageSrc = src?.endsWith('.png') && !src.startsWith('http') 
                              ? `http://localhost:8000/api/v1/books/${bookSlug}/cases/${selectedCase?.id}/images/${src}`
                              : src
                            return (
                              <div style={{ margin: '24px 0', textAlign: 'center' }}>
                                <Image
                                  src={imageSrc}
                                  alt={alt}
                                  style={{ maxWidth: '100%', borderRadius: '8px', border: '1px solid #d0d7de' }}
                                  preview={{
                                    mask: <div style={{ background: 'rgba(0, 0, 0, 0.5)', color: '#fff' }}>🔍 点击放大</div>
                                  }}
                                />
                                {alt && (
                                  <div style={{ 
                                    marginTop: '8px', 
                                    fontSize: '13px', 
                                    color: '#57606a',
                                    fontStyle: 'italic'
                                  }}>
                                    {alt}
                                  </div>
                                )}
                              </div>
                            )
                          },
                        }}
                      >
                        {caseReadme || '# 暂无文档'}
                      </ReactMarkdown>
                    </div>
                  </TabPane>
                </Tabs>
              </Card>
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '100px 20px',
              color: '#999'
            }}>
              <FolderOutlined style={{ fontSize: '64px', marginBottom: '16px' }} />
              <div style={{ fontSize: '16px' }}>请从左侧选择一个案例</div>
            </div>
          )}
        </Content>
      </Layout>
    </Layout>
  )
}
