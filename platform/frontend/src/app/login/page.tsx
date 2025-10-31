'use client'

import React, { useState } from 'react'
import { Layout, Card, Form, Input, Button, Checkbox, Divider, Typography, message, Tabs } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, GithubOutlined, WechatOutlined } from '@ant-design/icons'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const { Content } = Layout
const { Title, Text, Paragraph } = Typography

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const onLoginFinish = async (values: any) => {
    setLoading(true)
    try {
      // TODO: 调用登录API
      console.log('登录:', values)
      
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      message.success('登录成功！')
      router.push('/books')
    } catch (error) {
      message.error('登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const onRegisterFinish = async (values: any) => {
    setLoading(true)
    try {
      // TODO: 调用注册API
      console.log('注册:', values)
      
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      message.success('注册成功！请登录')
    } catch (error) {
      message.error('注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleSocialLogin = (provider: string) => {
    message.info(`${provider} 登录功能开发中`)
  }

  return (
    <Layout style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Content style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        padding: '50px 20px'
      }}>
        <Card style={{ width: '100%', maxWidth: '500px', borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
          {/* Logo和标题 */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <Title level={2} style={{ marginBottom: '8px' }}>
              Engineering Learning Platform
            </Title>
            <Paragraph type="secondary">
              智能工程教学平台
            </Paragraph>
          </div>

          {/* 登录/注册选项卡 */}
          <Tabs
            defaultActiveKey="login"
            centered
            items={[
              {
                key: 'login',
                label: '登录',
                children: (
                  <Form
                    name="login"
                    initialValues={{ remember: true }}
                    onFinish={onLoginFinish}
                    size="large"
                  >
                    <Form.Item
                      name="username"
                      rules={[{ required: true, message: '请输入用户名或邮箱' }]}
                    >
                      <Input 
                        prefix={<UserOutlined />} 
                        placeholder="用户名或邮箱" 
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
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Form.Item name="remember" valuePropName="checked" noStyle>
                          <Checkbox>记住我</Checkbox>
                        </Form.Item>
                        <Link href="/forgot-password">
                          <Text type="secondary">忘记密码？</Text>
                        </Link>
                      </div>
                    </Form.Item>

                    <Form.Item>
                      <Button type="primary" htmlType="submit" block loading={loading}>
                        登录
                      </Button>
                    </Form.Item>

                    {/* 社交登录 */}
                    <Divider>其他登录方式</Divider>
                    <Space style={{ width: '100%', justifyContent: 'center' }}>
                      <Button 
                        icon={<GithubOutlined />} 
                        onClick={() => handleSocialLogin('GitHub')}
                      >
                        GitHub
                      </Button>
                      <Button 
                        icon={<WechatOutlined />} 
                        type="primary"
                        style={{ background: '#07c160', borderColor: '#07c160' }}
                        onClick={() => handleSocialLogin('微信')}
                      >
                        微信
                      </Button>
                    </Space>
                  </Form>
                )
              },
              {
                key: 'register',
                label: '注册',
                children: (
                  <Form
                    name="register"
                    onFinish={onRegisterFinish}
                    size="large"
                  >
                    <Form.Item
                      name="email"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '请输入有效的邮箱地址' }
                      ]}
                    >
                      <Input 
                        prefix={<MailOutlined />} 
                        placeholder="邮箱地址" 
                      />
                    </Form.Item>

                    <Form.Item
                      name="username"
                      rules={[
                        { required: true, message: '请输入用户名' },
                        { min: 3, message: '用户名至少3个字符' }
                      ]}
                    >
                      <Input 
                        prefix={<UserOutlined />} 
                        placeholder="用户名" 
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[
                        { required: true, message: '请输入密码' },
                        { min: 8, message: '密码至少8个字符' }
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined />}
                        placeholder="密码（至少8位）"
                      />
                    </Form.Item>

                    <Form.Item
                      name="confirm"
                      dependencies={['password']}
                      rules={[
                        { required: true, message: '请确认密码' },
                        ({ getFieldValue }) => ({
                          validator(_, value) {
                            if (!value || getFieldValue('password') === value) {
                              return Promise.resolve()
                            }
                            return Promise.reject(new Error('两次密码输入不一致'))
                          },
                        }),
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined />}
                        placeholder="确认密码"
                      />
                    </Form.Item>

                    <Form.Item
                      name="agreement"
                      valuePropName="checked"
                      rules={[
                        {
                          validator: (_, value) =>
                            value ? Promise.resolve() : Promise.reject(new Error('请阅读并同意用户协议')),
                        },
                      ]}
                    >
                      <Checkbox>
                        我已阅读并同意 <Link href="/terms">用户协议</Link> 和 <Link href="/privacy">隐私政策</Link>
                      </Checkbox>
                    </Form.Item>

                    <Form.Item>
                      <Button type="primary" htmlType="submit" block loading={loading}>
                        注册
                      </Button>
                    </Form.Item>
                  </Form>
                )
              }
            ]}
          />

          {/* 测试账号提示 */}
          <Card 
            size="small" 
            style={{ 
              marginTop: '16px', 
              background: '#f0f2f5',
              borderRadius: '4px'
            }}
          >
            <Text type="secondary" style={{ fontSize: '12px' }}>
              <strong>测试账号:</strong><br />
              管理员: admin@example.com / admin123<br />
              用户: student@example.com / password123
            </Text>
          </Card>
        </Card>
      </Content>
    </Layout>
  )
}
