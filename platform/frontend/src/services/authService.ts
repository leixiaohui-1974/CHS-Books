/**
 * 认证服务
 * 提供所有认证相关的API调用
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理401错误
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 如果是401错误且不是refresh请求，尝试刷新token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authService.refreshToken(refreshToken);
          const { access_token } = response;
          
          localStorage.setItem('access_token', access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除token并跳转登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// 类型定义
export interface RegisterData {
  username: string;
  email?: string;
  phone?: string;
  password: string;
  verification_code: string;
}

export interface LoginData {
  identifier: string;
  password: string;
  remember_me?: boolean;
  device_id?: string;
  device_name?: string;
}

export interface SMSLoginData {
  phone: string;
  code: string;
  device_id?: string;
  device_name?: string;
}

export interface SendCodeData {
  type: 'register' | 'login' | 'reset_password' | 'change_email' | 'change_phone';
  recipient: string;
  method: 'email' | 'sms';
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
}

export interface ForgotPasswordData {
  email: string;
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
}

export interface UpdateUserInfoData {
  full_name?: string;
  avatar_url?: string;
  bio?: string;
}

export interface UserInfo {
  id: number;
  username: string;
  email?: string;
  phone?: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  role: string;
  status: string;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  is_premium: boolean;
  premium_expires_at?: string;
  total_learning_time: number;
  login_count: number;
  last_login_at?: string;
  created_at: string;
}

export interface AuthResponse {
  user_id: number;
  username: string;
  email?: string;
  avatar_url?: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  requires_2fa?: boolean;
  temp_token?: string;
}

// 认证服务类
class AuthService {
  /**
   * 用户注册
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post('/register', data);
    const authData = response.data;
    
    // 保存token
    this.saveTokens(authData.access_token, authData.refresh_token);
    
    return authData;
  }

  /**
   * 用户登录
   */
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await apiClient.post('/login', data);
    const authData = response.data;
    
    // 保存token
    this.saveTokens(authData.access_token, authData.refresh_token);
    
    return authData;
  }

  /**
   * 短信验证码登录
   */
  async smsLogin(data: SMSLoginData): Promise<AuthResponse> {
    const response = await apiClient.post('/sms-login', data);
    const authData = response.data;
    
    // 保存token
    this.saveTokens(authData.access_token, authData.refresh_token);
    
    return authData;
  }

  /**
   * 登出
   */
  async logout(allDevices: boolean = false): Promise<void> {
    try {
      await apiClient.post('/logout', { all_devices: allDevices });
    } finally {
      this.clearTokens();
    }
  }

  /**
   * 刷新Token
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string; expires_in: number }> {
    const response = await apiClient.post('/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  /**
   * 发送验证码
   */
  async sendCode(data: SendCodeData): Promise<{ success: boolean; message: string; expires_in: number }> {
    const response = await apiClient.post('/send-code', data);
    return response.data;
  }

  /**
   * 修改密码
   */
  async changePassword(data: ChangePasswordData): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.put('/change-password', data);
    return response.data;
  }

  /**
   * 忘记密码
   */
  async forgotPassword(data: ForgotPasswordData): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/forgot-password', data);
    return response.data;
  }

  /**
   * 重置密码
   */
  async resetPassword(data: ResetPasswordData): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/reset-password', data);
    return response.data;
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<UserInfo> {
    const response = await apiClient.get('/me');
    return response.data;
  }

  /**
   * 更新当前用户信息
   */
  async updateCurrentUser(data: UpdateUserInfoData): Promise<UserInfo> {
    const response = await apiClient.put('/me', data);
    return response.data;
  }

  /**
   * 检查可用性
   */
  async checkAvailability(field: 'username' | 'email' | 'phone', value: string): Promise<{ available: boolean; message?: string }> {
    const response = await apiClient.get('/check-availability', {
      params: { field, value }
    });
    return response.data;
  }

  /**
   * 保存Token到localStorage
   */
  private saveTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  /**
   * 清除Token
   */
  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  /**
   * 获取访问Token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * 获取刷新Token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }
}

// 导出单例
export const authService = new AuthService();
export default authService;
