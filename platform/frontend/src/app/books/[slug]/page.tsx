'use client'

import React, { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { 
  Layout, Card, Typography, Tag, Button, Collapse, Progress, 
  Space, Divider, Rate, Statistic, Row, Col, Tabs, Avatar,
  message, Spin, Empty
} from 'antd'
import {
  BookOutlined, PlayCircleOutlined, CheckCircleOutlined,
  ClockCircleOutlined, TrophyOutlined, UserOutlined,
  RocketOutlined, StarFilled, LockOutlined
} from '@ant-design/icons'
import Link from 'next/link'

const { Content } = Layout
const { Title, Paragraph, Text } = Typography
const { Panel } = Collapse

// Mock数据 - 后续会从API获取
const mockBookDetail = {
  id: 1,
  slug: 'water-system-control',
  title: '水系统控制论',
  subtitle: '基于水箱案例的控制理论入门',
  description: '通过24个经典水箱案例系统讲解控制理论基础知识，从最简单的开关控制到高级的模型预测控制，循序渐进地建立完整的控制系统知识体系。本课程特别注重理论与实践结合，每个案例都配有交互式计算工具，让您在实践中深入理解控制理论的精髓。',
  cover_color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  authors: ['张教授', '李工程师'],
  version: '2.0.0',
  difficulty: '初级',
  is_free: false,
  price: 299,
  original_price: 399,
  total_chapters: 6,
  total_cases: 24,
  estimated_hours: 192,
  enrollments: 1523,
  avg_rating: 4.8,
  rating_count: 328,
  tags: ['控制理论', 'PID控制', '水利工程', '自动化'],
  learning_objectives: [
    '掌握经典控制理论的基本概念和方法',
    '理解PID控制器的设计与调优',
    '学会使用状态空间方法分析控制系统',
    '掌握模型预测控制的基本原理',
    '能够独立设计简单的自动控制系统'
  ],
  prerequisites: [
    '高等数学基础',
    '基本的物理知识',
    '简单的编程经验（Python优先）'
  ],
  chapters: [
    {
      id: 1,
      order: 1,
      slug: 'chapter-1',
      title: '第1章：控制系统基础',
      description: '介绍控制系统的基本概念、分类和数学模型',
      is_free: true,
      estimated_minutes: 120,
      completed: false,
      progress: 0,
      cases: [
        {
          id: 1,
          order: 1,
          slug: 'case-1',
          title: '案例1：家庭水塔自动供水',
          subtitle: '开关控制入门',
          difficulty: '初级',
          estimated_minutes: 45,
          has_tool: true,
          is_free: true,
          completed: false,
          key_concepts: ['开关控制', '滞后现象', '系统稳定性']
        },
        {
          id: 2,
          order: 2,
          slug: 'case-2',
          title: '案例2：水箱液位比例控制',
          subtitle: 'P控制原理',
          difficulty: '初级',
          estimated_minutes: 50,
          has_tool: true,
          is_free: true,
          completed: false,
          key_concepts: ['比例控制', '稳态误差', '控制增益']
        }
      ]
    },
    {
      id: 2,
      order: 2,
      slug: 'chapter-2',
      title: '第2章：PID控制器设计',
      description: '深入学习PID控制器的原理、参数整定和工程应用',
      is_free: false,
      estimated_minutes: 180,
      completed: false,
      progress: 0,
      cases: [
        {
          id: 3,
          order: 1,
          slug: 'case-3',
          title: '案例3：PI控制器设计',
          subtitle: '消除稳态误差',
          difficulty: '初级',
          estimated_minutes: 60,
          has_tool: true,
          is_free: false,
          completed: false,
          key_concepts: ['积分控制', '稳态误差', 'PI控制']
        },
        {
          id: 4,
          order: 2,
          slug: 'case-4',
          title: '案例4：PID控制器参数整定',
          subtitle: 'Ziegler-Nichols方法',
          difficulty: '中级',
          estimated_minutes: 70,
          has_tool: true,
          is_free: false,
          completed: false,
          key_concepts: ['PID控制', '参数整定', '系统响应']
        }
      ]
    }
  ],
  instructor: {
    name: '张教授',
    title: '控制理论专家',
    avatar: '/avatars/instructor1.jpg',
    bio: '清华大学自动化系教授，从事控制理论研究20余年，主持多项国家级科研项目。'
  },
  reviews: [
    {
      id: 1,
      user: '学员A',
      rating: 5,
      date: '2025-10-25',
      comment: '非常好的课程！案例丰富，工具实用，学到了很多实际应用的知识。'
    },
    {
      id: 2,
      user: '学员B',
      rating: 5,
      date: '2025-10-20',
      comment: '教学方法很新颖，理论和实践结合得很好，推荐！'
    }
  ]
}

export default function BookDetailPage() {
  const params = useParams()
  const slug = params?.slug as string
  const [book, setBook] = useState(mockBookDetail)
  const [loading, setLoading] = useState(false)
  const [enrolled, setEnrolled] = useState(false)

  useEffect(() => {
    // TODO: 从API加载书籍详情
    // const fetchBookDetail = async () => {
    //   setLoading(true)
    //   try {
    //     const data = await booksAPI.getBook(slug)
    //     setBook(data)
    //   } catch (error) {
    //     message.error('加载失败')
    //   } finally {
    //     setLoading(false)
    //   }
    // }
    // fetchBookDetail()
  }, [slug])

  const handleEnroll = () => {
    // TODO: 调用注册学习API
    message.success('注册学习成功！')
    setEnrolled(true)
  }

  const handleStartLearning = (caseSlug: string) => {
    window.location.href = `/tools/${caseSlug}`
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '初级': return 'green'
      case '中级': return 'blue'
      case '高级': return 'red'
      default: return 'default'
    }
  }

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" />
      </Layout>
    )
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      {/* 顶部导航 */}
      <Layout.Header style={{ 
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
      </Layout.Header>

      <Content style={{ padding: '50px' }}>
        {/* 课程封面和基本信息 */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col xs={24} md={8}>
              <div style={{ 
                height: '300px', 
                background: book.cover_color,
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '28px',
                fontWeight: 'bold',
                textAlign: 'center',
                padding: '20px'
              }}>
                {book.title}
              </div>
            </Col>
            <Col xs={24} md={16}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div>
                  <Title level={2} style={{ marginBottom: '8px' }}>{book.title}</Title>
                  <Text type="secondary" style={{ fontSize: '16px' }}>{book.subtitle}</Text>
                </div>

                <div>
                  <Tag color={getDifficultyColor(book.difficulty)}>{book.difficulty}</Tag>
                  {book.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
                </div>

                <Space split="|" style={{ color: '#666' }}>
                  <span><BookOutlined /> {book.total_cases}个案例</span>
                  <span><ClockCircleOutlined /> {book.estimated_hours}学时</span>
                  <span><UserOutlined /> {book.enrollments}人学习</span>
                </Space>

                <div>
                  <Rate disabled value={book.avg_rating} />
                  <Text strong style={{ marginLeft: '8px' }}>{book.avg_rating}</Text>
                  <Text type="secondary"> ({book.rating_count}条评价)</Text>
                </div>

                <Divider />

                <Row gutter={16}>
                  <Col>
                    <Text delete={book.price !== book.original_price} type="secondary">
                      ¥{book.original_price}
                    </Text>
                  </Col>
                  <Col>
                    <Text strong style={{ fontSize: '28px', color: '#f5222d' }}>
                      ¥{book.price}
                    </Text>
                  </Col>
                </Row>

                {!enrolled ? (
                  <Button 
                    type="primary" 
                    size="large" 
                    icon={<RocketOutlined />}
                    onClick={handleEnroll}
                    style={{ width: '200px' }}
                  >
                    立即学习
                  </Button>
                ) : (
                  <Button 
                    type="primary" 
                    size="large" 
                    icon={<PlayCircleOutlined />}
                    style={{ width: '200px' }}
                  >
                    继续学习
                  </Button>
                )}
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 课程详情选项卡 */}
        <Card>
          <Tabs
            defaultActiveKey="chapters"
            items={[
              {
                key: 'chapters',
                label: '📚 课程章节',
                children: (
                  <Collapse 
                    accordion 
                    defaultActiveKey={['1']}
                    style={{ background: 'transparent', border: 'none' }}
                  >
                    {book.chapters.map((chapter) => (
                      <Panel
                        header={
                          <Space>
                            <Text strong>{chapter.title}</Text>
                            {chapter.is_free && <Tag color="green">免费试学</Tag>}
                            <Text type="secondary">({chapter.estimated_minutes}分钟)</Text>
                          </Space>
                        }
                        key={chapter.id}
                      >
                        <Paragraph type="secondary">{chapter.description}</Paragraph>
                        
                        <div style={{ marginTop: '16px' }}>
                          {chapter.cases.map((case_) => (
                            <Card 
                              key={case_.id}
                              size="small"
                              style={{ marginBottom: '12px' }}
                              hoverable
                            >
                              <Row align="middle" gutter={16}>
                                <Col flex="auto">
                                  <Space direction="vertical" size="small">
                                    <Space>
                                      {case_.completed ? (
                                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                                      ) : (
                                        <PlayCircleOutlined style={{ color: '#1890ff' }} />
                                      )}
                                      <Text strong>{case_.title}</Text>
                                      {case_.is_free && <Tag color="green">免费</Tag>}
                                      {!case_.is_free && !enrolled && <LockOutlined style={{ color: '#999' }} />}
                                    </Space>
                                    <Text type="secondary" style={{ fontSize: '13px' }}>
                                      {case_.subtitle}
                                    </Text>
                                    <Space size="small">
                                      <Tag color={getDifficultyColor(case_.difficulty)} style={{ fontSize: '12px' }}>
                                        {case_.difficulty}
                                      </Tag>
                                      <Text type="secondary" style={{ fontSize: '12px' }}>
                                        <ClockCircleOutlined /> {case_.estimated_minutes}分钟
                                      </Text>
                                      {case_.has_tool && (
                                        <Tag color="blue" style={{ fontSize: '12px' }}>🛠️ 交互工具</Tag>
                                      )}
                                    </Space>
                                    <div style={{ fontSize: '12px', color: '#666' }}>
                                      关键概念: {case_.key_concepts.join(' · ')}
                                    </div>
                                  </Space>
                                </Col>
                                <Col>
                                  {(case_.is_free || enrolled) ? (
                                    <Button 
                                      type="primary"
                                      onClick={() => handleStartLearning(case_.slug)}
                                    >
                                      开始学习
                                    </Button>
                                  ) : (
                                    <Button disabled>
                                      <LockOutlined /> 已锁定
                                    </Button>
                                  )}
                                </Col>
                              </Row>
                            </Card>
                          ))}
                        </div>
                      </Panel>
                    ))}
                  </Collapse>
                )
              },
              {
                key: 'overview',
                label: '📋 课程介绍',
                children: (
                  <div>
                    <Title level={4}>课程简介</Title>
                    <Paragraph>{book.description}</Paragraph>

                    <Divider />

                    <Title level={4}>学习目标</Title>
                    <ul>
                      {book.learning_objectives.map((obj, idx) => (
                        <li key={idx}>
                          <Paragraph>{obj}</Paragraph>
                        </li>
                      ))}
                    </ul>

                    <Divider />

                    <Title level={4}>前置要求</Title>
                    <ul>
                      {book.prerequisites.map((prereq, idx) => (
                        <li key={idx}>
                          <Paragraph>{prereq}</Paragraph>
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              },
              {
                key: 'instructor',
                label: '👨‍🏫 讲师介绍',
                children: (
                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    <Space size="large">
                      <Avatar size={80} icon={<UserOutlined />} />
                      <div>
                        <Title level={4} style={{ marginBottom: '4px' }}>{book.instructor.name}</Title>
                        <Text type="secondary">{book.instructor.title}</Text>
                      </div>
                    </Space>
                    <Paragraph>{book.instructor.bio}</Paragraph>
                  </Space>
                )
              },
              {
                key: 'reviews',
                label: '⭐ 学员评价',
                children: (
                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    {book.reviews.map((review) => (
                      <Card key={review.id} size="small">
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Space>
                            <Avatar icon={<UserOutlined />} />
                            <div>
                              <Text strong>{review.user}</Text>
                              <br />
                              <Text type="secondary" style={{ fontSize: '12px' }}>{review.date}</Text>
                            </div>
                          </Space>
                          <Rate disabled value={review.rating} style={{ fontSize: '14px' }} />
                          <Paragraph>{review.comment}</Paragraph>
                        </Space>
                      </Card>
                    ))}
                  </Space>
                )
              }
            ]}
          />
        </Card>
      </Content>
    </Layout>
  )
}
