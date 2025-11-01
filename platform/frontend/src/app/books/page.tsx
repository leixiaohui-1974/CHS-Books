'use client'

import React, { useState } from 'react'
import { Layout, Card, Row, Col, Typography, Tag, Button, Select, Input, Pagination, Space, Statistic } from 'antd'
import { BookOutlined, ClockCircleOutlined, StarFilled, UserOutlined } from '@ant-design/icons'
import Link from 'next/link'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography
const { Search } = Input

// Mock数据
const mockBooks = [
  {
    id: 1,
    slug: 'water-system-control',
    title: '水系统控制论',
    subtitle: '基于水箱案例的控制理论入门',
    description: '通过24个经典水箱案例系统讲解控制理论基础知识，从最简单的开关控制到高级的模型预测控制，循序渐进地建立完整的控制系统知识体系。',
    difficulty: '初级',
    total_cases: 24,
    estimated_hours: 192,
    enrollments: 1523,
    avg_rating: 4.8,
    price: 299,
    original_price: 399,
    tags: ['控制理论', '水利工程', 'PID控制'],
    cover_color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    id: 2,
    slug: 'open-channel-hydraulics',
    title: '明渠水力学计算',
    subtitle: '基于工程案例的水力计算入门',
    description: '通过30个经典水力工程案例系统讲解完整的水力学计算方法，从明渠流到有压流，从恒定流到非恒定流，涵盖完整的水力学知识体系。',
    difficulty: '中级',
    total_cases: 30,
    estimated_hours: 288,
    enrollments: 856,
    avg_rating: 4.7,
    price: 399,
    original_price: 499,
    tags: ['水力学', '明渠流', '非恒定流'],
    cover_color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    id: 3,
    slug: 'canal-pipeline-control',
    title: '运河与管道控制',
    subtitle: '闸泵联合调度与智能控制',
    description: '结合明渠水力学和控制理论，讲解运河系统的智能控制方法，包括闸门控制、泵站调度、多目标优化等实际工程应用。',
    difficulty: '高级',
    total_cases: 20,
    estimated_hours: 160,
    enrollments: 423,
    avg_rating: 4.9,
    price: 299,
    original_price: 299,
    tags: ['智能控制', '调度优化', '实时控制'],
    cover_color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  }
]

export default function BooksPage() {
  const [difficulty, setDifficulty] = useState<string>('all')
  const [searchText, setSearchText] = useState<string>('')
  const [currentPage, setCurrentPage] = useState<number>(1)
  const pageSize = 6

  // 筛选逻辑
  const filteredBooks = mockBooks.filter(book => {
    if (difficulty !== 'all' && book.difficulty !== difficulty) return false
    if (searchText && !book.title.toLowerCase().includes(searchText.toLowerCase())) return false
    return true
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '初级': return 'green'
      case '中级': return 'blue'
      case '高级': return 'red'
      default: return 'default'
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航 */}
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
          <Link href="/books"><Button type="link">课程</Button></Link>
          <Link href="/tools"><Button type="link">工具实验室</Button></Link>
          <Link href="/login"><Button type="primary">登录</Button></Link>
        </Space>
      </Header>

      <Content style={{ padding: '50px' }}>
        {/* 页面标题 */}
        <div style={{ marginBottom: '40px' }}>
          <Title level={2}>
            <BookOutlined /> 课程列表
          </Title>
          <Paragraph type="secondary">
            系统化的工程教材，完整的知识体系，从入门到精通
          </Paragraph>
        </div>

        {/* 筛选和搜索 */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={16} align="middle">
            <Col xs={24} sm={8} md={6}>
              <Space>
                <Text strong>难度筛选:</Text>
                <Select
                  value={difficulty}
                  onChange={setDifficulty}
                  style={{ width: 120 }}
                >
                  <Select.Option value="all">全部</Select.Option>
                  <Select.Option value="初级">初级</Select.Option>
                  <Select.Option value="中级">中级</Select.Option>
                  <Select.Option value="高级">高级</Select.Option>
                </Select>
              </Space>
            </Col>
            <Col xs={24} sm={16} md={12}>
              <Search
                placeholder="搜索课程名称..."
                allowClear
                onSearch={setSearchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: '100%' }}
              />
            </Col>
          </Row>
        </Card>

        {/* 统计信息 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic title="课程总数" value={filteredBooks.length} suffix="门" />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="教学案例" value={74} suffix="个" />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="学习用户" value={2802} suffix="人" />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="平均评分" value={4.8} precision={1} suffix="/ 5.0" />
            </Card>
          </Col>
        </Row>

        {/* 书籍卡片列表 */}
        <Row gutter={[24, 24]}>
          {filteredBooks.map((book) => (
            <Col xs={24} sm={12} lg={8} key={book.id}>
              <Card
                hoverable
                style={{ height: '100%' }}
                cover={
                  <div style={{ 
                    height: '200px', 
                    background: book.cover_color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '24px',
                    fontWeight: 'bold',
                    padding: '20px',
                    textAlign: 'center'
                  }}>
                    {book.title}
                  </div>
                }
              >
                <Card.Meta
                  title={
                    <Link href={`/books/${book.slug}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                      {book.title}
                    </Link>
                  }
                  description={
                    <div>
                      <Paragraph ellipsis={{ rows: 2 }} type="secondary">
                        {book.subtitle}
                      </Paragraph>
                      <Paragraph ellipsis={{ rows: 3 }} style={{ fontSize: '13px' }}>
                        {book.description}
                      </Paragraph>
                    </div>
                  }
                />
                
                {/* 标签 */}
                <div style={{ marginTop: '12px', marginBottom: '12px' }}>
                  <Tag color={getDifficultyColor(book.difficulty)}>{book.difficulty}</Tag>
                  {book.tags.slice(0, 2).map(tag => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </div>

                {/* 统计信息 */}
                <Space split="|" style={{ marginBottom: '16px', fontSize: '13px', color: '#666' }}>
                  <span><BookOutlined /> {book.total_cases}个案例</span>
                  <span><ClockCircleOutlined /> {book.estimated_hours}学时</span>
                  <span><UserOutlined /> {book.enrollments}人学习</span>
                </Space>

                {/* 评分 */}
                <div style={{ marginBottom: '16px' }}>
                  <StarFilled style={{ color: '#faad14', marginRight: '4px' }} />
                  <Text strong>{book.avg_rating}</Text>
                  <Text type="secondary"> / 5.0</Text>
                </div>

                {/* 价格和按钮 */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text delete={book.price !== book.original_price} type="secondary" style={{ marginRight: '8px' }}>
                      ¥{book.original_price}
                    </Text>
                    <Text strong style={{ fontSize: '20px', color: '#f5222d' }}>
                      ¥{book.price}
                    </Text>
                  </div>
                  <Link href={`/books/${book.slug}`}>
                    <Button type="primary">查看详情</Button>
                  </Link>
                </div>
              </Card>
            </Col>
          ))}
        </Row>

        {/* 分页 */}
        {filteredBooks.length > pageSize && (
          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <Pagination
              current={currentPage}
              pageSize={pageSize}
              total={filteredBooks.length}
              onChange={setCurrentPage}
              showSizeChanger={false}
            />
          </div>
        )}
      </Content>
    </Layout>
  )
}
