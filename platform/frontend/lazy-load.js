/**
 * CHS-Books 图片懒加载工具
 * 版本: v1.0
 * 日期: 2025-11-10
 * 
 * 使用Intersection Observer API实现图片懒加载
 * 提升页面首屏加载速度和性能
 */

(function() {
    'use strict';
    
    // ============ 配置选项 ============
    
    const config = {
        // Intersection Observer 配置
        rootMargin: '50px',      // 提前50px开始加载
        threshold: 0.01,         // 1%可见时触发
        
        // 加载占位图
        placeholderSrc: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E加载中...%3C/text%3E%3C/svg%3E',
        
        // 错误占位图
        errorSrc: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f5f5f5" width="400" height="300"/%3E%3Ctext fill="%23666" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E图片加载失败%3C/text%3E%3C/svg%3E',
        
        // CSS类名
        loadingClass: 'lazy-loading',
        loadedClass: 'lazy-loaded',
        errorClass: 'lazy-error',
        
        // 淡入动画时长
        fadeInDuration: 300
    };
    
    // ============ Intersection Observer 实现 ============
    
    let observer = null;
    const imageQueue = new Set();
    
    /**
     * 初始化图片懒加载
     * @param {string} selector - 图片选择器，默认为 'img[data-src]'
     */
    function initLazyLoad(selector = 'img[data-src]') {
        // 检查浏览器支持
        if (!('IntersectionObserver' in window)) {
            console.warn('[LazyLoad] IntersectionObserver 不支持，使用降级方案');
            loadAllImagesFallback(selector);
            return;
        }
        
        // 创建观察器
        observer = new IntersectionObserver(handleIntersection, {
            rootMargin: config.rootMargin,
            threshold: config.threshold
        });
        
        // 查找所有需要懒加载的图片
        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            // 设置占位图
            if (!img.src || img.src === window.location.href) {
                img.src = config.placeholderSrc;
            }
            
            // 添加加载中样式
            img.classList.add(config.loadingClass);
            
            // 开始观察
            observer.observe(img);
            imageQueue.add(img);
        });
        
        console.log(`[LazyLoad] 初始化完成，共 ${images.length} 张图片待加载`);
    }
    
    /**
     * 处理图片进入可视区域
     */
    function handleIntersection(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                loadImage(img);
                observer.unobserve(img);
            }
        });
    }
    
    /**
     * 加载单张图片
     */
    function loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        
        if (!src) {
            console.warn('[LazyLoad] 图片缺少 data-src 属性', img);
            return;
        }
        
        // 创建临时图片对象用于预加载
        const tempImg = new Image();
        
        // 加载成功
        tempImg.onload = () => {
            // 设置实际图片
            img.src = src;
            if (srcset) {
                img.srcset = srcset;
            }
            
            // 更新样式
            img.classList.remove(config.loadingClass);
            img.classList.add(config.loadedClass);
            
            // 淡入动画
            img.style.opacity = '0';
            img.style.transition = `opacity ${config.fadeInDuration}ms ease-in`;
            
            // 触发重排
            img.offsetHeight;
            
            // 显示图片
            img.style.opacity = '1';
            
            // 清理
            imageQueue.delete(img);
            
            // 触发自定义事件
            img.dispatchEvent(new CustomEvent('lazyloaded', {
                detail: { src }
            }));
        };
        
        // 加载失败
        tempImg.onerror = () => {
            console.error('[LazyLoad] 图片加载失败', src);
            
            // 设置错误占位图
            img.src = config.errorSrc;
            
            // 更新样式
            img.classList.remove(config.loadingClass);
            img.classList.add(config.errorClass);
            
            // 清理
            imageQueue.delete(img);
            
            // 触发自定义事件
            img.dispatchEvent(new CustomEvent('lazyerror', {
                detail: { src }
            }));
        };
        
        // 开始加载
        tempImg.src = src;
    }
    
    /**
     * 降级方案：直接加载所有图片
     */
    function loadAllImagesFallback(selector) {
        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
            }
        });
        console.log(`[LazyLoad] 降级方案：直接加载 ${images.length} 张图片`);
    }
    
    // ============ 手动加载控制 ============
    
    /**
     * 手动加载指定图片
     * @param {HTMLImageElement|string} target - 图片元素或选择器
     */
    function loadImageNow(target) {
        const img = typeof target === 'string' 
            ? document.querySelector(target)
            : target;
        
        if (!img || img.tagName !== 'IMG') {
            console.warn('[LazyLoad] 无效的图片元素', target);
            return;
        }
        
        if (observer) {
            observer.unobserve(img);
        }
        
        loadImage(img);
    }
    
    /**
     * 立即加载所有待加载图片
     */
    function loadAllImages() {
        imageQueue.forEach(img => {
            if (observer) {
                observer.unobserve(img);
            }
            loadImage(img);
        });
        console.log('[LazyLoad] 手动加载所有图片');
    }
    
    /**
     * 停止懒加载
     */
    function destroy() {
        if (observer) {
            observer.disconnect();
            observer = null;
        }
        imageQueue.clear();
        console.log('[LazyLoad] 已停止');
    }
    
    // ============ 响应式图片支持 ============
    
    /**
     * 设置响应式图片
     * @param {HTMLImageElement} img 
     * @param {Object} sources - { small: 'url', medium: 'url', large: 'url' }
     */
    function setResponsiveImage(img, sources) {
        const width = window.innerWidth;
        let selectedSrc;
        
        if (width < 768 && sources.small) {
            selectedSrc = sources.small;
        } else if (width < 1024 && sources.medium) {
            selectedSrc = sources.medium;
        } else {
            selectedSrc = sources.large || sources.medium || sources.small;
        }
        
        if (selectedSrc) {
            img.dataset.src = selectedSrc;
        }
    }
    
    // ============ 批量处理工具 ============
    
    /**
     * 批量设置图片懒加载属性
     * @param {NodeList|Array} images 
     */
    function prepareLazyImages(images) {
        images.forEach(img => {
            if (img.src && img.src !== config.placeholderSrc) {
                // 将现有src移到data-src
                img.dataset.src = img.src;
                img.src = config.placeholderSrc;
            }
            
            // 添加加载中样式
            img.classList.add(config.loadingClass);
        });
        
        return images;
    }
    
    /**
     * 重新扫描并加载新图片
     * 用于动态加载的内容
     */
    function refresh(container = document) {
        const newImages = container.querySelectorAll('img[data-src]:not(.lazy-loaded):not(.lazy-loading)');
        
        if (newImages.length === 0) {
            return;
        }
        
        newImages.forEach(img => {
            img.classList.add(config.loadingClass);
            if (observer) {
                observer.observe(img);
            } else {
                loadImage(img);
            }
            imageQueue.add(img);
        });
        
        console.log(`[LazyLoad] 刷新：新增 ${newImages.length} 张图片`);
    }
    
    // ============ 性能监控 ============
    
    /**
     * 获取加载统计
     */
    function getStats() {
        return {
            pending: imageQueue.size,
            total: document.querySelectorAll('img[data-src]').length,
            loaded: document.querySelectorAll(`.${config.loadedClass}`).length,
            error: document.querySelectorAll(`.${config.errorClass}`).length
        };
    }
    
    /**
     * 打印统计信息
     */
    function printStats() {
        const stats = getStats();
        console.log('[LazyLoad] 统计信息:', stats);
        return stats;
    }
    
    // ============ 自动初始化 ============
    
    // DOM加载完成后自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initLazyLoad();
        });
    } else {
        // DOM已经加载完成
        initLazyLoad();
    }
    
    // ============ 导出API ============
    
    window.LazyLoad = {
        init: initLazyLoad,
        load: loadImageNow,
        loadAll: loadAllImages,
        destroy: destroy,
        refresh: refresh,
        prepare: prepareLazyImages,
        setResponsive: setResponsiveImage,
        getStats: getStats,
        printStats: printStats,
        config: config
    };
    
    console.log('[LazyLoad] 图片懒加载工具已加载 v1.0');
    
})();

