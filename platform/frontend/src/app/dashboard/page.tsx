'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card, Row, Col, Statistic, Progress, List, Tag, Badge, Tabs,
  Timeline, Empty, Spin, message
} from 'antd';
import {
  TrophyOutlined, FireOutlined, BookOutlined, ClockCircleOutlined,
  CheckCircleOutlined, RocketOutlined, LineChartOutlined, StarOutlined
} from '@ant-design/icons';
import { learningService, SummaryStats, DailyGoal, Achievement } from '@/services/learningService';
import { useAuth } from '@/contexts/AuthContext';
import './dashboard.css';

const { TabPane } = Tabs;

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [dailyGoal, setDailyGoal] = useState<DailyGoal | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [recentAchievements, setRecentAchievements] = useState<Achievement[]>([]);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/dashboard');
      return;
    }

    if (user) {
      loadDashboardData();
    }
  }, [user, authLoading, router]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // 并行加载数据
      const [statsData, goalData, achievementsData] = await Promise.all([
        learningService.getSummaryStats(),
        learningService.getDailyGoal(),
        learningService.getAchievements(),
      ]);

      setStats(statsData);
      setDailyGoal(goalData);
      setAchievements(achievementsData);

      // 获取最近解锁的成就
      const recent = achievementsData
        .filter((a) => a.is_unlocked)
        .sort((a, b) => {
          const dateA = a.unlocked_at ? new Date(a.unlocked_at).getTime() : 0;
          const dateB = b.unlocked_at ? new Date(b.unlocked_at).getTime() : 0;
          return dateB - dateA;
        })
        .slice(0, 5);
      setRecentAchievements(recent);
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分钟`;
  };

  const getMasteryLevelColor = (level: string): string => {
    const colors: { [key: string]: string } = {
      not_started: 'default',
      learning: 'blue',
      practicing: 'orange',
      mastered: 'green',
      expert: 'purple',
    };
    return colors[level] || 'default';
  };

  const getMasteryLevelText = (level: string): string => {
    const texts: { [key: string]: string } = {
      not_started: '未开始',
      learning: '学习中',
      practicing: '练习中',
      mastered: '已掌握',
      expert: '精通',
    };
    return texts[level] || level;
  };

  const getRarityColor = (rarity: string): string => {
    const colors: { [key: string]: string } = {
      common: '#95de64',
      rare: '#69c0ff',
      epic: '#b37feb',
      legendary: '#ffd666',
    };
    return colors[rarity] || '#95de64';
  };

  if (authLoading || loading) {
    return (
      <div className="dashboard-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>学习仪表盘</h1>
        <p>欢迎回来，{user?.username}！</p>
      </div>

      {/* 每日目标 */}
      {dailyGoal && (
        <Card className="daily-goal-card" bordered={false}>
          <h2>
            <FireOutlined /> 今日目标
          </h2>
          <Row gutter={16}>
            <Col span={8}>
              <div className="goal-item">
                <div className="goal-label">学习时长</div>
                <Progress
                  type="circle"
                  percent={Math.round(
                    (dailyGoal.actual_study_time / dailyGoal.target_study_time) * 100
                  )}
                  format={() => formatTime(dailyGoal.actual_study_time)}
                  width={100}
                />
                <div className="goal-target">目标: {formatTime(dailyGoal.target_study_time)}</div>
              </div>
            </Col>
            <Col span={8}>
              <div className="goal-item">
                <div className="goal-label">练习题数</div>
                <Progress
                  type="circle"
                  percent={Math.round(
                    (dailyGoal.actual_exercises / dailyGoal.target_exercises) * 100
                  )}
                  format={() => `${dailyGoal.actual_exercises}题`}
                  width={100}
                  strokeColor="#52c41a"
                />
                <div className="goal-target">目标: {dailyGoal.target_exercises}题</div>
              </div>
            </Col>
            <Col span={8}>
              <div className="goal-item">
                <div className="goal-label">知识点数</div>
                <Progress
                  type="circle"
                  percent={Math.round(
                    (dailyGoal.actual_knowledge_points / dailyGoal.target_knowledge_points) * 100
                  )}
                  format={() => `${dailyGoal.actual_knowledge_points}个`}
                  width={100}
                  strokeColor="#1890ff"
                />
                <div className="goal-target">目标: {dailyGoal.target_knowledge_points}个</div>
              </div>
            </Col>
          </Row>
          <div className="overall-progress">
            <span>总体完成度：</span>
            <Progress
              percent={Math.round(dailyGoal.completion_percentage)}
              status={dailyGoal.is_completed ? 'success' : 'active'}
            />
          </div>
        </Card>
      )}

      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16} className="stats-cards">
          <Col xs={24} sm={12} lg={6}>
            <Card bordered={false}>
              <Statistic
                title="总学习时长"
                value={Math.round(stats.total_study_time / 3600)}
                suffix="小时"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card bordered={false}>
              <Statistic
                title="知识点掌握"
                value={stats.mastery_distribution.mastered + stats.mastery_distribution.expert}
                suffix={`/ ${stats.total_knowledge_points}`}
                prefix={<BookOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card bordered={false}>
              <Statistic
                title="练习正确率"
                value={stats.accuracy}
                precision={1}
                suffix="%"
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card bordered={false}>
              <Statistic
                title="连续学习"
                value={stats.streak_days}
                suffix="天"
                prefix={<FireOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      <Row gutter={16} className="content-section">
        {/* 左侧内容 */}
        <Col xs={24} lg={16}>
          {/* 掌握度分布 */}
          {stats && (
            <Card title="知识点掌握度分布" className="mastery-card" bordered={false}>
              <div className="mastery-distribution">
                {Object.entries(stats.mastery_distribution).map(([level, count]) => (
                  <div key={level} className="mastery-item">
                    <Tag color={getMasteryLevelColor(level)}>
                      {getMasteryLevelText(level)}
                    </Tag>
                    <span className="mastery-count">{count}个</span>
                    <Progress
                      percent={
                        stats.total_knowledge_points > 0
                          ? Math.round((count / stats.total_knowledge_points) * 100)
                          : 0
                      }
                      showInfo={false}
                      strokeColor={getMasteryLevelColor(level)}
                    />
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* 最近7天学习情况 */}
          {stats && stats.recent_7_days && stats.recent_7_days.length > 0 && (
            <Card
              title={
                <>
                  <LineChartOutlined /> 最近7天学习情况
                </>
              }
              className="recent-stats-card"
              bordered={false}
            >
              <Timeline mode="left">
                {stats.recent_7_days.map((day, index) => (
                  <Timeline.Item
                    key={index}
                    label={day.date}
                    color={day.study_time > 0 ? 'green' : 'gray'}
                  >
                    <div className="timeline-content">
                      <p>
                        学习 <strong>{formatTime(day.study_time)}</strong>
                      </p>
                      <p>
                        完成 <strong>{day.exercises}</strong> 道练习
                      </p>
                      {day.average_score > 0 && (
                        <p>
                          平均分 <strong>{day.average_score.toFixed(1)}</strong>
                        </p>
                      )}
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )}
        </Col>

        {/* 右侧内容 */}
        <Col xs={24} lg={8}>
          {/* 成就系统 */}
          <Card
            title={
              <>
                <TrophyOutlined /> 成就系统
              </>
            }
            className="achievements-card"
            bordered={false}
          >
            <Tabs defaultActiveKey="recent">
              <TabPane tab="最近获得" key="recent">
                {recentAchievements.length > 0 ? (
                  <List
                    dataSource={recentAchievements}
                    renderItem={(achievement) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={
                            <div
                              className="achievement-icon"
                              style={{ backgroundColor: getRarityColor(achievement.rarity) }}
                            >
                              {achievement.icon || <StarOutlined />}
                            </div>
                          }
                          title={
                            <div>
                              {achievement.title}
                              <Tag
                                color={getRarityColor(achievement.rarity)}
                                style={{ marginLeft: 8 }}
                              >
                                {achievement.rarity}
                              </Tag>
                            </div>
                          }
                          description={achievement.description}
                        />
                        <div className="achievement-points">+{achievement.points}</div>
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无成就" />
                )}
              </TabPane>
              <TabPane
                tab={
                  <Badge count={achievements.filter((a) => !a.is_unlocked).length} offset={[10, 0]}>
                    <span>进行中</span>
                  </Badge>
                }
                key="progress"
              >
                <List
                  dataSource={achievements.filter((a) => !a.is_unlocked).slice(0, 5)}
                  renderItem={(achievement) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={
                          <div className="achievement-icon-gray">
                            {achievement.icon || <StarOutlined />}
                          </div>
                        }
                        title={achievement.title}
                        description={
                          <>
                            <div>{achievement.description}</div>
                            <Progress
                              percent={Math.round(achievement.progress_percentage)}
                              size="small"
                              status="active"
                            />
                            <div className="achievement-progress-text">
                              {achievement.progress_value} / {achievement.requirement_value}
                            </div>
                          </>
                        }
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
            </Tabs>
          </Card>

          {/* 快速操作 */}
          <Card title="快速开始" className="quick-actions-card" bordered={false}>
            <List>
              <List.Item
                className="quick-action-item"
                onClick={() => router.push('/practice')}
              >
                <RocketOutlined /> 开始练习
              </List.Item>
              <List.Item
                className="quick-action-item"
                onClick={() => router.push('/question-sets')}
              >
                <BookOutlined /> 题集练习
              </List.Item>
              <List.Item
                className="quick-action-item"
                onClick={() => router.push('/wrong-questions')}
              >
                <FireOutlined /> 我的错题本
              </List.Item>
              <List.Item
                className="quick-action-item"
                onClick={() => router.push('/learning/review')}
              >
                <ClockCircleOutlined /> 复习知识点
              </List.Item>
              <List.Item
                className="quick-action-item"
                onClick={() => router.push('/achievements')}
              >
                <TrophyOutlined /> 查看成就
              </List.Item>
            </List>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
