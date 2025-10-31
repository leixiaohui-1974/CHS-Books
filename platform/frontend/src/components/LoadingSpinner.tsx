import React from 'react';
import { Spin, SpinProps } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps extends SpinProps {
  fullscreen?: boolean;
  text?: string;
}

/**
 * 加载动画组件
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  fullscreen = false,
  text = '加载中...',
  size = 'large',
  ...restProps
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 48 : 24 }} spin />;

  if (fullscreen) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          zIndex: 9999,
        }}
      >
        <Spin indicator={antIcon} size={size} {...restProps} />
        {text && (
          <div
            style={{
              marginTop: 20,
              fontSize: 16,
              color: '#666',
            }}
          >
            {text}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '50px 0',
      }}
    >
      <Spin indicator={antIcon} size={size} tip={text} {...restProps} />
    </div>
  );
};

export default LoadingSpinner;

/**
 * 页面加载组件
 */
export const PageLoading: React.FC = () => (
  <LoadingSpinner fullscreen text="页面加载中..." />
);

/**
 * 内容加载组件
 */
export const ContentLoading: React.FC<{ text?: string }> = ({ text = '加载中...' }) => (
  <LoadingSpinner text={text} />
);

/**
 * 按钮加载组件
 */
export const ButtonLoading: React.FC = () => (
  <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} size="small" />
);
