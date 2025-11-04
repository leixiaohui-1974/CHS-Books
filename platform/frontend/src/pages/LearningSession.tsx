/**
 * 学习会话页面
 * 集成代码工作区、结果展示和AI聊天的完整学习界面
 */

import React, { useState, useEffect } from 'react';
import { Layout, Row, Col, Card, Button, message, Spin } from 'antd';
import { PlayCircleOutlined, SaveOutlined, HistoryOutlined } from '@ant-design/icons';
import CodeWorkspace from '../components/CodeWorkspace';
import ResultDashboard from '../components/ResultDashboard';
import AIChat from '../components/AIChat';

const { Header, Content, Sider } = Layout;

interface Session {
  session_id: string;
  user_id: string;
  book_slug: string;
  case_slug: string;
  status: string;
  created_at: string;
}

interface ExecutionResult {
  execution_id: string;
  status: string;
  results?: any;
  error?: string;
}

const LearningSession: React.FC = () => {
  // 状态管理
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [currentCode, setCurrentCode] = useState('');
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  // 初始化会话
  useEffect(() => {
    initSession();
  }, []);

  const initSession = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/sessions/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          book_slug: 'water-environment-simulation',
          case_slug: 'case_01_diffusion',
        }),
      });

      if (!response.ok) throw new Error('创建会话失败');

      const data = await response.json();
      setSession(data);
      message.success('学习会话已创建');

      // 加载案例代码
      await loadCaseCode(data.book_slug, data.case_slug);
    } catch (error) {
      message.error('初始化失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const loadCaseCode = async (bookSlug: string, caseSlug: string) => {
    try {
      const response = await fetch('/api/v2/code/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_slug: bookSlug,
          case_slug: caseSlug,
        }),
      });

      if (!response.ok) throw new Error('加载代码失败');

      const data = await response.json();
      if (data.files && data.files.length > 0) {
        setCurrentCode(data.files[0].content);
      }
      message.success('代码加载完成');
    } catch (error) {
      message.error('加载代码失败: ' + error);
    }
  };

  const handleCodeChange = (newCode: string) => {
    setCurrentCode(newCode);
  };

  const handleExecute = async () => {
    if (!session) {
      message.warning('请先创建会话');
      return;
    }

    setExecuting(true);
    setExecutionResult(null);

    try {
      // 启动执行
      const response = await fetch('/api/v2/execution/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.session_id,
          script_path: 'main.py',
          parameters: {},
        }),
      });

      if (!response.ok) throw new Error('启动执行失败');

      const data = await response.json();
      
      // 连接WebSocket获取实时输出
      connectWebSocket(data.execution_id);

      message.success('执行已启动');
    } catch (error) {
      message.error('执行失败: ' + error);
      setExecuting(false);
    }
  };

  const connectWebSocket = (executionId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/api/v2/execution/ws/${executionId}`);

    ws.onopen = () => {
      setWsConnected(true);
      console.log('WebSocket已连接');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'output') {
        console.log('输出:', message.data);
      } else if (message.type === 'status') {
        console.log('状态:', message.status);
        
        if (message.status === 'completed') {
          setExecuting(false);
          setExecutionResult({
            execution_id: executionId,
            status: 'completed',
            results: message.results,
          });
          ws.close();
        } else if (message.status === 'failed') {
          setExecuting(false);
          setExecutionResult({
            execution_id: executionId,
            status: 'failed',
            error: message.error,
          });
          ws.close();
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      message.error('实时连接失败');
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.log('WebSocket已断开');
    };
  };

  const handleSave = async () => {
    if (!session) return;

    try {
      const response = await fetch(`/api/v2/code/${session.session_id}/edit`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: 'main.py',
          content: currentCode,
        }),
      });

      if (!response.ok) throw new Error('保存失败');

      message.success('代码已保存');
    } catch (error) {
      message.error('保存失败: ' + error);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" tip="正在初始化学习环境..." />
      </div>
    );
  }

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 头部 */}
      <Header style={{ 
        background: '#fff', 
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{ margin: 0 }}>智能知识平台 V2.0</h2>
          {session && (
            <span style={{ fontSize: 12, color: '#888' }}>
              会话: {session.session_id} | 状态: {session.status}
            </span>
          )}
        </div>
        
        <div>
          <Button 
            icon={<SaveOutlined />} 
            onClick={handleSave}
            style={{ marginRight: 8 }}
          >
            保存
          </Button>
          <Button 
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleExecute}
            loading={executing}
            disabled={!session}
          >
            {executing ? '执行中...' : '运行代码'}
          </Button>
        </div>
      </Header>

      {/* 主内容区 */}
      <Layout>
        {/* 左侧：代码编辑器 */}
        <Content style={{ padding: 16, minWidth: 600 }}>
          <Card 
            title="代码工作区" 
            bordered={false}
            style={{ height: '100%' }}
            extra={
              <Button size="small" icon={<HistoryOutlined />}>
                查看历史
              </Button>
            }
          >
            <CodeWorkspace
              sessionId={session?.session_id || ''}
              onCodeChange={handleCodeChange}
              initialCode={currentCode}
            />
          </Card>
        </Content>

        {/* 右侧：结果展示和AI聊天 */}
        <Sider 
          width={500} 
          style={{ 
            background: '#fff',
            borderLeft: '1px solid #f0f0f0'
          }}
        >
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* 结果展示区 - 占60% */}
            <div style={{ flex: '0 0 60%', padding: 16, borderBottom: '1px solid #f0f0f0' }}>
              <Card 
                title="执行结果" 
                bordered={false}
                size="small"
                extra={
                  wsConnected && (
                    <span style={{ color: '#52c41a', fontSize: 12 }}>
                      ● 实时连接
                    </span>
                  )
                }
              >
                {executionResult ? (
                  <ResultDashboard
                    executionId={executionResult.execution_id}
                    results={executionResult.results}
                  />
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '40px 0',
                    color: '#999'
                  }}>
                    {executing ? (
                      <Spin tip="代码执行中..." />
                    ) : (
                      <div>
                        <PlayCircleOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                        <p>点击"运行代码"查看结果</p>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            </div>

            {/* AI聊天区 - 占40% */}
            <div style={{ flex: '1', padding: 16, overflow: 'hidden' }}>
              <AIChat
                sessionId={session?.session_id || ''}
                context={{
                  code: currentCode,
                  results: executionResult?.results,
                }}
              />
            </div>
          </div>
        </Sider>
      </Layout>
    </Layout>
  );
};

export default LearningSession;
