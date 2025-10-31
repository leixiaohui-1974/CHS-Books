'use client'

import React from 'react'
import { Layout, Typography, Button, Card, Row, Col, Statistic } from 'antd'
import { RocketOutlined, BookOutlined, ToolOutlined, RobotOutlined } from '@ant-design/icons'
import Link from 'next/link'

const { Header, Content, Footer } = Layout
const { Title, Paragraph } = Typography

export default function HomePage() {
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
        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1890ff' }}>
          <RocketOutlined /> Engineering Learning Platform
        </div>
        <div>
          <Button type="link" href="/books">课程</Button>
          <Button type="link" href="/tools">工具实验室</Button>
          <Button type="link" href="/docs">文档</Button>
          <Button type="primary" style={{ marginLeft: 16 }} href="/login">登录</Button>
        </div>
      </Header>

      {/* 主要内容 */}
      <Content style={{ padding: '50px' }}>
        {/* Hero Section */}
        <div style={{ 
          textAlign: 'center', 
          padding: '80px 0',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: '8px',
          marginBottom: '50px'
        }}>
          <Title style={{ color: 'white', fontSize: '48px', marginBottom: '24px' }}>
            智能工程教学平台
          </Title>
          <Paragraph style={{ color: 'white', fontSize: '20px', marginBottom: '32px' }}>
            教材 + 工具 + AI助手 = 高效掌握工程知识
          </Paragraph>
          <Link href="/books">
            <Button type="primary" size="large" style={{ marginRight: '16px' }}>
              开始学习
            </Button>
          </Link>
          <Link href="/docs/quick-start">
            <Button size="large" ghost>
              查看文档
            </Button>
          </Link>
        </div>

        {/* 特性介绍 */}
        <Row gutter={[24, 24]} style={{ marginBottom: '50px' }}>
          <Col xs={24} md={8}>
            <Card 
              hoverable
              style={{ height: '100%', textAlign: 'center' }}
            >
              <BookOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
              <Title level={3}>系统化教材</Title>
              <Paragraph>
                完整的知识体系，从入门到精通
              </Paragraph>
              <ul style={{ textAlign: 'left', paddingLeft: '24px' }}>
                <li>3本专业教材</li>
                <li>74个教学案例</li>
                <li>640学时课程</li>
                <li>渐进式学习路径</li>
              </ul>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card 
              hoverable
              style={{ height: '100%', textAlign: 'center' }}
            >
              <ToolOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
              <Title level={3}>交互式工具</Title>
              <Paragraph>
                每个案例都有可运行的计算工具
              </Paragraph>
              <ul style={{ textAlign: 'left', paddingLeft: '24px' }}>
                <li>参数可配置</li>
                <li>实时可视化</li>
                <li>结果可导出</li>
                <li>历史记录</li>
              </ul>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card 
              hoverable
              style={{ height: '100%', textAlign: 'center' }}
            >
              <RobotOutlined style={{ fontSize: '48px', color: '#722ed1', marginBottom: '16px' }} />
              <Title level={3}>AI学习助手</Title>
              <Paragraph>
                基于RAG的智能问答和学习规划
              </Paragraph>
              <ul style={{ textAlign: 'left', paddingLeft: '24px' }}>
                <li>智能问答</li>
                <li>代码解释</li>
                <li>参数建议</li>
                <li>学习规划</li>
              </ul>
            </Card>
          </Col>
        </Row>

        {/* 统计数据 */}
        <Card style={{ marginBottom: '50px' }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic title="注册用户" value={1523} suffix="人" />
            </Col>
            <Col span={6}>
              <Statistic title="教材数量" value={3} suffix="本" />
            </Col>
            <Col span={6}>
              <Statistic title="教学案例" value={74} suffix="个" />
            </Col>
            <Col span={6}>
              <Statistic title="平均评分" value={4.8} precision={1} suffix="/ 5.0" />
            </Col>
          </Row>
        </Card>

        {/* 教材列表 */}
        <Title level={2} style={{ marginBottom: '24px' }}>热门课程</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={
                <div style={{ 
                  height: '200px', 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '24px',
                  fontWeight: 'bold'
                }}>
                  水系统控制论
                </div>
              }
            >
              <Card.Meta
                title="水系统控制论"
                description="基于水箱案例的控制理论入门"
              />
              <Paragraph style={{ marginTop: '16px' }}>
                24个案例 · 192学时 · 初级
              </Paragraph>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '20px', color: '#f5222d', fontWeight: 'bold' }}>
                  ¥299
                </span>
                <Button type="primary">开始学习</Button>
              </div>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={
                <div style={{ 
                  height: '200px', 
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '24px',
                  fontWeight: 'bold'
                }}>
                  明渠水力学
                </div>
              }
            >
              <Card.Meta
                title="明渠水力学计算"
                description="基于工程案例的水力计算入门"
              />
              <Paragraph style={{ marginTop: '16px' }}>
                30个案例 · 288学时 · 中级
              </Paragraph>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '20px', color: '#f5222d', fontWeight: 'bold' }}>
                  ¥399
                </span>
                <Button type="primary">开始学习</Button>
              </div>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card
              hoverable
              cover={
                <div style={{ 
                  height: '200px', 
                  background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '24px',
                  fontWeight: 'bold'
                }}>
                  运河管道控制
                </div>
              }
            >
              <Card.Meta
                title="运河与管道控制"
                description="闸泵联合调度与智能控制"
              />
              <Paragraph style={{ marginTop: '16px' }}>
                20个案例 · 160学时 · 高级
              </Paragraph>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '20px', color: '#f5222d', fontWeight: 'bold' }}>
                  ¥299
                </span>
                <Button type="primary">开始学习</Button>
              </div>
            </Card>
          </Col>
        </Row>
      </Content>

      {/* 底部 */}
      <Footer style={{ textAlign: 'center', background: '#001529', color: 'white' }}>
        <Paragraph style={{ color: 'rgba(255,255,255,0.65)' }}>
          Engineering Learning Platform ©2025 Created by AI Engineering Team
        </Paragraph>
        <Paragraph style={{ color: 'rgba(255,255,255,0.45)' }}>
          让工程教育更智能，让学习更高效
        </Paragraph>
      </Footer>
    </Layout>
  )
}
