'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authService } from '@/services/authService';
import { Spin } from 'antd';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * 路由守卫组件
 * 保护需要认证的页面
 */
export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  // 不需要认证的页面
  const publicRoutes = ['/login', '/register', '/forgot-password', '/'];

  useEffect(() => {
    const checkAuth = async () => {
      // 如果是公开路由，直接显示
      if (publicRoutes.some(route => pathname?.startsWith(route))) {
        setLoading(false);
        setAuthenticated(true);
        return;
      }

      // 检查是否有token
      const isAuth = authService.isAuthenticated();
      
      if (!isAuth) {
        // 未登录，跳转到登录页
        router.push(`/login?redirect=${pathname}`);
        return;
      }

      try {
        // 验证token有效性
        await authService.getCurrentUser();
        setAuthenticated(true);
      } catch (error) {
        // token无效，跳转到登录页
        router.push(`/login?redirect=${pathname}`);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [pathname, router]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return <>{children}</>;
}
