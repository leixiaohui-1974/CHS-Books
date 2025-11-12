/**
 * 学习追踪服务
 */

import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ========================================
// 类型定义
// ========================================

export interface Subject {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  order: number;
}

export interface Chapter {
  id: number;
  subject_id: number;
  name: string;
  description?: string;
  order: number;
}

export interface KnowledgePoint {
  id: number;
  chapter_id: number;
  name: string;
  description?: string;
  difficulty: string;
  video_url?: string;
  reading_url?: string;
  exercise_count: number;
  order: number;
}

export interface Progress {
  id: number;
  knowledge_point_id: number;
  knowledge_point_name: string;
  mastery_level: string;
  mastery_score: number;
  study_time: number;
  practice_count: number;
  correct_count: number;
  wrong_count: number;
  accuracy: number;
  next_review_date?: string;
  last_studied_at?: string;
}

export interface DailyGoal {
  id: number;
  date: string;
  target_study_time: number;
  target_exercises: number;
  target_knowledge_points: number;
  actual_study_time: number;
  actual_exercises: number;
  actual_knowledge_points: number;
  completion_percentage: number;
  is_completed: boolean;
}

export interface LearningPath {
  id: number;
  name: string;
  description?: string;
  difficulty: string;
  progress_percentage: number;
  total_knowledge_points: number;
  completed_count: number;
  is_active: boolean;
}

export interface Achievement {
  id: number;
  name: string;
  title: string;
  description: string;
  icon?: string;
  type: string;
  requirement_value: number;
  points: number;
  rarity: string;
  is_unlocked: boolean;
  progress_value: number;
  progress_percentage: number;
  unlocked_at?: string;
}

export interface SummaryStats {
  total_knowledge_points: number;
  mastery_distribution: {
    not_started: number;
    learning: number;
    practicing: number;
    mastered: number;
    expert: number;
  };
  total_study_time: number;
  total_practice_count: number;
  total_correct: number;
  total_wrong: number;
  accuracy: number;
  recent_7_days: Array<{
    date: string;
    study_time: number;
    activities: number;
    exercises: number;
    average_score: number;
  }>;
  streak_days: number;
}

export interface DailyStats {
  date: string;
  study_time: number;
  sessions: number;
  activities: number;
  knowledge_points_studied: number;
  knowledge_points_mastered: number;
  exercises_attempted: number;
  exercises_correct: number;
  average_score: number;
}

// ========================================
// 学习追踪服务类
// ========================================

class LearningService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/v1/learning`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器 - 添加token
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
  // 知识点相关
  // ========================================

  async getSubjects(): Promise<Subject[]> {
    const response = await this.api.get('/subjects');
    return response.data;
  }

  async getChapters(subjectId: number): Promise<Chapter[]> {
    const response = await this.api.get(`/subjects/${subjectId}/chapters`);
    return response.data;
  }

  async getKnowledgePoints(chapterId: number): Promise<KnowledgePoint[]> {
    const response = await this.api.get(`/chapters/${chapterId}/knowledge-points`);
    return response.data;
  }

  // ========================================
  // 学习进度相关
  // ========================================

  async getProgress(knowledgePointId?: number): Promise<Progress[]> {
    const params = knowledgePointId ? { knowledge_point_id: knowledgePointId } : {};
    const response = await this.api.get('/progress', { params });
    return response.data;
  }

  async updateProgress(
    knowledgePointId: number,
    isCorrect: boolean,
    timeSpent: number = 0
  ): Promise<any> {
    const response = await this.api.post('/progress/update', {
      knowledge_point_id: knowledgePointId,
      is_correct: isCorrect,
      time_spent: timeSpent,
    });
    return response.data;
  }

  async getReviewDueKnowledgePoints(limit: number = 20): Promise<Progress[]> {
    const response = await this.api.get('/progress/review-due', {
      params: { limit },
    });
    return response.data;
  }

  // ========================================
  // 学习活动相关
  // ========================================

  async createActivity(data: {
    activity_type: string;
    title: string;
    knowledge_point_id?: number;
    description?: string;
    duration?: number;
    score?: number;
  }): Promise<any> {
    const response = await this.api.post('/activities', data);
    return response.data;
  }

  async getActivities(activityType?: string, limit: number = 50): Promise<any> {
    const params: any = { limit };
    if (activityType) {
      params.activity_type = activityType;
    }
    const response = await this.api.get('/activities', { params });
    return response.data;
  }

  // ========================================
  // 每日目标相关
  // ========================================

  async getDailyGoal(targetDate?: string): Promise<DailyGoal> {
    const params = targetDate ? { target_date: targetDate } : {};
    const response = await this.api.get('/daily-goal', { params });
    return response.data;
  }

  // ========================================
  // 学习统计相关
  // ========================================

  async getSummaryStats(): Promise<SummaryStats> {
    const response = await this.api.get('/stats/summary');
    return response.data;
  }

  async getStatsRange(startDate: string, endDate: string): Promise<{ stats: DailyStats[] }> {
    const response = await this.api.get('/stats/range', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  }

  // ========================================
  // 学习路径相关
  // ========================================

  async createLearningPath(data: {
    name: string;
    knowledge_point_ids: number[];
    target_subject_id?: number;
    description?: string;
    difficulty?: string;
  }): Promise<any> {
    const response = await this.api.post('/paths', data);
    return response.data;
  }

  async generateAdaptivePath(subjectId: number, targetDifficulty: string = 'intermediate'): Promise<any> {
    const response = await this.api.post('/paths/generate-adaptive', {
      subject_id: subjectId,
      target_difficulty: targetDifficulty,
    });
    return response.data;
  }

  async getLearningPaths(isActive?: boolean): Promise<{ paths: LearningPath[] }> {
    const params = isActive !== undefined ? { is_active: isActive } : {};
    const response = await this.api.get('/paths', { params });
    return response.data;
  }

  async getPathDetails(pathId: number): Promise<any> {
    const response = await this.api.get(`/paths/${pathId}`);
    return response.data;
  }

  // ========================================
  // 成就系统相关
  // ========================================

  async getAchievements(unlockedOnly: boolean = false): Promise<Achievement[]> {
    const response = await this.api.get('/achievements', {
      params: { unlocked_only: unlockedOnly },
    });
    return response.data;
  }

  async getAchievementSummary(): Promise<any> {
    const response = await this.api.get('/achievements/summary');
    return response.data;
  }

  async checkAchievements(): Promise<any> {
    const response = await this.api.post('/achievements/check');
    return response.data;
  }
}

export const learningService = new LearningService();
