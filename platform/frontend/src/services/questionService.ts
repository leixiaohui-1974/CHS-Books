/**
 * 题目练习服务
 */

import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ========================================
// 类型定义
// ========================================

export interface Question {
  id: number;
  title: string;
  content: string;
  question_type: string;
  difficulty: string;
  knowledge_point_id?: number;
  chapter_id?: number;
  subject_id?: number;
  options?: Record<string, string>;
  explanation?: string;
  score: number;
  time_limit?: number;
  tags?: string[];
  submit_count: number;
  correct_count: number;
  accuracy_rate: number;
  average_time: number;
  is_active: boolean;
  created_at: string;
}

export interface CreateQuestionData {
  title: string;
  content: string;
  question_type: string;
  difficulty: string;
  correct_answer: string;
  knowledge_point_id?: number;
  chapter_id?: number;
  subject_id?: number;
  options?: Record<string, string>;
  explanation?: string;
  score?: number;
  time_limit?: number;
  tags?: string[];
}

export interface SubmitAnswerData {
  question_id: number;
  answer: string;
  time_spent: number;
  exercise_id?: number;
  code?: string;
}

export interface Submission {
  id: number;
  question_id: number;
  is_correct: boolean;
  score: number;
  status: string;
  judge_result?: Record<string, any>;
  time_spent: number;
  submitted_at: string;
}

export interface WrongQuestion {
  id: number;
  question_id: number;
  question_title: string;
  question_content: string;
  question_type: string;
  difficulty: string;
  wrong_count: number;
  correct_count: number;
  is_mastered: boolean;
  notes?: string;
  last_wrong_at: string;
}

export interface QuestionSet {
  id: number;
  title: string;
  description?: string;
  set_type: string;
  total_questions: number;
  total_score: number;
  pass_score: number;
  time_limit?: number;
  attempt_count: number;
  average_score: number;
  created_at: string;
}

export interface CreateQuestionSetData {
  title: string;
  question_ids: number[];
  description?: string;
  set_type?: string;
  subject_id?: number;
  chapter_id?: number;
  total_score?: number;
  pass_score?: number;
  time_limit?: number;
}

// ========================================
// 题目服务类
// ========================================

class QuestionService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/v1/questions`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.api.interceptors.request.use(
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
  }

  // ========================================
  // 题目管理
  // ========================================

  async createQuestion(data: CreateQuestionData): Promise<Question> {
    const response = await this.api.post('/', data);
    return response.data;
  }

  async getQuestions(params?: {
    question_type?: string;
    difficulty?: string;
    knowledge_point_id?: number;
    chapter_id?: number;
    subject_id?: number;
    tags?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total: number; questions: Question[] }> {
    const response = await this.api.get('/', { params });
    return response.data;
  }

  async getQuestion(id: number): Promise<Question> {
    const response = await this.api.get(`/${id}`);
    return response.data;
  }

  async updateQuestion(id: number, data: Partial<CreateQuestionData>): Promise<void> {
    await this.api.put(`/${id}`, data);
  }

  async deleteQuestion(id: number): Promise<void> {
    await this.api.delete(`/${id}`);
  }

  // ========================================
  // 提交和判题
  // ========================================

  async submitAnswer(data: SubmitAnswerData): Promise<Submission> {
    const response = await this.api.post('/submissions', data);
    return response.data;
  }

  async getSubmissions(params?: {
    question_id?: number;
    exercise_id?: number;
    limit?: number;
  }): Promise<{ submissions: Submission[] }> {
    const response = await this.api.get('/submissions', { params });
    return response.data;
  }

  // ========================================
  // 错题本
  // ========================================

  async getWrongQuestions(params?: {
    is_mastered?: boolean;
    limit?: number;
  }): Promise<WrongQuestion[]> {
    const response = await this.api.get('/wrong-questions', { params });
    return response.data;
  }

  async addWrongQuestionNote(questionId: number, notes: string): Promise<void> {
    await this.api.post(`/wrong-questions/${questionId}/note`, { notes });
  }

  async removeWrongQuestion(questionId: number): Promise<void> {
    await this.api.delete(`/wrong-questions/${questionId}`);
  }

  // ========================================
  // 题集管理
  // ========================================

  async createQuestionSet(data: CreateQuestionSetData): Promise<{ message: string; question_set_id: number }> {
    const response = await this.api.post('/question-sets', data);
    return response.data;
  }

  async getQuestionSets(params?: {
    set_type?: string;
    subject_id?: number;
    chapter_id?: number;
    limit?: number;
  }): Promise<{ question_sets: QuestionSet[] }> {
    const response = await this.api.get('/question-sets', { params });
    return response.data;
  }

  async getQuestionSet(id: number): Promise<QuestionSet & { question_ids: number[] }> {
    const response = await this.api.get(`/question-sets/${id}`);
    return response.data;
  }

  async getQuestionsBySet(id: number): Promise<{ questions: Question[] }> {
    const response = await this.api.get(`/question-sets/${id}/questions`);
    return response.data;
  }
}

export const questionService = new QuestionService();
