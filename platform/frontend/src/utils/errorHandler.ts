import { message } from 'antd';
import axios, { AxiosError } from 'axios';

/**
 * API错误接口
 */
interface ApiError {
  error?: string;
  message?: string;
  detail?: string | { [key: string]: any };
  status?: number;
}

/**
 * 处理API错误
 */
export const handleApiError = (error: unknown): string => {
  // Axios错误
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    
    // 网络错误
    if (!axiosError.response) {
      const errorMsg = '网络连接失败，请检查网络设置';
      message.error(errorMsg);
      return errorMsg;
    }

    const { status, data } = axiosError.response;
    
    // 根据HTTP状态码处理
    switch (status) {
      case 400:
        const msg400 = data?.detail || data?.message || '请求参数错误';
        message.error(msg400);
        return msg400;
      
      case 401:
        message.error('未登录或登录已过期，请重新登录');
        // 可以在这里触发跳转到登录页
        setTimeout(() => {
          window.location.href = '/login';
        }, 1000);
        return '未登录';
      
      case 403:
        message.error('没有权限访问此资源');
        return '无权限';
      
      case 404:
        const msg404 = '请求的资源不存在';
        message.error(msg404);
        return msg404;
      
      case 429:
        message.warning('请求过于频繁，请稍后再试');
        return '请求限流';
      
      case 500:
        message.error('服务器内部错误，请稍后再试');
        return '服务器错误';
      
      case 503:
        message.error('服务暂时不可用，请稍后再试');
        return '服务不可用';
      
      default:
        const defaultMsg = data?.message || data?.detail || '请求失败';
        message.error(defaultMsg);
        return defaultMsg;
    }
  }

  // 其他类型错误
  if (error instanceof Error) {
    message.error(error.message);
    return error.message;
  }

  // 未知错误
  const unknownMsg = '未知错误';
  message.error(unknownMsg);
  return unknownMsg;
};

/**
 * 验证表单字段错误
 */
export const getFieldError = (errors: any, field: string): string | undefined => {
  if (!errors || !errors[field]) return undefined;
  
  const fieldErrors = errors[field];
  if (Array.isArray(fieldErrors)) {
    return fieldErrors[0];
  }
  
  return fieldErrors;
};

/**
 * 显示成功消息
 */
export const showSuccess = (msg: string = '操作成功') => {
  message.success(msg);
};

/**
 * 显示警告消息
 */
export const showWarning = (msg: string) => {
  message.warning(msg);
};

/**
 * 显示信息消息
 */
export const showInfo = (msg: string) => {
  message.info(msg);
};

/**
 * 记录错误到控制台（开发模式）
 */
export const logError = (error: unknown, context?: string) => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);
  }
};

/**
 * 重试函数
 */
export const retryRequest = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // 如果是最后一次尝试，直接抛出错误
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // 等待后重试
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
    }
  }
  
  throw lastError;
};

/**
 * 防抖错误处理
 */
let errorTimeout: NodeJS.Timeout | null = null;

export const debouncedError = (msg: string, delay: number = 500) => {
  if (errorTimeout) {
    clearTimeout(errorTimeout);
  }
  
  errorTimeout = setTimeout(() => {
    message.error(msg);
    errorTimeout = null;
  }, delay);
};
