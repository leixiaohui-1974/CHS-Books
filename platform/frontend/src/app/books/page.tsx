'use client'

import React, { useState, useEffect } from 'react'
import { Layout, Card, Row, Col, Typography, Tag, Button, Input, Space, Spin, message, Select } from 'antd'
import { BookOutlined, StarFilled, ClockCircleOutlined, UserOutlined } from '@ant-design/icons'
import Link from 'next/link'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography
const { Search } = Input

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
  actual_cases?: number
}

const getCoverColor = (index: number) => {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  ]
  return colors[index % colors.length]
}

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)
  const [searchText, setSearchText] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')

  useEffect(() => {
    loadBooks()
  }, [])

  const loadBooks = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/books')
      const data = await res.json()
      if (data.success) {
        setBooks(data.books || [])
      }
    } catch (error) {
      message.error('加载书籍失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredBooks = books.filter(book => {
    if (selectedLevel !== 'all' && book.level !== selectedLevel) return false
    if (searchText && !book.title.toLowerCase().includes(searchText.toLowerCase())) return false
    return true
  })

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#fff', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        padding: '0 50px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Link href="/" style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff', textDecoration: 'none' }}>
          <BookOutlined /> Engineering Learning Platform
        </Link>
        <Space>
          <Link href="/demo"><Button type="link">AI助手</Button></Link>
          <Link href="/"><Button type="link">首页</Button></Link>
        </Space>
      </Header>

      <Content style={{ padding: '50px' }}>
        <div style={{ marginBottom: '32px' }}>
          <Title level={2}>
            <BookOutlined /> 课程列表
          </Title>
          <Paragraph style={{ fontSize: '16px', color: '#666' }}>
            系统化的工程教材，完整的知识体系，从入门到精通
          </Paragraph>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <Space size="large">
            <Space>
              <strong>难度筛选:</strong>
              <Select 
                value={selectedLevel}
                onChange={setSelectedLevel}
                style={{ width: 120 }}
              >
                <Select.Option value="all">全部</Select.Option>
                <Select.Option value="初级">初级</Select.Option>
                <Select.Option value="中级">中级</Select.Option>
                <Select.Option value="高级">高级</Select.Option>
              </Select>
            </Space>
            <Search
              placeholder="搜索课程名称..."
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
            />
          </Space>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px 0' }}>
            <Spin size="large" />
          </div>
        ) : (
          <Row gutter={[24, 24]}>
            {filteredBooks.map((book, index) => (
              <Col xs={24} md={12} lg={8} key={book.id}>
                <Link href={`/books/${book.slug}`} style={{ textDecoration: 'none' }}>
                  <Card
                    hoverable
                    cover={
                      <div style={{
                        height: '200px',
                        background: getCoverColor(index),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '24px',
                        fontWeight: 'bold'
                      }}>
                        {book.title}
                      </div>
                    }
                  >
                    <Card.Meta
                      title={book.title}
                      description={
                        <div>
                          <Text type="secondary">{book.subtitle}</Text>
                          <Paragraph 
                            ellipsis={{ rows: 2 }} 
                            style={{ marginTop: '8px', marginBottom: '8px' }}
                          >
                            {book.description}
                          </Paragraph>
                        </div>
                      }
                    />
                    
                    <div style={{ marginTop: '12px', marginBottom: '12px' }}>
                      <Space wrap>
                        <Tag color="blue">{book.level}</Tag>
                        {book.tags.slice(0, 3).map(tag => (
                          <Tag key={tag}>{tag}</Tag>
                        ))}
                      </Space>
                    </div>

                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                      <Space direction="vertical" size={0}>
                        <Text type="secondary">
                          <BookOutlined /> {book.actual_cases || book.stats.cases}个案例
                        </Text>
                        <Text type="secondary">
                          <ClockCircleOutlined /> {book.stats.hours}学时
                        </Text>
                      </Space>
                      <Space direction="vertical" size={0}>
                        <Text type="secondary">
                          <UserOutlined /> {book.stats.students}人学习
                        </Text>
                        <Text>
                          <StarFilled style={{ color: '#fadb14' }} /> {book.rating}
                        </Text>
                      </Space>
                    </Space>

                    <div style={{ 
                      marginTop: '16px', 
                      paddingTop: '16px', 
                      borderTop: '1px solid #f0f0f0',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <Text delete style={{ color: '#999' }}>¥{book.price.original}</Text>
                        <Text strong style={{ fontSize: '20px', color: '#f5222d', marginLeft: '8px' }}>
                          ¥{book.price.current}
                        </Text>
                      </div>
                      <Button type="primary">
                        查看详情
                      </Button>
                    </div>
                  </Card>
                </Link>
              </Col>
            ))}
          </Row>
        )}

        {filteredBooks.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '100px 0' }}>
            <Paragraph type="secondary">没有找到匹配的课程</Paragraph>
          </div>
        )}
      </Content>
    </Layout>
  )
}
