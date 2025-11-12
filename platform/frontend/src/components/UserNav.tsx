'use client';

import React from 'react';
import { Avatar, Dropdown, Space, Badge } from 'antd';
import type { MenuProps } from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DashboardOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

/**
 * 用户导航组件
 * 显示在顶部导航栏的用户菜单
 */
export default function UserNav() {
  const router = useRouter();
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <Space>
        <a
          href="/login"
          style={{ color: '#fff', textDecoration: 'none' }}
        >
          登录
        </a>
        <a
          href="/register"
          style={{
            color: '#fff',
            textDecoration: 'none',
            padding: '4px 16px',
            background: '#1890ff',
            borderRadius: '4px'
          }}
        >
          注册
        </a>
      </Space>
    );
  }

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'username',
      label: (
        <div style={{ padding: '8px 0' }}>
          <div style={{ fontWeight: 600, fontSize: 16 }}>
            {user.username}
          </div>
          {user.email && (
            <div style={{ fontSize: 12, color: '#999' }}>
              {user.email}
            </div>
          )}
        </div>
      ),
      disabled: true
    },
    {
      type: 'divider'
    },
    {
      key: 'dashboard',
      label: '学习中心',
      icon: <DashboardOutlined />,
      onClick: () => router.push('/dashboard')
    },
    {
      key: 'profile',
      label: '个人中心',
      icon: <UserOutlined />,
      onClick: () => router.push('/profile')
    },
    {
      key: 'achievements',
      label: '成就',
      icon: <TrophyOutlined />,
      onClick: () => router.push('/achievements')
    },
    {
      type: 'divider'
    },
    {
      key: 'settings',
      label: '设置',
      icon: <SettingOutlined />,
      onClick: () => router.push('/settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
      danger: true
    }
  ];

  return (
    <Dropdown menu={{ items: menuItems }} placement="bottomRight">
      <Space style={{ cursor: 'pointer' }}>
        <Badge
          dot={!user.is_verified}
          offset={[-5, 5]}
        >
          <Avatar
            src={user.avatar_url}
            icon={<UserOutlined />}
            style={{ backgroundColor: '#1890ff' }}
          />
        </Badge>
        <span style={{ color: '#fff' }}>
          {user.full_name || user.username}
        </span>
      </Space>
    </Dropdown>
  );
}
