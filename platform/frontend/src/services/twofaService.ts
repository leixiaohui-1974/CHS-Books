/**
 * 双因素认证服务
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/2fa`,
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
export interface TwoFAStatus {
  enabled: boolean;
  method: string | null;
  backup_codes_count: number;
}

export interface Enable2FAStartResponse {
  secret: string;
  qr_code: string;  // Base64 QR code image
  backup_codes: string[];
  message: string;
}

export interface Enable2FAConfirmRequest {
  secret: string;
  code: string;
  backup_codes: string[];
}

export interface Verify2FARequest {
  code: string;
  use_backup?: boolean;
}

export interface RegenerateBackupCodesResponse {
  backup_codes: string[];
  message: string;
}

// 2FA服务类
class TwoFAService {
  /**
   * 获取2FA状态
   */
  async getStatus(): Promise<TwoFAStatus> {
    const response = await apiClient.get('/status');
    return response.data;
  }

  /**
   * 开始启用2FA流程
   * 返回密钥、二维码和备用码
   */
  async startEnable(): Promise<Enable2FAStartResponse> {
    const response = await apiClient.post('/enable/start');
    return response.data;
  }

  /**
   * 确认启用2FA
   * 需要输入验证码确认
   */
  async confirmEnable(data: Enable2FAConfirmRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/enable/confirm', data);
    return response.data;
  }

  /**
   * 禁用2FA
   * 需要输入验证码确认
   */
  async disable(data: Verify2FARequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/disable', data);
    return response.data;
  }

  /**
   * 验证2FA代码
   */
  async verify(data: Verify2FARequest): Promise<{ valid: boolean; message: string }> {
    const response = await apiClient.post('/verify', data);
    return response.data;
  }

  /**
   * 重新生成备用码
   */
  async regenerateBackupCodes(code: string): Promise<RegenerateBackupCodesResponse> {
    const response = await apiClient.post('/backup-codes/regenerate', {
      code,
      use_backup: false
    });
    return response.data;
  }

  /**
   * 获取备用码数量
   */
  async getBackupCodesCount(): Promise<{ count: number; warning: boolean }> {
    const response = await apiClient.get('/backup-codes/count');
    return response.data;
  }
}

// 导出单例
export const twofaService = new TwoFAService();
export default twofaService;
