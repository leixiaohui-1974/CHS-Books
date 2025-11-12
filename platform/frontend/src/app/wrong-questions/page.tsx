'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card, Button, Tabs, Empty, Spin, Tag, Space, Modal, Input, message,
  Statistic, Row, Col, Tooltip, Popconfirm
} from 'ant-d';
import {
  BookOutlined, CheckCircleOutlined, EditOutlined, DeleteOutlined,
  FireOutlined, TrophyOutlined, BulbOutlined, WarningOutlined
} from '@ant-design/icons';
import { questionService, WrongQuestion, Question } from '@/services/questionService';
import { useAuth } from '@/contexts/AuthContext';
import ReactMarkdown from 'react-markdown';
import './wrong-questions.css';

const { TextArea } = Input;
const { TabPane } = Tabs;

export default function WrongQuestionsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [loading, setLoading] = useState(true);
  const [wrongQuestions, setWrongQuestions] = useState<WrongQuestion[]>([]);
  const [masteredQuestions, setMasteredQuestions] = useState<WrongQuestion[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [noteModalVisible, setNoteModalVisible] = useState(false);
  const [currentNotes, setCurrentNotes] = useState('');
  const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/wrong-questions');
      return;
    }

    if (user) {
      loadWrongQuestions();
    }
  }, [user, authLoading]);

  const loadWrongQuestions = async () => {
    try {
      setLoading(true);

      // 加载未掌握的错题
      const notMastered = await questionService.getWrongQuestions({
        is_mastered: false,
        limit: 100,
      });

      // 加载已掌握的错题
      const mastered = await questionService.getWrongQuestions({
        is_mastered: true,
        limit: 100,
      });

      setWrongQuestions(notMastered);
      setMasteredQuestions(mastered);
    } catch (error: any) {
      console.error('Failed to load wrong questions:', error);
      message.error('加载错题本失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (wrongQuestion: WrongQuestion) => {
    try {
      const question = await questionService.getQuestion(wrongQuestion.question_id);
      setSelectedQuestion(question);
    } catch (error: any) {
      console.error('Failed to load question detail:', error);
      message.error('加载题目详情失败');
    }
  };

  const handleAddNote = (wrongQuestion: WrongQuestion) => {
    setEditingQuestionId(wrongQuestion.question_id);
    setCurrentNotes(wrongQuestion.notes || '');
    setNoteModalVisible(true);
  };

  const handleSaveNote = async () => {
    if (!editingQuestionId) return;

    try {
      await questionService.addWrongQuestionNote(editingQuestionId, currentNotes);
      message.success('笔记保存成功');
      setNoteModalVisible(false);
      setEditingQuestionId(null);
      setCurrentNotes('');
      
      // 重新加载错题列表
      loadWrongQuestions();
    } catch (error: any) {
      console.error('Failed to save note:', error);
      message.error('保存笔记失败');
    }
  };

  const handleRemove = async (questionId: number) => {
    try {
      await questionService.removeWrongQuestion(questionId);
      message.success('已从错题本移除');
      
      // 重新加载错题列表
      loadWrongQuestions();
    } catch (error: any) {
      console.error('Failed to remove question:', error);
      message.error('移除失败');
    }
  };

  const handlePractice = (wrongQuestion: WrongQuestion) => {
    // 跳转到练习页面，只练习这道错题
    router.push(`/practice?question_id=${wrongQuestion.question_id}`);
  };

  const getDifficultyColor = (difficulty: string): string => {
    const colors: Record<string, string> = {
      easy: '#52c41a',
      medium: '#faad14',
      hard: '#f5222d',
      expert: '#722ed1',
    };
    return colors[difficulty] || '#1890ff';
  };

  const getDifficultyText = (difficulty: string): string => {
    const texts: Record<string, string> = {
      easy: '简单',
      medium: '中等',
      hard: '困难',
      expert: '专家',
    };
    return texts[difficulty] || difficulty;
  };

  const getQuestionTypeText = (type: string): string => {
    const texts: Record<string, string> = {
      single_choice: '单选题',
      multiple_choice: '多选题',
      true_false: '判断题',
      fill_blank: '填空题',
      short_answer: '简答题',
      code: '编程题',
      calculation: '计算题',
    };
    return texts[type] || type;
  };

  const renderWrongQuestionCard = (wrongQuestion: WrongQuestion, isMastered: boolean) => (
    <Card
      key={wrongQuestion.id}
      className={`wrong-question-card ${isMastered ? 'mastered' : ''}`}
      hoverable
    >
      <div className="card-header">
        <Space direction="vertical" size="small" style={{ flex: 1 }}>
          <div className="question-title">{wrongQuestion.question_title}</div>
          <Space size="small">
            <Tag color={getDifficultyColor(wrongQuestion.difficulty)}>
              {getDifficultyText(wrongQuestion.difficulty)}
            </Tag>
            <Tag color="blue">{getQuestionTypeText(wrongQuestion.question_type)}</Tag>
            {isMastered && <Tag color="success" icon={<CheckCircleOutlined />}>已掌握</Tag>}
          </Space>
        </Space>
      </div>

      <div className="card-content">
        <ReactMarkdown>{wrongQuestion.question_content.substring(0, 150)}...</ReactMarkdown>
      </div>

      <div className="card-stats">
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="错误次数"
              value={wrongQuestion.wrong_count}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#f5222d', fontSize: 18 }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="正确次数"
              value={wrongQuestion.correct_count}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a', fontSize: 18 }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="正确率"
              value={
                wrongQuestion.wrong_count + wrongQuestion.correct_count > 0
                  ? Math.round(
                      (wrongQuestion.correct_count /
                        (wrongQuestion.wrong_count + wrongQuestion.correct_count)) *
                        100
                    )
                  : 0
              }
              suffix="%"
              valueStyle={{ fontSize: 18 }}
            />
          </Col>
        </Row>
      </div>

      {wrongQuestion.notes && (
        <div className="card-notes">
          <BulbOutlined style={{ color: '#faad14', marginRight: 8 }} />
          <span className="notes-label">我的笔记: </span>
          <span className="notes-content">{wrongQuestion.notes}</span>
        </div>
      )}

      <div className="card-actions">
        <Space size="middle">
          <Button
            type="primary"
            icon={<FireOutlined />}
            onClick={() => handlePractice(wrongQuestion)}
          >
            练习
          </Button>
          <Button icon={<BookOutlined />} onClick={() => handleViewDetail(wrongQuestion)}>
            查看详情
          </Button>
          <Button icon={<EditOutlined />} onClick={() => handleAddNote(wrongQuestion)}>
            {wrongQuestion.notes ? '编辑笔记' : '添加笔记'}
          </Button>
          {isMastered && (
            <Popconfirm
              title="确定要移除这道题吗？"
              onConfirm={() => handleRemove(wrongQuestion.question_id)}
              okText="确定"
              cancelText="取消"
            >
              <Button danger icon={<DeleteOutlined />}>
                移除
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      <div className="card-footer">
        <span className="last-wrong-time">
          最后错误时间: {new Date(wrongQuestion.last_wrong_at).toLocaleString()}
        </span>
      </div>
    </Card>
  );

  if (authLoading || loading) {
    return (
      <div className="wrong-questions-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  const totalWrong = wrongQuestions.length;
  const totalMastered = masteredQuestions.length;
  const masteryRate =
    totalWrong + totalMastered > 0
      ? Math.round((totalMastered / (totalWrong + totalMastered)) * 100)
      : 0;

  return (
    <div className="wrong-questions-container">
      {/* 统计卡片 */}
      <Card className="stats-card">
        <Row gutter={32}>
          <Col span={8}>
            <Statistic
              title="待攻克错题"
              value={totalWrong}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="已掌握错题"
              value={totalMastered}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="掌握率"
              value={masteryRate}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{
                color: masteryRate >= 80 ? '#52c41a' : masteryRate >= 50 ? '#faad14' : '#f5222d',
              }}
            />
          </Col>
        </Row>
      </Card>

      {/* 错题列表 */}
      <Card className="questions-card">
        <Tabs defaultActiveKey="not-mastered" size="large">
          <TabPane
            tab={
              <span>
                <WarningOutlined />
                待攻克 ({totalWrong})
              </span>
            }
            key="not-mastered"
          >
            {wrongQuestions.length > 0 ? (
              <div className="questions-list">
                {wrongQuestions.map((wq) => renderWrongQuestionCard(wq, false))}
              </div>
            ) : (
              <Empty description="暂无待攻克错题" />
            )}
          </TabPane>
          <TabPane
            tab={
              <span>
                <CheckCircleOutlined />
                已掌握 ({totalMastered})
              </span>
            }
            key="mastered"
          >
            {masteredQuestions.length > 0 ? (
              <div className="questions-list">
                {masteredQuestions.map((wq) => renderWrongQuestionCard(wq, true))}
              </div>
            ) : (
              <Empty description="暂无已掌握错题" />
            )}
          </TabPane>
        </Tabs>
      </Card>

      {/* 题目详情弹窗 */}
      <Modal
        title="题目详情"
        open={!!selectedQuestion}
        onCancel={() => setSelectedQuestion(null)}
        footer={[
          <Button key="close" onClick={() => setSelectedQuestion(null)}>
            关闭
          </Button>,
          <Button
            key="practice"
            type="primary"
            icon={<FireOutlined />}
            onClick={() => {
              if (selectedQuestion) {
                router.push(`/practice?question_id=${selectedQuestion.id}`);
              }
            }}
          >
            开始练习
          </Button>,
        ]}
        width={800}
      >
        {selectedQuestion && (
          <div className="question-detail">
            <Space size="middle" style={{ marginBottom: 16 }}>
              <Tag color={getDifficultyColor(selectedQuestion.difficulty)}>
                {getDifficultyText(selectedQuestion.difficulty)}
              </Tag>
              <Tag color="blue">{getQuestionTypeText(selectedQuestion.question_type)}</Tag>
              <Tag color="orange">
                <TrophyOutlined /> {selectedQuestion.score}分
              </Tag>
            </Space>

            <h3>{selectedQuestion.title}</h3>
            <div className="detail-content">
              <ReactMarkdown>{selectedQuestion.content}</ReactMarkdown>
            </div>

            {selectedQuestion.explanation && (
              <div className="detail-explanation">
                <h4>
                  <BulbOutlined style={{ color: '#faad14' }} /> 答案解析
                </h4>
                <div className="explanation-content">{selectedQuestion.explanation}</div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 笔记编辑弹窗 */}
      <Modal
        title="编辑笔记"
        open={noteModalVisible}
        onOk={handleSaveNote}
        onCancel={() => {
          setNoteModalVisible(false);
          setEditingQuestionId(null);
          setCurrentNotes('');
        }}
        okText="保存"
        cancelText="取消"
      >
        <TextArea
          value={currentNotes}
          onChange={(e) => setCurrentNotes(e.target.value)}
          placeholder="记录你的解题思路、易错点等..."
          rows={6}
        />
      </Modal>
    </div>
  );
}
