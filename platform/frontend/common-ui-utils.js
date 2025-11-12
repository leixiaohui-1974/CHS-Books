/**
 * CHS-Books 统一UI工具函数库
 * 版本: v1.0
 * 日期: 2025-11-10
 * 
 * 提供统一的加载动画、Toast通知等UI组件
 * 所有前端页面都应使用这些统一的工具函数
 */

// ============ 加载动画 ============

/**
 * 显示全屏加载动画
 * @param {string} message - 加载提示文本，默认"加载中..."
 * @returns {HTMLElement} overlay DOM元素，用于后续关闭
 */
function showLoading(message = '加载中...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div class="loading-spinner"></div>
            <div class="loading-text">${message}</div>
        </div>
    `;
    document.body.appendChild(overlay);
    return overlay;
}

/**
 * 隐藏加载动画
 * @param {HTMLElement} overlay - showLoading返回的DOM元素
 */
function hideLoading(overlay) {
    if (overlay && overlay.parentElement) {
        overlay.style.opacity = '0';
        setTimeout(() => {
            if (overlay.parentElement) {
                overlay.remove();
            }
        }, 300);
    }
}

// ============ Toast通知 ============

/**
 * 显示错误提示Toast
 * @param {string} title - 错误标题
 * @param {string} message - 错误详细信息
 */
function showError(title, message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.innerHTML = `
        <div class="error-toast-header">
            <span>⚠️</span>
            <span>${title}</span>
        </div>
        <div class="error-toast-body">${message}</div>
        <button class="error-toast-close" onclick="this.parentElement.remove()">知道了</button>
    `;
    document.body.appendChild(toast);
    
    // 自动关闭
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

/**
 * 显示成功提示Toast
 * @param {string} message - 成功提示文本
 */
function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.innerHTML = `
        <div class="success-toast-header">
            <span>✅</span>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    // 自动关闭
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 2000);
}

/**
 * 显示警告提示Toast
 * @param {string} title - 警告标题
 * @param {string} message - 警告详细信息
 */
function showWarning(title, message) {
    const toast = document.createElement('div');
    toast.className = 'warning-toast';
    toast.innerHTML = `
        <div class="warning-toast-header">
            <span>⚡</span>
            <span>${title}</span>
        </div>
        <div class="warning-toast-body">${message}</div>
    `;
    document.body.appendChild(toast);
    
    // 自动关闭
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 3000);
}

/**
 * 显示信息提示Toast
 * @param {string} message - 信息提示文本
 */
function showInfo(message) {
    const toast = document.createElement('div');
    toast.className = 'info-toast';
    toast.innerHTML = `
        <div class="info-toast-header">
            <span>ℹ️</span>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    // 自动关闭
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, 3000);
}

// ============ 标准异步请求模式 ============

/**
 * 标准的异步请求处理函数
 * 自动处理加载状态、错误提示等
 * 
 * @param {string} url - 请求URL
 * @param {Object} options - fetch选项
 * @param {string} loadingMessage - 加载提示文本
 * @returns {Promise<Object>} 响应数据
 */
async function fetchWithUI(url, options = {}, loadingMessage = '加载中...') {
    const loading = showLoading(loadingMessage);
    
    try {
        const response = await fetch(url, options);
        
        // 检查HTTP状态
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // 检查业务状态
        if (data.success === false) {
            throw new Error(data.error || data.message || '操作失败');
        }
        
        return data;
        
    } catch (error) {
        console.error('请求失败:', error);
        showError('操作失败', error.message || '无法连接到服务器，请稍后重试');
        throw error;
        
    } finally {
        hideLoading(loading);
    }
}

// ============ 工具函数导出 ============

// 如果使用ES6模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showLoading,
        hideLoading,
        showError,
        showSuccess,
        showWarning,
        showInfo,
        fetchWithUI
    };
}

// 全局可用
window.CHSBooksUI = {
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    fetchWithUI
};

console.log('[CHS-Books] UI工具函数库已加载 v1.0');

