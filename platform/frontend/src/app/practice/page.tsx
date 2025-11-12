'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Card, Button, Radio, Checkbox, Input, Space, message, Modal, Tag,
  Progress, Statistic, Empty, Spin, Typography, Divider
} from 'ant-d';
import {
  CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined,
  TrophyOutlined, FireOutlined, BulbOutlined
} from '@ant-design/icons';
import { questionService, Question, Submission } from '@/services/questionService';
import { useAuth } from '@/contexts/AuthContext';
import ReactMarkdown from 'react-markdown';
import './practice.css';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

export default function PracticePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading: authLoading } = useAuth();

  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submissions, setSubmissions] = useState<Record<number, Submission>>({});
  const [startTime, setStartTime] = useState<Date>(new Date());
  const [showResult, setShowResult] = useState(false);
  const [currentSubmission, setCurrentSubmission] = useState<Submission | null>(null);

  // 获取URL参数
  const questionSetId = searchParams.get('set_id');
  const knowledgePointId = searchParams.get('kp_id');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/practice');
      return;
    }

    if (user) {
      loadQuestions();
    }
  }, [user, authLoading, questionSetId, knowledgePointId]);

  const loadQuestions = async () => {
    try {
      setLoading(true);

      if (questionSetId) {
        // 加载题集中的题目
        const { questions: setQuestions } = await questionService.getQuestionsBySet(
          parseInt(questionSetId)
        );
        setQuestions(setQuestions);
      } else {
        // 加载题目列表
        const params: any = { limit: 20 };
        if (knowledgePointId) {
          params.knowledge_point_id = parseInt(knowledgePointId);
        }
        const { questions: allQuestions } = await questionService.getQuestions(params);
        setQuestions(allQuestions);
      }

      setStartTime(new Date());
    } catch (error: any) {
      console.error('Failed to load questions:', error);
      message.error('加载题目失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (value: string) => {
    const currentQuestion = questions[currentIndex];
    setAnswers({
      ...answers,
      [currentQuestion.id]: value,
    });
  };

  const handleSubmit = async () => {
    const currentQuestion = questions[currentIndex];
    const answer = answers[currentQuestion.id];

    if (!answer) {
      message.warning('请先作答');
      return;
    }

    try {
      const timeSpent = Math.floor((new Date().getTime() - startTime.getTime()) / 1000);
      
      const submission = await questionService.submitAnswer({
        question_id: currentQuestion.id,
        answer,
        time_spent: timeSpent,
      });

      setSubmissions({
        ...submissions,
        [currentQuestion.id]: submission,
      });
      setCurrentSubmission(submission);
      setShowResult(true);

      // 如果答错，提示加入错题本
      if (!submission.is_correct) {
        message.warning('答案错误，已加入错题本');
      } else {
        message.success('回答正确！');
      }
    } catch (error: any) {
      console.error('Failed to submit answer:', error);
      message.error('提交失败');
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowResult(false);
      setCurrentSubmission(null);
      setStartTime(new Date());
    } else {
      // 完成所有题目
      showSummary();
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowResult(false);
      setCurrentSubmission(null);
    }
  };

  const showSummary = () => {
    const totalQuestions = questions.length;
    const answeredQuestions = Object.keys(submissions).length;
    const correctCount = Object.values(submissions).filter((s) => s.is_correct).length;
    const totalScore = Object.values(submissions).reduce((sum, s) => sum + s.score, 0);
    const maxScore = questions.reduce((sum, q) => sum + q.score, 0);

    Modal.success({
      title: '练习完成',
      width: 500,
      content: (
        <div style={{ padding: '20px 0' }}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Statistic
              title="完成题数"
              value={answeredQuestions}
              suffix={`/ ${totalQuestions}`}
              prefix={<CheckCircleOutlined />}
            />
            <Statistic
              title="正确题数"
              value={correctCount}
              suffix={`/ ${answeredQuestions}`}
              valueStyle={{ color: '#3f8600' }}
              prefix={<TrophyOutlined />}
            />
            <Statistic
              title="得分"
              value={totalScore.toFixed(1)}
              suffix={`/ ${maxScore}`}
              precision={1}
              valueStyle={{ color: '#1890ff' }}
            />
            <Statistic
              title="正确率"
              value={answeredQuestions > 0 ? (correctCount / answeredQuestions) * 100 : 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: correctCount / answeredQuestions >= 0.6 ? '#3f8600' : '#cf1322' }}
            />
          </Space>
        </div>
      ),
      onOk: () => {
        router.push('/dashboard');
      },
    });
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

  const renderQuestionInput = (question: Question) => {
    const questionType = question.question_type;
    const currentAnswer = answers[question.id] || '';
    const isSubmitted = submissions[question.id];

    if (questionType === 'single_choice') {
      return (
        <Radio.Group
          value={currentAnswer}
          onChange={(e) => handleAnswer(e.target.value)}
          disabled={isSubmitted}
          style={{ width: '100%' }}
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {question.options &&
              Object.entries(question.options).map(([key, value]) => (
                <Radio key={key} value={key} style={{ fontSize: '16px' }}>
                  <span style={{ marginLeft: 8 }}>{key}. {value}</span>
                </Radio>
              ))}
          </Space>
        </Radio.Group>
      );
    } else if (questionType === 'multiple_choice') {
      return (
        <Checkbox.Group
          value={currentAnswer.split('')}
          onChange={(values) => handleAnswer(values.sort().join(''))}
          disabled={isSubmitted}
          style={{ width: '100%' }}
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {question.options &&
              Object.entries(question.options).map(([key, value]) => (
                <Checkbox key={key} value={key} style={{ fontSize: '16px' }}>
                  <span style={{ marginLeft: 8 }}>{key}. {value}</span>
                </Checkbox>
              ))}
          </Space>
        </Checkbox.Group>
      );
    } else if (questionType === 'true_false') {
      return (
        <Radio.Group
          value={currentAnswer}
          onChange={(e) => handleAnswer(e.target.value)}
          disabled={isSubmitted}
          size="large"
        >
          <Space size="large">
            <Radio value="true">正确</Radio>
            <Radio value="false">错误</Radio>
          </Space>
        </Radio.Group>
      );
    } else {
      return (
        <TextArea
          value={currentAnswer}
          onChange={(e) => handleAnswer(e.target.value)}
          disabled={isSubmitted}
          placeholder="请输入你的答案"
          rows={6}
          style={{ fontSize: '16px' }}
        />
      );
    }
  };

  if (authLoading || loading) {
    return (
      <div className="practice-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="practice-empty">
        <Empty description="暂无题目" />
        <Button type="primary" onClick={() => router.push('/dashboard')}>
          返回首页
        </Button>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const currentAnswer = answers[currentQuestion.id];
  const isSubmitted = submissions[currentQuestion.id];

  return (
    <div className="practice-container">
      {/* 进度条 */}
      <div className="practice-progress">
        <Progress
          percent={Math.round(((currentIndex + 1) / questions.length) * 100)}
          status="active"
          strokeColor="#1890ff"
        />
        <div className="progress-text">
          题目进度: {currentIndex + 1} / {questions.length}
        </div>
      </div>

      {/* 题目卡片 */}
      <Card className="question-card">
        {/* 题目头部 */}
        <div className="question-header">
          <Space size="middle">
            <Tag color={getDifficultyColor(currentQuestion.difficulty)}>
              {getDifficultyText(currentQuestion.difficulty)}
            </Tag>
            <Tag color="blue">{getQuestionTypeText(currentQuestion.question_type)}</Tag>
            <Tag color="orange">
              <TrophyOutlined /> {currentQuestion.score}分
            </Tag>
            {currentQuestion.time_limit && (
              <Tag color="red">
                <ClockCircleOutlined /> {currentQuestion.time_limit}秒
              </Tag>
            )}
          </Space>
        </div>

        {/* 题目标题 */}
        <Title level={4} style={{ marginTop: 16 }}>
          {currentIndex + 1}. {currentQuestion.title}
        </Title>

        {/* 题目内容 */}
        <div className="question-content">
          <ReactMarkdown>{currentQuestion.content}</ReactMarkdown>
        </div>

        <Divider />

        {/* 答题区域 */}
        <div className="answer-area">
          {renderQuestionInput(currentQuestion)}
        </div>

        {/* 结果展示 */}
        {showResult && currentSubmission && (
          <div className="result-panel">
            <Card
              className={`result-card ${currentSubmission.is_correct ? 'correct' : 'wrong'}`}
            >
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div className="result-header">
                  {currentSubmission.is_correct ? (
                    <>
                      <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
                      <Title level={3} style={{ color: '#52c41a', margin: 0 }}>
                        回答正确！
                      </Title>
                    </>
                  ) : (
                    <>
                      <CloseCircleOutlined style={{ fontSize: 48, color: '#f5222d' }} />
                      <Title level={3} style={{ color: '#f5222d', margin: 0 }}>
                        回答错误
                      </Title>
                    </>
                  )}
                </div>

                <div>
                  <Text strong>得分: </Text>
                  <Text style={{ fontSize: 18, color: '#1890ff' }}>
                    {currentSubmission.score} / {currentQuestion.score}
                  </Text>
                </div>

                {!currentSubmission.is_correct && currentQuestion.explanation && (
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <BulbOutlined style={{ color: '#faad14' }} />
                      <Text strong style={{ marginLeft: 8 }}>答案解析:</Text>
                    </div>
                    <Paragraph style={{ backgroundColor: '#fff7e6', padding: 12, borderRadius: 4 }}>
                      {currentQuestion.explanation}
                    </Paragraph>
                  </div>
                )}
              </Space>
            </Card>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="action-buttons">
          <Space size="middle">
            <Button onClick={handlePrevious} disabled={currentIndex === 0}>
              上一题
            </Button>
            {!isSubmitted ? (
              <Button
                type="primary"
                onClick={handleSubmit}
                disabled={!currentAnswer}
                icon={<FireOutlined />}
              >
                提交答案
              </Button>
            ) : (
              <Button type="primary" onClick={handleNext} icon={<FireOutlined />}>
                {currentIndex < questions.length - 1 ? '下一题' : '完成练习'}
              </Button>
            )}
          </Space>
        </div>
      </Card>

      {/* 答题卡（侧边栏） */}
      <Card className="answer-sheet" title="答题卡">
        <div className="answer-grid">
          {questions.map((q, index) => {
            const isAnswered = answers[q.id];
            const isCorrect = submissions[q.id]?.is_correct;
            const isCurrent = index === currentIndex;

            return (
              <div
                key={q.id}
                className={`answer-item ${isCurrent ? 'current' : ''} ${
                  isAnswered ? (isCorrect ? 'correct' : isCorrect === false ? 'wrong' : 'answered') : ''
                }`}
                onClick={() => setCurrentIndex(index)}
              >
                {index + 1}
              </div>
            );
          })}
        </div>

        <Divider />

        <div className="answer-legend">
          <Space direction="vertical" size="small">
            <div>
              <span className="legend-box current"></span>
              <Text>当前题</Text>
            </div>
            <div>
              <span className="legend-box answered"></span>
              <Text>已答题</Text>
            </div>
            <div>
              <span className="legend-box correct"></span>
              <Text>答对</Text>
            </div>
            <div>
              <span className="legend-box wrong"></span>
              <Text>答错</Text>
            </div>
          </Space>
        </div>
      </Card>
    </div>
  );
}
