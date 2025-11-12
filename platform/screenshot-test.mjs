/**
 * 浏览器截图测试 - 使用Playwright
 * 配置优化以避免崩溃
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function captureScreenshots() {
  console.log('🚀 启动浏览器截图测试...\n');

  let browser;
  try {
    // 启动浏览器 - 使用稳定配置
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-extensions'
      ]
    });

    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
    });

    const page = await context.newPage();

    // 收集控制台日志
    const consoleLogs = [];
    const errors = [];

    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push({ type: msg.type(), text });
      if (msg.type() === 'error') {
        console.log(`[浏览器错误] ${text}`);
      }
    });

    page.on('pageerror', error => {
      errors.push(error.message);
      console.error(`[页面错误] ${error.message}`);
    });

    console.log('📍 访问页面: http://localhost:3000/textbook-demo\n');

    // 访问页面
    try {
      const response = await page.goto('http://localhost:3000/textbook-demo', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });

      console.log(`✅ 页面加载成功 (HTTP ${response.status()})\n`);

      // 等待一段时间让React组件渲染
      console.log('⏳ 等待React渲染（10秒）...\n');
      await page.waitForTimeout(10000);

      // 截图1：初始状态
      const screenshotDir = path.join(process.cwd(), 'screenshots');
      if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
      }

      const screenshot1 = path.join(screenshotDir, '01-initial-load.png');
      await page.screenshot({ path: screenshot1, fullPage: true });
      console.log(`📸 截图1已保存: ${screenshot1}`);

      // 检查页面元素
      const hasLoading = await page.$('.interactive-textbook-loading');
      const hasError = await page.$('.interactive-textbook-error');
      const hasTextbook = await page.$('.textbook-panel');
      const hasCode = await page.$('.code-panel');

      console.log('\n🔍 页面元素检测:');
      console.log(`   Loading组件: ${hasLoading ? '❌ 仍存在（异常）' : '✅ 已消失'}`);
      console.log(`   Error组件: ${hasError ? '❌ 存在（异常）' : '✅ 不存在'}`);
      console.log(`   Textbook面板: ${hasTextbook ? '✅ 已渲染' : '❌ 未渲染'}`);
      console.log(`   Code面板: ${hasCode ? '✅ 已渲染' : '❌ 未渲染'}`);

      // 如果内容已渲染，进行交互测试
      if (hasTextbook && hasCode) {
        console.log('\n✅ 内容已成功渲染！进行交互测试...\n');

        // 截图2：完整页面
        const screenshot2 = path.join(screenshotDir, '02-full-page.png');
        await page.screenshot({ path: screenshot2, fullPage: true });
        console.log(`📸 截图2已保存: ${screenshot2}`);

        // 截图3：教材面板特写
        if (hasTextbook) {
          const screenshot3 = path.join(screenshotDir, '03-textbook-panel.png');
          await hasTextbook.screenshot({ path: screenshot3 });
          console.log(`📸 截图3已保存（教材面板）: ${screenshot3}`);
        }

        // 截图4：代码面板特写
        if (hasCode) {
          const screenshot4 = path.join(screenshotDir, '04-code-panel.png');
          await hasCode.screenshot({ path: screenshot4 });
          console.log(`📸 截图4已保存（代码面板）: ${screenshot4}`);
        }

        // 模拟滚动
        console.log('\n📜 测试滚动功能...');
        await page.evaluate(() => {
          const textbook = document.querySelector('.textbook-panel');
          if (textbook) {
            textbook.scrollTop = 200;
          }
        });
        await page.waitForTimeout(1000);

        const screenshot5 = path.join(screenshotDir, '05-after-scroll.png');
        await page.screenshot({ path: screenshot5, fullPage: true });
        console.log(`📸 截图5已保存（滚动后）: ${screenshot5}`);

      } else {
        console.log('\n⚠️  内容未完全渲染，可能仍在Loading状态');

        // 获取页面HTML以供分析
        const html = await page.content();
        const htmlFile = path.join(screenshotDir, 'page-source.html');
        fs.writeFileSync(htmlFile, html);
        console.log(`📄 页面HTML已保存: ${htmlFile}`);
      }

      // 检查网络请求
      console.log('\n🌐 检查网络请求...');
      const apiCalls = consoleLogs.filter(log =>
        log.text.includes('textbooks') || log.text.includes('API')
      );

      if (apiCalls.length > 0) {
        console.log('   API相关日志:');
        apiCalls.forEach(call => {
          console.log(`     [${call.type}] ${call.text}`);
        });
      } else {
        console.log('   ⚠️  未发现API调用日志');
      }

      // 生成测试报告
      const report = {
        timestamp: new Date().toISOString(),
        url: 'http://localhost:3000/textbook-demo',
        httpStatus: response.status(),
        elements: {
          hasLoading: hasLoading !== null,
          hasError: hasError !== null,
          hasTextbook: hasTextbook !== null,
          hasCode: hasCode !== null
        },
        consoleLogs: consoleLogs.length,
        errors: errors.length,
        screenshots: fs.readdirSync(screenshotDir).filter(f => f.endsWith('.png'))
      };

      const reportFile = path.join(screenshotDir, 'test-report.json');
      fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
      console.log(`\n📊 测试报告已保存: ${reportFile}`);

      // 最终结果
      console.log('\n' + '='.repeat(60));
      console.log('📊 测试结果总结');
      console.log('='.repeat(60));

      const success = hasTextbook && hasCode && !hasLoading && !hasError;

      if (success) {
        console.log('✅ 测试成功！页面正常渲染');
        console.log(`   - 截图数量: ${report.screenshots.length}张`);
        console.log(`   - 控制台日志: ${consoleLogs.length}条`);
        console.log(`   - JavaScript错误: ${errors.length}个`);
        console.log(`\n📁 截图目录: ${screenshotDir}`);
        return true;
      } else {
        console.log('❌ 测试失败！发现问题:');
        if (hasLoading) console.log('   - 仍显示Loading状态');
        if (hasError) console.log('   - 存在Error组件');
        if (!hasTextbook) console.log('   - 教材面板未渲染');
        if (!hasCode) console.log('   - 代码面板未渲染');
        if (errors.length > 0) console.log(`   - ${errors.length}个JavaScript错误`);
        console.log(`\n📁 截图和日志保存在: ${screenshotDir}`);
        return false;
      }

    } catch (navError) {
      console.error('❌ 页面导航失败:', navError.message);
      return false;
    }

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    return false;
  } finally {
    if (browser) {
      await browser.close();
      console.log('\n🔒 浏览器已关闭');
    }
  }
}

// 运行测试
captureScreenshots().then(success => {
  console.log('\n' + '='.repeat(60));
  console.log(success ? '✅ 测试完成！' : '❌ 测试失败！');
  console.log('='.repeat(60));
  process.exit(success ? 0 : 1);
});
