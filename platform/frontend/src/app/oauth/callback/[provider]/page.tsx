'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams, useParams } from 'next/navigation';
import { Spin, Result, Button } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { oauthService, OAuthProvider } from '@/services/oauthService';
import { useAuth } from '@/contexts/AuthContext';

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams();
  const { login } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      // 1. 获取参数
      const provider = params.provider as OAuthProvider;
      const code = searchParams?.get('code');
      const state = searchParams?.get('state');
      const error_param = searchParams?.get('error');

      // 2. 检查是否有错误
      if (error_param) {
        setError(`OAuth授权失败: ${error_param}`);
        setLoading(false);
        return;
      }

      // 3. 验证参数
      if (!code || !state) {
        setError('缺少必要的回调参数');
        setLoading(false);
        return;
      }

      // 4. 验证state（防CSRF）
      if (!oauthService.validateState(provider, state)) {
        setError('无效的state参数，可能是CSRF攻击');
        setLoading(false);
        return;
      }

      // 5. 调用后端处理OAuth回调
      const result = await oauthService.handleCallback(provider, code, state);

      // 6. 清除state
      oauthService.clearState(provider);

      // 7. 刷新用户信息
      await login();

      // 8. 成功
      setSuccess(true);
      setLoading(false);

      // 9. 延迟跳转
      setTimeout(() => {
        if (result.is_new_user) {
          // 新用户跳转到欢迎页或个人信息完善页
          router.push('/profile?welcome=true');
        } else {
          // 老用户跳转到dashboard
          router.push('/dashboard');
        }
      }, 1500);

    } catch (err: any) {
      console.error('OAuth回调处理失败:', err);
      setError(err.response?.data?.detail || err.message || 'OAuth登录失败');
      setLoading(false);
      
      // 清除state
      const provider = params.provider as OAuthProvider;
      oauthService.clearState(provider);
    }
  };

  const getProviderName = (provider: string): string => {
    const names: Record<string, string> = {
      github: 'GitHub',
      google: 'Google',
      wechat: '微信'
    };
    return names[provider] || provider;
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: '24px'
      }}>
        <Spin 
          indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
          size="large"
        />
        <div style={{ fontSize: 18, color: '#666' }}>
          正在完成{getProviderName(params.provider as string)}登录...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '24px'
      }}>
        <Result
          status="error"
          title="登录失败"
          subTitle={error}
          extra={[
            <Button 
              type="primary" 
              key="retry" 
              onClick={() => router.push('/login')}
            >
              返回登录
            </Button>
          ]}
        />
      </div>
    );
  }

  if (success) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '24px'
      }}>
        <Result
          status="success"
          title="登录成功！"
          subTitle="正在跳转..."
        />
      </div>
    );
  }

  return null;
}
