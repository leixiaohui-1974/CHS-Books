/**
 * CHS-Books 学习进度跟踪器
 * 版本: v1.0
 * 日期: 2025-11-11
 * 
 * 客户端学习进度管理工具
 */

(function() {
    'use strict';
    
    // ============ 配置 ============
    
    const config = {
        userId: 'default_user',
        apiBase: '/api/progress',
        autoSave: true,
        saveInterval: 30000,  // 30秒自动保存
        sessionTracking: true
    };
    
    // ============ 状态管理 ============
    
    let currentSession = null;
    let autoSaveTimer = null;
    let sessionStartTime = null;
    
    // ============ API调用 ============
    
    /**
     * 更新进度
     */
    async function updateProgress(itemType, itemId, status, options = {}) {
        const data = {
            user_id: config.userId,
            item_type: itemType,
            item_id: itemId,
            status: status,
            progress_percent: options.progressPercent,
            time_spent: options.timeSpent,
            notes: options.notes
        };
        
        try {
            const response = await fetch(`${config.apiBase}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('[ProgressTracker] 进度已更新:', result);
                
                // 触发自定义事件
                window.dispatchEvent(new CustomEvent('progressUpdated', {
                    detail: result
                }));
                
                return result;
            } else {
                console.error('[ProgressTracker] 更新失败:', result);
                return null;
            }
        } catch (error) {
            console.error('[ProgressTracker] 请求失败:', error);
            return null;
        }
    }
    
    /**
     * 获取用户进度
     */
    async function getUserProgress(filters = {}) {
        const params = new URLSearchParams();
        if (filters.itemType) params.append('item_type', filters.itemType);
        if (filters.status) params.append('status', filters.status);
        
        try {
            const response = await fetch(
                `${config.apiBase}/user/${config.userId}?${params}`
            );
            const result = await response.json();
            
            if (result.success) {
                return result;
            } else {
                console.error('[ProgressTracker] 获取进度失败');
                return null;
            }
        } catch (error) {
            console.error('[ProgressTracker] 请求失败:', error);
            return null;
        }
    }
    
    /**
     * 获取特定项目进度
     */
    async function getItemProgress(itemType, itemId) {
        try {
            const response = await fetch(
                `${config.apiBase}/item/${itemType}/${itemId}?user_id=${config.userId}`
            );
            const result = await response.json();
            
            if (result.success) {
                return result;
            } else {
                return null;
            }
        } catch (error) {
            console.error('[ProgressTracker] 获取项目进度失败:', error);
            return null;
        }
    }
    
    /**
     * 获取统计信息
     */
    async function getStatistics() {
        try {
            const response = await fetch(
                `${config.apiBase}/statistics/${config.userId}`
            );
            const result = await response.json();
            
            if (result.success) {
                return result.statistics;
            } else {
                return null;
            }
        } catch (error) {
            console.error('[ProgressTracker] 获取统计失败:', error);
            return null;
        }
    }
    
    // ============ 学习会话管理 ============
    
    /**
     * 开始学习会话
     */
    async function startSession(itemType, itemId) {
        if (currentSession) {
            console.warn('[ProgressTracker] 已有活动会话，将结束旧会话');
            await endSession();
        }
        
        const data = {
            user_id: config.userId,
            item_type: itemType,
            item_id: itemId
        };
        
        try {
            const response = await fetch(`${config.apiBase}/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                currentSession = result.session;
                sessionStartTime = new Date();
                console.log('[ProgressTracker] 学习会话已开始:', currentSession);
                
                // 触发事件
                window.dispatchEvent(new CustomEvent('sessionStarted', {
                    detail: currentSession
                }));
                
                return currentSession;
            }
        } catch (error) {
            console.error('[ProgressTracker] 开始会话失败:', error);
        }
        
        return null;
    }
    
    /**
     * 结束学习会话
     */
    async function endSession() {
        if (!currentSession) {
            console.warn('[ProgressTracker] 没有活动的学习会话');
            return null;
        }
        
        try {
            const response = await fetch(
                `${config.apiBase}/session/end?user_id=${config.userId}`,
                { method: 'POST' }
            );
            
            const result = await response.json();
            
            if (result.success) {
                console.log('[ProgressTracker] 学习会话已结束:', result);
                
                const session = currentSession;
                currentSession = null;
                sessionStartTime = null;
                
                // 触发事件
                window.dispatchEvent(new CustomEvent('sessionEnded', {
                    detail: {
                        session: session,
                        duration: result.duration
                    }
                }));
                
                return result;
            }
        } catch (error) {
            console.error('[ProgressTracker] 结束会话失败:', error);
        }
        
        return null;
    }
    
    /**
     * 获取当前会话
     */
    async function getCurrentSession() {
        try {
            const response = await fetch(
                `${config.apiBase}/session/current/${config.userId}`
            );
            const result = await response.json();
            
            if (result.success && result.active) {
                currentSession = result.session;
                return result;
            }
        } catch (error) {
            console.error('[ProgressTracker] 获取当前会话失败:', error);
        }
        
        return null;
    }
    
    /**
     * 获取会话持续时间
     */
    function getSessionDuration() {
        if (!sessionStartTime) return 0;
        return Math.floor((new Date() - sessionStartTime) / 1000);
    }
    
    // ============ 便捷方法 ============
    
    /**
     * 标记为已开始
     */
    async function markAsStarted(itemType, itemId) {
        return await updateProgress(itemType, itemId, 'in_progress', {
            progressPercent: 0
        });
    }
    
    /**
     * 标记为已完成
     */
    async function markAsCompleted(itemType, itemId) {
        return await updateProgress(itemType, itemId, 'completed', {
            progressPercent: 100
        });
    }
    
    /**
     * 更新进度百分比
     */
    async function updateProgressPercent(itemType, itemId, percent) {
        const status = percent >= 100 ? 'completed' : 'in_progress';
        return await updateProgress(itemType, itemId, status, {
            progressPercent: percent
        });
    }
    
    /**
     * 添加学习笔记
     */
    async function addNote(itemType, itemId, note) {
        return await updateProgress(itemType, itemId, 'in_progress', {
            notes: note
        });
    }
    
    // ============ 自动跟踪 ============
    
    /**
     * 启用自动跟踪
     */
    function enableAutoTracking() {
        // 页面可见性变化
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // 页面卸载前
        window.addEventListener('beforeunload', handleBeforeUnload);
        
        // 定期自动保存
        if (config.autoSave) {
            autoSaveTimer = setInterval(autoSaveProgress, config.saveInterval);
        }
        
        console.log('[ProgressTracker] 自动跟踪已启用');
    }
    
    /**
     * 禁用自动跟踪
     */
    function disableAutoTracking() {
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        window.removeEventListener('beforeunload', handleBeforeUnload);
        
        if (autoSaveTimer) {
            clearInterval(autoSaveTimer);
            autoSaveTimer = null;
        }
        
        console.log('[ProgressTracker] 自动跟踪已禁用');
    }
    
    /**
     * 处理页面可见性变化
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            console.log('[ProgressTracker] 页面隐藏，暂停会话');
        } else {
            console.log('[ProgressTracker] 页面可见，恢复会话');
        }
    }
    
    /**
     * 页面卸载前处理
     */
    function handleBeforeUnload(e) {
        if (currentSession) {
            // 同步结束会话（注意：这可能不会完成）
            endSession();
        }
    }
    
    /**
     * 自动保存进度
     */
    async function autoSaveProgress() {
        if (!currentSession) return;
        
        const duration = getSessionDuration();
        if (duration > 0) {
            await updateProgress(
                currentSession.item_type,
                currentSession.item_id,
                'in_progress',
                { timeSpent: config.saveInterval / 1000 }
            );
            console.log('[ProgressTracker] 自动保存完成');
        }
    }
    
    // ============ UI辅助 ============
    
    /**
     * 创建进度条
     */
    function createProgressBar(percent, options = {}) {
        const container = document.createElement('div');
        container.className = 'progress-bar-container';
        container.style.cssText = `
            width: 100%;
            height: ${options.height || '8px'};
            background: ${options.bgColor || '#e0e0e0'};
            border-radius: 4px;
            overflow: hidden;
        `;
        
        const bar = document.createElement('div');
        bar.className = 'progress-bar';
        bar.style.cssText = `
            width: ${percent}%;
            height: 100%;
            background: ${options.barColor || '#4CAF50'};
            transition: width 0.3s ease;
        `;
        
        container.appendChild(bar);
        
        if (options.showText) {
            const text = document.createElement('div');
            text.textContent = `${percent}%`;
            text.style.cssText = `
                text-align: center;
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            `;
            container.appendChild(text);
        }
        
        return container;
    }
    
    /**
     * 获取状态徽章HTML
     */
    function getStatusBadge(status) {
        const badges = {
            'not_started': '<span style="background:#6c757d;color:white;padding:2px 8px;border-radius:12px;font-size:12px;">未开始</span>',
            'in_progress': '<span style="background:#ffc107;color:white;padding:2px 8px;border-radius:12px;font-size:12px;">进行中</span>',
            'completed': '<span style="background:#28a745;color:white;padding:2px 8px;border-radius:12px;font-size:12px;">已完成</span>',
            'reviewed': '<span style="background:#007bff;color:white;padding:2px 8px;border-radius:12px;font-size:12px;">已复习</span>'
        };
        
        return badges[status] || badges['not_started'];
    }
    
    /**
     * 格式化时长
     */
    function formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds}秒`;
        } else if (seconds < 3600) {
            return `${Math.floor(seconds / 60)}分钟`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}小时${minutes}分钟`;
        }
    }
    
    // ============ 初始化 ============
    
    /**
     * 初始化进度跟踪器
     */
    async function init(options = {}) {
        // 合并配置
        Object.assign(config, options);
        
        // 检查是否有活动会话
        const session = await getCurrentSession();
        if (session && session.active) {
            console.log('[ProgressTracker] 恢复活动会话:', session);
            currentSession = session.session;
            sessionStartTime = new Date(session.session.start_time);
        }
        
        // 启用自动跟踪
        if (config.sessionTracking) {
            enableAutoTracking();
        }
        
        console.log('[ProgressTracker] 初始化完成');
    }
    
    // 页面加载时自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            init();
        });
    } else {
        init();
    }
    
    // ============ 导出API ============
    
    window.ProgressTracker = {
        // 配置
        config: config,
        
        // 初始化
        init: init,
        
        // 进度管理
        updateProgress: updateProgress,
        getUserProgress: getUserProgress,
        getItemProgress: getItemProgress,
        getStatistics: getStatistics,
        
        // 便捷方法
        markAsStarted: markAsStarted,
        markAsCompleted: markAsCompleted,
        updateProgressPercent: updateProgressPercent,
        addNote: addNote,
        
        // 会话管理
        startSession: startSession,
        endSession: endSession,
        getCurrentSession: getCurrentSession,
        getSessionDuration: getSessionDuration,
        
        // 自动跟踪
        enableAutoTracking: enableAutoTracking,
        disableAutoTracking: disableAutoTracking,
        
        // UI辅助
        createProgressBar: createProgressBar,
        getStatusBadge: getStatusBadge,
        formatDuration: formatDuration
    };
    
    console.log('[ProgressTracker] 学习进度跟踪器已加载 v1.0');
    
})();

