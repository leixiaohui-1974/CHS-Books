/**
 * CHS-Books 内容缓存管理器
 * 版本: v1.0
 * 日期: 2025-11-10
 * 
 * 使用IndexedDB和LocalStorage实现多层缓存机制
 * 提升内容加载速度和离线访问能力
 */

(function() {
    'use strict';
    
    // ============ 配置选项 ============
    
    const config = {
        // IndexedDB 配置
        dbName: 'CHSBooksCache',
        dbVersion: 1,
        
        // 存储配置
        stores: {
            textbooks: 'textbooks',      // 教材内容
            chapters: 'chapters',        // 章节内容
            cases: 'cases',              // 案例内容
            images: 'images',            // 图片缓存
            api: 'api'                   // API响应缓存
        },
        
        // 缓存策略
        maxAge: {
            textbooks: 7 * 24 * 60 * 60 * 1000,   // 7天
            chapters: 7 * 24 * 60 * 60 * 1000,     // 7天
            cases: 3 * 24 * 60 * 60 * 1000,        // 3天
            images: 30 * 24 * 60 * 60 * 1000,      // 30天
            api: 1 * 60 * 60 * 1000                // 1小时
        },
        
        // 大小限制（字节）
        maxSize: {
            textbooks: 5 * 1024 * 1024,   // 5MB
            chapters: 2 * 1024 * 1024,     // 2MB
            cases: 2 * 1024 * 1024,        // 2MB
            images: 10 * 1024 * 1024,      // 10MB per image
            api: 1 * 1024 * 1024           // 1MB
        },
        
        // 总存储限制
        totalQuota: 100 * 1024 * 1024,    // 100MB
        
        // LocalStorage前缀
        lsPrefix: 'chs_cache_'
    };
    
    // ============ IndexedDB 管理 ============
    
    let db = null;
    let dbInitialized = false;
    
    /**
     * 初始化IndexedDB
     */
    function initDB() {
        return new Promise((resolve, reject) => {
            if (dbInitialized && db) {
                resolve(db);
                return;
            }
            
            if (!window.indexedDB) {
                console.warn('[CacheManager] IndexedDB 不支持，使用 LocalStorage');
                resolve(null);
                return;
            }
            
            const request = indexedDB.open(config.dbName, config.dbVersion);
            
            request.onerror = () => {
                console.error('[CacheManager] IndexedDB 打开失败', request.error);
                reject(request.error);
            };
            
            request.onsuccess = () => {
                db = request.result;
                dbInitialized = true;
                console.log('[CacheManager] IndexedDB 初始化成功');
                resolve(db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // 创建各个对象存储
                Object.values(config.stores).forEach(storeName => {
                    if (!db.objectStoreNames.contains(storeName)) {
                        const store = db.createObjectStore(storeName, { keyPath: 'id' });
                        store.createIndex('timestamp', 'timestamp', { unique: false });
                        store.createIndex('size', 'size', { unique: false });
                    }
                });
                
                console.log('[CacheManager] IndexedDB 结构创建完成');
            };
        });
    }
    
    /**
     * 从IndexedDB获取数据
     */
    function getFromDB(storeName, key) {
        return new Promise(async (resolve, reject) => {
            try {
                await initDB();
                
                if (!db) {
                    resolve(null);
                    return;
                }
                
                const transaction = db.transaction([storeName], 'readonly');
                const store = transaction.objectStore(storeName);
                const request = store.get(key);
                
                request.onsuccess = () => {
                    const result = request.result;
                    
                    if (!result) {
                        resolve(null);
                        return;
                    }
                    
                    // 检查是否过期
                    const maxAge = config.maxAge[storeName] || config.maxAge.api;
                    const age = Date.now() - result.timestamp;
                    
                    if (age > maxAge) {
                        console.log(`[CacheManager] 缓存过期: ${storeName}/${key}`);
                        deleteFromDB(storeName, key); // 异步删除
                        resolve(null);
                        return;
                    }
                    
                    console.log(`[CacheManager] 命中缓存: ${storeName}/${key}`);
                    resolve(result.data);
                };
                
                request.onerror = () => {
                    console.error('[CacheManager] 读取失败', request.error);
                    reject(request.error);
                };
            } catch (error) {
                console.error('[CacheManager] getFromDB 错误', error);
                resolve(null);
            }
        });
    }
    
    /**
     * 保存到IndexedDB
     */
    function saveToDB(storeName, key, data) {
        return new Promise(async (resolve, reject) => {
            try {
                await initDB();
                
                if (!db) {
                    resolve(false);
                    return;
                }
                
                // 计算数据大小
                const dataStr = JSON.stringify(data);
                const size = new Blob([dataStr]).size;
                
                // 检查大小限制
                const maxSize = config.maxSize[storeName] || config.maxSize.api;
                if (size > maxSize) {
                    console.warn(`[CacheManager] 数据过大，不缓存: ${size} > ${maxSize}`);
                    resolve(false);
                    return;
                }
                
                const transaction = db.transaction([storeName], 'readwrite');
                const store = transaction.objectStore(storeName);
                
                const record = {
                    id: key,
                    data: data,
                    timestamp: Date.now(),
                    size: size
                };
                
                const request = store.put(record);
                
                request.onsuccess = () => {
                    console.log(`[CacheManager] 缓存成功: ${storeName}/${key} (${(size / 1024).toFixed(2)} KB)`);
                    resolve(true);
                };
                
                request.onerror = () => {
                    console.error('[CacheManager] 保存失败', request.error);
                    reject(request.error);
                };
            } catch (error) {
                console.error('[CacheManager] saveToDB 错误', error);
                resolve(false);
            }
        });
    }
    
    /**
     * 从IndexedDB删除数据
     */
    function deleteFromDB(storeName, key) {
        return new Promise(async (resolve, reject) => {
            try {
                await initDB();
                
                if (!db) {
                    resolve(false);
                    return;
                }
                
                const transaction = db.transaction([storeName], 'readwrite');
                const store = transaction.objectStore(storeName);
                const request = store.delete(key);
                
                request.onsuccess = () => {
                    console.log(`[CacheManager] 删除成功: ${storeName}/${key}`);
                    resolve(true);
                };
                
                request.onerror = () => {
                    console.error('[CacheManager] 删除失败', request.error);
                    reject(request.error);
                };
            } catch (error) {
                console.error('[CacheManager] deleteFromDB 错误', error);
                resolve(false);
            }
        });
    }
    
    /**
     * 清空指定存储
     */
    function clearStore(storeName) {
        return new Promise(async (resolve, reject) => {
            try {
                await initDB();
                
                if (!db) {
                    resolve(false);
                    return;
                }
                
                const transaction = db.transaction([storeName], 'readwrite');
                const store = transaction.objectStore(storeName);
                const request = store.clear();
                
                request.onsuccess = () => {
                    console.log(`[CacheManager] 清空存储: ${storeName}`);
                    resolve(true);
                };
                
                request.onerror = () => {
                    console.error('[CacheManager] 清空失败', request.error);
                    reject(request.error);
                };
            } catch (error) {
                console.error('[CacheManager] clearStore 错误', error);
                resolve(false);
            }
        });
    }
    
    // ============ LocalStorage 备用方案 ============
    
    /**
     * 从LocalStorage获取
     */
    function getFromLS(key) {
        try {
            const fullKey = config.lsPrefix + key;
            const item = localStorage.getItem(fullKey);
            
            if (!item) {
                return null;
            }
            
            const parsed = JSON.parse(item);
            
            // 检查过期
            if (parsed.expiry && Date.now() > parsed.expiry) {
                localStorage.removeItem(fullKey);
                return null;
            }
            
            return parsed.data;
        } catch (error) {
            console.error('[CacheManager] LocalStorage 读取失败', error);
            return null;
        }
    }
    
    /**
     * 保存到LocalStorage
     */
    function saveToLS(key, data, maxAge) {
        try {
            const fullKey = config.lsPrefix + key;
            const item = {
                data: data,
                expiry: Date.now() + maxAge
            };
            
            localStorage.setItem(fullKey, JSON.stringify(item));
            return true;
        } catch (error) {
            // 可能是存储满了
            console.warn('[CacheManager] LocalStorage 保存失败', error);
            
            // 尝试清理旧数据
            cleanupLS();
            
            // 再试一次
            try {
                localStorage.setItem(fullKey, JSON.stringify(item));
                return true;
            } catch (e) {
                return false;
            }
        }
    }
    
    /**
     * 清理LocalStorage中的过期项
     */
    function cleanupLS() {
        const now = Date.now();
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(config.lsPrefix)) {
                try {
                    const item = JSON.parse(localStorage.getItem(key));
                    if (item.expiry && now > item.expiry) {
                        keysToRemove.push(key);
                    }
                } catch (e) {
                    // 无效数据，也删除
                    keysToRemove.push(key);
                }
            }
        }
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log(`[CacheManager] LocalStorage 清理: ${keysToRemove.length} 项`);
    }
    
    // ============ 统一缓存API ============
    
    /**
     * 获取缓存
     */
    async function get(storeName, key) {
        // 先尝试IndexedDB
        const dbResult = await getFromDB(storeName, key);
        if (dbResult !== null) {
            return dbResult;
        }
        
        // 再尝试LocalStorage
        const lsKey = `${storeName}_${key}`;
        return getFromLS(lsKey);
    }
    
    /**
     * 设置缓存
     */
    async function set(storeName, key, data) {
        // 尝试保存到IndexedDB
        const dbSuccess = await saveToDB(storeName, key, data);
        
        if (!dbSuccess) {
            // 降级到LocalStorage
            const lsKey = `${storeName}_${key}`;
            const maxAge = config.maxAge[storeName] || config.maxAge.api;
            return saveToLS(lsKey, data, maxAge);
        }
        
        return dbSuccess;
    }
    
    /**
     * 删除缓存
     */
    async function remove(storeName, key) {
        await deleteFromDB(storeName, key);
        const lsKey = `${storeName}_${key}`;
        localStorage.removeItem(config.lsPrefix + lsKey);
    }
    
    /**
     * 清空所有缓存
     */
    async function clearAll() {
        // 清空IndexedDB
        for (const storeName of Object.values(config.stores)) {
            await clearStore(storeName);
        }
        
        // 清空LocalStorage
        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(config.lsPrefix)) {
                keys.push(key);
            }
        }
        keys.forEach(key => localStorage.removeItem(key));
        
        console.log('[CacheManager] 所有缓存已清空');
    }
    
    // ============ API请求缓存装饰器 ============
    
    /**
     * 带缓存的fetch
     */
    async function cachedFetch(url, options = {}) {
        const cacheKey = url + JSON.stringify(options);
        
        // 检查缓存
        const cached = await get(config.stores.api, cacheKey);
        if (cached && !options.bypassCache) {
            console.log(`[CacheManager] API缓存命中: ${url}`);
            return cached;
        }
        
        // 发起请求
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            
            // 只缓存成功的响应
            if (response.ok) {
                await set(config.stores.api, cacheKey, data);
            }
            
            return data;
        } catch (error) {
            console.error('[CacheManager] 请求失败', error);
            
            // 如果有缓存，返回过期的缓存
            if (cached) {
                console.warn('[CacheManager] 使用过期缓存');
                return cached;
            }
            
            throw error;
        }
    }
    
    // ============ 存储统计 ============
    
    /**
     * 获取存储使用情况
     */
    async function getStorageInfo() {
        const info = {
            indexedDB: {},
            localStorage: {},
            total: 0
        };
        
        // IndexedDB统计
        if (db) {
            for (const storeName of Object.values(config.stores)) {
                try {
                    const transaction = db.transaction([storeName], 'readonly');
                    const store = transaction.objectStore(storeName);
                    const index = store.index('size');
                    
                    const countRequest = store.count();
                    const count = await new Promise(resolve => {
                        countRequest.onsuccess = () => resolve(countRequest.result);
                    });
                    
                    let totalSize = 0;
                    const cursorRequest = index.openCursor();
                    
                    await new Promise(resolve => {
                        cursorRequest.onsuccess = (event) => {
                            const cursor = event.target.result;
                            if (cursor) {
                                totalSize += cursor.value.size || 0;
                                cursor.continue();
                            } else {
                                resolve();
                            }
                        };
                    });
                    
                    info.indexedDB[storeName] = {
                        count: count,
                        size: totalSize,
                        sizeFormatted: formatBytes(totalSize)
                    };
                    
                    info.total += totalSize;
                } catch (error) {
                    console.error(`[CacheManager] 统计失败: ${storeName}`, error);
                }
            }
        }
        
        // LocalStorage统计
        let lsSize = 0;
        let lsCount = 0;
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(config.lsPrefix)) {
                const value = localStorage.getItem(key);
                lsSize += new Blob([value]).size;
                lsCount++;
            }
        }
        info.localStorage = {
            count: lsCount,
            size: lsSize,
            sizeFormatted: formatBytes(lsSize)
        };
        info.total += lsSize;
        
        info.totalFormatted = formatBytes(info.total);
        info.quotaUsage = ((info.total / config.totalQuota) * 100).toFixed(2) + '%';
        
        return info;
    }
    
    /**
     * 格式化字节数
     */
    function formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
    }
    
    /**
     * 打印存储信息
     */
    async function printStorageInfo() {
        const info = await getStorageInfo();
        console.log('[CacheManager] 存储使用情况:');
        console.log('IndexedDB:', info.indexedDB);
        console.log('LocalStorage:', info.localStorage);
        console.log('总计:', info.totalFormatted, '(' + info.quotaUsage + ')');
        return info;
    }
    
    // ============ 自动初始化 ============
    
    // 页面加载时初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initDB().catch(error => {
                console.error('[CacheManager] 初始化失败', error);
            });
        });
    } else {
        initDB().catch(error => {
            console.error('[CacheManager] 初始化失败', error);
        });
    }
    
    // 定期清理过期缓存
    setInterval(() => {
        cleanupLS();
    }, 30 * 60 * 1000); // 每30分钟
    
    // ============ 导出API ============
    
    window.CacheManager = {
        // 基础操作
        get: get,
        set: set,
        remove: remove,
        clearAll: clearAll,
        
        // 网络请求
        fetch: cachedFetch,
        
        // 存储信息
        getStorageInfo: getStorageInfo,
        printStorageInfo: printStorageInfo,
        
        // 配置
        config: config,
        
        // 内部API（高级用户）
        _db: () => db,
        _initDB: initDB
    };
    
    console.log('[CacheManager] 缓存管理器已加载 v1.0');
    
})();

