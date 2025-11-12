/**
 * 浏览器自动化测试 - 检测前端渲染问题
 * 使用Playwright测试教材Demo页面
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function testTextbookDemo() {
  console.log('🚀 启动浏览器测试...\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 收集控制台日志和错误
  const consoleLogs = [];
  const errors = [];

  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push({ type: msg.type(), text });
    console.log(`[浏览器 ${msg.type()}] ${text}`);
  });

  page.on('pageerror', error => {
    errors.push(error.message);
    console.error(`[页面错误] ${error.message}`);
  });

  try {
    console.log('📍 访问: http://localhost:3000/textbook-demo\n');

    // 访问页面
    const response = await page.goto('http://localhost:3000/textbook-demo', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log(`✅ 页面加载完成 (HTTP ${response.status()})\n`);

    // 等待5秒观察动态渲染
    console.log('⏳ 等待5秒观察React渲染...\n');
    await page.waitForTimeout(5000);

    // 截图
    const screenshotPath = path.join(process.cwd(), 'logs', 'screenshot.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存: ${screenshotPath}\n`);

    // 检查页面内容
    const bodyText = await page.textContent('body');
    const hasLoadingText = bodyText.includes('加载教材中');
    const hasErrorText = bodyText.includes('教材加载失败');
    const hasContent = bodyText.includes('水箱实验') || bodyText.includes('代码编辑器');

    // 检查关键元素
    const loadingSpinner = await page.$('.interactive-textbook-loading');
    const errorDiv = await page.$('.interactive-textbook-error');
    const textbookPanel = await page.$('.textbook-panel');
    const codePanel = await page.$('.code-panel');

    // 收集测试结果
    const results = {
      timestamp: new Date().toISOString(),
      url: 'http://localhost:3000/textbook-demo',
      httpStatus: response.status(),
      hasLoadingText,
      hasErrorText,
      hasContent,
      elements: {
        loadingSpinner: loadingSpinner !== null,
        errorDiv: errorDiv !== null,
        textbookPanel: textbookPanel !== null,
        codePanel: codePanel !== null
      },
      consoleLogs,
      errors,
      screenshot: screenshotPath
    };

    // 打印测试结果
    console.log('=' .repeat(60));
    console.log('📊 测试结果');
    console.log('=' .repeat(60));
    console.log(`HTTP状态: ${results.httpStatus}`);
    console.log(`包含"加载教材中": ${hasLoadingText ? '❌ 是（异常）' : '✅ 否'}`);
    console.log(`包含"加载失败": ${hasErrorText ? '❌ 是（异常）' : '✅ 否'}`);
    console.log(`包含教材内容: ${hasContent ? '✅ 是' : '❌ 否（异常）'}`);
    console.log('');
    console.log('关键元素检测:');
    console.log(`  Loading Spinner: ${results.elements.loadingSpinner ? '❌ 存在（应该消失）' : '✅ 不存在'}`);
    console.log(`  Error Div: ${results.elements.errorDiv ? '❌ 存在' : '✅ 不存在'}`);
    console.log(`  Textbook Panel: ${results.elements.textbookPanel ? '✅ 存在' : '❌ 不存在'}`);
    console.log(`  Code Panel: ${results.elements.codePanel ? '✅ 存在' : '❌ 不存在'}`);
    console.log('');
    console.log(`控制台日志数量: ${consoleLogs.length}`);
    console.log(`JavaScript错误数量: ${errors.length}`);
    console.log('');

    if (errors.length > 0) {
      console.log('⚠️  JavaScript错误:');
      errors.forEach((err, i) => {
        console.log(`  ${i + 1}. ${err}`);
      });
      console.log('');
    }

    // 查找React Query相关日志
    const queryLogs = consoleLogs.filter(log =>
      log.text.includes('query') ||
      log.text.includes('fetch') ||
      log.text.includes('textbook') ||
      log.text.includes('API')
    );

    if (queryLogs.length > 0) {
      console.log('🔍 React Query相关日志:');
      queryLogs.forEach(log => {
        console.log(`  [${log.type}] ${log.text}`);
      });
      console.log('');
    }

    // 保存详细报告
    const reportPath = path.join(process.cwd(), 'logs', 'browser-test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`📄 详细报告已保存: ${reportPath}\n`);

    // 判断测试是否通过
    const testPassed =
      results.httpStatus === 200 &&
      !hasLoadingText &&
      !hasErrorText &&
      hasContent &&
      results.elements.textbookPanel &&
      results.elements.codePanel &&
      !results.elements.loadingSpinner &&
      errors.length === 0;

    console.log('=' .repeat(60));
    if (testPassed) {
      console.log('✅ 测试通过！前端渲染正常');
    } else {
      console.log('❌ 测试失败！发现以下问题:');
      if (hasLoadingText) console.log('  - 仍然显示"加载教材中"');
      if (hasErrorText) console.log('  - 显示错误信息');
      if (!hasContent) console.log('  - 缺少教材内容');
      if (!results.elements.textbookPanel) console.log('  - 教材面板未渲染');
      if (!results.elements.codePanel) console.log('  - 代码面板未渲染');
      if (results.elements.loadingSpinner) console.log('  - Loading spinner未消失');
      if (errors.length > 0) console.log(`  - ${errors.length}个JavaScript错误`);
    }
    console.log('=' .repeat(60));

    return { success: testPassed, results };

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// 运行测试
testTextbookDemo()
  .then(result => {
    process.exit(result.success ? 0 : 1);
  })
  .catch(error => {
    console.error('测试执行失败:', error);
    process.exit(1);
  });
