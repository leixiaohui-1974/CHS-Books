/**
 * 结果展示仪表板 - V2.0
 * 标准化展示执行结果：图表、表格、指标、报告
 */

'use client'

import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Image,
  Alert,
  Tag,
  Space,
  Button,
  Tabs,
  Empty,
  Spin
} from 'antd'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  DownloadOutlined,
  LineChartOutlined,
  TableOutlined,
  FileTextOutlined,
  BulbOutlined
} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'

const { TabPane } = Tabs

interface ResultDashboardProps {
  executionId: string
}

interface ExecutionResult {
  execution_id: string
  status: string
  execution_time: number
  result_files: Array<{
    type: 'plot' | 'table' | 'data' | 'report'
    title: string
    file_path: string
    metadata?: any
  }>
  console_output: string
  insights?: string[]
  metrics?: Array<{
    name: string
    value: number
    unit: string
    status?: 'normal' | 'warning' | 'error'
  }>
}

export const ResultDashboard: React.FC<ResultDashboardProps> = ({
  executionId
}) => {
  const [loading, setLoading] = useState(true)
  const [result, setResult] = useState<ExecutionResult | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    loadResult()
  }, [executionId])

  /**
   * 加载执行结果
   */
  const loadResult = async () => {
    setLoading(true)
    
    try {
      const response = await fetch(`/api/v1/execution/${executionId}/result`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setResult(data)
      } else {
        setError('加载结果失败')
      }
    } catch (err) {
      setError('网络错误')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  /**
   * 导出结果
   */
  const exportResult = () => {
    // 实现导出功能
    console.log('导出结果:', executionId)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="加载结果中..." />
      </div>
    )
  }

  if (error || !result) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
      />
    )
  }

  // 分类结果
  const plots = result.result_files.filter(f => f.type === 'plot')
  const tables = result.result_files.filter(f => f.type === 'table')
  const reports = result.result_files.filter(f => f.type === 'report')

  return (
    <div className="result-dashboard">
      {/* 顶部状态栏 */}
      <Card>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="执行状态"
              value={result.status === 'completed' ? '成功' : '失败'}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: result.status === 'completed' ? '#3f8600' : '#cf1322' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="执行时间"
              value={result.execution_time}
              suffix="秒"
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="生成文件"
              value={result.result_files.length}
              suffix="个"
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col span={6}>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={exportResult}
              block
            >
              导出报告
            </Button>
          </Col>
        </Row>
      </Card>

      {/* AI智能洞察 */}
      {result.insights && result.insights.length > 0 && (
        <Card
          title={
            <Space>
              <BulbOutlined />
              <span>AI智能洞察</span>
            </Space>
          }
          style={{ marginTop: '16px' }}
        >
          {result.insights.map((insight, index) => (
            <Alert
              key={index}
              message={insight}
              type="info"
              showIcon
              style={{ marginBottom: '8px' }}
            />
          ))}
        </Card>
      )}

      {/* 关键指标 */}
      {result.metrics && result.metrics.length > 0 && (
        <Card
          title={
            <Space>
              <ThunderboltOutlined />
              <span>关键指标</span>
            </Space>
          }
          style={{ marginTop: '16px' }}
        >
          <Row gutter={[16, 16]}>
            {result.metrics.map((metric, index) => (
              <Col span={6} key={index}>
                <Card size="small">
                  <Statistic
                    title={metric.name}
                    value={metric.value}
                    suffix={metric.unit}
                    valueStyle={{
                      color: metric.status === 'normal' ? '#3f8600' :
                             metric.status === 'warning' ? '#faad14' : '#cf1322'
                    }}
                  />
                  {metric.status && (
                    <Tag 
                      color={
                        metric.status === 'normal' ? 'success' :
                        metric.status === 'warning' ? 'warning' : 'error'
                      }
                      style={{ marginTop: '8px' }}
                    >
                      {metric.status === 'normal' ? '正常' :
                       metric.status === 'warning' ? '警告' : '异常'}
                    </Tag>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 主要结果展示 */}
      <Card style={{ marginTop: '16px' }}>
        <Tabs defaultActiveKey="plots">
          {/* 图表标签页 */}
          {plots.length > 0 && (
            <TabPane
              tab={
                <span>
                  <LineChartOutlined />
                  图表 ({plots.length})
                </span>
              }
              key="plots"
            >
              <Row gutter={[16, 16]}>
                {plots.map((plot, index) => (
                  <Col span={12} key={index}>
                    <Card
                      title={plot.title}
                      size="small"
                      extra={
                        <Button
                          size="small"
                          icon={<DownloadOutlined />}
                          onClick={() => {
                            // 下载图片
                            window.open(plot.file_path, '_blank')
                          }}
                        >
                          下载
                        </Button>
                      }
                    >
                      <Image
                        src={plot.file_path}
                        alt={plot.title}
                        style={{ width: '100%' }}
                      />
                      {plot.metadata?.description && (
                        <p style={{ marginTop: '8px', color: '#666' }}>
                          {plot.metadata.description}
                        </p>
                      )}
                    </Card>
                  </Col>
                ))}
              </Row>
            </TabPane>
          )}

          {/* 数据表格标签页 */}
          {tables.length > 0 && (
            <TabPane
              tab={
                <span>
                  <TableOutlined />
                  数据表 ({tables.length})
                </span>
              }
              key="tables"
            >
              {tables.map((table, index) => (
                <Card
                  key={index}
                  title={table.title}
                  size="small"
                  style={{ marginBottom: '16px' }}
                  extra={
                    <Button
                      size="small"
                      icon={<DownloadOutlined />}
                    >
                      导出CSV
                    </Button>
                  }
                >
                  <Table
                    dataSource={table.metadata?.preview || []}
                    columns={(table.metadata?.columns || []).map((col: string) => ({
                      title: col,
                      dataIndex: col,
                      key: col
                    }))}
                    pagination={{ pageSize: 10 }}
                    size="small"
                  />
                  {table.metadata?.statistics && (
                    <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                      共 {table.metadata.row_count} 行 × {table.metadata.col_count} 列
                    </div>
                  )}
                </Card>
              ))}
            </TabPane>
          )}

          {/* 报告标签页 */}
          {reports.length > 0 && (
            <TabPane
              tab={
                <span>
                  <FileTextOutlined />
                  报告 ({reports.length})
                </span>
              }
              key="reports"
            >
              {reports.map((report, index) => (
                <Card key={index} title={report.title} size="small" style={{ marginBottom: '16px' }}>
                  <div style={{ padding: '10px' }}>
                    {/* 假设报告内容是Markdown */}
                    <ReactMarkdown>
                      {report.metadata?.content || '报告内容'}
                    </ReactMarkdown>
                  </div>
                </Card>
              ))}
            </TabPane>
          )}

          {/* 控制台输出 */}
          <TabPane
            tab={
              <span>
                <FileTextOutlined />
                控制台输出
              </span>
            }
            key="console"
          >
            <pre
              style={{
                backgroundColor: '#1e1e1e',
                color: '#d4d4d4',
                padding: '16px',
                borderRadius: '4px',
                maxHeight: '500px',
                overflow: 'auto',
                fontFamily: 'Monaco, Consolas, monospace',
                fontSize: '12px'
              }}
            >
              {result.console_output}
            </pre>
          </TabPane>
        </Tabs>
      </Card>

      {/* 无结果提示 */}
      {plots.length === 0 && tables.length === 0 && reports.length === 0 && (
        <Empty
          description="暂无结果文件"
          style={{ marginTop: '32px' }}
        />
      )}
    </div>
  )
}

export default ResultDashboard
