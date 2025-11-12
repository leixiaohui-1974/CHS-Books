'use client';

import React, { useState } from 'react';
import { Form, Input, Button, message, Steps, Checkbox, Spin } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authService, RegisterData, SendCodeData } from '@/services/authService';
import './register.css';

const { Step } = Steps;

export default function RegisterPage() {
  const router = useRouter();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [registerType, setRegisterType] = useState<'email' | 'phone'>('email');

  // 发送验证码
  const handleSendCode = async () => {
    try {
      const recipient = registerType === 'email' 
        ? form.getFieldValue('email')
        : form.getFieldValue('phone');

      if (!recipient) {
        message.error(`请输入${registerType === 'email' ? '邮箱' : '手机号'}`);
        return;
      }

      setSendingCode(true);

      const data: SendCodeData = {
        type: 'register',
        recipient,
        method: registerType
      };

      await authService.sendCode(data);
      message.success('验证码已发送，请查收');

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

  // 检查可用性
  const checkAvailability = async (field: 'username' | 'email' | 'phone', value: string) => {
    if (!value) return;

    try {
      const result = await authService.checkAvailability(field, value);
      if (!result.available) {
        const fieldNames = {
          username: '用户名',
          email: '邮箱',
          phone: '手机号'
        };
        throw new Error(`${fieldNames[field]}已被使用`);
      }
    } catch (error: any) {
      throw new Error(error.message || '检查失败');
    }
  };

  // 提交注册
  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);

      const data: RegisterData = {
        username: values.username,
        password: values.password,
        verification_code: values.code,
        ...(registerType === 'email' ? { email: values.email } : { phone: values.phone })
      };

      const response = await authService.register(data);
      
      message.success('注册成功！');
      
      // 跳转到首页或用户中心
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);

    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 步骤内容
  const steps = [
    {
      title: '基本信息',
      content: (
        <>
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { pattern: /^[a-zA-Z0-9_]{4,50}$/, message: '用户名为4-50位，只能包含字母、数字、下划线' },
              {
                validator: async (_, value) => {
                  if (value && value.length >= 4) {
                    await checkAvailability('username', value);
                  }
                }
              }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名 (4-50位字符)"
              size="large"
            />
          </Form.Item>

          <div style={{ marginBottom: 24 }}>
            <Button.Group style={{ width: '100%' }}>
              <Button
                type={registerType === 'email' ? 'primary' : 'default'}
                onClick={() => setRegisterType('email')}
                style={{ width: '50%' }}
              >
                邮箱注册
              </Button>
              <Button
                type={registerType === 'phone' ? 'primary' : 'default'}
                onClick={() => setRegisterType('phone')}
                style={{ width: '50%' }}
              >
                手机注册
              </Button>
            </Button.Group>
          </div>

          {registerType === 'email' ? (
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' },
                {
                  validator: async (_, value) => {
                    if (value && value.includes('@')) {
                      await checkAvailability('email', value);
                    }
                  }
                }
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="邮箱地址"
                size="large"
              />
            </Form.Item>
          ) : (
            <Form.Item
              name="phone"
              rules={[
                { required: true, message: '请输入手机号' },
                { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
                {
                  validator: async (_, value) => {
                    if (value && value.length === 11) {
                      await checkAvailability('phone', value);
                    }
                  }
                }
              ]}
            >
              <Input
                prefix={<PhoneOutlined />}
                placeholder="手机号"
                size="large"
              />
            </Form.Item>
          )}
        </>
      )
    },
    {
      title: '设置密码',
      content: (
        <>
          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8位' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
                message: '密码必须包含大小写字母和数字'
              }
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码 (至少8位，含大小写字母和数字)"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirm"
            dependencies={['password']}
            hasFeedback
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
              size="large"
            />
          </Form.Item>
        </>
      )
    },
    {
      title: '验证',
      content: (
        <>
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
              size="large"
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

          <Form.Item
            name="agree"
            valuePropName="checked"
            rules={[
              {
                validator: (_, value) =>
                  value ? Promise.resolve() : Promise.reject(new Error('请同意服务条款和隐私政策')),
              },
            ]}
          >
            <Checkbox>
              我已阅读并同意{' '}
              <Link href="/terms">服务条款</Link>
              {' '}和{' '}
              <Link href="/privacy">隐私政策</Link>
            </Checkbox>
          </Form.Item>
        </>
      )
    }
  ];

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h1>注册账号</h1>
          <p>加入Platform，开启学习之旅</p>
        </div>

        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          {steps.map((step) => (
            <Step key={step.title} title={step.title} />
          ))}
        </Steps>

        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <div className="steps-content">
            {steps[currentStep].content}
          </div>

          <div className="steps-action">
            {currentStep > 0 && (
              <Button
                style={{ marginRight: 8 }}
                onClick={() => setCurrentStep(currentStep - 1)}
              >
                上一步
              </Button>
            )}

            {currentStep < steps.length - 1 && (
              <Button
                type="primary"
                onClick={async () => {
                  try {
                    // 验证当前步骤的字段
                    const fieldsToValidate = currentStep === 0
                      ? ['username', registerType === 'email' ? 'email' : 'phone']
                      : ['password', 'confirm'];

                    await form.validateFields(fieldsToValidate);
                    setCurrentStep(currentStep + 1);
                  } catch (error) {
                    // 验证失败，不进行下一步
                  }
                }}
              >
                下一步
              </Button>
            )}

            {currentStep === steps.length - 1 && (
              <Button type="primary" htmlType="submit" loading={loading}>
                完成注册
              </Button>
            )}
          </div>
        </Form>

        <div className="register-footer">
          <span>已有账号？</span>
          <Link href="/login">立即登录</Link>
        </div>
      </div>
    </div>
  );
}
