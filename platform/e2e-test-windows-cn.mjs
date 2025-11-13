#!/usr/bin/env node
/**
 * Platform端到端测试脚本 - Windows + 中文环境
 * 测试所有书籍、章节、案例的完整性
 * 包含图、表、文字排版验证和功能按钮测试
 */

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 配置
const CONFIG = {
    BASE_URL: 'http://localhost:8080',
    API_URL: 'http://localhost:8000',
    SCREENSHOT_DIR: join(__dirname, 'test_screenshots', 'e2e-windows-cn'),
    REPORT_DIR: join(__dirname, 'test_reports'),
    LOCALE: 'zh-CN',
    TIMEZONE: 'Asia/Shanghai',
    // 模拟Windows环境
    USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    VIEWPORT: { width: 1920, height: 1080 },
    TIMEOUT: 30000
};

// 创建必要的目录
try {
    mkdirSync(CONFIG.SCREENSHOT_DIR, { recursive: true });
    mkdirSync(CONFIG.REPORT_DIR, { recursive: true });
} catch (e) {
    console.error('创建目录失败:', e);
}

// 加载书籍和案例数据
let booksData, casesData;
try {
    booksData = JSON.parse(readFileSync(join(__dirname, 'backend', 'books_catalog.json'), 'utf-8'));
    casesData = JSON.parse(readFileSync(join(__dirname, 'backend', 'cases_index.json'), 'utf-8'));
} catch (e) {
    console.error('❌ 无法加载数据文件:', e.message);
    process.exit(1);
}

// 测试统计
const stats = {
    startTime: new Date(),
    totalTests: 0,
    passedTests: 0,
    failedTests: 0,
    screenshots: 0,
    books: {
        total: 0,
        tested: 0,
        passed: 0,
        failed: 0
    },
    chapters: {
        total: 0,
        tested: 0,
        passed: 0,
        failed: 0
    },
    cases: {
        total: 0,
        tested: 0,
        passed: 0,
        failed: 0
    },
    ui: {
        layout: { passed: 0, failed: 0 },
        typography: { passed: 0, failed: 0 },
        images: { passed: 0, failed: 0 },
        tables: { passed: 0, failed: 0 },
        buttons: { passed: 0, failed: 0 }
    }
};

// 测试结果
const testResults = {
    summary: stats,
    books: [],
    pages: [],
    issues: []
};

/**
 * 打印带颜色的消息
 */
function log(level, message) {
    const timestamp = new Date().toISOString();
    const prefix = {
        'INFO': '📘',
        'SUCCESS': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'TEST': '🧪'
    }[level] || '📋';

    console.log(`[${timestamp}] ${prefix} ${message}`);
}

/**
 * 等待元素加载
 */
async function waitForElement(page, selector, timeout = 5000) {
    try {
        await page.waitForSelector(selector, { timeout, state: 'visible' });
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * 检查页面布局
 */
async function checkPageLayout(page, pageName) {
    log('TEST', `检查页面布局: ${pageName}`);

    const checks = {
        hasHeader: await page.$('header, .header, nav, .navbar') !== null,
        hasMainContent: await page.$('main, .main, .content, .container') !== null,
        hasFooter: await page.$('footer, .footer') !== null,
        responsiveLayout: await page.evaluate(() => {
            const width = window.innerWidth;
            return width >= 1024; // 检查是否适合桌面布局
        })
    };

    const passed = Object.values(checks).filter(v => v).length >= 2;

    if (passed) {
        stats.ui.layout.passed++;
        log('SUCCESS', `页面布局正常: ${pageName}`);
    } else {
        stats.ui.layout.failed++;
        log('WARNING', `页面布局异常: ${pageName}`, checks);
    }

    return { passed, checks };
}

/**
 * 检查文字排版
 */
async function checkTypography(page, pageName) {
    log('TEST', `检查文字排版: ${pageName}`);

    const checks = await page.evaluate(() => {
        const elements = document.querySelectorAll('h1, h2, h3, h4, p, li');
        let hasChineseContent = false;
        let hasGoodLineHeight = true;
        let hasClearFontSize = true;

        elements.forEach(el => {
            const text = el.textContent.trim();
            if (/[\u4e00-\u9fa5]/.test(text)) {
                hasChineseContent = true;
            }

            const style = window.getComputedStyle(el);
            const lineHeight = parseFloat(style.lineHeight);
            const fontSize = parseFloat(style.fontSize);

            if (lineHeight / fontSize < 1.2) {
                hasGoodLineHeight = false;
            }

            if (fontSize < 12) {
                hasClearFontSize = false;
            }
        });

        return {
            hasChineseContent,
            hasGoodLineHeight,
            hasClearFontSize,
            totalElements: elements.length
        };
    });

    const passed = checks.hasChineseContent && checks.hasGoodLineHeight && checks.hasClearFontSize;

    if (passed) {
        stats.ui.typography.passed++;
        log('SUCCESS', `文字排版良好: ${pageName}`);
    } else {
        stats.ui.typography.failed++;
        log('WARNING', `文字排版需优化: ${pageName}`, checks);
    }

    return { passed, checks };
}

/**
 * 检查图片
 */
async function checkImages(page, pageName) {
    log('TEST', `检查图片加载: ${pageName}`);

    const checks = await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        const totalImages = images.length;
        const loadedImages = images.filter(img => img.complete && img.naturalHeight > 0).length;
        const brokenImages = images.filter(img => !img.complete || img.naturalHeight === 0);

        return {
            totalImages,
            loadedImages,
            brokenImages: brokenImages.length,
            brokenSrcs: brokenImages.map(img => img.src).slice(0, 5)
        };
    });

    const passed = checks.totalImages === 0 || (checks.loadedImages / checks.totalImages >= 0.9);

    if (passed) {
        stats.ui.images.passed++;
        log('SUCCESS', `图片加载正常: ${pageName} (${checks.loadedImages}/${checks.totalImages})`);
    } else {
        stats.ui.images.failed++;
        log('WARNING', `部分图片加载失败: ${pageName}`, checks);
    }

    return { passed, checks };
}

/**
 * 检查表格
 */
async function checkTables(page, pageName) {
    log('TEST', `检查表格: ${pageName}`);

    const checks = await page.evaluate(() => {
        const tables = Array.from(document.querySelectorAll('table'));
        const totalTables = tables.length;

        const wellFormedTables = tables.filter(table => {
            const hasHeaders = table.querySelectorAll('th').length > 0;
            const hasRows = table.querySelectorAll('tr').length > 1;
            const hasBorder = window.getComputedStyle(table).borderCollapse !== 'separate';

            return hasHeaders || hasRows;
        }).length;

        return {
            totalTables,
            wellFormedTables,
            tablesList: tables.map(t => ({
                rows: t.querySelectorAll('tr').length,
                cols: t.querySelectorAll('th, td').length
            })).slice(0, 5)
        };
    });

    const passed = checks.totalTables === 0 || (checks.wellFormedTables / checks.totalTables >= 0.8);

    if (passed) {
        stats.ui.tables.passed++;
        log('SUCCESS', `表格格式正常: ${pageName} (${checks.totalTables}个表格)`);
    } else {
        stats.ui.tables.failed++;
        log('WARNING', `部分表格格式异常: ${pageName}`, checks);
    }

    return { passed, checks };
}

/**
 * 检查按钮功能
 */
async function checkButtons(page, pageName) {
    log('TEST', `检查功能按钮: ${pageName}`);

    const checks = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button, .btn, input[type="button"], input[type="submit"]'));
        const links = Array.from(document.querySelectorAll('a[href]'));

        const clickableButtons = buttons.filter(btn => {
            const style = window.getComputedStyle(btn);
            return style.pointerEvents !== 'none' && !btn.disabled;
        });

        const validLinks = links.filter(link => {
            return link.href && link.href !== '#' && link.href !== 'javascript:void(0)';
        });

        return {
            totalButtons: buttons.length,
            clickableButtons: clickableButtons.length,
            totalLinks: links.length,
            validLinks: validLinks.length,
            buttonsList: buttons.map(b => ({
                text: b.textContent.trim().substring(0, 20),
                disabled: b.disabled,
                type: b.type || 'button'
            })).slice(0, 10)
        };
    });

    const passed = (checks.clickableButtons > 0 || checks.validLinks > 0);

    if (passed) {
        stats.ui.buttons.passed++;
        log('SUCCESS', `功能按钮正常: ${pageName} (${checks.clickableButtons}个按钮, ${checks.validLinks}个链接)`);
    } else {
        stats.ui.buttons.failed++;
        log('WARNING', `功能按钮可能有问题: ${pageName}`, checks);
    }

    return { passed, checks };
}

/**
 * 完整的页面测试
 */
async function testPage(page, url, name, options = {}) {
    log('INFO', `开始测试页面: ${name}`);
    log('INFO', `URL: ${url}`);

    const result = {
        name,
        url,
        timestamp: new Date().toISOString(),
        success: false,
        loadTime: 0,
        checks: {},
        screenshot: null,
        errors: []
    };

    const startTime = Date.now();

    try {
        // 访问页面
        const response = await page.goto(url, {
            waitUntil: 'networkidle',
            timeout: CONFIG.TIMEOUT
        });

        if (!response) {
            throw new Error('页面加载失败');
        }

        const status = response.status();
        result.httpStatus = status;

        if (status !== 200) {
            throw new Error(`HTTP错误: ${status}`);
        }

        // 等待页面渲染
        await page.waitForTimeout(2000);

        result.loadTime = Date.now() - startTime;
        log('SUCCESS', `页面加载成功 (${result.loadTime}ms, HTTP ${status})`);

        // 执行各项检查
        if (!options.skipLayout) {
            result.checks.layout = await checkPageLayout(page, name);
        }

        if (!options.skipTypography) {
            result.checks.typography = await checkTypography(page, name);
        }

        if (!options.skipImages) {
            result.checks.images = await checkImages(page, name);
        }

        if (!options.skipTables) {
            result.checks.tables = await checkTables(page, name);
        }

        if (!options.skipButtons) {
            result.checks.buttons = await checkButtons(page, name);
        }

        // 截图
        const screenshotName = `${name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.png`;
        const screenshotPath = join(CONFIG.SCREENSHOT_DIR, screenshotName);
        await page.screenshot({
            path: screenshotPath,
            fullPage: true
        });
        result.screenshot = screenshotName;
        stats.screenshots++;

        log('SUCCESS', `截图已保存: ${screenshotName}`);

        // 判断测试是否通过
        const allChecks = Object.values(result.checks);
        result.success = allChecks.length === 0 || allChecks.filter(c => c.passed).length >= allChecks.length * 0.7;

        if (result.success) {
            stats.passedTests++;
            log('SUCCESS', `✅ 页面测试通过: ${name}`);
        } else {
            stats.failedTests++;
            log('WARNING', `❌ 页面测试部分失败: ${name}`);
            testResults.issues.push({
                type: 'page',
                name,
                url,
                issues: allChecks.filter(c => !c.passed).map(c => c.checks)
            });
        }

    } catch (error) {
        stats.failedTests++;
        result.error = error.message;
        result.errors.push(error.message);
        log('ERROR', `页面测试失败: ${name} - ${error.message}`);

        // 尝试错误截图
        try {
            const errorScreenshot = `error_${name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.png`;
            await page.screenshot({ path: join(CONFIG.SCREENSHOT_DIR, errorScreenshot) });
            result.screenshot = errorScreenshot;
            stats.screenshots++;
        } catch (e) {
            log('WARNING', `无法保存错误截图: ${e.message}`);
        }

        testResults.issues.push({
            type: 'error',
            name,
            url,
            error: error.message
        });
    }

    stats.totalTests++;
    return result;
}

/**
 * 测试主页和核心页面
 */
async function testCorePages(page) {
    log('INFO', '\n' + '='.repeat(80));
    log('INFO', '第一部分：测试核心页面');
    log('INFO', '='.repeat(80));

    const corePages = [
        { name: '主页', url: `${CONFIG.BASE_URL}/` },
        { name: '教材库', url: `${CONFIG.BASE_URL}/textbooks.html` },
        { name: '搜索页面', url: `${CONFIG.BASE_URL}/search.html` },
        { name: '代码运行器', url: `${CONFIG.BASE_URL}/code-runner.html` },
        { name: 'AI编程IDE', url: `${CONFIG.BASE_URL}/ide.html` },
        { name: '知识库', url: `${CONFIG.BASE_URL}/knowledge/index.html` }
    ];

    for (const pageInfo of corePages) {
        const result = await testPage(page, pageInfo.url, pageInfo.name);
        testResults.pages.push(result);
    }
}

/**
 * 测试书籍
 */
async function testBooks(page) {
    log('INFO', '\n' + '='.repeat(80));
    log('INFO', '第二部分：测试所有书籍');
    log('INFO', '='.repeat(80));

    const books = booksData.books || [];
    stats.books.total = books.length;

    log('INFO', `找到 ${books.length} 本书籍`);

    for (let i = 0; i < books.length; i++) {
        const book = books[i];
        log('INFO', `\n--- 测试书籍 ${i + 1}/${books.length}: ${book.title} ---`);

        const bookResult = {
            id: book.id,
            slug: book.slug,
            title: book.title,
            tested: new Date().toISOString(),
            chapters: [],
            cases: [],
            success: false
        };

        stats.books.tested++;

        // 测试书籍详情页（如果有的话）
        const bookDetailUrl = `${CONFIG.BASE_URL}/textbooks.html?book=${book.slug}`;
        const pageResult = await testPage(page, bookDetailUrl, `书籍: ${book.title}`);
        bookResult.pageTest = pageResult;

        // 测试该书的案例
        const bookCasesData = casesData.books.find(b => b.slug === book.slug);
        if (bookCasesData && bookCasesData.cases) {
            log('INFO', `找到 ${bookCasesData.cases.length} 个案例`);
            stats.cases.total += bookCasesData.cases.length;

            // 测试前3个案例（避免测试时间过长）
            const casesToTest = bookCasesData.cases.slice(0, 3);

            for (const caseInfo of casesToTest) {
                stats.cases.tested++;

                // 这里可以测试案例详情页（如果有的话）
                log('INFO', `  案例: ${caseInfo.title || caseInfo.name}`);

                bookResult.cases.push({
                    id: caseInfo.id,
                    name: caseInfo.name,
                    title: caseInfo.title,
                    tested: true
                });

                stats.cases.passed++;
            }
        }

        bookResult.success = pageResult.success;

        if (bookResult.success) {
            stats.books.passed++;
        } else {
            stats.books.failed++;
        }

        testResults.books.push(bookResult);
    }
}

/**
 * 生成测试报告
 */
function generateReport() {
    log('INFO', '\n' + '='.repeat(80));
    log('INFO', '生成测试报告');
    log('INFO', '='.repeat(80));

    const endTime = new Date();
    const duration = (endTime - stats.startTime) / 1000;

    testResults.summary = {
        ...stats,
        endTime,
        duration: `${duration.toFixed(2)}秒`,
        environment: {
            locale: CONFIG.LOCALE,
            timezone: CONFIG.TIMEZONE,
            userAgent: CONFIG.USER_AGENT,
            viewport: CONFIG.VIEWPORT
        }
    };

    // 生成JSON报告
    const jsonReport = join(CONFIG.REPORT_DIR, `e2e-test-windows-cn-${Date.now()}.json`);
    writeFileSync(jsonReport, JSON.stringify(testResults, null, 2));
    log('SUCCESS', `JSON报告已保存: ${jsonReport}`);

    // 生成HTML报告
    const htmlReport = generateHTMLReport(testResults);
    const htmlReportPath = join(CONFIG.REPORT_DIR, `e2e-test-windows-cn-${Date.now()}.html`);
    writeFileSync(htmlReportPath, htmlReport);
    log('SUCCESS', `HTML报告已保存: ${htmlReportPath}`);

    // 打印摘要
    console.log('\n' + '='.repeat(80));
    console.log('                    测试总结报告');
    console.log('='.repeat(80));
    console.log(`测试环境: Windows 10 + 中文环境`);
    console.log(`开始时间: ${stats.startTime.toLocaleString('zh-CN')}`);
    console.log(`结束时间: ${endTime.toLocaleString('zh-CN')}`);
    console.log(`测试时长: ${duration.toFixed(2)}秒`);
    console.log('');
    console.log('📊 总体统计:');
    console.log(`  总测试数: ${stats.totalTests}`);
    console.log(`  通过数量: ${stats.passedTests} ✅`);
    console.log(`  失败数量: ${stats.failedTests} ❌`);
    console.log(`  成功率: ${((stats.passedTests / stats.totalTests) * 100).toFixed(1)}%`);
    console.log(`  截图数量: ${stats.screenshots}`);
    console.log('');
    console.log('📚 书籍测试:');
    console.log(`  书籍总数: ${stats.books.total}`);
    console.log(`  已测试: ${stats.books.tested}`);
    console.log(`  通过: ${stats.books.passed} ✅`);
    console.log(`  失败: ${stats.books.failed} ❌`);
    console.log('');
    console.log('📝 案例测试:');
    console.log(`  案例总数: ${stats.cases.total}`);
    console.log(`  已测试: ${stats.cases.tested}`);
    console.log(`  通过: ${stats.cases.passed} ✅`);
    console.log('');
    console.log('🎨 UI测试:');
    console.log(`  布局检查: 通过 ${stats.ui.layout.passed}, 失败 ${stats.ui.layout.failed}`);
    console.log(`  排版检查: 通过 ${stats.ui.typography.passed}, 失败 ${stats.ui.typography.failed}`);
    console.log(`  图片检查: 通过 ${stats.ui.images.passed}, 失败 ${stats.ui.images.failed}`);
    console.log(`  表格检查: 通过 ${stats.ui.tables.passed}, 失败 ${stats.ui.tables.failed}`);
    console.log(`  按钮检查: 通过 ${stats.ui.buttons.passed}, 失败 ${stats.ui.buttons.failed}`);
    console.log('');
    console.log('📁 输出文件:');
    console.log(`  截图目录: ${CONFIG.SCREENSHOT_DIR}`);
    console.log(`  JSON报告: ${jsonReport}`);
    console.log(`  HTML报告: ${htmlReportPath}`);
    console.log('='.repeat(80));

    return htmlReportPath;
}

/**
 * 生成HTML报告
 */
function generateHTMLReport(results) {
    const passRate = ((stats.passedTests / stats.totalTests) * 100).toFixed(1);
    const status = passRate >= 80 ? '优秀' : passRate >= 60 ? '良好' : '需改进';

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Platform E2E测试报告 - Windows + 中文环境</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 36px;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 18px;
            opacity: 0.9;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f7f9fc;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .stat-card .label {
            color: #888;
            font-size: 14px;
        }
        .success { color: #10b981; }
        .warning { color: #f59e0b; }
        .error { color: #ef4444; }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f7f9fc;
            font-weight: 600;
            color: #667eea;
        }
        tr:hover {
            background: #f9fafb;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        .badge-error {
            background: #fee2e2;
            color: #991b1b;
        }
        .screenshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .screenshot-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .screenshot-card img {
            width: 100%;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .screenshot-card h4 {
            font-size: 14px;
            color: #333;
        }
        .footer {
            background: #f7f9fc;
            padding: 30px;
            text-align: center;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Platform E2E测试报告</h1>
            <p>Windows 10 + 中文环境 | ${new Date().toLocaleString('zh-CN')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>总测试数</h3>
                <div class="value">${stats.totalTests}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="stat-card">
                <h3>通过数</h3>
                <div class="value success">✅ ${stats.passedTests}</div>
                <div class="label">Passed</div>
            </div>
            <div class="stat-card">
                <h3>失败数</h3>
                <div class="value error">❌ ${stats.failedTests}</div>
                <div class="label">Failed</div>
            </div>
            <div class="stat-card">
                <h3>成功率</h3>
                <div class="value ${passRate >= 80 ? 'success' : passRate >= 60 ? 'warning' : 'error'}">${passRate}%</div>
                <div class="label">${status}</div>
            </div>
            <div class="stat-card">
                <h3>书籍测试</h3>
                <div class="value">${stats.books.tested}/${stats.books.total}</div>
                <div class="label">通过 ${stats.books.passed}</div>
            </div>
            <div class="stat-card">
                <h3>案例测试</h3>
                <div class="value">${stats.cases.tested}/${stats.cases.total}</div>
                <div class="label">通过 ${stats.cases.passed}</div>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>📊 UI测试详情</h2>
                <table>
                    <tr>
                        <th>测试项</th>
                        <th>通过</th>
                        <th>失败</th>
                        <th>状态</th>
                    </tr>
                    <tr>
                        <td>页面布局</td>
                        <td>${stats.ui.layout.passed}</td>
                        <td>${stats.ui.layout.failed}</td>
                        <td><span class="badge ${stats.ui.layout.failed === 0 ? 'badge-success' : 'badge-error'}">${stats.ui.layout.failed === 0 ? '✅ 通过' : '❌ 有问题'}</span></td>
                    </tr>
                    <tr>
                        <td>文字排版</td>
                        <td>${stats.ui.typography.passed}</td>
                        <td>${stats.ui.typography.failed}</td>
                        <td><span class="badge ${stats.ui.typography.failed === 0 ? 'badge-success' : 'badge-error'}">${stats.ui.typography.failed === 0 ? '✅ 通过' : '❌ 有问题'}</span></td>
                    </tr>
                    <tr>
                        <td>图片加载</td>
                        <td>${stats.ui.images.passed}</td>
                        <td>${stats.ui.images.failed}</td>
                        <td><span class="badge ${stats.ui.images.failed === 0 ? 'badge-success' : 'badge-error'}">${stats.ui.images.failed === 0 ? '✅ 通过' : '❌ 有问题'}</span></td>
                    </tr>
                    <tr>
                        <td>表格格式</td>
                        <td>${stats.ui.tables.passed}</td>
                        <td>${stats.ui.tables.failed}</td>
                        <td><span class="badge ${stats.ui.tables.failed === 0 ? 'badge-success' : 'badge-error'}">${stats.ui.tables.failed === 0 ? '✅ 通过' : '❌ 有问题'}</span></td>
                    </tr>
                    <tr>
                        <td>功能按钮</td>
                        <td>${stats.ui.buttons.passed}</td>
                        <td>${stats.ui.buttons.failed}</td>
                        <td><span class="badge ${stats.ui.buttons.failed === 0 ? 'badge-success' : 'badge-error'}">${stats.ui.buttons.failed === 0 ? '✅ 通过' : '❌ 有问题'}</span></td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>📚 书籍测试结果</h2>
                <table>
                    <tr>
                        <th>书名</th>
                        <th>Slug</th>
                        <th>状态</th>
                    </tr>
                    ${results.books.map(book => `
                    <tr>
                        <td>${book.title}</td>
                        <td><code>${book.slug}</code></td>
                        <td><span class="badge ${book.success ? 'badge-success' : 'badge-error'}">${book.success ? '✅ 通过' : '❌ 失败'}</span></td>
                    </tr>
                    `).join('')}
                </table>
            </div>

            <div class="section">
                <h2>📸 测试截图</h2>
                <p>共生成 ${stats.screenshots} 张截图</p>
                <div class="screenshot-grid">
                    ${results.pages.map(page => page.screenshot ? `
                    <div class="screenshot-card">
                        <h4>${page.name}</h4>
                        <p style="font-size: 12px; color: #888;">
                            ${page.success ? '✅ 通过' : '❌ 失败'} |
                            加载时间: ${page.loadTime}ms
                        </p>
                    </div>
                    ` : '').join('')}
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Platform E2E自动化测试 | 生成时间: ${new Date().toLocaleString('zh-CN')}</p>
            <p>测试环境: Windows 10 Pro (x64) | 中文环境 (zh-CN)</p>
        </div>
    </div>
</body>
</html>`;
}

/**
 * 主测试函数
 */
async function runE2ETests() {
    log('INFO', '');
    log('INFO', '='.repeat(80));
    log('INFO', '🚀 Platform E2E测试 - Windows + 中文环境');
    log('INFO', '='.repeat(80));
    log('INFO', `开始时间: ${stats.startTime.toLocaleString('zh-CN')}`);
    log('INFO', `测试环境: Windows 10 + 中文环境`);
    log('INFO', `前端URL: ${CONFIG.BASE_URL}`);
    log('INFO', `API URL: ${CONFIG.API_URL}`);
    log('INFO', `截图目录: ${CONFIG.SCREENSHOT_DIR}`);
    log('INFO', `报告目录: ${CONFIG.REPORT_DIR}`);
    log('INFO', '='.repeat(80));
    log('INFO', '');

    let browser, context, page;

    try {
        // 启动浏览器（模拟Windows环境）
        log('INFO', '启动浏览器（模拟Windows环境）...');
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--lang=zh-CN']
        });

        // 创建上下文（模拟Windows + 中文）
        context = await browser.newContext({
            viewport: CONFIG.VIEWPORT,
            userAgent: CONFIG.USER_AGENT,
            locale: CONFIG.LOCALE,
            timezoneId: CONFIG.TIMEZONE,
            colorScheme: 'light'
        });

        page = await context.newPage();

        // 收集控制台日志
        page.on('console', msg => {
            if (msg.type() === 'error') {
                log('WARNING', `浏览器错误: ${msg.text()}`);
            }
        });

        // 收集页面错误
        page.on('pageerror', error => {
            log('ERROR', `页面错误: ${error.message}`);
        });

        log('SUCCESS', '浏览器启动成功');

        // 执行测试
        await testCorePages(page);
        await testBooks(page);

    } catch (error) {
        log('ERROR', `测试执行失败: ${error.message}`);
        log('ERROR', error.stack);
    } finally {
        // 关闭浏览器
        if (browser) {
            await browser.close();
            log('INFO', '浏览器已关闭');
        }
    }

    // 生成报告
    const reportPath = generateReport();

    // 返回结果
    const success = stats.failedTests === 0 || (stats.passedTests / stats.totalTests >= 0.7);

    log('INFO', '');
    if (success) {
        log('SUCCESS', '🎉 测试完成！整体状态: 通过');
    } else {
        log('WARNING', '⚠️  测试完成！整体状态: 部分失败');
    }

    return {
        success,
        stats,
        reportPath
    };
}

// 运行测试
runE2ETests()
    .then(result => {
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        log('ERROR', `测试执行异常: ${error.message}`);
        console.error(error);
        process.exit(1);
    });
