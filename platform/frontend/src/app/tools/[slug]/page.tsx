'use client'

import React, { useState } from 'react'
import { useParams } from 'next/navigation'
import { 
  Layout, Card, Typography, Button, Form, Input, InputNumber,
  Select, Space, Divider, Alert, Tabs, message, Spin
} from 'antd'
import {
  PlayCircleOutlined, DownloadOutlined, SaveOutlined,
  CodeOutlined, LineChartOutlined, SettingOutlined,
  BookOutlined
} from '@ant-design/icons'
import Link from 'next/link'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title as ChartTitle,
  Tooltip,
  Legend
} from 'chart.js'

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ChartTitle,
  Tooltip,
  Legend
)

const { Content } = Layout
const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

// Mock工具配置
const mockToolConfig = {
  case_id: 1,
  slug: 'case-1',
  title: '案例1：家庭水塔自动供水',
  subtitle: '开关控制入门',
  description: '通过模拟家庭水塔的自动供水系统，理解开关控制的基本原理。本工具允许您调整水塔参数和控制策略，观察系统的动态响应。',
  key_concepts: ['开关控制', '滞后现象', '系统稳定性'],
  parameters: [
    {
      name: 'tank_capacity',
      label: '水塔容量',
      type: 'number',
      unit: 'm³',
      default: 10,
      min: 5,
      max: 50,
      step: 1,
      description: '水塔的总容量，影响系统的调节特性'
    },
    {
      name: 'inflow_rate',
      label: '进水流量',
      type: 'number',
      unit: 'm³/h',
      default: 5,
      min: 1,
      max: 20,
      step: 0.5,
      description: '水泵的额定进水流量'
    },
    {
      name: 'outflow_rate',
      label: '用水流量',
      type: 'number',
      unit: 'm³/h',
      default: 3,
      min: 0.5,
      max: 15,
      step: 0.5,
      description: '用户的平均用水流量'
    },
    {
      name: 'high_level',
      label: '高水位阈值',
      type: 'number',
      unit: '%',
      default: 80,
      min: 50,
      max: 95,
      step: 5,
      description: '触发关闭水泵的水位百分比'
    },
    {
      name: 'low_level',
      label: '低水位阈值',
      type: 'number',
      unit: '%',
      default: 30,
      min: 10,
      max: 50,
      step: 5,
      description: '触发开启水泵的水位百分比'
    },
    {
      name: 'simulation_time',
      label: '仿真时长',
      type: 'number',
      unit: '小时',
      default: 24,
      min: 1,
      max: 168,
      step: 1,
      description: '仿真的总时长'
    }
  ]
}

export default function ToolPage() {
  const params = useParams()
  const slug = params?.slug as string
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [activeTab, setActiveTab] = useState('params')

  const handleExecute = async (values: any) => {
    setLoading(true)
    try {
      // TODO: 调用工具执行API
      // const result = await toolsAPI.executeTool(mockToolConfig.case_id, values)
      
      // Mock结果
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockResult = {
        status: 'success',
        execution_time: 1.23,
        output: {
          summary: {
            avg_water_level: 55.3,
            pump_on_time: 12.5,
            pump_cycles: 15,
            efficiency: 92.5
          },
          time_series: {
            time: Array.from({ length: 24 }, (_, i) => i),
            water_level: Array.from({ length: 24 }, () => Math.random() * 40 + 30),
            pump_state: Array.from({ length: 24 }, () => Math.random() > 0.5 ? 1 : 0)
          }
        },
        charts: [
          {
            title: '水位变化曲线',
            data: {
              labels: Array.from({ length: 24 }, (_, i) => `${i}h`),
              datasets: [
                {
                  label: '水位 (%)',
                  data: Array.from({ length: 24 }, () => Math.random() * 40 + 30),
                  borderColor: 'rgb(75, 192, 192)',
                  backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }
              ]
            }
          }
        ]
      }
      
      setResult(mockResult)
      setActiveTab('result')
      message.success('执行成功！')
    } catch (error) {
      message.error('执行失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveResult = () => {
    message.success('结果已保存到学习记录')
  }

  const handleDownloadResult = () => {
    message.success('结果已下载')
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
        {/* 工具标题 */}
        <Card style={{ marginBottom: '24px' }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Title level={3} style={{ marginBottom: '8px' }}>
              <CodeOutlined /> {mockToolConfig.title}
            </Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>
              {mockToolConfig.subtitle}
            </Text>
            <Paragraph>{mockToolConfig.description}</Paragraph>
            <Space>
              <Text strong>关键概念:</Text>
              {mockToolConfig.key_concepts.map(concept => (
                <Text key={concept} code>{concept}</Text>
              ))}
            </Space>
          </Space>
        </Card>

        {/* 主要内容 */}
        <Card>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'params',
                label: <span><SettingOutlined /> 参数设置</span>,
                children: (
                  <div>
                    <Alert
                      message="参数说明"
                      description="调整下方参数，然后点击"运行仿真"按钮执行计算。合理的参数设置能够帮助您更好地理解控制系统的行为。"
                      type="info"
                      showIcon
                      style={{ marginBottom: '24px' }}
                    />

                    <Form
                      form={form}
                      layout="vertical"
                      onFinish={handleExecute}
                      initialValues={mockToolConfig.parameters.reduce((acc, param) => {
                        acc[param.name] = param.default
                        return acc
                      }, {} as any)}
                    >
                      {mockToolConfig.parameters.map(param => (
                        <Form.Item
                          key={param.name}
                          name={param.name}
                          label={`${param.label} (${param.unit})`}
                          extra={param.description}
                          rules={[{ required: true, message: `请输入${param.label}` }]}
                        >
                          <InputNumber
                            min={param.min}
                            max={param.max}
                            step={param.step}
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      ))}

                      <Divider />

                      <Space>
                        <Button 
                          type="primary" 
                          htmlType="submit" 
                          icon={<PlayCircleOutlined />}
                          loading={loading}
                          size="large"
                        >
                          运行仿真
                        </Button>
                        <Button onClick={() => form.resetFields()}>
                          重置参数
                        </Button>
                      </Space>
                    </Form>
                  </div>
                )
              },
              {
                key: 'result',
                label: <span><LineChartOutlined /> 结果展示</span>,
                disabled: !result,
                children: result && (
                  <div>
                    <Space style={{ marginBottom: '24px' }}>
                      <Button 
                        type="primary" 
                        icon={<SaveOutlined />}
                        onClick={handleSaveResult}
                      >
                        保存结果
                      </Button>
                      <Button 
                        icon={<DownloadOutlined />}
                        onClick={handleDownloadResult}
                      >
                        下载报告
                      </Button>
                    </Space>

                    {/* 关键指标 */}
                    <Card title="关键指标" style={{ marginBottom: '24px' }}>
                      <Space size="large" wrap>
                        <div>
                          <Text type="secondary">平均水位</Text>
                          <br />
                          <Text strong style={{ fontSize: '24px', color: '#1890ff' }}>
                            {result.output.summary.avg_water_level.toFixed(1)}%
                          </Text>
                        </div>
                        <Divider type="vertical" style={{ height: '60px' }} />
                        <div>
                          <Text type="secondary">泵开启时间</Text>
                          <br />
                          <Text strong style={{ fontSize: '24px', color: '#52c41a' }}>
                            {result.output.summary.pump_on_time.toFixed(1)}h
                          </Text>
                        </div>
                        <Divider type="vertical" style={{ height: '60px' }} />
                        <div>
                          <Text type="secondary">开关循环次数</Text>
                          <br />
                          <Text strong style={{ fontSize: '24px', color: '#faad14' }}>
                            {result.output.summary.pump_cycles}次
                          </Text>
                        </div>
                        <Divider type="vertical" style={{ height: '60px' }} />
                        <div>
                          <Text type="secondary">系统效率</Text>
                          <br />
                          <Text strong style={{ fontSize: '24px', color: '#722ed1' }}>
                            {result.output.summary.efficiency.toFixed(1)}%
                          </Text>
                        </div>
                      </Space>
                    </Card>

                    {/* 图表展示 */}
                    {result.charts.map((chart: any, idx: number) => (
                      <Card key={idx} title={chart.title} style={{ marginBottom: '24px' }}>
                        <Line 
                          data={chart.data}
                          options={{
                            responsive: true,
                            plugins: {
                              legend: {
                                position: 'top' as const,
                              },
                            },
                          }}
                        />
                      </Card>
                    ))}

                    {/* 执行信息 */}
                    <Alert
                      message="执行完成"
                      description={`仿真成功完成，耗时 ${result.execution_time} 秒`}
                      type="success"
                      showIcon
                    />
                  </div>
                )
              }
            ]}
          />
        </Card>
      </Content>
    </Layout>
  )
}
