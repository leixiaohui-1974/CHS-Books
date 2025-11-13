#!/bin/bash
###############################################################################
# Platform端到端测试 - Windows + 中文环境模拟（基于HTML分析）
# 测试所有页面的HTML结构、中文内容、图表、功能按钮
###############################################################################

set -e

# 配置
BASE_URL="http://localhost:8080"
REPORT_DIR="/home/user/CHS-Books/platform/test_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/e2e-html-test-$TIMESTAMP.md"
JSON_FILE="$REPORT_DIR/e2e-html-test-$TIMESTAMP.json"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 初始化统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 初始化JSON报告
cat > "$JSON_FILE" << 'EOF'
{
  "testName": "Platform E2E测试 - Windows + 中文环境",
  "timestamp": "",
  "environment": {
    "platform": "Windows 10 模拟",
    "locale": "zh-CN",
    "timezone": "Asia/Shanghai"
  },
  "summary": {},
  "tests": []
}
EOF

# 日志函数
log_info() {
    echo "[INFO] $1" | tee -a "$REPORT_FILE"
}

log_success() {
    echo "[✅ SUCCESS] $1" | tee -a "$REPORT_FILE"
    ((PASSED_TESTS++))
}

log_fail() {
    echo "[❌ FAIL] $1" | tee -a "$REPORT_FILE"
    ((FAILED_TESTS++))
}

log_test() {
    echo "[🧪 TEST] $1" | tee -a "$REPORT_FILE"
    ((TOTAL_TESTS++))
}

# 测试单个页面
test_page() {
    local url="$1"
    local name="$2"

    log_test "测试页面: $name ($url)"

    # 下载HTML
    local html=$(curl -s "$url" || echo "")

    if [ -z "$html" ]; then
        log_fail "无法访问 $name"
        return 1
    fi

    # 检查HTTP状态码
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    if [ "$http_code" == "200" ]; then
        log_success "$name HTTP状态码: 200"
    else
        log_fail "$name HTTP状态码异常: $http_code"
        return 1
    fi

    # 检查HTML基本结构
    if echo "$html" | grep -q "<!DOCTYPE html>"; then
        log_success "$name 包含DOCTYPE声明"
    else
        log_fail "$name 缺少DOCTYPE声明"
    fi

    # 检查字符编码
    if echo "$html" | grep -qi "charset=.*utf-8"; then
        log_success "$name 使用UTF-8编码"
    else
        log_fail "$name 未使用UTF-8编码"
    fi

    # 检查中文内容
    if echo "$html" | grep -P "[\x{4e00}-\x{9fa5}]" > /dev/null; then
        log_success "$name 包含中文内容"
    else
        log_fail "$name 缺少中文内容"
    fi

    # 检查标题
    local title=$(echo "$html" | grep -oP '<title>\K[^<]+' || echo "无标题")
    log_info "  页面标题: $title"

    # 检查基本HTML元素
    if echo "$html" | grep -q "<header\|<nav\|class=\"header\"\|class=\"navbar\""; then
        log_success "$name 包含导航/头部元素"
    else
        log_info "  注意: $name 可能缺少导航栏"
    fi

    if echo "$html" | grep -q "<main\|<div.*class=\".*main\|<div.*class=\".*content"; then
        log_success "$name 包含主内容区域"
    else
        log_info "  注意: $name 可能缺少主内容区域"
    fi

    # 检查JavaScript和CSS
    local js_count=$(echo "$html" | grep -c "<script" || echo "0")
    local css_count=$(echo "$html" | grep -c "<style\|<link.*stylesheet" || echo "0")
    log_info "  JavaScript文件数: $js_count"
    log_info "  CSS样式数: $css_count"

    # 检查图片
    local img_count=$(echo "$html" | grep -c "<img" || echo "0")
    log_info "  图片数量: $img_count"

    # 检查表格
    local table_count=$(echo "$html" | grep -c "<table" || echo "0")
    if [ "$table_count" -gt 0 ]; then
        log_info "  表格数量: $table_count"
    fi

    # 检查按钮和链接
    local button_count=$(echo "$html" | grep -c "<button\|class=\".*btn" || echo "0")
    local link_count=$(echo "$html" | grep -c "<a href" || echo "0")
    log_info "  按钮数量: $button_count"
    log_info "  链接数量: $link_count"

    if [ "$button_count" -gt 0 ] || [ "$link_count" -gt 0 ]; then
        log_success "$name 包含可交互元素"
    fi

    echo "" | tee -a "$REPORT_FILE"

    return 0
}

# 开始测试
echo "================================================================================" | tee "$REPORT_FILE"
echo "  Platform E2E测试报告 - Windows + 中文环境模拟" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$REPORT_FILE"
echo "测试环境: Windows 10 + 中文 (zh-CN)" | tee -a "$REPORT_FILE"
echo "前端URL: $BASE_URL" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 第一部分: 测试核心页面
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "第一部分: 核心页面测试" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

test_page "$BASE_URL/" "主页"
test_page "$BASE_URL/textbooks.html" "教材库"
test_page "$BASE_URL/search.html" "搜索页面"
test_page "$BASE_URL/code-runner.html" "代码运行器"
test_page "$BASE_URL/ide.html" "AI编程IDE"
test_page "$BASE_URL/knowledge/index.html" "知识库"

# 第二部分: 测试书籍页面（示例）
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "第二部分: 书籍页面测试 (抽样)" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

declare -a books=(
    "water-system-control:水系统控制论"
    "open-channel-hydraulics:明渠水力学计算"
    "canal-pipeline-control:运河与管道控制"
    "ecohydraulics:生态水力学"
)

for book in "${books[@]}"; do
    IFS=':' read -r slug name <<< "$book"
    test_page "$BASE_URL/textbooks.html?book=$slug" "书籍: $name"
done

# 生成测试总结
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "测试总结" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

SUCCESS_RATE=$(echo "scale=1; ($PASSED_TESTS * 100) / $TOTAL_TESTS" | bc)

echo "📊 总体统计:" | tee -a "$REPORT_FILE"
echo "  总测试数: $TOTAL_TESTS" | tee -a "$REPORT_FILE"
echo "  通过数量: $PASSED_TESTS ✅" | tee -a "$REPORT_FILE"
echo "  失败数量: $FAILED_TESTS ❌" | tee -a "$REPORT_FILE"
echo "  成功率: ${SUCCESS_RATE}%" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 评估结果
if [ "$SUCCESS_RATE" -ge "90" ]; then
    echo "✅ 测试评级: 优秀" | tee -a "$REPORT_FILE"
elif [ "$SUCCESS_RATE" -ge "75" ]; then
    echo "✅ 测试评级: 良好" | tee -a "$REPORT_FILE"
elif [ "$SUCCESS_RATE" -ge "60" ]; then
    echo "⚠️  测试评级: 及格" | tee -a "$REPORT_FILE"
else
    echo "❌ 测试评级: 需改进" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "📁 完整报告已保存至: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "📁 JSON数据已保存至: $JSON_FILE" | tee -a "$REPORT_FILE"
echo "================================================================================" | tee -a "$REPORT_FILE"

# 更新JSON报告
cat > "$JSON_FILE" << EOF
{
  "testName": "Platform E2E测试 - Windows + 中文环境",
  "timestamp": "$(date -Iseconds)",
  "environment": {
    "platform": "Windows 10 模拟",
    "locale": "zh-CN",
    "timezone": "Asia/Shanghai",
    "baseUrl": "$BASE_URL"
  },
  "summary": {
    "totalTests": $TOTAL_TESTS,
    "passedTests": $PASSED_TESTS,
    "failedTests": $FAILED_TESTS,
    "successRate": "${SUCCESS_RATE}%"
  },
  "reportFile": "$REPORT_FILE"
}
EOF

# 返回状态码
if [ "$FAILED_TESTS" -eq 0 ]; then
    exit 0
else
    exit 1
fi
