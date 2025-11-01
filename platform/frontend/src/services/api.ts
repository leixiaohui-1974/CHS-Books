/**
 * API客户端
 * 封装所有后端API请求
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token过期，尝试刷新
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken
          })
          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)
          
          // 重试原请求
          error.config.headers.Authorization = `Bearer ${access_token}`
          return apiClient.request(error.config)
        } catch (refreshError) {
          // 刷新失败，清除token并跳转登录
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// ========================================
// API接口函数
// ========================================

export const authAPI = {
  // 注册
  register: async (data: { email: string; username: string; password: string; full_name?: string }) => {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  // 登录
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  // 登出
  logout: async () => {
    const response = await apiClient.post('/auth/logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    return response.data
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },
}

export const booksAPI = {
  // 获取书籍列表
  getBooks: async (params?: {
    page?: number
    page_size?: number
    status?: string
    difficulty?: string
    tag?: string
    search?: string
  }) => {
    const response = await apiClient.get('/books', { params })
    return response.data
  },

  // 获取书籍详情
  getBook: async (bookIdOrSlug: string | number) => {
    const response = await apiClient.get(`/books/${bookIdOrSlug}`)
    return response.data
  },

  // 获取书籍章节
  getBookChapters: async (bookId: number) => {
    const response = await apiClient.get(`/books/${bookId}/chapters`)
    return response.data
  },

  // 注册学习
  enrollBook: async (bookId: number) => {
    const response = await apiClient.post(`/books/${bookId}/enroll`)
    return response.data
  },

  // 评价书籍
  rateBook: async (bookId: number, rating: number, comment?: string) => {
    const response = await apiClient.post(`/books/${bookId}/rate`, { rating, comment })
    return response.data
  },
}

export const toolsAPI = {
  // 执行工具
  executeTool: async (caseId: number, inputParams: Record<string, any>) => {
    const response = await apiClient.post('/tools/execute', {
      case_id: caseId,
      input_params: inputParams,
    })
    return response.data
  },

  // 获取执行结果
  getToolResult: async (taskId: string) => {
    const response = await apiClient.get(`/tools/result/${taskId}`)
    return response.data
  },

  // 获取执行历史
  getToolHistory: async (caseId?: number, page: number = 1, pageSize: number = 20) => {
    const response = await apiClient.get('/tools/history', {
      params: { case_id: caseId, page, page_size: pageSize }
    })
    return response.data
  },

  // 保存执行结果
  saveToolExecution: async (taskId: string, name?: string) => {
    const response = await apiClient.post(`/tools/${taskId}/save`, { name })
    return response.data
  },
}

export const aiAPI = {
  // AI对话
  chat: async (message: string, context?: Record<string, any>) => {
    const response = await apiClient.post('/ai/chat', { message, context })
    return response.data
  },
}

export const progressAPI = {
  // 获取书籍学习进度
  getBookProgress: async (bookId: number) => {
    const response = await apiClient.get(`/progress/books/${bookId}`)
    return response.data
  },
}

export default apiClient
