'use client';

import React, { useEffect, useState } from 'react';
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  Steps,
  message,
  Alert,
  Divider,
  Space,
  Tag,
  Typography,
  List,
  Spin
} from 'antd';
import {
  LockOutlined,
  SafetyOutlined,
  QrcodeOutlined,
  KeyOutlined,
  CheckCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { twofaService, Enable2FAStartResponse } from '@/services/twofaService';
import './security.css';

const { Step } = Steps;
const { Title, Paragraph, Text } = Typography;

export default function SecuritySettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [backupCodesCount, setBackupCodesCount] = useState(0);
  
  // 启用2FA Modal
  const [enableModalVisible, setEnableModalVisible] = useState(false);
  const [enableStep, setEnableStep] = useState(0);
  const [enableData, setEnableData] = useState<Enable2FAStartResponse | null>(null);
  const [confirmForm] = Form.useForm();
  
  // 禁用2FA Modal
  const [disableModalVisible, setDisableModalVisible] = useState(false);
  const [disableForm] = Form.useForm();
  
  // 重新生成备用码 Modal
  const [regenerateModalVisible, setRegenerateModalVisible] = useState(false);
  const [newBackupCodes, setNewBackupCodes] = useState<string[]>([]);
  const [regenerateForm] = Form.useForm();

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const status = await twofaService.getStatus();
      setTwoFAEnabled(status.enabled);
      setBackupCodesCount(status.backup_codes_count);
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push('/login');
      } else {
        message.error('加载安全设置失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 开始启用2FA
  const handleStartEnable = async () => {
    try {
      setEnableModalVisible(true);
      setEnableStep(0);
      
      const data = await twofaService.startEnable();
      setEnableData(data);
      setEnableStep(1);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '启用失败');
      setEnableModalVisible(false);
    }
  };

  // 确认启用2FA
  const handleConfirmEnable = async (values: any) => {
    if (!enableData) return;

    try {
      await twofaService.confirmEnable({
        secret: enableData.secret,
        code: values.code,
        backup_codes: enableData.backup_codes
      });

      message.success('双因素认证已成功启用');
      setEnableModalVisible(false);
      setEnableData(null);
      confirmForm.resetFields();
      await loadStatus();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '验证码错误');
    }
  };

  // 禁用2FA
  const handleDisable = async (values: any) => {
    try {
      await twofaService.disable({
        code: values.code,
        use_backup: values.use_backup || false
      });

      message.success('双因素认证已禁用');
      setDisableModalVisible(false);
      disableForm.resetFields();
      await loadStatus();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '验证码错误');
    }
  };

  // 重新生成备用码
  const handleRegenerateBackupCodes = async (values: any) => {
    try {
      const result = await twofaService.regenerateBackupCodes(values.code);
      setNewBackupCodes(result.backup_codes);
      regenerateForm.resetFields();
      message.success(result.message);
      await loadStatus();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '验证码错误');
    }
  };

  // 下载备用码
  const downloadBackupCodes = (codes: string[]) => {
    const content = `Platform 双因素认证备用码\n生成时间: ${new Date().toLocaleString()}\n\n${codes.join('\n')}\n\n请妥善保管这些备用码，每个备用码只能使用一次。`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backup-codes-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="security-settings-container">
      <Title level={2}>安全设置</Title>
      <Paragraph>
        管理您的账号安全设置，启用双因素认证以提高账号安全性
      </Paragraph>

      <Card 
        title={
          <Space>
            <SafetyOutlined />
            双因素认证 (2FA)
          </Space>
        }
        extra={
          twoFAEnabled ? (
            <Tag icon={<CheckCircleOutlined />} color="success">
              已启用
            </Tag>
          ) : (
            <Tag color="default">未启用</Tag>
          )
        }
      >
        <Paragraph>
          双因素认证为您的账号添加额外的安全保护层。登录时除了密码外，还需要输入认证器应用生成的6位动态验证码。
        </Paragraph>

        {!twoFAEnabled ? (
          <div>
            <Alert
              message="建议启用双因素认证"
              description="启用双因素认证可以大大提高账号安全性，即使密码泄露，攻击者也无法登录您的账号。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Button 
              type="primary" 
              icon={<LockOutlined />}
              onClick={handleStartEnable}
            >
              启用双因素认证
            </Button>
          </div>
        ) : (
          <div>
            <Alert
              message="双因素认证已启用"
              description={`您的账号受到双因素认证保护。剩余备用码: ${backupCodesCount} 个`}
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            {backupCodesCount < 3 && (
              <Alert
                message="备用码不足"
                description="您的备用码数量较少，建议重新生成备用码。"
                type="warning"
                showIcon
                icon={<WarningOutlined />}
                style={{ marginBottom: 16 }}
              />
            )}

            <Space>
              <Button 
                icon={<KeyOutlined />}
                onClick={() => setRegenerateModalVisible(true)}
              >
                重新生成备用码
              </Button>
              <Button 
                danger
                onClick={() => setDisableModalVisible(true)}
              >
                禁用双因素认证
              </Button>
            </Space>
          </div>
        )}
      </Card>

      {/* 启用2FA Modal */}
      <Modal
        title="启用双因素认证"
        open={enableModalVisible}
        onCancel={() => {
          setEnableModalVisible(false);
          setEnableData(null);
          setEnableStep(0);
          confirmForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Steps current={enableStep} style={{ marginBottom: 24 }}>
          <Step title="准备" />
          <Step title="扫描二维码" />
          <Step title="验证" />
        </Steps>

        {enableStep === 0 && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>正在生成密钥和二维码...</p>
          </div>
        )}

        {enableStep === 1 && enableData && (
          <div>
            <Alert
              message="第1步：扫描二维码"
              description="使用认证器应用（如Google Authenticator、Microsoft Authenticator）扫描下方二维码"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <img 
                src={enableData.qr_code} 
                alt="QR Code" 
                style={{ maxWidth: '250px' }}
              />
            </div>

            <Divider>或手动输入密钥</Divider>

            <div style={{ marginBottom: 24 }}>
              <Text code copyable style={{ fontSize: 16 }}>
                {enableData.secret}
              </Text>
            </div>

            <Alert
              message="第2步：保存备用码"
              description="备用码用于在无法使用认证器时登录账号，请妥善保存"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <div className="backup-codes-container">
              {enableData.backup_codes.map((code, index) => (
                <Tag key={index} style={{ margin: 4, fontFamily: 'monospace' }}>
                  {code}
                </Tag>
              ))}
            </div>

            <Button
              block
              icon={<KeyOutlined />}
              onClick={() => downloadBackupCodes(enableData.backup_codes)}
              style={{ marginTop: 16, marginBottom: 24 }}
            >
              下载备用码
            </Button>

            <Alert
              message="第3步：验证"
              description="输入认证器应用显示的6位验证码"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form
              form={confirmForm}
              onFinish={handleConfirmEnable}
              layout="vertical"
            >
              <Form.Item
                name="code"
                label="验证码"
                rules={[
                  { required: true, message: '请输入验证码' },
                  { len: 6, message: '验证码为6位数字' },
                  { pattern: /^\d{6}$/, message: '验证码必须为数字' }
                ]}
              >
                <Input
                  prefix={<SafetyOutlined />}
                  placeholder="输入6位验证码"
                  maxLength={6}
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" block size="large">
                  确认启用
                </Button>
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>

      {/* 禁用2FA Modal */}
      <Modal
        title="禁用双因素认证"
        open={disableModalVisible}
        onCancel={() => {
          setDisableModalVisible(false);
          disableForm.resetFields();
        }}
        footer={null}
      >
        <Alert
          message="警告"
          description="禁用双因素认证会降低账号安全性，请谨慎操作"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Form
          form={disableForm}
          onFinish={handleDisable}
          layout="vertical"
        >
          <Form.Item
            name="code"
            label="请输入验证码以确认"
            rules={[{ required: true, message: '请输入验证码' }]}
          >
            <Input
              prefix={<SafetyOutlined />}
              placeholder="6位验证码或备用码"
              maxLength={9}
            />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%' }}>
              <Button onClick={() => setDisableModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" danger htmlType="submit">
                确认禁用
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 重新生成备用码 Modal */}
      <Modal
        title="重新生成备用码"
        open={regenerateModalVisible}
        onCancel={() => {
          setRegenerateModalVisible(false);
          setNewBackupCodes([]);
          regenerateForm.resetFields();
        }}
        footer={null}
        width={500}
      >
        {newBackupCodes.length === 0 ? (
          <>
            <Alert
              message="注意"
              description="重新生成后，旧的备用码将全部失效"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form
              form={regenerateForm}
              onFinish={handleRegenerateBackupCodes}
              layout="vertical"
            >
              <Form.Item
                name="code"
                label="请输入验证码以确认"
                rules={[
                  { required: true, message: '请输入验证码' },
                  { len: 6, message: '验证码为6位数字' }
                ]}
              >
                <Input
                  prefix={<SafetyOutlined />}
                  placeholder="输入6位验证码"
                  maxLength={6}
                />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  生成新备用码
                </Button>
              </Form.Item>
            </Form>
          </>
        ) : (
          <>
            <Alert
              message="新备用码已生成"
              description="请妥善保存这些备用码，每个备用码只能使用一次"
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <div className="backup-codes-container">
              {newBackupCodes.map((code, index) => (
                <Tag key={index} style={{ margin: 4, fontFamily: 'monospace' }}>
                  {code}
                </Tag>
              ))}
            </div>

            <Button
              block
              icon={<KeyOutlined />}
              onClick={() => downloadBackupCodes(newBackupCodes)}
              style={{ marginTop: 16 }}
            >
              下载备用码
            </Button>
          </>
        )}
      </Modal>
    </div>
  );
}
