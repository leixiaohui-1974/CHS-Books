#!/usr/bin/env node

/**
 * 简化版浏览器测试 - 通过HTML分析验证渲染
 * 不需要真实浏览器，直接分析服务端渲染的HTML
 */

const http = require('http');

async function fetchHTML(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function testTextbookPage() {
  console.log('🚀 开始HTML分析测试\n');
  console.log('=' .repeat(60));

  try {
    // 测试后端API
    console.log('📡 测试后端API...');
    const apiData = await new Promise((resolve, reject) => {
      http.get('http://localhost:8000/api/v1/textbooks/water-system-intro/chapter-01/case-water-tank', (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch(e) {
            reject(e);
          }
        });
      }).on('error', reject);
    });

    console.log(`✅ API响应正常`);
    console.log(`   - Sections: ${apiData.sections.length}个`);
    console.log(`   - 标题: ${apiData.title}`);
    console.log(`   - 代码行: ${apiData.starter_code.split('\n').length}行`);
    console.log('');

    // 测试前端页面
    console.log('🌐 获取前端HTML...');
    const html = await fetchHTML('http://localhost:3000/textbook-demo');

    console.log(`✅ 页面HTML获取成功 (${html.length} 字符)\n`);

    // 分析HTML内容
    console.log('🔍 分析页面内容...\n');

    const checks = {
      hasLoadingDiv: html.includes('interactive-textbook-loading'),
      hasLoadingText: html.includes('加载教材中'),
      hasErrorDiv: html.includes('interactive-textbook-error'),
      hasTextbookPanel: html.includes('textbook-panel'),
      hasCodePanel: html.includes('code-panel'),
      hasMonacoEditor: html.includes('monaco-editor') || html.includes('MonacoEditor'),
      hasReactMarkdown: html.includes('markdown') || html.includes('ReactMarkdown'),
      hasInteractiveTextbook: html.includes('InteractiveTextbook'),
      hasNextJS: html.includes('__next') || html.includes('Next.js'),
      hasReactQuery: html.includes('query') || html.includes('QueryClient'),
    };

    console.log('页面元素检查:');
    console.log(`  Loading Div: ${checks.hasLoadingDiv ? '✅ 存在（初始状态）' : '❌ 不存在'}`);
    console.log(`  Loading 文本: ${checks.hasLoadingText ? '✅ 存在（初始状态）' : '❌ 不存在'}`);
    console.log(`  Error Div: ${checks.hasErrorDiv ? '❌ 存在（异常）' : '✅ 不存在'}`);
    console.log(`  Textbook Panel: ${checks.hasTextbookPanel ? '✅ 已渲染' : '⏳ 未渲染（需JS）'}`);
    console.log(`  Code Panel: ${checks.hasCodePanel ? '✅ 已渲染' : '⏳ 未渲染（需JS）'}`);
    console.log(`  Monaco Editor: ${checks.hasMonacoEditor ? '✅ 引用' : '⏳ 未引用'}`);
    console.log(`  React Markdown: ${checks.hasReactMarkdown ? '✅ 引用' : '⏳ 未引用'}`);
    console.log(`  InteractiveTextbook: ${checks.hasInteractiveTextbook ? '✅ 组件存在' : '❌ 组件缺失'}`);
    console.log(`  Next.js: ${checks.hasNextJS ? '✅ 正常' : '❌ 异常'}`);
    console.log(`  React Query: ${checks.hasReactQuery ? '✅ 引用' : '⏳ 未引用'}`);
    console.log('');

    // 检查JavaScript bundles
    console.log('📦 JavaScript Bundles:');
    const scriptMatches = html.match(/<script[^>]+src="([^"]+)"/g) || [];
    console.log(`   找到 ${scriptMatches.length} 个脚本标签`);

    const hasAppJS = scriptMatches.some(s => s.includes('/app/') || s.includes('textbook-demo'));
    const hasChunks = scriptMatches.some(s => s.includes('chunks'));
    console.log(`   - App JS: ${hasAppJS ? '✅' : '❌'}`);
    console.log(`   - Chunks: ${hasChunks ? '✅' : '❌'}`);
    console.log('');

    // 分析页面结构
    console.log('🏗️  页面结构分析:');

    // 提取关键HTML片段
    const bodyMatch = html.match(/<body[^>]*>(.*?)<\/body>/s);
    if (bodyMatch) {
      const bodyContent = bodyMatch[1];
      const divCount = (bodyContent.match(/<div/g) || []).length;
      const scriptCount = (bodyContent.match(/<script/g) || []).length;
      console.log(`   - Div元素: ${divCount}个`);
      console.log(`   - Script标签: ${scriptCount}个`);

      // 检查是否有hydration标记
      const hasHydration = bodyContent.includes('__next_f') || bodyContent.includes('self.__next');
      console.log(`   - Next.js Hydration: ${hasHydration ? '✅ 存在' : '❌ 缺失'}`);
    }
    console.log('');

    // 生成测试报告
    console.log('=' .repeat(60));
    console.log('📊 测试总结\n');

    const serverSideOK = checks.hasLoadingDiv && checks.hasLoadingText && !checks.hasErrorDiv;
    const clientSideReady = checks.hasNextJS && hasAppJS && hasChunks;

    console.log(`服务端渲染: ${serverSideOK ? '✅ 正常' : '❌ 异常'}`);
    console.log(`客户端代码: ${clientSideReady ? '✅ 就绪' : '❌ 未就绪'}`);
    console.log(`API后端: ✅ 正常 (${apiData.sections.length} sections)`);
    console.log('');

    if (serverSideOK && clientSideReady) {
      console.log('✅ 页面结构正常！');
      console.log('');
      console.log('📝 说明:');
      console.log('   - 初始HTML显示loading状态（正常）');
      console.log('   - JavaScript bundles已加载');
      console.log('   - React组件将在浏览器中hydrate');
      console.log('   - API数据将通过React Query获取');
      console.log('   - 最终会渲染出完整的教材+代码编辑器界面');
      console.log('');
      console.log('⚠️  限制:');
      console.log('   - 无法测试真实浏览器中的JavaScript执行');
      console.log('   - 无法验证React Query是否正确获取数据');
      console.log('   - 无法截图验证最终渲染效果');
      console.log('');
      console.log('💡 建议:');
      console.log('   - 在本地浏览器访问: http://localhost:3000/textbook-demo');
      console.log('   - 打开浏览器开发者工具查看Console');
      console.log('   - 检查Network面板确认API调用成功');
      console.log('');
      return true;
    } else {
      console.log('❌ 发现问题！');
      if (!serverSideOK) {
        console.log('   - 服务端渲染异常');
      }
      if (!clientSideReady) {
        console.log('   - 客户端代码未就绪');
      }
      return false;
    }

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('');
    console.error('请确保:');
    console.error('  1. 后端服务运行在 http://localhost:8000');
    console.error('  2. 前端服务运行在 http://localhost:3000');
    return false;
  } finally {
    console.log('=' .repeat(60));
  }
}

// 运行测试
testTextbookPage().then(success => {
  process.exit(success ? 0 : 1);
});
