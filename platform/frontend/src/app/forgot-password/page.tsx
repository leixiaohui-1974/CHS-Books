'use client';

import React, { useState } from 'react';
import { Form, Input, Button, message, Result } from 'antd';
import { MailOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { authService, ForgotPasswordData } from '@/services/authService';
import './forgot-password.css';

export default function ForgotPasswordPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);

      const data: ForgotPasswordData = {
        email: values.email
      };

      await authService.forgotPassword(data);
      setSuccess(true);
      message.success('密码重置邮件已发送');

    } catch (error: any) {
      message.error(error.response?.data?.detail || '发送失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="forgot-password-container">
        <div className="forgot-password-card">
          <Result
            status="success"
            title="邮件已发送！"
            subTitle="我们已向您的邮箱发送了密码重置链接，请查收邮件并按照提示重置密码。"
            extra={[
              <Link href="/login" key="login">
                <Button type="primary">返回登录</Button>
              </Link>
            ]}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <div className="forgot-password-header">
          <h1>忘记密码</h1>
          <p>输入您的邮箱地址，我们将发送密码重置链接</p>
        </div>

        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱地址"
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
              发送重置链接
            </Button>
          </Form.Item>
        </Form>

        <div className="forgot-password-footer">
          <Link href="/login">
            <ArrowLeftOutlined /> 返回登录
          </Link>
        </div>
      </div>
    </div>
  );
}
