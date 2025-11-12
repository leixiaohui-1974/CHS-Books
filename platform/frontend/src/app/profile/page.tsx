'use client';

import React, { useEffect, useState } from 'react';
import {
  Card,
  Avatar,
  Descriptions,
  Button,
  Modal,
  Form,
  Input,
  Upload,
  message,
  Tabs,
  Statistic,
  Row,
  Col,
  List,
  Badge,
  Tag
} from 'antd';
import {
  UserOutlined,
  EditOutlined,
  LogoutOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  CalendarOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  BookOutlined,
  UploadOutlined,
  GithubOutlined,
  WechatOutlined
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { authService, UserInfo, UpdateUserInfoData, ChangePasswordData } from '@/services/authService';
import { oauthService, OAuthAccountInfo, OAuthProvider } from '@/services/oauthService';
import './profile.css';

const { TabPane } = Tabs;

export default function ProfilePage() {
  const router = useRouter();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [oauthAccounts, setOauthAccounts] = useState<OAuthAccountInfo[]>([]);
  const [editForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  // 加载用户信息
  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      setLoading(true);
      const data = await authService.getCurrentUser();
      setUserInfo(data);
      
      // 设置编辑表单初始值
      editForm.setFieldsValue({
        full_name: data.full_name,
        bio: data.bio
      });

      // 加载OAuth账号
      try {
        const accounts = await oauthService.getOAuthAccounts();
        setOauthAccounts(accounts);
      } catch (err) {
        console.error('加载OAuth账号失败:', err);
      }
    } catch (error: any) {
      message.error('加载用户信息失败');
      if (error.response?.status === 401) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  // 编辑用户信息
  const handleEdit = async (values: any) => {
    try {
      const data: UpdateUserInfoData = {
        full_name: values.full_name,
        bio: values.bio
      };

      const updated = await authService.updateCurrentUser(data);
      setUserInfo(updated);
      setEditModalVisible(false);
      message.success('信息更新成功');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败');
    }
  };

  // 修改密码
  const handleChangePassword = async (values: any) => {
    try {
      const data: ChangePasswordData = {
        old_password: values.old_password,
        new_password: values.new_password
      };

      await authService.changePassword(data);
      setPasswordModalVisible(false);
      passwordForm.resetFields();
      message.success('密码修改成功，请重新登录');

      // 跳转到登录页
      setTimeout(() => {
        router.push('/login');
      }, 1500);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '修改密码失败');
    }
  };

  // 登出
  const handleLogout = async () => {
    Modal.confirm({
      title: '确认登出',
      content: '确定要退出登录吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await authService.logout();
          message.success('已退出登录');
          router.push('/login');
        } catch (error) {
          message.error('登出失败');
        }
      }
    });
  };

  // 格式化学习时长
  const formatLearningTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分钟`;
  };

  // 格式化日期
  const formatDate = (dateString?: string) => {
    if (!dateString) return '未知';
    return new Date(dateString).toLocaleString('zh-CN');
  };

  // 处理OAuth绑定
  const handleBindOAuth = async (provider: OAuthProvider) => {
    try {
      await oauthService.startOAuthLogin(provider);
    } catch (error: any) {
      message.error(error.response?.data?.detail || `绑定${provider}失败`);
    }
  };

  // 处理OAuth解绑
  const handleUnbindOAuth = async (provider: OAuthProvider) => {
    Modal.confirm({
      title: `确认解绑${provider}账号？`,
      content: '解绑后将无法使用该账号登录',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await oauthService.unbindAccount(provider);
          message.success(`已解绑${provider}账号`);
          // 重新加载OAuth账号列表
          const accounts = await oauthService.getOAuthAccounts();
          setOauthAccounts(accounts);
        } catch (error: any) {
          message.error(error.response?.data?.detail || `解绑${provider}失败`);
        }
      }
    });
  };

  // 检查是否已绑定某个OAuth账号
  const isOAuthBound = (provider: string): boolean => {
    return oauthAccounts.some(account => account.provider === provider);
  };

  if (loading || !userInfo) {
    return <div className="profile-loading">加载中...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <Card>
          <div className="profile-header-content">
            <Avatar
              size={100}
              icon={<UserOutlined />}
              src={userInfo.avatar_url}
            />
            <div className="profile-info">
              <h1>{userInfo.username}</h1>
              {userInfo.full_name && <p className="full-name">{userInfo.full_name}</p>}
              <div className="profile-meta">
                <Tag color={userInfo.is_premium ? 'gold' : 'default'}>
                  {userInfo.is_premium ? '会员' : '普通用户'}
                </Tag>
                <Tag color={userInfo.is_verified ? 'green' : 'default'}>
                  {userInfo.is_verified ? '已认证' : '未认证'}
                </Tag>
                <Tag color="blue">{userInfo.role}</Tag>
              </div>
              {userInfo.bio && <p className="bio">{userInfo.bio}</p>}
            </div>
            <div className="profile-actions">
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => setEditModalVisible(true)}
              >
                编辑资料
              </Button>
              <Button
                icon={<LogoutOutlined />}
                onClick={handleLogout}
              >
                退出登录
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card title="学习统计" bordered={false}>
            <Statistic
              title="总学习时长"
              value={formatLearningTime(userInfo.total_learning_time)}
              prefix={<ClockCircleOutlined />}
            />
            <Statistic
              title="登录次数"
              value={userInfo.login_count}
              prefix={<UserOutlined />}
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>

        <Col xs={24} md={16}>
          <Card title="账号信息" bordered={false}>
            <Descriptions column={1}>
              <Descriptions.Item label="用户ID">
                {userInfo.id}
              </Descriptions.Item>
              <Descriptions.Item label="用户名">
                {userInfo.username}
              </Descriptions.Item>
              <Descriptions.Item
                label="邮箱"
                icon={<MailOutlined />}
              >
                {userInfo.email || '未绑定'}
                {userInfo.email && (
                  <Badge
                    status={userInfo.email_verified ? 'success' : 'warning'}
                    text={userInfo.email_verified ? '已验证' : '未验证'}
                    style={{ marginLeft: 8 }}
                  />
                )}
              </Descriptions.Item>
              <Descriptions.Item
                label="手机号"
                icon={<PhoneOutlined />}
              >
                {userInfo.phone || '未绑定'}
                {userInfo.phone && (
                  <Badge
                    status={userInfo.phone_verified ? 'success' : 'warning'}
                    text={userInfo.phone_verified ? '已验证' : '未验证'}
                    style={{ marginLeft: 8 }}
                  />
                )}
              </Descriptions.Item>
              <Descriptions.Item label="注册时间">
                <CalendarOutlined /> {formatDate(userInfo.created_at)}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录">
                <CalendarOutlined /> {formatDate(userInfo.last_login_at)}
              </Descriptions.Item>
              <Descriptions.Item label="账号状态">
                <Badge
                  status={userInfo.status === 'active' ? 'success' : 'error'}
                  text={userInfo.status}
                />
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Card title="安全设置" style={{ marginTop: 16 }}>
        <List>
          <List.Item
            actions={[
              <Button
                key="change"
                type="link"
                onClick={() => setPasswordModalVisible(true)}
              >
                修改
              </Button>
            ]}
          >
            <List.Item.Meta
              avatar={<LockOutlined style={{ fontSize: 24 }} />}
              title="登录密码"
              description="定期更换密码以保护账号安全"
            />
          </List.Item>
          <List.Item
            actions={[
              <Button key="bind" type="link" disabled>
                绑定
              </Button>
            ]}
          >
            <List.Item.Meta
              avatar={<MailOutlined style={{ fontSize: 24 }} />}
              title="邮箱绑定"
              description={userInfo.email ? `已绑定: ${userInfo.email}` : '未绑定邮箱'}
            />
          </List.Item>
          <List.Item
            actions={[
              <Button key="bind" type="link" disabled>
                绑定
              </Button>
            ]}
          >
            <List.Item.Meta
              avatar={<PhoneOutlined style={{ fontSize: 24 }} />}
              title="手机绑定"
              description={userInfo.phone ? `已绑定: ${userInfo.phone}` : '未绑定手机号'}
            />
          </List.Item>
        </List>
      </Card>

      <Card title="第三方账号" style={{ marginTop: 16 }}>
        <List>
          <List.Item
            actions={[
              isOAuthBound('github') ? (
                <Button 
                  key="unbind" 
                  type="link" 
                  danger
                  onClick={() => handleUnbindOAuth('github')}
                >
                  解绑
                </Button>
              ) : (
                <Button 
                  key="bind" 
                  type="link"
                  onClick={() => handleBindOAuth('github')}
                >
                  绑定
                </Button>
              )
            ]}
          >
            <List.Item.Meta
              avatar={<GithubOutlined style={{ fontSize: 24 }} />}
              title="GitHub"
              description={isOAuthBound('github') ? '已绑定GitHub账号' : '绑定GitHub账号快速登录'}
            />
          </List.Item>
          <List.Item
            actions={[
              isOAuthBound('google') ? (
                <Button 
                  key="unbind" 
                  type="link" 
                  danger
                  onClick={() => handleUnbindOAuth('google')}
                >
                  解绑
                </Button>
              ) : (
                <Button 
                  key="bind" 
                  type="link"
                  onClick={() => handleBindOAuth('google')}
                >
                  绑定
                </Button>
              )
            ]}
          >
            <List.Item.Meta
              avatar={<span style={{ fontSize: 24 }}>🔗</span>}
              title="Google"
              description={isOAuthBound('google') ? '已绑定Google账号' : '绑定Google账号快速登录'}
            />
          </List.Item>
          <List.Item
            actions={[
              isOAuthBound('wechat') ? (
                <Button 
                  key="unbind" 
                  type="link" 
                  danger
                  onClick={() => handleUnbindOAuth('wechat')}
                >
                  解绑
                </Button>
              ) : (
                <Button 
                  key="bind" 
                  type="link"
                  onClick={() => handleBindOAuth('wechat')}
                >
                  绑定
                </Button>
              )
            ]}
          >
            <List.Item.Meta
              avatar={<WechatOutlined style={{ fontSize: 24, color: '#07c160' }} />}
              title="微信"
              description={isOAuthBound('wechat') ? '已绑定微信账号' : '绑定微信账号快速登录'}
            />
          </List.Item>
        </List>
      </Card>

      {/* 编辑资料Modal */}
      <Modal
        title="编辑资料"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
      >
        <Form
          form={editForm}
          onFinish={handleEdit}
          layout="vertical"
        >
          <Form.Item
            name="full_name"
            label="全名"
          >
            <Input placeholder="请输入您的全名" />
          </Form.Item>

          <Form.Item
            name="bio"
            label="个人简介"
          >
            <Input.TextArea
              rows={4}
              placeholder="介绍一下自己吧"
              maxLength={500}
              showCount
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              保存
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 修改密码Modal */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onCancel={() => setPasswordModalVisible(false)}
        footer={null}
      >
        <Form
          form={passwordForm}
          onFinish={handleChangePassword}
          layout="vertical"
        >
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password placeholder="请输入当前密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 8, message: '密码至少8位' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
                message: '密码必须包含大小写字母和数字'
              }
            ]}
            hasFeedback
          >
            <Input.Password placeholder="至少8位，含大小写字母和数字" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            hasFeedback
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              确认修改
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
