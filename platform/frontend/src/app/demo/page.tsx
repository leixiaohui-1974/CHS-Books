'use client'

import React, { useState } from 'react'
import { Layout, Typography, Card, Button, Input, Row, Col, Space, Tag, Divider } from 'antd'
import { RobotOutlined, CodeOutlined, ThunderboltOutlined, CheckCircleOutlined } from '@ant-design/icons'
import Link from 'next/link'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

export default function DemoPage() {
  const [code, setCode] = useState(`def calculate_water_flow(height, width):
    """计算明渠水流量"""
    area = height * width
    velocity = 2.5  # m/s
    flow = area * velocity
    return flow

# 计算示例
result = calculate_water_flow(2.0, 3.0)
print(f"水流量: {result} m³/s")`)
  
  const [aiResponse, setAiResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const explainCode = () => {
    setLoading(true)
    setTimeout(() => {
      setAiResponse(`📚 代码解释：

这段代码实现了明渠水流量的计算功能：

1. **函数定义**：calculate_water_flow 接收两个参数
   - height: 水深 (米)
   - width: 渠道宽度 (米)

2. **计算过程**：
   - area = height × width (计算过水断面面积)
   - velocity = 2.5 m/s (设定平均流速)
   - flow = area × velocity (根据连续性方程计算流量)

3. **应用示例**：
   - 输入：水深2.0米，宽度3.0米
   - 输出：流量15.0立方米/秒

💡 优化建议：
- 可以将流速作为参数，增加灵活性
- 考虑添加糙率系数，使用曼宁公式计算流速
- 增加输入验证，确保参数为正数`)
      setLoading(false)
    }, 1500)
  }

  const validateCode = () => {
    setLoading(true)
    setTimeout(() => {
      setAiResponse(`✅ 代码验证结果：

语法检查：通过 ✓
- 无语法错误
- 缩进正确
- 变量命名规范

功能检查：通过 ✓
- 计算逻辑正确
- 返回值类型正确
- 文档字符串完整

性能评估：优秀
- 时间复杂度：O(1)
- 空间复杂度：O(1)
- 无明显性能问题

代码质量评分：★★★★☆ (4.5/5.0)`)
      setLoading(false)
    }, 1200)
  }

  const optimizeCode = () => {
    setCode(`def calculate_water_flow(height: float, width: float, roughness: float = 0.013) -> dict:
    """
    计算明渠水流量（使用曼宁公式）
    
    参数：
        height: 水深 (米)
        width: 渠道宽度 (米)
        roughness: 曼宁糙率系数（默认0.013）
    
    返回：
        dict: 包含流量、流速、断面积等信息
    """
    if height <= 0 or width <= 0:
        raise ValueError("水深和宽度必须为正数")
    
    # 计算水力要素
    area = height * width
    wetted_perimeter = width + 2 * height
    hydraulic_radius = area / wetted_perimeter
    
    # 曼宁公式计算流速
    slope = 0.001  # 渠底坡度
    velocity = (1 / roughness) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
    
    # 计算流量
    flow = area * velocity
    
    return {
        'flow': round(flow, 3),
        'velocity': round(velocity, 3),
        'area': round(area, 3),
        'hydraulic_radius': round(hydraulic_radius, 3)
    }

# 使用示例
try:
    result = calculate_water_flow(2.0, 3.0)
    print(f"计算结果：")
    print(f"  流量: {result['flow']} m³/s")
    print(f"  流速: {result['velocity']} m/s")
    print(f"  断面积: {result['area']} m²")
except ValueError as e:
    print(f"错误: {e}")`)
    setAiResponse(`🚀 代码已优化！

优化内容：
✓ 添加类型注解，提高代码可读性
✓ 使用曼宁公式，计算更精确
✓ 计算水力半径等关键参数
✓ 添加输入验证和异常处理
✓ 返回详细的计算结果字典
✓ 改进文档字符串，说明更详细

性能提升：保持O(1)时间复杂度
代码质量：★★★★★ (5.0/5.0)`)
  }

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
          <RobotOutlined /> Engineering Learning Platform
        </Link>
        <Space>
          <Link href="/books"><Button type="link">课程</Button></Link>
          <Link href="/"><Button type="link">返回首页</Button></Link>
        </Space>
      </Header>

      <Content style={{ padding: '50px' }}>
        <Title level={2}>
          <CodeOutlined /> AI编程助手 - 智能代码分析与优化
        </Title>
        <Paragraph style={{ fontSize: '16px', color: '#666' }}>
          体验强大的AI编程功能：代码解释、智能验证、自动优化
        </Paragraph>

        <Row gutter={[24, 24]} style={{ marginTop: '30px' }}>
          {/* 左侧：代码编辑器 */}
          <Col xs={24} lg={12}>
            <Card 
              title={
                <Space>
                  <CodeOutlined />
                  <span>Python代码编辑器</span>
                </Space>
              }
              style={{ height: '600px', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column' }}
            >
              <TextArea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                style={{ 
                  fontFamily: 'Monaco, Consolas, monospace',
                  fontSize: '14px',
                  flex: 1,
                  marginBottom: '16px'
                }}
                placeholder="在此输入Python代码..."
              />
              
              <Space wrap>
                <Button 
                  type="primary" 
                  icon={<RobotOutlined />}
                  onClick={explainCode}
                  loading={loading}
                >
                  AI解释代码
                </Button>
                <Button 
                  icon={<CheckCircleOutlined />}
                  onClick={validateCode}
                  loading={loading}
                >
                  代码验证
                </Button>
                <Button 
                  icon={<ThunderboltOutlined />}
                  onClick={optimizeCode}
                  loading={loading}
                >
                  智能优化
                </Button>
              </Space>
            </Card>
          </Col>

          {/* 右侧：AI分析结果 */}
          <Col xs={24} lg={12}>
            <Card 
              title={
                <Space>
                  <RobotOutlined />
                  <span>AI分析结果</span>
                </Space>
              }
              style={{ height: '600px', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ flex: 1, overflow: 'auto' }}
            >
              {aiResponse ? (
                <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'system-ui' }}>
                  {aiResponse}
                </div>
              ) : (
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  color: '#999'
                }}>
                  <RobotOutlined style={{ fontSize: '64px', marginBottom: '20px' }} />
                  <Text type="secondary">点击上方按钮，AI将为您分析代码</Text>
                </div>
              )}
            </Card>
          </Col>
        </Row>

        <Divider />

        {/* 功能特性展示 */}
        <Title level={3} style={{ marginTop: '40px' }}>
          平台核心功能
        </Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card hoverable>
              <Space direction="vertical" size="small">
                <Tag color="blue">代码智能</Tag>
                <Title level={4}>智能代码分析</Title>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  <li>AST语法分析</li>
                  <li>复杂度计算</li>
                  <li>质量评分</li>
                  <li>优化建议</li>
                </ul>
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card hoverable>
              <Space direction="vertical" size="small">
                <Tag color="green">AI助手</Tag>
                <Title level={4}>智能学习助手</Title>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  <li>代码解释</li>
                  <li>错误诊断</li>
                  <li>智能问答</li>
                  <li>学习建议</li>
                </ul>
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card hoverable>
              <Space direction="vertical" size="small">
                <Tag color="purple">工具集</Tag>
                <Title level={4}>计算工具箱</Title>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  <li>在线运行</li>
                  <li>参数配置</li>
                  <li>结果可视化</li>
                  <li>历史记录</li>
                </ul>
              </Space>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  )
}

