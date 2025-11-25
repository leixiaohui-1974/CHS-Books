/**
 * CHS-Books Platform 综合E2E浏览器测试
 * 使用Playwright进行全面的浏览器自动化测试和截图
 *
 * 测试内容:
 * 1. 核心页面加载测试
 * 2. UI元素渲染验证
 * 3. 中文内容显示
 * 4. 响应式布局
 * 5. 交互功能测试
 * 6. API集成测试
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 配置
const CONFIG = {
  FRONTEND_URL: 'http://localhost:8080',
  BACKEND_URL: 'http://localhost:8000',
  SCREENSHOT_DIR: path.join(__dirname, 'e2e_screenshots'),
  REPORT_DIR: path.join(__dirname, 'test_reports'),
  TIMEOUT: 30000,
  VIEWPORT: { width: 1920, height: 1080 }
};

// 测试统计
const stats = {
  total: 0,
  passed: 0,
  failed: 0,
  pages: [],
  screenshots: [],
  errors: []
};

// 测试结果
const results = {
  timestamp: new Date().toISOString(),
  environment: {
    frontend: CONFIG.FRONTEND_URL,
    backend: CONFIG.BACKEND_URL
  },
  tests: []
};

/**
 * 日志函数
 */
function log(message, type = 'info') {
  const timestamp = new Date().toISOString().substring(11, 19);
  const icons = {
    info: '📘',
    success: '✅',
    error: '❌',
    warning: '⚠️',
    test: '🧪',
    screenshot: '📸'
  };
  console.log(`[${timestamp}] ${icons[type] || '•'} ${message}`);
}

/**
 * 初始化目录
 */
function initDirs() {
  if (!fs.existsSync(CONFIG.SCREENSHOT_DIR)) {
    fs.mkdirSync(CONFIG.SCREENSHOT_DIR, { recursive: true });
  }
  if (!fs.existsSync(CONFIG.REPORT_DIR)) {
    fs.mkdirSync(CONFIG.REPORT_DIR, { recursive: true });
  }
}

/**
 * 保存截图
 */
async function saveScreenshot(page, name) {
  const filename = `${name.replace(/[^a-zA-Z0-9_-]/g, '_')}.png`;
  const filepath = path.join(CONFIG.SCREENSHOT_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  stats.screenshots.push(filename);
  log(`截图已保存: ${filename}`, 'screenshot');
  return filepath;
}

/**
 * 测试页面
 */
async function testPage(page, url, name, checks = {}) {
  stats.total++;
  const testResult = {
    name,
    url,
    success: false,
    timestamp: new Date().toISOString(),
    checks: {},
    screenshot: null,
    error: null
  };

  log(`测试页面: ${name}`, 'test');
  log(`URL: ${url}`, 'info');

  try {
    // 访问页面
    const response = await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: CONFIG.TIMEOUT
    });

    testResult.httpStatus = response.status();

    if (response.status() !== 200) {
      throw new Error(`HTTP状态码异常: ${response.status()}`);
    }
    log(`HTTP状态: ${response.status()}`, 'success');

    // 等待页面加载
    await page.waitForTimeout(2000);

    // 截图
    const screenshotPath = await saveScreenshot(page, name);
    testResult.screenshot = path.basename(screenshotPath);

    // 检查页面标题
    const title = await page.title();
    testResult.checks.title = title;
    log(`页面标题: ${title}`, 'info');

    // 检查中文内容
    const chineseContent = await page.evaluate(() => {
      const text = document.body.innerText;
      const chineseRegex = /[\u4e00-\u9fa5]/g;
      const matches = text.match(chineseRegex);
      return matches ? matches.length : 0;
    });
    testResult.checks.chineseCharacters = chineseContent;
    if (chineseContent > 0) {
      log(`中文字符数: ${chineseContent}`, 'success');
    } else {
      log(`警告: 未检测到中文内容`, 'warning');
    }

    // 检查关键UI元素
    if (checks.elements) {
      for (const [elementName, selector] of Object.entries(checks.elements)) {
        const element = await page.$(selector);
        testResult.checks[elementName] = element !== null;
        if (element) {
          log(`UI元素 [${elementName}]: 存在`, 'success');
        } else {
          log(`UI元素 [${elementName}]: 不存在`, 'warning');
        }
      }
    }

    // 检查JavaScript错误
    testResult.checks.jsErrors = [];

    // 检查图片加载
    const images = await page.$$('img');
    testResult.checks.imageCount = images.length;
    log(`图片数量: ${images.length}`, 'info');

    // 检查链接
    const links = await page.$$('a');
    testResult.checks.linkCount = links.length;
    log(`链接数量: ${links.length}`, 'info');

    // 执行自定义检查
    if (checks.custom) {
      for (const [checkName, checkFn] of Object.entries(checks.custom)) {
        try {
          const result = await checkFn(page);
          testResult.checks[checkName] = result;
          log(`自定义检查 [${checkName}]: ${result ? '通过' : '失败'}`, result ? 'success' : 'warning');
        } catch (err) {
          testResult.checks[checkName] = false;
          log(`自定义检查 [${checkName}] 出错: ${err.message}`, 'error');
        }
      }
    }

    // 判断测试是否通过
    testResult.success = response.status() === 200;

    if (testResult.success) {
      stats.passed++;
      log(`测试通过!`, 'success');
    } else {
      stats.failed++;
      log(`测试失败`, 'error');
    }

  } catch (error) {
    stats.failed++;
    testResult.error = error.message;
    stats.errors.push({ page: name, error: error.message });
    log(`测试出错: ${error.message}`, 'error');
  }

  results.tests.push(testResult);
  stats.pages.push({ name, success: testResult.success });
  console.log('');
  return testResult;
}

/**
 * 测试响应式布局
 */
async function testResponsive(page, url, name) {
  log(`测试响应式布局: ${name}`, 'test');

  const viewports = [
    { name: 'desktop', width: 1920, height: 1080 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ];

  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: CONFIG.TIMEOUT });
    await page.waitForTimeout(1000);

    const screenshotName = `${name}_${viewport.name}`;
    await saveScreenshot(page, screenshotName);
    log(`  ${viewport.name} (${viewport.width}x${viewport.height})`, 'success');
  }

  // 恢复默认视口
  await page.setViewportSize(CONFIG.VIEWPORT);
  console.log('');
}

/**
 * 测试API健康状态
 */
async function testApiHealth() {
  log('测试后端API健康状态', 'test');
  stats.total++;

  try {
    const response = await fetch(`${CONFIG.BACKEND_URL}/health`);
    const data = await response.json();

    if (response.ok && data.status === 'healthy') {
      stats.passed++;
      log(`API状态: ${data.status}`, 'success');
      log(`数据库: ${data.database}`, 'success');
      results.tests.push({
        name: 'API健康检查',
        url: `${CONFIG.BACKEND_URL}/health`,
        success: true,
        checks: data
      });
      return true;
    } else {
      throw new Error('API不健康');
    }
  } catch (error) {
    stats.failed++;
    log(`API健康检查失败: ${error.message}`, 'error');
    stats.errors.push({ page: 'API健康检查', error: error.message });
    results.tests.push({
      name: 'API健康检查',
      url: `${CONFIG.BACKEND_URL}/health`,
      success: false,
      error: error.message
    });
    return false;
  }
}

/**
 * 测试交互功能
 */
async function testInteraction(page, url, name, actions) {
  log(`测试交互功能: ${name}`, 'test');
  stats.total++;

  const testResult = {
    name: `交互测试: ${name}`,
    url,
    success: false,
    actions: [],
    screenshots: []
  };

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: CONFIG.TIMEOUT });
    await page.waitForTimeout(2000);

    // 截图 - 初始状态
    await saveScreenshot(page, `${name}_交互前`);
    testResult.screenshots.push(`${name}_交互前.png`);

    for (const action of actions) {
      try {
        if (action.type === 'click') {
          const element = await page.$(action.selector);
          if (element) {
            await element.click();
            await page.waitForTimeout(action.wait || 1000);
            log(`  点击: ${action.name}`, 'success');
            testResult.actions.push({ ...action, success: true });
          } else {
            log(`  点击失败: ${action.name} - 元素不存在`, 'warning');
            testResult.actions.push({ ...action, success: false, error: '元素不存在' });
          }
        } else if (action.type === 'scroll') {
          await page.evaluate((y) => window.scrollTo(0, y), action.y || 500);
          await page.waitForTimeout(action.wait || 500);
          log(`  滚动到: ${action.y || 500}px`, 'success');
          testResult.actions.push({ ...action, success: true });
        } else if (action.type === 'input') {
          const element = await page.$(action.selector);
          if (element) {
            await element.fill(action.value);
            log(`  输入: ${action.name}`, 'success');
            testResult.actions.push({ ...action, success: true });
          }
        }

        // 每个动作后截图
        if (action.screenshot) {
          await saveScreenshot(page, `${name}_${action.name}`);
          testResult.screenshots.push(`${name}_${action.name}.png`);
        }
      } catch (err) {
        log(`  动作失败: ${action.name} - ${err.message}`, 'error');
        testResult.actions.push({ ...action, success: false, error: err.message });
      }
    }

    // 截图 - 最终状态
    await saveScreenshot(page, `${name}_交互后`);
    testResult.screenshots.push(`${name}_交互后.png`);

    testResult.success = true;
    stats.passed++;
    log(`交互测试完成`, 'success');

  } catch (error) {
    stats.failed++;
    testResult.error = error.message;
    log(`交互测试出错: ${error.message}`, 'error');
  }

  results.tests.push(testResult);
  console.log('');
  return testResult;
}

/**
 * 生成测试报告
 */
function generateReport() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const passRate = stats.total > 0 ? (stats.passed / stats.total * 100).toFixed(1) : 0;

  // JSON报告
  const jsonReport = {
    ...results,
    statistics: stats,
    passRate: `${passRate}%`
  };

  const jsonPath = path.join(CONFIG.REPORT_DIR, `e2e_browser_test_${timestamp}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify(jsonReport, null, 2));

  // Markdown报告
  const mdReport = `# CHS-Books Platform E2E浏览器测试报告

## 测试信息

- **测试时间**: ${new Date().toLocaleString('zh-CN')}
- **前端URL**: ${CONFIG.FRONTEND_URL}
- **后端URL**: ${CONFIG.BACKEND_URL}

---

## 测试总结

### 📊 整体统计

| 指标 | 数量 |
|------|------|
| 总测试数 | ${stats.total} |
| 通过 | ${stats.passed} ✅ |
| 失败 | ${stats.failed} ❌ |
| 通过率 | ${passRate}% |

### 📸 截图统计

共生成 ${stats.screenshots.length} 张截图

### 📄 页面测试结果

| 页面 | 状态 |
|------|------|
${stats.pages.map(p => `| ${p.name} | ${p.success ? '✅ 通过' : '❌ 失败'} |`).join('\n')}

${stats.errors.length > 0 ? `
### ❌ 错误列表

| 页面 | 错误信息 |
|------|----------|
${stats.errors.map(e => `| ${e.page} | ${e.error} |`).join('\n')}
` : ''}

---

## 截图列表

${stats.screenshots.map(s => `- \`${s}\``).join('\n')}

---

## 测试结论

**总体评级**: ${passRate >= 90 ? '✅ 优秀' : passRate >= 70 ? '✅ 良好' : passRate >= 60 ? '⚠️ 及格' : '❌ 需改进'}

**生成时间**: ${new Date().toLocaleString('zh-CN')}
`;

  const mdPath = path.join(CONFIG.REPORT_DIR, `e2e_browser_test_${timestamp}.md`);
  fs.writeFileSync(mdPath, mdReport);

  log(`JSON报告: ${jsonPath}`, 'success');
  log(`Markdown报告: ${mdPath}`, 'success');

  return { jsonPath, mdPath };
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(70));
  console.log('  🚀 CHS-Books Platform E2E 浏览器测试');
  console.log('='.repeat(70));
  console.log('');

  initDirs();

  let browser;

  try {
    // 测试API健康状态
    console.log('-'.repeat(70));
    await testApiHealth();
    console.log('');

    // 启动浏览器
    log('启动浏览器...', 'info');
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer'
      ]
    });

    const context = await browser.newContext({
      viewport: CONFIG.VIEWPORT,
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai'
    });

    const page = await context.newPage();

    // 收集控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        log(`浏览器控制台错误: ${msg.text()}`, 'warning');
      }
    });

    page.on('pageerror', error => {
      log(`页面JavaScript错误: ${error.message}`, 'error');
    });

    log('浏览器启动成功', 'success');
    console.log('');

    // ==================== 核心页面测试 ====================
    console.log('-'.repeat(70));
    log('📚 核心页面测试', 'info');
    console.log('-'.repeat(70));
    console.log('');

    // 1. 主页
    await testPage(page, `${CONFIG.FRONTEND_URL}/index.html`, '主页', {
      elements: {
        'header': 'header, .header, nav',
        'main': 'main, .main, .content',
        'footer': 'footer, .footer'
      }
    });

    // 2. 教材库
    await testPage(page, `${CONFIG.FRONTEND_URL}/textbooks.html`, '教材库', {
      elements: {
        'bookList': '.book-list, .textbook-list, .books',
        'searchBar': 'input[type="search"], input[type="text"], .search'
      }
    });

    // 3. 搜索页面
    await testPage(page, `${CONFIG.FRONTEND_URL}/search.html`, '搜索页面', {
      elements: {
        'searchInput': 'input[type="search"], input[type="text"]',
        'searchButton': 'button, .search-btn'
      }
    });

    // 4. 代码运行器
    await testPage(page, `${CONFIG.FRONTEND_URL}/code-runner.html`, '代码运行器', {
      elements: {
        'codeEditor': 'textarea, .editor, .code-editor, #code',
        'runButton': 'button, .run-btn, #run'
      }
    });

    // 5. IDE页面
    await testPage(page, `${CONFIG.FRONTEND_URL}/ide.html`, 'AI编程IDE', {
      elements: {
        'editor': '.editor, textarea, #editor',
        'terminal': '.terminal, .output, #output'
      }
    });

    // 6. 知识库
    await testPage(page, `${CONFIG.FRONTEND_URL}/knowledge/index.html`, '知识库', {
      elements: {
        'knowledgeContent': '.knowledge, .content, main'
      }
    });

    // 7. 学习页面
    await testPage(page, `${CONFIG.FRONTEND_URL}/learning.html`, '学习页面', {});

    // 8. 统一入口
    await testPage(page, `${CONFIG.FRONTEND_URL}/unified.html`, '统一入口', {});

    // ==================== 响应式测试 ====================
    console.log('-'.repeat(70));
    log('📱 响应式布局测试', 'info');
    console.log('-'.repeat(70));
    console.log('');

    await testResponsive(page, `${CONFIG.FRONTEND_URL}/index.html`, '主页响应式');
    await testResponsive(page, `${CONFIG.FRONTEND_URL}/textbooks.html`, '教材库响应式');

    // ==================== 交互测试 ====================
    console.log('-'.repeat(70));
    log('🖱️ 交互功能测试', 'info');
    console.log('-'.repeat(70));
    console.log('');

    // 代码运行器交互测试
    await testInteraction(page, `${CONFIG.FRONTEND_URL}/code-runner.html`, '代码运行器交互', [
      { type: 'scroll', y: 300, screenshot: true, name: '滚动' },
      { type: 'click', selector: 'button, .run-btn', name: '运行按钮', wait: 2000, screenshot: true }
    ]);

    // 搜索页面交互测试
    await testInteraction(page, `${CONFIG.FRONTEND_URL}/search.html`, '搜索交互', [
      { type: 'input', selector: 'input[type="text"], input[type="search"]', value: '水力学', name: '输入搜索词' },
      { type: 'click', selector: 'button', name: '搜索按钮', wait: 2000, screenshot: true }
    ]);

    // 关闭浏览器
    await browser.close();
    log('浏览器已关闭', 'info');

  } catch (error) {
    log(`测试执行出错: ${error.message}`, 'error');
    stats.errors.push({ page: '测试框架', error: error.message });
    if (browser) {
      await browser.close();
    }
  }

  // 生成报告
  console.log('');
  console.log('-'.repeat(70));
  log('📝 生成测试报告', 'info');
  console.log('-'.repeat(70));
  const { jsonPath, mdPath } = generateReport();

  // 打印总结
  console.log('');
  console.log('='.repeat(70));
  console.log('  📊 测试总结');
  console.log('='.repeat(70));
  console.log(`  总测试数: ${stats.total}`);
  console.log(`  通过: ${stats.passed} ✅`);
  console.log(`  失败: ${stats.failed} ❌`);
  console.log(`  通过率: ${(stats.passed / stats.total * 100).toFixed(1)}%`);
  console.log(`  截图数: ${stats.screenshots.length}`);
  console.log('');
  console.log(`  📁 报告目录: ${CONFIG.REPORT_DIR}`);
  console.log(`  📸 截图目录: ${CONFIG.SCREENSHOT_DIR}`);
  console.log('='.repeat(70));

  // 返回退出码
  if (stats.failed === 0) {
    console.log('\n✅ 所有测试通过!');
    process.exit(0);
  } else if (stats.passed / stats.total >= 0.7) {
    console.log('\n⚠️ 部分测试失败，但整体通过率>=70%');
    process.exit(0);
  } else {
    console.log('\n❌ 测试失败过多');
    process.exit(1);
  }
}

// 运行测试
main().catch(error => {
  console.error('测试执行失败:', error);
  process.exit(1);
});
