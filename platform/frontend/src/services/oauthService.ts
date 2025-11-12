/**
 * OAuth服务
 * 提供第三方登录API调用
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/oauth`,
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

// 类型定义
export interface OAuthUrlResponse {
  auth_url: string;
  state: string;
}

export interface OAuthLoginResponse {
  user_id: number;
  username: string;
  email?: string;
  avatar_url?: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
  is_new_user: boolean;
}

export interface OAuthAccountInfo {
  provider: string;
  provider_user_id: string;
  created_at: string;
}

export type OAuthProvider = 'github' | 'google' | 'wechat';

// OAuth服务类
class OAuthService {
  /**
   * 获取GitHub OAuth授权URL
   */
  async getGithubAuthUrl(): Promise<OAuthUrlResponse> {
    const response = await apiClient.get('/github/url');
    return response.data;
  }

  /**
   * 处理GitHub OAuth回调
   */
  async githubCallback(code: string, state: string): Promise<OAuthLoginResponse> {
    const response = await apiClient.post('/github/callback', { code, state });
    
    // 保存token
    this.saveTokens(response.data.access_token, response.data.refresh_token);
    
    return response.data;
  }

  /**
   * 获取Google OAuth授权URL
   */
  async getGoogleAuthUrl(): Promise<OAuthUrlResponse> {
    const response = await apiClient.get('/google/url');
    return response.data;
  }

  /**
   * 处理Google OAuth回调
   */
  async googleCallback(code: string, state: string): Promise<OAuthLoginResponse> {
    const response = await apiClient.post('/google/callback', { code, state });
    
    // 保存token
    this.saveTokens(response.data.access_token, response.data.refresh_token);
    
    return response.data;
  }

  /**
   * 获取微信OAuth授权URL
   */
  async getWechatAuthUrl(): Promise<OAuthUrlResponse> {
    const response = await apiClient.get('/wechat/url');
    return response.data;
  }

  /**
   * 处理微信OAuth回调
   */
  async wechatCallback(code: string, state: string): Promise<OAuthLoginResponse> {
    const response = await apiClient.post('/wechat/callback', { code, state });
    
    // 保存token
    this.saveTokens(response.data.access_token, response.data.refresh_token);
    
    return response.data;
  }

  /**
   * 获取OAuth授权URL（通用方法）
   */
  async getAuthUrl(provider: OAuthProvider): Promise<OAuthUrlResponse> {
    switch (provider) {
      case 'github':
        return this.getGithubAuthUrl();
      case 'google':
        return this.getGoogleAuthUrl();
      case 'wechat':
        return this.getWechatAuthUrl();
      default:
        throw new Error(`不支持的OAuth提供商: ${provider}`);
    }
  }

  /**
   * 处理OAuth回调（通用方法）
   */
  async handleCallback(
    provider: OAuthProvider,
    code: string,
    state: string
  ): Promise<OAuthLoginResponse> {
    switch (provider) {
      case 'github':
        return this.githubCallback(code, state);
      case 'google':
        return this.googleCallback(code, state);
      case 'wechat':
        return this.wechatCallback(code, state);
      default:
        throw new Error(`不支持的OAuth提供商: ${provider}`);
    }
  }

  /**
   * 获取用户的OAuth账号列表
   */
  async getOAuthAccounts(): Promise<OAuthAccountInfo[]> {
    const response = await apiClient.get('/accounts');
    return response.data;
  }

  /**
   * 绑定OAuth账号
   */
  async bindAccount(
    provider: OAuthProvider,
    code: string,
    state: string
  ): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post(`/bind/${provider}`, { code, state });
    return response.data;
  }

  /**
   * 解绑OAuth账号
   */
  async unbindAccount(
    provider: OAuthProvider
  ): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/unbind/${provider}`);
    return response.data;
  }

  /**
   * 发起OAuth登录流程
   * 
   * @param provider OAuth提供商
   * @returns Promise<void>
   */
  async startOAuthLogin(provider: OAuthProvider): Promise<void> {
    try {
      // 1. 获取授权URL
      const { auth_url, state } = await this.getAuthUrl(provider);
      
      // 2. 保存state到sessionStorage（用于回调验证）
      sessionStorage.setItem(`oauth_state_${provider}`, state);
      
      // 3. 跳转到OAuth授权页面
      window.location.href = auth_url;
    } catch (error) {
      console.error(`OAuth登录失败 (${provider}):`, error);
      throw error;
    }
  }

  /**
   * 验证OAuth state参数
   */
  validateState(provider: OAuthProvider, state: string): boolean {
    const savedState = sessionStorage.getItem(`oauth_state_${provider}`);
    return savedState === state;
  }

  /**
   * 清除OAuth state
   */
  clearState(provider: OAuthProvider): void {
    sessionStorage.removeItem(`oauth_state_${provider}`);
  }

  /**
   * 保存Token到localStorage
   */
  private saveTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }
}

// 导出单例
export const oauthService = new OAuthService();
export default oauthService;
