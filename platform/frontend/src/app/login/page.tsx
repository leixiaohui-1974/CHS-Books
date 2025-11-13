'use client';

import React, { useState } from 'react';
import { Form, Input, Button, Checkbox, Tabs, message, Divider } from 'antd';
import { UserOutlined, LockOutlined, PhoneOutlined, SafetyOutlined, GithubOutlined, WechatOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authService, LoginData, SMSLoginData, SendCodeData } from '@/services/authService';
import { oauthService } from '@/services/oauthService';
import './login.css';

const { TabPane } = Tabs;

export default function LoginPage() {
  const router = useRouter();
  const [passwordForm] = Form.useForm();
  const [smsForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [activeTab, setActiveTab] = useState('password');

  // 密码登录
  const handlePasswordLogin = async (values: any) => {
    try {
      setLoading(true);

      const data: LoginData = {
        identifier: values.identifier,
        password: values.password,
        remember_me: values.remember,
        device_name: navigator.userAgent
      };

      const response = await authService.login(data);

      // 检查是否需要2FA
      if (response.requires_2fa) {
        message.info('请输入双因素认证码');
        // 保存临时token并跳转到2FA验证页面
        if (response.temp_token) {
          sessionStorage.setItem('temp_token', response.temp_token);
          router.push('/verify-2fa');
        }
        return;
      }

      message.success('登录成功！');

      // 跳转到首页或用户中心
      setTimeout(() => {
        router.push('/dashboard');
      }, 500);

    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 短信登录
  const handleSMSLogin = async (values: any) => {
    try {
      setLoading(true);

      const data: SMSLoginData = {
        phone: values.phone,
        code: values.code,
        device_name: navigator.userAgent
      };

      const response = await authService.smsLogin(data);

      message.success('登录成功！');

      setTimeout(() => {
        router.push('/dashboard');
      }, 500);

    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查手机号和验证码');
    } finally {
      setLoading(false);
    }
  };

  // 发送验证码
  const handleSendCode = async () => {
    try {
      const phone = smsForm.getFieldValue('phone');

      if (!phone) {
        message.error('请输入手机号');
        return;
      }

      if (!/^1[3-9]\d{9}$/.test(phone)) {
        message.error('请输入有效的手机号');
        return;
      }

      setSendingCode(true);

      const data: SendCodeData = {
        type: 'login',
        recipient: phone,
        method: 'sms'
      };

      await authService.sendCode(data);
      message.success('验证码已发送');

      // 开始倒计时
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

    } catch (error: any) {
      message.error(error.response?.data?.detail || '发送验证码失败');
    } finally {
      setSendingCode(false);
    }
  };

  // OAuth登录
  const handleOAuthLogin = async (provider: 'github' | 'google' | 'wechat') => {
    try {
      await oauthService.startOAuthLogin(provider);
    } catch (error: any) {
      message.error(error.response?.data?.detail || `${provider}登录失败`);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>欢迎回来</h1>
          <p>登录您的账号继续学习</p>
        </div>

        <Tabs activeKey={activeTab} onChange={setActiveTab} centered>
          <TabPane tab="账号登录" key="password">
            <Form
              form={passwordForm}
              onFinish={handlePasswordLogin}
              layout="vertical"
              size="large"
            >
              <Form.Item
                name="identifier"
                rules={[{ required: true, message: '请输入用户名/邮箱/手机号' }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="用户名 / 邮箱 / 手机号"
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                />
              </Form.Item>

              <Form.Item>
                <div className="login-options">
                  <Form.Item name="remember" valuePropName="checked" noStyle>
                    <Checkbox>记住我 (7天)</Checkbox>
                  </Form.Item>
                  <Link href="/forgot-password" className="forgot-link">
                    忘记密码？
                  </Link>
                </div>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  size="large"
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="短信登录" key="sms">
            <Form
              form={smsForm}
              onFinish={handleSMSLogin}
              layout="vertical"
              size="large"
            >
              <Form.Item
                name="phone"
                rules={[
                  { required: true, message: '请输入手机号' },
                  { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                ]}
              >
                <Input
                  prefix={<PhoneOutlined />}
                  placeholder="手机号"
                />
              </Form.Item>

              <Form.Item
                name="code"
                rules={[
                  { required: true, message: '请输入验证码' },
                  { len: 6, message: '验证码为6位数字' }
                ]}
              >
                <Input
                  prefix={<SafetyOutlined />}
                  placeholder="6位验证码"
                  suffix={
                    <Button
                      type="link"
                      onClick={handleSendCode}
                      loading={sendingCode}
                      disabled={countdown > 0}
                    >
                      {countdown > 0 ? `${countdown}秒后重发` : '获取验证码'}
                    </Button>
                  }
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  size="large"
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>

        <Divider>或使用以下方式登录</Divider>

        <div className="oauth-buttons">
          <Button
            icon={<WechatOutlined />}
            onClick={() => handleOAuthLogin('wechat')}
            className="oauth-btn wechat"
          >
            微信
          </Button>
          <Button
            icon={<GithubOutlined />}
            onClick={() => handleOAuthLogin('github')}
            className="oauth-btn github"
          >
            GitHub
          </Button>
        </div>

        <div className="login-footer">
          <span>还没有账号？</span>
          <Link href="/register">立即注册</Link>
        </div>
      </div>
    </div>
  );
}
