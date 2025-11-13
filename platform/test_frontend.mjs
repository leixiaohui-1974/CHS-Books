#!/usr/bin/env node
/**
 * 前端功能测试脚本
 * 使用Playwright进行浏览器测试和截图
 */

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

// 创建截图目录
const screenshotDir = '/workspace/platform/test_screenshots';
try {
    mkdirSync(screenshotDir, { recursive: true });
} catch (e) {}

// 测试配置
const BASE_URL = 'http://localhost:8080';
const API_URL = 'http://localhost:8000';

const tests = [
    {
        name: '主页',
        url: `${BASE_URL}/`,
        screenshot: 'index.png',
        checks: [
            { type: 'title', value: '水系统控制理论教程' },
            { type: 'text', value: '智能学习平台' },
            { type: 'element', selector: '.nav-card' }
        ]
    },
    {
        name: '教材库',
        url: `${BASE_URL}/textbooks.html`,
        screenshot: 'textbooks.png',
        checks: [
            { type: 'title', value: '教材' },
            { type: 'element', selector: '.book-card' }
        ]
    },
    {
        name: '搜索页面',
        url: `${BASE_URL}/search.html`,
        screenshot: 'search.png',
        checks: [
            { type: 'title', value: '搜索' },
            { type: 'element', selector: 'input[type="search"], input.search' }
        ]
    },
    {
        name: '代码运行器',
        url: `${BASE_URL}/code-runner.html`,
        screenshot: 'code-runner.png',
        checks: [
            { type: 'title', value: '代码' },
            { type: 'element', selector: 'textarea, .code-editor' }
        ]
    },
    {
        name: 'IDE',
        url: `${BASE_URL}/ide.html`,
        screenshot: 'ide.png',
        checks: [
            { type: 'title', value: 'IDE' }
        ]
    },
    {
        name: '知识库',
        url: `${BASE_URL}/knowledge/index.html`,
        screenshot: 'knowledge.png',
        checks: [
            { type: 'title', value: '知识' }
        ]
    }
];

// 测试结果
const results = [];

async function runTests() {
    console.log('=' .repeat(60));
    console.log('开始前端功能测试...');
    console.log('=' .repeat(60));
    console.log(`前端URL: ${BASE_URL}`);
    console.log(`后端URL: ${API_URL}`);
    console.log(`截图目录: ${screenshotDir}`);
    console.log('=' .repeat(60));
    console.log('');

    // 启动浏览器
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    
    const page = await context.newPage();

    // 运行每个测试
    for (const test of tests) {
        console.log(`\n测试: ${test.name}`);
        console.log(`URL: ${test.url}`);
        
        const result = {
            name: test.name,
            url: test.url,
            success: false,
            checks: [],
            error: null,
            screenshot: test.screenshot
        };

        try {
            // 访问页面
            const response = await page.goto(test.url, {
                waitUntil: 'networkidle',
                timeout: 10000
            });

            if (!response) {
                throw new Error('无法加载页面');
            }

            const status = response.status();
            console.log(`  HTTP状态: ${status}`);
            
            if (status !== 200) {
                throw new Error(`HTTP错误: ${status}`);
            }

            // 等待页面加载
            await page.waitForTimeout(2000);

            // 执行检查
            for (const check of test.checks) {
                let checkResult = { ...check, passed: false };
                
                try {
                    if (check.type === 'title') {
                        const title = await page.title();
                        checkResult.passed = title.includes(check.value);
                        checkResult.actual = title;
                        console.log(`  ✓ 标题检查: "${title}"`);
                    } else if (check.type === 'text') {
                        const content = await page.content();
                        checkResult.passed = content.includes(check.value);
                        console.log(`  ✓ 文本检查: "${check.value}" ${checkResult.passed ? '找到' : '未找到'}`);
                    } else if (check.type === 'element') {
                        const element = await page.$(check.selector);
                        checkResult.passed = element !== null;
                        console.log(`  ✓ 元素检查: "${check.selector}" ${checkResult.passed ? '存在' : '不存在'}`);
                    }
                } catch (e) {
                    checkResult.error = e.message;
                    console.log(`  ✗ 检查失败: ${e.message}`);
                }
                
                result.checks.push(checkResult);
            }

            // 截图
            const screenshotPath = join(screenshotDir, test.screenshot);
            await page.screenshot({
                path: screenshotPath,
                fullPage: true
            });
            console.log(`  📸 截图已保存: ${test.screenshot}`);

            result.success = result.checks.length === 0 || result.checks.some(c => c.passed);
            console.log(`  ${result.success ? '✅ 测试通过' : '❌ 测试失败'}`);

        } catch (error) {
            result.error = error.message;
            console.log(`  ❌ 错误: ${error.message}`);
            
            // 尝试截图即使出错
            try {
                const screenshotPath = join(screenshotDir, `error_${test.screenshot}`);
                await page.screenshot({ path: screenshotPath });
                console.log(`  📸 错误截图: error_${test.screenshot}`);
            } catch (e) {}
        }

        results.push(result);
    }

    await browser.close();

    // 生成报告
    console.log('\n' + '=' .repeat(60));
    console.log('测试报告');
    console.log('=' .repeat(60));
    
    const passedTests = results.filter(r => r.success).length;
    const totalTests = results.length;
    
    console.log(`\n总计: ${totalTests} 个测试`);
    console.log(`通过: ${passedTests} 个`);
    console.log(`失败: ${totalTests - passedTests} 个`);
    console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

    // 保存JSON报告
    const reportPath = join(screenshotDir, 'test_report.json');
    writeFileSync(reportPath, JSON.stringify({
        timestamp: new Date().toISOString(),
        summary: {
            total: totalTests,
            passed: passedTests,
            failed: totalTests - passedTests,
            successRate: ((passedTests / totalTests) * 100).toFixed(1) + '%'
        },
        results
    }, null, 2));
    
    console.log(`\n📄 详细报告: ${reportPath}`);
    console.log(`📁 截图目录: ${screenshotDir}`);
    console.log('\n' + '=' .repeat(60));
    
    return results;
}

// 运行测试
runTests().catch(console.error);
