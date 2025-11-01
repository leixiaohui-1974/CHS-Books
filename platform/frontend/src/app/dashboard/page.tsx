'use client'

import React, { useState } from 'react'
import { 
  Layout, Card, Typography, Progress, Button, List, 
  Space, Statistic, Row, Col, Tag, Avatar, Empty, Tabs
} from 'antd'
import {
  BookOutlined, TrophyOutlined, ClockCircleOutlined,
  RocketOutlined, StarFilled, CheckCircleOutlined,
  UserOutlined, FireOutlined, CalendarOutlined
} from '@ant-design/icons'
import Link from 'next/link'

const { Content } = Layout
const { Title, Text, Paragraph } = Typography

// Mock用户数据
const mockUserData = {
  user: {
    name: '张同学',
    email: 'student@example.com',
    avatar: null,
    join_date: '2025-09-01',
    level: 5,
    points: 2350,
    next_level_points: 3000
  },
  stats: {
    enrolled_courses: 3,
    completed_courses: 1,
    total_learning_hours: 87,
    current_streak: 7,
    total_cases_completed: 15,
    avg_score: 92
  },
  enrolled_books: [
    {
      id: 1,
      slug: 'water-system-control',
      title: '水系统控制论',
      cover_color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      progress: 45,
      total_chapters: 6,
      completed_chapters: 2,
      last_study: '2025-10-31',
      next_chapter: '第3章：状态空间分析'
    },
    {
      id: 2,
      slug: 'open-channel-hydraulics',
      title: '明渠水力学计算',
      cover_color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      progress: 20,
      total_chapters: 5,
      completed_chapters: 1,
      last_study: '2025-10-29',
      next_chapter: '第2章：能量方程'
    }
  ],
  recent_activities: [
    {
      id: 1,
      type: 'complete',
      title: '完成案例4：PID控制器设计',
      book: '水系统控制论',
      date: '2025-10-31 14:30',
      score: 95
    },
    {
      id: 2,
      type: 'start',
      title: '开始学习第3章',
      book: '水系统控制论',
      date: '2025-10-31 10:00'
    },
    {
      id: 3,
      type: 'achievement',
      title: '获得成就：连续学习7天',
      date: '2025-10-31 08:00'
    }
  ],
  achievements: [
    { id: 1, name: '初学者', description: '完成第一个案例', icon: '🎯', unlocked: true },
    { id: 2, name: '勤奋好学', description: '连续学习7天', icon: '🔥', unlocked: true },
    { id: 3, name: '理论专家', description: '完成一门课程', icon: '🎓', unlocked: true },
    { id: 4, name: '实践大师', description: '运行100次工具', icon: '🛠️', unlocked: false },
    { id: 5, name: '全能选手', description: '完成所有课程', icon: '🏆', unlocked: false }
  ]
}

export default function DashboardPage() {
  const [userData] = useState(mockUserData)

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'complete': return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'start': return <RocketOutlined style={{ color: '#1890ff' }} />
      case 'achievement': return <TrophyOutlined style={{ color: '#faad14' }} />
      default: return <BookOutlined />
    }
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
          <Link href="/dashboard"><Button type="link">我的学习</Button></Link>
          <Avatar icon={<UserOutlined />} />
        </Space>
      </Layout.Header>

      <Content style={{ padding: '50px' }}>
        {/* 用户信息卡片 */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={24} align="middle">
            <Col>
              <Avatar size={80} icon={<UserOutlined />} />
            </Col>
            <Col flex="auto">
              <Space direction="vertical" size="small">
                <Title level={3} style={{ marginBottom: 0 }}>
                  {userData.user.name}
                  <Tag color="blue" style={{ marginLeft: '12px' }}>Lv.{userData.user.level}</Tag>
                </Title>
                <Text type="secondary">{userData.user.email}</Text>
                <Space>
                  <Text type="secondary">
                    <CalendarOutlined /> 加入时间: {userData.user.join_date}
                  </Text>
                  <Text type="secondary">
                    <FireOutlined /> 当前连续学习: {userData.stats.current_streak} 天
                  </Text>
                </Space>
              </Space>
            </Col>
            <Col>
              <Card size="small">
                <Space direction="vertical" align="center">
                  <Text type="secondary">经验值</Text>
                  <Text strong style={{ fontSize: '24px' }}>
                    {userData.user.points} / {userData.user.next_level_points}
                  </Text>
                  <Progress 
                    percent={(userData.user.points / userData.user.next_level_points) * 100} 
                    strokeColor="#1890ff"
                    showInfo={false}
                  />
                </Space>
              </Card>
            </Col>
          </Row>
        </Card>

        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="已注册课程" 
                value={userData.stats.enrolled_courses} 
                prefix={<BookOutlined />}
                suffix="门"
              />
            </Card>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="完成课程" 
                value={userData.stats.completed_courses} 
                prefix={<CheckCircleOutlined />}
                suffix="门"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="学习时长" 
                value={userData.stats.total_learning_hours} 
                prefix={<ClockCircleOutlined />}
                suffix="小时"
              />
            </Card>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="连续学习" 
                value={userData.stats.current_streak} 
                prefix={<FireOutlined />}
                suffix="天"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="完成案例" 
                value={userData.stats.total_cases_completed} 
                prefix={<RocketOutlined />}
                suffix="个"
              />
            </Card>
          </Col>
          <Col xs={12} sm={8} md={4}>
            <Card>
              <Statistic 
                title="平均得分" 
                value={userData.stats.avg_score} 
                prefix={<StarFilled />}
                suffix="分"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={24}>
          {/* 我的课程 */}
          <Col xs={24} lg={12}>
            <Card 
              title="📚 我的课程"
              extra={<Link href="/books">浏览更多</Link>}
              style={{ marginBottom: '24px' }}
            >
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                {userData.enrolled_books.map(book => (
                  <Card key={book.id} size="small" hoverable>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Space>
                        <div style={{
                          width: '60px',
                          height: '60px',
                          background: book.cover_color,
                          borderRadius: '4px'
                        }} />
                        <div style={{ flex: 1 }}>
                          <Link href={`/books/${book.slug}`}>
                            <Text strong>{book.title}</Text>
                          </Link>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            上次学习: {book.last_study}
                          </Text>
                        </div>
                      </Space>
                      
                      <div>
                        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                          <Text type="secondary">
                            进度: {book.completed_chapters}/{book.total_chapters} 章节
                          </Text>
                          <Text strong>{book.progress}%</Text>
                        </Space>
                        <Progress percent={book.progress} strokeColor="#1890ff" />
                      </div>

                      <Button 
                        type="primary" 
                        block
                        icon={<RocketOutlined />}
                      >
                        继续学习：{book.next_chapter}
                      </Button>
                    </Space>
                  </Card>
                ))}
              </Space>
            </Card>
          </Col>

          {/* 右侧栏 */}
          <Col xs={24} lg={12}>
            {/* 最近动态 */}
            <Card 
              title="🕐 最近动态"
              style={{ marginBottom: '24px' }}
            >
              <List
                dataSource={userData.recent_activities}
                renderItem={item => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={getActivityIcon(item.type)}
                      title={item.title}
                      description={
                        <Space size="small">
                          {item.book && <Tag>{item.book}</Tag>}
                          <Text type="secondary">{item.date}</Text>
                          {item.score && <Tag color="green">得分: {item.score}</Tag>}
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>

            {/* 成就系统 */}
            <Card title="🏆 我的成就">
              <Row gutter={[16, 16]}>
                {userData.achievements.map(achievement => (
                  <Col key={achievement.id} span={8}>
                    <Card 
                      size="small"
                      style={{ 
                        textAlign: 'center',
                        opacity: achievement.unlocked ? 1 : 0.4,
                        background: achievement.unlocked ? '#f6ffed' : '#f0f0f0'
                      }}
                    >
                      <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                        {achievement.icon}
                      </div>
                      <Text strong style={{ fontSize: '12px' }}>
                        {achievement.name}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        {achievement.description}
                      </Text>
                      {achievement.unlocked && (
                        <div style={{ marginTop: '4px' }}>
                          <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        </div>
                      )}
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  )
}
