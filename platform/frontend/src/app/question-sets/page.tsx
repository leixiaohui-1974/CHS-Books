'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card, Button, Empty, Spin, Tag, Space, Row, Col, Statistic, Modal, Form,
  Input, Select, message, Divider
} from 'ant-d';
import {
  BookOutlined, FireOutlined, TrophyOutlined, ClockCircleOutlined,
  PlusOutlined, CheckCircleOutlined, StarOutlined
} from '@ant-design/icons';
import { questionService, QuestionSet } from '@/services/questionService';
import { useAuth } from '@/contexts/AuthContext';
import './question-sets.css';

const { TextArea } = Input;

export default function QuestionSetsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [loading, setLoading] = useState(true);
  const [questionSets, setQuestionSets] = useState<QuestionSet[]>([]);
  const [filteredSets, setFilteredSets] = useState<QuestionSet[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/question-sets');
      return;
    }

    if (user) {
      loadQuestionSets();
    }
  }, [user, authLoading]);

  useEffect(() => {
    filterSets();
  }, [selectedType, questionSets]);

  const loadQuestionSets = async () => {
    try {
      setLoading(true);
      const { question_sets } = await questionService.getQuestionSets({ limit: 100 });
      setQuestionSets(question_sets);
    } catch (error: any) {
      console.error('Failed to load question sets:', error);
      message.error('加载题集失败');
    } finally {
      setLoading(false);
    }
  };

  const filterSets = () => {
    if (selectedType === 'all') {
      setFilteredSets(questionSets);
    } else {
      setFilteredSets(questionSets.filter((set) => set.set_type === selectedType));
    }
  };

  const handleCreateSet = async (values: any) => {
    try {
      // 这里简化处理，实际应用中需要一个选择题目的界面
      await questionService.createQuestionSet({
        title: values.title,
        description: values.description,
        set_type: values.set_type,
        question_ids: [], // 需要从其他界面选择
        pass_score: values.pass_score,
        time_limit: values.time_limit,
      });

      message.success('题集创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      loadQuestionSets();
    } catch (error: any) {
      console.error('Failed to create question set:', error);
      message.error('创建题集失败');
    }
  };

  const handleStartPractice = (setId: number) => {
    router.push(`/practice?set_id=${setId}`);
  };

  const getSetTypeText = (type: string): string => {
    const texts: Record<string, string> = {
      practice: '日常练习',
      quiz: '小测验',
      exam: '模拟考试',
      chapter: '章节测试',
      final: '期末考试',
    };
    return texts[type] || type;
  };

  const getSetTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      practice: 'blue',
      quiz: 'cyan',
      exam: 'red',
      chapter: 'orange',
      final: 'purple',
    };
    return colors[type] || 'default';
  };

  const renderQuestionSetCard = (set: QuestionSet) => {
    const passRate = set.attempt_count > 0 && set.total_score > 0
      ? (set.average_score / set.total_score) * 100
      : 0;

    return (
      <Card
        key={set.id}
        className="question-set-card"
        hoverable
        actions={[
          <Button
            type="primary"
            icon={<FireOutlined />}
            onClick={() => handleStartPractice(set.id)}
            key="start"
          >
            开始练习
          </Button>,
          <Button icon={<BookOutlined />} onClick={() => {}} key="detail">
            查看详情
          </Button>,
        ]}
      >
        <div className="card-header">
          <Tag color={getSetTypeColor(set.set_type)} className="type-tag">
            {getSetTypeText(set.set_type)}
          </Tag>
          {passRate >= 60 && set.attempt_count > 0 && (
            <Tag color="success" icon={<CheckCircleOutlined />}>
              已通过
            </Tag>
          )}
        </div>

        <div className="card-title">{set.title}</div>

        {set.description && (
          <div className="card-description">{set.description}</div>
        )}

        <Divider style={{ margin: '16px 0' }} />

        <Row gutter={16} className="card-stats">
          <Col span={12}>
            <Statistic
              title="题目数"
              value={set.total_questions}
              prefix={<BookOutlined />}
              valueStyle={{ fontSize: 20 }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="总分"
              value={set.total_score}
              prefix={<TrophyOutlined />}
              valueStyle={{ fontSize: 20, color: '#1890ff' }}
            />
          </Col>
        </Row>

        <Row gutter={16} className="card-stats">
          <Col span={12}>
            <Statistic
              title="及格分"
              value={set.pass_score}
              valueStyle={{ fontSize: 18, color: '#faad14' }}
            />
          </Col>
          <Col span={12}>
            {set.time_limit ? (
              <Statistic
                title="时限"
                value={set.time_limit}
                suffix="分钟"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ fontSize: 18, color: '#f5222d' }}
              />
            ) : (
              <div style={{ textAlign: 'center', paddingTop: 8 }}>
                <div style={{ fontSize: 12, color: '#8c8c8c' }}>时限</div>
                <div style={{ fontSize: 18, marginTop: 4 }}>不限时</div>
              </div>
            )}
          </Col>
        </Row>

        {set.attempt_count > 0 && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <div className="card-performance">
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <div className="performance-item">
                  <span className="performance-label">练习次数:</span>
                  <span className="performance-value">{set.attempt_count} 次</span>
                </div>
                <div className="performance-item">
                  <span className="performance-label">平均得分:</span>
                  <span className="performance-value" style={{ color: '#1890ff' }}>
                    {set.average_score.toFixed(1)} 分
                  </span>
                </div>
                <div className="performance-item">
                  <span className="performance-label">通过率:</span>
                  <span
                    className="performance-value"
                    style={{ color: passRate >= 60 ? '#52c41a' : '#f5222d' }}
                  >
                    {passRate.toFixed(1)}%
                  </span>
                </div>
              </Space>
            </div>
          </>
        )}
      </Card>
    );
  };

  if (authLoading || loading) {
    return (
      <div className="question-sets-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="question-sets-container">
      {/* 头部 */}
      <Card className="header-card">
        <div className="header-content">
          <div className="header-left">
            <h1 className="page-title">
              <BookOutlined style={{ marginRight: 12 }} />
              题集练习
            </h1>
            <p className="page-description">精选题集，系统练习，快速提升</p>
          </div>
          <div className="header-right">
            <Button
              type="primary"
              size="large"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              创建题集
            </Button>
          </div>
        </div>

        {/* 筛选器 */}
        <div className="filter-bar">
          <Space size="middle">
            <span>题集类型:</span>
            <Select
              value={selectedType}
              onChange={setSelectedType}
              style={{ width: 150 }}
            >
              <Select.Option value="all">全部</Select.Option>
              <Select.Option value="practice">日常练习</Select.Option>
              <Select.Option value="quiz">小测验</Select.Option>
              <Select.Option value="chapter">章节测试</Select.Option>
              <Select.Option value="exam">模拟考试</Select.Option>
              <Select.Option value="final">期末考试</Select.Option>
            </Select>
          </Space>
        </div>
      </Card>

      {/* 题集列表 */}
      <div className="sets-grid">
        {filteredSets.length > 0 ? (
          filteredSets.map((set) => renderQuestionSetCard(set))
        ) : (
          <Empty description="暂无题集" style={{ gridColumn: '1 / -1', padding: '60px 0' }} />
        )}
      </div>

      {/* 创建题集弹窗 */}
      <Modal
        title="创建题集"
        open={createModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        okText="创建"
        cancelText="取消"
        width={600}
      >
        <Form form={form} onFinish={handleCreateSet} layout="vertical">
          <Form.Item
            name="title"
            label="题集名称"
            rules={[{ required: true, message: '请输入题集名称' }]}
          >
            <Input placeholder="例如: 第一章练习题" />
          </Form.Item>

          <Form.Item name="description" label="题集描述">
            <TextArea rows={3} placeholder="简要描述这个题集的内容和目的" />
          </Form.Item>

          <Form.Item
            name="set_type"
            label="题集类型"
            rules={[{ required: true, message: '请选择题集类型' }]}
          >
            <Select placeholder="选择类型">
              <Select.Option value="practice">日常练习</Select.Option>
              <Select.Option value="quiz">小测验</Select.Option>
              <Select.Option value="chapter">章节测试</Select.Option>
              <Select.Option value="exam">模拟考试</Select.Option>
              <Select.Option value="final">期末考试</Select.Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="pass_score"
                label="及格分数"
                rules={[{ required: true, message: '请输入及格分数' }]}
              >
                <Input type="number" placeholder="例如: 60" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="time_limit" label="时间限制(分钟)">
                <Input type="number" placeholder="不填则不限时" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
